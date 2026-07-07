from fastapi.testclient import TestClient
import pytest
from datetime import date
from importlib import import_module

from stock_analyzer_app.api import app
from stock_analyzer_app.api.app import runtime
from stock_analyzer_app.storage.repositories import InMemoryAnalysisRepository
from stock_analyzer_app.sync import InMemorySyncRepository, SyncService


client = TestClient(app)
api_app_module = import_module("stock_analyzer_app.api.app")


@pytest.fixture(autouse=True)
def reset_runtime_to_in_memory():
    runtime.analysis_repository = InMemoryAnalysisRepository()
    runtime.sync_repository = InMemorySyncRepository()
    runtime.sync_service = SyncService(runtime.sync_repository, providers=[])


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["api"] == "ok"
    assert {"connected", "configured"} <= set(payload["database"])
    assert "scheduler" in payload
    assert "latest_successful_sync_job" in payload


def test_sample_endpoint_returns_symbols_and_bars():
    response = client.get("/api/sample")

    assert response.status_code == 200
    payload = response.json()
    assert "symbols" in payload
    assert "SAMPLE1" in payload["symbols"]
    assert payload["symbols"]["SAMPLE1"][0]["symbol"] == "SAMPLE1"


def test_sync_job_endpoints_create_and_report_status():
    response = client.post(
        "/api/sync/jobs",
        json={"job_type": "sync_daily_bars", "symbols": ["SAMPLE1"], "start_date": "2024-01-01", "end_date": "2024-01-02"},
    )

    assert response.status_code == 200
    job = response.json()
    assert job["task_id"] == str(job["id"])
    assert job["job_type"] == "sync_daily_bars"

    status = client.get(f"/api/sync/jobs/{job['id']}").json()
    items = client.get(f"/api/sync/jobs/{job['id']}/items").json()
    coverage = client.get("/api/sync/coverage").json()

    assert status["id"] == job["id"]
    assert isinstance(items["items"], list)
    assert "analysis_daily_bars" in coverage


def test_sync_readiness_endpoint_reports_latest_analysis_coverage():
    response = client.get("/api/sync/readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["latest_trade_date"] == "2024-01-13"
    assert payload["expected_symbols"] == len(runtime.analysis_repository.list_stocks())
    assert payload["updated_symbols"] == len(runtime.analysis_repository.list_stocks())
    assert payload["missing_symbols"] == []
    assert payload["ready_for_analysis"] is True


def test_full_pipeline_request_returns_existing_running_job_without_creating_duplicate(monkeypatch):
    existing = runtime.sync_repository.create_job("full_daily_pipeline", "manual", ["fake"])
    runtime.sync_repository.mark_job_running(existing["id"])
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: pytest.fail("duplicate pipeline should not start"))

    response = client.post(
        "/api/sync/jobs",
        json={"job_type": "full_daily_pipeline", "start_date": "2024-01-01", "end_date": "2024-01-02"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == existing["id"]
    assert payload["status"] == "running"
    assert len(runtime.sync_repository.list_jobs()) == 1


def test_retry_sync_job_runs_failed_items_only(monkeypatch):
    source = runtime.sync_repository.create_job("full_daily_pipeline", "manual", ["fake"])
    runtime.sync_repository.finish_job(source["id"], "completed_with_errors", {"success": 1, "failed": 2})
    runtime.sync_repository.add_item(
        source["id"],
        {
            "symbol": "AAA.SZ",
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "status": "success",
            "provider": "fake",
            "attempt_count": 1,
        },
    )
    runtime.sync_repository.add_item(
        source["id"],
        {
            "symbol": "BBB.SZ",
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "status": "failed",
            "provider": None,
            "attempt_count": 1,
            "error_message": "temporary provider failure",
        },
    )
    runtime.sync_repository.add_item(
        source["id"],
        {
            "symbol": "CCC.SZ",
            "date_start": "2024-01-15",
            "date_end": "2024-02-15",
            "status": "failed",
            "provider": None,
            "attempt_count": 1,
            "error_message": "temporary provider failure",
        },
    )
    captured = {}

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            captured.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "requested_by": requested_by,
                    "symbols": symbols,
                }
            )
            return {
                "id": 99,
                "job_type": "full_daily_pipeline",
                "status": "completed",
                "requested_by": requested_by,
                "summary": {"success": len(symbols), "failed": 0},
            }

    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    response = client.post(f"/api/sync/jobs/{source['id']}/retry")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == "99"
    assert payload["retried_from_job_id"] == source["id"]
    assert captured == {
        "start_date": "2024-01-01",
        "end_date": "2024-02-15",
        "requested_by": f"retry:{source['id']}",
        "symbols": ["BBB.SZ", "CCC.SZ"],
    }


