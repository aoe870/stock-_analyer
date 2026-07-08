# Data Collector and API Service Split Design

Date: 2026-07-07

## Purpose

The current system can be slow because user-facing API requests and data collection still share one runtime boundary. The backend API can create pipelines, start scheduler-driven sync, and even auto-trigger dashboard sync when local data is missing. This makes a normal page visit depend on remote provider latency, provider quotas, retry behavior, and large sync jobs.

The next version should split responsibilities:

1. The data collector service fetches and prepares all product data ahead of time.
2. The API service reads already collected data and returns immediately.
3. The database is the contract between both services.
4. Missing data is reported as data status, not fixed by blocking a user request.

This design supersedes any earlier design that allowed the user-facing API to call Miana directly for short-TTL refresh. From this version onward, all provider access belongs to the collector service.

## Current Problem Summary

Current code shows three coupling points that should be removed:

| Area | Current Behavior | Problem |
| --- | --- | --- |
| App startup | `stock_analyzer_app.__main__` starts the scheduler before running uvicorn | API and collector lifecycle are tied together |
| API sync endpoints | `POST /api/sync/jobs` builds and runs `DailySyncPipeline` directly | User-facing API process performs collection work |
| Dashboard fallback | `_ensure_yesterday_data_for_dashboard()` can run `run_full_daily_pipeline()` | A page request can trigger remote data fetch and block |

These behaviors make performance unpredictable. They also make deployment harder because scaling API replicas can accidentally scale schedulers or provider callers.

## Target Architecture

Use three runtime roles.

```text
Miana / other providers
        |
        v
Data Collector Service  --->  MySQL / read model tables  --->  API Service  --->  Frontend
        |                              ^
        v                              |
sync_jobs / sync_requests / health ----+
```

### Data Collector Service

The collector service is the only process allowed to call Miana, Tushare, AkShare, Eastmoney, or any future remote provider.

Responsibilities:

- Own provider credentials and rate limits.
- Run scheduled collection jobs.
- Run backfill and retry queues.
- Compute derived data such as adjusted bars, indicators, strategy signals, rankings, and coverage.
- Write normalized tables and raw payloads.
- Maintain sync job status, dataset freshness, and failure details.
- Consume manual sync requests from a database queue.

Non-responsibilities:

- It does not serve frontend pages.
- It does not run user-facing read APIs.
- It does not depend on browser request timing.

### API Service

The API service is a read service over the prepared data store.

Responsibilities:

- Serve stock detail, market dashboard, data center, screening, and backtest read APIs.
- Return data status for every optional dataset.
- Insert non-blocking sync requests for admin/manual refresh actions.
- Expose collector health and last job summaries by reading database state.

Non-responsibilities:

- It does not hold provider tokens.
- It does not import provider chain code.
- It does not construct or run sync pipelines.
- It does not start APScheduler.
- It does not call Miana or other remote providers on page requests.

### Shared Database Contract

MySQL is the first implementation contract because the project already uses it.

The database should contain:

- normalized domain tables
- raw payload tables
- sync job tables
- sync request queue
- dataset freshness status
- collection failure details

A message broker can be added later, but it is not required for the first split. A database-backed queue is simpler and fits the current codebase.

## Service Modes

Add an explicit runtime mode:

| Mode | Entry Point | Behavior |
| --- | --- | --- |
| `api` | `python -m stock_analyzer_app api` or current module default | Runs FastAPI only, no scheduler, no provider clients |
| `collector` | `python -m stock_analyzer_app collector` | Runs scheduler and queue worker, no public FastAPI |
| `worker-once` | `python -m stock_analyzer_app collect --job daily_core_pipeline` | Runs one job for tests, cron, or manual repair |

The existing `python -m stock_analyzer_app` can keep API mode as the default for local compatibility, but it must not start the scheduler by default.

## Collection Coverage Model

"Collect all data" should mean all data required by the product views, defined by a coverage manifest. The collector should know exactly which datasets must be ready before users click.

