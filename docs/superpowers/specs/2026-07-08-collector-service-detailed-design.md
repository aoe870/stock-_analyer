# Collector Service Detailed Design

Date: 2026-07-08

## Purpose

The collector service is the dedicated data acquisition runtime for the stock analysis system. It owns all remote provider calls, scheduled collection work, on-demand backfill requests, retry behavior, dataset freshness tracking, and normalized persistence. The API service must remain a fast read service and must never block a user request on provider latency.

This document expands the earlier API/collector split design with collector-specific behavior, operational rules, and next-version hardening work.

## Design Goals

1. Keep user-facing API requests fast and predictable.
2. Make the collector the only runtime that calls Miana, Tushare, AkShare, Eastmoney, or future providers.
3. Support scheduled collection and user-triggered on-demand collection through the same queue contract.
4. Avoid repeated collection for symbols that recently returned empty or partial enterprise data.
5. Preserve progress across deploys and restarts.
6. Make missing data visible through freshness state instead of hiding it behind slow page loads.
7. Let local development apply collector changes without requiring a full image rebuild.

## Runtime Topology

```text
Frontend
   |
   v
API service  ---- creates/reads ----> sync_requests
   |                                    |
   |                                    v
   +---- reads normalized tables <---- Collector service
                                      |
                                      v
                                Remote providers
```

### API Service Boundary

The API service can:

- read normalized data and raw local snapshots
- return `data_status` for missing or stale datasets
- create `sync_requests` rows for manual or on-demand refresh
- expose request status by reading database rows

The API service cannot:

- call provider clients
- start the scheduler
- construct or run sync pipelines
- wait for collector completion before returning a read response

### Collector Service Boundary

The collector service can:

- consume `sync_requests`
- run scheduled jobs
- run one-off repair jobs
- call provider clients with tokens and rate limits
- write normalized tables, raw payloads, jobs, items, and freshness rows

The collector service should not:

- serve frontend pages
- expose public read APIs
- depend on browser request timing
- create duplicate work for the same active scope

## Entry Points

### API Mode

Command:

```powershell
python -m stock_analyzer_app api
```

Behavior:

- starts FastAPI
- does not start APScheduler
- sets `STOCK_ANALYZER_SYNC_ENABLED=false` in Docker
- does not need provider tokens

### Collector Mode

Command:

```powershell
python -m stock_analyzer_app collector
```

Behavior:

- starts scheduler through `runtime.start_scheduler()`
- creates a `CollectorService`
- recovers abandoned claimed queue rows
- continuously processes pending requests

### Collect Once Mode

Command:

```powershell
python -m stock_analyzer_app collect --once --limit 10
```

Behavior:

- creates a `CollectorService`
- recovers abandoned claimed queue rows
- processes one batch and exits
- intended for tests, one-off repair, and scripted maintenance

## Database Contracts

### `sync_requests`

`sync_requests` is the API-to-collector queue.

Required fields:

| Field | Meaning |
| --- | --- |
| `id` | Queue id returned to API callers |
| `request_type` | Collector action, such as `full_daily_pipeline` |
| `dataset` | Logical dataset affected by the request |
| `scope_json` | JSON scope, usually date range or symbols |
| `priority` | Higher value is processed first |
| `status` | `pending`, `claimed`, `completed`, `failed`, or `cancelled` |
| `requested_by` | `api`, `collector`, `manual`, or test/runtime origin |
| `reason` | Human-readable reason such as `overview:on-demand:000001.SZ` |
| `created_at` | Queue creation time |
| `claimed_at` | Worker claim time |
| `finished_at` | Completion or failure time |
| `error_message` | Request-level failure text |

Queue ordering:

1. pending requests only
2. highest `priority` first
3. oldest `created_at` first for equal priority

### `dataset_freshness`

`dataset_freshness` records the last attempt and last successful state for a dataset scope.

Required fields:

| Field | Meaning |
| --- | --- |
| `dataset` | Logical dataset, such as `stock_research_context` |
| `scope_key` | `global` or a symbol such as `000001.SZ` |
| `latest_data_date` | Newest business data date when available |
| `last_success_at` | Last successful write time |
| `last_attempt_at` | Last attempt time, including empty results |
| `status` | `ready`, `partial`, `empty`, `failed`, `missing`, or `stale` |
| `rows_count` | Rows written for the scope |
| `missing_count` | Missing modules or symbols |
| `failed_count` | Failed modules or symbols |
| `owner_job_type` | Pipeline that owns the dataset |
| `summary_json` | Provider/module details |

