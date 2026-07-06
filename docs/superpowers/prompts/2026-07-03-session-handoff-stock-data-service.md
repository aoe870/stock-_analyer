# Stock Data Service Session Handoff

Date: 2026-07-03

## Current Goal

Support Miana as a data source, store multi-source data, and run a large full-history sync with controlled concurrency.

## Key Decisions

- Miana is the primary provider now, with fallback to `akshare` and `eastmoney`.
- Full-history sync should use controlled concurrency, not a naive serial loop.
- Miana requests are rate-limited to 500/minute.
- `detail` / tick-level data is not part of the default full sync.

## Config

- `STOCK_ANALYZER_MIANA_TOKEN` is set in local `.env`.
- `STOCK_ANALYZER_PROVIDER_PRIORITY=miana,tushare,akshare,eastmoney`
- `STOCK_ANALYZER_SYNC_MAX_WORKERS=16`
- `STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE=500`

## Code Changes Already Made

- Added Miana provider integration.
- Added multi-source storage tables and raw payload archive.
- Added concurrency and rate limiting in the sync pipeline.
- Added job dedup / stale-running cleanup logic.

## Current Sync Status

- Latest fresh sync job: `138`
- Status: `running`
- Started at: `2026-07-03 05:27:59`
- Universe size: `5859`
- Processed so far: `31`
- Success: `30`
- Failure: `0` at the last checked moment

## Recent Verification

- Focused tests passed after the concurrency change.
- Full test suite passed: `92 passed`

## How To Resume

1. Check job `138` status and item progress.
2. If the service is down, restart the backend first.
3. If a stale `full_daily_pipeline` is still marked running, cancel stale rows in `sync_jobs` before starting a new one.
4. Continue watching Miana success rate and failures.

## Useful Files

- [App settings](../../../stock_analyzer_app/config/settings.py)
- [Miana provider](../../../stock_analyzer_app/data_provider/miana_provider.py)
- [Sync pipeline](../../../stock_analyzer_app/sync/pipeline.py)
- [API app](../../../stock_analyzer_app/api/app.py)
- [Handoff prompt](../prompts/2026-06-27-codex-handoff-stock-data-service.md)
