from stock_analyzer_app.data.csv_loader import parse_ohlcv_csv


def test_parse_ohlcv_csv_normalizes_english_headers():
    rows = parse_ohlcv_csv(
        """symbol,trade_date,open,high,low,close,volume,amount
AAA,2024-01-02,10,12,9,11,1000,11000
"""
    )

    assert rows == [
        {
            "symbol": "AAA",
            "trade_date": "2024-01-02",
            "open": 10.0,
            "high": 12.0,
            "low": 9.0,
            "close": 11.0,
            "volume": 1000.0,
            "amount": 11000.0,
            "source": "csv",
            "is_adjusted": False,
        }
    ]


def test_parse_ohlcv_csv_normalizes_chinese_headers_and_default_symbol():
    rows = parse_ohlcv_csv(
        """日期,开盘,最高,最低,收盘,成交量,成交额
2024/01/02,10,12,9,11,1000,11000
""",
        default_symbol="BBB",
    )

    assert rows[0]["symbol"] == "BBB"
    assert rows[0]["trade_date"] == "2024-01-02"
    assert rows[0]["open"] == 10.0
    assert rows[0]["amount"] == 11000.0

