import pytest
from fastapi.testclient import TestClient
import importlib

from stock_analyzer_app.api.app import create_app, runtime
from stock_analyzer_app.collector import CollectorService
from stock_analyzer_app.config import AppSettings
from stock_analyzer_app.data_provider.demo_provider import DemoAshareProvider
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available

api_module = importlib.import_module("stock_analyzer_app.api.app")


pytestmark = pytest.mark.skipif(
    not mysql_available(AppSettings.from_env()),
    reason="MySQL test database is not available",
)


def test_api_full_daily_pipeline_uses_persisted_sync_path(monkeypatch):
    runtime.configure_repositories()
    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [DemoAshareProvider()])
    assert isinstance(runtime.analysis_repository, MySqlRepository)
    runtime.analysis_repository.clear_test_data(["DEMO001.SZ"])
    client = TestClient(create_app())

    response = client.post(
        "/api/sync/jobs",
        json={"job_type": "full_daily_pipeline", "start_date": "2024-06-01", "end_date": "2024-08-31"},
    )

    assert response.status_code == 202
    request = response.json()
    assert request["status"] == "pending"

    processed = CollectorService(runtime.sync_repository, runtime.make_daily_pipeline).process_pending_requests(limit=1)

    assert processed == 1
    assert runtime.sync_repository.get_sync_request(request["id"])["status"] == "completed"
    rows = runtime.analysis_repository.latest_screening_rows("2024-12-31", symbols=["DEMO001.SZ"])
    assert rows
    assert rows[0]["symbol"] == "DEMO001.SZ"

    backtest = client.post(
        "/api/backtests",
        json={"symbols": ["DEMO001.SZ"], "start_date": "2024-06-01", "end_date": "2024-12-31"},
    ).json()
    assert backtest["summary"]["trade_count"] >= 1


def test_api_persists_screening_and_backtest_run_history_to_mysql(monkeypatch):
    runtime.configure_repositories()
    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [DemoAshareProvider()])
    client = TestClient(create_app())
    response = client.post(
        "/api/sync/jobs",
        json={"job_type": "full_daily_pipeline", "start_date": "2024-06-01", "end_date": "2024-12-31"},
    )
    assert response.status_code == 202
    CollectorService(runtime.sync_repository, runtime.make_daily_pipeline).process_pending_requests(limit=1)

    screening = client.post(
        "/api/screenings",
        json={"trade_date": "2024-12-31", "symbols": ["DEMO001.SZ"]},
    ).json()
    backtest = client.post(
        "/api/backtests",
        json={"symbols": ["DEMO001.SZ"], "start_date": "2024-06-01", "end_date": "2024-12-31"},
    ).json()

    persisted_screening = runtime.analysis_repository.get_screening_run(int(screening["task_id"]))
    persisted_screening_results = runtime.analysis_repository.get_screening_results(int(screening["task_id"]))
    persisted_backtest = runtime.analysis_repository.get_backtest_run(int(backtest["task_id"]))

    assert persisted_screening["status"] == "completed"
    assert persisted_screening["universe"] == ["DEMO001.SZ"]
    assert persisted_screening_results
    assert persisted_backtest["symbols"] == ["DEMO001.SZ"]
    assert persisted_backtest["summary"]["trade_count"] >= 1
    assert persisted_backtest["trades"]


def test_api_full_daily_pipeline_uses_runtime_provider_chain(monkeypatch):
    runtime.configure_repositories()
    runtime.analysis_repository.clear_test_data(["CHAIN001.SZ"])

    class ChainProvider:
        name = "chain"

        def fetch_stock_universe(self):
            return [{"symbol": "CHAIN001.SZ", "exchange": "SZ", "name": "Chain One", "source": self.name}]

        def fetch_trading_calendar(self, exchange, start_date, end_date):
            return []

        def fetch_daily_bars(self, symbol, start_date, end_date):
            return [
                {
                    "symbol": symbol,
                    "trade_date": "2024-01-02",
                    "open": 10,
                    "high": 11,
                    "low": 9,
                    "close": 10,
                    "volume": 100,
                    "amount": 1000,
                    "source": self.name,
                    "is_adjusted": False,
                }
            ]

        def fetch_adjustment_factors(self, symbol, start_date, end_date):
            return [{"symbol": symbol, "trade_date": "2024-01-02", "adj_factor": 1.0, "source": self.name}]

        def fetch_stock_status(self, symbols, trade_date):
            return []

    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [ChainProvider()])
    client = TestClient(create_app())

    response = client.post(
        "/api/sync/jobs",
        json={"job_type": "full_daily_pipeline", "symbols": ["CHAIN001.SZ"], "start_date": "2024-01-01", "end_date": "2024-01-31"},
    )

    assert response.status_code == 202
    request = response.json()
    assert request["scope"]["symbols"] == ["CHAIN001.SZ"]
    CollectorService(runtime.sync_repository, runtime.make_daily_pipeline).process_pending_requests(limit=1)
    rows = runtime.analysis_repository.latest_screening_rows("2024-01-31", symbols=["CHAIN001.SZ"])
    assert rows[0]["source"] == "chain"


def test_runtime_scheduler_pipeline_uses_runtime_provider_chain(monkeypatch):
    runtime.configure_repositories()

    class ChainProvider:
        name = "chain"

    monkeypatch.setattr(runtime, "build_sync_providers", lambda: [ChainProvider()])

    pipeline = runtime.make_daily_pipeline()

    assert [provider.name for provider in pipeline.providers] == ["chain"]