def test_retry_sync_job_rejects_jobs_without_failed_items(monkeypatch):
    source = runtime.sync_repository.create_job("full_daily_pipeline", "manual", ["fake"])
    runtime.sync_repository.finish_job(source["id"], "completed", {"success": 1, "failed": 0})
    runtime.sync_repository.add_item(
        source["id"],
        {
            "symbol": "AAA.SZ",
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "status": "success",
            "provider": "fake",
            "attempt_count": 1,
        },
    )
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: pytest.fail("retry pipeline should not start"))

    response = client.post(f"/api/sync/jobs/{source['id']}/retry")

    assert response.status_code == 409
    assert response.json()["detail"] == "sync job has no failed items to retry"


def test_v2_sync_job_types_dispatch_to_separate_pipelines(monkeypatch):
    captured = []

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            captured.append(("fundamental", requested_by, symbols))
            return {"id": 11, "job_type": "fundamental_refresh_pipeline", "status": "completed", "summary": {"success": 1}}

        def run_market_structure_pipeline(self, requested_by):
            captured.append(("market", requested_by, None))
            return {"id": 12, "job_type": "market_structure_pipeline", "status": "completed", "summary": {"success": 1}}

    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    fundamental = client.post("/api/sync/jobs", json={"job_type": "fundamental_refresh_pipeline", "symbols": ["AAA.SZ"]}).json()
    market = client.post("/api/sync/jobs", json={"job_type": "market_structure_pipeline"}).json()

    assert fundamental["task_id"] == "11"
    assert market["task_id"] == "12"
    assert captured == [
        ("fundamental", "manual", ["AAA.SZ"]),
        ("market", "manual", None),
    ]


def test_stock_data_endpoints_return_local_analysis_rows():
    stocks = client.get("/api/stocks").json()
    assert stocks["stocks"]
    symbol = stocks["stocks"][0]["symbol"]

    detail = client.get(f"/api/stocks/{symbol}").json()
    bars = client.get(f"/api/stocks/{symbol}/bars").json()
    indicators = client.get(f"/api/stocks/{symbol}/indicators").json()
    signals = client.get(f"/api/stocks/{symbol}/signals").json()

    assert detail["symbol"] == symbol
    assert bars
    assert indicators
    assert isinstance(signals, list)


def test_market_dashboard_endpoint_returns_stable_shape():
    response = client.get("/api/market/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert {"indexes", "sectors", "rankings", "breadth", "freshness", "data_source_status"} <= set(payload)
    assert isinstance(payload["rankings"]["gainers"], list)
    assert payload["freshness"]["latest_trade_date"] == "2024-01-13"


def helper_old_market_dashboard_enriches_with_miana_sort_rankings(monkeypatch):
    class Provider:
        name = "miana"

        def fetch_stock_rankings(self, sort, order):
            rows = {
                ("changeRate", "DESC"): [{"symbol": "AAA.SZ", "name": "Alpha", "change_rate": 0.03, "amount": 100}],
                ("changeRate", "ASC"): [{"symbol": "BBB.SZ", "name": "Beta", "change_rate": -0.02, "amount": 80}],
                ("amount", "DESC"): [{"symbol": "CCC.SZ", "name": "Cash", "change_rate": 0.01, "amount": 1000}],
            }
            return rows[(sort, order)]

        def fetch_index_rankings(self, sort, order):
            return [{"index_code": "sh000001", "name": "上证指数", "price": 3200, "change_rate": 0.005}]

        def fetch_sector_rankings(self, sort, order):
            return [{"sector_code": "BK001", "name": "Bank", "price": 1000, "change_rate": 0.02}]

    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [Provider()])

    payload = client.get("/api/market/dashboard").json()

    assert payload["rankings"]["gainers"][0]["symbol"] == "AAA.SZ"
    assert payload["rankings"]["losers"][0]["symbol"] == "BBB.SZ"
    assert payload["rankings"]["amount"][0]["symbol"] == "CCC.SZ"
    assert payload["indexes"][0]["index_code"] == "sh000001"
    assert payload["sectors"][0]["sector_code"] == "BK001"
    assert payload["data_source_status"]["provider"] == "miana"
    assert payload["data_source_status"]["stock_rankings"] == "ok"
    assert payload["data_source_status"]["sector_rankings"] == "ok"


