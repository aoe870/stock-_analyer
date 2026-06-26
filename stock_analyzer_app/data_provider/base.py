from typing import Protocol


class StockDataProvider(Protocol):
    name: str

    def fetch_stock_universe(self) -> list[dict]:
        raise NotImplementedError

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        raise NotImplementedError

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        raise NotImplementedError

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        raise NotImplementedError

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        raise NotImplementedError

