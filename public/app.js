const state = {
  route: "dashboard",
  health: null,
  settings: null,
  coverage: null,
  jobs: [],
  stocks: [],
  selectedSymbol: localStorage.getItem("selectedSymbol") || "",
  lastScreening: null,
  lastBacktest: null,
};

const routes = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Local service status, data coverage, and recent sync activity.",
    render: renderDashboard,
  },
  sync: {
    title: "Sync Center",
    subtitle: "Run daily data sync jobs and inspect provider failures.",
    render: renderSyncCenter,
  },
  stocks: {
    title: "Stocks",
    subtitle: "Local stock universe stored in MySQL.",
    render: renderStocks,
  },
  screening: {
    title: "Screening",
    subtitle: "Evaluate materialized EXPMA17/50 signals from local analysis data.",
    render: renderScreening,
  },
  backtests: {
    title: "Backtests",
    subtitle: "Run historical strategy checks against local analysis bars.",
    render: renderBacktests,
  },
  "stock-detail": {
    title: "Stock Detail",
    subtitle: "Inspect bars, indicators, signals, and data quality for one symbol.",
    render: renderStockDetail,
  },
  settings: {
    title: "Settings",
    subtitle: "Runtime configuration and local service defaults.",
    render: renderSettings,
  },
};

const viewRoot = document.querySelector("#view-root");
const pageTitle = document.querySelector("#page-title");
const pageSubtitle = document.querySelector("#page-subtitle");
const apiStatus = document.querySelector("#api-status");

function fmt(value, digits = 2) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : String(value);
}