def helper_old_market_dashboard_uses_short_ttl_cache_for_live_miana_rankings(monkeypatch):
    calls = {"stock": 0, "index": 0, "sector": 0}

    class Provider:
        name = "miana"

        def fetch_stock_rankings(self, sort, order):
            calls["stock"] += 1
            return [{"symbol": "AAA.SZ", "name": "Alpha", "change_rate": 0.03, "amount": 100}]

        def fetch_index_rankings(self, sort, order):
            calls["index"] += 1
            return [{"index_code": "sh000001", "name": "Index", "price": 3200, "change_rate": 0.005}]

        def fetch_sector_rankings(self, sort, order):
            calls["sector"] += 1
            return [{"sector_code": "BK001", "name": "Bank", "price": 1000, "change_rate": 0.02}]

    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [Provider()])

    first = client.get("/api/market/dashboard").json()
    second = client.get("/api/market/dashboard").json()

    assert first["rankings"]["gainers"][0]["symbol"] == second["rankings"]["gainers"][0]["symbol"]
    assert calls == {"stock": 3, "index": 1, "sector": 1}


def test_market_dashboard_does_not_start_sync_when_yesterday_data_exists(monkeypatch):
    class FixedDate:
        @classmethod
        def today(cls):
            return date(2024, 1, 14)

    monkeypatch.setattr(api_app_module, "date", FixedDate)
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: pytest.fail("dashboard should use existing local data"))

    response = client.get("/api/market/dashboard")

    assert response.status_code == 200
    assert response.json()["freshness"]["latest_trade_date"] == "2024-01-13"


def test_market_dashboard_starts_yesterday_sync_when_local_data_is_missing(monkeypatch):
    class FixedDate:
        @classmethod
        def today(cls):
            return date(2026, 7, 6)

    captured = {}

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            captured.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "requested_by": requested_by,
                    "symbols": symbols,
                }
            )
            return {"id": 91, "job_type": "full_daily_pipeline", "status": "completed", "summary": {"success": 1, "failed": 0}}

    monkeypatch.setattr(api_app_module, "date", FixedDate)
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    response = client.get("/api/market/dashboard")

    assert response.status_code == 200
    assert captured == {
        "start_date": "2026-07-05",
        "end_date": "2026-07-05",
        "requested_by": "dashboard:auto",
        "symbols": None,
    }


def test_market_dashboard_does_not_fetch_live_miana_rankings_on_click(monkeypatch):
    class Provider:
        name = "miana"

        def fetch_stock_rankings(self, sort, order):
            raise AssertionError("dashboard should not fetch live stock rankings")

        def fetch_index_rankings(self, sort, order):
            raise AssertionError("dashboard should not fetch live index rankings")

        def fetch_sector_rankings(self, sort, order):
            raise AssertionError("dashboard should not fetch live sector rankings")

    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [Provider()])

    payload = client.get("/api/market/dashboard").json()

    assert payload["data_source_status"]["provider"] == "local"
    assert payload["data_source_status"]["stock_rankings"] == "local"


def test_stock_research_endpoints_return_stable_shapes():
    symbol = client.get("/api/stocks").json()["stocks"][0]["symbol"]

    overview = client.get(f"/api/stocks/{symbol}/overview").json()
    financials = client.get(f"/api/stocks/{symbol}/financials").json()
    capital_flow = client.get(f"/api/stocks/{symbol}/capital-flow").json()

    assert overview["stock"]["symbol"] == symbol
    assert "latest_bar" in overview
    assert {"share_capital", "corporate_actions", "holders", "officers", "officer_rewards"} <= set(overview)
    assert "enterprise_modules" in overview["data_quality"]
    assert {"income", "balance", "cashflow", "summary"} <= set(financials)
    assert financials["summary"] == {"latest_report_date": None, "income_rows": 0, "balance_rows": 0, "cashflow_rows": 0}
    assert capital_flow == {"symbol": symbol, "rows": [], "summary": {"latest_trade_date": None, "rows": 0}}


def test_stock_overview_does_not_auto_refresh_missing_enterprise_research_by_default(monkeypatch):
    captured = {}

    class Repository:
        synced = False

        def stock_research_snapshot(self, symbol):
            base = {
                "stock": {"symbol": symbol},
                "latest_bar": None,
                "company_profile": None,
                "share_capital": [],
                "corporate_actions": [],
                "holders": [],
                "officer_rewards": [],
                "data_quality": {
                    "has_bars": False,
                    "has_research_data": self.synced,
                    "enterprise_modules": {
                        "company_profile": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "share_capital": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "corporate_actions": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "holders": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "officers": {"rows": 1 if self.synced else 0, "status": "synced" if self.synced else "missing", "newest_date": None, "provider": "miana" if self.synced else None},
                        "officer_rewards": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "capital_flow": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    },
                },
            }
            base["officers"] = [{"officer_name": "Officer A", "title": "董事长"}] if self.synced else []
            return base

    repository = Repository()

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            captured["requested_by"] = requested_by
            captured["symbols"] = symbols
            repository.synced = True
            return {"id": 88, "status": "completed", "summary": {"success": 1, "metadata_errors": 0}}

    runtime.analysis_repository = repository
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    response = client.get("/api/stocks/AAA.SZ/overview")

    assert response.status_code == 200
    assert captured == {}
    assert response.json()["officers"] == []


