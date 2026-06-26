import pytest
from datetime import date, timedelta

from stock_analyzer_app.config.settings import AppSettings
from stock_analyzer_app.data_provider.base import StockDataProvider
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available
from stock_analyzer_app.sync.pipeline import DailySyncPipeline


pytestmark = pytest.mark.skipif(
    not mysql_available(AppSettings.from_env()),
    reason="MySQL test database is not available",
)


class PipelineProvider(StockDataProvider):
    name = "unit"

    def fetch_stock_universe(self):
        return [{"symbol": "TST002.SZ", "exchange": "SZ", "name": "Pipeline Two", "source": self.name}]

    def fetch_trading_calendar(self, exchange, start_date, end_date):
        return [{"exchange": exchange, "trade_date": start_date, "is_open": True}]

    def fetch_daily_bars(self, symbol, start_date, end_date):
        closes = [10] * 30 + [9] * 20 + [15] * 20 + [13]
        start = date(2024, 3, 1)
        return [
            {
                "symbol": symbol,
                "trade_date": (start + timedelta(days=index)).isoformat(),
                "open": close,
                "high": close + 1,
                "low": close - 1,
                "close": close,
                "volume": 1000,
                "amount": close * 1000,
                "source": self.name,
                "is_adjusted": False,
            }
            for index, close in enumerate(closes)
        ]

    def fetch_adjustment_factors(self, symbol, start_date, end_date):
        return [
            {"symbol": symbol, "trade_date": row["trade_date"], "adj_factor": 1.0, "source": self.name}
            for row in self.fetch_daily_bars(symbol, start_date, end_date)
        ]

    def fetch_stock_status(self, symbols, trade_date):
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]


def test_daily_sync_pipeline_persists_market_data_and_materialized_analysis():
    repo = MySqlRepository(AppSettings.from_env())
    repo.clear_test_data(["TST002.SZ"])
    pipeline = DailySyncPipeline(repository=repo, providers=[PipelineProvider()])

    job = pipeline.run_full_daily_pipeline(start_date="2024-03-01", end_date="2024-04-10", requested_by="unit")

    assert job["status"] == "completed"
    assert job["summary"]["success"] == 1
    rows = repo.latest_screening_rows("2024-05-20", symbols=["TST002.SZ"])
    assert rows[0]["symbol"] == "TST002.SZ"
    assert rows[0]["selected_signal"] == "HALF_SELL"
    assert repo.coverage()["strategy_signals"]["rows"] >= 1
    assert repo.trading_calendar("SZ", "2024-03-01", "2024-03-01") == [
        {"exchange": "SZ", "trade_date": "2024-03-01", "is_open": True}
    ]
    assert repo.stock_status(["TST002.SZ"], "2024-04-10") == [
        {"symbol": "TST002.SZ", "trade_date": "2024-04-10", "is_st": False, "is_suspended": False}
    ]
