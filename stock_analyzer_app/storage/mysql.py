import json
from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

from stock_analyzer_app.config import AppSettings


def mysql_available(settings: AppSettings) -> bool:
    try:
        connection = pymysql.connect(
            host=settings.db.host,
            port=settings.db.port,
            user=settings.db.user,
            password=settings.db.password,
            database=settings.db.name,
            connect_timeout=1,
            read_timeout=1,
            write_timeout=1,
        )
        connection.close()
        return True
    except Exception:
        return False


class MySqlRepository:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    @contextmanager
    def connection(self):
        connection = pymysql.connect(
            host=self.settings.db.host,
            port=self.settings.db.port,
            user=self.settings.db.user,
            password=self.settings.db.password,
            database=self.settings.db.name,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def clear_test_data(self, symbols: list[str]) -> None:
        if not symbols:
            return
        placeholders = ",".join(["%s"] * len(symbols))
        request_conditions = " OR ".join(["scope_json LIKE %s OR reason LIKE %s"] * len(symbols))
        request_params = []
        for symbol in symbols:
            request_params.extend([f"%{symbol}%", f"%{symbol}%"])
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM sync_requests WHERE {request_conditions}", request_params)
                cursor.execute(f"DELETE FROM strategy_signals WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM daily_indicators WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM analysis_daily_bars WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM latest_market_quotes WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM sector_constituents WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM index_constituents WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_officer_rewards WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_company_officers WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_top10_holders WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM cashflow_statements WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM balance_sheets WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM income_statements WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM daily_money_flow WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM share_capital_history WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM corporate_actions WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_company_profiles WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_provider_profiles WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_daily_status WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM adjustment_factors WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM daily_bars WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM raw_provider_payloads WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM dataset_freshness WHERE scope_key IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stocks WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM sync_job_items WHERE symbol IN ({placeholders})", symbols)

    def upsert_stocks(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stocks (symbol, exchange, name, industry, list_date, delist_date, is_active, is_st, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                exchange=VALUES(exchange), name=VALUES(name), industry=VALUES(industry),
                list_date=VALUES(list_date), delist_date=VALUES(delist_date),
                is_active=VALUES(is_active), is_st=VALUES(is_st), source=VALUES(source)
        """
        values = [
            (
                row["symbol"],
                row.get("exchange") or _exchange_from_symbol(row["symbol"]),
                row.get("name", row["symbol"]),
                row.get("industry"),
                row.get("list_date"),
                row.get("delist_date"),
                bool(row.get("is_active", True)),
                bool(row.get("is_st", False)),
                row.get("source", "unknown"),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_daily_bars(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO daily_bars (symbol, trade_date, open, high, low, close, volume, amount, source, is_adjusted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open=VALUES(open), high=VALUES(high), low=VALUES(low), close=VALUES(close),
                volume=VALUES(volume), amount=VALUES(amount)
        """
        values = [
            (
                row["symbol"],
                row["trade_date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row.get("volume", 0),
                row.get("amount", 0),
                row.get("source", "unknown"),
                bool(row.get("is_adjusted", False)),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_adjustment_factors(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO adjustment_factors (symbol, trade_date, adj_factor, source)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE adj_factor=VALUES(adj_factor)
        """
        self._executemany(sql, [(row["symbol"], row["trade_date"], row["adj_factor"], row.get("source", "unknown")) for row in rows])

    def upsert_trading_calendar(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO trading_calendar (exchange, trade_date, is_open, previous_trade_date, next_trade_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                is_open=VALUES(is_open),
                previous_trade_date=VALUES(previous_trade_date),
                next_trade_date=VALUES(next_trade_date)
        """
        values = [
            (
                row["exchange"],
                row["trade_date"],
                bool(row.get("is_open", False)),
                row.get("previous_trade_date"),
                row.get("next_trade_date"),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT exchange, trade_date, is_open FROM trading_calendar WHERE exchange=%s AND trade_date BETWEEN %s AND %s ORDER BY trade_date",
                    (exchange, start_date, end_date),
                )
                return [{"exchange": row["exchange"], "trade_date": str(row["trade_date"]), "is_open": bool(row["is_open"])} for row in cursor.fetchall()]

    def upsert_stock_status(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_daily_status (symbol, trade_date, is_st, is_suspended, source)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                is_st=VALUES(is_st),
                is_suspended=VALUES(is_suspended)
        """
        values = [
            (
                row["symbol"],
                row["trade_date"],
                bool(row.get("is_st", False)),
                bool(row.get("is_suspended", False)),
                row.get("source", "unknown"),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_stock_provider_profiles(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_provider_profiles
                (symbol, provider, provider_symbol, exchange, name, industry, country_code, exchange_code,
                 market, type, is_active, is_st, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                provider_symbol=VALUES(provider_symbol), exchange=VALUES(exchange), name=VALUES(name),
                industry=VALUES(industry), country_code=VALUES(country_code), exchange_code=VALUES(exchange_code),
                market=VALUES(market), type=VALUES(type), is_active=VALUES(is_active), is_st=VALUES(is_st),
                raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", row.get("source", "unknown")),
                row.get("provider_symbol") or row["symbol"],
                row.get("exchange"),
                row.get("name"),
                row.get("industry"),
                row.get("country_code"),
                row.get("exchange_code"),
                row.get("market"),
                row.get("type"),
                bool(row.get("is_active", True)),
                bool(row.get("is_st", False)),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_stock_company_profiles(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_company_profiles
                (symbol, provider, company_name, industry, region, found_date, registered_capital,
                 employee_count, accounting_firm, legal_adviser, concepts, address, legal_person,
                 chairman, president, secretary, org_tel, org_email, org_web, org_profile,
                 company_profile, main_business, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                company_name=VALUES(company_name), industry=VALUES(industry), region=VALUES(region),
                found_date=VALUES(found_date), registered_capital=VALUES(registered_capital),
                employee_count=VALUES(employee_count), accounting_firm=VALUES(accounting_firm),
                legal_adviser=VALUES(legal_adviser), concepts=VALUES(concepts), address=VALUES(address),
                legal_person=VALUES(legal_person), chairman=VALUES(chairman), president=VALUES(president),
                secretary=VALUES(secretary), org_tel=VALUES(org_tel), org_email=VALUES(org_email),
                org_web=VALUES(org_web), org_profile=VALUES(org_profile), company_profile=VALUES(company_profile),
                main_business=VALUES(main_business),
                raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", row.get("source", "unknown")),
                row.get("company_name"),
                row.get("industry"),
                row.get("region"),
                row.get("found_date"),
                row.get("registered_capital"),
                row.get("employee_count"),
                row.get("accounting_firm"),
                row.get("legal_adviser"),
                row.get("concepts"),
                row.get("address"),
                row.get("legal_person"),
                row.get("chairman"),
                row.get("president"),
                row.get("secretary"),
                row.get("org_tel"),
                row.get("org_email"),
                row.get("org_web"),
                row.get("org_profile"),
                row.get("company_profile"),
                row.get("main_business"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_corporate_actions(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO corporate_actions
                (symbol, provider, action_type, currency, dividend, split_factor, notice_date, report_date,
                 equity_record_date, ex_dividend_date, pay_cash_date, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                currency=VALUES(currency), dividend=VALUES(dividend), split_factor=VALUES(split_factor),
                equity_record_date=VALUES(equity_record_date), ex_dividend_date=VALUES(ex_dividend_date),
                pay_cash_date=VALUES(pay_cash_date), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", row.get("source", "unknown")),
                row.get("action_type") or row.get("type", "unknown"),
                row.get("currency"),
                row.get("dividend"),
                row.get("split_factor"),
                row.get("notice_date"),
                row.get("report_date"),
                row.get("equity_record_date"),
                row.get("ex_dividend_date"),
                row.get("pay_cash_date"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_share_capital_history(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO share_capital_history
                (symbol, provider, end_date, total_shares, floating_shares, limited_shares, change_reason, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_shares=VALUES(total_shares), floating_shares=VALUES(floating_shares),
                limited_shares=VALUES(limited_shares), change_reason=VALUES(change_reason), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", row.get("source", "unknown")),
                row["end_date"],
                row.get("total_shares"),
                row.get("floating_shares"),
                row.get("limited_shares"),
                row.get("change_reason"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_daily_money_flow(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO daily_money_flow
                (symbol, provider, trade_date, amount, main_net_inflow_amount, main_net_ratio,
                 super_large_inflow, super_large_outflow, super_large_net_inflow, super_large_net_ratio,
                 large_inflow, large_outflow, large_net_inflow, large_net_ratio,
                 medium_inflow, medium_outflow, medium_net_inflow, medium_net_ratio,
                 small_inflow, small_outflow, small_net_inflow, small_net_ratio, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                amount=VALUES(amount), main_net_inflow_amount=VALUES(main_net_inflow_amount),
                main_net_ratio=VALUES(main_net_ratio), super_large_inflow=VALUES(super_large_inflow),
                super_large_outflow=VALUES(super_large_outflow), super_large_net_inflow=VALUES(super_large_net_inflow),
                super_large_net_ratio=VALUES(super_large_net_ratio), large_inflow=VALUES(large_inflow),
                large_outflow=VALUES(large_outflow), large_net_inflow=VALUES(large_net_inflow),
                large_net_ratio=VALUES(large_net_ratio), medium_inflow=VALUES(medium_inflow),
                medium_outflow=VALUES(medium_outflow), medium_net_inflow=VALUES(medium_net_inflow),
                medium_net_ratio=VALUES(medium_net_ratio), small_inflow=VALUES(small_inflow),
                small_outflow=VALUES(small_outflow), small_net_inflow=VALUES(small_net_inflow),
                small_net_ratio=VALUES(small_net_ratio), raw_json=VALUES(raw_json)
        """
        keys = [
            "super_large_inflow",
            "super_large_outflow",
            "super_large_net_inflow",
            "super_large_net_ratio",
            "large_inflow",
            "large_outflow",
            "large_net_inflow",
            "large_net_ratio",
            "medium_inflow",
            "medium_outflow",
            "medium_net_inflow",
            "medium_net_ratio",
            "small_inflow",
            "small_outflow",
            "small_net_inflow",
            "small_net_ratio",
        ]
        values = [
            (
                row["symbol"],
                row.get("provider", row.get("source", "unknown")),
                row["trade_date"],
                row.get("amount"),
                row.get("main_net_inflow_amount"),
                row.get("main_net_ratio"),
                *(row.get(key) for key in keys),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_income_statements(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO income_statements
                (symbol, provider, report_date, notice_date, report_period, currency, revenue, operating_revenue,
                 operating_profit, total_profit, net_profit, net_profit_parent, eps, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                notice_date=VALUES(notice_date), currency=VALUES(currency), revenue=VALUES(revenue),
                operating_revenue=VALUES(operating_revenue), operating_profit=VALUES(operating_profit),
                total_profit=VALUES(total_profit), net_profit=VALUES(net_profit),
                net_profit_parent=VALUES(net_profit_parent), eps=VALUES(eps), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["report_date"],
                row.get("notice_date"),
                row.get("report_period", ""),
                row.get("currency"),
                row.get("revenue"),
                row.get("operating_revenue"),
                row.get("operating_profit"),
                row.get("total_profit"),
                row.get("net_profit"),
                row.get("net_profit_parent"),
                row.get("eps"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_balance_sheets(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO balance_sheets
                (symbol, provider, report_date, notice_date, report_period, currency, total_assets,
                 total_liabilities, total_equity, monetary_funds, accounts_receivable, inventory, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                notice_date=VALUES(notice_date), currency=VALUES(currency), total_assets=VALUES(total_assets),
                total_liabilities=VALUES(total_liabilities), total_equity=VALUES(total_equity),
                monetary_funds=VALUES(monetary_funds), accounts_receivable=VALUES(accounts_receivable),
                inventory=VALUES(inventory), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["report_date"],
                row.get("notice_date"),
                row.get("report_period", ""),
                row.get("currency"),
                row.get("total_assets"),
                row.get("total_liabilities"),
                row.get("total_equity"),
                row.get("monetary_funds"),
                row.get("accounts_receivable"),
                row.get("inventory"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_cashflow_statements(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO cashflow_statements
                (symbol, provider, report_date, notice_date, report_period, currency, net_operating_cashflow,
                 net_investing_cashflow, net_financing_cashflow, cash_and_equivalents, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                notice_date=VALUES(notice_date), currency=VALUES(currency),
                net_operating_cashflow=VALUES(net_operating_cashflow),
                net_investing_cashflow=VALUES(net_investing_cashflow),
                net_financing_cashflow=VALUES(net_financing_cashflow),
                cash_and_equivalents=VALUES(cash_and_equivalents), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["report_date"],
                row.get("notice_date"),
                row.get("report_period", ""),
                row.get("currency"),
                row.get("net_operating_cashflow"),
                row.get("net_investing_cashflow"),
                row.get("net_financing_cashflow"),
                row.get("cash_and_equivalents"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_stock_top10_holders(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_top10_holders
                (symbol, provider, report_date, holder_name, holder_rank, hold_volume, hold_ratio, share_type, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                holder_rank=VALUES(holder_rank), hold_volume=VALUES(hold_volume),
                hold_ratio=VALUES(hold_ratio), share_type=VALUES(share_type), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["report_date"],
                row["holder_name"],
                row.get("holder_rank"),
                row.get("hold_volume"),
                row.get("hold_ratio"),
                row.get("share_type"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_stock_company_officers(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_company_officers
                (symbol, provider, officer_name, title, start_date, end_date, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                start_date=VALUES(start_date), end_date=VALUES(end_date), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["officer_name"],
                row.get("title", ""),
                row.get("start_date"),
                row.get("end_date"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_stock_officer_rewards(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO stock_officer_rewards
                (symbol, provider, report_date, officer_name, title, reward, hold_volume, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title=VALUES(title), reward=VALUES(reward), hold_volume=VALUES(hold_volume), raw_json=VALUES(raw_json)
        """
        values = [
            (
                row["symbol"],
                row.get("provider", "unknown"),
                row["report_date"],
                row["officer_name"],
                row.get("title"),
                row.get("reward"),
                row.get("hold_volume"),
                _json_text(row.get("raw_json", {})),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_market_indexes(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO market_indexes (index_code, provider, name, exchange_code, country_code, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name), exchange_code=VALUES(exchange_code), country_code=VALUES(country_code), raw_json=VALUES(raw_json)
        """
        self._executemany(
            sql,
            [
                (row["index_code"], row.get("provider", "unknown"), row.get("name", row["index_code"]), row.get("exchange_code"), row.get("country_code"), _json_text(row.get("raw_json", {})))
                for row in rows
            ],
        )

    def upsert_index_constituents(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO index_constituents (index_code, provider, symbol, weight, raw_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE weight=VALUES(weight), raw_json=VALUES(raw_json)
        """
        self._executemany(sql, [(row["index_code"], row.get("provider", "unknown"), row["symbol"], row.get("weight"), _json_text(row.get("raw_json", {}))) for row in rows])

    def upsert_latest_index_quotes(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO latest_index_quotes
                (index_code, provider, quote_time, price, change_amount, change_rate, volume, amount, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                quote_time=VALUES(quote_time), price=VALUES(price), change_amount=VALUES(change_amount),
                change_rate=VALUES(change_rate), volume=VALUES(volume), amount=VALUES(amount), raw_json=VALUES(raw_json)
        """
        self._executemany(
            sql,
            [
                (
                    row["index_code"],
                    row.get("provider", row.get("source", "unknown")),
                    row.get("quote_time") or row.get("trade_date"),
                    row.get("price") or row.get("close"),
                    row.get("change_amount") or row.get("change"),
                    row.get("change_rate"),
                    row.get("volume"),
                    row.get("amount"),
                    _json_text(row.get("raw_json", row)),
                )
                for row in rows
            ],
        )

    def upsert_market_sectors(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO market_sectors (sector_code, provider, name, market, raw_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), market=VALUES(market), raw_json=VALUES(raw_json)
        """
        self._executemany(
            sql,
            [(row["sector_code"], row.get("provider", "unknown"), row.get("name", row["sector_code"]), row.get("market"), _json_text(row.get("raw_json", {}))) for row in rows],
        )

    def upsert_sector_constituents(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO sector_constituents (sector_code, provider, symbol, weight, raw_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE weight=VALUES(weight), raw_json=VALUES(raw_json)
        """
        self._executemany(sql, [(row["sector_code"], row.get("provider", "unknown"), row["symbol"], row.get("weight"), _json_text(row.get("raw_json", {}))) for row in rows])

    def upsert_latest_sector_quotes(self, rows: list[dict]) -> None:
        values = [
            (
                row["sector_code"],
                row.get("provider", row.get("source", "unknown")),
                row.get("quote_time") or row.get("trade_date"),
                row.get("price") or row.get("close"),
                row.get("change_amount") or row.get("change"),
                row.get("change_rate"),
                row.get("amount"),
                _json_text(row.get("raw_json", row)),
            )
            for row in rows
        ]
        if not values:
            return
        providers = sorted({value[1] for value in values})
        placeholders = ",".join(["%s"] * len(providers))
        sql = """
            INSERT INTO latest_sector_quotes
                (sector_code, provider, quote_time, price, change_amount, change_rate, amount, raw_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                quote_time=VALUES(quote_time), price=VALUES(price), change_amount=VALUES(change_amount),
                change_rate=VALUES(change_rate), amount=VALUES(amount), raw_json=VALUES(raw_json)
        """
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM latest_sector_quotes WHERE provider IN ({placeholders})", providers)
                cursor.executemany(sql, values)

    def save_raw_provider_payload(
        self,
        provider: str,
        endpoint: str,
        payload: dict | list,
        symbol: str | None = None,
        trade_date: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        request_params: dict | None = None,
    ) -> None:
        payload_json = _json_text(payload)
        payload_hash = __import__("hashlib").sha256(payload_json.encode("utf-8")).hexdigest()
        sql = """
            INSERT IGNORE INTO raw_provider_payloads
                (provider, endpoint, symbol, trade_date, request_params_json, date_start, date_end, payload_hash, payload_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._execute(
            sql,
            (
                provider,
                endpoint,
                symbol,
                trade_date,
                _json_text(request_params or {}),
                date_start,
                date_end,
                payload_hash,
                payload_json,
            ),
        )

    def stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        if not symbols:
            return []
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT symbol, trade_date, MAX(is_st) AS is_st, MAX(is_suspended) AS is_suspended
                    FROM stock_daily_status
                    WHERE trade_date=%s AND symbol IN ({",".join(["%s"] * len(symbols))})
                    GROUP BY symbol, trade_date
                    """,
                    (trade_date, *symbols),
                )
                by_symbol = {row["symbol"]: row for row in cursor.fetchall()}
        return [
            {
                "symbol": symbol,
                "trade_date": str(by_symbol[symbol]["trade_date"]),
                "is_st": bool(by_symbol[symbol]["is_st"]),
                "is_suspended": bool(by_symbol[symbol]["is_suspended"]),
            }
            for symbol in symbols
            if symbol in by_symbol
        ]

    def upsert_analysis_daily_bars(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO analysis_daily_bars
                (symbol, trade_date, open, high, low, close, volume, amount, adj_factor, price_mode, source, data_quality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open=VALUES(open), high=VALUES(high), low=VALUES(low), close=VALUES(close),
                volume=VALUES(volume), amount=VALUES(amount), adj_factor=VALUES(adj_factor),
                source=VALUES(source), data_quality=VALUES(data_quality)
        """
        values = [
            (
                row["symbol"],
                row["trade_date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row.get("volume", 0),
                row.get("amount", 0),
                row.get("adj_factor"),
                row.get("price_mode", "forward_adjusted"),
                row.get("source", "unknown"),
                row.get("data_quality", "ok"),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_daily_indicators(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO daily_indicators
                (symbol, trade_date, strategy_key, expma17, expma50, cross_price, cross_in_kline, warmup_ready)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                expma17=VALUES(expma17), expma50=VALUES(expma50), cross_price=VALUES(cross_price),
                cross_in_kline=VALUES(cross_in_kline), warmup_ready=VALUES(warmup_ready)
        """
        values = [
            (
                row["symbol"],
                row["trade_date"],
                row.get("strategy_key", "expma_17_50"),
                row.get("expma17"),
                row.get("expma50"),
                row.get("cross_price"),
                bool(row.get("cross_in_kline", False)),
                bool(row.get("warmup_ready", False)),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def upsert_strategy_signals(self, rows: list[dict]) -> None:
        sql = """
            INSERT INTO strategy_signals
                (symbol, trade_date, strategy_key, selected_signal, raw_flags_json, trend_state)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                selected_signal=VALUES(selected_signal), raw_flags_json=VALUES(raw_flags_json),
                trend_state=VALUES(trend_state)
        """
        values = [
            (
                row["symbol"],
                row["trade_date"],
                row.get("strategy_key", "expma_17_50"),
                row.get("selected_signal"),
                _json_text(row.get("raw_flags_json", row.get("raw_flags", {}))),
                row.get("trend_state", "unknown"),
            )
            for row in rows
        ]
        self._executemany(sql, values)

    def list_stocks(self) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT symbol, exchange, name, industry, is_active, is_st, source FROM stocks ORDER BY symbol")
                return list(cursor.fetchall())

    def get_stock(self, symbol: str) -> dict | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT symbol, exchange, name, industry, is_active, is_st, source FROM stocks WHERE symbol=%s", (symbol,))
                return cursor.fetchone()

    def latest_screening_rows(self, trade_date: str, symbols: list[str] | None = None, price_mode: str = "forward_adjusted") -> list[dict]:
        symbol_params: list[Any] = []
        symbol_clause = ""
        if symbols:
            symbol_clause = " AND adb.symbol IN (" + ",".join(["%s"] * len(symbols)) + ")"
            symbol_params.extend(symbols)
        sql = f"""
            SELECT adb.symbol, s.name, adb.trade_date, adb.open, adb.high, adb.low, adb.close,
                   adb.volume, adb.amount, adb.price_mode, adb.source, adb.data_quality,
                   di.expma17, di.expma50, di.cross_price, di.cross_in_kline, di.warmup_ready,
                   ss.selected_signal, ss.raw_flags_json, ss.trend_state
            FROM analysis_daily_bars adb
            JOIN (
                SELECT symbol, MAX(trade_date) AS trade_date
                FROM analysis_daily_bars
                WHERE price_mode=%s AND trade_date <= %s
                GROUP BY symbol
            ) latest ON latest.symbol=adb.symbol AND latest.trade_date=adb.trade_date
            LEFT JOIN stocks s ON s.symbol=adb.symbol
            LEFT JOIN daily_indicators di ON di.symbol=adb.symbol AND di.trade_date=adb.trade_date AND di.strategy_key='expma_17_50'
            LEFT JOIN strategy_signals ss ON ss.symbol=adb.symbol AND ss.trade_date=adb.trade_date AND ss.strategy_key='expma_17_50'
            WHERE adb.price_mode=%s {symbol_clause}
            ORDER BY adb.symbol
        """
        params: list[Any] = [price_mode, trade_date, price_mode, *symbol_params]
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return [_decode_analysis_row(row) for row in cursor.fetchall()]

    def analysis_bars_with_signals(self, symbols: list[str], start_date: str, end_date: str, price_mode: str = "forward_adjusted") -> dict[str, list[dict]]:
        if not symbols:
            return {}
        params: list[Any] = [price_mode, start_date, end_date, *symbols]
        sql = f"""
            SELECT adb.symbol, adb.trade_date, adb.open, adb.high, adb.low, adb.close,
                   adb.volume, adb.amount, adb.price_mode, adb.source, adb.data_quality,
                   di.expma17, di.expma50, di.cross_price, di.cross_in_kline, di.warmup_ready,
                   ss.selected_signal, ss.raw_flags_json, ss.trend_state
            FROM analysis_daily_bars adb
            LEFT JOIN daily_indicators di ON di.symbol=adb.symbol AND di.trade_date=adb.trade_date AND di.strategy_key='expma_17_50'
            LEFT JOIN strategy_signals ss ON ss.symbol=adb.symbol AND ss.trade_date=adb.trade_date AND ss.strategy_key='expma_17_50'
            WHERE adb.price_mode=%s AND adb.trade_date BETWEEN %s AND %s
              AND adb.symbol IN ({",".join(["%s"] * len(symbols))})
            ORDER BY adb.symbol, adb.trade_date
        """
        output = {symbol: [] for symbol in symbols}
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                for row in cursor.fetchall():
                    output[row["symbol"]].append(_decode_analysis_row(row))
        return output

    def bars(self, symbol: str, price_mode: str = "forward_adjusted") -> list[dict]:
        rows = self.analysis_bars_with_signals([symbol], "0001-01-01", "9999-12-31", price_mode).get(symbol, [])
        if rows or price_mode != "forward_adjusted":
            return rows
        return self.analysis_bars_with_signals([symbol], "0001-01-01", "9999-12-31", "unadjusted").get(symbol, [])

    def indicators(self, symbol: str) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM daily_indicators WHERE symbol=%s ORDER BY trade_date", (symbol,))
                return [_numbers(row) for row in cursor.fetchall()]

    def signals(self, symbol: str) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM strategy_signals WHERE symbol=%s ORDER BY trade_date", (symbol,))
                rows = []
                for row in cursor.fetchall():
                    decoded = dict(row)
                    decoded["raw_flags"] = json.loads(decoded.pop("raw_flags_json") or "{}")
                    rows.append(decoded)
                return rows

    def stock_financials(self, symbol: str) -> dict:
        income = self._select_symbol_rows("income_statements", symbol, "report_date DESC")
        balance = self._select_symbol_rows("balance_sheets", symbol, "report_date DESC")
        cashflow = self._select_symbol_rows("cashflow_statements", symbol, "report_date DESC")
        report_dates = [row.get("report_date") for row in [*income, *balance, *cashflow] if row.get("report_date")]
        return {
            "symbol": symbol,
            "income": income,
            "balance": balance,
            "cashflow": cashflow,
            "summary": {
                "latest_report_date": max(report_dates) if report_dates else None,
                "income_rows": len(income),
                "balance_rows": len(balance),
                "cashflow_rows": len(cashflow),
            },
        }

    def stock_capital_flow(self, symbol: str) -> dict:
        rows = self._select_symbol_rows("daily_money_flow", symbol, "trade_date DESC")
        return {
            "symbol": symbol,
            "rows": rows,
            "summary": {
                "latest_trade_date": rows[0].get("trade_date") if rows else None,
                "rows": len(rows),
            },
        }

    def _enterprise_module_status(self, symbol: str, table: str, date_column: str | None = None) -> dict:
        date_expr = f"MAX({date_column})" if date_column else "NULL"
        row = self._select_rows(
            f"""
            SELECT COUNT(*) AS rows_count, {date_expr} AS newest_date, MIN(provider) AS provider
            FROM {table}
            WHERE symbol=%s
            """,
            (symbol,),
        )[0]
        rows_count = int(row["rows_count"])
        return {
            "rows": rows_count,
            "status": "synced" if rows_count else "missing",
            "newest_date": row.get("newest_date"),
            "provider": row.get("provider"),
        }

    def _enterprise_module_statuses(self, symbol: str) -> dict:
        return {
            "company_profile": self._enterprise_module_status(symbol, "stock_company_profiles"),
            "share_capital": self._enterprise_module_status(symbol, "share_capital_history", "end_date"),
            "corporate_actions": self._enterprise_module_status(symbol, "corporate_actions", "notice_date"),
            "holders": self._enterprise_module_status(symbol, "stock_top10_holders", "report_date"),
            "officers": self._enterprise_module_status(symbol, "stock_company_officers"),
            "officer_rewards": self._enterprise_module_status(symbol, "stock_officer_rewards", "report_date"),
            "capital_flow": self._enterprise_module_status(symbol, "daily_money_flow", "trade_date"),
        }

    def stock_research_snapshot(self, symbol: str) -> dict:
        stock = self.get_stock(symbol)
        if not stock:
            raise KeyError(symbol)
        bars = self.bars(symbol)
        company_profile = self._first_symbol_row("stock_company_profiles", symbol)
        enterprise_modules = self._enterprise_module_statuses(symbol)
        return {
            "stock": stock,
            "latest_bar": bars[-1] if bars else None,
            "company_profile": company_profile,
            "share_capital": self._select_symbol_rows("share_capital_history", symbol, "end_date DESC"),
            "corporate_actions": self._select_symbol_rows("corporate_actions", symbol, "notice_date DESC"),
            "holders": self._select_symbol_rows("stock_top10_holders", symbol, "report_date DESC, holder_rank ASC"),
            "officers": self._select_symbol_rows("stock_company_officers", symbol, "officer_name ASC"),
            "officer_rewards": self._select_symbol_rows("stock_officer_rewards", symbol, "report_date DESC, reward DESC"),
            "data_quality": {
                "has_bars": bool(bars),
                "has_research_data": any(item["rows"] for item in enterprise_modules.values()),
                "enterprise_modules": enterprise_modules,
            },
        }

    def _market_dashboard_ranking_date(self) -> str | None:
        rows = self._select_rows(
            """
            SELECT trade_date, COUNT(*) AS row_count
            FROM analysis_daily_bars
            WHERE price_mode='forward_adjusted'
            GROUP BY trade_date
            ORDER BY trade_date DESC
            LIMIT 30
            """
        )
        for row in rows:
            if int(row["row_count"]) >= 20:
                return row["trade_date"]
        return rows[0]["trade_date"] if rows else None

    def _stock_rankings_for_date(self, trade_date: str) -> dict[str, list[dict]]:
        base_sql = """
            SELECT cur.symbol, COALESCE(s.name, cur.symbol) AS name, cur.trade_date, cur.close, cur.volume, cur.amount,
                   cur.price_mode, cur.data_quality, (cur.close - prev.close) AS `change`,
                   ((cur.close / prev.close) - 1) AS change_rate
            FROM analysis_daily_bars cur
            JOIN analysis_daily_bars prev
              ON prev.symbol=cur.symbol
             AND prev.price_mode=cur.price_mode
             AND prev.trade_date=(
                SELECT MAX(p.trade_date)
                FROM analysis_daily_bars p
                WHERE p.symbol=cur.symbol
                  AND p.price_mode=cur.price_mode
                  AND p.trade_date < cur.trade_date
             )
            JOIN stocks s ON s.symbol=cur.symbol
            WHERE cur.trade_date=%s
              AND cur.price_mode='forward_adjusted'
              AND prev.close > 0
              AND s.is_active=1
              AND s.symbol REGEXP '^[0-9]{{6}}\\.(SH|SZ|BJ)$'
            ORDER BY {order_by}
            LIMIT 20
        """
        return {
            "gainers": self._select_rows(base_sql.format(order_by="change_rate DESC, cur.symbol"), (trade_date,)),
            "losers": self._select_rows(base_sql.format(order_by="change_rate ASC, cur.symbol"), (trade_date,)),
            "amount": self._select_rows(base_sql.format(order_by="cur.amount DESC, cur.symbol"), (trade_date,)),
        }

    def market_dashboard_snapshot(self) -> dict:
        indexes = self._select_rows(
            """
            SELECT q.index_code, q.provider, COALESCE(i.name, q.index_code) AS name, i.exchange_code, i.country_code,
                   q.quote_time AS trade_date, q.price, q.change_amount AS `change`, q.change_rate, q.volume, q.amount
            FROM latest_index_quotes q
            LEFT JOIN market_indexes i ON i.index_code=q.index_code AND i.provider=q.provider
            ORDER BY q.change_rate DESC, q.index_code
            LIMIT 50
            """
        )
        if not indexes:
            indexes = self._select_rows("SELECT index_code, provider, name, exchange_code, country_code FROM market_indexes ORDER BY index_code LIMIT 50")
        sectors = self._select_rows(
            """
            SELECT q.sector_code, q.provider, COALESCE(s.name, q.sector_code) AS name, s.market,
                   q.quote_time AS trade_date, q.price, q.change_amount AS `change`, q.change_rate, q.amount
            FROM latest_sector_quotes q
            LEFT JOIN market_sectors s ON s.sector_code=q.sector_code AND s.provider=q.provider
            ORDER BY q.change_rate DESC, q.sector_code
            LIMIT 100
            """
        )
        if not sectors:
            sectors = self._select_rows("SELECT sector_code, provider, name, market FROM market_sectors ORDER BY name LIMIT 100")
        ranking_date = self._market_dashboard_ranking_date()
        rankings = self._stock_rankings_for_date(ranking_date) if ranking_date else {"gainers": [], "losers": [], "amount": []}
        readiness = self.sync_readiness()
        return {
            "indexes": indexes,
            "sectors": sectors,
            "rankings": rankings,
            "breadth": {"up": 0, "down": 0, "flat": readiness.get("updated_symbols", 0)},
            "freshness": {
                "latest_trade_date": readiness.get("latest_trade_date"),
                "ranking_trade_date": ranking_date,
                "ready_for_analysis": readiness.get("ready_for_analysis", False),
                "updated_symbols": readiness.get("updated_symbols", 0),
                "expected_symbols": readiness.get("expected_symbols", 0),
            },
        }

    def data_center_coverage(self) -> dict:
        return {
            "core": self.coverage(),
            "research": {
                "financial_statements": {"rows": self._count_rows("income_statements") + self._count_rows("balance_sheets") + self._count_rows("cashflow_statements")},
                "capital_flow": self._count_symbols_and_rows("daily_money_flow"),
                "company_profiles": self._count_symbols_and_rows("stock_company_profiles"),
                "corporate_actions": self._count_symbols_and_rows("corporate_actions"),
                "share_capital": self._count_symbols_and_rows("share_capital_history"),
                "holders": self._count_symbols_and_rows("stock_top10_holders"),
                "officers": self._count_symbols_and_rows("stock_company_officers"),
                "officer_rewards": self._count_symbols_and_rows("stock_officer_rewards"),
            },
            "market_structure": {
                "indexes": {"rows": self._count_rows("market_indexes")},
                "sectors": {"rows": self._count_rows("market_sectors")},
                "index_constituents": {"rows": self._count_rows("index_constituents")},
                "sector_constituents": {"rows": self._count_rows("sector_constituents")},
            },
            "sync": {
                "readiness": self.sync_readiness(),
                "jobs": self.list_jobs(10),
            },
        }

    def coverage(self) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT trade_date AS latest_trade_date
                    FROM analysis_daily_bars FORCE INDEX (idx_analysis_date_mode)
                    WHERE price_mode='forward_adjusted'
                    ORDER BY trade_date DESC
                    LIMIT 1
                    """
                )
                latest_trade_date_row = cursor.fetchone()
                latest_trade_date = latest_trade_date_row["latest_trade_date"] if latest_trade_date_row else None
                if latest_trade_date:
                    cursor.execute(
                        """
                        SELECT COUNT(DISTINCT symbol) AS symbol_count, COUNT(*) AS row_count
                        FROM analysis_daily_bars
                        WHERE trade_date=%s AND price_mode='forward_adjusted'
                        """,
                        (latest_trade_date,),
                    )
                    analysis = cursor.fetchone()
                    cursor.execute(
                        "SELECT COUNT(*) AS row_count FROM daily_indicators WHERE trade_date=%s",
                        (latest_trade_date,),
                    )
                    indicators = cursor.fetchone()
                    cursor.execute(
                        "SELECT COUNT(*) AS row_count FROM strategy_signals WHERE trade_date=%s",
                        (latest_trade_date,),
                    )
                    signals = cursor.fetchone()
                else:
                    analysis = {"symbol_count": 0, "row_count": 0}
                    indicators = {"row_count": 0}
                    signals = {"row_count": 0}
        return {
            "analysis_daily_bars": {
                "symbols": analysis["symbol_count"],
                "rows": analysis["row_count"],
                "latest_trade_date": str(latest_trade_date) if latest_trade_date else None,
                "scope": "latest_trade_date",
            },
            "daily_indicators": {"rows": indicators["row_count"], "scope": "latest_trade_date"},
            "strategy_signals": {"rows": signals["row_count"], "scope": "latest_trade_date"},
        }

    def sync_readiness(self) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT trade_date AS latest_trade_date
                    FROM analysis_daily_bars FORCE INDEX (idx_analysis_date_mode)
                    WHERE price_mode='forward_adjusted'
                    ORDER BY trade_date DESC
                    LIMIT 1
                    """
                )
                latest_trade_date_row = cursor.fetchone()
                latest_trade_date = latest_trade_date_row["latest_trade_date"] if latest_trade_date_row else None
                cursor.execute(
                    """
                    SELECT COUNT(*) AS expected_symbols
                    FROM stocks
                    WHERE is_active=1
                      AND symbol REGEXP '^[0-9]{6}\\.(SH|SZ|BJ)$'
                    """
                )
                expected_symbols = cursor.fetchone()["expected_symbols"]
                if latest_trade_date:
                    cursor.execute(
                        """
                        SELECT COUNT(DISTINCT adb.symbol) AS updated_symbols
                        FROM analysis_daily_bars adb
                        JOIN stocks s ON s.symbol=adb.symbol
                        WHERE adb.trade_date=%s
                          AND adb.price_mode='forward_adjusted'
                          AND s.is_active=1
                          AND s.symbol REGEXP '^[0-9]{6}\\.(SH|SZ|BJ)$'
                        """,
                        (latest_trade_date,),
                    )
                    updated_symbols = cursor.fetchone()["updated_symbols"]
                    cursor.execute(
                        """
                        SELECT s.symbol
                        FROM stocks s
                        LEFT JOIN analysis_daily_bars adb
                          ON adb.symbol=s.symbol
                         AND adb.trade_date=%s
                         AND adb.price_mode='forward_adjusted'
                        WHERE s.is_active=1
                          AND s.symbol REGEXP '^[0-9]{6}\\.(SH|SZ|BJ)$'
                          AND adb.symbol IS NULL
                        ORDER BY s.symbol
                        """,
                        (latest_trade_date,),
                    )
                    missing_symbols = [row["symbol"] for row in cursor.fetchall()]
                else:
                    updated_symbols = 0
                    cursor.execute(
                        """
                        SELECT symbol
                        FROM stocks
                        WHERE is_active=1
                          AND symbol REGEXP '^[0-9]{6}\\.(SH|SZ|BJ)$'
                        ORDER BY symbol
                        """
                    )
                    missing_symbols = [row["symbol"] for row in cursor.fetchall()]
                cursor.execute(
                    """
                    SELECT id
                    FROM sync_jobs
                    WHERE job_type='full_daily_pipeline'
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
                latest_job_id_row = cursor.fetchone()
                latest_job = self.get_job(latest_job_id_row["id"]) if latest_job_id_row else None
                failed_symbols: list[str] = []
                if latest_job:
                    cursor.execute(
                        """
                        SELECT DISTINCT symbol
                        FROM sync_job_items
                        WHERE job_id=%s AND status='failed' AND symbol IS NOT NULL
                        ORDER BY symbol
                        """,
                        (latest_job["id"],),
                    )
                    failed_symbols = [row["symbol"] for row in cursor.fetchall()]
        return {
            "latest_trade_date": str(latest_trade_date) if latest_trade_date else None,
            "expected_symbols": expected_symbols,
            "updated_symbols": updated_symbols,
            "missing_symbol_count": len(missing_symbols),
            "missing_symbols": missing_symbols[:100],
            "failed_symbol_count": len(failed_symbols),
            "failed_symbols": failed_symbols[:100],
            "latest_sync_job": latest_job,
            "ready_for_analysis": bool(expected_symbols) and not missing_symbols and not failed_symbols,
        }

    def create_job(self, job_type: str, requested_by: str, provider_priority: list[str]) -> dict:
        sql = """
            INSERT INTO sync_jobs (job_type, status, requested_by, provider_priority_json)
            VALUES (%s, 'pending', %s, %s)
        """
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (job_type, requested_by, json.dumps(provider_priority)))
                job_id = cursor.lastrowid
        return self.get_job(job_id)

    def mark_job_running(self, job_id: int) -> None:
        self._execute("UPDATE sync_jobs SET status='running', started_at=NOW() WHERE id=%s", (job_id,))

    def finish_job(self, job_id: int, status: str, summary: dict) -> dict:
        self._execute("UPDATE sync_jobs SET status=%s, summary_json=%s, finished_at=NOW() WHERE id=%s", (status, json.dumps(summary), job_id))
        return self.get_job(job_id)

    def add_item(self, job_id: int, item: dict) -> None:
        sql = """
            INSERT INTO sync_job_items (job_id, symbol, trade_date, date_start, date_end, status, provider, attempt_count, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._execute(
            sql,
            (
                job_id,
                item.get("symbol"),
                item.get("trade_date"),
                item.get("date_start"),
                item.get("date_end"),
                item.get("status"),
                item.get("provider"),
                item.get("attempt_count", 0),
                item.get("error_message"),
            ),
        )

    def get_job(self, job_id: int) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sync_jobs WHERE id=%s", (job_id,))
                row = cursor.fetchone()
        if not row:
            raise KeyError(job_id)
        row["provider_priority"] = json.loads(row.pop("provider_priority_json") or "[]")
        row["summary"] = json.loads(row.pop("summary_json") or "{}")
        return row

    def list_jobs(self, limit: int = 100) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sync_jobs ORDER BY id DESC LIMIT %s", (limit,))
                rows = cursor.fetchall()
        jobs = []
        for row in rows:
            row["provider_priority"] = json.loads(row.pop("provider_priority_json") or "[]")
            row["summary"] = json.loads(row.pop("summary_json") or "{}")
            jobs.append(row)
        return jobs

    def get_job_items(self, job_id: int) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sync_job_items WHERE job_id=%s ORDER BY id", (job_id,))
                return list(cursor.fetchall())

    def has_running_job(self, job_type: str) -> bool:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM sync_jobs WHERE job_type=%s AND status IN ('pending','running')", (job_type,))
                return cursor.fetchone()["count"] > 0

    def create_sync_request(
        self,
        request_type: str,
        dataset: str | None = None,
        scope: dict | None = None,
        priority: int = 50,
        requested_by: str = "api",
        reason: str | None = None,
    ) -> dict:
        sql = """
            INSERT INTO sync_requests (request_type, dataset, scope_json, priority, status, requested_by, reason)
            VALUES (%s, %s, %s, %s, 'pending', %s, %s)
        """
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        request_type,
                        dataset or request_type,
                        json.dumps(scope or {}),
                        int(priority),
                        requested_by,
                        reason,
                    ),
                )
                request_id = cursor.lastrowid
        return self.get_sync_request(request_id)

    def get_sync_request(self, request_id: int) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sync_requests WHERE id=%s", (request_id,))
                row = cursor.fetchone()
        if not row:
            raise KeyError(request_id)
        row["scope"] = json.loads(row.pop("scope_json") or "{}")
        return row

    def list_sync_requests(self, limit: int = 100) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM sync_requests
                    ORDER BY FIELD(status, 'pending', 'claimed', 'failed', 'completed', 'cancelled'), priority DESC, id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
        requests = []
        for row in rows:
            row["scope"] = json.loads(row.pop("scope_json") or "{}")
            requests.append(row)
        return requests

    def claim_sync_request(self, request_id: int) -> dict:
        self._execute(
            "UPDATE sync_requests SET status='claimed', claimed_at=NOW() WHERE id=%s AND status='pending'",
            (request_id,),
        )
        return self.get_sync_request(request_id)

    def finish_sync_request(self, request_id: int, status: str, error_message: str | None = None) -> dict:
        self._execute(
            "UPDATE sync_requests SET status=%s, error_message=%s, finished_at=NOW() WHERE id=%s",
            (status, error_message, request_id),
        )
        return self.get_sync_request(request_id)

    def recover_claimed_sync_requests(self) -> int:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sync_requests SET status='pending', claimed_at=NULL WHERE status='claimed'")
                return int(cursor.rowcount)

    def upsert_dataset_freshness(
        self,
        dataset: str,
        scope_key: str = "global",
        status: str = "missing",
        latest_data_date: str | None = None,
        rows: int = 0,
        missing_count: int = 0,
        failed_count: int = 0,
        owner_job_type: str | None = None,
        summary: dict | None = None,
    ) -> dict:
        sql = """
            INSERT INTO dataset_freshness
                (dataset, scope_key, latest_data_date, last_success_at, last_attempt_at, status,
                 rows_count, missing_count, failed_count, owner_job_type, summary_json)
            VALUES (%s, %s, %s, IF(%s='ready', NOW(), NULL), NOW(), %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                latest_data_date=VALUES(latest_data_date),
                last_success_at=IF(VALUES(status)='ready', NOW(), last_success_at),
                last_attempt_at=NOW(),
                status=VALUES(status),
                rows_count=VALUES(rows_count),
                missing_count=VALUES(missing_count),
                failed_count=VALUES(failed_count),
                owner_job_type=VALUES(owner_job_type),
                summary_json=VALUES(summary_json)
        """
        self._execute(
            sql,
            (
                dataset,
                scope_key,
                latest_data_date,
                status,
                status,
                int(rows),
                int(missing_count),
                int(failed_count),
                owner_job_type,
                json.dumps(summary or {}),
            ),
        )
        return self.get_dataset_freshness(dataset, scope_key)

    def get_dataset_freshness(self, dataset: str, scope_key: str = "global") -> dict | None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM dataset_freshness WHERE dataset=%s AND scope_key=%s",
                    (dataset, scope_key),
                )
                row = cursor.fetchone()
        if not row:
            return None
        row["rows"] = row.pop("rows_count")
        row["summary"] = json.loads(row.pop("summary_json") or "{}")
        return row

    def list_symbols_missing_enterprise_data(self, limit: int = 100, excluded_symbols: set[str] | list[str] | None = None) -> list[str]:
        excluded = sorted({str(symbol) for symbol in (excluded_symbols or []) if symbol})
        ttl_days = max(0, int(getattr(self.settings, "enterprise_refresh_ttl_days", 7)))
        excluded_sql = ""
        params: list[Any] = []
        if excluded:
            excluded_sql = f"AND s.symbol NOT IN ({','.join(['%s'] * len(excluded))})"
            params.extend(excluded)
        params.append(max(0, int(limit)))
        sql = f"""
            SELECT s.symbol
            FROM stocks s
            LEFT JOIN (
                SELECT symbol, COUNT(*) AS rows_count FROM stock_company_profiles GROUP BY symbol
            ) company_profiles ON company_profiles.symbol = s.symbol
            LEFT JOIN (
                SELECT symbol, COUNT(*) AS rows_count FROM stock_top10_holders GROUP BY symbol
            ) holders ON holders.symbol = s.symbol
            LEFT JOIN (
                SELECT symbol, COUNT(*) AS rows_count FROM stock_company_officers GROUP BY symbol
            ) officers ON officers.symbol = s.symbol
            LEFT JOIN (
                SELECT symbol, COUNT(*) AS rows_count FROM stock_officer_rewards GROUP BY symbol
            ) officer_rewards ON officer_rewards.symbol = s.symbol
            LEFT JOIN dataset_freshness research_attempt
                ON research_attempt.dataset = 'stock_research_context'
                AND research_attempt.scope_key = s.symbol
                AND research_attempt.last_attempt_at >= NOW() - INTERVAL {ttl_days} DAY
            WHERE COALESCE(s.is_active, 1) = 1
              {excluded_sql}
              AND research_attempt.scope_key IS NULL
              AND (
                COALESCE(company_profiles.rows_count, 0) = 0
                OR COALESCE(holders.rows_count, 0) = 0
                OR COALESCE(officers.rows_count, 0) = 0
                OR COALESCE(officer_rewards.rows_count, 0) = 0
              )
            ORDER BY
                COALESCE(officers.rows_count, 0) ASC,
                COALESCE(holders.rows_count, 0) ASC,
                COALESCE(officer_rewards.rows_count, 0) ASC,
                s.symbol ASC
            LIMIT %s
        """
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return [row["symbol"] for row in cursor.fetchall()]

    def create_screening_run(self, strategy_key: str, trade_date: str, universe: list[str], filters: dict) -> dict:
        sql = """
            INSERT INTO screening_runs (strategy_key, trade_date, universe_json, filters_json, status)
            VALUES (%s, %s, %s, %s, 'running')
        """
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (strategy_key, trade_date, json.dumps(universe), json.dumps(filters)))
                run_id = cursor.lastrowid
        return self.get_screening_run(run_id)

    def finish_screening_run(self, run_id: int, summary: dict, results: list[dict]) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE screening_runs SET status='completed', summary_json=%s, finished_at=NOW() WHERE id=%s",
                    (json.dumps(summary), run_id),
                )
                cursor.execute("DELETE FROM screening_results WHERE run_id=%s", (run_id,))
                cursor.executemany(
                    """
                    INSERT INTO screening_results
                        (run_id, symbol, trade_date, close, expma17, expma50, selected_signal, trend_state, score, reason_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            run_id,
                            row["symbol"],
                            row["trade_date"],
                            row["close"],
                            row.get("expma17"),
                            row.get("expma50"),
                            row.get("selected_signal") or row.get("signal"),
                            row.get("trend_state", ""),
                            row.get("score"),
                            json.dumps(row.get("reason", row.get("reason_json", {}))),
                        )
                        for row in results
                    ],
                )
        return self.get_screening_run(run_id)

    def get_screening_run(self, run_id: int) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM screening_runs WHERE id=%s", (run_id,))
                row = cursor.fetchone()
        if not row:
            raise KeyError(run_id)
        row["universe"] = json.loads(row.pop("universe_json") or "[]")
        row["filters"] = json.loads(row.pop("filters_json") or "{}")
        row["summary"] = json.loads(row.pop("summary_json") or "{}")
        return row

    def get_screening_results(self, run_id: int) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM screening_results WHERE run_id=%s ORDER BY symbol", (run_id,))
                rows = []
                for row in cursor.fetchall():
                    decoded = _numbers(dict(row))
                    decoded["reason"] = json.loads(decoded.pop("reason_json") or "{}")
                    rows.append(decoded)
                return rows

    def create_backtest_run(
        self,
        strategy_key: str,
        symbols: list[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
        fee_rate: float,
        slippage_rate: float,
        price_mode: str,
        allow_partial_coverage: bool,
    ) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO backtest_runs
                        (strategy_key, symbols_json, start_date, end_date, initial_capital, fee_rate, slippage_rate,
                         price_mode, status, allow_partial_coverage)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'running', %s)
                    """,
                    (
                        strategy_key,
                        json.dumps(symbols),
                        start_date,
                        end_date,
                        initial_capital,
                        fee_rate,
                        slippage_rate,
                        price_mode,
                        allow_partial_coverage,
                    ),
                )
                run_id = cursor.lastrowid
        return self.get_backtest_run(run_id, include_details=False)

    def finish_backtest_run(self, run_id: int, summary: dict, coverage: dict, trades: list[dict], equity: list[dict]) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE backtest_runs SET status='completed', summary_json=%s, coverage_json=%s, finished_at=NOW() WHERE id=%s",
                    (json.dumps(summary), json.dumps(coverage), run_id),
                )
                cursor.execute("DELETE FROM backtest_trades WHERE run_id=%s", (run_id,))
                cursor.execute("DELETE FROM backtest_equity WHERE run_id=%s", (run_id,))
                cursor.executemany(
                    """
                    INSERT INTO backtest_trades
                        (run_id, symbol, signal_date, execution_date, `signal`, `action`, price, quantity, fee,
                         slippage, position_before, position_after, is_filled)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            run_id,
                            trade["symbol"],
                            trade["signal_date"],
                            trade.get("trade_date") or trade.get("execution_date"),
                            trade["signal"],
                            trade.get("side") or trade.get("action", ""),
                            trade.get("price"),
                            trade.get("quantity"),
                            trade.get("cost", trade.get("fee", 0)),
                            trade.get("slippage", 0),
                            trade.get("position_before", 0),
                            trade.get("target_position", trade.get("position_after", 0)),
                            trade.get("is_filled", True),
                        )
                        for trade in trades
                    ],
                )
                cursor.executemany(
                    """
                    INSERT INTO backtest_equity (run_id, trade_date, equity, cash, market_value, drawdown, positions_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            run_id,
                            row["trade_date"],
                            row["equity"],
                            row.get("cash", 0),
                            row.get("market_value", row["equity"] - row.get("cash", 0)),
                            row.get("drawdown", 0),
                            json.dumps(row.get("positions", row.get("positions_json", {}))),
                        )
                        for row in equity
                    ],
                )
        return self.get_backtest_run(run_id)

    def get_backtest_run(self, run_id: int, include_details: bool = True) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM backtest_runs WHERE id=%s", (run_id,))
                row = cursor.fetchone()
                if not row:
                    raise KeyError(run_id)
                run = _numbers(dict(row))
                run["symbols"] = json.loads(run.pop("symbols_json") or "[]")
                run["summary"] = json.loads(run.pop("summary_json") or "{}")
                run["coverage"] = json.loads(run.pop("coverage_json") or "{}")
                if include_details:
                    cursor.execute("SELECT * FROM backtest_trades WHERE run_id=%s ORDER BY id", (run_id,))
                    run["trades"] = [_numbers(dict(item)) for item in cursor.fetchall()]
                    cursor.execute("SELECT * FROM backtest_equity WHERE run_id=%s ORDER BY trade_date", (run_id,))
                    equity_rows = []
                    for item in cursor.fetchall():
                        decoded = _numbers(dict(item))
                        decoded["positions"] = json.loads(decoded.pop("positions_json") or "{}")
                        equity_rows.append(decoded)
                    run["equity"] = equity_rows
                return run

    def list_backtest_runs(self) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM backtest_runs ORDER BY id DESC")
                ids = [row["id"] for row in cursor.fetchall()]
        return [self.get_backtest_run(run_id, include_details=False) for run_id in ids]

    def _executemany(self, sql: str, values: Iterable[tuple]) -> None:
        values = list(values)
        if not values:
            return
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql, values)

    def _execute(self, sql: str, values: tuple) -> None:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)

    def _select_rows(self, sql: str, values: tuple = ()) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                return [_json_ready(_numbers(dict(row))) for row in cursor.fetchall()]

    def _select_symbol_rows(self, table: str, symbol: str, order_by: str) -> list[dict]:
        return self._select_rows(f"SELECT * FROM {table} WHERE symbol=%s ORDER BY {order_by}", (symbol,))

    def _first_symbol_row(self, table: str, symbol: str) -> dict | None:
        rows = self._select_rows(f"SELECT * FROM {table} WHERE symbol=%s LIMIT 1", (symbol,))
        return rows[0] if rows else None

    def _count_rows(self, table: str) -> int:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) AS rows_count FROM {table}")
                return int(cursor.fetchone()["rows_count"])

    def _count_symbols_and_rows(self, table: str) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(DISTINCT symbol) AS symbols, COUNT(*) AS rows_count FROM {table}")
                row = cursor.fetchone()
        return {"symbols": int(row["symbols"]), "rows": int(row["rows_count"])}


def _json_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _decode_analysis_row(row: dict) -> dict:
    decoded = _numbers(dict(row))
    decoded["signal"] = decoded.get("selected_signal")
    decoded["raw_flags"] = json.loads(decoded.pop("raw_flags_json") or "{}")
    return decoded


def _numbers(row: dict) -> dict:
    for key, value in list(row.items()):
        if key.endswith("id") or key in {"id", "run_id", "job_id"}:
            continue
        if hasattr(value, "__float__"):
            row[key] = float(value)
    return row


def _json_ready(row: dict) -> dict:
    for key, value in list(row.items()):
        if hasattr(value, "isoformat"):
            row[key] = value.isoformat()
    return row


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SZ"):
        return "SZ"
    if symbol.endswith(".SH"):
        return "SH"
    return "UNKNOWN"
