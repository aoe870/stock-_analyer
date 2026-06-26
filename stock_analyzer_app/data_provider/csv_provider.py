from pathlib import Path

from stock_analyzer_app.data.csv_loader import parse_ohlcv_csv


class CsvRepairProvider:
    name = "csv"

    def __init__(self, daily_bar_files: dict[str, Path] | None = None) -> None:
        self.daily_bar_files = daily_bar_files or {}

    def fetch_stock_universe(self) -> list[dict]:
        return [{"symbol": symbol, "source": self.name} for symbol in sorted(self.daily_bar_files)]

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        return []

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        path = self.daily_bar_files[symbol]
        return [
            row
            for row in parse_ohlcv_csv(path.read_text(encoding="utf-8"), default_symbol=symbol)
            if start_date <= row["trade_date"] <= end_date
        ]

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return []

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]

