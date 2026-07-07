# Enterprise Detail Data Display Design

Date: 2026-07-06

## Purpose

This design defines the next version of the stock detail workspace: expose richer enterprise data from Miana-backed local storage before adding any new implementation code.

Miana documentation source: `https://miana.com.cn/document`.

The product goal is to turn the current stock detail page from a K-line-focused view into a practical company research workspace. Users should be able to inspect company profile, financial statements, holders, executives, rewards, corporate actions, share capital, and capital flow without triggering slow live Miana requests on every click.

The operating rule remains:

- Page clicks read local MySQL data.
- Sync jobs fetch Miana data and persist normalized records plus raw payloads.
- Single-stock manual refresh is allowed when the user explicitly requests it.
- Low-frequency enterprise data is not part of the high-frequency market dashboard click path.

## Current System Baseline

The project already has a large part of the required backend foundation.

The Miana document contains the enterprise information endpoints this version should use. The project already maps the following Miana stock enterprise endpoints in `stock_analyzer_app/data_provider/miana_provider.py`:

| Data Family | Method | Miana Endpoint Currently Mapped |
| --- | --- | --- |
| Company profile | `fetch_company_profiles` | `/stock/v1/companyInfo` |
| Corporate actions | `fetch_corporate_actions` | `/stock/v1/distribute` |
| Share capital | `fetch_share_capital_history` | `/stock/v1/shares` |
| Daily money flow | `fetch_daily_money_flow` | `/stock/v1/dailyMoneyflow` |
| Income statement | `fetch_income_statements` | `/stock/v1/incomeSheet` |
| Balance sheet | `fetch_balance_sheets` | `/stock/v1/balanceSheet` |
| Cashflow statement | `fetch_cashflow_statements` | `/stock/v1/cashflow` |
| Top 10 holders | `fetch_top10_holders` | `/stock/v1/top10holders` |
| Company officers | `fetch_company_officers` | `/stock/v1/companyOfficer` |
| Officer rewards | `fetch_officer_rewards` | `/stock/v1/rewards` |

Existing storage tables already cover:

- `stock_company_profiles`
- `corporate_actions`
- `share_capital_history`
- `daily_money_flow`
- `income_statements`
- `balance_sheets`
- `cashflow_statements`
- `stock_top10_holders`
- `stock_company_officers`
- `stock_officer_rewards`
- `raw_provider_payloads`

Existing APIs already expose stable entry points:

- `GET /api/stocks/{symbol}/overview`
- `GET /api/stocks/{symbol}/financials`
- `GET /api/stocks/{symbol}/capital-flow`
- `GET /api/data-center/coverage`

The frontend currently uses those APIs but displays only a small subset of fields.

## Scope

### In Scope

1. Expand stock detail UI to show enterprise research data already persisted locally.
2. Add missing read API fields where repository data exists but is not surfaced cleanly.
3. Improve empty, stale, and missing-sync states for enterprise modules.
4. Add coverage counters for each enterprise data family.
5. Add tests that lock the API shape and frontend references.
6. Preserve raw Miana payloads for future field backfill.

### Out of Scope

1. No new remote deployment.
2. No live Miana request on ordinary page click.
3. No financial ratio modeling beyond direct display and simple derived labels.
4. No multi-provider reconciliation UI.
5. No chart-heavy financial analytics in this first version.
6. No automatic full-market enterprise refresh on every daily market sync.

## Product Design

### Stock Detail Layout

Replace the current long stock detail grid with a tabbed research workspace:

1. `行情K线`
2. `财务三表`
3. `企业资料`
4. `股东高管`
5. `分红股本`
6. `资金流`
7. `数据状态`

The header stays compact:

- Stock name and symbol
- Exchange and industry tags
- Latest available trade date
- Data quality badge
- Enterprise data freshness badge
- Manual refresh button for current stock enterprise data

### Tab 1: 行情K线

Keep existing K-line behavior:

- Day/week/month switch
- EXPMA overlays
- Recent daily rows
- Strategy signals

This tab should not be expanded in this version except to display a clearer data freshness label.

### Tab 2: 财务三表

Show three sub-tabs:

1. 利润表
2. 资产负债表
3. 现金流量表

Profit table columns:

- `report_date`
- `notice_date`
- `report_period`
- `currency`
- `revenue`
- `operating_revenue`
- `operating_profit`
- `total_profit`
- `net_profit`
- `net_profit_parent`
- `eps`

Balance table columns:

- `report_date`
- `notice_date`
- `report_period`
- `currency`
- `total_assets`
- `total_liabilities`
- `total_equity`
- `monetary_funds`
- `accounts_receivable`
- `inventory`

Cashflow table columns:

- `report_date`
- `notice_date`
- `report_period`
- `currency`
- `net_operating_cashflow`
- `net_investing_cashflow`
- `net_financing_cashflow`
- `cash_and_equivalents`

Default sort:

- Newest `report_date` first.

Display behavior:

- Amounts right-aligned.
- Currency shown once per row.
- Empty state distinguishes `未同步` from `Miana 无返回`.
- A small summary strip shows the latest report period and latest announcement date.

### Tab 3: 企业资料

Company profile fields:

- `industry`
- `region`
- `concepts`
- `address`
- `legal_person`
- `chairman`
- `president`
- `secretary`
- `org_tel`
- `org_email`
- `org_web`
- `main_business`
- `org_profile`

Layout:

- Use descriptions for short fields.
- Use text blocks for `main_business` and `org_profile`.
- Keep all content in the stock detail workspace, not a separate page.

### Tab 4: 股东高管

Sub-tabs:

1. 十大股东
2. 董监高
3. 薪酬持股

Top 10 holders columns:

- `report_date`
- `holder_rank`
- `holder_name`
- `hold_volume`
- `hold_ratio`
- `share_type`

Company officers columns:

- `officer_name`
- `title`
- `start_date`
- `end_date`

Officer rewards columns:

- `report_date`
- `officer_name`
- `title`
- `reward`
- `hold_volume`

Default behavior:

- Holders grouped visually by `report_date`.
- Rewards sorted by `report_date DESC, reward DESC`.
- If officer list exists but rewards are empty, show officer data and mark rewards separately as empty.

### Tab 5: 分红股本

Sub-tabs:

1. 分红送配
2. 股本变动

Corporate actions columns:

- `notice_date`
- `report_date`
- `action_type`
- `currency`
- `dividend`
- `split_factor`
- `equity_record_date`
- `ex_dividend_date`
- `pay_cash_date`

Share capital columns:

- `end_date`
- `total_shares`
- `floating_shares`
- `limited_shares`
- `change_reason`

Display behavior:

- Dates sorted newest first.
- Use compact tables, not cards per event.
- Missing dates display `-`, not blank cells.

### Tab 6: 资金流

Daily money flow fields:

- `trade_date`
- `amount`
- `main_net_inflow_amount`
- `main_net_ratio`
- `super_large_inflow`
- `super_large_outflow`

Display behavior:

- Latest row summary strip.
- Recent rows table.
- `main_net_ratio` formatted as percent.
- Positive and negative net inflow styled consistently with existing market red/green conventions.

### Tab 7: 数据状态

Show module-level data readiness:

| Module | Status Source |
| --- | --- |
| 公司资料 | `company_profile` exists |
| 财务三表 | count of income, balance, cashflow rows |
| 股东 | count of top holder rows |
| 董监高 | count of officer rows |
| 薪酬 | count of reward rows |
| 分红 | count of corporate action rows |
| 股本 | count of share capital rows |
| 资金流 | count of money flow rows |

Each module should show:

- row count
- newest date if available
- provider name
- status: `synced`, `empty`, `stale`, or `missing`

## Backend API Design

### `GET /api/stocks/{symbol}/overview`

Return a complete enterprise overview shape:

```json
{
  "stock": {},
  "latest_bar": {},
  "company_profile": {},
  "share_capital": [],
  "corporate_actions": [],
  "holders": [],
  "officers": [],
  "officer_rewards": [],
  "data_quality": {
    "has_bars": true,
    "has_research_data": true,
    "enterprise_modules": {
      "company_profile": {"rows": 1, "status": "synced"},
      "share_capital": {"rows": 3, "status": "synced"},
      "corporate_actions": {"rows": 2, "status": "synced"},
      "holders": {"rows": 10, "status": "synced"},
      "officers": {"rows": 8, "status": "synced"},
      "officer_rewards": {"rows": 8, "status": "synced"}
    }
  }
}
```

Notes:

- `officer_rewards` should be added to the overview response because the current provider and storage already support it.
- Existing clients should not break if they ignore the new fields.
- Empty arrays should be returned for missing optional data.

### `GET /api/stocks/{symbol}/financials`

Return:

```json
{
  "symbol": "000001.SZ",
  "income": [],
  "balance": [],
  "cashflow": [],
  "summary": {
    "latest_report_date": "2025-12-31",
    "income_rows": 4,
    "balance_rows": 4,
    "cashflow_rows": 4
  }
}
```

### `GET /api/stocks/{symbol}/capital-flow`

Return:

```json
{
  "symbol": "000001.SZ",
  "rows": [],
  "summary": {
    "latest_trade_date": "2026-07-03",
    "rows": 20
  }
}
```

### `GET /api/data-center/coverage`

Extend `research` coverage:

```json
{
  "research": {
    "financial_statements": {"rows": 0},
    "capital_flow": {"symbols": 0, "rows": 0},
    "company_profiles": {"symbols": 0, "rows": 0},
    "corporate_actions": {"symbols": 0, "rows": 0},
    "share_capital": {"symbols": 0, "rows": 0},
    "holders": {"symbols": 0, "rows": 0},
    "officers": {"symbols": 0, "rows": 0},
    "officer_rewards": {"symbols": 0, "rows": 0}
  }
}
```

## Storage Design

No new table is required for the first implementation slice if Miana documentation confirms the existing mapped fields are sufficient.

Repository additions:

1. Include `stock_officer_rewards` in `stock_research_snapshot`.
2. Add enterprise module status metadata in `stock_research_snapshot`.
3. Add `summary` to `stock_financials`.
4. Add `summary` to `stock_capital_flow`.
5. Extend `data_center_coverage` with per-family counts.

If the Miana documentation lists additional enterprise fields that are not currently normalized, prefer this policy:

- Add normalized columns only for fields needed in the UI.
- Preserve all other fields in `raw_json`.
- Avoid schema churn for fields that are not displayed or filtered.

## Sync Design

### Manual Current-Stock Refresh

The existing `fundamental_refresh_pipeline` should remain the primary refresh path for enterprise data.

Stock detail should expose one explicit action:

- `刷新企业数据`

Behavior:

1. Trigger current-stock fundamental refresh.
2. Refresh page data after job completes.
3. Show job status if refresh is still running.
4. Do not block basic K-line viewing while enterprise refresh runs.

### Scheduled Enterprise Refresh

Recommended default:

- Daily core K-line sync at `00:00` remains focused on market data.
- Enterprise data refresh runs separately.
- Company profile, officers, share capital, and holders are low-frequency.
- Financial statements and corporate actions can refresh daily for watched or recently opened stocks.

Suggested schedule for next implementation:

| Data Family | Recommended Refresh |
| --- | --- |
| Company profile | Monthly or manual |
| Financial statements | Daily stale-symbol batch plus manual |
| Corporate actions | Daily stale-symbol batch plus manual |
| Share capital | Weekly plus manual |
| Holders | Weekly plus manual |
| Officers | Monthly plus manual |
| Officer rewards | Monthly plus manual |
| Capital flow | Previous trading day for watched/recent symbols |

## Frontend Design

The stock detail view should stay dense and operational. It should avoid marketing-style cards and avoid nesting cards inside cards.

Implementation constraints:

- Use tabs for major data families.
- Use tables for repeated data.
- Use descriptions only for company profile and status metadata.
- Use stable table heights so the page does not jump when switching tabs.
- Keep amount and percentage formatting consistent with existing helpers.
- Do not add explanatory text that describes how to use the page.

Frontend state additions:

```js
stockEnterpriseActiveTab: "financials"
stockOverview.company_profile
stockOverview.holders
stockOverview.officers
stockOverview.officer_rewards
stockOverview.corporate_actions
stockOverview.share_capital
stockOverview.data_quality.enterprise_modules
stockFinancials.summary
stockCapitalFlow.summary
```

## Miana Documentation Field Checklist

Before implementation, compare the Miana documentation at `https://miana.com.cn/document` against the current provider mapping for these endpoint groups:

1. `/stock/v1/companyInfo`
2. `/stock/v1/incomeSheet`
3. `/stock/v1/balanceSheet`
4. `/stock/v1/cashflow`
5. `/stock/v1/top10holders`
6. `/stock/v1/companyOfficer`
7. `/stock/v1/rewards`
8. `/stock/v1/distribute`
9. `/stock/v1/shares`
10. `/stock/v1/dailyMoneyflow`

For each endpoint, verify and record the documented details in the implementation plan:

- required request parameters
- response list path
- date field names
- amount units
- percentage units
- whether fields are already normalized
- whether raw payload contains additional fields worth displaying

