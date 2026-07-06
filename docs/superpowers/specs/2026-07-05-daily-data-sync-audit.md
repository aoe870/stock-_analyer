# Daily Data Sync Audit

Date: 2026-07-05

## Purpose

This document reviews the current stock data update path and identifies what is still needed to make daily automatic updates reliable enough to support downstream screening, backtesting, and analysis.

## Current Update Flow

The application starts the scheduler in `stock_analyzer_app/__main__.py` by calling `runtime.start_scheduler()`.

`SchedulerService` registers one APScheduler cron job:

- Job id: `full_daily_pipeline`
- Configured time: `STOCK_ANALYZER_SYNC_TIME`
- Current local value: `00:00`
- Timezone: `Asia/Shanghai`
- Execution: `run_daily_pipeline_once()`

When triggered, the scheduler now runs:

```text
target_date = today - 1 calendar day
run_full_daily_pipeline(start_date=target_date, end_date=target_date, requested_by="scheduler")
```

The intended product behavior is different:

- Daily automatic sync at `00:00 Asia/Shanghai` should sync the previous day's data.
- Intraday or real-time data should be synced on demand only when the user opens a specific stock detail view.
- The scheduled job should support baseline analysis data; the on-demand stock detail sync should enrich or refresh one symbol when needed.

The full daily pipeline then:

1. Builds the provider chain from `STOCK_ANALYZER_PROVIDER_PRIORITY`.
2. Fetches the stock universe unless a symbol list is explicitly supplied.
3. Upserts `stocks` and Miana provider profile rows.
4. Fetches bars, adjusted bars, adjustment factors, analysis bars, indicators, and strategy signals per symbol.
5. Persists optional side data such as company profile, corporate actions, share capital, and money flow when available.
6. Records symbol-level success or failure in `sync_job_items`.
7. Marks the job as `completed`, `completed_with_errors`, or `failed`.

## Current Strengths

- Symbol-level isolation is implemented. One failed symbol does not fail the whole job.
- Provider fallback exists through the provider chain: `miana,tushare,akshare,eastmoney`.
- Miana request rate limiting exists.
- Full pipeline concurrency is configurable with `STOCK_ANALYZER_SYNC_MAX_WORKERS`.
- Sync jobs and item-level failures are persisted.
- Manual retry endpoint now exists:

```text
POST /api/sync/jobs/{job_id}/retry
```

It retries only failed symbols from the source job and records `requested_by="retry:{job_id}"`.
- Scheduled jobs now retry failed symbols automatically after the main scheduled run.
- Scheduled retry uses configurable lower concurrency:
  - `STOCK_ANALYZER_SYNC_RETRY_MAX_WORKERS`
  - `STOCK_ANALYZER_SYNC_RETRY_ROUNDS`
- Stock detail bars can trigger one-symbol refresh with:

```text
GET /api/stocks/{symbol}/bars?refresh=true
```

- Data readiness is exposed through:

```text
GET /api/sync/readiness
```

## Evidence From Current Database

Latest inspected sync jobs:

- Job `138`: initial full sync, `completed_with_errors`, `3977` success, `1553` failed.
- Job `139`: first retry, `1236` success, `317` failed.
- Job `140`: second retry, `240` success, `77` failed.
- Job `141`: third retry, `73` success, `4` failed.
- Job `142`: final retry, `2` success, `2` failed.

Analysis table evidence:

- Latest `analysis_daily_bars.trade_date`: `2026-07-03`
- Total analysis symbols: `5532`
- Total analysis rows: `10226291`
- Active Miana symbols matching A-share code format: `5530`
- Symbols with analysis rows on `2026-07-03`: `2334`
- Active Miana symbols without `2026-07-03` analysis rows: `3201`

Sample coverage check:

```text
000001.SZ analysis range: 1991-04-03 to 2024-12-31
300750.SZ analysis range: 2018-06-11 to 2026-07-03
600000.SH analysis range: 1999-11-10 to 2026-07-01
688001.SH analysis range: 2019-07-22 to 2026-07-03
```

This shows the current store is useful, but latest-date coverage is not complete enough to treat the data foundation as fully reliable yet.

## Gaps That Must Be Addressed

### 1. Midnight Sync Targets The Previous Calendar Day

At `00:00 Asia/Shanghai`, the scheduler now targets the previous calendar day for the full-universe daily sync.

Remaining improvement: once trading calendar support is reliable, the previous calendar day should be resolved to the latest completed open trading day.

Current behavior:

- At `00:00`, run the scheduled daily pipeline for `yesterday`.
- Treat weekends and holidays as normal no-new-data days or skip days rather than failed data days.
- Keep intraday or real-time refresh out of the scheduled full-universe job; trigger it only from the stock detail flow for the requested symbol.

### 2. Miana K-Line Pagination Is Missing

Miana `_fetch_kline()` currently sends:

```text
limit=2000
order=ASC
```

For long-listed stocks, a full-history request from `1990-12-19` can return only the earliest 2000 rows, not the latest rows. This explains why older symbols such as `000001.SZ` do not have complete recent analysis coverage.

