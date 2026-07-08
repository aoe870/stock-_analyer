import pytest

from stock_analyzer_app.config.settings import AppSettings, DatabaseSettings
from stock_analyzer_app.data_provider.base import StockDataProvider
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain
from stock_analyzer_app.sync.service import InMemorySyncRepository, SyncService
from stock_analyzer_app.sync.pipeline import DailySyncPipeline
from stock_analyzer_app.tasks.scheduler import SyncSchedulerGuard
import threading


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
        miana_token="",
        miana_base_url="https://miana.com.cn/api",
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
        miana_token="",
        miana_base_url="https://miana.com.cn/api",
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


def test_daily_pipeline_persists_local_market_dashboard_quote_snapshots():
    class RepositoryWithMarketSnapshots(InMemorySyncRepository):
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

        def upsert_market_indexes(self, rows):
            self.indexes = rows

        def upsert_market_sectors(self, rows):
            self.sectors = rows

        def upsert_latest_index_quotes(self, rows):
            self.index_quotes = rows

        def upsert_latest_sector_quotes(self, rows):
            self.sector_quotes = rows

    class MarketSnapshotProvider(FakeProvider):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.sector_ranking_requests = []

        def fetch_index_rankings(self, sort="changeRate", order="DESC"):
            return [{"index_code": "sh000001", "provider": self.name, "name": "Index", "trade_date": "2024-01-02", "price": 3200, "change_rate": 0.01}]

        def fetch_sector_rankings(self, sort="changeRate", order="DESC", sector_type="all"):
            self.sector_ranking_requests.append({"sort": sort, "order": order, "sector_type": sector_type})
            return [{"sector_code": "BK001", "provider": self.name, "name": "Bank", "trade_date": "2024-01-02", "price": 1000, "change_rate": 0.02}]

    repository = RepositoryWithMarketSnapshots()
    provider = MarketSnapshotProvider("fake", universe=[{"symbol": "AAA.SZ", "exchange": "SZ", "name": "AAA", "source": "fake"}])
    pipeline = DailySyncPipeline(repository=repository, providers=[provider])

    job = pipeline.run_full_daily_pipeline("2024-01-02", "2024-01-02", requested_by="unit")

    assert job["status"] == "completed"
    assert repository.indexes[0]["index_code"] == "sh000001"
    assert repository.sectors[0]["sector_code"] == "BK001"
    assert repository.index_quotes[0]["price"] == 3200
    assert repository.sector_quotes[0]["change_rate"] == 0.02
    assert provider.sector_ranking_requests == [{"sort": "changeRate", "order": "DESC", "sector_type": "industry"}]


def test_daily_pipeline_processes_symbols_concurrently_with_configured_workers():
    class RepositoryWithParallelSupport(InMemorySyncRepository):
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

    barrier = threading.Barrier(3)
    lock = threading.Lock()
    active = {"count": 0, "max": 0}

    class ParallelProvider(FakeProvider):
        def fetch_stock_universe(self):
            return [
                {"symbol": "AAA.SZ", "exchange": "SZ", "name": "AAA", "source": self.name},
                {"symbol": "BBB.SZ", "exchange": "SZ", "name": "BBB", "source": self.name},
                {"symbol": "CCC.SZ", "exchange": "SZ", "name": "CCC", "source": self.name},
            ]

        def fetch_trading_calendar(self, exchange, start_date, end_date):
            return []

        def fetch_daily_bars(self, symbol, start_date, end_date):
            with lock:
                active["count"] += 1
                active["max"] = max(active["max"], active["count"])
            try:
                barrier.wait(timeout=5)
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
            finally:
                with lock:
                    active["count"] -= 1

        def fetch_adjustment_factors(self, symbol, start_date, end_date):
            return [{"symbol": symbol, "trade_date": start_date, "adj_factor": 1.0, "source": self.name}]

        def fetch_stock_status(self, symbols, trade_date):
            return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]

    repository = RepositoryWithParallelSupport()
    pipeline = DailySyncPipeline(repository=repository, providers=[ParallelProvider("parallel")], max_workers=3)

    job = pipeline.run_full_daily_pipeline(
        "2024-01-02",
        "2024-01-02",
        requested_by="unit",
        symbols=["AAA.SZ", "BBB.SZ", "CCC.SZ"],
    )

    assert job["status"] == "completed"
    assert job["summary"]["success"] == 3
    assert active["max"] >= 2


