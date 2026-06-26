from fastapi.testclient import TestClient
import pytest

from stock_analyzer_app.api import app
from stock_analyzer_app.api.app import runtime
from stock_analyzer_app.storage.repositories import InMemoryAnalysisRepository
from stock_analyzer_app.sync import InMemorySyncRepository, SyncService


client = TestClient(app)


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
