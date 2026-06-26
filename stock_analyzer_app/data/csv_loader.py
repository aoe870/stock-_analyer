import csv
from datetime import datetime
from io import StringIO


HEADER_MAP = {
    "symbol": "symbol",
    "代码": "symbol",
    "证券代码": "symbol",
    "trade_date": "trade_date",
    "date": "trade_date",
    "日期": "trade_date",
    "交易日期": "trade_date",
    "open": "open",
    "开盘": "open",
    "开盘价": "open",
    "high": "high",
    "最高": "high",
    "最高价": "high",
    "low": "low",
    "最低": "low",
    "最低价": "low",
    "close": "close",
    "收盘": "close",
    "收盘价": "close",
    "volume": "volume",
    "成交量": "volume",
    "amount": "amount",
    "成交额": "amount",
}

REQUIRED = ("symbol", "trade_date", "open", "high", "low", "close", "volume", "amount")


def parse_ohlcv_csv(text: str, default_symbol: str | None = None) -> list[dict]:
    reader = csv.DictReader(StringIO(text.strip()))
    if not reader.fieldnames:
        return []

    normalized_headers = {header: HEADER_MAP.get(header.strip(), header.strip()) for header in reader.fieldnames}
    rows: list[dict] = []
    for raw in reader:
        row = {normalized_headers[key]: value for key, value in raw.items() if key is not None}
        if default_symbol and not row.get("symbol"):
            row["symbol"] = default_symbol
        missing = [field for field in REQUIRED if not row.get(field)]
        if missing:
            raise ValueError(f"missing required CSV fields: {', '.join(missing)}")

        rows.append(
            {
                "symbol": str(row["symbol"]).strip(),
                "trade_date": _normalize_date(str(row["trade_date"]).strip()),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "amount": float(row["amount"]),
                "source": "csv",
                "is_adjusted": False,
            }
        )
    return sorted(rows, key=lambda item: (item["symbol"], item["trade_date"]))


def _normalize_date(value: str) -> str:
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"unsupported date format: {value}")

