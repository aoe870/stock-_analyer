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


def test_mysql_repository_bars_falls_back_to_unadjusted_rows_for_detail_view():
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
                "adj_factor": None,
                "price_mode": "unadjusted",
                "source": "unit",
                "data_quality": "missing_adj_factor",
            }
        ]
    )

    bars = repo.bars("TST001.SZ")

    assert len(bars) == 1
    assert bars[0]["price_mode"] == "unadjusted"
    assert bars[0]["data_quality"] == "missing_adj_factor"


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


def test_mysql_repository_persists_miana_side_data_and_raw_payloads():
    repo = repository()
    repo.upsert_stocks([{"symbol": "TST001.SZ", "exchange": "SZ", "name": "Test One", "source": "miana"}])

    repo.upsert_stock_provider_profiles(
        [
            {
                "symbol": "TST001.SZ",
                "provider": "miana",
                "provider_symbol": "szTST001",
                "exchange": "SZ",
                "name": "Test One",
                "industry": "Software",
                "country_code": "CHN",
                "exchange_code": "XSHE",
                "market": "cn_hsj",
                "type": "STOCK",
                "is_active": True,
                "is_st": False,
                "raw_json": {"code": "TST001", "name": "Test One"},
            }
        ]
    )
    repo.upsert_stock_company_profiles(
        [{"symbol": "TST001.SZ", "provider": "miana", "industry": "Software", "region": "SZ", "raw_json": {"industry": "Software"}}]
    )
    repo.upsert_corporate_actions(
        [
            {
                "symbol": "TST001.SZ",
                "provider": "miana",
                "action_type": "dividend",
                "currency": "CNY",
                "dividend": 1.23,
                "split_factor": None,
                "notice_date": "2024-05-01",
                "report_date": "2023",
                "equity_record_date": "2024-05-10",
                "ex_dividend_date": "2024-05-11",
                "pay_cash_date": "2024-05-12",
                "raw_json": {"type": "dividend"},
            }
        ]
    )
    repo.upsert_share_capital_history(
        [
            {
                "symbol": "TST001.SZ",
                "provider": "miana",
                "end_date": "2024-01-01",
                "total_shares": 1000,
                "floating_shares": 900,
                "limited_shares": 100,
                "change_reason": "initial",
                "raw_json": {"totalShares": 1000},
            }
        ]
    )
    repo.upsert_daily_money_flow(
        [
            {
                "symbol": "TST001.SZ",
                "provider": "miana",
                "trade_date": "2024-01-02",
                "amount": 10000,
                "main_net_inflow_amount": 500,
                "main_net_ratio": 0.05,
                "super_large_inflow": 1000,
                "super_large_outflow": 500,
                "raw_json": {"amount": 10000},
            }
        ]
    )
    repo.save_raw_provider_payload(
        provider="miana",
        endpoint="/api/stock/v2/kline",
        payload={"msg": "ok", "data": [{"price": 10}]},
        symbol="TST001.SZ",
        date_start="2024-01-01",
        date_end="2024-01-02",
        request_params={"symbol": "szTST001", "fq": "qfq"},
    )

    with repo.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT provider_symbol, industry FROM stock_provider_profiles WHERE symbol=%s AND provider=%s", ("TST001.SZ", "miana"))
            assert cursor.fetchone() == {"provider_symbol": "szTST001", "industry": "Software"}
            cursor.execute("SELECT industry FROM stock_company_profiles WHERE symbol=%s AND provider=%s", ("TST001.SZ", "miana"))
            assert cursor.fetchone()["industry"] == "Software"
            cursor.execute("SELECT action_type, dividend FROM corporate_actions WHERE symbol=%s AND provider=%s", ("TST001.SZ", "miana"))
            action = cursor.fetchone()
            assert action["action_type"] == "dividend"
            assert float(action["dividend"]) == 1.23
            cursor.execute("SELECT total_shares FROM share_capital_history WHERE symbol=%s AND provider=%s", ("TST001.SZ", "miana"))
            assert float(cursor.fetchone()["total_shares"]) == 1000
            cursor.execute("SELECT amount, main_net_inflow_amount FROM daily_money_flow WHERE symbol=%s AND provider=%s", ("TST001.SZ", "miana"))
            flow = cursor.fetchone()
            assert float(flow["amount"]) == 10000
            assert float(flow["main_net_inflow_amount"]) == 500
            cursor.execute("SELECT request_params_json, date_start, date_end FROM raw_provider_payloads WHERE provider=%s AND symbol=%s", ("miana", "TST001.SZ"))
            raw = cursor.fetchone()
            assert raw["date_start"].isoformat() == "2024-01-01"
            assert raw["date_end"].isoformat() == "2024-01-02"
            assert '"fq": "qfq"' in raw["request_params_json"]


