from stock_analyzer_app.config.settings import AppSettings, DatabaseSettings
from stock_analyzer_app.data_provider.miana_provider import MianaProvider, miana_symbol, normalized_symbol
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain


def test_miana_symbol_conversion_for_a_share_exchanges():
    assert miana_symbol("600519.SH") == "sh600519"
    assert miana_symbol("000001.SZ") == "sz000001"
    assert miana_symbol("430001.BJ") == "bj430001"
    assert normalized_symbol({"code": "600519", "exchangeCode": "XSHG"}) == "600519.SH"
    assert normalized_symbol({"code": "000001", "exchangeCode": "XSHE"}) == "000001.SZ"
    assert normalized_symbol({"code": "430001", "exchangeCode": "BJSE"}) == "430001.BJ"


def test_miana_provider_normalizes_stock_list_and_kline_rows():
    def fake_get(endpoint, params):
        if endpoint == "/stock/v1/stockList":
            return {
                "code": 200,
                "data": [
                    {"code": "000001", "name": "平安银行", "exchangeCode": "XSHE", "countryCode": "CHN", "type": "STOCK"}
                ],
            }
        if endpoint == "/stock/v2/kline":
            assert params["symbol"] == "sz000001"
            assert params["fq"] == "bfq"
            return {
                "code": 200,
                "data": [
                    {"date": "2024-01-02 00:00:00", "open": 10, "high": 11, "low": 9, "price": 10.5, "volume": 100, "amount": 1000}
                ],
            }
        raise AssertionError(endpoint)

    provider = MianaProvider("token", http_get=fake_get)

    universe = provider.fetch_stock_universe()
    bars = provider.fetch_daily_bars("000001.SZ", "2024-01-01", "2024-01-03")

    assert universe == [
        {
            "symbol": "000001.SZ",
            "exchange": "SZ",
            "name": "平安银行",
            "industry": None,
            "is_active": True,
            "is_st": False,
            "source": "miana",
            "provider": "miana",
            "provider_symbol": "sz000001",
            "country_code": "CHN",
            "exchange_code": "XSHE",
            "market": None,
            "type": "STOCK",
            "raw_json": {"code": "000001", "name": "平安银行", "exchangeCode": "XSHE", "countryCode": "CHN", "type": "STOCK"},
        }
    ]
    assert bars == [
        {
            "symbol": "000001.SZ",
            "trade_date": "2024-01-02",
            "open": 10,
            "high": 11,
            "low": 9,
            "close": 10.5,
            "volume": 100,
            "amount": 1000,
            "source": "miana",
            "is_adjusted": False,
        }
    ]


def test_miana_provider_derives_adjustment_factors_from_bfq_and_qfq_close():
    def fake_get(endpoint, params):
        assert endpoint == "/stock/v2/kline"
        close = 10 if params["fq"] == "bfq" else 12
        return {"code": 200, "data": [{"date": "2024-01-02", "open": close, "high": close, "low": close, "price": close, "volume": 1, "amount": 1}]}

    provider = MianaProvider("token", http_get=fake_get)

    factors = provider.fetch_adjustment_factors("000001.SZ", "2024-01-01", "2024-01-03")
    adjusted = provider.fetch_adjusted_daily_bars("000001.SZ", "2024-01-01", "2024-01-03")

    assert factors == [{"symbol": "000001.SZ", "trade_date": "2024-01-02", "adj_factor": 1.2, "source": "miana"}]
    assert adjusted[0]["is_adjusted"] is True
    assert adjusted[0]["close"] == 12


def test_miana_provider_normalizes_stock_and_index_rankings_from_sort_payloads():
    def fake_get(endpoint, params):
        if endpoint == "/stock/v1/sort":
            assert params == {"market": "cn_hs", "sort": "changeRate", "order": "DESC", "page": "1"}
            return {
                "code": 200,
                "data": {
                    "page": 1,
                    "list": [
                        {
                            "code": "600519",
                            "name": "贵州茅台",
                            "exchangeCode": "XSHG",
                            "date": "2026-07-06",
                            "price": 1800,
                            "change": 18,
                            "changeRate": 1,
                            "volume": 100,
                            "amount": 180000,
                        }
                    ],
                },
            }
        if endpoint == "/index/v1/sort":
            assert params == {"countryCode": "CHN", "sort": "changeRate", "order": "DESC", "page": "1"}
            return {
                "code": 200,
                "data": {
                    "list": [
                        {
                            "code": "000001",
                            "name": "上证指数",
                            "exchangeCode": "XSHG",
                            "date": "2026-07-06",
                            "price": 3200,
                            "changeRate": 0.5,
                        }
                    ],
                },
            }
        raise AssertionError(endpoint)

    provider = MianaProvider("token", http_get=fake_get)

    stock_rows = provider.fetch_stock_rankings(sort="changeRate", order="DESC")
    index_rows = provider.fetch_index_rankings(sort="changeRate", order="DESC")

    assert stock_rows[0]["symbol"] == "600519.SH"
    assert stock_rows[0]["change_rate"] == 0.01
    assert stock_rows[0]["amount"] == 180000
    assert index_rows[0]["index_code"] == "sh000001"
    assert index_rows[0]["price"] == 3200
    assert index_rows[0]["change_rate"] == 0.005


