# Miana Provider and Multi-Source Storage Design

## Goal

Add Miana as a first-class market data provider and preserve all Miana data that may be useful later, while keeping the application queries simple for the current EXPMA daily analysis workflow.

The implementation must support multiple providers storing overlapping data for the same symbol and date. Provider-specific raw data must be retained so future processing can use fields that are not normalized in the first version.

## Scope

In scope:

- Load Miana configuration from local `.env` and environment variables.
- Add `MianaProvider` to the provider chain.
- Store Miana raw API responses with endpoint and request parameters.
- Store normalized Miana stock universe, unadjusted daily bars, forward-adjusted daily bars, derived adjustment factors, company profiles, corporate actions, share capital history, and daily money flow.
- Use Miana as the preferred provider when `STOCK_ANALYZER_MIANA_TOKEN` is configured.
- Prevent duplicate `full_daily_pipeline` jobs from running concurrently.

Out of scope for the first version:

- Full-market default storage of tick-by-tick trade details from `/api/stock/v1/detail`.
- Intraday minute bars.
- A provider comparison UI.
- A full trading-calendar replacement. Calendar rows may still come from existing providers or be inferred later.

Tick-by-tick details should be available as an explicit, symbol-scoped sync operation later because the data volume is high and it is not required for daily EXPMA analysis.

## Miana Endpoints

Core endpoints:

- `/api/stock/v1/stockList`
  - Used for stock universe.
  - Request filters: `countryCode=CHN` or `market=cn_hsj`.
  - Normalized into `stocks` and `stock_provider_profiles`.

- `/api/stock/v2/kline`
  - Used for daily OHLCV.
  - Daily request: `type=d1`.
  - Unadjusted request: `fq=bfq`.
  - Forward-adjusted request: `fq=qfq`.
  - Use `beginDate`, `endDate`, `order=ASC`, and `limit`.
  - `price` maps to `close`.

- `/api/stock/v1/companyInfo`
  - Used for industry and descriptive company metadata.
  - Stored in `stock_company_profiles`.

- `/api/stock/v1/distribute`
  - Used for dividend, split, and rights issue events.
  - Stored in `corporate_actions`.

- `/api/stock/v1/shares`
  - Used for historical total/floating/limited shares.
  - Stored in `share_capital_history`.

- `/api/stock/v1/dailyMoneyflow`
  - Used for daily money-flow fields.
  - Stored in `daily_money_flow`.

Optional endpoint:

- `/api/stock/v1/detail`
  - Tick-by-tick trade details.
  - Not included in full-market default sync.
  - Raw payload storage is allowed only for explicit symbol-scoped sync.

## Configuration

Add settings:

```text
STOCK_ANALYZER_MIANA_TOKEN=
STOCK_ANALYZER_MIANA_BASE_URL=https://miana.com.cn/api
STOCK_ANALYZER_PROVIDER_PRIORITY=miana,tushare,akshare,eastmoney
```

If the token is missing, `miana` is skipped when building the provider chain.

The local `.env` file must remain ignored by Git.

## Storage Design

### Raw Payloads

Extend `raw_provider_payloads` so each provider response can be replayed or reprocessed later:

- `provider`
- `endpoint`
- `symbol`
- `trade_date`
- `request_params_json`
- `date_start`
- `date_end`
- `payload_hash`
- `payload_json`
- `fetched_at`

The unique key should include provider, endpoint, symbol, date range or trade date, request params hash, and payload hash. This keeps repeated fetches idempotent without losing materially different responses.

### Provider Profiles

Create `stock_provider_profiles`:

- `symbol`
- `provider`
- `provider_symbol`
- `exchange`
- `name`
- `industry`
- `country_code`
- `exchange_code`
- `market`
- `type`
- `is_active`
- `is_st`
- `raw_json`
- `updated_at`

The existing `stocks` table remains the canonical stock table used by foreign keys and UI queries. Provider profiles preserve provider-specific names, exchange codes, and metadata without overwriting other provider data.

### Normalized Miana Data

Use existing tables where they already support provider-specific records:

- `daily_bars`
  - Store `fq=bfq` rows as `source=miana`, `is_adjusted=false`.
  - Store `fq=qfq` rows as `source=miana`, `is_adjusted=true`.

