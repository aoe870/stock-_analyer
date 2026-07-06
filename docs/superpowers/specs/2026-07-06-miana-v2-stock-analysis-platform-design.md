# Miana V2 Stock Analysis Platform Design

Date: 2026-07-06

## Purpose

This document defines the next version of the stock analysis platform based on the data available from Miana's public API documentation at `https://miana.com.cn/document`.

The goal is to move the product from a K-line and strategy prototype into a practical stock research terminal with market overview, stock detail research, data health visibility, financial data, capital flow, sectors, and index context.

This version is intentionally scoped to A-share stock analysis. Miana also exposes fund, futures, forex, crypto, and other endpoints, but those are out of scope for V2.

## Product Scope

V2 includes four product areas:

1. Market dashboard
2. Enhanced stock detail workspace
3. Data center
4. New data ingestion for financial statements, capital flow, sectors, and indexes

V2 does not include:

- Full multi-asset support for funds, futures, forex, or crypto
- Full-market minute-level history sync
- Portfolio management
- Account trading
- Real-time websocket streaming

## Miana API Capability Map

### Core Stock Data

| Capability | Endpoint | Product Use |
| --- | --- | --- |
| Stock universe | `/api/stock/v1/stockList` | Stock pool, search, exchange metadata |
| Realtime quotes | `/api/stock/v2/realtime` | Stock detail header, watchlist quotes; supports multiple symbols per call |
| Full-market realtime | `/api/stock/v2/realtimeMarket` | Market breadth and dashboard snapshot |
| Stock ranking | `/api/stock/v1/sort` | Gainers, losers, turnover, amount, valuation ranking |
| K-line | `/api/stock/v2/kline` | Daily/weekly/monthly K-line, adjusted prices, charting and strategies |

### Stock Research Data

| Capability | Endpoint | Product Use |
| --- | --- | --- |
| Company profile | `/api/stock/v1/companyInfo` | Company profile tab, industry, region, business description |
| Income statement | `/api/stock/v1/incomeSheet` | Revenue, profit, margin trend |
| Balance sheet | `/api/stock/v1/balanceSheet` | Assets, liabilities, equity, leverage |
| Cashflow statement | `/api/stock/v1/cashflow` | Operating cashflow, investing cashflow, financing cashflow |
| Capital flow | `/api/stock/v1/dailyMoneyflow` | Main capital, large order, medium order, small order flow |
| Corporate actions | `/api/stock/v1/distribute` | Dividend, split, ex-dividend timeline |
| Share capital history | `/api/stock/v1/shares` | Total/floating/limited shares trend |
| Top 10 holders | `/api/stock/v1/top10holders` | Shareholder concentration |
| Company officers | `/api/stock/v1/companyOfficer` | Board and executive team |
| Rewards | `/api/stock/v1/rewards` | Executive reward and shareholding data |
| New IPO | `/api/stock/v1/newIPO` | IPO calendar and new-stock watch |
| AH stock list | `/api/stock/v1/ahStockList` | A/H comparison and cross-market context |

### Market Structure Data

| Capability | Endpoint | Product Use |
| --- | --- | --- |
| Index list | `/api/index/v1/indexList` | Index selector |
| Index realtime | `/api/index/v2/realtime`, `/api/index/v1/realtimeMarket` | Dashboard index cards |
| Index K-line | `/api/index/v2/kline` | Index trend chart |
| Index constituents | `/api/index/v1/constituent` | Index member analysis |
| Sector list | `/api/sector/v1/sectorList` | Sector selector |
| Sector realtime | `/api/sector/v2/realtime`, `/api/sector/v1/realtimeMarket` | Sector heat and ranking |
| Sector K-line | `/api/sector/v2/kline` | Sector trend chart |
| Sector constituents | `/api/sector/v1/constituent` | Sector member analysis |
| Trade calendar | `/api/ticker/v1/tradeCals` | Reliable previous trading day resolution |

## Data Frequency Model

The main performance risk is treating all data as daily full-market data. V2 must use frequency-aware sync jobs.

| Data Type | Frequency | Default Sync |
| --- | --- | --- |
| Stock universe | Low | Daily at 00:00 |
| Daily K-line and adjusted K-line | Daily | Daily at 00:00 for previous completed trading day |
| Strategy indicators and signals | Derived daily | After daily K-line sync |
| Realtime quotes | Intraday | On page open or watchlist refresh only |
| Capital flow | Daily | Optional daily job after close or on-demand by stock |
| Company profile | Low | Monthly plus on-demand by stock |
| Financial statements | Low/quarterly | Weekly plus on-demand by stock |
| Corporate actions | Low | Weekly |
| Share capital | Low | Weekly |
| Holders/officers/rewards | Low | Monthly |
| Index and sector lists | Low | Daily or weekly |
| Index and sector realtime | Intraday | Dashboard on-demand |
| Index and sector K-line | Daily | Daily at 00:00 |
| Minute K-line | High | Single-symbol on-demand only |

