from pathlib import Path

import pytest

from stock_analyzer_app.config.settings import AppSettings
from stock_analyzer_app.storage.migrations import (
    MigrationChecksumMismatch,
    calculate_sha256,
    load_migration_files,
    plan_migrations,
)


def test_settings_reads_mysql_and_provider_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("STOCK_ANALYZER_TUSHARE_TOKEN", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_PROVIDER_PRIORITY", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_MIANA_TOKEN", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_SYNC_MAX_WORKERS", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE", raising=False)
    monkeypatch.setenv("STOCK_ANALYZER_DB_HOST", "db.local")
    monkeypatch.setenv("STOCK_ANALYZER_DB_PASSWORD", "secret")

    settings = AppSettings.from_env()

    assert settings.db.host == "db.local"
    assert settings.db.password == "secret"
    assert settings.provider_priority == ["tushare", "akshare", "eastmoney"]
    assert settings.sync_enabled is True
    assert settings.sync_max_workers == 8
    assert settings.miana_base_url == "http://124.222.142.232:9876/api"
    assert settings.miana_max_requests_per_minute == 500
    assert settings.sync_include_optional_metadata is False


def test_settings_loads_local_dotenv_for_miana_config(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("STOCK_ANALYZER_MIANA_TOKEN", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_MIANA_BASE_URL", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_PROVIDER_PRIORITY", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_SYNC_MAX_WORKERS", raising=False)
    monkeypatch.delenv("STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE", raising=False)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "STOCK_ANALYZER_MIANA_TOKEN=local-token",
                "STOCK_ANALYZER_MIANA_BASE_URL=https://example.test/api",
                "STOCK_ANALYZER_PROVIDER_PRIORITY=miana,akshare",
                "STOCK_ANALYZER_SYNC_MAX_WORKERS=12",
            ]
        ),
        encoding="utf-8",
    )

    settings = AppSettings.from_env()

    assert settings.miana_token == "local-token"
    assert settings.miana_base_url == "https://example.test/api"
    assert settings.provider_priority == ["miana", "akshare"]
    assert settings.sync_max_workers == 12


def test_load_migration_files_returns_filename_order():
    files = load_migration_files(Path("db/migrations"))

    assert [file.path.name for file in files] == [
        "001_create_core_schema.sql",
        "002_create_analysis_schema.sql",
        "003_create_run_history_schema.sql",
        "004_create_stock_status_schema.sql",
        "005_create_miana_multisource_schema.sql",
        "006_create_miana_v2_research_schema.sql",
        "007_extend_company_profiles.sql",
    ]
    assert all(len(file.checksum) == 64 for file in files)


def test_calculate_sha256_uses_file_bytes(tmp_path):
    migration = tmp_path / "001_example.sql"
    migration.write_bytes(b"SELECT 1;\n")

    assert calculate_sha256(migration) == "b4e0497804e46e0a0b0b8c31975b062152d551bac49c3c2e80932567b4085dcd"


def test_plan_migrations_refuses_changed_applied_file(tmp_path):
    migration = tmp_path / "001_example.sql"
    migration.write_text("SELECT 1;\n", encoding="utf-8")
    loaded = load_migration_files(tmp_path)

    applied = {"001_example.sql": "0" * 64}

    with pytest.raises(MigrationChecksumMismatch):
        plan_migrations(loaded, applied)


def test_plan_migrations_skips_applied_and_applies_new(tmp_path):
    first = tmp_path / "001_first.sql"
    second = tmp_path / "002_second.sql"
    first.write_text("SELECT 1;\n", encoding="utf-8")
    second.write_text("SELECT 2;\n", encoding="utf-8")
    loaded = load_migration_files(tmp_path)

    plan = plan_migrations(loaded, {loaded[0].version: loaded[0].checksum})

    assert [item.version for item in plan.to_apply] == ["002_second.sql"]
    assert [item.version for item in plan.skipped] == ["001_first.sql"]


def test_seed_file_uses_idempotent_upserts():
    seed = Path("db/seeds/001_default_settings.sql").read_text(encoding="utf-8")

    assert "INSERT INTO settings" in seed
    assert "ON DUPLICATE KEY UPDATE" in seed
    assert "default_price_mode" in seed
    assert "forward_adjusted" in seed
