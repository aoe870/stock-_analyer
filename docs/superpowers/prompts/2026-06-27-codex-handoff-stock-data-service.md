# Codex Handoff Prompt: Stock Data Service Implementation

You are working in the repository `D:\Develop\soucre\stock _analyer`.

Stop following the older CSV/sample-only implementation direction. The current source of truth is:

`docs/superpowers/specs/2026-06-27-expma-stock-analysis-web-design.md`

Read that design document carefully before making further code changes. Implement according to the updated design.

## Core Direction

Build a local A-share stock data service and analysis app.

The backend has two logical subsystems inside one FastAPI application for version 1:

1. Data acquisition.
2. Data aggregation and analysis.

Do not split these into separately deployed services in version 1. Keep module, table, API, and task boundaries clean so a future `stock-data-sync-worker` can be extracted later.

## Version 1 Scope

Implement A-share daily data only.

Included:

- Stock universe.
- Trading calendar.
- Daily OHLCV bars.
- Adjustment factors.
- ST status and suspension/market-open status when provider support exists.
- MySQL storage.
- Data sync jobs.
- Aggregated analysis daily bars.
- EXPMA17/50 indicators and materialized strategy signals.
- Screening.
- Backtesting.
- Sync/status APIs and local UI.

Excluded for version 1:

- Minute bars.
- Real-time quotes.
- Financial statements.
- Valuation factors.
- Multi-factor ranking.
- HK/US/ETF expansion.
- Live trading.

## Required Architecture

Use these package boundaries:

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

Provider adapters must not write directly to MySQL. They return normalized dictionaries to sync services. Sync services own persistence, retry, fallback, and job logging.

Screening and backtesting must read local MySQL analysis data. They should not call external providers during normal user analysis requests.

## Storage and Scripts

Implement MySQL 8.x storage and migration scripts.

Required files:

- `docker-compose.yml`
- `db/migrations/001_create_core_schema.sql`
- `db/migrations/002_create_analysis_schema.sql`
- `db/migrations/003_create_run_history_schema.sql`
- `db/seeds/001_default_settings.sql`
- `scripts/init_db.ps1`
- `scripts/migrate_db.ps1`
- `scripts/seed_db.ps1`
- `scripts/dev_server.ps1`
- `scripts/sync_once.ps1`
- `scripts/deploy_local.ps1`
- `scripts/backup_db.ps1`
- `scripts/restore_db.ps1`

Migration rules:

- Track applied migrations in `schema_migrations`.
- Apply migrations in filename order.
- Compute and store SHA-256 checksums.
- Refuse to continue if an already-applied migration changed.
- Scripts must be idempotent and must not drop user data.

## Provider Defaults

Provider priority:

1. Tushare when `STOCK_ANALYZER_TUSHARE_TOKEN` is configured.
2. AkShare/Eastmoney fallback.
3. CSV import only for manual repair, tests, and local experiments.

Provider contract:

- `fetch_stock_universe()`
- `fetch_trading_calendar(exchange, start_date, end_date)`
- `fetch_daily_bars(symbol, start_date, end_date)`
- `fetch_adjustment_factors(symbol, start_date, end_date)`
- `fetch_stock_status(symbols, trade_date)` when supported

## Scheduler

Use APScheduler as the version 1 scheduler.

Requirements:

- Runs inside the FastAPI process unless disabled.
- Writes durable execution records to `sync_jobs`.
- Does not start duplicate daily pipeline jobs if one is already running.
- Shares the same task execution path for scheduled and manual jobs.
- Can be disabled with `STOCK_ANALYZER_SYNC_ENABLED=false`.

## Price and Recompute Policy

Store unadjusted market bars and forward-adjusted analysis bars.

Default analysis and backtesting price mode: `forward_adjusted`.

If forward-adjusted data is unavailable, fallback to `unadjusted` only when clearly marked in metadata.

When daily bars or adjustment factors change:

1. Rebuild `analysis_daily_bars`.
2. Rebuild `daily_indicators`.
3. Rebuild `strategy_signals`.
4. Start recomputation from 60 trading rows before the earliest changed date.
5. Mark overlapping cached screening/backtest results as stale; do not automatically rerun them in version 1.

## Failure and Coverage Policy

Partial sync success is allowed.

- If some items fail and some succeed, sync job status should be `completed_with_errors`.
- Screening allows partial coverage by default and reports evaluated/skipped/missing/error counts.
- Backtest requires sufficient coverage by default.
- Backtest may skip incomplete symbols only when the request explicitly sets `allow_partial_coverage=true`.
- Coverage checks must use `analysis_daily_bars`, not raw provider tables.

## Development Discipline

Keep existing user or other-agent changes unless the user explicitly asks to revert them.

Use test-first implementation for storage, sync, aggregation, indicators, screening, backtest, API, and scripts.

Before finishing, run relevant tests and report exactly what passed or failed.

Do not commit unrelated untracked files unless the user asks.

If the old implementation plan conflicts with the updated design document, the updated design document wins.