def test_daily_pipeline_persists_miana_side_data_and_adjusted_bars():
    class RepositoryWithMianaSideData(InMemorySyncRepository):
        def upsert_stocks(self, rows):
            self.stocks = rows

        def upsert_stock_provider_profiles(self, rows):
            self.provider_profiles = rows

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

        def upsert_stock_company_profiles(self, rows):
            self.company_profiles = rows

        def upsert_corporate_actions(self, rows):
            self.corporate_actions = rows

        def upsert_share_capital_history(self, rows):
            self.share_history = rows

        def upsert_daily_money_flow(self, rows):
            self.money_flow = rows

        def save_raw_provider_payload(self, **payload):
            self.raw_payloads = getattr(self, "raw_payloads", [])
            self.raw_payloads.append(payload)

    class MianaLikeProvider(FakeProvider):
        name = "miana"

        def __init__(self):
            super().__init__(
                "miana",
                universe=[
                    {
                        "symbol": "AAA.SZ",
                        "exchange": "SZ",
                        "name": "AAA",
                        "source": "miana",
                        "provider": "miana",
                        "provider_symbol": "szAAA",
                        "raw_json": {"code": "AAA"},
                    }
                ],
            )
            self.raw_payloads = [{"endpoint": "/stock/v2/kline", "payload": {"code": 200}, "request_params": {"fq": "qfq"}, "symbol": "AAA.SZ"}]

        def fetch_adjusted_daily_bars(self, symbol, start_date, end_date):
            return [{**self.fetch_daily_bars(symbol, start_date, end_date)[0], "close": 12, "is_adjusted": True}]

        def fetch_company_profiles(self, symbol):
            return [{"symbol": symbol, "provider": "miana", "industry": "Tech", "raw_json": {"industry": "Tech"}}]

        def fetch_corporate_actions(self, symbol):
            return [{"symbol": symbol, "provider": "miana", "action_type": "dividend", "report_date": "2023", "notice_date": "2024-01-01"}]

        def fetch_share_capital_history(self, symbol):
            return [{"symbol": symbol, "provider": "miana", "end_date": "2024-01-01", "total_shares": 1000}]

        def fetch_daily_money_flow(self, symbol, trade_date):
            return [{"symbol": symbol, "provider": "miana", "trade_date": trade_date, "amount": 1000}]

        def drain_raw_payloads(self):
            rows = self.raw_payloads
            self.raw_payloads = []
            return rows

    repository = RepositoryWithMianaSideData()
    pipeline = DailySyncPipeline(repository=repository, providers=[MianaLikeProvider()])

    job = pipeline.run_full_daily_pipeline("2024-01-02", "2024-01-02", requested_by="unit")

    assert job["status"] == "completed"
    assert repository.provider_profiles[0]["provider_symbol"] == "szAAA"
    assert any(row["is_adjusted"] for row in repository.daily_bars)
    assert repository.company_profiles[0]["industry"] == "Tech"
    assert repository.corporate_actions[0]["action_type"] == "dividend"
    assert repository.share_history[0]["total_shares"] == 1000
    assert repository.money_flow[0]["amount"] == 1000
    assert repository.raw_payloads[0]["endpoint"] == "/stock/v2/kline"


def test_daily_pipeline_can_skip_low_frequency_miana_side_data_for_daily_runs():
    class RepositoryWithMianaSideData(InMemorySyncRepository):
        def upsert_stocks(self, rows):
            self.stocks = rows

        def upsert_stock_provider_profiles(self, rows):
            self.provider_profiles = rows

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

        def upsert_stock_company_profiles(self, rows):
            self.company_profiles = rows

        def upsert_corporate_actions(self, rows):
            self.corporate_actions = rows

        def upsert_share_capital_history(self, rows):
            self.share_history = rows

        def upsert_daily_money_flow(self, rows):
            self.money_flow = rows

    class MianaLikeProvider(FakeProvider):
        name = "miana"

        def __init__(self):
            super().__init__(
                "miana",
                universe=[{"symbol": "AAA.SZ", "exchange": "SZ", "name": "AAA", "source": "miana"}],
            )
            self.optional_calls = []

        def fetch_adjusted_daily_bars(self, symbol, start_date, end_date):
            return [{**self.fetch_daily_bars(symbol, start_date, end_date)[0], "close": 12, "is_adjusted": True}]

        def fetch_company_profiles(self, symbol):
            self.optional_calls.append("company")
            return [{"symbol": symbol, "provider": "miana", "industry": "Tech", "raw_json": {"industry": "Tech"}}]

        def fetch_corporate_actions(self, symbol):
            self.optional_calls.append("actions")
            return [{"symbol": symbol, "provider": "miana", "action_type": "dividend", "report_date": "2023", "notice_date": "2024-01-01"}]

        def fetch_share_capital_history(self, symbol):
            self.optional_calls.append("shares")
            return [{"symbol": symbol, "provider": "miana", "end_date": "2024-01-01", "total_shares": 1000}]

        def fetch_daily_money_flow(self, symbol, trade_date):
            self.optional_calls.append("money_flow")
            return [{"symbol": symbol, "provider": "miana", "trade_date": trade_date, "amount": 1000}]

    provider = MianaLikeProvider()
    repository = RepositoryWithMianaSideData()
    pipeline = DailySyncPipeline(repository=repository, providers=[provider], include_optional_metadata=False)

    job = pipeline.run_full_daily_pipeline("2024-01-02", "2024-01-02", requested_by="unit")

    assert job["status"] == "completed"
    assert provider.optional_calls == []
    assert not hasattr(repository, "company_profiles")
    assert not hasattr(repository, "corporate_actions")
    assert not hasattr(repository, "share_history")
    assert not hasattr(repository, "money_flow")


