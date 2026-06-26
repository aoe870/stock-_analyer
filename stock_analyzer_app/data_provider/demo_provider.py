from datetime import date, timedelta


class DemoAshareProvider:
    name = "demo"

    def fetch_stock_universe(self) -> list[dict]:
        return [{"symbol": "DEMO001.SZ", "exchange": "SZ", "name": "Demo One", "industry": "Demo", "source": self.name}]

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        rows = []
        current = start
        previous_open = None
        while current <= end:
            is_open = current.weekday() < 5
            rows.append(
                {
                    "exchange": exchange,
                    "trade_date": current.isoformat(),
                    "is_open": is_open,
                    "previous_trade_date": previous_open,
                    "next_trade_date": None,
                }
            )
            if is_open:
                previous_open = current.isoformat()
            current += timedelta(days=1)
        return rows

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        closes = [10] * 70 + [9] * 20 + [15] * 25 + [13, 14, 15, 16]
        start = date.fromisoformat(start_date)
        rows = []
        for index, close in enumerate(closes):
            trade_date = (start + timedelta(days=index)).isoformat()
            if trade_date > end_date:
                break
            rows.append(
                {
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "open": close,
                    "high": close + 1,
                    "low": close - 1,
                    "close": close,
                    "volume": 100000 + index,
                    "amount": close * (100000 + index),
                    "source": self.name,
                    "is_adjusted": False,
                }
            )
        return rows

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return [
            {"symbol": symbol, "trade_date": row["trade_date"], "adj_factor": 1.0, "source": self.name}
            for row in self.fetch_daily_bars(symbol, start_date, end_date)
        ]

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]
