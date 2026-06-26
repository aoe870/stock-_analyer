# EXPMA Stock Analysis Data Service Design

## Purpose

Build a local stock analysis service for A-share research. The service continuously synchronizes stock market data into a local database, derives normalized and aggregated analysis data, and exposes screening, stock-detail, and backtest APIs for a browser UI.

The first version focuses on:

- Automatic daily synchronization of A-share stock data.
- Local MySQL storage for raw, normalized, aggregated, and analysis results.
- Indicator-based stock screening.
- Historical backtesting.
- A built-in EXPMA17/50 trend pullback strategy based on the supplied Tongdaxin formula.
- Local browser operation with no required cloud service.

This tool is for research and engineering use only. It does not provide investment advice.

## Version 1 Decisions

These decisions are fixed for the first implementation so worker agents do not need to re-open architecture questions while coding:

- Market scope: A-share daily data only.
- Data scope: stock list, trading calendar, daily OHLCV bars, adjustment factors, ST status, and suspension/market-open status when the provider supports it.
- Out of scope for version 1: minute bars, real-time quotes, financial statements, valuation factors, multi-factor ranking, HK/US/ETF expansion, and live trading.
- Providers: Tushare first when `STOCK_ANALYZER_TUSHARE_TOKEN` is configured; AkShare/Eastmoney fallback; CSV import only for manual repair, tests, and local experiments.
- Storage: MySQL 8.x is required for the service database.
- Runtime shape: one FastAPI backend process with logical data-acquisition and analysis subsystems; do not split into separately deployed services in version 1.
- Scheduler: APScheduler is the default in-process scheduler.
- Deployment: provide local Windows PowerShell scripts and Docker Compose for MySQL.
- Price modes: store unadjusted bars and forward-adjusted analysis bars; backtests and screening use `forward_adjusted` by default and clearly mark fallback to `unadjusted`.
- Failure policy: partial sync success is allowed; screening continues with available symbols and reports missing/failed coverage; backtest requires sufficient coverage unless the request explicitly allows partial coverage.
- Recompute policy: when daily bars or adjustment factors change, recompute analysis bars, indicators, and signals from 60 trading rows before the earliest changed date through the latest affected date.

## Product Shape

The application is a local data service plus Web UI:

- Backend: FastAPI service.
- Frontend: browser UI for sync status, stock detail, screening, and backtests.
- Storage: MySQL for stock metadata, raw provider payloads, normalized bars, derived indicators, strategy signals, sync jobs, strategy settings, and backtest runs.
- Data acquisition: provider adapters and scheduled jobs that synchronize stock universe and market data.
- Data aggregation and analysis: normalization, quality checks, adjusted price preparation, indicator calculation, signal generation, screening, and backtesting.
- Core logic: pure Python modules for deterministic indicators, strategy signals, screening, and backtesting.

The app should run locally and expose a browser URL such as `http://127.0.0.1:8000`.

## Backend Architecture

The backend has two primary subsystems:

1. Data acquisition.
2. Data aggregation and analysis.

These subsystems communicate through MySQL tables and small repository interfaces. Provider-specific code does not leak into strategy, screening, or backtest modules.

In version 1 these are logical subsystems inside one backend application, not two separately deployed services. The project should keep module, table, API, and task boundaries clean so data acquisition can later be split into an independent worker process without rewriting analysis code.

Recommended version 1 runtime:

- One FastAPI application process serving APIs and static UI.
- One APScheduler-backed in-process scheduler/background task runner for sync and aggregation jobs.
- One MySQL database shared by data acquisition and analysis modules.

Future split, when scale requires it:

- `stock-data-sync-worker`: owns provider calls, sync jobs, retries, and raw/canonical market data writes.
- `stock-analysis-api`: owns query APIs, screening, backtesting, stock detail, and result history.
- Communication remains through MySQL first; a durable queue can be added later for job dispatch.

### Backend Modules

`stock_analyzer_app/`

- `api/`
  - FastAPI routers for sync status, stock data, screening, backtests, strategy metadata, and run history.
- `config/`
  - Environment and UI-editable settings, including MySQL connection, Tushare token, provider priority, sync schedule, cache TTL, fee, slippage, and default data source mode.
- `data_provider/`
  - Unified provider interface for stock universe, trading calendar, daily OHLCV bars, adjustment factors, suspension status, ST status, and optional basic market fields.
  - Tushare is preferred when a token is configured and the requested endpoint is available.
  - AkShare/Eastmoney public data is the fallback path.
  - CSV import remains available as a manual fallback and test fixture source.
- `sync/`
  - Scheduled and manual data synchronization jobs.
  - Handles incremental sync, retry, provider fallback, symbol-level failure isolation, and sync logs.
- `storage/`
  - MySQL schema, migrations, repository helpers, and transaction boundaries.
  - Stores raw provider snapshots, normalized daily bars, stock metadata, sync job state, derived indicators, strategy signals, screening results, and backtest outputs.
- `aggregation/`
  - Converts raw provider payloads into canonical tables.
  - Validates required fields, de-duplicates rows, aligns trading dates, applies adjustment factors where available, and prepares analysis-ready daily bars.
- `indicators/`
  - EMA/EXPMA, CROSS, REF, and shared series helpers.
  - Indicator functions are deterministic and independent from data providers and storage.
