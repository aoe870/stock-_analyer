# Miana API Gap Next Version Design

Date: 2026-07-07

## Purpose

This document reviews the local `miana-api.md` interface file against the current application integration and defines the next version feature design.

The goal is not to add another broad platform rewrite. The next version should fill the highest-value gaps left after the enterprise data work:

1. More complete stock detail research context.
2. Reliable previous trading day resolution.
3. News, research reports, IPO, AH, and reference data.
4. Index and sector trend data.
5. Careful realtime quote usage with cache and quota control.

Normal page clicks should continue to read local data or collector-maintained short-lived snapshots. Miana requests should run only in the data collector service, not in user-facing API handlers.

Architecture note:

- `docs/superpowers/specs/2026-07-07-data-collector-api-service-split-design.md` supersedes any API design that allowed FastAPI handlers to call Miana directly.
- The API gap map in this document defines which Miana endpoints to add next.
- The collector/API split document defines where those provider calls are allowed to run.

## Current Integration Baseline

The current Miana provider already covers the core A-share data path:

| Capability | Miana Endpoint | Current Status |
| --- | --- | --- |
| Stock list | `/api/stock/v1/stockList` | Integrated |
| Stock K-line | `/api/stock/v2/kline` | Integrated |
| Stock ranking | `/api/stock/v1/sort` | Integrated |
| Index ranking | `/api/index/v1/sort` | Integrated |
| Sector ranking | `/api/sector/v1/sort` | Integrated |
| Company info | `/api/stock/v1/companyInfo` | Integrated |
| Corporate actions | `/api/stock/v1/distribution` with fallback | Integrated |
| Share capital | `/api/stock/v1/shares` | Integrated |
| Daily money flow | `/api/stock/v1/dailyMoneyflow` | Integrated |
| Income statement | `/api/stock/v1/incomeStatement` with fallback | Integrated |
| Balance sheet | `/api/stock/v1/balanceSheet` | Integrated |
| Cashflow statement | `/api/stock/v1/cashFlowStatement` with fallback | Integrated |
| Top 10 shareholders | `/api/stock/v1/top10Shareholders` with fallback | Integrated |
| Company officers | `/api/stock/v1/companyOfficers` | Integrated |
| Officer rewards | `/api/stock/v1/rewards` | Integrated |
| Index list | `/api/index/v1/indexList` | Integrated |
| Index constituents | `/api/index/v1/constituent` | Integrated |
| Sector list | `/api/sector/v1/sectorList` | Integrated |
| Sector constituents | `/api/sector/v1/constituent` | Integrated |

Existing design documents already cover company detail display and the first Miana V2 platform direction:

- `docs/superpowers/specs/2026-07-06-company-detail-data-display-design.md`
- `docs/superpowers/specs/2026-07-06-miana-v2-stock-analysis-platform-design.md`

This document extends those designs with an API coverage gap map and a practical next-version scope.

## API Gap Map

### P0: Add Next

These are high-value gaps that directly improve existing user workflows.

| Capability | Miana Endpoint | Product Use | Data Frequency |
| --- | --- | --- | --- |
| Trading calendar | `/api/ticker/v1/tradeCals` | Resolve previous trading day correctly for weekends and holidays | Daily or monthly cache |
| Single or batched stock quote | `/api/stock/v2/realtime` | Stock detail header, selected watchlist quote snapshot | Collector refresh with 30-60 second TTL during market hours |
| Stock news | `/api/stock/v1/news` | Stock detail `News` tab | Daily sync plus on-demand stale refresh |
| Research reports | `/api/stock/v1/researchReport` | Stock detail `Research Reports` tab | Daily sync plus on-demand stale refresh |
| Financial metrics | `/api/stock/v1/financialInfo` | Company detail valuation and operating metric summary | Daily or weekly stale refresh |
| Top 10 floating shareholders | `/api/stock/v1/top10FloatShareholders` | Complete shareholder view | Weekly or monthly stale refresh |

Why P0:

