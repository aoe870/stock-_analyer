import os

import pytest

from stock_analyzer_app.config.settings import AppSettings
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available


pytestmark = pytest.mark.skipif(
    not mysql_available(AppSettings.from_env()),
    reason="MySQL test database is not available",
)


def repository():
    repo = MySqlRepository(AppSettings.from_env())
    repo.clear_test_data(["TST001.SZ", "TST002.SZ"])
    return repo


def test_mysql_repository_upserts_market_and_analysis_rows_idempotently():
    repo = repository()
    repo.upsert_stocks(
        [
            {
                "symbol": "TST001.SZ",
                "exchange": "SZ",
                "name": "Test One",
                "industry": "Testing",
                "list_date": "2024-01-01",
                "delist_date": None,
                "is_active": True,
                "is_st": False,
                "source": "unit",
            }
        ]
    )
    repo.upsert_daily_bars(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "open": 10,
                "high": 12,
                "low": 9,
                "close": 11,
                "volume": 1000,
                "amount": 11000,
                "source": "unit",
                "is_adjusted": False,
            }
        ]
    )
    repo.upsert_adjustment_factors(
        [{"symbol": "TST001.SZ", "trade_date": "2024-01-02", "adj_factor": 2.0, "source": "unit"}]
    )
    repo.upsert_analysis_daily_bars(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "open": 20,
                "high": 24,
                "low": 18,
                "close": 22,
                "volume": 1000,
                "amount": 11000,
                "adj_factor": 2.0,
                "price_mode": "forward_adjusted",
                "source": "unit",
                "data_quality": "ok",
            }
        ]
    )
    repo.upsert_analysis_daily_bars(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "open": 20,
                "high": 24,
                "low": 18,
                "close": 22,
                "volume": 1000,
                "amount": 11000,
                "adj_factor": 2.0,
                "price_mode": "forward_adjusted",
                "source": "unit",
                "data_quality": "ok",
            }
        ]
    )

    bars = repo.analysis_bars_with_signals(["TST001.SZ"], "2024-01-01", "2024-01-03")

    assert len(bars["TST001.SZ"]) == 1
    assert bars["TST001.SZ"][0]["close"] == 22.0
    assert repo.coverage()["analysis_daily_bars"]["rows"] >= 1


def test_mysql_repository_materialized_indicators_and_signals_feed_screening_rows():
    repo = repository()
    repo.upsert_stocks(
        [{"symbol": "TST001.SZ", "exchange": "SZ", "name": "Test One", "source": "unit"}]
    )
    repo.upsert_analysis_daily_bars(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "open": 10,
                "high": 12,
                "low": 9,
                "close": 11,
                "volume": 1000,
                "amount": 11000,
                "adj_factor": 1.0,
                "price_mode": "forward_adjusted",
                "source": "unit",
                "data_quality": "ok",
            }
        ]
    )
    repo.upsert_daily_indicators(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "strategy_key": "expma_17_50",
                "expma17": 10.5,
                "expma50": 9.5,
                "cross_price": None,
                "cross_in_kline": False,
                "warmup_ready": True,
            }
        ]
    )
    repo.upsert_strategy_signals(
        [
            {
                "symbol": "TST001.SZ",
                "trade_date": "2024-01-02",
                "strategy_key": "expma_17_50",
                "selected_signal": "BUY",
                "raw_flags_json": '{"buy": true}',
                "trend_state": "above_expma17_expma50",
            }
        ]
    )

    rows = repo.latest_screening_rows("2024-01-02", symbols=["TST001.SZ"])

    assert rows[0]["symbol"] == "TST001.SZ"
    assert rows[0]["selected_signal"] == "BUY"
    assert rows[0]["raw_flags"] == {"buy": True}
    assert rows[0]["expma17"] == 10.5


def test_mysql_repository_persists_sync_jobs_and_items():
    repo = repository()

    job = repo.create_job("sync_daily_bars", "manual", ["unit"])
    repo.mark_job_running(job["id"])
    repo.add_item(job["id"], {"symbol": "TST001.SZ", "status": "success", "provider": "unit", "attempt_count": 1})
    finished = repo.finish_job(job["id"], "completed", {"success": 1, "failed": 0})

    assert finished["status"] == "completed"
    assert repo.get_job(job["id"])["summary"]["success"] == 1
    assert repo.get_job_items(job["id"])[0]["symbol"] == "TST001.SZ"


def test_mysql_repository_upserts_trading_calendar_and_stock_status():
    repo = repository()
    repo.upsert_stocks(
        [
            {"symbol": "TST001.SZ", "exchange": "SZ", "name": "Test One", "source": "unit"},
            {"symbol": "TST002.SZ", "exchange": "SZ", "name": "Test Two", "source": "unit"},
        ]
    )

    repo.upsert_trading_calendar(
        [
            {"exchange": "SZ", "trade_date": "2024-01-02", "is_open": True},
            {"exchange": "SZ", "trade_date": "2024-01-03", "is_open": False},
        ]
    )
    repo.upsert_stock_status(
        [
            {"symbol": "TST001.SZ", "trade_date": "2024-01-02", "is_st": True, "is_suspended": False},
            {"symbol": "TST002.SZ", "trade_date": "2024-01-02", "is_st": False, "is_suspended": True},
        ]
    )

    calendar = repo.trading_calendar("SZ", "2024-01-01", "2024-01-03")
    statuses = repo.stock_status(["TST001.SZ", "TST002.SZ"], "2024-01-02")

    assert calendar == [
        {"exchange": "SZ", "trade_date": "2024-01-02", "is_open": True},
        {"exchange": "SZ", "trade_date": "2024-01-03", "is_open": False},
    ]
    assert statuses == [
        {"symbol": "TST001.SZ", "trade_date": "2024-01-02", "is_st": True, "is_suspended": False},
        {"symbol": "TST002.SZ", "trade_date": "2024-01-02", "is_st": False, "is_suspended": True},
    ]