- `strategies/`
  - Strategy signal generation.
  - The EXPMA17/50 strategy lives here and returns signal rows, not trades.
- `screening/`
  - Batch evaluation for a stock universe on a target date.
  - Reads analysis-ready bars/signals from MySQL and produces ranked or filtered candidates.
- `backtest/`
  - Converts strategy signals into trades using the selected execution model.
  - Computes equity curve, positions, trades, and performance metrics.
- `tasks/`
  - In-process task orchestration for sync, aggregation, screening, and backtests.
  - The API contract should allow later migration to a durable queue.

## Data Flow

### Daily Sync Flow

1. Scheduler starts a sync job after the A-share trading day is expected to be complete, or the user triggers a manual sync.
2. The job refreshes trading calendar and stock universe metadata.
3. The job determines missing or stale symbol/date ranges from MySQL.
4. Provider adapters fetch raw data by symbol/date range.
5. Raw responses are stored for audit when practical.
6. Aggregation normalizes rows into canonical daily bar records.
7. Quality checks reject or quarantine invalid rows.
8. Adjustment factors are merged when available.
9. Analysis-ready bars are upserted.
10. Indicator and strategy signal tables are recalculated for affected symbols and date ranges.
11. The sync job records success, skipped, failed, retryable, and provider-fallback counts.

### Analysis Flow

Screening and backtesting should prefer local MySQL data. They should not call external providers during normal analysis requests.

- Screening reads the latest available signals for the selected date/universe.
- Stock detail reads daily bars, indicators, and signal markers.
- Backtesting reads analysis-ready bars/signals from MySQL for the requested date range.
- If required data is missing, the API returns a clear data coverage error and may optionally offer to start a sync job.

This separation keeps external data instability out of user-facing analysis workflows.

## Storage Design

Storage uses MySQL as the system of record.

Recommended first-version deployment:

- MySQL 8.x.
- `utf8mb4` character set.
- `InnoDB` tables.
- UTC timestamps for service metadata.
- Local trading dates stored as `DATE`.
- Decimal numeric columns for prices and amounts where exact persistence matters.

Local development should include `docker-compose.yml` for MySQL. The application must also support connecting to an existing MySQL instance through environment variables.

### Core Tables

`stocks`

- `symbol` primary identifier, such as `000001.SZ`.
- `exchange`, `name`, `list_date`, `delist_date`.
- `is_active`, `is_st`, `industry`, `source`, `updated_at`.

`trading_calendar`

- `exchange`, `trade_date`, `is_open`.
- Optional previous/next trading date fields for fast backtest execution lookup.

`raw_provider_payloads`

- Provider audit table for important sync responses.
- Fields: `id`, `provider`, `endpoint`, `symbol`, `trade_date`, `payload_hash`, `payload_json`, `fetched_at`.
- Raw payload storage may be limited by retention settings if disk use becomes high.

`daily_bars`

- Canonical daily OHLCV rows.
- Fields: `symbol`, `trade_date`, `open`, `high`, `low`, `close`, `volume`, `amount`, `source`, `is_adjusted`, `created_at`, `updated_at`.
- Unique key: `(symbol, trade_date, is_adjusted, source)`.

`adjustment_factors`

- Fields: `symbol`, `trade_date`, `adj_factor`, `source`, `updated_at`.
- Used to prepare forward-adjusted analysis bars when provider data is unadjusted.

`analysis_daily_bars`

- Preferred bars for analysis and backtesting.
- Fields: `symbol`, `trade_date`, `open`, `high`, `low`, `close`, `volume`, `amount`, `adj_factor`, `price_mode`, `source`, `data_quality`, `updated_at`.
- Unique key: `(symbol, trade_date, price_mode)`.
- First version uses `price_mode = forward_adjusted` when possible, otherwise `unadjusted`.

`daily_indicators`

- Derived indicator values by symbol/date/parameter set.
- Fields: `symbol`, `trade_date`, `strategy_key`, `expma17`, `expma50`, `cross_price`, `cross_in_kline`, `warmup_ready`, `updated_at`.
- Unique key: `(symbol, trade_date, strategy_key)`.

`strategy_signals`

- Raw boolean flags and selected signal.
- Fields: `symbol`, `trade_date`, `strategy_key`, `selected_signal`, `raw_flags_json`, `trend_state`, `updated_at`.
- Unique key: `(symbol, trade_date, strategy_key)`.

`sync_jobs`

- One row per sync execution.
- Fields: `id`, `job_type`, `status`, `requested_by`, `started_at`, `finished_at`, `provider_priority_json`, `summary_json`, `error_message`.

`sync_job_items`

- Per-symbol or per-date sync details.
- Fields: `id`, `job_id`, `symbol`, `trade_date`, `status`, `provider`, `attempt_count`, `error_message`, `updated_at`.

`screening_runs`

- Stores user-triggered screening requests and summary metadata.
- Fields: `id`, `strategy_key`, `trade_date`, `universe_json`, `filters_json`, `status`, `summary_json`, `created_at`, `finished_at`.

`screening_results`

- Stores rows returned by a screening run.
- Fields: `run_id`, `symbol`, `trade_date`, `close`, `expma17`, `expma50`, `selected_signal`, `trend_state`, `score`, `reason_json`.

`backtest_runs`

