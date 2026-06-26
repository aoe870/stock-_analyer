# Stock Analysis Frontend Design

## Purpose

Build a local browser UI for the A-share stock data service. The frontend is an operational research workspace: it shows data sync health, data coverage, stock universe status, EXPMA17/50 screening, stock detail charts, and backtest results.

The UI must support repeated daily use. It should be quiet, dense, and predictable rather than marketing-oriented.

## Source Of Truth

This frontend design depends on the backend design:

- `docs/superpowers/specs/2026-06-27-expma-stock-analysis-web-design.md`

If API or data behavior conflicts with this frontend document, the backend design controls service semantics and this document controls presentation and interaction.

## Version 1 Decisions

- Frontend stack: React + Vite + TypeScript.
- Charts: ECharts.
- API/server state: React Query.
- Styling: CSS modules or a small app-level CSS system; avoid large UI frameworks unless implementation pressure justifies one.
- Routing: client-side routes for main workspace pages.
- Layout: left navigation, top status bar, dense work area.
- Product style: operational dashboard and research tool, not a landing page.
- Authentication: out of scope for version 1.
- Mobile: responsive enough for inspection, but primary target is desktop.

## Information Architecture

Primary navigation:

- Dashboard
- Sync Center
- Stocks
- Screening
- Backtests
- Stock Detail
- Settings

Secondary pages:

- Backtest Result
- Sync Job Detail
- Screening Result

The app should preserve important filters in the URL where practical, especially selected date, strategy, symbol, and run IDs.

## App Shell

The app shell provides a stable frame:

- Left sidebar navigation with icon + label items.
- Top status bar with API health, MySQL status, scheduler status, latest successful sync time, and active task count.
- Main content area with page-specific controls and data.
- Toast/notification area for task creation, failures, and completion.

The shell should avoid nested cards. Use full-width page bands, tables, toolbars, and panels. Cards are appropriate for summary metric tiles and repeated result items only.

## Visual Style

The UI should feel like a professional data terminal:

- Neutral background with clear table contrast.
- Restrained accent colors for signal states and status.
- No hero sections, decorative gradients, or ornamental background shapes.
- 8px or smaller border radius unless a component library requires otherwise.
- Dense typography sized for scanning, not presentation.
- Stable row heights and toolbar heights.
- Icons for navigation and compact actions. Use lucide icons if available.

Suggested semantic colors:

- Healthy/complete: green.
- Running/pending: blue.
- Warning/partial coverage: amber.
- Failed/error: red.
- Neutral/missing: gray.
- Buy-like signals: green.
- Risk-reduction/clear signals: red or amber depending severity.

Avoid a one-note palette. The interface should not be dominated by a single hue family.

## Pages

### Dashboard

Purpose: first page for daily status and recent activity.

Content:

- Service health: API, MySQL, migrations, scheduler.
- Latest sync summary: last successful full pipeline, last failed job, next scheduled sync.
- Data coverage summary: latest trade date, symbols complete, symbols missing, data quality counts.
- Recent screening runs.
- Recent backtest runs.
- Quick actions: run full daily pipeline, open screening, open backtest.

Behavior:

- Poll health and active tasks.
- Show coverage gaps without auto-starting sync.
- When a sync action starts, show task ID and route to Sync Job Detail.

### Sync Center

Purpose: operate and inspect data acquisition.

Content:

- Manual sync toolbar:
  - job type selector
  - date range inputs
  - optional symbol selector
  - provider priority display
  - start button
- Job table:
  - job ID
  - type
  - status
  - requested by
  - start/end time
  - success/skipped/failed/retry counts
  - provider fallback count
- Coverage panel:
  - latest available trade date
  - missing symbols
  - stale symbols
  - data quality distribution

Sync Job Detail:

- Summary counts.
- Timeline/status log.
- Failed item table with symbol, date range, provider, attempt count, error.
- Retry failed items action.

Behavior:

- Long-running jobs are created through the API and then polled.
- Top-level status `completed_with_errors` should be visually distinct from `failed`.
- Failed item table must be filterable by provider, symbol, and error type.

### Stocks

Purpose: inspect local stock universe and data readiness.

Content:

- Filters:
  - exchange
  - active listing status
  - ST status
  - industry
  - data coverage state
  - keyword search
- Table columns:
  - symbol
  - name
  - exchange
  - industry
  - active/ST flags
  - latest analysis date
  - data quality
  - last sync time

Behavior:

- Clicking a symbol opens Stock Detail.
- Missing coverage should be visible without opening detail.

### Screening

Purpose: run and inspect EXPMA17/50 screening.

Controls:

- strategy selector, default `expma_17_50`
- trade date
- universe filters
- signal filter:
  - buy-like
  - risk-reduction
  - trend-qualified
  - all
- exclude ST toggle
- exclude suspended toggle
- data quality selector
- run button

Result summary:

- evaluated count
- skipped count
- missing coverage count
- error count
- price mode
- latest sync time

Result table:

- symbol/name
- trade date
- close/high/low
- EXPMA17
- EXPMA50
- trend state
- selected signal
- raw flags summary
- data source
- data quality
- reason

Behavior:

- Screening allows partial coverage by default.
- Missing coverage rows must be summarized and optionally inspectable.
- Clicking a result opens Stock Detail on the same date.

### Backtests

Purpose: configure backtests and browse run history.

Controls:

- strategy selector
- symbol selector or universe filter
- start date
- end date
- initial capital
- fee rate
- slippage rate
- price mode
- allow partial coverage toggle, off by default
- run button

Run history table:

- run ID
- strategy
- symbol count
- date range
- status
- total return
- max drawdown
- trade count
- created/finished time
- stale marker

Behavior:

- Backtest must block when coverage is insufficient unless partial coverage is explicitly enabled.
- If partial coverage is enabled, skipped symbols must be listed.
- Clicking a completed run opens Backtest Result.

### Backtest Result

Purpose: inspect performance and audit trades.

Content:

- Summary metrics:
  - total return
  - annualized return
  - max drawdown
  - win rate
  - trade count
  - average trade return
  - exposure
  - turnover
- Metadata:
  - strategy
  - price mode
  - fee/slippage
  - symbols
  - data coverage state
  - stale marker
- Charts:
  - equity curve
  - drawdown curve
- Tables:
  - trades
  - unfilled signals
  - daily positions/equity

Behavior:

- Stale results should display a clear rerun action.
- Trade table rows link to Stock Detail at signal or execution date.

### Stock Detail

Purpose: inspect one symbol across price, indicators, and signals.

Controls:

- symbol search
- date range
- price mode
- strategy selector

Content:

- Stock header: symbol, name, exchange, industry, active/ST status.
- Data coverage strip.
- K-line chart with:
  - OHLC candlesticks
  - EXPMA17
  - EXPMA50
  - volume subplot
  - signal markers
- Signal table:
  - trade date
  - selected signal
  - raw flags
  - close
  - EXPMA values
  - warmup-ready state
- Data quality panel.

Behavior:

- Chart must stay readable at desktop and tablet widths.
- Signal marker legend should be persistent.
- Rows and chart markers should coordinate hover/selection when practical.

### Settings

Purpose: inspect local configuration and adjust non-secret defaults.

Content:

- MySQL connection status.
- Migration status.
- Provider priority.
- Tushare token presence/status, without displaying the token.
- Scheduler enabled state.
- Sync time and timezone.
- Default strategy.
- Default price mode.
- Default fee/slippage.
- Raw payload retention setting, if implemented.

Behavior:

- Secret editing is optional for version 1. If supported, the UI must explain storage behavior and never echo secrets back.
- Settings changes that affect sync or analysis should indicate whether restart or recomputation is required.

## API Integration

The frontend consumes the backend APIs from the backend design:

- health/settings/strategies
- sync jobs and coverage
- stocks and stock detail data
- screenings
- backtests

React Query keys should be stable and structured:

- `["health"]`
- `["settings"]`
- `["syncJobs", filters]`
- `["syncJob", jobId]`
- `["syncCoverage", filters]`
- `["stocks", filters]`
- `["stock", symbol]`
- `["stockBars", symbol, range, priceMode]`
- `["stockSignals", symbol, strategyKey, range]`
- `["screeningRun", runId]`
- `["backtestRun", runId]`

Polling:

- Health: low-frequency polling.
- Active sync jobs: medium-frequency polling while jobs are running.
- Active screening/backtest tasks: medium-frequency polling until terminal status.
- Completed historical data: no polling unless invalidated by user action.

## State And URL Behavior

Keep server data in React Query. Keep local transient UI state in components unless it is shared across pages.

URL query parameters should preserve:

- selected symbol
- trade date
- date ranges
- strategy key
- active run ID
- major filters

This makes browser refresh and shared URLs useful during research.

## Tables

Tables are central to the product and must be designed as first-class components.

Requirements:

- Stable column widths.
- Sortable key numeric/date columns.
- Filterable signal/status/data quality columns.
- Sticky header for long tables.
- Pagination or virtualization for large lists.
- Compact row density.
- Empty, loading, error, and partial-data states.
- Export can be added later; not required in version 1.

## Charts

Use ECharts for:

- K-line chart with EXPMA overlays and volume.
- Signal markers.
- Equity curve.
- Drawdown curve.
- Optional coverage timeline.

Chart requirements:

- Use real data from API, not generated placeholder data in production screens.
- Preserve readable labels and tooltips.
- Avoid overlapping chart controls and legends.
- Support resize when the sidebar or viewport changes.
- Show data quality/coverage warnings near the chart, not hidden in tooltips only.

## Long-Running Task UX

Long-running actions include sync, screening, and backtest creation.

Required interaction:

1. User submits request.
2. UI shows immediate task/job ID.
3. UI polls status endpoint.
4. UI shows progress summary and latest errors.
5. Terminal state routes or links to result page.

Terminal states:

- `completed`
- `completed_with_errors`
- `failed`
- `cancelled`, if cancellation is later implemented

Version 1 does not require cancellation, but the task UI should leave room for it.

## Error And Empty States

Design explicit states for:

- API unreachable.
- MySQL unreachable.
- Migrations missing.
- Scheduler disabled.
- No synced data.
- Partial sync failures.
- Missing coverage.
- Backtest blocked by insufficient coverage.
- Provider token missing.
- Chart has no rows in selected range.

Error messages should be actionable. For example, missing coverage should offer a sync action; migration failure should point to deployment scripts.

## Responsive Layout

Primary target is desktop:

- Desktop: persistent sidebar and wide data tables.
- Tablet: collapsible sidebar; tables remain horizontally scrollable when necessary.
- Phone: read-only inspection is acceptable; full workflow ergonomics are not a version 1 requirement.

Text must not overflow buttons, table cells, or metric tiles. Long symbols/names should truncate with tooltip where needed.

## Accessibility And Keyboard

Version 1 should support:

- Visible focus states.
- Keyboard navigation through forms and primary actions.
- Labels for form controls.
- Sufficient color contrast.
- Signal/status colors paired with text labels.

## Testing Strategy

Frontend tests:

- App shell renders navigation and top status.
- Dashboard renders health and sync summary.
- Sync Center starts a job and renders status updates.
- Sync Job Detail renders failed items and retry action.
- Stocks page filters and opens Stock Detail.
- Screening page submits parameters and renders result counts/table.
- Backtest page blocks missing coverage unless partial coverage is enabled.
- Backtest Result renders metrics, charts, trades, and stale marker.
- Stock Detail renders K-line chart, EXPMA overlays, signal markers, and data quality warnings.
- Settings page never displays secret token values.

Preferred tools:

- Component tests for reusable controls and tables.
- API mocking for page tests.
- Playwright smoke tests for critical flows if the frontend implementation uses a real dev server.

## File Structure

Recommended frontend layout:

```text
apps/web/
  index.html
  package.json
  vite.config.ts
  src/
    main.tsx
    app/
      App.tsx
      routes.tsx
      queryClient.ts
    api/
      client.ts
      health.ts
      settings.ts
      sync.ts
      stocks.ts
      screening.ts
      backtests.ts
    components/
      AppShell.tsx
      StatusBar.tsx
      DataTable.tsx
      MetricTile.tsx
      TaskStatusBadge.tsx
      DataQualityBadge.tsx
      SignalBadge.tsx
      CoverageSummary.tsx
    charts/
      KLineChart.tsx
      EquityCurveChart.tsx
      DrawdownChart.tsx
    pages/
      DashboardPage.tsx
      SyncCenterPage.tsx
      SyncJobDetailPage.tsx
      StocksPage.tsx
      ScreeningPage.tsx
      ScreeningResultPage.tsx
      BacktestsPage.tsx
      BacktestResultPage.tsx
      StockDetailPage.tsx
      SettingsPage.tsx
    styles/
      tokens.css
      app.css
```

If the implementation chooses to serve static frontend files from FastAPI in version 1, the built output can be copied into `public/` or served from the Vite build directory. Source code should remain under `apps/web/`.

## Acceptance Criteria

The frontend design is implemented acceptably when:

- The app starts locally and connects to the FastAPI backend.
- The app shell exposes all primary pages.
- Health, MySQL, scheduler, and latest sync status are visible globally.
- Users can start and inspect sync jobs.
- Users can inspect stock universe and data coverage.
- Users can run EXPMA17/50 screening and inspect partial coverage.
- Users can configure and run backtests with coverage validation.
- Users can inspect backtest metrics, equity, drawdown, trades, and positions.
- Users can inspect a stock K-line chart with EXPMA17, EXPMA50, signal markers, and data quality.
- Settings expose provider priority, token presence, scheduler settings, and default costs without leaking secrets.
- Tables and charts have loading, empty, error, and partial-data states.
- Core frontend flows are covered by automated tests.
