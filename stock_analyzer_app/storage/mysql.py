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
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM strategy_signals WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM daily_indicators WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM analysis_daily_bars WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM stock_daily_status WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM adjustment_factors WHERE symbol IN ({placeholders})", symbols)
                cursor.execute(f"DELETE FROM daily_bars WHERE symbol IN ({placeholders})", symbols)
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
        return self.analysis_bars_with_signals([symbol], "0001-01-01", "9999-12-31", price_mode).get(symbol, [])

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

    def coverage(self) -> dict:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT symbol) AS symbol_count, COUNT(*) AS row_count FROM analysis_daily_bars")
                analysis = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) AS row_count FROM daily_indicators")
                indicators = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) AS row_count FROM strategy_signals")
                signals = cursor.fetchone()
        return {
            "analysis_daily_bars": {"symbols": analysis["symbol_count"], "rows": analysis["row_count"]},
            "daily_indicators": {"rows": indicators["row_count"]},
            "strategy_signals": {"rows": signals["row_count"]},
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

    def list_jobs(self) -> list[dict]:
        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM sync_jobs ORDER BY id DESC")
                ids = [row["id"] for row in cursor.fetchall()]
        return [self.get_job(job_id) for job_id in ids]

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


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SZ"):
        return "SZ"
    if symbol.endswith(".SH"):
        return "SH"
    return "UNKNOWN"