- The trading calendar directly addresses previous trading day mistakes.
- Quote data should not force full-market realtime usage, but selected quote refresh is useful.
- News and research reports make stock detail a research workspace instead of only a K-line view.
- `financialInfo` can explain why financial sections look empty or incomplete by adding a direct metrics snapshot.
- Floating shareholders are a natural completion of the existing holder module.

### P1: Add After P0

These improve market context and data center coverage, but they are less urgent than P0.

| Capability | Miana Endpoint | Product Use | Data Frequency |
| --- | --- | --- | --- |
| Index K-line | `/api/index/v2/kline` | Index trend charts, market dashboard context | Daily at 00:00 for previous trading day |
| Index realtime | `/api/index/v2/realtime` | Major index quote strip | 30-60 second TTL, on demand |
| Sector K-line | `/api/sector/v2/kline` | Sector trend charts and sector detail | Daily at 00:00 for previous trading day |
| Sector realtime | `/api/sector/v2/realtime` | Selected sector quote refresh | 30-60 second TTL, on demand |
| IPO calendar | `/api/stock/v1/newIPO` | Data center IPO calendar | Daily |
| AH stock list | `/api/stock/v1/ahStockList` | A/H comparison and cross-market reference | Daily or weekly |
| Exchange list | `/api/stock/v1/exchangeList` | Reference metadata, search filters, symbol normalization | Weekly or monthly |
| Keyword search | `/api/ticker/v1/search` | Better global search if local stock list misses symbols | On demand with cache |
| Country and currency references | `/api/ticker/v1/country`, `/api/ticker/v1/currencyType` | Reference data for future multi-market support | Monthly |

### P2: Defer

These should not drive the next version unless there is a separate product decision.

| Capability | Miana Endpoint | Reason to Defer |
| --- | --- | --- |
| Full-market stock realtime | `/api/stock/v2/realtimeMarket` | Enterprise-only and high-volume; use rankings/local cache first |
| Full-market index realtime | `/api/index/v1/realtimeMarket` | Enterprise-only; selected index realtime is enough |
| Full-market sector realtime | `/api/sector/v1/realtimeMarket` | Enterprise-only; selected sector realtime is enough |
| Transaction detail | `/api/stock/v1/detail` | Intraday/tick-like workflow, not needed for daily research version |
| Non-daily money flow | `/api/stock/v1/moneyflow` | Needs field validation and clear UI purpose |
| Websocket quote subscription | `ws` section | Requires connection lifecycle, auth, throttling, and frontend streaming design |
| Crypto, forex, fund, future, metal APIs | `/api/crypto/*`, `/api/forex/*`, `/api/fund/*`, `/api/future/*`, `/api/metal/*` | Multi-asset support is outside the current A-share product scope |

## Next Version Product Scope

The recommended next version theme is:

> Research context and reliable market date handling.

It should include four user-facing additions.

### 1. Stock Detail Quote and Research Context

Stock detail should add:

- Quote snapshot strip from `/api/stock/v2/realtime`, collected by the collector service and cached by symbol.
- News tab from `/api/stock/v1/news`.
- Research report tab from `/api/stock/v1/researchReport`.
- Financial metrics summary from `/api/stock/v1/financialInfo`.
- Floating shareholder section from `/api/stock/v1/top10FloatShareholders`.

The quote strip should not call Miana from a user-facing API. The collector owns quote refresh and writes latest snapshots. News, reports, financial metrics, and shareholders should also be read from local storage after sync.

### 2. Trading Calendar Based Target Date

The daily data pipeline should use `/api/ticker/v1/tradeCals` for exchange calendars:

- Cache `XSHG`, `XSHE`, and `BJSE` calendars locally.
- Resolve target date to the last completed trading day.
- Treat weekends and holidays as non-trading days.
- Keep a fallback to the current local latest-bar logic if Miana calendar is unavailable.

This directly prevents syncing an empty Sunday or holiday as if it were a trading day.

### 3. Market Structure Trends