def test_mysql_repository_persists_v2_research_and_market_structure_data():
    repo = repository()
    provider = "unit_market_structure"
    repo._execute("DELETE FROM index_constituents WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM sector_constituents WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM latest_index_quotes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM latest_sector_quotes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM market_indexes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM market_sectors WHERE provider=%s", (provider,))
    repo.upsert_stocks([{"symbol": "TST001.SZ", "exchange": "SZ", "name": "Test One", "source": provider}])

    repo.upsert_income_statements(
        [
            {
                "symbol": "TST001.SZ",
                "provider": provider,
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
                "raw_json": {"revenue": 100},
            }
        ]
    )
    repo.upsert_balance_sheets(
        [
            {
                "symbol": "TST001.SZ",
                "provider": provider,
                "report_date": "2024-12-31",
                "report_period": "2024A",
                "total_assets": 1000,
                "total_liabilities": 400,
                "total_equity": 600,
                "raw_json": {"totalAssets": 1000},
            }
        ]
    )
    repo.upsert_cashflow_statements(
        [
            {
                "symbol": "TST001.SZ",
                "provider": provider,
                "report_date": "2024-12-31",
                "report_period": "2024A",
                "net_operating_cashflow": 50,
                "raw_json": {"netOperatingCashflow": 50},
            }
        ]
    )
    repo.upsert_stock_top10_holders(
        [
            {
                "symbol": "TST001.SZ",
                "provider": provider,
                "report_date": "2024-12-31",
                "holder_name": "Holder A",
                "holder_rank": 1,
                "hold_volume": 100,
                "hold_ratio": 5.5,
                "raw_json": {"name": "Holder A"},
            }
        ]
    )
    repo.upsert_market_indexes([{"index_code": "sh000001", "provider": provider, "name": "Index One", "exchange_code": "XSHG", "country_code": "CHN", "raw_json": {}}])
    repo.upsert_market_sectors([{"sector_code": "BK001", "provider": provider, "name": "Sector One", "market": "cn_hs", "raw_json": {}}])
    repo.upsert_latest_index_quotes([{"index_code": "sh000001", "provider": provider, "trade_date": "2024-01-02", "price": 3200, "change_rate": 9.99, "amount": 1000, "raw_json": {}}])
    repo.upsert_latest_sector_quotes([{"sector_code": "BK001", "provider": provider, "trade_date": "2024-01-02", "price": 1000, "change_rate": 9.99, "amount": 800, "raw_json": {}}])
    repo.upsert_index_constituents([{"index_code": "sh000001", "provider": provider, "symbol": "TST001.SZ", "weight": 1.2, "raw_json": {}}])
    repo.upsert_sector_constituents([{"sector_code": "BK001", "provider": provider, "symbol": "TST001.SZ", "weight": 2.3, "raw_json": {}}])

    financials = repo.stock_financials("TST001.SZ")
    coverage = repo.data_center_coverage()
    dashboard = repo.market_dashboard_snapshot()

    assert financials["income"][0]["revenue"] == 100.0
    assert financials["balance"][0]["total_assets"] == 1000.0
    assert financials["cashflow"][0]["net_operating_cashflow"] == 50.0
    assert coverage["research"]["financial_statements"]["rows"] >= 3
    assert coverage["research"]["holders"]["rows"] >= 1
    assert coverage["market_structure"]["indexes"]["rows"] >= 1
    assert dashboard["indexes"][0]["index_code"] == "sh000001"
    assert dashboard["indexes"][0]["price"] == 3200.0
    assert dashboard["sectors"][0]["sector_code"] == "BK001"
    assert dashboard["sectors"][0]["change_rate"] == 9.99
    repo._execute("DELETE FROM index_constituents WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM sector_constituents WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM latest_index_quotes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM latest_sector_quotes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM market_indexes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM market_sectors WHERE provider=%s", (provider,))