## Existing Data Model

The current application already has these useful tables and persistence paths:

- `stocks`
- `daily_bars`
- `adjustment_factors`
- `analysis_daily_bars`
- `daily_indicators`
- `strategy_signals`
- `stock_provider_profiles`
- `stock_company_profiles`
- `corporate_actions`
- `share_capital_history`
- `daily_money_flow`
- `raw_provider_payloads`
- `sync_jobs`
- `sync_job_items`

V2 should reuse these tables where possible instead of duplicating concepts.

## New Storage Design

### Financial Statements

Add one normalized table for each report family, because the field sets are different and the UI will query them separately.

- `income_statements`
- `balance_sheets`
- `cashflow_statements`

Common columns:

- `symbol`
- `provider`
- `report_date`
- `notice_date`
- `report_period`
- `currency`
- `raw_json`
- `created_at`
- `updated_at`

Each table should also store a small set of normalized numeric fields needed by the first UI version:

Income:

- `revenue`
- `operating_revenue`
- `operating_profit`
- `total_profit`
- `net_profit`
- `net_profit_parent`
- `eps`

Balance:

- `total_assets`
- `total_liabilities`
- `total_equity`
- `monetary_funds`
- `accounts_receivable`
- `inventory`

Cashflow:

- `net_operating_cashflow`
- `net_investing_cashflow`
- `net_financing_cashflow`
- `cash_and_equivalents`

If a Miana field name differs, store the original payload in `raw_json` and map only the fields present in the response.

### Holder and Officer Data

Add:

- `stock_top10_holders`
- `stock_company_officers`
- `stock_officer_rewards`

These are low-frequency research tables and should not be part of the daily midnight K-line job.

### Index and Sector Data

Add:

- `market_indexes`
- `index_constituents`
- `index_daily_bars`
- `market_sectors`
- `sector_constituents`
- `sector_daily_bars`

For realtime market snapshots, do not persist every dashboard poll by default. Store only latest snapshot rows if needed:

- `latest_market_quotes`
- `latest_sector_quotes`
- `latest_index_quotes`

This avoids turning UI polling into unbounded time-series storage.

## Sync Job Design

Split sync into explicit job types.

### Daily Core Job

Job type: `daily_core_pipeline`

Runs at `00:00 Asia/Shanghai`.

Responsibilities:

1. Resolve target date to previous completed trading day.
2. Sync stock universe if stale.
3. Sync daily K-line and adjusted K-line for target date.
4. Generate adjustment factors, analysis bars, indicators, and strategy signals.
5. Persist symbol-level failures.
6. Retry failed symbols with the existing retry mechanism.

This job must not fetch company profile, financial statements, holders, officers, or other low-frequency data.

### Capital Flow Job

Job type: `daily_money_flow_pipeline`

Runs after market close or manually.

Responsibilities:

1. Sync `/stock/v1/dailyMoneyflow` for selected symbols.
2. Persist into `daily_money_flow`.
3. Record failure items separately from K-line failures.

Default mode should be configurable:

- `disabled`
- `watchlist_only`
- `full_market`

Recommended default: `watchlist_only`.

### Fundamental Refresh Job

Job type: `fundamental_refresh_pipeline`

Runs weekly or on demand by stock.

Responsibilities:

1. Company profile
2. Income statement
3. Balance sheet
4. Cashflow statement
5. Corporate actions
6. Share capital
7. Top holders
8. Officers and rewards

Recommended modes:

- On stock detail open, refresh that one stock if stale.
- Weekly batch refresh a limited number of stale symbols.
- Manual full refresh for admin use.

### Market Structure Job

Job type: `market_structure_pipeline`

Runs daily or weekly.

Responsibilities:

1. Index list
2. Index constituents
3. Index daily K-line
4. Sector list
5. Sector constituents
6. Sector daily K-line

This supports dashboard, sector analysis, and stock context.

### Realtime Data

Realtime quote endpoints should be used by API handlers when the user opens relevant pages.

Do not persist every realtime response by default. Cache latest responses in memory or overwrite latest quote tables.

## Backend API Design

### Dashboard

Add:

- `GET /api/market/dashboard`
- `GET /api/market/rankings`
- `GET /api/market/sectors`
- `GET /api/market/indexes`

Dashboard response should include:

- Major index cards
- Market breadth
- Top gainers/losers
- Amount ranking
- Sector ranking
- Data freshness and sync status