### Dataset Manifest

Create a manifest in code or configuration:

| Dataset | Scope | Freshness SLA | Owner Job |
| --- | --- | --- | --- |
| Trading calendar | `XSHG`, `XSHE`, `BJSE` | 30 days cached ahead | `calendar_pipeline` |
| Stock universe | A-share market | Daily | `reference_pipeline` |
| Daily bars | All active A-share symbols | Previous trading day by 00:30 | `daily_market_pipeline` |
| Adjusted bars | All active A-share symbols | After daily bars | `daily_market_pipeline` |
| Indicators and signals | All active A-share symbols | After adjusted bars | `analysis_pipeline` |
| Stock rankings | Market dashboard scopes | Previous trading day by 00:30 | `daily_market_pipeline` |
| Sector ranking and heat | All configured sector scopes | Previous trading day by 00:30 | `market_structure_pipeline` |
| Index overview | Major indexes | Previous trading day by 00:30 | `market_structure_pipeline` |
| Sector/index K-lines | Configured indexes and sectors | Previous trading day by 00:30 | `market_structure_pipeline` |
| Company profile | All active A-share symbols | 30 days | `fundamental_pipeline` |
| Financial statements | All active A-share symbols | 7 days, plus post-announcement refresh | `fundamental_pipeline` |
| Holders and officers | All active A-share symbols | 30 days | `fundamental_pipeline` |
| Financial metrics | All active A-share symbols | 7 days | `research_context_pipeline` |
| News and research reports | Active/recent/watched symbols first, then full market when feasible | 1 day | `research_context_pipeline` |
| IPO and AH pairs | Reference scope | Daily | `reference_pipeline` |
| Latest quote snapshot | Watchlist, opened symbols, major indexes, hot sectors | 30-60 seconds during market hours | `quote_snapshot_pipeline` |

If full-market collection for a dataset is too expensive, the manifest must say so and define the prioritized scope. The API still must not compensate by calling providers directly.

## Data Flow

### Scheduled Collection Flow

1. Collector loads dataset manifest.
2. Collector resolves the latest completed trading day from `trading_calendars`.
3. Collector creates a `sync_jobs` row for each due pipeline.
4. Collector fetches provider data with rate limits and retries.
5. Collector writes normalized records and raw payloads.
6. Collector updates `dataset_freshness`.
7. Collector marks job status and failure details.

### User Request Flow

1. Frontend requests data from API.
2. API reads local tables only.
3. API returns data and `data_status`.
4. If data is missing or stale, API may insert a `sync_requests` row.
5. API response does not wait for the collector.
6. Collector later consumes the request and updates storage.

### Manual Refresh Flow

Manual refresh becomes asynchronous:

1. User clicks refresh in UI.
2. API inserts a `sync_requests` row with dataset, symbol scope, priority, and reason.
3. API returns `202 Accepted` with `request_id`.
4. Frontend polls `GET /api/sync/requests/{id}` or reads Data Center job status.
5. Collector processes the request.
6. Frontend refreshes local read APIs after completion.

## Database Additions

### `sync_requests`

Queue for API-to-collector requests.

Columns:

- `id`
- `request_type`
- `dataset`
- `scope_json`
- `priority`
- `status`
- `requested_by`
- `reason`
- `created_at`
- `claimed_at`
- `finished_at`
- `error_message`

Valid statuses:

- `pending`
- `claimed`
- `completed`
- `failed`
- `cancelled`

### `dataset_freshness`

Collector-maintained status per dataset and scope.

Columns:

- `dataset`
- `scope_key`
- `latest_data_date`
- `last_success_at`
- `last_attempt_at`
- `status`
- `rows`
- `missing_count`
- `failed_count`
- `owner_job_type`
- `summary_json`

Valid statuses:

- `ready`
- `partial`
- `missing`
- `stale`
- `failed`

### `provider_call_log`