def test_latest_sector_quotes_replace_previous_provider_snapshot():
    repo = repository()
    provider = "unit_sector_snapshot"
    repo._execute("DELETE FROM latest_sector_quotes WHERE provider=%s", (provider,))
    repo._execute("DELETE FROM market_sectors WHERE provider=%s", (provider,))

    repo.upsert_market_sectors(
        [
            {"sector_code": "THEME001", "provider": provider, "name": "2025三季报扭亏", "market": "cn_hs", "raw_json": {}},
            {"sector_code": "BK001", "provider": provider, "name": "银行", "market": "cn_hs", "raw_json": {}},
        ]
    )
    repo.upsert_latest_sector_quotes(
        [
            {
                "sector_code": "THEME001",
                "provider": provider,
                "trade_date": "2024-01-01",
                "price": 1000,
                "change_rate": 0.99,
                "amount": 100,
                "raw_json": {},
            }
        ]
    )

    repo.upsert_latest_sector_quotes(
        [
            {
                "sector_code": "BK001",
                "provider": provider,
                "trade_date": "2024-01-02",
                "price": 1000,
                "change_rate": 0.01,
                "amount": 100,
                "raw_json": {},
            }
        ]
    )

    sectors = repo.market_dashboard_snapshot()["sectors"]

    assert any(row["sector_code"] == "BK001" for row in sectors)
    assert all(row["sector_code"] != "THEME001" for row in sectors)


def test_market_dashboard_builds_stock_rankings_from_latest_complete_analysis_date():
    repo = repository()
    symbols = [f"990{i:03d}.SZ" for i in range(1, 26)]
    repo.clear_test_data(symbols)
    repo.upsert_stocks(
        [
            {"symbol": symbol, "exchange": "SZ", "name": f"Rank {index}", "source": "unit"}
            for index, symbol in enumerate(symbols, start=1)
        ]
    )

    rows = []
    for index, symbol in enumerate(symbols, start=1):
        current_close = 10 + index
        if index == 1:
            current_close = 15
        if index == 2:
            current_close = 8
        rows.extend(
            [
                {
                    "symbol": symbol,
                    "trade_date": "2099-01-02",
                    "open": 10,
                    "high": 10,
                    "low": 10,
                    "close": 10,
                    "volume": 100,
                    "amount": 1000,
                    "price_mode": "forward_adjusted",
                    "source": "unit",
                    "data_quality": "ok",
                },
                {
                    "symbol": symbol,
                    "trade_date": "2099-01-03",
                    "open": current_close,
                    "high": current_close,
                    "low": current_close,
                    "close": current_close,
                    "volume": 100 + index,
                    "amount": 1000 + index,
                    "price_mode": "forward_adjusted",
                    "source": "unit",
                    "data_quality": "ok",
                },
            ]
        )
    rows.append(
        {
            "symbol": symbols[0],
            "trade_date": "2099-01-04",
            "open": 16,
            "high": 16,
            "low": 16,
            "close": 16,
            "volume": 1,
            "amount": 1,
            "price_mode": "forward_adjusted",
            "source": "unit",
            "data_quality": "ok",
        }
    )
    repo.upsert_analysis_daily_bars(rows)

    rankings = repo.market_dashboard_snapshot()["rankings"]

    assert rankings["gainers"][0]["symbol"] == symbols[-1]
    assert rankings["gainers"][0]["trade_date"] == "2099-01-03"
    assert rankings["gainers"][0]["change_rate"] == 2.5
    assert rankings["losers"][0]["symbol"] == symbols[1]
    assert rankings["losers"][0]["change_rate"] == -0.2
    assert rankings["amount"][0]["trade_date"] == "2099-01-03"
    repo.clear_test_data(symbols)
