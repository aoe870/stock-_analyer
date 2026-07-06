# Miana V2 Stock Analysis Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first V2 slice of the Miana-powered stock research platform: richer data storage, Miana provider mappings, backend read APIs, and frontend surfaces for market dashboard, stock detail research, and data center.

**Architecture:** Keep the current FastAPI + MySQL + static Vue frontend architecture. Add focused migrations and repository methods for new data families, then expose read APIs that the frontend can consume without changing deployment topology.

**Tech Stack:** Python 3.12, FastAPI, PyMySQL, MySQL 8, pytest, Vue 3, Element Plus, ECharts, Docker Compose.

---

## File Structure

- `db/migrations/006_create_miana_v2_research_schema.sql`: new financial, holder, officer, index, and sector tables.
- `stock_analyzer_app/data_provider/miana_provider.py`: Miana endpoint mappings for financial statements, holders, officers, indexes, and sectors.
- `stock_analyzer_app/storage/mysql.py`: persistence and read methods for the new tables.
- `stock_analyzer_app/sync/pipeline.py`: keep daily core sync lean; add helper paths for optional V2 research refreshes.
- `stock_analyzer_app/api/app.py`: add market dashboard, stock overview, financial, capital flow, and data center endpoints.
- `public/app.js`: add V2 frontend views and API calls.
- `public/styles.css`: add layout styles for dashboard, stock research tabs, and data center.
- `tests/test_miana_provider.py`: provider normalization tests.
- `tests/test_mysql_repositories.py`: persistence tests.
- `tests/test_api.py`: API response tests.
- `tests/test_frontend_workspace.py`: static frontend regression tests.

## Task 1: Add Miana V2 Research Schema

**Files:**
- Create: `db/migrations/006_create_miana_v2_research_schema.sql`
- Modify: `tests/test_storage_migrations.py`

- [ ] **Step 1: Write the failing migration-order test**

Add `006_create_miana_v2_research_schema.sql` to the expected migration list in `tests/test_storage_migrations.py`.

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
docker run --rm -v "${PWD}:/work" -w /work stock_analyer-app python -m pytest tests/test_storage_migrations.py::test_load_migration_files_returns_filename_order -q
```

Expected: failure because the migration file does not exist yet.

- [ ] **Step 3: Create the migration**

Create tables:

- `income_statements`
- `balance_sheets`
- `cashflow_statements`
- `stock_top10_holders`
- `stock_company_officers`
- `stock_officer_rewards`
- `market_indexes`
- `index_constituents`
- `index_daily_bars`
- `market_sectors`
- `sector_constituents`
- `sector_daily_bars`
- `latest_market_quotes`
- `latest_sector_quotes`
- `latest_index_quotes`

- [ ] **Step 4: Run the migration-order test**

Expected: pass.

## Task 2: Map New Miana Provider Endpoints

**Files:**
- Modify: `stock_analyzer_app/data_provider/miana_provider.py`
- Modify: `tests/test_miana_provider.py`

- [ ] **Step 1: Write failing provider tests**

Add tests for:

- `fetch_income_statements()`
- `fetch_balance_sheets()`
- `fetch_cashflow_statements()`
- `fetch_top10_holders()`
- `fetch_company_officers()`
- `fetch_officer_rewards()`
- `fetch_index_list()`
- `fetch_sector_list()`
- `fetch_sector_constituents()`
- `fetch_index_constituents()`

- [ ] **Step 2: Run the provider tests**

Expected: `AttributeError` for missing provider methods.

- [ ] **Step 3: Implement provider methods**

Use Miana endpoints:

- `/stock/v1/incomeSheet`
- `/stock/v1/balanceSheet`
- `/stock/v1/cashflow`
- `/stock/v1/top10holders`
- `/stock/v1/companyOfficer`
- `/stock/v1/rewards`
- `/index/v1/indexList`
- `/index/v1/constituent`
- `/sector/v1/sectorList`
- `/sector/v1/constituent`
- `/index/v2/kline`
- `/sector/v2/kline`

Normalize common fields and preserve complete payloads in `raw_json`.

- [ ] **Step 4: Run provider tests**

Expected: pass.

## Task 3: Persist and Read V2 Research Data

**Files:**
- Modify: `stock_analyzer_app/storage/mysql.py`
- Modify: `tests/test_mysql_repositories.py`

- [ ] **Step 1: Write failing repository tests**

Add tests for upserting and reading:

- financial statement summary rows
- top holder rows
- sector list rows
- index list rows
- sector/index constituents

- [ ] **Step 2: Run repository tests**

Expected: failures for missing methods.

- [ ] **Step 3: Implement repository methods**

Add `upsert_*` methods and read methods:

- `upsert_income_statements`
- `upsert_balance_sheets`
- `upsert_cashflow_statements`
- `upsert_stock_top10_holders`
- `upsert_stock_company_officers`
- `upsert_stock_officer_rewards`
- `upsert_market_indexes`
- `upsert_index_constituents`
- `upsert_market_sectors`
- `upsert_sector_constituents`
- `stock_research_snapshot`
- `market_dashboard_snapshot`
- `data_center_coverage`

- [ ] **Step 4: Run repository tests**

Expected: pass.

## Task 4: Add Backend Read APIs

**Files:**
- Modify: `stock_analyzer_app/api/app.py`
- Modify: `tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