function pct(value) {
  return value === null || value === undefined ? "" : `${fmt(Number(value) * 100, 2)}%`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText} ${text}`.trim());
  }
  return response.json();
}

async function loadCoreData() {
  const [health, settings, coverage, jobsPayload, stocksPayload] = await Promise.all([
    api("/api/health"),
    api("/api/settings"),
    api("/api/sync/coverage"),
    api("/api/sync/jobs"),
    api("/api/stocks"),
  ]);
  state.health = health;
  state.settings = settings;
  state.coverage = coverage;
  state.jobs = jobsPayload.jobs || [];
  state.stocks = stocksPayload.stocks || [];
  if (!state.selectedSymbol && state.stocks.length) {
    state.selectedSymbol = state.stocks[0].symbol;
  }
  setApiStatus(true);
}

function setApiStatus(ok, label) {
  apiStatus.className = ok ? "status-pill ok" : "status-pill error";
  apiStatus.textContent = label || (ok ? "API online" : "API error");
}

function currentRoute() {
  const route = window.location.hash.replace(/^#\//, "") || "dashboard";
  return routes[route] ? route : "dashboard";
}

async function renderCurrentRoute() {
  state.route = currentRoute();
  const config = routes[state.route];
  pageTitle.textContent = config.title;
  pageSubtitle.textContent = config.subtitle;
  document.querySelectorAll(".nav-list a").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === state.route);
  });
  viewRoot.innerHTML = `<section class="panel span-12"><span class="muted">Loading ${config.title.toLowerCase()}...</span></section>`;
  try {
    await loadCoreData();
    await config.render();
  } catch (error) {
    setApiStatus(false);
    viewRoot.innerHTML = errorPanel(error);
  }
}

function errorPanel(error) {
  return `
    <section class="panel span-12">
      <div class="panel-head"><h2>Request failed</h2></div>
      <p class="muted">${escapeHtml(error.message)}</p>
    </section>
  `;
}

function renderDashboard() {
  const latest = state.jobs[0];
  const coverage = state.coverage || {};
  const analysis = coverage.analysis_daily_bars || {};
  const indicators = coverage.daily_indicators || {};
  const signals = coverage.strategy_signals || {};
  viewRoot.innerHTML = `
    <section class="page-grid">
      ${metricPanel("Database", state.health?.database?.connected ? "Connected" : "Disconnected", state.health?.database?.message || "", state.health?.database?.connected ? "ok" : "error")}
      ${metricPanel("Migrations", state.health?.migrations?.applied ?? "-", state.health?.migrations?.status || "", state.health?.migrations?.status === "ok" ? "ok" : "warn")}
      ${metricPanel("Scheduler", state.health?.scheduler?.running ? "Running" : "Stopped", (state.health?.scheduler?.jobs || []).join(", "), state.health?.scheduler?.running ? "ok" : "warn")}
      ${metricPanel("Analysis Rows", analysis.rows ?? 0, `${analysis.symbols ?? 0} symbols`, "ok")}
      <section class="panel span-8">
        <div class="panel-head"><h2>Recent Sync Jobs</h2><a class="link-button" href="#/sync">Open Sync Center</a></div>
        ${jobsTable(state.jobs.slice(0, 8))}
      </section>
      <section class="panel span-4">
        <div class="panel-head"><h2>Coverage</h2></div>
        <div class="summary-list">
          ${kv("Analysis daily bars", `${analysis.rows ?? 0} rows`)}
          ${kv("Indicator rows", `${indicators.rows ?? 0}`)}
          ${kv("Signal rows", `${signals.rows ?? 0}`)}
          ${kv("Latest completed job", latest?.status || "none")}
        </div>
      </section>
    </section>
  `;
}

function renderSyncCenter() {
  viewRoot.innerHTML = `
    <section class="page-grid">
      <section class="panel span-12">
        <div class="panel-head"><h2>Manual Daily Pipeline</h2></div>
        <form id="sync-form" class="toolbar">
          <input name="symbols" placeholder="Symbols, e.g. 000001.SZ,600000.SH" />
          <input name="start_date" type="date" value="2024-01-02" />
          <input name="end_date" type="date" value="2024-01-05" />
          <button type="submit">Run Sync</button>
        </form>
        <p id="sync-message" class="muted"></p>
      </section>
      <section class="panel span-12">
        <div class="panel-head"><h2>Sync Jobs</h2><button id="reload-jobs" class="secondary" type="button">Reload</button></div>
        <div id="sync-jobs">${jobsTable(state.jobs)}</div>
      </section>
    </section>
  `;
  document.querySelector("#sync-form").addEventListener("submit", runSyncJob);
  document.querySelector("#reload-jobs").addEventListener("click", renderCurrentRoute);
}

function renderStocks() {
  viewRoot.innerHTML = `
    <section class="panel span-12">
      <div class="panel-head">
        <h2>Stock Universe</h2>
        <div class="toolbar">
          <input id="stock-filter" placeholder="Filter symbol or name" />
          <span class="muted">${state.stocks.length} rows</span>
        </div>
      </div>
      <div id="stocks-table">${stocksTable(state.stocks)}</div>
    </section>
  `;
  document.querySelector("#stock-filter").addEventListener("input", (event) => {
    const term = event.target.value.toLowerCase();
    const rows = state.stocks.filter((stock) => `${stock.symbol} ${stock.name}`.toLowerCase().includes(term));
    document.querySelector("#stocks-table").innerHTML = stocksTable(rows);
    bindStockLinks();
  });
  bindStockLinks();
}

function renderScreening() {
  viewRoot.innerHTML = `
    <section class="page-grid">
      <section class="panel span-12">
        <div class="panel-head"><h2>Screening Parameters</h2></div>
        <form id="screening-form" class="toolbar">
          <input name="trade_date" type="date" />
          <input name="symbols" placeholder="Optional symbols" />
          <select name="signal_filter">
            <option value="all">All signals</option>
            <option value="buy_like">Buy-like</option>
            <option value="risk_reduction">Risk reduction</option>
            <option value="trend_up">Trend up</option>
          </select>
          <select name="price_mode">
            <option value="forward_adjusted">Forward adjusted</option>
            <option value="unadjusted">Unadjusted</option>
          </select>
          <button type="submit">Run Screening</button>
        </form>
      </section>
      <section class="panel span-12">
        <div class="panel-head"><h2>Results</h2><span id="screening-summary" class="muted"></span></div>
        <div id="screening-results">${screeningTable(state.lastScreening?.results || [])}</div>
      </section>
    </section>
  `;
  document.querySelector("#screening-form").addEventListener("submit", runScreening);
}

function renderBacktests() {
  viewRoot.innerHTML = `
    <section class="page-grid">
      <section class="panel span-12">
        <div class="panel-head"><h2>Backtest Parameters</h2></div>
        <form id="backtest-form" class="toolbar">
          <input name="symbols" placeholder="Symbols, blank uses local universe" />
          <input name="start_date" type="date" value="2024-01-01" />
          <input name="end_date" type="date" value="2024-12-31" />
          <input name="initial_capital" type="number" value="100000" min="1" />
          <input name="fee_rate" type="number" value="0.0003" step="0.0001" />
          <input name="slippage_rate" type="number" value="0.0005" step="0.0001" />
          <button type="submit">Run Backtest</button>
        </form>
      </section>
      <section class="panel span-4">
        <div class="panel-head"><h2>Summary</h2></div>
        <div id="backtest-summary">${backtestSummary(state.lastBacktest)}</div>
      </section>
      <section class="panel span-8">
        <div class="panel-head"><h2>Equity Curve</h2></div>
        <div id="backtest-chart" class="chart-panel"></div>
      </section>
      <section class="panel span-12">
        <div class="panel-head"><h2>Trades</h2></div>
        <div id="backtest-trades">${tradesTable(state.lastBacktest?.trades || [])}</div>
      </section>
    </section>
  `;
  document.querySelector("#backtest-form").addEventListener("submit", runBacktest);
  renderEquityChart(state.lastBacktest?.equity || [], "#backtest-chart");
}

async function renderStockDetail() {
  const symbol = state.selectedSymbol || state.stocks[0]?.symbol || "";
  const options = state.stocks.map((stock) => `<option value="${escapeHtml(stock.symbol)}"${stock.symbol === symbol ? " selected" : ""}>${escapeHtml(stock.symbol)} ${escapeHtml(stock.name || "")}</option>`).join("");
  viewRoot.innerHTML = `
    <section class="page-grid">
      <section class="panel span-12">
        <div class="panel-head">
          <h2>Symbol</h2>
          <div class="toolbar">
            <select id="detail-symbol">${options}</select>
            <button id="load-detail" type="button">Load</button>
          </div>
        </div>
      </section>
      <div id="detail-body" class="span-12">${symbol ? '<section class="panel"><span class="muted">Loading detail...</span></section>' : '<section class="panel"><span class="empty">No stocks available.</span></section>'}</div>
    </section>
  `;
  document.querySelector("#load-detail")?.addEventListener("click", () => {
    state.selectedSymbol = document.querySelector("#detail-symbol").value;
    localStorage.setItem("selectedSymbol", state.selectedSymbol);
    renderStockDetail();
  });
  if (!symbol) return;
  const [stock, bars, indicators, signals] = await Promise.all([
    api(`/api/stocks/${encodeURIComponent(symbol)}`),
    api(`/api/stocks/${encodeURIComponent(symbol)}/bars`),
    api(`/api/stocks/${encodeURIComponent(symbol)}/indicators`),
    api(`/api/stocks/${encodeURIComponent(symbol)}/signals`),
  ]);
  document.querySelector("#detail-body").innerHTML = stockDetail(stock, bars, indicators, signals);
  renderPriceChart(bars, indicators, "#detail-price-chart");
}

function renderSettings() {
  const settings = state.settings || {};
  viewRoot.innerHTML = `
    <section class="page-grid">
      <section class="panel span-6">
        <div class="panel-head"><h2>Database</h2></div>
        <div class="settings-list">
          ${kv("Host", settings.mysql?.host)}
          ${kv("Port", settings.mysql?.port)}
          ${kv("Database", settings.mysql?.database)}
          ${kv("User", settings.mysql?.user)}
          ${kv("Connected", state.health?.database?.connected ? "yes" : "no")}
        </div>
      </section>
      <section class="panel span-6">
        <div class="panel-head"><h2>Data Sources</h2></div>
        <div class="settings-list">
          ${kv("Priority", (settings.data_source_priority || []).join(" -> "))}
          ${kv("Tushare token", settings.tushare_token_configured ? "configured" : "not configured")}
          ${kv("Sync enabled", String(settings.sync_enabled))}
          ${kv("Sync time", settings.sync_time)}
        </div>
      </section>
      <section class="panel span-6">
        <div class="panel-head"><h2>Backtest Defaults</h2></div>
        <div class="settings-list">
          ${kv("Price mode", settings.default_price_mode)}
          ${kv("Fee rate", settings.fee_rate)}
          ${kv("Slippage rate", settings.slippage_rate)}
        </div>
      </section>
    </section>
  `;
}

function metricPanel(label, value, detail, tone) {
  return `
    <section class="panel span-3">
      <span class="metric-label">${escapeHtml(label)}</span>
      <strong class="metric-value">${escapeHtml(value)}</strong>
      <span class="badge ${tone || ""}">${escapeHtml(detail || "ok")}</span>
    </section>
  `;
}

function kv(label, value) {
  return `<div class="kv"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value ?? "")}</strong></div>`;
}

function jobsTable(jobs) {
  if (!jobs.length) return `<p class="empty">No sync jobs yet.</p>`;
  return `
    <div class="table-wrap">
      <table class="data-table compact">
        <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Requested</th><th>Success</th><th>Failed</th><th>Providers</th></tr></thead>
        <tbody>
          ${jobs.map((job) => `
            <tr>
              <td>${job.id}</td>
              <td>${escapeHtml(job.job_type)}</td>
              <td><span class="badge ${job.status === "completed" ? "ok" : job.status === "failed" ? "error" : "warn"}">${escapeHtml(job.status)}</span></td>
              <td>${escapeHtml(job.requested_by)}</td>
              <td>${job.summary?.success ?? 0}</td>
              <td>${job.summary?.failed ?? 0}</td>
              <td>${escapeHtml((job.provider_priority || []).join(", "))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function stocksTable(stocks) {
  if (!stocks.length) return `<p class="empty">No stocks in the local universe.</p>`;
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Symbol</th><th>Name</th><th>Exchange</th><th>Industry</th><th>ST</th><th>Active</th><th>Source</th></tr></thead>
        <tbody>
          ${stocks.map((stock) => `
            <tr>
              <td><button class="link-button stock-link" data-symbol="${escapeHtml(stock.symbol)}">${escapeHtml(stock.symbol)}</button></td>
              <td>${escapeHtml(stock.name)}</td>
              <td>${escapeHtml(stock.exchange)}</td>
              <td>${escapeHtml(stock.industry || "")}</td>
              <td>${stock.is_st ? "yes" : "no"}</td>
              <td>${stock.is_active ? "yes" : "no"}</td>
              <td>${escapeHtml(stock.source)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function screeningTable(rows) {
  if (!rows.length) return `<p class="empty">Run a screening task to populate candidates.</p>`;
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Symbol</th><th>Date</th><th>Close</th><th>EXPMA17</th><th>EXPMA50</th><th>Signal</th><th>Trend</th><th>Quality</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td>${escapeHtml(row.symbol)}</td>
              <td>${escapeHtml(row.trade_date)}</td>
              <td>${fmt(row.close)}</td>
              <td>${fmt(row.expma17)}</td>
              <td>${fmt(row.expma50)}</td>
              <td>${escapeHtml(row.selected_signal || row.signal || "")}</td>
              <td>${escapeHtml(row.trend_state || "")}</td>
              <td>${escapeHtml(row.data_quality || "")}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function backtestSummary(payload) {
  if (!payload) return `<p class="empty">Run a backtest to view summary metrics.</p>`;
  const summary = payload.summary || {};
  return `
    <div class="summary-list">
      ${kv("Total return", pct(summary.total_return))}
      ${kv("Max drawdown", pct(summary.max_drawdown))}
      ${kv("Trade count", summary.trade_count)}
      ${kv("Exposure", pct(summary.exposure))}
      ${kv("Turnover", pct(summary.turnover))}
      ${kv("Final equity", fmt(summary.final_equity))}
    </div>
  `;
}

function tradesTable(trades) {
  if (!trades.length) return `<p class="empty">No trades to display.</p>`;
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Symbol</th><th>Signal Date</th><th>Execution</th><th>Signal</th><th>Action</th><th>Price</th><th>Position</th></tr></thead>
        <tbody>
          ${trades.map((trade) => `
            <tr>
              <td>${escapeHtml(trade.symbol)}</td>
              <td>${escapeHtml(trade.signal_date)}</td>
              <td>${escapeHtml(trade.trade_date || trade.execution_date)}</td>
              <td>${escapeHtml(trade.signal)}</td>
              <td>${escapeHtml(trade.side || trade.action || "")}</td>
              <td>${fmt(trade.price)}</td>
              <td>${pct(trade.target_position ?? trade.position_after)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function stockDetail(stock, bars, indicators, signals) {
  const latestBar = bars[bars.length - 1] || {};
  const signalDates = new Set(signals.map((signal) => String(signal.trade_date)));
  return `
    <div class="page-grid">
      <section class="panel span-3">${kv("Name", stock.name)}${kv("Exchange", stock.exchange)}${kv("Source", stock.source)}</section>
      <section class="panel span-3">${kv("Latest close", fmt(latestBar.close))}${kv("Price mode", latestBar.price_mode)}${kv("Quality", latestBar.data_quality)}</section>
      <section class="panel span-6"><div id="detail-price-chart" class="chart-panel"></div></section>
      <section class="panel span-12">
        <div class="panel-head"><h2>Daily Bars</h2><span class="muted">${bars.length} rows, ${signals.length} signals</span></div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>EXPMA17</th><th>EXPMA50</th><th>Signal</th><th>Quality</th></tr></thead>
            <tbody>
              ${bars.slice(-160).map((bar) => {
                const indicator = indicators.find((item) => String(item.trade_date) === String(bar.trade_date)) || {};
                const signal = signals.find((item) => String(item.trade_date) === String(bar.trade_date)) || {};
                return `
                  <tr>
                    <td>${escapeHtml(bar.trade_date)}</td>
                    <td>${fmt(bar.open)}</td>
                    <td>${fmt(bar.high)}</td>
                    <td>${fmt(bar.low)}</td>
                    <td>${fmt(bar.close)}</td>
                    <td>${fmt(indicator.expma17)}</td>
                    <td>${fmt(indicator.expma50)}</td>
                    <td>${signalDates.has(String(bar.trade_date)) ? escapeHtml(signal.selected_signal || "") : ""}</td>
                    <td>${escapeHtml(bar.data_quality || "")}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `;
}

async function runSyncJob(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const symbols = parseSymbols(form.get("symbols"));
  const message = document.querySelector("#sync-message");
  message.textContent = "Submitting sync job...";
  try {
    const job = await api("/api/sync/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_type: "full_daily_pipeline",
        symbols,
        start_date: form.get("start_date") || null,
        end_date: form.get("end_date") || null,
      }),
    });
    message.textContent = `Job ${job.id} finished with status ${job.status}.`;
    await renderCurrentRoute();
  } catch (error) {
    message.textContent = error.message;
  }
}

async function runScreening(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = {
    trade_date: form.get("trade_date") || null,
    symbols: parseSymbols(form.get("symbols")),
    signal_filter: form.get("signal_filter"),
    price_mode: form.get("price_mode"),
  };
  if (!payload.symbols.length) payload.symbols = null;
  state.lastScreening = await api("/api/screenings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  document.querySelector("#screening-summary").textContent = summaryText(state.lastScreening.summary);
  document.querySelector("#screening-results").innerHTML = screeningTable(state.lastScreening.results || []);
}

async function runBacktest(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const symbols = parseSymbols(form.get("symbols"));
  const payload = {
    symbols: symbols.length ? symbols : null,
    start_date: form.get("start_date"),
    end_date: form.get("end_date"),
    initial_capital: Number(form.get("initial_capital")),
    fee_rate: Number(form.get("fee_rate")),
    slippage_rate: Number(form.get("slippage_rate")),
    price_mode: "forward_adjusted",
    allow_partial_coverage: true,
  };
  state.lastBacktest = await api("/api/backtests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  document.querySelector("#backtest-summary").innerHTML = backtestSummary(state.lastBacktest);
  document.querySelector("#backtest-trades").innerHTML = tradesTable(state.lastBacktest.trades || []);
  renderEquityChart(state.lastBacktest.equity || [], "#backtest-chart");
}

function parseSymbols(value) {
  return String(value || "")
    .split(/[,\s]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function summaryText(summary) {
  if (!summary) return "";
  return Object.entries(summary).map(([key, value]) => `${key}: ${value}`).join(" | ");
}

function bindStockLinks() {
  document.querySelectorAll(".stock-link").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedSymbol = button.dataset.symbol;
      localStorage.setItem("selectedSymbol", state.selectedSymbol);
      window.location.hash = "#/stock-detail";
    });
  });
}

function renderEquityChart(rows, selector) {
  const chart = document.querySelector(selector);
  if (!chart) return;
  chart.innerHTML = "";
  if (!rows.length) {
    chart.innerHTML = `<span class="empty" style="position:absolute;left:12px;top:12px;">No equity data.</span>`;
    return;
  }
  const values = rows.map((row) => Number(row.equity));
  renderBars(chart, values, rows.map((row) => row.trade_date));
}

function renderPriceChart(bars, indicators, selector) {
  const chart = document.querySelector(selector);
  if (!chart) return;
  chart.innerHTML = "";
  const rows = bars.slice(-120);
  if (!rows.length) {
    chart.innerHTML = `<span class="empty" style="position:absolute;left:12px;top:12px;">No bar data.</span>`;
    return;
  }
  renderBars(chart, rows.map((row) => Number(row.close)), rows.map((row) => row.trade_date));
  const byDate = new Map(indicators.map((row) => [String(row.trade_date), row]));
  renderPoints(chart, rows.map((row) => byDate.get(String(row.trade_date))?.expma17), "#176b5b");
  renderPoints(chart, rows.map((row) => byDate.get(String(row.trade_date))?.expma50), "#9a5b00");
}

function renderBars(chart, values, labels) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const width = Math.max(4, Math.floor((chart.clientWidth || 720) / Math.max(values.length, 1)) - 2);
  values.forEach((value, index) => {
    const span = max === min ? 0.5 : (value - min) / (max - min);
    const bar = document.createElement("div");
    bar.className = "spark-bar";
    bar.style.left = `${index * (width + 2)}px`;
    bar.style.width = `${width}px`;
    bar.style.height = `${22 + span * 210}px`;
    bar.title = `${labels[index]}: ${fmt(value)}`;
    chart.appendChild(bar);
  });
}

function renderPoints(chart, values, color) {
  const numeric = values.map((value) => (value === null || value === undefined ? null : Number(value))).filter((value) => Number.isFinite(value));
  if (!numeric.length) return;
  const min = Math.min(...numeric);
  const max = Math.max(...numeric);
  const width = Math.max(4, Math.floor((chart.clientWidth || 720) / Math.max(values.length, 1)));
  values.forEach((value, index) => {
    const number = Number(value);
    if (!Number.isFinite(number)) return;
    const span = max === min ? 0.5 : (number - min) / (max - min);
    const point = document.createElement("div");
    point.className = "line-point";
    point.style.background = color;
    point.style.left = `${index * width}px`;
    point.style.bottom = `${20 + span * 220}px`;
    point.title = fmt(number);
    chart.appendChild(point);
  });
}

window.addEventListener("hashchange", renderCurrentRoute);
document.querySelector("#refresh-view").addEventListener("click", renderCurrentRoute);

if (!window.location.hash) {
  window.location.hash = "#/dashboard";
} else {
  renderCurrentRoute();
}
