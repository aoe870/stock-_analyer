#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

COMPOSE="${DOCKER_COMPOSE:-docker compose}"
ENV_FILE="$ROOT_DIR/.env"
ENV_EXAMPLE="$ROOT_DIR/.env.example"
HEALTH_URL="${STOCK_ANALYZER_HEALTH_URL:-http://127.0.0.1:8000/api/health}"

if [ ! -f "$ENV_FILE" ]; then
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "Created .env from .env.example. Edit provider tokens before running large sync jobs."
fi

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

DB_NAME="${STOCK_ANALYZER_DB_NAME:-stock_analyzer}"
DB_USER="${STOCK_ANALYZER_DB_USER:-stock_analyzer}"
DB_PASSWORD="${STOCK_ANALYZER_DB_PASSWORD:-change-me}"

mysql_exec() {
  $COMPOSE exec -T -e MYSQL_PWD="$DB_PASSWORD" mysql mysql -u "$DB_USER" "$DB_NAME" "$@"
}

wait_for_mysql() {
  echo "Waiting for MySQL..."
  for _ in $(seq 1 60); do
    if mysql_exec -e "SELECT 1;" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "MySQL did not become ready in time." >&2
  return 1
}

migrate() {
  echo "Running migrate..."
  mysql_exec -e "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(64) PRIMARY KEY, checksum CHAR(64) NOT NULL, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
  for file in db/migrations/*.sql; do
    [ -f "$file" ] || continue
    version="$(basename "$file")"
    checksum="$(sha256sum "$file" | awk '{print tolower($1)}')"
    applied="$($COMPOSE exec -T -e MYSQL_PWD="$DB_PASSWORD" mysql mysql -N -B -u "$DB_USER" "$DB_NAME" -e "SELECT checksum FROM schema_migrations WHERE version='$version';" 2>/dev/null || true)"
    if [ -n "$applied" ]; then
      if [ "${applied,,}" != "$checksum" ]; then
        echo "Migration checksum mismatch: $version" >&2
        return 1
      fi
      continue
    fi
    mysql_exec < "$file"
    mysql_exec -e "INSERT INTO schema_migrations (version, checksum) VALUES ('$version', '$checksum');"
  done
}

seed() {
  echo "Running seed..."
  mysql_exec < db/seeds/001_default_settings.sql
}

wait_for_health() {
  echo "Waiting for app health..."
  for _ in $(seq 1 60); do
    if command -v curl >/dev/null 2>&1; then
      if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
        return 0
      fi
    elif command -v wget >/dev/null 2>&1; then
      if wget -qO- "$HEALTH_URL" >/dev/null 2>&1; then
        return 0
      fi
    else
      echo "curl or wget is required for health checks." >&2
      return 1
    fi
    sleep 2
  done
  echo "App health check failed: $HEALTH_URL" >&2
  return 1
}

$COMPOSE build
$COMPOSE up -d mysql
wait_for_mysql
migrate
seed
$COMPOSE up -d api collector
wait_for_health

echo "Deployment complete."
echo "URL: http://127.0.0.1:8000"
echo "Health: $HEALTH_URL"