Add tests for:

- `GET /api/market/dashboard`
- `GET /api/stocks/{symbol}/overview`
- `GET /api/stocks/{symbol}/financials`
- `GET /api/stocks/{symbol}/capital-flow`
- `GET /api/data-center/coverage`

- [ ] **Step 2: Run API tests**

Expected: 404 for new endpoints.

- [ ] **Step 3: Implement endpoints**

Use repository methods when available. Return empty but stable shapes when optional data is missing.

- [ ] **Step 4: Run API tests**

Expected: pass.

## Task 5: Add V2 Frontend Views

**Files:**
- Modify: `public/app.js`
- Modify: `public/styles.css`
- Modify: `tests/test_frontend_workspace.py`

- [ ] **Step 1: Write frontend static tests**

Assert the frontend contains:

- market dashboard API call
- stock overview API call
- financials API call
- capital flow API call
- data center coverage API call
- navigation entries for Market, Stocks, Sectors, Strategy Lab, Data Center

- [ ] **Step 2: Run frontend tests**

Expected: failures for missing calls or labels.

- [ ] **Step 3: Implement frontend views**

Add:

- market dashboard cards and rankings
- stock detail research tabs
- data center coverage panels

- [ ] **Step 4: Run frontend tests**

Expected: pass.

## Task 6: Verification

**Files:**
- No new files

- [ ] **Step 1: Run focused test suite**

```powershell
docker run --rm -v "${PWD}:/work" -w /work stock_analyer-app python -m pytest tests/test_miana_provider.py tests/test_api.py tests/test_frontend_workspace.py tests/test_storage_migrations.py::test_load_migration_files_returns_filename_order -q
```

- [ ] **Step 2: Validate Docker Compose config**

```powershell
docker compose config --quiet
```

- [ ] **Step 3: Document known gaps**

If MySQL integration tests are not run locally, note that repository persistence still needs a MySQL-backed verification pass.

## Self-Review

Spec coverage:

- Market dashboard: Task 4 and Task 5
- Stock detail research: Task 2, Task 3, Task 4, Task 5
- Data center: Task 3, Task 4, Task 5
- Financial/capital/sector/index ingestion: Task 1, Task 2, Task 3
- Sync separation: partially covered by existing lean daily sync; full independent job orchestration can be a follow-up after the first read/display slice.

Known scoped gap:

- This plan does not implement full scheduled job orchestration for every new data family in the first pass. It creates the storage, provider mappings, persistence, and UI/API surfaces needed to make the new data usable, then follow-up work can add batch schedulers safely.

