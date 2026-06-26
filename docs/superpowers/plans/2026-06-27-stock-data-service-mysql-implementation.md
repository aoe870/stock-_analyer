# Stock Data Service MySQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the CSV/sample-only prototype with a local A-share daily data service backed by MySQL, sync jobs, materialized analysis data, screening, backtesting, and operational APIs/UI.

**Architecture:** Keep one FastAPI process for version 1, with clean package boundaries for config, storage, providers, sync, aggregation, indicators, strategies, screening, backtest, API, and tasks. Provider adapters return normalized dictionaries only; sync services own persistence and durable job records; analysis requests read local MySQL analysis tables rather than external providers.

**Tech Stack:** Python 3.12, FastAPI, PyMySQL, APScheduler, pytest, MySQL 8.x, Docker Compose, PowerShell scripts, vanilla browser UI.

---

## File Structure

- Create/modify `requirements.txt` with FastAPI, Uvicorn, pytest, httpx, PyMySQL, APScheduler, python-dotenv.
- Create `docker-compose.yml`.
- Create SQL migrations under `db/migrations/` and seed SQL under `db/seeds/`.
- Create PowerShell scripts under `scripts/`.
- Create packages:
  - `stock_analyzer_app/config/`
  - `stock_analyzer_app/storage/`
  - `stock_analyzer_app/data_provider/`
  - `stock_analyzer_app/sync/`
  - `stock_analyzer_app/aggregation/`
  - `stock_analyzer_app/indicators/`
  - `stock_analyzer_app/strategies/`
  - `stock_analyzer_app/screening/`
  - `stock_analyzer_app/backtest/`
  - `stock_analyzer_app/api/`
  - `stock_analyzer_app/tasks/`
- Preserve compatibility imports where practical so existing tests keep expressing the same core behavior.

## Tasks

### Task 1: Storage Schema and Migration Runner

**Files:**
- Create: `db/migrations/001_create_core_schema.sql`
- Create: `db/migrations/002_create_analysis_schema.sql`
- Create: `db/migrations/003_create_run_history_schema.sql`
- Create: `db/seeds/001_default_settings.sql`
- Create: `stock_analyzer_app/config/settings.py`
- Create: `stock_analyzer_app/storage/migrations.py`
- Create: `tests/test_storage_migrations.py`

- [ ] Write failing tests for migration ordering, SHA-256 checksum calculation, changed-checksum refusal, and seed upsert discoverability.
- [ ] Run `pytest tests/test_storage_migrations.py -q`; expect import failures.
- [ ] Implement settings and migration planning helpers without requiring a live MySQL server for unit tests.
- [ ] Run `pytest tests/test_storage_migrations.py -q`; expect pass.

### Task 2: Required Package Boundaries and Core Compatibility

**Files:**
- Replace: `stock_analyzer_app/indicators.py` with `stock_analyzer_app/indicators/__init__.py`
- Create: `stock_analyzer_app/indicators/series.py`
- Create: `stock_analyzer_app/strategies/expma.py`
- Modify: `stock_analyzer_app/strategy.py`
- Replace: `stock_analyzer_app/backtest.py` with `stock_analyzer_app/backtest/__init__.py`
- Replace: `stock_analyzer_app/screening.py` with `stock_analyzer_app/screening/__init__.py`

- [ ] Run existing core tests to capture current behavior.
- [ ] Move implementations into required packages and keep compatibility wrappers.
- [ ] Run `pytest tests/test_indicators.py tests/test_strategy.py tests/test_backtest.py -q`; expect pass.

### Task 3: Provider Contracts and Sync Jobs

**Files:**
- Create: `stock_analyzer_app/data_provider/base.py`
- Create: `stock_analyzer_app/data_provider/csv_provider.py`
- Create: `stock_analyzer_app/data_provider/provider_chain.py`
- Create: `stock_analyzer_app/sync/jobs.py`
- Create: `stock_analyzer_app/sync/service.py`
- Create: `stock_analyzer_app/tasks/scheduler.py`
- Create: `tests/test_provider_sync.py`

- [ ] Write failing tests for provider contract methods, Tushare-first priority from settings, symbol-level failure isolation, `completed_with_errors`, and duplicate daily pipeline prevention.
- [ ] Implement provider chain and sync service using repository interfaces/fakes in tests.
- [ ] Run `pytest tests/test_provider_sync.py -q`; expect pass.

### Task 4: Aggregation and Materialization

**Files:**
- Create: `stock_analyzer_app/aggregation/daily.py`
- Create: `stock_analyzer_app/storage/repositories.py`
- Create: `tests/test_aggregation.py`

- [ ] Write failing tests for raw bar validation, forward-adjusted analysis bars, unadjusted fallback metadata, and recompute warmup start 60 rows before changed date.
- [ ] Implement aggregation functions and repository protocols.
- [ ] Run `pytest tests/test_aggregation.py -q`; expect pass.

### Task 5: Repository-Backed Screening and Backtesting

**Files:**
- Modify: `stock_analyzer_app/screening/__init__.py`
- Modify: `stock_analyzer_app/backtest/__init__.py`
- Create: `tests/test_analysis_repositories.py`

- [ ] Write failing tests proving screening/backtest read analysis repositories and do not call providers.
- [ ] Add coverage summaries and `allow_partial_coverage` handling.
- [ ] Run `pytest tests/test_analysis_repositories.py -q`; expect pass.

### Task 6: API Routers and UI

**Files:**
- Replace: `stock_analyzer_app/api.py` with `stock_analyzer_app/api/__init__.py`
- Create: `stock_analyzer_app/api/app.py`
- Create: `stock_analyzer_app/api/sync.py`
- Create: `stock_analyzer_app/api/stocks.py`
- Create: `stock_analyzer_app/api/screening.py`
- Create: `stock_analyzer_app/api/backtests.py`
- Modify: `stock_analyzer_app/__main__.py`
- Modify: `public/index.html`
- Modify: `public/styles.css`
- Modify: `public/app.js`
- Modify: `tests/test_api.py`

- [ ] Write failing tests for health database/migration/scheduler fields, sync job creation/status/items/retry/coverage, stocks/bars/indicators/signals, screening task/result, and backtest task/run history.
- [ ] Implement routers with task IDs and repository-backed service calls.
- [ ] Update UI to show sync dashboard, coverage, screening, backtest, and stock detail data.
- [ ] Run `pytest tests/test_api.py -q`; expect pass.

### Task 7: Scripts and Local Deployment

**Files:**
- Create: `scripts/init_db.ps1`
- Create: `scripts/migrate_db.ps1`
- Create: `scripts/seed_db.ps1`
- Create: `scripts/dev_server.ps1`
- Create: `scripts/sync_once.ps1`
- Create: `scripts/deploy_local.ps1`
- Create: `scripts/backup_db.ps1`
- Create: `scripts/restore_db.ps1`
- Create: `tests/test_scripts.py`

- [ ] Write failing tests that required scripts exist and contain idempotent migration/checksum/backup/restore safeguards.
- [ ] Implement scripts with no destructive default behavior.
- [ ] Run `pytest tests/test_scripts.py -q`; expect pass.

### Task 8: Full Verification

- [ ] Run `pytest -q`.
- [ ] If MySQL is available, run `scripts/migrate_db.ps1` and `scripts/seed_db.ps1`; otherwise report that live MySQL verification was not run.
- [ ] Start the FastAPI app and verify `/api/health`.