Market dashboard and sector pages should add:

- Index daily bars from `/api/index/v2/kline`.
- Sector daily bars from `/api/sector/v2/kline`.
- Optional selected index quote from `/api/index/v2/realtime`.
- Optional selected sector quote from `/api/sector/v2/realtime`.

This gives the dashboard trend context without relying on enterprise-only full-market realtime endpoints.

### 4. Data Center Reference Modules

Data Center should add reference pages or tables for:

- IPO calendar from `/api/stock/v1/newIPO`.
- AH stock pairs from `/api/stock/v1/ahStockList`.
- Exchange metadata from `/api/stock/v1/exchangeList`.
- Trading calendar coverage from `/api/ticker/v1/tradeCals`.

These are low-frequency datasets and should be synced ahead of user clicks.

## Data Storage Design

### New Tables

Add focused normalized tables and preserve raw payloads for all new Miana responses.

| Table | Purpose | Key Columns |
| --- | --- | --- |
| `trading_calendars` | Exchange trading day cache | `exchange_code`, `trading_day`, `trading_type`, `last_trading_day`, `raw_json` |
| `latest_stock_quotes` | Latest cached selected stock quotes | `symbol`, `provider`, `local_date`, `price`, `change`, `change_rate`, `volume`, `amount`, `turnover`, `pe_ttm`, `pb`, `raw_json` |
| `stock_news` | Stock news list | `symbol`, `announcement_date`, `announcement_time`, `title`, `summary`, `url`, `source`, `platform`, `raw_json` |
| `stock_research_reports` | Broker research reports | `symbol`, `announcement_date`, `title`, `summary`, `institution`, `institution_code`, `source`, `raw_json` |
| `stock_financial_metrics` | Direct financial metric snapshot | `symbol`, `provider`, metric fields needed by UI, `report_date`, `raw_json` |
| `stock_top10_float_shareholders` | Floating shareholder details | `symbol`, `report_date`, `announcement_date`, `holder_name`, `hold_amount`, `hold_ratio`, `hold_float_ratio`, `holder_type`, `raw_json` |
| `index_daily_bars` | Index daily K-line | `index_code`, `trade_date`, `open`, `high`, `low`, `close`, `pre_close`, `volume`, `amount`, `raw_json` |
| `sector_daily_bars` | Sector daily K-line | `sector_code`, `trade_date`, `open`, `high`, `low`, `close`, `pre_close`, `volume`, `amount`, `raw_json` |
| `new_ipo_calendar` | IPO schedule | `code`, `name`, `exchange_code`, `country_code`, `subscription_start_date`, `subscription_end_date`, `listing_date`, `final_price`, `winning_rate`, `raw_json` |
| `stock_ah_pairs` | A/H pair reference | `a_code`, `a_name`, `a_exchange_code`, `h_code`, `h_name`, `h_exchange_code`, `raw_json` |
| `stock_exchanges` | Exchange metadata | `exchange_code`, `exchange_name`, `country_code`, `currency_code`, `timezone`, `raw_json` |

### Realtime Storage Rule

Do not store every realtime quote response as history.

Use one of these:

1. In-memory cache only for selected quote requests.
2. `latest_stock_quotes` overwrite per symbol for visibility and API stability.

Recommended default: use `latest_stock_quotes` plus a 30-60 second API TTL. This lets the UI show a cached value after provider failure without creating unbounded time-series rows.

### Raw Payload Policy

Every new table should include `raw_json` or continue writing to `raw_provider_payloads`.

Reason:

- `miana-api.md` contains some garbled Chinese descriptions, but endpoint paths and field names are usable.
- Live payloads may include fields not shown in the UI yet.
- Financial metric names may need later remapping without losing source data.

## Sync Design

### Job Types

Add or extend these sync job types:

| Job Type | Purpose | Default Schedule |
| --- | --- | --- |
| `trading_calendar_pipeline` | Sync `XSHG`, `XSHE`, `BJSE` trading calendars | Daily or monthly refresh |
| `stock_research_context_pipeline` | Sync news, research reports, financial metrics, floating holders for selected symbols | Daily stale-symbol batch |
| `market_trend_pipeline` | Sync index and sector K-lines for previous trading day | Daily at 00:00 after date resolution |
| `reference_data_pipeline` | Sync IPO, AH pairs, exchange metadata, country/currency references | Daily for IPO/AH, monthly for exchanges |
| `quote_snapshot_pipeline` | Refresh selected stock/index/sector quote snapshots | Collector-owned market-hours loop with TTL |

### Previous Trading Day Flow

At `00:00 Asia/Shanghai`:

1. Ensure trading calendar cache exists for target exchanges.
2. Resolve the previous completed trading day using `lastTradingDay`.
3. If today is a non-trading day, use the last trading day instead of today or yesterday.
4. Run daily bar, ranking, index K-line, and sector K-line sync for the resolved date.
5. Record the target date in the sync job metadata.

If calendar sync fails:

- Use the latest local successful trading day as fallback.
- Mark job metadata with `calendar_fallback=true`.
- Do not trigger full-market provider calls for a date that is known to be a weekend by local calendar rules.

### Stock Research Context Sync

Default mode should be stale-symbol batch, not full-market every day.

Suggested staleness:

| Data | Stale After |
| --- | --- |
| News | 1 day |
| Research reports | 1 day |
| Financial metrics | 7 days |
| Floating shareholders | 30 days |

Manual refresh for a current stock can refresh all four families for that symbol.

## Backend API Design

Add stable read APIs that return local data first.

### Stock Detail

| API | Behavior |
| --- | --- |
| `GET /api/stocks/{symbol}/quote` | Return latest collector-maintained quote snapshot; never call Miana from the API process |
| `GET /api/stocks/{symbol}/news` | Return local stock news, newest first |
| `GET /api/stocks/{symbol}/research-reports` | Return local research reports, newest first |
| `GET /api/stocks/{symbol}/financial-metrics` | Return latest local financial metrics snapshot |
| `GET /api/stocks/{symbol}/floating-shareholders` | Return local top floating shareholders |
| `POST /api/stocks/{symbol}/refresh-research-context` | Trigger symbol-level news, reports, metrics, and floating-holder sync |

### Market and Data Center

| API | Behavior |
| --- | --- |
| `GET /api/market/indexes/{code}/bars` | Return local index daily bars |
| `GET /api/market/sectors/{code}/bars` | Return local sector daily bars |
| `GET /api/market/ipo-calendar` | Return local IPO calendar |
| `GET /api/market/ah-pairs` | Return local AH pairs |
| `GET /api/reference/exchanges` | Return local exchange metadata |
| `GET /api/reference/trading-calendar?exchange_code=XSHG` | Return local trading calendar rows |

### API Empty State Contract

Each read API should distinguish:

- `missing`: no sync has ever run for the symbol or dataset.
- `empty`: sync ran successfully and provider returned no records.
- `stale`: data exists but is older than the dataset policy.
- `synced`: data exists and is fresh.

Use a common `data_status` object:

```json
{
  "status": "synced",
  "rows": 12,
  "latest_date": "2026-07-06",
  "provider": "miana",
  "last_synced_at": "2026-07-07T00:10:00+08:00"
}
```

## Frontend Design

### Stock Detail Additions

Add compact sections to the existing stock detail workspace:

1. Quote snapshot strip:
   - last price
   - change and change rate
   - open, high, low, previous close
   - volume, amount, turnover
   - PE TTM, PB, market cap

2. `News` tab:
   - news title
   - announcement date
   - source and platform
   - summary
   - external URL

3. `Research Reports` tab:
   - report title
   - institution
   - announcement date
   - summary
   - source

4. Financial metrics block:
   - latest metric date
   - valuation metrics available from `financialInfo`
   - profitability and balance metrics only where the endpoint returns stable fields

