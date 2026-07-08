# Collector API Service Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split data collection from user-facing API execution so page requests only read local data and enqueue asynchronous collection requests.

**Architecture:** Add a database-backed `sync_requests` queue and `dataset_freshness` status contract. API mode creates requests and reads status only; collector mode owns scheduler, provider chain, and pipeline execution. Docker runs separate `api` and `collector` services against the same MySQL database.

**Tech Stack:** Python, FastAPI, APScheduler, MySQL, pytest, Docker Compose.

---

### Task 1: Add Queue and Freshness Repository Contracts

**Files:**
- Modify: `stock_analyzer_app/sync/service.py`
- Modify: `stock_analyzer_app/storage/mysql.py`
- Add: `db/migrations/008_create_collector_split_schema.sql`
- Test: `tests/test_api.py`
- Test: `tests/test_mysql_repositories.py`

- [ ] Add failing tests for `create_sync_request`, `list_sync_requests`, `get_sync_request`, and `upsert_dataset_freshness`.
- [ ] Implement in-memory repository methods.
- [ ] Add MySQL migration for `sync_requests` and `dataset_freshness`.
- [ ] Implement MySQL repository methods.
- [ ] Run targeted repository tests.

### Task 2: Make API Sync Endpoints Asynchronous

**Files:**
- Modify: `stock_analyzer_app/api/app.py`
- Test: `tests/test_api.py`

- [ ] Add failing tests proving `POST /api/sync/jobs` returns `202` and does not call `runtime.make_daily_pipeline`.
- [ ] Add failing tests proving retry creates a high-priority `sync_requests` row.
- [ ] Replace direct pipeline execution in API sync endpoints with queue insertion.
- [ ] Add `GET /api/sync/requests` and `GET /api/sync/requests/{id}`.
- [ ] Run targeted API tests.

### Task 3: Remove Blocking Dashboard Collection

**Files:**
- Modify: `stock_analyzer_app/api/app.py`
- Test: `tests/test_api.py`

- [ ] Add failing test proving dashboard never calls `run_full_daily_pipeline` when local data is missing.
- [ ] Change dashboard missing-data behavior to return local payload plus `data_status`.
- [ ] Run dashboard API tests.

### Task 4: Add Collector Runtime Mode

**Files:**
- Modify: `stock_analyzer_app/__main__.py`
- Add: `stock_analyzer_app/collector.py`
- Test: `tests/test_collector_runtime.py`

- [ ] Add failing tests for API mode not starting scheduler by default.
- [ ] Add failing tests for collector mode starting scheduler and processing one queued request with a stub pipeline.
- [ ] Implement CLI modes: `api`, `collector`, and `collect`.
- [ ] Keep default module execution compatible with API mode.
- [ ] Run runtime tests.

### Task 5: Split Docker Services

**Files:**
- Modify: `docker-compose.yml`
- Test: `tests/test_docker_compose.py`

- [ ] Add failing static test that compose contains separate `api` and `collector` services.
- [ ] Update compose so provider credentials are only on `collector`.
- [ ] Run docker compose static test.

### Task 6: Verification

**Files:**
- All changed files

- [ ] Run targeted tests for API, scheduler, repository, collector runtime, and docker compose.
- [ ] Run broader regression tests if the targeted suite passes.
- [ ] Review git diff for accidental provider calls in API mode.