def test_miana_provider_builds_bars_and_factors_from_one_bfq_and_one_qfq_request():
    requests = []

    def fake_get(endpoint, params):
        assert endpoint == "/stock/v2/kline"
        requests.append(params["fq"])
        close = 10 if params["fq"] == "bfq" else 12
        return {
            "code": 200,
            "data": [
                {
                    "date": "2024-01-02",
                    "open": close,
                    "high": close,
                    "low": close,
                    "price": close,
                    "volume": 1,
                    "amount": 1,
                }
            ],
        }

    provider = MianaProvider("token", http_get=fake_get)

    bundle = provider.fetch_daily_bar_bundle("000001.SZ", "2024-01-01", "2024-01-03")

    assert requests == ["bfq", "qfq"]
    assert bundle["bars"][0]["close"] == 10
    assert bundle["adjusted_bars"][0]["close"] == 12
    assert bundle["factors"] == [{"symbol": "000001.SZ", "trade_date": "2024-01-02", "adj_factor": 1.2, "source": "miana"}]


def test_miana_provider_fetches_long_kline_ranges_in_date_segments():
    requests = []

    def fake_get(endpoint, params):
        assert endpoint == "/stock/v2/kline"
        requests.append((params["beginDate"], params["endDate"]))
        return {
            "code": 200,
            "data": [
                {
                    "date": params["beginDate"][:10],
                    "open": 10,
                    "high": 11,
                    "low": 9,
                    "price": 10,
                    "volume": 1,
                    "amount": 1,
                }
            ],
        }

    provider = MianaProvider("token", http_get=fake_get)

    rows = provider.fetch_daily_bars("000001.SZ", "2020-01-01", "2026-07-03")

    assert len(requests) > 1
    assert requests[0][0] == "2020-01-01 00:00:00"
    assert requests[-1][1] == "2026-07-03 23:59:59"
    assert [row["trade_date"] for row in rows] == sorted(row["trade_date"] for row in rows)


def test_miana_provider_normalizes_financial_statement_rows():
    def fake_get(endpoint, params):
        assert params["symbol"] == "sz000001"
        if endpoint == "/stock/v1/incomeSheet":
            return {
                "code": 200,
                "data": [
                    {
                        "reportDate": "2024-12-31",
                        "noticeDate": "2025-04-01",
                        "reportPeriod": "2024A",
                        "currency": "CNY",
                        "revenue": 100,
                        "operatingRevenue": 90,
                        "operatingProfit": 30,
                        "totalProfit": 28,
                        "netProfit": 20,
                        "netProfitParent": 18,
                        "eps": 1.2,
                    }
                ],
            }
        if endpoint == "/stock/v1/balanceSheet":
            return {
                "code": 200,
                "data": [
                    {
                        "reportDate": "2024-12-31",
                        "totalAssets": 1000,
                        "totalLiabilities": 400,
                        "totalEquity": 600,
                        "monetaryFunds": 120,
                        "accountsReceivable": 80,
                        "inventory": 60,
                    }
                ],
            }
        if endpoint == "/stock/v1/cashflow":
            return {
                "code": 200,
                "data": [
                    {
                        "reportDate": "2024-12-31",
                        "netOperatingCashflow": 50,
                        "netInvestingCashflow": -20,
                        "netFinancingCashflow": -10,
                        "cashAndEquivalents": 200,
                    }
                ],
            }
        raise AssertionError(endpoint)

    provider = MianaProvider("token", http_get=fake_get)

    assert provider.fetch_income_statements("000001.SZ")[0] == {
        "symbol": "000001.SZ",
        "provider": "miana",
        "report_date": "2024-12-31",
        "notice_date": "2025-04-01",
        "report_period": "2024A",
        "currency": "CNY",
        "revenue": 100,
        "operating_revenue": 90,
        "operating_profit": 30,
        "total_profit": 28,
        "net_profit": 20,
        "net_profit_parent": 18,
        "eps": 1.2,
        "raw_json": {
            "reportDate": "2024-12-31",
            "noticeDate": "2025-04-01",
            "reportPeriod": "2024A",
            "currency": "CNY",
            "revenue": 100,
            "operatingRevenue": 90,
            "operatingProfit": 30,
            "totalProfit": 28,
            "netProfit": 20,
            "netProfitParent": 18,
            "eps": 1.2,
        },
    }
    assert provider.fetch_balance_sheets("000001.SZ")[0]["total_assets"] == 1000
    assert provider.fetch_cashflow_statements("000001.SZ")[0]["net_operating_cashflow"] == 50