- `adjustment_factors`
  - Store `source=miana`.
  - Calculate `adj_factor = qfq_close / bfq_close` for each matching date.

- `analysis_daily_bars`
  - Store selected analysis rows with `source=miana`.
  - This table remains the analysis-ready view, not a complete provider comparison table.

- `stock_daily_status`
  - Store `is_st` inferred from provider profile name.
  - Store `is_suspended=false` unless a later endpoint provides a reliable suspension signal.

Create new normalized tables:

- `stock_company_profiles`
  - `symbol`, `provider`, `industry`, `region`, `concepts`, contact fields, profile text, raw JSON.

- `corporate_actions`
  - `symbol`, `provider`, `action_type`, `currency`, `dividend`, `split_factor`, `notice_date`, `report_date`, `equity_record_date`, `ex_dividend_date`, `pay_cash_date`, raw JSON.

- `share_capital_history`
  - `symbol`, `provider`, `end_date`, `total_shares`, `floating_shares`, `limited_shares`, `change_reason`, raw JSON.

- `daily_money_flow`
  - `symbol`, `provider`, `trade_date`, amount fields for main, super-large, large, medium, and small orders, raw JSON.

## Provider Behavior

`MianaProvider` should:

- Normalize local symbols:
  - Internal `600519.SH` -> Miana `sh600519`.
  - Internal `000001.SZ` -> Miana `sz000001`.
  - Internal BJ symbols -> Miana `bjXXXXXX`.

- Normalize Miana symbols:
  - `XSHG` -> `.SH`.
  - `XSHE` -> `.SZ`.
  - `BJSE` -> `.BJ`.

- Fetch stock universe from Miana and upsert both canonical stocks and provider profiles.

- Fetch daily bars by calling K-line twice:
  - `fq=bfq` for raw bars.
  - `fq=qfq` for adjusted bars.

- Compute Miana adjustment factors from matching raw and adjusted close values.

- Return normalized dictionaries compatible with current repository methods.

- Persist raw payloads through repository methods, not directly inside provider code when possible. Provider code should focus on API calls and normalization.

## Sync Flow

For `full_daily_pipeline`:

1. Reject or return the existing job when another `full_daily_pipeline` is `pending` or `running`.
2. Fetch stock universe from the first configured provider that succeeds.
3. Persist canonical stocks and provider profiles when provider data includes profile details.
4. For each symbol:
   - Fetch unadjusted daily bars.
   - Fetch or derive adjustment factors.
   - Persist unadjusted and adjusted provider bars when available.
   - Materialize analysis rows, indicators, and signals from forward-adjusted rows.
   - Fetch optional company profile, corporate actions, shares, and money flow when enabled for the job.
5. Record symbol-level failures without stopping the full job.

For daily incremental sync:

- Default to the latest required date range, not a historical full range.
- Reuse the same provider priority.

## Error Handling

- Missing Miana token skips the provider.
- Miana HTTP errors are symbol-level failures after retry.
- If `qfq` exists but `bfq` is missing, store adjusted bars and mark adjustment quality as incomplete.
- If `bfq` exists but `qfq` is missing, store raw bars and mark analysis quality as missing adjusted data.
- Raw payload storage failures should be logged and counted as metadata errors, but should not block normalized market data persistence.

## Testing

Add tests for:

- Settings load Miana token and base URL from `.env`.
- Provider chain includes Miana when configured and skips it when token is missing.
- Miana symbol conversion for SH, SZ, and BJ symbols.
- Miana K-line normalization maps `price` to `close`.
- Adjustment factors are derived from `qfq_close / bfq_close`.
- Repository stores provider profiles and normalized Miana side tables.
- Duplicate `full_daily_pipeline` requests do not create concurrent jobs.

## Acceptance Criteria

- A configured Miana token makes `miana` the first provider.
- Miana stock list can populate canonical stocks and provider profiles.
- Miana daily K-line can populate raw bars, adjusted bars, adjustment factors, analysis bars, indicators, and signals.
- Miana company profile, corporate actions, share capital history, and daily money flow are stored for later use.
- Existing AkShare/Tushare behavior remains available as fallback.
- Running a second full pipeline while one is active returns the existing active job or a clear conflict response.