Implemented behavior:

- Miana K-line requests are split into date segments instead of issuing one full-history request.
- This avoids relying on one `limit=2000` response for long-listed stocks.

Remaining recommended behavior:

- Add coverage verification after full sync: each active symbol should have a latest analysis date close to the market latest date unless it is suspended, delisted, or provider-empty.

### 3. Scheduler Guard Can Be Blocked By Stale Running Jobs

The API path uses `_active_sync_job()` with recent-activity detection. The scheduler path uses `SyncSchedulerGuard.can_start()`, which only calls `repository.has_running_job()`.

If a job remains `running` after a process crash or stuck worker, future scheduled jobs can be skipped indefinitely.

Implemented behavior:

- Scheduler guard now detects stale `pending` or `running` jobs.
- Mark stale jobs as `failed` or `stale_cancelled` before starting the next scheduled job.
- Record the stale cutoff in the job summary.

### 4. Failed Item Retry Is Manual, Not Automatic

The retry endpoint exists, and scheduled jobs now automatically retry failed symbols after the scheduled run.

Implemented behavior:

- After a scheduled job completes with failed items, enqueue or directly start a retry job for failed symbols.
- Use lower concurrency for retry jobs, such as 2-4 workers.
- Limit retry rounds, for example 3 rounds per source job.
- Leave deterministic provider errors as final failures with clear reason text.

### 5. On-Demand Real-Time Stock Detail Sync Is A Separate Path

The intended behavior is that daily scheduled sync maintains baseline historical and previous-day analysis data. Real-time or intraday refresh should only happen when a user opens a stock detail page.

Implemented behavior:

- Stock bars endpoint supports `refresh=true` to trigger a one-symbol detail refresh.
- Do not run full-universe real-time sync from the scheduler.
- Persist stock-detail refreshes as their own job type or as `full_daily_pipeline` jobs with explicit `symbols=[...]` and `requested_by="detail:{symbol}"`.
- Daily analysis readiness checks remain based on completed analysis bars, not partially refreshed intraday data.

### 6. No Data Readiness Gate Exists

Downstream analysis now has a basic readiness endpoint.

Implemented behavior:

- `GET /api/sync/readiness` returns:
  - latest market date
  - symbols expected
  - symbols updated
  - missing symbols
  - failed symbols
  - ready_for_analysis boolean

Remaining recommended behavior:

- Screening and backtest endpoints should report when requested data is stale or incomplete.

### 7. Trading Calendar Is Not Reliable Yet

`MianaProvider.fetch_trading_calendar()` currently returns an empty list. This means the system cannot reliably distinguish:

- normal weekend or holiday
- provider not returning data
- missing data due to sync failure

Recommended behavior:

- Use a provider that returns a real A-share trading calendar.
- Persist recent and future calendar rows.
- Make scheduler target the latest completed open trading date.

## Recommended Completion Path

### Phase 1: Make Daily 00:00 Sync Target The Previous Day

Status: implemented with previous calendar day.

```text
target_date = today - 1 calendar day
start_date = target_date
end_date = target_date
requested_by = scheduler
```

Remaining improvement: once trading calendar data is reliable, replace calendar-day `yesterday` with the latest completed open trading day.

### Phase 2: Add Automatic Retry After Scheduled Jobs

Status: implemented.

When a scheduled job finishes with failed symbols:

1. Create a retry job for failed symbols.
2. Use low concurrency.
3. Repeat up to a configured retry limit.
4. Preserve the source job id in `requested_by` or summary metadata.

### Phase 3: Fix Miana Historical Pagination

Status: implemented with date-windowed fetching.

### Phase 4: Add Readiness Reporting

Status: implemented as `GET /api/sync/readiness`.

Create a data readiness endpoint or repository method that answers whether the latest trading day is complete enough for analysis.

Example output:

```json
{
  "latest_trade_date": "2026-07-03",
  "expected_symbols": 5530,
  "updated_symbols": 5528,
  "failed_symbols": 2,
  "ready_for_analysis": false
}
```

### Phase 5: Add On-Demand Stock Detail Refresh

Status: implemented as `GET /api/stocks/{symbol}/bars?refresh=true`.

When the user opens a stock detail page:

1. Check whether the symbol has fresh enough detail data.
2. If stale or missing, run a one-symbol refresh job.
3. Return existing cached data immediately when possible.
4. Surface refresh status separately from scheduled daily sync readiness.

## Current Verdict

The update system has a solid foundation: provider chain, concurrent pipeline, persisted jobs, symbol-level failures, and manual failed-symbol retry are in place.

After the implementation pass, the core daily automation path is stronger:

1. Midnight scheduler targets the previous calendar day.
2. Scheduled jobs automatically retry failed items with configurable retry rounds and retry concurrency.
3. Stale running jobs are cancelled by the scheduler guard.
4. Miana K-line fetching is segmented by date range.
5. On-demand stock detail refresh exists.
6. Data readiness reporting exists.

The remaining hardening work is to add a reliable A-share trading calendar and make analysis endpoints enforce or report readiness when data is incomplete.