Optional first-version table for diagnostics and quota visibility.

Columns:

- `provider`
- `endpoint`
- `scope_key`
- `status_code`
- `duration_ms`
- `success`
- `error_message`
- `created_at`

This is not required for UI features, but it helps explain slow or failed collection.

## Backend API Changes

### Remove Provider Execution From API

The API service should no longer expose endpoints that synchronously run pipelines.

Change behavior:

| Current API | New Behavior |
| --- | --- |
| `POST /api/sync/jobs` | Create `sync_requests` row and return `202 Accepted` |
| `POST /api/sync/jobs/{job_id}/retry` | Create high-priority retry request |
| Dashboard auto-sync on missing data | Remove blocking sync; return `data_status` and optional pending request |
| Stock detail refresh fundamentals | Create symbol-scoped request; do not run provider calls |
| Quote refresh | Read latest collector snapshot only; no Miana call from API |

### Read API Status Contract

Every API that can return incomplete data should include status:

```json
{
  "data": [],
  "data_status": {
    "dataset": "sector_rankings",
    "status": "stale",
    "latest_data_date": "2026-07-03",
    "last_success_at": "2026-07-04T00:12:00+08:00",
    "pending_request_id": 123,
    "message": "collector has not completed the latest trading day"
  }
}
```

The frontend can show a clear state without causing a slow backend call.

### Health APIs

Add read-only operations:

- `GET /api/collector/status`
- `GET /api/collector/datasets`
- `GET /api/sync/requests/{id}`
- `GET /api/sync/requests`

These endpoints read database state only.

## Collector Job Design

### Job Types

| Job Type | Purpose | Schedule |
| --- | --- | --- |
| `calendar_pipeline` | Trading calendars | Monthly and on startup if missing |
| `reference_pipeline` | Stock list, exchanges, IPO, AH pairs | Daily 00:00 |
| `daily_market_pipeline` | Daily bars, adjusted bars, rankings | Daily 00:05 after calendar resolution |
| `analysis_pipeline` | Indicators, strategy signals, screening read models | After daily market pipeline |
| `market_structure_pipeline` | Index/sector lists, constituents, K-lines, heat | Daily 00:20 |
| `fundamental_pipeline` | Company profile, financial statements, holders, officers, corporate actions | Continuous stale-symbol batch |
| `research_context_pipeline` | News, research reports, financial metrics | Continuous stale-symbol batch |
| `quote_snapshot_pipeline` | Latest quotes for configured scopes | Market hours only |
| `request_worker` | Consume `sync_requests` | Continuous |

### Collector Concurrency

Use separate concurrency limits:

- market data workers
- fundamentals workers
- news/report workers
- quote workers
- retry workers

This prevents slow fundamentals or news collection from blocking daily market data.

### Completion Targets

Default service-level targets:

| Dataset Group | Target |
| --- | --- |
| Calendar and reference data | Ready before daily market job starts |
| Previous trading day market data | Ready before 00:30 |
| Indicators and strategy signals | Ready before 00:45 |
| Index and sector context | Ready before 01:00 |
| Fundamentals | Eventually complete, highest priority for opened/watched symbols |
| News and reports | Previous day data ready before market open |
| Quote snapshots | Best effort during market hours, never blocks API |

## Deployment Design

### Docker Compose

Split current single `app` service into:

| Service | Command | Provider Tokens |
| --- | --- | --- |
| `api` | FastAPI only | No |
| `collector` | Scheduler and request worker | Yes |
| `mysql` | Shared storage | No |

Only the collector container gets:

- `STOCK_ANALYZER_MIANA_TOKEN`
- `STOCK_ANALYZER_TUSHARE_TOKEN`
- provider rate limit settings

The API container gets:

- database connection settings
- UI/API settings
- no provider credentials
- sync execution disabled

### Scaling Rule

API can scale horizontally because it is read-only.

Collector should run as one scheduler leader. Later versions can add multiple workers, but only one process should own scheduled job creation.

