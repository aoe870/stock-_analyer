import pytest

from stock_analyzer_app.config.settings import AppSettings, DatabaseSettings
from stock_analyzer_app.data_provider.base import StockDataProvider
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain
from stock_analyzer_app.sync.service import InMemorySyncRepository, SyncService
from stock_analyzer_app.sync.pipeline import DailySyncPipeline
from stock_analyzer_app.tasks.scheduler import SyncSchedulerGuard


class FakeProvider(StockDataProvider):
    def __init__(self, name, universe=None, failing_symbols=None):
        self.name = name
        self._universe = universe or []
        self.failing_symbols = set(failing_symbols or [])

    def fetch_stock_universe(self):
        return list(self._universe)

    def fetch_trading_calendar(self, exchange, start_date, end_date):
        return [{"exchange": exchange, "trade_date": start_date, "is_open": True}]

    def fetch_daily_bars(self, symbol, start_date, end_date):
        if symbol in self.failing_symbols:
            raise RuntimeError(f"{symbol} failed")
        return [
            {
                "symbol": symbol,
                "trade_date": start_date,
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
        return [{"symbol": symbol, "trade_date": start_date, "adj_factor": 1.0, "source": self.name}]

    def fetch_stock_status(self, symbols, trade_date):
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]


def test_provider_contract_exposes_required_methods():
    required = {
        "fetch_stock_universe",
        "fetch_trading_calendar",
        "fetch_daily_bars",
        "fetch_adjustment_factors",
        "fetch_stock_status",
    }

    assert required <= set(dir(StockDataProvider))


def test_provider_chain_prefers_tushare_when_token_configured():
    settings = AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["tushare", "akshare", "eastmoney"],
        tushare_token="token",
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )

    chain = build_provider_chain(settings)

    assert [provider.name for provider in chain.providers][:3] == ["tushare", "akshare", "eastmoney"]


def test_provider_chain_skips_tushare_without_token():
    settings = AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["tushare", "akshare", "eastmoney"],
        tushare_token="",
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )

    chain = build_provider_chain(settings)

    assert [provider.name for provider in chain.providers] == ["akshare", "eastmoney"]


def test_sync_daily_bars_records_completed_with_errors_for_partial_success():
    repository = InMemorySyncRepository()
    provider = FakeProvider("fake", failing_symbols={"BBB"})
    service = SyncService(repository=repository, providers=[provider])

    job = service.sync_daily_bars(["AAA", "BBB"], "2024-01-02", "2024-01-02", requested_by="manual")

    assert job["status"] == "completed_with_errors"
    assert job["summary"] == {"success": 1, "skipped": 0, "failed": 1, "retryable": 0, "provider_fallback": 0}
    assert repository.daily_bars[0]["symbol"] == "AAA"
    assert {item["status"] for item in repository.items[job["id"]]} == {"success", "failed"}


def test_daily_pipeline_records_metadata_errors_without_blocking_symbol_sync():
    class RepositoryWithMetadata(InMemorySyncRepository):
        def upsert_stocks(self, rows):
            self.stocks = rows

        def upsert_trading_calendar(self, rows):
            self.calendar = rows

        def upsert_adjustment_factors(self, rows):
            self.factors = rows

        def upsert_analysis_daily_bars(self, rows):
            self.analysis = rows

        def upsert_daily_indicators(self, rows):
            self.indicators = rows

        def upsert_strategy_signals(self, rows):
            self.signals = rows

        def upsert_stock_status(self, rows):
            self.status = rows

    class MetadataFailingProvider(FakeProvider):
        def fetch_trading_calendar(self, exchange, start_date, end_date):
            raise RuntimeError("calendar unavailable")

        def fetch_stock_status(self, symbols, trade_date):
            raise RuntimeError("status unavailable")

    repository = RepositoryWithMetadata()
    provider = MetadataFailingProvider("fake", universe=[{"symbol": "AAA.SZ", "exchange": "SZ", "name": "AAA", "source": "fake"}])
    pipeline = DailySyncPipeline(repository=repository, providers=[provider])

    job = pipeline.run_full_daily_pipeline("2024-01-02", "2024-01-02", requested_by="unit")

    assert job["status"] == "completed"
    assert job["summary"]["success"] == 1
    assert job["summary"]["metadata_errors"] == 2
    assert repository.get_job_items(job["id"])[0]["status"] == "success"


def test_scheduler_guard_prevents_duplicate_daily_pipeline():
    repository = InMemorySyncRepository()
    first = repository.create_job("full_daily_pipeline", "scheduler", ["fake"])
    repository.mark_job_running(first["id"])
    guard = SyncSchedulerGuard(repository)

    assert guard.can_start("full_daily_pipeline") is False
    repository.finish_job(first["id"], "completed", {})
    assert guard.can_start("full_daily_pipeline") is True