def test_stock_overview_refresh_missing_triggers_enterprise_research_once(monkeypatch):
    captured = {}

    class Repository:
        synced = False

        def stock_research_snapshot(self, symbol):
            base = {
                "stock": {"symbol": symbol},
                "latest_bar": None,
                "company_profile": None,
                "share_capital": [],
                "corporate_actions": [],
                "holders": [],
                "officer_rewards": [],
                "data_quality": {
                    "has_bars": False,
                    "has_research_data": self.synced,
                    "enterprise_modules": {
                        "company_profile": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "share_capital": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "corporate_actions": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "holders": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "officers": {"rows": 1 if self.synced else 0, "status": "synced" if self.synced else "missing", "newest_date": None, "provider": "miana" if self.synced else None},
                        "officer_rewards": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                        "capital_flow": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    },
                },
            }
            base["officers"] = [{"officer_name": "Officer A", "title": "董事长"}] if self.synced else []
            return base

    repository = Repository()

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            captured["requested_by"] = requested_by
            captured["symbols"] = symbols
            repository.synced = True
            return {"id": 88, "status": "completed", "summary": {"success": 1, "metadata_errors": 0}}

    runtime.analysis_repository = repository
    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    response = client.get("/api/stocks/AAA.SZ/overview?refresh_missing=true")

    assert response.status_code == 200
    assert captured == {"requested_by": "overview:auto:AAA.SZ", "symbols": ["AAA.SZ"]}
    assert response.json()["officers"] == [{"officer_name": "Officer A", "title": "董事长"}]


def test_data_center_coverage_endpoint_returns_v2_sections():
    response = client.get("/api/data-center/coverage")

    assert response.status_code == 200
    payload = response.json()
    assert {"core", "research", "market_structure", "sync"} <= set(payload)
    assert "analysis_daily_bars" in payload["core"]
    assert "financial_statements" in payload["research"]
    for key in ["corporate_actions", "share_capital", "holders", "officers", "officer_rewards"]:
        assert key in payload["research"]


def test_stock_bars_refresh_triggers_single_symbol_detail_sync(monkeypatch):
    captured = {}

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            captured.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "requested_by": requested_by,
                    "symbols": symbols,
                }
            )
            return {"id": 77, "status": "completed", "summary": {"success": 1, "failed": 0}}

    monkeypatch.setattr(runtime, "make_daily_pipeline", lambda: Pipeline())

    response = client.get("/api/stocks/SAMPLE1/bars?refresh=true")

    assert response.status_code == 200
    assert captured["requested_by"] == "detail:SAMPLE1"
    assert captured["symbols"] == ["SAMPLE1"]
    assert captured["start_date"] == "2024-01-14"
    assert captured["end_date"] == date.today().isoformat()


def test_screen_endpoint_returns_latest_rows():
    response = client.post("/api/screen", json={"signal_filter": "all"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["success"] >= 1
    assert payload["results"]
    assert {"symbol", "trade_date", "close", "expma17", "expma50", "trend_state", "raw_flags"} <= set(
        payload["results"][0]
    )


def test_screening_task_endpoints_return_results():
    response = client.post("/api/screenings", json={"trade_date": "2024-01-10", "symbols": ["SAMPLE1"]})

    assert response.status_code == 200
    task = response.json()
    assert task["status"] == "completed"
    assert client.get(f"/api/screenings/{task['task_id']}").json()["status"] == "completed"
    assert "results" in client.get(f"/api/screenings/{task['task_id']}/results").json()


def test_backtest_endpoint_returns_summary_trades_and_equity():
    symbol = client.get("/api/stocks").json()["stocks"][0]["symbol"]
    response = client.post(
        "/api/backtest",
        json={
            "symbols": [symbol],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 50000,
            "fee_rate": 0,
            "slippage_rate": 0,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["initial_capital"] == 50000
    assert "total_return" in payload["summary"]
    assert payload["equity"]
    assert isinstance(payload["trades"], list)


def test_backtest_task_and_run_history_endpoints():
    symbol = client.get("/api/stocks").json()["stocks"][0]["symbol"]
    response = client.post(
        "/api/backtests",
        json={
            "symbols": [symbol],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "allow_partial_coverage": False,
            "initial_capital": 50000,
        },
    )

    assert response.status_code == 200
    task = response.json()
    assert task["status"] == "completed"
    assert client.get(f"/api/backtests/{task['task_id']}").json()["status"] == "completed"
    assert isinstance(client.get("/api/backtests/runs").json()["runs"], list)