- Stores backtest request and summary metrics.
- Fields: `id`, `strategy_key`, `symbols_json`, `start_date`, `end_date`, `initial_capital`, `fee_rate`, `slippage_rate`, `price_mode`, `status`, `summary_json`, `created_at`, `finished_at`.

`backtest_trades`

- Executed and unfilled trade records.
- Fields: `run_id`, `symbol`, `signal_date`, `execution_date`, `signal`, `action`, `price`, `quantity`, `fee`, `slippage`, `position_before`, `position_after`, `is_filled`.

`backtest_equity`

- Daily equity rows.
- Fields: `run_id`, `trade_date`, `equity`, `cash`, `market_value`, `drawdown`, `positions_json`.

`settings`

- Key/value settings controlled by environment or UI.
- Sensitive secrets such as Tushare token should be stored outside the database when possible, or encrypted if stored.

### Physical Schema Requirements

The implementation must include versioned SQL migration files. The first migration should create the database objects below. Column names may be extended later, but the first implementation should keep these core fields and indexes stable.

Recommended migration layout:

- `db/migrations/001_create_core_schema.sql`
- `db/migrations/002_create_analysis_schema.sql`
- `db/migrations/003_create_run_history_schema.sql`
- `db/seeds/001_default_settings.sql`

The service should create the database if it is missing, then apply migrations in filename order. Applied migrations must be tracked in a `schema_migrations` table.

Required migration tracking table:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(64) PRIMARY KEY,
    checksum CHAR(64) NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Core market data tables:

```sql
CREATE TABLE stocks (
    symbol VARCHAR(16) PRIMARY KEY,
    exchange VARCHAR(8) NOT NULL,
    name VARCHAR(128) NOT NULL,
    industry VARCHAR(128) NULL,
    list_date DATE NULL,
    delist_date DATE NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_st BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_stocks_exchange_active (exchange, is_active),
    KEY idx_stocks_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE trading_calendar (
    exchange VARCHAR(8) NOT NULL,
    trade_date DATE NOT NULL,
    is_open BOOLEAN NOT NULL,
    previous_trade_date DATE NULL,
    next_trade_date DATE NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (exchange, trade_date),
    KEY idx_calendar_open_date (exchange, is_open, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE daily_bars (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 6) NOT NULL,
    high DECIMAL(18, 6) NOT NULL,
    low DECIMAL(18, 6) NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    volume DECIMAL(24, 4) NOT NULL,
    amount DECIMAL(24, 4) NOT NULL,
    source VARCHAR(32) NOT NULL,
    is_adjusted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, is_adjusted, source),
    KEY idx_daily_bars_date (trade_date),
    CONSTRAINT fk_daily_bars_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE adjustment_factors (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    adj_factor DECIMAL(18, 8) NOT NULL,
    source VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, source),
    KEY idx_adjustment_date (trade_date),
    CONSTRAINT fk_adjustment_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Provider audit and sync tables:

```sql
CREATE TABLE raw_provider_payloads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(32) NOT NULL,
    endpoint VARCHAR(64) NOT NULL,
    symbol VARCHAR(16) NULL,
    trade_date DATE NULL,
    payload_hash CHAR(64) NOT NULL,
    payload_json JSON NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_raw_payload (provider, endpoint, symbol, trade_date, payload_hash),
    KEY idx_raw_payload_symbol_date (symbol, trade_date),
    KEY idx_raw_payload_fetched (fetched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sync_jobs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_type VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    requested_by VARCHAR(32) NOT NULL,
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    provider_priority_json JSON NULL,
    summary_json JSON NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_sync_jobs_status (status, created_at),
    KEY idx_sync_jobs_type_created (job_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sync_job_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id BIGINT NOT NULL,
    symbol VARCHAR(16) NULL,
    trade_date DATE NULL,
    date_start DATE NULL,
    date_end DATE NULL,
    status VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NULL,
    attempt_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_sync_items_job_status (job_id, status),
    KEY idx_sync_items_symbol_date (symbol, trade_date),
    CONSTRAINT fk_sync_items_job FOREIGN KEY (job_id) REFERENCES sync_jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Analysis tables:

```sql
CREATE TABLE analysis_daily_bars (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 6) NOT NULL,
    high DECIMAL(18, 6) NOT NULL,
    low DECIMAL(18, 6) NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    volume DECIMAL(24, 4) NOT NULL,
    amount DECIMAL(24, 4) NOT NULL,
    adj_factor DECIMAL(18, 8) NULL,
    price_mode VARCHAR(32) NOT NULL,
    source VARCHAR(32) NOT NULL,
    data_quality VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, price_mode),
    KEY idx_analysis_date_mode (trade_date, price_mode),
    KEY idx_analysis_quality (data_quality),
    CONSTRAINT fk_analysis_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE daily_indicators (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    strategy_key VARCHAR(64) NOT NULL,
    expma17 DECIMAL(18, 6) NULL,
    expma50 DECIMAL(18, 6) NULL,
    cross_price DECIMAL(18, 6) NULL,
    cross_in_kline BOOLEAN NOT NULL DEFAULT FALSE,
    warmup_ready BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, strategy_key),
    KEY idx_indicators_date_strategy (trade_date, strategy_key),
    CONSTRAINT fk_indicators_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE strategy_signals (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    strategy_key VARCHAR(64) NOT NULL,
    selected_signal VARCHAR(32) NULL,
    raw_flags_json JSON NOT NULL,
    trend_state VARCHAR(64) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, strategy_key),
    KEY idx_signals_date_strategy_signal (trade_date, strategy_key, selected_signal),
    CONSTRAINT fk_signals_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Run history tables:

```sql
CREATE TABLE screening_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_key VARCHAR(64) NOT NULL,
    trade_date DATE NOT NULL,
    universe_json JSON NOT NULL,
    filters_json JSON NOT NULL,
    status VARCHAR(32) NOT NULL,
    summary_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    KEY idx_screening_runs_date (trade_date, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE screening_results (
    run_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    expma17 DECIMAL(18, 6) NULL,
    expma50 DECIMAL(18, 6) NULL,
    selected_signal VARCHAR(32) NULL,
    trend_state VARCHAR(64) NOT NULL,
    score DECIMAL(18, 6) NULL,
    reason_json JSON NULL,
    PRIMARY KEY (run_id, symbol),
    KEY idx_screening_results_signal (run_id, selected_signal),
    CONSTRAINT fk_screening_results_run FOREIGN KEY (run_id) REFERENCES screening_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE backtest_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_key VARCHAR(64) NOT NULL,
    symbols_json JSON NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(24, 4) NOT NULL,
    fee_rate DECIMAL(18, 8) NOT NULL,
    slippage_rate DECIMAL(18, 8) NOT NULL,
    price_mode VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    summary_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    KEY idx_backtest_runs_created (created_at),
    KEY idx_backtest_runs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE backtest_trades (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    run_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    signal_date DATE NOT NULL,
    execution_date DATE NULL,
    signal VARCHAR(32) NOT NULL,
    action VARCHAR(32) NOT NULL,
    price DECIMAL(18, 6) NULL,
    quantity DECIMAL(24, 6) NULL,
    fee DECIMAL(24, 6) NOT NULL DEFAULT 0,
    slippage DECIMAL(24, 6) NOT NULL DEFAULT 0,
    position_before DECIMAL(8, 4) NOT NULL,
    position_after DECIMAL(8, 4) NOT NULL,
    is_filled BOOLEAN NOT NULL,
    KEY idx_backtest_trades_run_symbol (run_id, symbol, signal_date),
    CONSTRAINT fk_backtest_trades_run FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE backtest_equity (
    run_id BIGINT NOT NULL,
    trade_date DATE NOT NULL,
    equity DECIMAL(24, 6) NOT NULL,
    cash DECIMAL(24, 6) NOT NULL,
    market_value DECIMAL(24, 6) NOT NULL,
    drawdown DECIMAL(18, 8) NOT NULL,
    positions_json JSON NOT NULL,
    PRIMARY KEY (run_id, trade_date),
    CONSTRAINT fk_backtest_equity_run FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE settings (
    setting_key VARCHAR(128) PRIMARY KEY,
    setting_value JSON NOT NULL,
    is_secret BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Data Structure Rules

- Use `symbol` as the stable external stock identifier across all tables.
- Use MySQL `JSON` columns for request payloads, summaries, raw flags, and provider metadata that do not need relational filtering in version 1.
- Keep prices as `DECIMAL(18, 6)`, quantities and cash/equity as `DECIMAL(24, 6)`, rates as `DECIMAL(18, 8)`.
- Do not store computed indicators only in API memory. Default EXPMA17/50 indicators and signals must be materialized.
- Use idempotent upserts for all sync-derived tables.
- Re-running the same sync range should update rows, not duplicate them.
- Analysis tables should be rebuildable from canonical market data tables.
- Backtest and screening run tables are append-only except for status and completion metadata.

## Data Model

### Daily Bar

Normalized daily bars must include:

- `symbol`
- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `amount`
- `adj_factor` when available
- `source`
- `is_adjusted`
- `price_mode`
- `data_quality`

The backtest should use forward-adjusted prices by default when enough adjustment data is available. If only unadjusted data is available, the run must record that fact in metadata.

### Stock Universe

The first version should support:

- A-share common stocks.
- Manual symbol lists.
- Optional universe filters such as exchange, name keyword, industry, active listing status, and ST exclusion.

ETF and HK/US support are out of scope for the first version unless the data provider abstraction makes them trivial.

## Data Source Policy

Default priority:

1. Tushare, when token exists and the endpoint succeeds.
2. AkShare/Eastmoney public data.
3. CSV import for manual repair or local experiments.
4. Existing local MySQL data for analysis requests.

Provider failures must be visible in sync logs. A run should record which provider supplied each symbol/date range or why it failed.

Local MySQL data is the primary source for screening and backtesting. External providers are used by sync jobs, not by normal analysis requests.

### Provider Contract

Each provider adapter must implement a common interface and return normalized Python dictionaries before storage:

- `fetch_stock_universe()`
- `fetch_trading_calendar(exchange, start_date, end_date)`
- `fetch_daily_bars(symbol, start_date, end_date)`
- `fetch_adjustment_factors(symbol, start_date, end_date)`
- `fetch_stock_status(symbols, trade_date)` when supported

Provider adapters must not write directly to MySQL. They return data to sync services, and sync services own persistence, retry, fallback, and job logging.

Version 1 provider expectations:

- Tushare should be used for the most complete metadata and adjustment-factor path when a token exists.
- AkShare/Eastmoney should provide a no-token fallback for daily bars and basic metadata, accepting that coverage and field consistency may be weaker.
- CSV import must reuse the same normalization and validation path as provider data.
- If providers disagree for the same symbol/date, provider priority decides the canonical row; the losing row may remain in raw payload audit data.

## Sync Policy

### Scheduled Jobs

The first version should support these job types:

- `sync_calendar`: refresh trading calendar.
- `sync_stock_universe`: refresh stock list and metadata.
- `sync_daily_bars`: fetch daily OHLCV data for missing or stale dates.
- `sync_adjustment_factors`: fetch adjustment factors.
- `aggregate_daily`: rebuild analysis-ready daily bars.
- `compute_signals`: recalculate indicators and strategy signals for affected symbols.

The service can run these jobs in-process for the first version. The design should keep job records durable in MySQL so interrupted syncs can be inspected and rerun.

### Incremental Sync

Incremental sync should:

- Detect the latest available `trade_date` per symbol.
- Fetch only missing dates by default.
- Allow a forced refresh for a date range.
- Recompute analysis rows, indicators, and signals from a warmup window before the first changed date.
- Mark symbols as skipped when the market was closed, the symbol was not listed, or the provider lacks data.

The warmup window for EXPMA17/50 is 60 trading rows before the earliest changed date. If fewer than 60 prior rows exist, recomputation starts from the first available row and marks early signals as not warmup-ready.

### Retry and Failure Handling

- A symbol-level failure should not fail the whole job.
- Retry transient provider errors with a small bounded retry count.
- Fall back to the next provider when configured.
- Record permanent failures with provider, endpoint, symbol, date range, and error message.
- Keep partial successful data and make coverage visible to the API/UI.
- A completed sync job may have failed items. Its top-level status should be `completed_with_errors`, not `failed`, when at least one item succeeded.

## Aggregation and Analysis

Aggregation is responsible for turning provider-specific data into analysis-ready rows.

### Normalization

Provider data must be normalized before storage:

- Symbol format normalized to a single convention.
- Dates stored as `DATE`.
- Numeric values converted to database numeric types.
- Missing open/high/low/close rejected.
- Duplicate rows resolved by provider priority and latest successful sync.

### Data Quality

Each analysis row should expose a `data_quality` state:

- `ok`: row is complete and suitable for analysis.
- `missing_adj_factor`: row is usable but not fully adjusted.
- `provider_gap`: provider did not return expected data.
- `invalid`: row failed validation and is excluded from analysis.

### Indicator Materialization

EXPMA values and strategy signals should be materialized in MySQL after sync. This makes screening fast and lets the UI inspect historical signal state without recalculating every request.

Backtests may still recompute strategy signals in memory for custom strategy parameters. For default EXPMA17/50, they should reuse materialized indicators/signals when possible.

### Recompute Triggers

The aggregation layer must enqueue or run downstream recomputation when these inputs change:

- New or changed `daily_bars`.
- New or changed `adjustment_factors`.
- Changed stock status that affects screening filters.
- Forced refresh over a historical date range.

Recomputation order:

1. Rebuild `analysis_daily_bars`.
2. Rebuild `daily_indicators`.
3. Rebuild `strategy_signals`.
4. Mark affected screening/backtest cached results as stale if they overlap the changed symbol/date range.

Version 1 does not need automatic reruns of old screening or backtest runs. It only needs to mark metadata clearly enough that users can rerun them.

## Indicator Semantics

The strategy uses Tongdaxin-style expressions:

- `EMA(CLOSE, N)` maps to pandas-style exponential moving average with `span=N`, `adjust=False`.
- `EXPMA17 = EMA(CLOSE, 17)`.
- `EXPMA50 = EMA(CLOSE, 50)`.
- `CROSS(A, B)` is true when `A > B` today and `REF(A, 1) <= REF(B, 1)`.
- `REF(X, 1)` is the previous trading row for the same symbol.

Warmup:

- At least 60 daily bars should be loaded before a signal is considered reliable.
- Rows without enough prior data can still expose indicators but should not produce tradable signals.

## EXPMA17/50 Strategy

Parameters:

- `SHORT = 17`
- `LONG = 50`

Computed series:

- `EXPMA17`
- `EXPMA50`
- `golden_cross = CROSS(EXPMA17, EXPMA50)`
- `death_cross = CROSS(EXPMA50, EXPMA17)`

Signals:

- `BUY`: `golden_cross AND EXPMA17 > EXPMA50`
- `HALF_SELL`: `CLOSE < EXPMA17 AND REF(CLOSE,1) >= REF(EXPMA17,1) AND EXPMA17 > EXPMA50`
- `RE_BUY`: `CLOSE > EXPMA17 AND REF(CLOSE,1) <= REF(EXPMA17,1) AND CLOSE > EXPMA50 AND EXPMA17 > EXPMA50`
- `CLEAR_1`: `CLOSE < EXPMA50 AND EXPMA17 > EXPMA50`
- `CLEAR_2`: `death_cross`
- `RE_BUY_50`: `CLOSE > EXPMA50 AND REF(CLOSE,1) <= REF(EXPMA50,1) AND EXPMA17 > EXPMA50`

The supplied formula also defines `cross_price` and `cross_in_kline`. The first version should calculate and display them as diagnostic fields, but the explicit `BUY` rule remains the tradable entry unless the user later asks to require `cross_in_kline`.

Signal priority on the same bar:

1. `CLEAR_2`
2. `CLEAR_1`
3. `HALF_SELL`
4. `BUY`
5. `RE_BUY`
6. `RE_BUY_50`

This prevents contradictory same-day actions from generating multiple orders. The selected signal and all raw boolean flags should both be stored for audit.

## Backtest Execution Model

The first version uses next trading day open execution:

- A signal generated after day `T` close executes at day `T+1` open.
- If there is no next bar, the signal remains unfilled.
- Trades use adjusted open prices when adjusted data is available.

Position states:

- `0%`: no position.
- `50%`: half position.
- `100%`: full position.

Action mapping:

- `BUY`: move to 100%.
- `HALF_SELL`: move to 50% only if current position is 100%.
- `RE_BUY`: move to 100% only if current position is 50%.
- `CLEAR_1`: move to 0%.
- `CLEAR_2`: move to 0%.
- `RE_BUY_50`: after a clear state, move to 100% when the signal appears.

Costs:

- Fee rate and slippage are configurable.
- Defaults should be conservative and visible in every result.

Portfolio mode:

- First version supports equal-weight multi-symbol backtests.
- Each symbol gets an independent strategy state.
- Portfolio equity is the sum of per-symbol subaccounts.

Cash and sizing:

- Initial capital is divided equally across selected symbols at run start.
- A symbol only uses its allocated subaccount.
- Unused cash remains in cash with zero interest.

## Screening Behavior

Screening evaluates the latest available materialized signal for each symbol on the selected date.

The result table should include:

- Symbol and name.
- Trade date.
- Close, high, low.
- EXPMA17, EXPMA50.
- Trend state: above/below EXPMA17 and EXPMA50.
- Selected signal.
- Raw signal flags.
- Data source.
- Data quality marker.
- Error or stale-data marker when applicable.

Filters:

- Show only BUY-like signals.
- Show only risk-reduction signals.
- Show all trend-qualified stocks where `EXPMA17 > EXPMA50`.
- Exclude ST or suspended stocks when data supports it.
- Filter by exchange, industry, listing status, and data quality.

## API Sketch

Health and settings:

- `GET /api/health`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/strategies`

Sync:

- `POST /api/sync/jobs`
- `GET /api/sync/jobs`
- `GET /api/sync/jobs/{job_id}`
- `GET /api/sync/jobs/{job_id}/items`
- `POST /api/sync/jobs/{job_id}/retry`
- `GET /api/sync/coverage`

Data:

- `GET /api/stocks`
- `GET /api/stocks/{symbol}`
- `GET /api/stocks/{symbol}/bars`
- `GET /api/stocks/{symbol}/indicators`
- `GET /api/stocks/{symbol}/signals`

Screening:

- `POST /api/screenings`
- `GET /api/screenings/{task_id}`
- `GET /api/screenings/{task_id}/results`

Backtests:

- `POST /api/backtests`
- `GET /api/backtests/{task_id}`
- `GET /api/backtests/runs`
- `GET /api/backtests/runs/{run_id}`

Long-running endpoints return a task ID immediately. The frontend polls status in the first version.

## Frontend Areas

- Sync dashboard:
  - Show latest sync time, job status, provider failures, coverage by date, and failed symbols.
  - Allow manual sync and retry failed items.
- Screening page:
  - Select market, stock universe, date, and strategy.
  - Run screening against local MySQL analysis data.
  - Show candidates with latest price, EXPMA17, EXPMA50, signal type, trend state, data quality, and reason.
- Backtest page:
  - Select stock universe or manual symbols.
  - Select date range, initial capital, fee, slippage, benchmark, and price mode.
  - Run backtest and watch task status.
- Backtest result page:
  - Summary metrics: total return, annualized return, max drawdown, win rate, trade count, average trade return, exposure, and turnover.
  - Equity curve, drawdown curve, trade table, and daily position table.
- Stock detail page:
  - K-line chart with EXPMA17 and EXPMA50.
  - Signal markers for BUY, HALF_SELL, RE_BUY, CLEAR_1, CLEAR_2, and RE_BUY_50.
  - Data coverage and data quality markers.
- Settings page:
  - MySQL connection status.
  - Data source priority.
  - Tushare token presence/status.
  - Sync schedule and retention settings.
  - Default backtest parameters.

The UI should be quiet and operational: dense tables, clear filters, stable chart panels, and direct controls. Avoid marketing-style layouts.

## Initialization and Deployment

The repository must include scripts for database initialization, schema migration, local development startup, and production-like local deployment. These scripts are part of the deliverable, not optional developer notes.

### Required File Layout

```text
db/
  migrations/
    001_create_core_schema.sql
    002_create_analysis_schema.sql
    003_create_run_history_schema.sql
  seeds/
    001_default_settings.sql
scripts/
  init_db.ps1
  migrate_db.ps1
  seed_db.ps1
  dev_server.ps1
  sync_once.ps1
  deploy_local.ps1
  backup_db.ps1
  restore_db.ps1
docker-compose.yml
stock_analyzer_app/
  __main__.py
  config/
  storage/
  sync/
  aggregation/
```

PowerShell scripts are required because the current development environment is Windows. Shell equivalents can be added later if Linux deployment becomes a target.

### Docker Compose

`docker-compose.yml` must provide a local MySQL service for development and repeatable testing.

Required behavior:

- Service name: `mysql`.
- Image: a MySQL 8.x image.
- Port mapping: `3306:3306` unless overridden by environment.
- Database name: `stock_analyzer`.
- App user: `stock_analyzer`.
- Persistent named volume for MySQL data.
- Healthcheck that waits for MySQL readiness.

The application should not require Docker if the user already has MySQL. Docker Compose is the default local bootstrap path, not the only supported deployment mode.

### Environment Configuration

The app should read configuration from environment variables and optionally a local `.env` file. The `.env` file must not be committed.

Required variables:

```text
STOCK_ANALYZER_DB_HOST=127.0.0.1
STOCK_ANALYZER_DB_PORT=3306
STOCK_ANALYZER_DB_NAME=stock_analyzer
STOCK_ANALYZER_DB_USER=stock_analyzer
STOCK_ANALYZER_DB_PASSWORD=change-me
STOCK_ANALYZER_PROVIDER_PRIORITY=tushare,akshare,eastmoney
STOCK_ANALYZER_TUSHARE_TOKEN=
STOCK_ANALYZER_SYNC_ENABLED=true
STOCK_ANALYZER_SYNC_TIME=18:30
STOCK_ANALYZER_TIMEZONE=Asia/Shanghai
STOCK_ANALYZER_LOG_LEVEL=INFO
```

Secrets such as database password and Tushare token should be read from environment variables. If the UI edits them later, the implementation must explicitly document where they are stored and how they are protected.

### Database Initialization

`scripts/init_db.ps1` must:

- Verify MySQL client connectivity.
- Create the database if it does not exist.
- Create the application database user if the operator supplies an admin connection.
- Grant only the permissions required by the app.
- Call `scripts/migrate_db.ps1`.
- Call `scripts/seed_db.ps1`.

Expected usage:

```powershell
.\scripts\init_db.ps1 `
  -Host 127.0.0.1 `
  -Port 3306 `
  -Database stock_analyzer `
  -AppUser stock_analyzer `
  -AppPassword change-me
```

The script should be idempotent. Running it twice should not drop data or recreate existing tables destructively.

### Schema Migration

`scripts/migrate_db.ps1` must:

- Connect using the configured app database credentials.
- Ensure `schema_migrations` exists.
- Compute a SHA-256 checksum for each migration file.
- Apply unapplied migrations in filename order.
- Refuse to continue if an already-applied migration file checksum has changed.
- Print applied, skipped, and failed migration counts.

Destructive migrations are not allowed in version 1. Any schema change that may drop or rewrite user data must be a separate explicit maintenance operation.

### Seed Data

`scripts/seed_db.ps1` must insert default settings:

- Default provider priority.
- Default sync schedule.
- Default fee and slippage.
- Default strategy key: `expma_17_50`.
- Default price mode: `forward_adjusted`.

Seed scripts must use upserts so they can be rerun after deployment.

### Local Development Startup

`scripts/dev_server.ps1` must:

- Verify the Python virtual environment exists.
- Install dependencies if requested by a flag.
- Run migrations.
- Start the FastAPI app on `http://127.0.0.1:8000`.
- Leave sync scheduling enabled or disabled based on `STOCK_ANALYZER_SYNC_ENABLED`.
- Start or validate Docker Compose MySQL when requested by a flag.

Expected usage:

```powershell
.\scripts\dev_server.ps1
```

### One-Time Sync

`scripts/sync_once.ps1` must start a manual sync job without requiring the browser UI.

Expected usage:

```powershell
.\scripts\sync_once.ps1 -JobType sync_daily_bars -StartDate 2024-01-01 -EndDate 2024-12-31
```

Supported `JobType` values:

- `sync_calendar`
- `sync_stock_universe`
- `sync_daily_bars`
- `sync_adjustment_factors`
- `aggregate_daily`
- `compute_signals`
- `full_daily_pipeline`

`full_daily_pipeline` runs the normal sequence: calendar, universe, daily bars, adjustment factors, aggregation, signal computation.

### Local Deployment

`scripts/deploy_local.ps1` must prepare a repeatable local deployment:

- Create or validate `.venv`.
- Install pinned dependencies.
- Initialize or migrate MySQL schema.
- Seed default settings.
- Run backend smoke checks.
- Print the final browser URL and health endpoint.

Expected usage:

```powershell
.\scripts\deploy_local.ps1
```

The first deployment target is a developer workstation. Windows service installation can be added later, but the design should keep startup commands compatible with service managers.

### Backup and Restore

`scripts/backup_db.ps1` must create a timestamped MySQL dump of the application database.

`scripts/restore_db.ps1` must restore a dump into a selected database after an explicit confirmation parameter.

Backups should be documented because local MySQL becomes the system of record for synchronized and derived data.

### Startup Checks

The application should fail fast at startup when:

- Required database settings are missing.
- MySQL is unreachable.
- Required migrations are not applied.
- The configured provider priority is empty.

The health endpoint should report:

- API status.
- Database connectivity.
- Migration status.
- Scheduler status.
- Latest successful sync job.

### Scheduler Requirements

APScheduler is the first-version scheduler. It should run inside the FastAPI process unless disabled by configuration.

Scheduler requirements:

- Jobs are declared in code and persisted as durable execution records in `sync_jobs`.
- The scheduler must not start duplicate daily pipeline jobs if one is already running.
- Manual API-triggered jobs and scheduled jobs share the same task execution path.
- The scheduler can be disabled with `STOCK_ANALYZER_SYNC_ENABLED=false`.
- Default schedule runs after normal A-share market data availability, using `STOCK_ANALYZER_SYNC_TIME` and `STOCK_ANALYZER_TIMEZONE`.

## Error Handling

Data sync failures:

- A symbol-level failure should not fail the entire sync job.
- The job summary must include counts for success, skipped, failed, retryable, and provider fallback.
- Provider failures must be visible in job item details.

Data coverage failures:

- Analysis APIs should report missing date ranges instead of silently fetching external data.
- Screening should mark symbols skipped when required bars or indicators are missing.
- Backtest creation should fail early if coverage is insufficient for the requested universe/date range, unless the user allows partial coverage.
- Partial screening is allowed by default. Results must include counts for evaluated, skipped, missing data, and provider/sync errors.
- Partial backtest is disabled by default. The request must explicitly set `allow_partial_coverage=true` before symbols with incomplete coverage are skipped.
- Coverage checks must use `analysis_daily_bars`, not raw provider tables.

Insufficient history:

- Mark symbol as skipped for tradable signals if fewer than the warmup bars are available.

Suspension or missing next open:

- The signal remains unfilled if there is no executable next bar.
- The run records an unfilled signal.

Provider inconsistency:

- Normalize field names and date formats before writing canonical tables.
- Reject bars with missing open/high/low/close.
- Keep rejected row details in sync logs when possible.

## Testing Strategy

Use test-first development for implementation.

Storage tests:

- MySQL schema migrations create required tables and indexes.
- Repository upserts are idempotent.
- Duplicate provider rows do not create duplicate canonical bars.
- Sync job and item state transitions are durable.

Provider and sync tests:

- Provider adapters normalize stock universe and daily bars.
- Incremental sync fetches only missing date ranges.
- Provider fallback records the selected provider.
- Symbol-level failures do not abort the job.

Aggregation tests:

- Raw bars normalize into canonical daily bars.
- Adjustment factors produce analysis-ready forward-adjusted rows.
- Invalid rows are rejected or marked with data quality state.
- Indicator recomputation starts from an adequate warmup window.

Core tests:

- `EMA` and `CROSS` semantics.
- `REF` previous-row behavior.
- EXPMA strategy signal generation for hand-built price series.
- Same-day signal priority.
- Next-day-open execution.
- Position transitions among 0%, 50%, and 100%.
- Fee/slippage calculation.
- Missing next bar leaves signal unfilled.
- Multi-symbol equal-weight portfolio aggregation.

API tests:

- Start sync task and retrieve status.
- Retrieve sync coverage.
- Start screening task.
- Start backtest task.
- Retrieve status and results.
- Provider failure surfaces as symbol-level error.
- Missing coverage surfaces as an explicit API error.

Script tests:

- Database migration script applies migrations in order.
- Migration script refuses changed checksums for already-applied migrations.
- Seed script is idempotent.
- Local deployment script runs migrations and health checks.
- One-time sync script creates a sync job with the requested job type and date range.

Frontend tests:

- Sync dashboard renders latest job state and failed items.
- Screening page submits parameters and renders result rows.
- Backtest page starts a run and displays summary metrics.
- Stock detail renders bars, EXPMA overlays, and signal markers from API data.

## Out Of Scope For Version 1

- Intraday backtesting.
- Real-time streaming quotes.
- Short selling.
- Margin or financing.
- Dividend/tax modeling beyond adjusted prices.
- AI ranking or LLM analysis.
- Strategy expression editor.
- Distributed task queue.
- Live trading.
- Multi-user permissions.

## Open Implementation Decisions

These are implementation details, not product blockers:

- Exact charting library: ECharts is a practical default for K-line overlays and signal markers.
- Whether raw provider payload retention is unlimited or time-limited.
- Whether the first release ships as one command or separate backend/frontend commands.
- Whether sensitive settings are only environment variables in version 1 or can also be edited in the UI with explicit storage protection.

## Acceptance Criteria

The first implemented release is acceptable when:

- The local Web app starts successfully.
- The backend connects to MySQL and initializes required schema.
- Docker Compose can start a local MySQL 8.x instance for development.
- Database migration files, seed files, and PowerShell scripts are present in the required layout.
- Initialization, migration, seed, local deployment, one-time sync, backup, and restore scripts are documented and runnable.
- A user can configure data source settings and see provider/token status.
- APScheduler can run the configured daily pipeline without creating duplicate concurrent jobs.
- A user can run or schedule stock universe and daily bar synchronization.
- Sync jobs persist status, summary counts, and symbol-level errors.
- Aggregation produces analysis-ready daily bars in MySQL.
- EXPMA17/50 indicators and signals are materialized for synced symbols.
- Historical data changes recompute analysis rows, indicators, and signals from the required 60-row warmup window.
- A user can run EXPMA17/50 screening on a synced A-share universe.
- A user can run a historical EXPMA17/50 backtest with next-day-open execution.
- Results include metrics, trades, daily equity, signal details, and data coverage metadata.
- The stock detail chart displays daily bars, EXPMA17, EXPMA50, and signal markers.
- Core storage, sync, aggregation, indicator, strategy, and backtest behavior is covered by automated tests.