If documentation includes additional high-value fields, add them only if they serve one of the planned UI sections.

## Implementation Phases

### Phase 1: Backend Read Shape

Goal:

- Make existing enterprise data available through stable API shapes.

Work:

1. Extend repository snapshots.
2. Add summaries and module statuses.
3. Add tests for `overview`, `financials`, `capital-flow`, and `data-center`.

Exit criteria:

- API returns all planned fields with empty arrays or empty objects when data is missing.
- Existing API consumers still pass tests.

### Phase 2: Frontend Stock Detail Workspace

Goal:

- Display existing enterprise data in the stock detail page.

Work:

1. Replace the current stock detail grid with tabs.
2. Add financial statement tables.
3. Add company profile descriptions.
4. Add holder, officer, and reward tables.
5. Add corporate action and share capital tables.
6. Add capital flow summary and table.
7. Add data status tab.

Exit criteria:

- A synced stock can be inspected without opening developer tools.
- Empty modules show clear empty states.
- Frontend static tests verify the new tabs, state keys, and API fields.

### Phase 3: Manual Enterprise Refresh UX

Goal:

- Let users refresh enterprise data for the current stock explicitly.

Work:

1. Add or reuse API trigger for current-stock fundamental refresh.
2. Add stock-detail refresh button.
3. Display running/completed/failed state.
4. Reload stock detail data after completion.

Exit criteria:

- Refresh does not trigger on normal page click.
- A failed refresh does not break the stock detail page.

### Phase 4: Coverage and Data Center

Goal:

- Make enterprise data readiness visible.

Work:

1. Extend coverage API.
2. Add data-center rows for each enterprise data family.
3. Surface latest successful enterprise refresh job.
4. Show missing/empty/stale distinction.

Exit criteria:

- User can tell whether a missing table is due to no sync, no provider data, or failed sync.

## Test Plan

### Provider Tests

- Verify Miana response normalization for every enterprise endpoint currently used.
- Include variants for date aliases and numeric field aliases.
- Preserve `raw_json`.

### Repository Tests

- Upsert and read company profile.
- Upsert and read financial statements.
- Upsert and read holders/officers/rewards.
- Upsert and read corporate actions/share capital.
- Upsert and read money flow.
- Verify overview includes `officer_rewards`.
- Verify coverage includes all enterprise families.

### API Tests

- `GET /api/stocks/{symbol}/overview` returns stable enterprise shape.
- `GET /api/stocks/{symbol}/financials` returns `summary`.
- `GET /api/stocks/{symbol}/capital-flow` returns `summary`.
- `GET /api/data-center/coverage` includes expanded research coverage.
- Empty-data symbols return stable shapes.

### Frontend Tests

- Stock detail contains planned tab labels.
- Frontend references new overview fields.
- Frontend references `officer_rewards`.
- Frontend references financial and capital-flow summaries.
- Data center references expanded research coverage keys.

## Acceptance Criteria

The version is acceptable when:

1. Stock detail displays company profile, financial statements, holders, officers, officer rewards, corporate actions, share capital, and capital flow when local data exists.
2. Page click does not call Miana directly.
3. Missing enterprise data is shown as empty or missing, not as a broken page.
4. User can manually refresh enterprise data for the current stock.
5. Data center shows coverage for each enterprise data family.
6. API response shapes are stable and tested.
7. Repository tests verify persistence and read paths.
8. Frontend tests verify the new display surfaces.

## Risks

1. Miana field names may differ from current assumptions.
   - Mitigation: verify endpoint docs before coding and keep `raw_json`.
2. Frontend `public/app.js` is already large.
   - Mitigation: keep the first implementation scoped to stock detail tabs; split components only if the existing architecture supports it safely.
3. Enterprise data refresh can be slow for full market.
   - Mitigation: default to single-stock manual refresh and stale-symbol batches.
4. Financial values may have inconsistent units.
   - Mitigation: display raw normalized numeric values first, then add unit labels only after documentation confirmation.

## Open Decisions

1. Whether to include all raw Miana fields in an expandable debug panel.
   - Recommendation: no for the first version; keep UI focused.
2. Whether capital flow should refresh for all stocks daily.
   - Recommendation: no; refresh watched/recent symbols first.
3. Whether to add financial trend charts immediately.
   - Recommendation: no; tables first, charts later after field units are validated.
4. Whether to split `public/app.js` as part of this version.
   - Recommendation: defer unless the edit becomes unsafe; this project currently uses a single static Vue file.
