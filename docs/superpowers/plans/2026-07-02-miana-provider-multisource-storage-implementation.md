# Miana Provider Multi-Source Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Miana as a first-class provider and persist raw plus normalized Miana data for later reuse.

**Architecture:** Keep provider normalization in `stock_analyzer_app/data_provider/miana_provider.py`, persistence in `MySqlRepository`, and orchestration in `DailySyncPipeline`. Existing analysis tables remain the read model, while new provider-specific tables preserve side data and raw payloads.

**Tech Stack:** Python 3.12, FastAPI, PyMySQL, pytest, MySQL migrations, python-dotenv, urllib from the standard library.

---

### Task 1: Migrations and Repository Storage

**Files:**
- Create: `db/migrations/005_create_miana_multisource_schema.sql`
- Modify: `stock_analyzer_app/storage/mysql.py`
- Test: `tests/test_mysql_repositories.py`

- [ ] Write failing tests that verify provider profiles, company profiles, corporate actions, share capital history, daily money flow, and raw payload metadata are persisted.
- [ ] Run `pytest tests/test_mysql_repositories.py -q` and confirm the new tests fail before implementation.
- [ ] Add migration `005_create_miana_multisource_schema.sql` with `stock_provider_profiles`, `stock_company_profiles`, `corporate_actions`, `share_capital_history`, `daily_money_flow`, and extra nullable columns on `raw_provider_payloads`.
- [ ] Add repository methods `upsert_stock_provider_profiles`, `upsert_stock_company_profiles`, `upsert_corporate_actions`, `upsert_share_capital_history`, `upsert_daily_money_flow`, and `save_raw_provider_payload`.
- [ ] Run `pytest tests/test_mysql_repositories.py -q` and confirm pass.

### Task 2: Miana Provider

**Files:**
- Create: `stock_analyzer_app/data_provider/miana_provider.py`
- Modify: `stock_analyzer_app/data_provider/provider_chain.py`
- Modify: `stock_analyzer_app/config/settings.py`
- Test: `tests/test_miana_provider.py`

- [ ] Write failing tests for symbol conversion, stock list normalization, K-line normalization, adjusted bar handling, and adjustment factor derivation.
- [ ] Run `pytest tests/test_miana_provider.py -q` and confirm failures.
- [ ] Implement `MianaProvider` with injectable HTTP getter for tests and real urllib JSON fetching for production.
- [ ] Wire `miana` into `build_provider_chain`, skipping it when token is missing.
- [ ] Run `pytest tests/test_miana_provider.py -q` and confirm pass.

### Task 3: Pipeline Integration and Duplicate Guard

**Files:**
- Modify: `stock_analyzer_app/sync/pipeline.py`
- Modify: `stock_analyzer_app/api/app.py`
- Test: `tests/test_provider_sync.py`
- Test: `tests/test_api.py`

- [ ] Write failing tests proving `full_daily_pipeline` stores Miana side data when provider returns it.
- [ ] Write failing API test proving a second full pipeline request does not create a concurrent duplicate job.
- [ ] Run the focused tests and confirm failures.
- [ ] Update pipeline to persist provider profiles, raw payloads, adjusted bars, company profiles, corporate actions, shares, and money flow when present.
- [ ] Update API full pipeline creation to return the active pending/running job instead of creating a duplicate.
- [ ] Run focused tests and confirm pass.

### Task 4: Verification

**Files:**
- Existing touched files only.

- [ ] Run `pytest tests/test_storage_migrations.py tests/test_miana_provider.py tests/test_provider_sync.py tests/test_api.py -q`.
- [ ] Run any MySQL-focused tests that are available in the environment.
- [ ] Report exact pass/fail status and any external-service limitation.
