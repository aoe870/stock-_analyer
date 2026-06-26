from pathlib import Path


PUBLIC_DIR = Path("public")


def test_frontend_workspace_defines_required_navigation_pages():
    html = (PUBLIC_DIR / "index.html").read_text(encoding="utf-8")

    required_routes = [
        "#/dashboard",
        "#/sync",
        "#/stocks",
        "#/screening",
        "#/backtests",
        "#/stock-detail",
        "#/settings",
    ]

    for route in required_routes:
        assert f'href="{route}"' in html
    assert 'id="app-shell"' in html
    assert 'id="view-root"' in html
    assert 'id="screen-body"' not in html
    assert 'id="equity-chart"' not in html


def test_frontend_workspace_javascript_has_route_renderers_and_api_bindings():
    js = (PUBLIC_DIR / "app.js").read_text(encoding="utf-8")

    for renderer in [
        "renderDashboard",
        "renderSyncCenter",
        "renderStocks",
        "renderScreening",
        "renderBacktests",
        "renderStockDetail",
        "renderSettings",
    ]:
        assert f"function {renderer}" in js

    for endpoint in [
        "/api/health",
        "/api/sync/jobs",
        "/api/sync/coverage",
        "/api/stocks",
        "/api/screenings",
        "/api/backtests",
        "/api/settings",
    ]:
        assert endpoint in js


def test_frontend_workspace_css_uses_operational_layout_not_demo_panels():
    css = (PUBLIC_DIR / "styles.css").read_text(encoding="utf-8")

    assert ".workspace" in css
    assert ".sidebar" in css
    assert ".page-grid" in css
    assert ".data-table" in css
    assert ".chart-panel" in css
    assert ".topbar" in css