### Stock Detail

Add:

- `GET /api/stocks/{symbol}/overview`
- `GET /api/stocks/{symbol}/capital-flow`
- `GET /api/stocks/{symbol}/financials`
- `GET /api/stocks/{symbol}/corporate-actions`
- `GET /api/stocks/{symbol}/share-capital`
- `GET /api/stocks/{symbol}/holders`
- `POST /api/stocks/{symbol}/refresh-fundamentals`

The existing `GET /api/stocks/{symbol}/bars?refresh=true` remains for K-line refresh.

### Data Center

Add:

- `GET /api/data-center/coverage`
- `GET /api/data-center/failures`
- `GET /api/data-center/provider-calls`
- `POST /api/sync/jobs/{job_type}`

Coverage should report:

- Daily K-line coverage
- Analysis bar coverage
- Financial statement coverage
- Capital flow coverage
- Sector/index coverage
- Latest successful job by type
- Failed symbols by job type

## Frontend Design

### Navigation

V2 top-level navigation:

- Market
- Stocks
- Screener
- Sectors
- Strategy Lab
- Data Center
- Settings

### Market Dashboard

Main panels:

1. Major index strip
2. Market breadth and turnover
3. Sector heat table
4. Gainers/losers/amount ranking tabs
5. Capital flow leaders
6. Data freshness footer

The dashboard should be dense and operational, not a marketing page.

### Stock Detail Workspace

Header:

- Symbol, name, exchange, industry
- Last price and change
- Turnover, amount, market cap, PE/PB
- Data quality and freshness badges

Tabs:

- Chart
- Capital Flow
- Financials
- Company
- Holders
- Corporate Actions
- Strategy

Chart tab:

- Daily/weekly/monthly K-line
- EXPMA17/50 overlay
- Volume
- Strategy signal markers

Financials tab:

- Revenue and profit trend
- Balance sheet key metrics
- Cashflow trend
- Quarter/year selector

Capital Flow tab:

- Main net inflow
- Large/medium/small order breakdown
- Recent flow table

### Data Center

Panels:

- Sync status cards
- Coverage matrix
- Failed queue table
- Provider call volume table
- Manual sync controls

Manual sync controls must be explicit about scope:

- Sync previous trading day
- Retry failed symbols
- Refresh fundamentals for selected symbols
- Refresh market structure

## Implementation Phases

### Phase 1: Data Model and Provider Mapping

1. Add migrations for financial, holder, officer, index, and sector tables.
2. Add Miana provider methods for the new stock research endpoints.
3. Add tests for payload normalization and persistence.

### Phase 2: Sync Job Separation

1. Rename or wrap the current full pipeline as the daily core job.
2. Add independent fundamental refresh pipeline.
3. Add capital flow pipeline.
4. Add market structure pipeline.
5. Extend sync job reporting by job type.

### Phase 3: Backend Read APIs

1. Add stock overview and financial APIs.
2. Add market dashboard APIs.
3. Add data center coverage APIs.
4. Keep realtime calls on demand and cache latest values.

### Phase 4: Frontend V2

1. Rebuild navigation around Market, Stocks, Sectors, Strategy, Data Center.
2. Implement market dashboard.
3. Enhance stock detail tabs.
4. Implement data center.
5. Add loading, empty, stale, and failure states.

### Phase 5: Hardening

1. Add trading-calendar based target date resolution.
2. Add stale data warnings for analysis and screening.
3. Add provider call budgeting.
4. Add data backfill tools for fundamentals and market structure.

## Acceptance Criteria

V2 is acceptable when:

1. Daily midnight sync finishes without pulling low-frequency research data.
2. Stock detail can show K-line, realtime quote, company profile, financials, capital flow, corporate actions, and share capital when data exists.
3. Market dashboard shows index, sector, ranking, and freshness data.
4. Data center clearly reports coverage and failed symbols.
5. Low-frequency refresh jobs can run independently from daily K-line sync.
6. All new storage and provider mappings have automated tests.
7. Frontend remains usable when optional data is missing.

## Open Decisions

1. Whether daily money flow should default to `watchlist_only` or `full_market`.
2. Whether financial data refresh should be weekly full-market or stale-symbol batch.
3. Whether latest realtime quotes should be persisted in MySQL or held only in memory.
4. Whether sector/index K-lines should use separate chart tables or a generalized market bar table.

Recommended defaults:

1. Daily money flow: `watchlist_only`
2. Financial refresh: stale-symbol batch plus on-demand detail refresh
3. Realtime quotes: cache latest values, no historical realtime persistence
4. Sector/index K-lines: separate tables for simpler first implementation

