# EXPMA Stock Analysis Web Design

## Purpose

Build a new local Web stock analysis tool. The two existing projects under `D:\Develop\soucre\daily_stock_analysis` are references for data access, indicators, UI organization, and backtesting ideas only. This project is a new standalone application.

The first version focuses on:

- Indicator-based stock screening.
- Historical backtesting.
- A built-in EXPMA17/50 trend pullback strategy based on the supplied Tongdaxin formula.
- Local browser operation with no required cloud service.

This tool is for research and engineering use only. It does not provide investment advice.

## Product Shape

The first version is a local Web application:

- Backend: FastAPI service.
- Frontend: React + Vite browser UI.
- Storage: SQLite for local metadata, cached bars, strategy settings, and backtest runs.
- Core logic: pure Python modules for data normalization, indicators, strategy signals, screening, and backtesting.

The app should run locally and expose a browser URL such as `http://127.0.0.1:8000`.

## Architecture

### Backend Modules

`stock_analyzer_app/`

- `api/`
  - FastAPI routers for data, screening, backtests, strategy metadata, and run history.
- `data_provider/`
  - Unified provider interface for daily OHLCV bars and stock universe data.
  - AkShare/Eastmoney public data is the default path.
  - Tushare is preferred when a token is configured and the requested endpoint is available.
- `indicators/`
  - EMA/EXPMA, CROSS, REF, and shared series helpers.
  - Indicator functions are deterministic and independent from data providers.
- `strategies/`
  - Strategy signal generation.
  - The EXPMA17/50 strategy lives here and returns signal rows, not trades.
- `screening/`
  - Batch evaluation for a stock universe on a target date.
  - Produces ranked or filtered candidates with latest signal state.
- `backtest/`
  - Converts strategy signals into trades using the selected execution model.
  - Computes equity curve, positions, trades, and performance metrics.
- `storage/`
  - SQLite schema and repository helpers.
  - Stores cached daily bars, stock list snapshots, strategy configurations, backtest run metadata, summary metrics, trades, and daily equity rows.
- `tasks/`
  - Background task orchestration for long-running screening and backtests.
  - First version can use in-process tasks; the API contract should allow later migration to a durable queue.
- `config/`
  - Environment and UI-editable settings, including Tushare token, cache TTL, fee, slippage, and default data source priority.

### Frontend Areas

`apps/web/`

- Screening page:
  - Select market, stock universe, date, and strategy.
  - Run screening.
  - Show candidates with latest price, EXPMA17, EXPMA50, signal type, trend state, and reason.
- Backtest page:
  - Select stock universe or manual symbols.
  - Select date range, initial capital, fee, slippage, benchmark, and data source mode.
  - Run backtest and watch task status.
- Backtest result page:
  - Summary metrics: total return, annualized return, max drawdown, win rate, trade count, average trade return, exposure, and turnover.
  - Equity curve, drawdown curve, trade table, and daily position table.
- Stock detail page:
  - K-line chart with EXPMA17 and EXPMA50.
  - Signal markers for BUY, HALF_SELL, RE_BUY, CLEAR_1, CLEAR_2, and RE_BUY_50.
- Settings page:
  - Data source priority.
  - Tushare token presence/status.
  - Cache controls.
  - Default backtest parameters.

The UI should be quiet and operational: dense tables, clear filters, stable chart panels, and direct controls. Avoid marketing-style layouts.

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

The backtest should use forward-adjusted prices by default when the provider supports them. If only unadjusted data is available, the run must record that fact in metadata.

### Stock Universe

The first version should support:

- A-share common stocks.
- Manual symbol lists.
- Optional universe filters such as exchange, name keyword, and ST exclusion.

ETF and HK/US support are out of scope for the first version unless the data provider abstraction makes them trivial.

## Data Source Policy

Default priority:

1. Tushare, when token exists and the endpoint succeeds.
2. AkShare/Eastmoney public data.
3. Cached local bars, only when the user allows stale cache fallback.

Provider failures must be visible in task logs. A run should record which provider supplied each symbol or why it failed.

## Indicator Semantics

The strategy uses Tongdaxin-style expressions:

- `EMA(CLOSE, N)` maps to pandas exponential moving average with `span=N`, `adjust=False`.
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

Screening evaluates the latest available signal for each symbol on the selected date.

The result table should include:

- Symbol and name.
- Trade date.
- Close, high, low.
- EXPMA17, EXPMA50.
- Trend state: above/below EXPMA17 and EXPMA50.
- Selected signal.
- Raw signal flags.
- Data source.
- Error or stale-data marker when applicable.

Filters:

- Show only BUY-like signals.
- Show only risk-reduction signals.
- Show all trend-qualified stocks where `EXPMA17 > EXPMA50`.
- Exclude ST or suspended stocks when data supports it.

## API Sketch

- `GET /api/health`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/strategies`
- `POST /api/screenings`
- `GET /api/screenings/{task_id}`
- `GET /api/screenings/{task_id}/results`
- `POST /api/backtests`
- `GET /api/backtests/{task_id}`
- `GET /api/backtests/runs`
- `GET /api/backtests/runs/{run_id}`
- `GET /api/stocks/{symbol}/bars`
- `GET /api/stocks/{symbol}/signals`

Long-running endpoints return a task ID immediately. The frontend polls status in the first version.

## Error Handling

Data failures:

- A symbol-level failure should not fail the entire run.
- The task summary must include counts for success, skipped, failed, and stale-cache fallback.

Insufficient history:

- Mark symbol as skipped for tradable signals if fewer than the warmup bars are available.

Suspension or missing next open:

- The signal remains unfilled if there is no executable next bar.
- The run records an unfilled signal.

Provider inconsistency:

- Normalize field names and date formats before indicators.
- Reject bars with missing open/high/low/close.

## Testing Strategy

Use test-first development for implementation.

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

- Start screening task.
- Start backtest task.
- Retrieve status and results.
- Provider failure surfaces as symbol-level error.

Frontend tests:

- Screening page submits parameters and renders result rows.
- Backtest page starts a run and displays summary metrics.
- Stock detail renders signal markers from API data.

## Out Of Scope For Version 1

- Intraday backtesting.
- Short selling.
- Margin or financing.
- Dividend/tax modeling beyond adjusted prices.
- AI ranking or LLM analysis.
- Strategy expression editor.
- Distributed task queue.
- Live trading.

## Open Implementation Decisions

These are implementation details, not product blockers:

- Exact charting library: ECharts is a practical default for K-line overlays and signal markers.
- Exact background task implementation: FastAPI background tasks are enough for version 1; a queue can be added later.
- Whether the first release ships as one command or separate backend/frontend commands.

## Acceptance Criteria

The first implemented release is acceptable when:

- The local Web app starts successfully.
- A user can configure data source settings.
- A user can run EXPMA17/50 screening on an A-share universe.
- A user can run a historical EXPMA17/50 backtest with next-day-open execution.
- Results include metrics, trades, daily equity, and signal details.
- The stock detail chart displays EXPMA17, EXPMA50, and signal markers.
- Core indicator, strategy, and backtest behavior is covered by automated tests.
