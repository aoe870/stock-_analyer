class TushareProvider:
    name = "tushare"

    def __init__(self, token: str, module=None) -> None:
        self.token = token
        self.module = module if module is not None else _optional_import("tushare")

    def _pro(self):
        if self.module is None:
            raise RuntimeError("Tushare is not installed. Install tushare and configure STOCK_ANALYZER_TUSHARE_TOKEN.")
        if not self.token:
            raise RuntimeError("STOCK_ANALYZER_TUSHARE_TOKEN is required for Tushare.")
        self.module.set_token(self.token)
        return self.module.pro_api()

    def fetch_stock_universe(self) -> list[dict]:
        rows = self._pro().stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,list_date")
        return [
            {
                "symbol": row["ts_code"],
                "exchange": row["ts_code"].split(".")[-1],
                "name": row["name"],
                "industry": row.get("industry"),
                "list_date": _date(row.get("list_date")),
                "is_active": True,
                "is_st": "ST" in row.get("name", "").upper(),
                "source": self.name,
            }
            for row in _records(rows)
        ]

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        rows = self._pro().trade_cal(exchange=exchange, start_date=_compact(start_date), end_date=_compact(end_date))
        return [
            {"exchange": exchange, "trade_date": _date(row["cal_date"]), "is_open": bool(int(row["is_open"]))}
            for row in _records(rows)
        ]

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        rows = self._pro().daily(ts_code=symbol, start_date=_compact(start_date), end_date=_compact(end_date))
        return [
            {
                "symbol": row["ts_code"],
                "trade_date": _date(row["trade_date"]),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row.get("vol", 0),
                "amount": row.get("amount", 0),
                "source": self.name,
                "is_adjusted": False,
            }
            for row in _records(rows)
        ]

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        rows = self._pro().adj_factor(ts_code=symbol, start_date=_compact(start_date), end_date=_compact(end_date))
        return [
            {"symbol": row["ts_code"], "trade_date": _date(row["trade_date"]), "adj_factor": row["adj_factor"], "source": self.name}
            for row in _records(rows)
        ]

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False} for symbol in symbols]


def _optional_import(name: str):
    try:
        return __import__(name)
    except ImportError:
        return None


def _records(frame):
    if hasattr(frame, "to_dict"):
        return frame.to_dict("records")
    return list(frame or [])


def _compact(value: str) -> str:
    return value.replace("-", "")


def _date(value) -> str | None:
    if value in (None, ""):
        return None
    text = str(value)
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return text