def test_miana_provider_normalizes_holder_officer_index_and_sector_rows():
    def fake_get(endpoint, params):
        if endpoint == "/stock/v1/top10holders":
            return {"code": 200, "data": [{"date": "2024-12-31", "name": "Holder A", "rank": 1, "holdVol": 100, "holdRatio": 5.5, "shareType": "A"}]}
        if endpoint == "/stock/v1/companyOfficer":
            return {"code": 200, "data": [{"name": "Officer A", "title": "董事长", "startDate": "2024-01-01"}]}
        if endpoint == "/stock/v1/rewards":
            return {"code": 200, "data": [{"date": "2024-12-31", "name": "Officer A", "title": "董事长", "reward": 100000, "holdVol": 10}]}
        if endpoint == "/index/v1/indexList":
            return {"code": 200, "data": [{"code": "000001", "name": "上证指数", "exchangeCode": "XSHG", "countryCode": "CHN"}]}
        if endpoint == "/sector/v1/sectorList":
            return {"code": 200, "data": [{"code": "BK001", "name": "银行", "market": "cn_hs"}]}
        if endpoint == "/index/v1/constituent":
            assert params["symbol"] == "sh000001"
            return {"code": 200, "data": [{"code": "600000", "exchangeCode": "XSHG", "weight": 1.2}]}
        if endpoint == "/sector/v1/constituent":
            assert params["symbol"] == "BK001"
            return {"code": 200, "data": [{"code": "000001", "exchangeCode": "XSHE", "weight": 2.3}]}
        raise AssertionError(endpoint)

    provider = MianaProvider("token", http_get=fake_get)

    assert provider.fetch_top10_holders("000001.SZ")[0]["holder_name"] == "Holder A"
    assert provider.fetch_company_officers("000001.SZ")[0]["officer_name"] == "Officer A"
    assert provider.fetch_officer_rewards("000001.SZ")[0]["reward"] == 100000
    assert provider.fetch_index_list()[0]["index_code"] == "sh000001"
    assert provider.fetch_sector_list()[0]["sector_code"] == "BK001"
    assert provider.fetch_index_constituents("sh000001")[0]["symbol"] == "600000.SH"
    assert provider.fetch_sector_constituents("BK001")[0]["symbol"] == "000001.SZ"


def test_provider_chain_includes_miana_only_when_token_configured():
    with_miana = AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["miana", "akshare"],
        tushare_token="",
        miana_token="token",
        miana_base_url="https://example.test/api",
        sync_max_workers=8,
        miana_max_requests_per_minute=321,
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )
    without_miana = AppSettings(
        db=with_miana.db,
        provider_priority=["miana", "akshare"],
        tushare_token="",
        miana_token="",
        miana_base_url="https://example.test/api",
        sync_max_workers=8,
        miana_max_requests_per_minute=321,
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )

    assert [provider.name for provider in build_provider_chain(with_miana).providers] == ["miana", "akshare"]
    assert [provider.name for provider in build_provider_chain(without_miana).providers] == ["akshare"]


def test_provider_chain_passes_miana_rate_limit_configuration():
    settings = AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["miana"],
        tushare_token="",
        miana_token="token",
        miana_base_url="https://example.test/api",
        sync_max_workers=8,
        miana_max_requests_per_minute=321,
        sync_enabled=True,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )

    provider = build_provider_chain(settings).providers[0]

    assert provider.max_requests_per_minute == 321
