from pathlib import Path


PUBLIC_DIR = Path("public")


def read_public(name: str) -> str:
    return (PUBLIC_DIR / name).read_text(encoding="utf-8")


def test_frontend_uses_local_vue_element_plus_and_echarts_assets():
    html = read_public("index.html")

    for asset in [
        "/static/vendor/vue.global.prod.js",
        "/static/vendor/element-plus.css",
        "/static/vendor/element-plus.full.min.js",
        "/static/vendor/echarts.min.js",
    ]:
        assert asset in html

    for filename in [
        "vue.global.prod.js",
        "element-plus.css",
        "element-plus.full.min.js",
        "echarts.min.js",
    ]:
        assert (PUBLIC_DIR / "vendor" / filename).exists()


def test_frontend_shell_is_framework_app_with_stockinsight_navigation():
    html = read_public("index.html")
    js = read_public("app.js")

    for text in ["StockInsight", "行情中心", "自选观察", "选股器", "策略回测", "数据同步", "系统设置"]:
        assert text in html + js

    assert 'id="app"' in html
    assert "v-cloak" in html
    assert "<el-container" not in html
    assert "template:" in js
    assert "<el-container" in js
    assert "<el-menu" in js
    assert "<el-main" in js
    assert 'id="detail-drawer"' not in html


def test_frontend_javascript_is_vue_app_with_analysis_workflows():
    js = read_public("app.js")

    for symbol in ["Vue.createApp", "ElementPlus", "echarts.init", "app.mount(\"#app\")"]:
        assert symbol in js

    for endpoint in [
        "/api/health",
        "/api/settings",
        "/api/sync/coverage",
        "/api/sync/readiness",
        "/api/sync/jobs",
        "/api/stocks",
        "/api/screenings",
        "/api/backtests",
    ]:
        assert endpoint in js

    for behavior in [
        "navigateToStock",
        "renderKlineChart",
        "aggregateKlineRows",
        "runScreener",
        "runBacktest",
        "runManualSync",
        "retryJob",
        "toggleSidebar",
    ]:
        assert f"{behavior}(" in js

    assert "klinePeriod" in js


def test_frontend_v2_uses_market_stock_research_and_data_center_apis():
    js = read_public("app.js")

    for endpoint in [
        "/api/market/dashboard",
        "/api/stocks/${symbol}/overview",
        "/api/stocks/${symbol}/financials",
        "/api/stocks/${symbol}/capital-flow",
        "/api/data-center/coverage",
    ]:
        assert endpoint in js

    for state_name in [
        "marketDashboard",
        "stockOverview",
        "stockFinancials",
        "stockCapitalFlow",
        "dataCenterCoverage",
    ]:
        assert state_name in js

    for copy in ["公司资料", "分红与股本", "主营业务", "股本历史", "涨幅榜", "跌幅榜", "成交额榜", "data_source_status"]:
        assert copy in js


def test_frontend_stock_detail_exposes_enterprise_research_tabs():
    js = read_public("app.js")

    for label in ["财务三表", "企业资料", "股东高管", "分红股本", "资金流", "数据状态", "十大股东", "董监高", "薪酬持股"]:
        assert label in js

    for marker in [
        "stockEnterpriseActiveTab",
        "stockOverview.officer_rewards",
        "stockOverview.data_quality?.enterprise_modules",
        "stockFinancials.summary",
        "stockCapitalFlow.summary",
        "enterpriseModuleStatus",
        "officer_rewards",
        "corporate_actions",
        "share_capital",
    ]:
        assert marker in js


def test_frontend_company_profile_shows_miana_v1_company_info_fields():
    js = read_public("app.js")

    for label in ["机构名称", "成立日期", "注册资本", "员工数量", "会计师事务所", "法律顾问", "公司简介"]:
        assert label in js

    for marker in [
        "stockOverview.company_profile.company_name",
        "stockOverview.company_profile.found_date",
        "stockOverview.company_profile.registered_capital",
        "stockOverview.company_profile.employee_count",
        "stockOverview.company_profile.accounting_firm",
        "stockOverview.company_profile.legal_adviser",
        "stockOverview.company_profile.company_profile",
    ]:
        assert marker in js


def test_frontend_officer_table_uses_miana_title_field_for_position():
    js = read_public("app.js")

    assert '<el-table-column prop="title" label="职务"' in js


def test_frontend_officer_reward_table_uses_backend_title_and_hold_volume_fields():
    js = read_public("app.js")

    assert '<el-table-column prop="title" label="职务" />' in js
    assert '<el-table-column prop="hold_volume" label="持股数"' in js


def test_frontend_lazy_loads_enterprise_people_tab_with_refresh_missing_flag():
    js = read_public("app.js")

    assert '@tab-change="handleEnterpriseTabChange"' in js
    assert "async handleEnterpriseTabChange(tabName)" in js
    assert 'if (tabName !== "people") return;' in js
    assert 'this.loadStockOverview(symbol, true)' in js
    assert 'const query = refreshMissing ? "?refresh_missing=true" : "";' in js


def test_frontend_reuses_recent_market_dashboard_payload_between_route_switches():
    js = read_public("app.js")

    for marker in [
        "marketDashboardCacheTtlMs",
        "marketDashboardLoadedAt",
        "loadMarketDashboard(force = false)",
        "Date.now() - this.marketDashboardLoadedAt < this.marketDashboardCacheTtlMs",
        "await this.loadRoute(true)",
    ]:
        assert marker in js


def test_stock_detail_kline_period_selector_is_wired_to_chart_aggregation():
    js = read_public("app.js")

    assert 'v-model="klinePeriod"' in js
    assert '@change="renderKlineChart"' in js
    assert 'label="day">日线' in js
    assert 'label="week">周线' in js
    assert 'label="month">月线' in js
    assert 'aggregateKlineRows(this.stockBars, this.klinePeriod)' in js
    assert 'period === "week"' in js
    assert 'period === "month"' in js


def test_stock_detail_kline_chart_keeps_full_history_available_for_zooming():
    js = read_public("app.js")
    render_start = js.index("    renderKlineChart()")
    render_end = js.index("renderEquityChart()", render_start)
    render_code = js[render_start:render_end]

    assert "aggregateKlineRows(this.stockBars, this.klinePeriod).slice(-160)" not in render_code
    assert "aggregateKlineRows(this.stockBars, this.klinePeriod)" in render_code
    assert "this.zoomStartForRows(rows)" in render_code


def test_frontend_copy_is_readable_and_visual_stock_platform_oriented():
    text = read_public("index.html") + read_public("app.js")

    for copy in ["市场概览", "股票搜索", "K线图", "EXPMA17", "筛选条件", "回测配置", "最大回撤", "失败重试"]:
        assert copy in text

    mojibake_markers = ["浠", "鏌", "鍚", "绛", "鑲", "€"]
    for marker in mojibake_markers:
        assert marker not in text


def test_frontend_css_has_polished_framework_overrides():
    css = read_public("styles.css")

    for selector in [
        ".app-shell",
        ".brand-panel",
        ".hero-market",
        ".glass-card",
        ".stock-detail-grid",
        ".kline-chart",
        ".metric-strip",
        ".watch-chip",
        ".el-card",
        ".el-table",
    ]:
        assert selector in css

    assert "border-radius: 8px" in css
