# Work Record

Last updated: 2026-07-08

## Current Repository State

- Latest commit: `8fde95d feat: split collector service from API`
- Working tree before this record: clean
- Main runtime services:
  - `stock_analyzer_api`: running on `http://127.0.0.1:8000`
  - `stock_analyzer_collector`: running
  - `stock_analyzer_mysql`: running and healthy

## Recent Work Summary

The latest completed work split the user-facing API service from the data collector service.

Key changes:

- Added explicit runtime modes in `stock_analyzer_app/__main__.py`:
  - `python -m stock_analyzer_app api`
  - `python -m stock_analyzer_app collector`
  - `python -m stock_analyzer_app collect`
- Added `stock_analyzer_app/collector.py` with queue processing, request recovery, automatic enterprise backfill, and recent-attempt filtering.
- Added `sync_requests` and `dataset_freshness` tables in `db/migrations/008_create_collector_split_schema.sql`.
- Changed API sync behavior to enqueue collector requests instead of running pipelines in the API process.
- Changed stock overview enterprise refresh to create on-demand queue requests and dedupe active requests.
- Added enterprise refresh TTL:
  - setting: `STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS`
  - default: `7`
- Added Docker `api` and `collector` services with provider tokens only assigned to collector.
- Added Docker source mounts for local development so services can load current source without rebuilding the image.

## Important Design Documents

- `docs/superpowers/specs/2026-07-07-data-collector-api-service-split-design.md`
- `docs/superpowers/plans/2026-07-07-collector-api-service-split-implementation.md`
- `docs/superpowers/specs/2026-07-08-collector-service-detailed-design.md`
- `docs/superpowers/specs/2026-07-07-miana-api-gap-next-version-design.md`

Start with `2026-07-08-collector-service-detailed-design.md` when resuming collector work.

## Verification Already Run

After the collector/API split and before commit `8fde95d`, full tests passed:

```powershell
docker compose stop collector
docker compose run --rm -v "${PWD}:/work" -w /work api python -m pytest -q
docker compose up -d --no-build collector
```

Result:

```text
155 passed in 114.80s
```

## Local Docker Notes

Docker image rebuilds can hang or fail if Docker cannot reach Docker Hub for `python:3.12-slim`.

Current local workaround:

- `docker-compose.yml` mounts local source into `api` and `collector`.
- Use `docker compose up -d --no-build api collector` after source changes when dependencies did not change.

Useful checks:

```powershell
docker compose ps -a
docker compose exec -T api python -c "import importlib; m=importlib.import_module('stock_analyzer_app.api.app'); print(hasattr(m, '_enqueue_enterprise_on_demand_request'))"
docker compose exec -T collector python -c "import stock_analyzer_app.collector as c; print(hasattr(c.CollectorService, '_recent_enterprise_attempt'))"
```

Both Python checks should print `True`.

## Collector Operational Notes

Queue status:

```sql
SELECT status, request_type, reason, COUNT(*) AS cnt
FROM sync_requests
GROUP BY status, request_type, reason
ORDER BY status, request_type, reason;
```

Freshness status:

```sql
SELECT dataset, status, COUNT(*) AS cnt, MAX(updated_at) AS latest_update
FROM dataset_freshness
GROUP BY dataset, status
ORDER BY dataset, status;
```

Default collector settings:

```text
STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE=5
STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS=7
```

Stop collector before Docker-backed full tests because tests and collector share the same MySQL instance.

## Next Recommended Work

1. Add claim timeout recovery instead of recovering all claimed `sync_requests`.
2. Add request attempt count and retry scheduling to `sync_requests`.
3. Add a dataset manifest for coverage-driven collector scheduling.
4. Normalize `data_status` across all optional read endpoints.
5. Add Data Center collector panels for backlog, stuck requests, and stale datasets.
6. Add provider call diagnostics for rate, latency, empty responses, and failures.
7. Review whether `.env` should keep `STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE=10` or align with `.env.example` default `5`.

## Cleanup Policy

Safe to delete at any time:

- `.pytest_cache/`
- `dist/`
- `build/`
- `__pycache__/`
- `*.pyc`
- local `*.db` and `*.sqlite` files if they are not intentionally used for debugging

Do not delete without checking first:

- `.venv/`
- `.git/`
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`
- `miana-api.md`
- `.env`