## Frontend Behavior

Frontend should treat the API as fast local read access.

Changes:

- No page should show a long spinner because backend is collecting remote data.
- Missing panels show dataset status and latest available date.
- Manual refresh buttons show queued/running/completed states.
- Market dashboard reads the latest completed trading day, not "yesterday" by calendar subtraction.
- If latest data is stale, show a freshness badge and keep the latest available data visible.

## Migration Plan

### Phase 1: Stop Blocking Page Requests

- Remove dashboard auto-sync from read path.
- Change manual sync endpoints to create `sync_requests`.
- Add `dataset_freshness` reads to dashboard and stock detail.
- Keep old pipeline code, but call it only from collector mode.

### Phase 2: Add Collector Mode

- Add explicit CLI modes: `api`, `collector`, `collect`.
- Move scheduler startup out of API mode.
- Add collector loop for scheduled jobs and request queue.
- Ensure API mode does not import provider chain unless tests explicitly configure it.

### Phase 3: Coverage-Driven Collection

- Add dataset manifest.
- Add freshness update after every job.
- Add missing/stale dataset detection.
- Add stale-symbol prioritization for fundamentals, news, reports, and metrics.

### Phase 4: Docker Split

- Split `docker-compose.yml` into `api` and `collector` services.
- Put provider tokens only in collector.
- Add health checks for both services.
- Verify API still works when collector is temporarily stopped.

### Phase 5: Performance Hardening

- Add indexes for read-heavy pages.
- Add latest snapshot tables for dashboard and stock detail headers.
- Add provider call diagnostics.
- Add collector backlog and SLA metrics in Data Center.

## Test Plan

### API Tests

- API startup does not start scheduler.
- API mode does not build provider chain for read endpoints.
- Dashboard read does not call `run_full_daily_pipeline`.
- Stock detail read does not call provider or pipeline code.
- Manual refresh returns `202 Accepted` and creates `sync_requests`.
- Missing data response includes `data_status`.

### Collector Tests

- Collector mode starts scheduler.
- Collector consumes pending `sync_requests`.
- Collector marks request completed or failed.
- Collector updates `dataset_freshness`.
- Scheduled job creation is guarded by running-job checks.

### Repository Tests

- `sync_requests` insert, claim, complete, fail.
- `dataset_freshness` upsert and read by dataset/scope.
- stale/missing/ready status computation.

### Integration Tests

- Start API with seeded MySQL data and no provider token; all read endpoints work.
- Start collector with provider stubs; data is written and API sees it.
- Stop collector; API remains fast and returns stale status.
- Create manual refresh request; collector processes it asynchronously.

## Acceptance Criteria

The split is successful when:

1. A normal page request never runs provider code or sync pipeline code.
2. API mode can run without Miana/Tushare/AkShare credentials.
3. Collector mode is the only mode that calls remote providers.
4. Scheduler runs only in collector mode.
5. Dashboard and stock detail return local data in predictable time.
6. Missing or stale data is visible through `data_status`.
7. Manual refresh creates a queue item and returns immediately.
8. Docker deployment has separate `api` and `collector` services.
9. Data Center shows collector health, backlog, latest success, and failed datasets.

## Relationship To API Gap Design

The API gap design remains useful for deciding which Miana endpoints to integrate next. This split design changes how those endpoints are used:

- Provider methods are implemented in the collector path only.
- API read endpoints never call Miana.
- Quote snapshots are collected by `quote_snapshot_pipeline`, not refreshed by API.
- News, reports, metrics, holders, IPO, AH, exchange data, calendars, index bars, and sector bars are all collected before UI reads them.

Recommended next implementation order:

1. Remove blocking sync from API read paths.
2. Add `sync_requests` and `dataset_freshness`.
3. Add collector mode and move scheduler there.
4. Split Docker services.
5. Then implement the next Miana endpoint gaps under collector-only rules.