def test_fundamental_refresh_pipeline_persists_research_data_without_daily_bars():
    class RepositoryWithResearch(InMemorySyncRepository):
        def upsert_income_statements(self, rows):
            self.income = rows

        def upsert_balance_sheets(self, rows):
            self.balance = rows

        def upsert_cashflow_statements(self, rows):
            self.cashflow = rows

        def upsert_stock_top10_holders(self, rows):
            self.holders = rows

        def upsert_stock_company_officers(self, rows):
            self.officers = rows

        def upsert_stock_officer_rewards(self, rows):
            self.rewards = rows

    class ResearchProvider(FakeProvider):
        def fetch_income_statements(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "report_date": "2024-12-31", "revenue": 100}]

        def fetch_balance_sheets(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "report_date": "2024-12-31", "total_assets": 1000}]

        def fetch_cashflow_statements(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "report_date": "2024-12-31", "net_operating_cashflow": 50}]

        def fetch_top10_holders(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "report_date": "2024-12-31", "holder_name": "Holder A"}]

        def fetch_company_officers(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "officer_name": "Officer A", "title": "董事长"}]

        def fetch_officer_rewards(self, symbol):
            return [{"symbol": symbol, "provider": self.name, "report_date": "2024-12-31", "officer_name": "Officer A"}]

    repository = RepositoryWithResearch()
    pipeline = DailySyncPipeline(repository=repository, providers=[ResearchProvider("miana")])

    job = pipeline.run_fundamental_refresh_pipeline(requested_by="unit", symbols=["AAA.SZ"])

    assert job["status"] == "completed"
    assert repository.income[0]["revenue"] == 100
    assert repository.balance[0]["total_assets"] == 1000
    assert repository.cashflow[0]["net_operating_cashflow"] == 50
    assert repository.holders[0]["holder_name"] == "Holder A"
    freshness = repository.get_dataset_freshness("stock_research_context", "AAA.SZ")
    assert freshness["status"] == "ready"
    assert freshness["rows"] == 6
    assert freshness["owner_job_type"] == "fundamental_refresh_pipeline"


def test_market_structure_pipeline_persists_indexes_sectors_and_constituents():
    class RepositoryWithMarketStructure(InMemorySyncRepository):
        def upsert_market_indexes(self, rows):
            self.indexes = rows

        def upsert_market_sectors(self, rows):
            self.sectors = rows

        def upsert_index_constituents(self, rows):
            self.index_constituents = rows

        def upsert_sector_constituents(self, rows):
            self.sector_constituents = rows

    class MarketProvider(FakeProvider):
        def fetch_index_list(self):
            return [{"index_code": "sh000001", "provider": self.name, "name": "上证指数"}]

        def fetch_sector_list(self):
            return [{"sector_code": "BK001", "provider": self.name, "name": "银行"}]

        def fetch_index_constituents(self, index_code):
            return [{"index_code": index_code, "provider": self.name, "symbol": "AAA.SZ"}]

        def fetch_sector_constituents(self, sector_code):
            return [{"sector_code": sector_code, "provider": self.name, "symbol": "AAA.SZ"}]

    repository = RepositoryWithMarketStructure()
    pipeline = DailySyncPipeline(repository=repository, providers=[MarketProvider("miana")])

    job = pipeline.run_market_structure_pipeline(requested_by="unit")

    assert job["status"] == "completed"
    assert repository.indexes[0]["index_code"] == "sh000001"
    assert repository.sectors[0]["sector_code"] == "BK001"
    assert repository.index_constituents[0]["symbol"] == "AAA.SZ"
    assert repository.sector_constituents[0]["symbol"] == "AAA.SZ"


def test_scheduler_guard_prevents_duplicate_daily_pipeline():
    repository = InMemorySyncRepository()
    first = repository.create_job("full_daily_pipeline", "scheduler", ["fake"])
    repository.mark_job_running(first["id"])
    guard = SyncSchedulerGuard(repository)

    assert guard.can_start("full_daily_pipeline") is False
    repository.finish_job(first["id"], "completed", {})
    assert guard.can_start("full_daily_pipeline") is True