5. Floating shareholders sub-tab:
   - holder name
   - report date
   - hold amount
   - hold ratio
   - float hold ratio
   - holder type

### Market and Data Center Additions

Add:

- Index trend mini charts from local `index_daily_bars`.
- Sector trend mini charts from local `sector_daily_bars`.
- IPO calendar table.
- AH pair table.
- Trading calendar status in Data Center.
- Reference data coverage counters.

Keep this operational and dense. Use tables and compact chart panels, not marketing-style cards.

## Testing Design

### Provider Tests

Add normalization tests for:

- `/ticker/v1/tradeCals`
- `/stock/v2/realtime`
- `/stock/v1/news`
- `/stock/v1/researchReport`
- `/stock/v1/financialInfo`
- `/stock/v1/top10FloatShareholders`
- `/index/v2/kline`
- `/sector/v2/kline`
- `/stock/v1/newIPO`
- `/stock/v1/ahStockList`
- `/stock/v1/exchangeList`

### Repository Tests

Verify:

- Upsert replaces latest quotes per symbol.
- News and reports deduplicate by symbol, date, title, and source.
- Calendar rows resolve last trading day.
- IPO rows update when listing or price fields change.
- AH pair rows replace stale pair metadata.
- Index and sector bars upsert by code and trade date.

### API Tests

Verify:

- Quote API returns the latest collector snapshot and never calls provider code.
- Collector quote snapshot pipeline refreshes selected scopes when TTL expires.
- News/report APIs return stable empty shapes.
- Trading calendar API distinguishes trading and non-trading days.
- Daily sync target date uses calendar `lastTradingDay`.
- Data Center coverage includes all new datasets.

### Frontend Tests

Verify frontend references:

- quote snapshot fields
- news tab
- research report tab
- financial metrics block
- floating shareholder sub-tab
- IPO calendar
- AH pair table
- trading calendar status

## Acceptance Criteria

The next version is acceptable when:

1. Daily sync no longer targets a weekend or holiday as the market date.
2. Stock detail can display quote, news, research reports, financial metrics, and floating shareholders when local data exists.
3. Stock detail does not call Miana for news, reports, metrics, or shareholders on every tab click.
4. Quote snapshots use a TTL and selected-symbol scope in the collector service.
5. Index and sector pages can show daily trend bars from local storage.
6. Data Center shows IPO, AH pairs, exchanges, and trading calendar coverage.
7. Missing data is reported as `missing`, `empty`, `stale`, or `synced`, not as a blank unexplained table.
8. All provider, repository, API, and frontend references are covered by automated tests.

## Risks and Decisions

### Risks

1. Full-market realtime endpoints are enterprise-only.
   - Decision: do not depend on them for normal dashboard or stock detail workflows.
2. Realtime quote polling can become expensive.
   - Decision: collector-owned selected symbols only, with 30-60 second TTL and latest-row overwrite.
3. `financialInfo` field meanings need validation against live payloads.
   - Decision: normalize only fields displayed in the first UI slice and preserve raw payload.
4. `miana-api.md` has some garbled Chinese text.
   - Decision: trust endpoint paths and field names, then verify with provider tests before implementation.
5. Frontend `public/app.js` is already large.
   - Decision: keep UI additions scoped; split files only if the implementation becomes unsafe.

### Explicit Deferrals

Do not include these in the next version:

- Websocket streaming.
- Multi-asset product support.
- Full-market realtime ingestion.
- Intraday transaction detail workspace.
- Portfolio management or trading.

## Recommended Implementation Order

1. Trading calendar provider, storage, and target-date resolution.
2. Stock quote provider in collector mode, latest snapshot storage, and read-only stock detail quote API.
3. News and research report provider, storage, APIs, and stock detail tabs.
4. Financial metrics and floating shareholder provider, storage, APIs, and UI sections.
5. Index and sector K-line provider, storage, sync, and mini trend charts.
6. IPO, AH, exchange reference sync and Data Center views.

This order addresses correctness first, then user-visible research context, then broader market/reference context.
