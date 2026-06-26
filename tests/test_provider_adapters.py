import pytest

from stock_analyzer_app.config import AppSettings, DatabaseSettings
from stock_analyzer_app.data_provider.akshare_provider import AkShareProvider
from stock_analyzer_app.data_provider.eastmoney_provider import EastmoneyProvider
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain
from stock_analyzer_app.data_provider.tushare_provider import TushareProvider


def settings(token=""):
    return AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["tushare", "akshare", "eastmoney"],
        tushare_token=token,
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )


def test_provider_chain_builds_concrete_adapters_and_skips_tushare_without_token():
    chain = build_provider_chain(settings(token=""))

    assert [type(provider) for provider in chain.providers] == [AkShareProvider, EastmoneyProvider]


def test_provider_chain_includes_tushare_when_token_exists():
    chain = build_provider_chain(settings(token="token"))

    assert isinstance(chain.providers[0], TushareProvider)
    assert chain.providers[0].token == "token"


def test_missing_optional_provider_dependency_raises_clear_runtime_error():
    provider = AkShareProvider(module=None)

    with pytest.raises(RuntimeError, match="AkShare is not installed"):
        provider.fetch_stock_universe()


def test_akshare_daily_bars_normalizes_chinese_columns():
    class FakeAkShare:
        @staticmethod
        def stock_zh_a_hist(symbol, period, start_date, end_date, adjust):
            assert symbol == "000001"
            assert period == "daily"
            assert start_date == "20240102"
            assert end_date == "20240105"
            assert adjust == ""
            return [
                {
                    "日期": "2024-01-02",
                    "开盘": 10.1,
                    "最高": 10.5,
                    "最低": 9.9,
                    "收盘": 10.3,
                    "成交量": 12345,
                    "成交额": 67890,
                }
            ]

    rows = AkShareProvider(module=FakeAkShare()).fetch_daily_bars("000001.SZ", "2024-01-02", "2024-01-05")

    assert rows == [
        {
            "symbol": "000001.SZ",
            "trade_date": "2024-01-02",
            "open": 10.1,
            "high": 10.5,
            "low": 9.9,
            "close": 10.3,
            "volume": 12345,
            "amount": 67890,
            "source": "akshare",
            "is_adjusted": False,
        }
    ]


def test_akshare_adjustment_factors_are_derived_from_forward_adjusted_close():
    calls = []

    class FakeAkShare:
        @staticmethod
        def stock_zh_a_hist(symbol, period, start_date, end_date, adjust):
            calls.append(adjust)
            rows_by_adjust = {
                "": [
                    {"日期": "2024-01-02", "收盘": 10.0},
                    {"日期": "2024-01-03", "收盘": 20.0},
                    {"日期": "2024-01-04", "收盘": 0},
                ],
                "qfq": [
                    {"日期": "2024-01-02", "收盘": 12.5},
                    {"日期": "2024-01-03", "收盘": 20.0},
                    {"日期": "2024-01-04", "收盘": 1.0},
                ],
            }
            return rows_by_adjust[adjust]

    rows = AkShareProvider(module=FakeAkShare()).fetch_adjustment_factors("000001.SZ", "2024-01-02", "2024-01-05")

    assert calls == ["", "qfq"]
    assert rows == [
        {"symbol": "000001.SZ", "trade_date": "2024-01-02", "adj_factor": 1.25, "source": "akshare"},
        {"symbol": "000001.SZ", "trade_date": "2024-01-03", "adj_factor": 1.0, "source": "akshare"},
    ]


def test_akshare_stock_status_uses_st_and_suspension_lists_when_available():
    class FakeAkShare:
        @staticmethod
        def stock_zh_a_st_em():
            return [
                {"代码": "000001", "名称": "*ST Alpha"},
                {"代码": "600000", "名称": "ST Beta"},
            ]

        @staticmethod
        def stock_tfp_em(date):
            assert date == "20240102"
            return [
                {"代码": "600000", "名称": "ST Beta", "停牌时间": "2024-01-02"},
            ]

    rows = AkShareProvider(module=FakeAkShare()).fetch_stock_status(
        ["000001.SZ", "600000.SH", "000002.SZ"],
        "2024-01-02",
    )

    assert rows == [
        {"symbol": "000001.SZ", "trade_date": "2024-01-02", "is_st": True, "is_suspended": False},
        {"symbol": "600000.SH", "trade_date": "2024-01-02", "is_st": True, "is_suspended": True},
        {"symbol": "000002.SZ", "trade_date": "2024-01-02", "is_st": False, "is_suspended": False},
    ]
