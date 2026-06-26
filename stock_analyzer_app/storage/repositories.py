from stock_analyzer_app.aggregation.daily import materialize_expma_analysis
from stock_analyzer_app.data.sample import sample_symbol_bars


class InMemoryAnalysisRepository:
    def __init__(self, symbol_bars: dict[str, list[dict]] | None = None) -> None:
        self.symbol_bars = symbol_bars or sample_symbol_bars()
        self.rows = self._build_rows(self.symbol_bars)

    def list_stocks(self) -> list[dict]:
        return [
            {
                "symbol": symbol,
                "name": rows[0].get("name", ""),
                "exchange": _exchange_from_symbol(symbol),
                "is_active": True,
                "is_st": False,
                "source": rows[0].get("source", "local"),
            }
            for symbol, rows in sorted(self.symbol_bars.items())
            if rows
        ]

    def get_stock(self, symbol: str) -> dict | None:
        for row in self.list_stocks():
            if row["symbol"] == symbol:
                return row
        return None

    def latest_screening_rows(self, trade_date: str, symbols: list[str] | None = None, price_mode: str = "forward_adjusted"):
        output = []
        for symbol in symbols or sorted(self.rows):
            candidates = [
                row
                for row in self.rows.get(symbol, [])
                if row["trade_date"] <= trade_date and row.get("price_mode", price_mode) == price_mode
            ]
            if candidates:
                output.append(candidates[-1])
        return output

    def analysis_bars_with_signals(self, symbols: list[str], start_date: str, end_date: str, price_mode: str = "forward_adjusted"):
        return {
            symbol: [
                row
                for row in self.rows.get(symbol, [])
                if start_date <= row["trade_date"] <= end_date and row.get("price_mode", price_mode) == price_mode
            ]
            for symbol in symbols
        }

    def bars(self, symbol: str, price_mode: str = "forward_adjusted") -> list[dict]:
        return [row for row in self.rows.get(symbol, []) if row.get("price_mode", price_mode) == price_mode]

    def indicators(self, symbol: str) -> list[dict]:
        return [
            {
                "symbol": row["symbol"],
                "trade_date": row["trade_date"],
                "strategy_key": "expma_17_50",
                "expma17": row.get("expma17"),
                "expma50": row.get("expma50"),
                "cross_price": row.get("cross_price"),
                "cross_in_kline": row.get("cross_in_kline", False),
                "warmup_ready": row.get("warmup_ready", False),
            }
            for row in self.rows.get(symbol, [])
        ]

    def signals(self, symbol: str) -> list[dict]:
        return [
            {
                "symbol": row["symbol"],
                "trade_date": row["trade_date"],
                "strategy_key": "expma_17_50",
                "selected_signal": row.get("selected_signal") or row.get("signal"),
                "raw_flags": row.get("raw_flags", {}),
                "trend_state": row.get("trend_state", ""),
            }
            for row in self.rows.get(symbol, [])
            if (row.get("selected_signal") or row.get("signal") or any(row.get("raw_flags", {}).values()))
        ]

    def _build_rows(self, symbol_bars: dict[str, list[dict]]) -> dict[str, list[dict]]:
        output = {}
        for symbol, bars in symbol_bars.items():
            normalized = []
            for row in bars:
                normalized.append(
                    {
                        **row,
                        "price_mode": row.get("price_mode", "forward_adjusted"),
                        "data_quality": row.get("data_quality", "ok"),
                        "selected_signal": row.get("selected_signal") or row.get("signal"),
                    }
                )
            materialized = materialize_expma_analysis(normalized, warmup=0)
            by_date = {row["trade_date"]: dict(row) for row in normalized}
            for indicator in materialized["indicators"]:
                by_date[indicator["trade_date"]].update(indicator)
            for signal in materialized["signals"]:
                target = by_date[signal["trade_date"]]
                target["selected_signal"] = signal["selected_signal"]
                target["signal"] = signal["selected_signal"]
                target["trend_state"] = signal["trend_state"]
                target["raw_flags"] = __import__("json").loads(signal["raw_flags_json"])
            output[symbol] = [by_date[date] for date in sorted(by_date)]
        return output


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SZ") or symbol.startswith(("0", "3")):
        return "SZ"
    if symbol.endswith(".SH") or symbol.startswith("6"):
        return "SH"
    return "LOCAL"

