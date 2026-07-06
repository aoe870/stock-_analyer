from pathlib import Path


REQUIRED_SCRIPTS = [
    "start_app.ps1",
    "init_db.ps1",
    "migrate_db.ps1",
    "seed_db.ps1",
    "dev_server.ps1",
    "sync_once.ps1",
    "deploy_local.ps1",
    "backup_db.ps1",
    "restore_db.ps1",
]


def test_required_local_mysql_scripts_exist():
    for script in REQUIRED_SCRIPTS:
        assert (Path("scripts") / script).exists(), script


def test_root_start_script_delegates_to_start_app():
    content = Path("start.ps1").read_text(encoding="utf-8")

    assert "scripts\\start_app.ps1" in content
    assert "@PSBoundParameters" in content


def test_start_app_script_bootstraps_database_and_server():
    content = Path("scripts/start_app.ps1").read_text(encoding="utf-8")

    assert "docker compose" in content
    assert "migrate_db.ps1" in content
    assert "seed_db.ps1" in content
    assert "-m stock_analyzer_app" in content
    assert "http://127.0.0.1:8000" in content


def test_docker_compose_declares_mysql_8_service():
    content = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "mysql:" in content
    assert "app:" in content
    assert "build:" in content
    assert "mysql:8" in content
    assert "stock_analyzer" in content
    assert "3306:3306" in content
    assert "8000:8000" in content
    assert "healthcheck:" in content
    assert "condition: service_healthy" in content


def test_linux_and_windows_docker_deploy_entrypoints_exist():
    linux = Path("deploy.sh")
    windows = Path("deploy.ps1")

    assert linux.exists()
    assert windows.exists()

    linux_content = linux.read_text(encoding="utf-8")
    windows_content = windows.read_text(encoding="utf-8")

    for expected in ["docker compose", "up -d mysql", "migrate", "seed", "up -d app", "/api/health"]:
        assert expected in linux_content
    for expected in ["docker compose", "up -d mysql", "migrate", "seed", "up -d app", "/api/health"]:
        assert expected in windows_content


def test_dockerfile_packages_application_for_linux_compose():
    dockerfile = Path("Dockerfile")
    dockerignore = Path(".dockerignore")
    env_example = Path(".env.example")

    assert dockerfile.exists()
    assert dockerignore.exists()
    assert env_example.exists()

    content = dockerfile.read_text(encoding="utf-8")
    assert "python:3.12-slim" in content
    assert "requirements.txt" in content
    assert "stock_analyzer_app" in content
    assert "public" in content
    assert "EXPOSE 8000" in content
    assert "python" in content and "-m" in content and "stock_analyzer_app" in content

    ignored = dockerignore.read_text(encoding="utf-8")
    for pattern in [".venv", "logs", ".git", "__pycache__", "dist"]:
        assert pattern in ignored

    env_text = env_example.read_text(encoding="utf-8")
    for key in [
        "STOCK_ANALYZER_DB_HOST=mysql",
        "STOCK_ANALYZER_DB_NAME=stock_analyzer",
        "STOCK_ANALYZER_DB_USER=stock_analyzer",
        "STOCK_ANALYZER_SYNC_TIME=00:00",
        "STOCK_ANALYZER_MIANA_TOKEN=",
    ]:
        assert key in env_text


def test_container_entrypoint_binds_all_interfaces():
    content = Path("stock_analyzer_app/__main__.py").read_text(encoding="utf-8")

    assert "STOCK_ANALYZER_HOST" in content
    assert "0.0.0.0" in content
    assert "STOCK_ANALYZER_PORT" in content


def test_migration_script_tracks_checksums_and_refuses_changed_migrations():
    content = Path("scripts/migrate_db.ps1").read_text(encoding="utf-8")

    assert "schema_migrations" in content
    assert "SHA256" in content
    assert "throw" in content
    assert "checksum mismatch" in content
    assert "Get-ChildItem" in content
    assert "LASTEXITCODE" in content


def test_mysql_scripts_do_not_use_unsupported_powershell_input_redirection():
    for script in ["migrate_db.ps1", "seed_db.ps1", "restore_db.ps1"]:
        content = Path("scripts", script).read_text(encoding="utf-8")

        assert " < " not in content
        assert "docker exec -i stock_analyzer_mysql mysql" in content


def test_scripts_do_not_bind_reserved_powershell_host_variable():
    for script in ["init_db.ps1", "migrate_db.ps1", "seed_db.ps1", "backup_db.ps1", "restore_db.ps1"]:
        content = Path("scripts", script).read_text(encoding="utf-8")

        assert "$Host" not in content
        assert "Alias('Host')" in content


def test_init_and_seed_scripts_are_idempotent():
    init = Path("scripts/init_db.ps1").read_text(encoding="utf-8")
    seed = Path("scripts/seed_db.ps1").read_text(encoding="utf-8")

    assert "CREATE DATABASE IF NOT EXISTS" in init
    assert "CREATE USER IF NOT EXISTS" in init
    assert "ON DUPLICATE KEY UPDATE" in seed


def test_restore_requires_explicit_confirmation():
    restore = Path("scripts/restore_db.ps1").read_text(encoding="utf-8")

    assert "ConfirmRestore" in restore
    assert "throw" in restore
    assert "mysql" in restore


def test_sync_once_exposes_supported_job_types():
    sync = Path("scripts/sync_once.ps1").read_text(encoding="utf-8")

    for job_type in [
        "sync_calendar",
        "sync_stock_universe",
        "sync_daily_bars",
        "sync_adjustment_factors",
        "aggregate_daily",
        "compute_signals",
        "full_daily_pipeline",
    ]:
        assert job_type in sync
