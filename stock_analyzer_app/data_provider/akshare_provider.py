class AkShareProvider:
    name = "akshare"

    def __init__(self, module="auto") -> None:
        self.module = _optional_import("akshare") if module == "auto" else module

    def _ak(self):
        if self.module is None:
            raise RuntimeError("AkShare is not installed. Install akshare to use the AkShare/Eastmoney fallback provider.")
        return self.module

    def fetch_stock_universe(self) -> list[dict]:
        rows = self._ak().stock_info_a_code_name()
        output = []
        for row in _records(rows):
            code = str(row.get("code") or row.get("证券代码") or row.get("代码"))
            name = row.get("name") or row.get("证券简称") or row.get("名称") or code
            output.append(
                {
                    "symbol": _symbol(code),
                    "exchange": _exchange(code),
                    "name": name,
                    "industry": None,
                    "is_active": True,
                    "is_st": "ST" in str(name).upper(),
                    "source": self.name,
                }
            )
        return output

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        rows = self._ak().tool_trade_date_hist_sina()
        return [
            {"exchange": exchange, "trade_date": str(row.get("trade_date") or row.get("交易日"))[:10], "is_open": True}
            for row in _records(rows)
            if start_date <= str(row.get("trade_date") or row.get("交易日"))[:10] <= end_date
        ]

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        code = symbol.split(".")[0]
        rows = self._ak().stock_zh_a_hist(symbol=code, period="daily", start_date=_compact(start_date), end_date=_compact(end_date), adjust="")
        output = []
        for row in _records(rows):
            output.append(
                {
                    "symbol": _symbol(code),
                    "trade_date": str(row.get("日期"))[:10],
                    "open": row.get("开盘"),
                    "high": row.get("最高"),
                    "low": row.get("最低"),
                    "close": row.get("收盘"),
                    "volume": row.get("成交量", 0),
                    "amount": row.get("成交额", 0),
                    "source": self.name,
                    "is_adjusted": False,
                }
            )
        return output

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        code = symbol.split(".")[0]
        raw_rows = self._ak().stock_zh_a_hist(symbol=code, period="daily", start_date=_compact(start_date), end_date=_compact(end_date), adjust="")
        adjusted_rows = self._ak().stock_zh_a_hist(symbol=code, period="daily", start_date=_compact(start_date), end_date=_compact(end_date), adjust="qfq")
        raw_close_by_date = {
            _trade_date(row): _number(_field(row, "close"))
            for row in _records(raw_rows)
        }
        output = []
        for row in _records(adjusted_rows):
            trade_date = _trade_date(row)
            raw_close = raw_close_by_date.get(trade_date)
            adjusted_close = _number(_field(row, "close"))
            if not trade_date or raw_close in (None, 0) or adjusted_close is None:
                continue
            output.append(
                {
                    "symbol": _symbol(code),
                    "trade_date": trade_date,
                    "adj_factor": adjusted_close / raw_close,
                    "source": self.name,
                }
            )
        return output

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        st_codes = _codes_from_rows(self._ak().stock_zh_a_st_em()) if hasattr(self._ak(), "stock_zh_a_st_em") else set()
        suspended_codes = set()
        if hasattr(self._ak(), "stock_tfp_em"):
            suspended_codes = _codes_from_rows(self._ak().stock_tfp_em(date=_compact(trade_date)))
        return [
            {
                "symbol": symbol,
                "trade_date": trade_date,
                "is_st": symbol.split(".")[0] in st_codes,
                "is_suspended": symbol.split(".")[0] in suspended_codes,
            }
            for symbol in symbols
        ]


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


def _symbol(code: str) -> str:
    suffix = "SH" if code.startswith("6") else "SZ"
    return f"{code}.{suffix}"


def _exchange(code: str) -> str:
    return "SH" if code.startswith("6") else "SZ"


def _field(row: dict, field: str):
    columns = {
        "date": ("日期", "trade_date", "date", "鏃ユ湡"),
        "close": ("收盘", "close", "鏀剁洏"),
    }
    for column in columns[field]:
        if column in row:
            return row[column]
    return None


def _trade_date(row: dict) -> str:
    value = _field(row, "date")
    if value is None:
        return ""
    return str(value)[:10]


def _number(value):
    if value in (None, ""):
        return None
    return float(value)


def _codes_from_rows(rows) -> set[str]:
    codes = set()
    for row in _records(rows):
        value = row.get("代码") or row.get("code") or row.get("证券代码") or row.get("股票代码") or row.get("浠ｇ爜")
        if value not in (None, ""):
            codes.add(str(value).split(".")[0].zfill(6))
    return codes