Freshness is used for two different decisions:

- API responses can tell the frontend whether data is missing, stale, or ready.
- Collector planning can skip recently attempted empty scopes to avoid repeated provider calls.

## Queue Lifecycle

### Create

Requests are created by the API or collector:

- API creates manual refresh requests from `/api/sync/jobs`.
- API creates symbol-scoped on-demand enterprise requests from stock overview reads when `refresh_missing=true`.
- Collector creates automatic enterprise backfill requests for missing symbols.

Request creation must be non-blocking. The caller receives a queue row immediately.

### Deduplicate

The API checks for an active on-demand enterprise request before creating a new one.

Duplicate conditions:

- `request_type = fundamental_refresh_pipeline`
- `status in (pending, claimed)`
- `reason = overview:on-demand:<symbol>`
- `scope.symbols = [<symbol>]`

If the request exists, the API reuses it.

### Claim

The collector claims pending requests before running work. Claiming changes status to `claimed` and sets `claimed_at`.

The claim step is the concurrency boundary. Only a claimed request should run provider work.

### Execute

The collector maps request types to pipeline calls:

| Request Type | Pipeline Call |
| --- | --- |
| `full_daily_pipeline` | `run_full_daily_pipeline(start_date, end_date, symbols)` |
| `sync_daily_bars` | `run_full_daily_pipeline(start_date, end_date, symbols)` |
| `fundamental_refresh_pipeline` | `run_fundamental_refresh_pipeline(symbols)` |
| `market_structure_pipeline` | `run_market_structure_pipeline()` |

Unknown request types fail the request with an explicit error.

### Finish

After execution:

- success marks request `completed`
- exception marks request `failed` and stores `error_message`
- empty auto-enterprise scopes can complete without running a provider call after TTL filtering

### Recover

At collector startup, `recover_claimed_requests()` moves abandoned `claimed` rows back to `pending` when the repository supports it.

This protects against:

- container restarts
- process kills
- host shutdowns
- deployment interruptions

## Enterprise Data Collection

Enterprise data includes company profile, share capital, corporate actions, holders, officers, officer rewards, financial statements, financial metrics, and capital flow context.

The current highest-risk enterprise modules are holders and officers because the UI makes missing people data highly visible. The collector therefore supports both automatic backfill and on-demand refresh.

### Automatic Missing Backfill

Before each request-processing pass, the collector can enqueue one automatic enterprise backfill request.

Eligibility:

1. `STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE > 0`
2. repository implements `list_symbols_missing_enterprise_data`
3. symbol is not already in an active enterprise request
4. symbol has no recent freshness attempt within TTL

Created request:

```json
{
  "request_type": "fundamental_refresh_pipeline",
  "dataset": "stock_research_context",
  "scope": {"symbols": ["000001.SZ", "000002.SZ"]},
  "priority": 40,
  "requested_by": "collector",
  "reason": "enterprise:auto:missing"
}
```

### On-Demand Enterprise Refresh

When the user opens a stock page and passes `refresh_missing=true`, the API checks whether enterprise modules are missing. If they are missing:

1. If there is an active on-demand request for the same symbol, reuse it.
2. If there is a recent freshness attempt within TTL, skip creating a new request.
3. Otherwise create a high-priority request.

Created request:

```json
{
  "request_type": "fundamental_refresh_pipeline",
  "dataset": "stock_research_context",
  "scope": {"symbols": ["000001.SZ"]},
  "priority": 100,
  "requested_by": "api",
  "reason": "overview:on-demand:000001.SZ"
}
```

The API returns the current local snapshot immediately. It does not wait for the collector.

### TTL Rule

Configuration:

```text
STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS=7
```

Meaning:

- A symbol with `dataset_freshness(dataset=stock_research_context, scope_key=<symbol>)` and `last_attempt_at` within the TTL is considered recently attempted.
- Recent attempts are skipped for automatic backfill.
- Recent attempts are also skipped for API-created on-demand refresh.
- Attempts older than TTL can be retried.

This rule prevents repeated collection of known-empty Miana enterprise modules while still allowing later retry after the provider data changes.

## Priority Model

Recommended priority bands:

| Priority | Owner | Use |
| --- | --- | --- |
| 100 | API | User opened a symbol and requested missing enterprise data |
| 90 | API | Retry failed sync job |
| 80 | API | Single-symbol bars/detail refresh |
| 70 | API | Dashboard latest-market-data request |
| 50 | API/manual | Generic manual sync request |
| 40 | Collector | Automatic enterprise missing-data batch |
| 10-30 | Collector | Low-priority background enrichment |

The collector should process higher priority user-visible gaps before broad background backfills.

## Scheduling Model

The collector owns all scheduled jobs. API containers must not start scheduled work.

Current collector startup calls `runtime.start_scheduler()`, then queue processing begins.

Target scheduled datasets:

| Dataset Group | Target Time |
| --- | --- |
| Trading calendar and stock universe | before daily market collection |
| Previous trading day bars and adjusted bars | after close or after midnight data availability |
| Indicators and signals | after adjusted bars |
| Index overview and sector heat | after market structure data is collected |
| Enterprise data | continuous small batches |
| News/reports/metrics | continuous or market-open batch, depending on provider limits |

Calendar-aware scheduling should use the latest trading day from the trading calendar rather than simple calendar yesterday.

## Provider Rate Limits

Provider throttling belongs to collector mode only.

Important settings:

```text
STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE=500
STOCK_ANALYZER_SYNC_MAX_WORKERS=8
STOCK_ANALYZER_SYNC_RETRY_MAX_WORKERS=4
STOCK_ANALYZER_SYNC_RETRY_ROUNDS=3
STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE=5
```

Operational rule:

- Increase `STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE` to create larger batches.
- Increase provider request rate only when the upstream platform and local error rate support it.
- Do not let broad background batches starve on-demand requests.

## Docker Runtime Design

Docker services:

| Service | Command | Provider Tokens | Scheduler |
| --- | --- | --- | --- |
| `api` | `python -m stock_analyzer_app api` | no | no |
| `collector` | `python -m stock_analyzer_app collector` | yes | yes |
| `mysql` | MySQL 8.4 | no | no |

Development compose mounts current source into both `api` and `collector`:

```yaml
volumes:
  - ./stock_analyzer_app:/app/stock_analyzer_app
  - ./public:/app/public
  - ./db:/app/db
```

This prevents local services from continuing to run stale image code when Docker Hub or base image pulls are unavailable.

Production deployment may remove the source mounts and rely on immutable images once the build pipeline is reliable.

## API Status Contract

Read endpoints should expose freshness without blocking.

Example:

```json
{
  "data_status": {
    "dataset": "stock_research_context",
    "status": "missing",
    "latest_data_date": null,
    "pending_request_id": 123,
    "message": "collector request queued"
  }
}
```

The frontend should:

- show available local data immediately
- show missing modules as empty states
- show queued/running refresh state when a request exists
- poll request status if the user explicitly refreshed

The frontend should not show a long spinner while the API waits for provider calls, because the API should not wait for provider calls.

## Failure Handling

### Request-Level Failure

If a pipeline call raises an exception, the collector marks the request `failed` and writes `error_message`.

The request should not remain `claimed` after an exception.

### Item-Level Failure

Pipeline item failures should be stored in sync job items and summarized in job status. A request can complete even when some symbols fail if the pipeline successfully records partial results.

### Empty Provider Results

Empty enterprise modules are not always errors. They should update `dataset_freshness` with an empty or partial status and a last attempt timestamp so the TTL rule can prevent repeated requests.

### Abandoned Claims

Collector startup recovers claimed rows. A future hardening step should recover only claims older than a configured timeout instead of all claimed rows.

## Observability

The following views are needed for daily operations:

### Queue Backlog

Group by:

- status
- request type
- reason
- priority band

Useful SQL:

```sql
SELECT status, request_type, reason, COUNT(*) AS cnt
FROM sync_requests
GROUP BY status, request_type, reason
ORDER BY status, request_type, reason;
```

### Freshness Coverage

Group by:

- dataset
- status
- latest update

Useful SQL:

```sql
SELECT dataset, status, COUNT(*) AS cnt, MAX(updated_at) AS latest_update
FROM dataset_freshness
GROUP BY dataset, status
ORDER BY dataset, status;
```

### Stuck Work

Rows to inspect:

- `claimed` requests with old `claimed_at`
- repeated `failed` requests for the same reason
- symbols with old `partial` freshness
- provider endpoints with high empty or failure rates

## Operational Runbook

### Check Services

```powershell
docker compose ps -a
```

Expected:

- `stock_analyzer_api` is up
- `stock_analyzer_collector` is up
- `stock_analyzer_mysql` is healthy

### Check Collector Config

```powershell
docker compose exec -T collector python -c "import os; print(os.getenv('STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS'), os.getenv('STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE'))"
```

Expected default:

```text
7 5
```

### Pause Collector For Tests

Because local tests and the running collector can share the same MySQL, stop collector before a full Docker-backed test suite:

```powershell
docker compose stop collector
docker compose run --rm -v "${PWD}:/work" -w /work api python -m pytest -q
docker compose up -d --no-build collector
```

### Verify Code Loaded In Containers

When using source mounts:

```powershell
docker compose exec -T api python -c "import importlib; m=importlib.import_module('stock_analyzer_app.api.app'); print(hasattr(m, '_enqueue_enterprise_on_demand_request'))"
docker compose exec -T collector python -c "import stock_analyzer_app.collector as c; print(hasattr(c.CollectorService, '_recent_enterprise_attempt'))"
```

Both commands should print `True`.

## Test Strategy

### Unit Tests

Collector tests should cover:

- pending request processing
- completed requests are skipped
- pending requests are not starved by completed rows
- automatic enterprise missing-data batch creation
- active enterprise requests are deduplicated
- claimed requests are recovered
- on-demand requests are processed before auto batches
- recent freshness attempts are filtered from auto batches

### API Tests

API tests should cover:

- read endpoints do not run pipelines
- manual sync endpoints create requests and return `202`
- dashboard stale data creates queue state instead of blocking
- stock overview on-demand refresh reuses active requests
- stock overview skips recent enterprise attempts
- stock bars refresh creates a single-symbol request

### MySQL Repository Tests

Repository tests should cover:

- `sync_requests` create, list, get, claim, finish
- `dataset_freshness` upsert and read
- enterprise missing-symbol listing with TTL
- test cleanup removes symbol-scoped sync requests

### Docker Compose Tests

Compose tests should cover:

- separate `api` and `collector` services exist
- API command is `python -m stock_analyzer_app api`
- collector command is `python -m stock_analyzer_app collector`
- provider tokens are only exposed to collector
- source mounts exist for local development

## Known Limitations

1. The collector currently runs a simple single-process polling loop.
2. Recovering claimed requests is coarse and should become timeout-based.
3. `sync_requests` does not yet have a unique key for active on-demand symbol requests; deduplication is implemented in application logic.
4. Provider call diagnostics are not yet stored in a dedicated table.
5. Full-market enterprise backfill speed depends on provider rate limits and batch size.
6. API status responses are not yet consistently normalized across all read endpoints.
7. Production image rebuilds still depend on reliable access to the Python base image unless a local mirror or pinned base image cache is used.

## Next-Version Enhancements

### Queue Hardening

- Add claim timeout recovery instead of recovering all claimed requests.
- Add attempt counts and next retry time to `sync_requests`.
- Add optional dedupe key for request scope.
- Add request cancellation API.

### Collector Scaling

- Separate scheduler leader from queue workers.
- Allow multiple worker processes to claim rows safely.
- Add per-dataset worker pools.
- Prevent low-priority background jobs from consuming all provider quota.

### Dataset Manifest

- Add a collector-owned manifest that defines dataset scope, freshness SLA, owner pipeline, and priority.
- Use the manifest to create daily scheduled requests.
- Use the manifest to render Data Center coverage.

### Observability

- Add provider call log table.
- Add collector heartbeat table.
- Add Data Center panels for backlog, stuck claimed requests, and stale datasets.
- Add per-provider request rate and error summaries.

### API Consistency

- Return normalized `data_status` on all optional datasets.
- Return active `request_id` for missing data when one exists.
- Avoid duplicate `sync_requests` for dashboard auto-refresh and symbol detail refresh.

## Acceptance Criteria

Collector service design is satisfied when:

1. API mode can run without provider tokens.
2. API read endpoints do not call pipelines.
3. Collector mode is the only runtime that calls providers.
4. Manual and on-demand refresh requests return immediately as queue rows.
5. On-demand enterprise refresh is deduplicated per active symbol request.
6. Recent empty or partial enterprise attempts are skipped within TTL.
7. Collector recovers abandoned claimed requests on startup.
8. Local Docker services load current source code without requiring an image rebuild.
9. Full tests pass with collector stopped and can be followed by restarting collector.
10. Operators can inspect backlog and freshness with simple database queries.
