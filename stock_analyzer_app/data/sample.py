from stock_analyzer_app.strategy import compute_expma_signals


def sample_symbol_bars() -> dict[str, list[dict]]:
    symbols = {
        "SAMPLE1": ("趋势样本一", [10, 9, 8, 14, 11, 12, 13, 15, 14, 16, 18, 17, 19]),
        "SAMPLE2": ("趋势样本二", [20, 19, 18, 17, 21, 23, 22, 20, 24, 25, 23, 26, 27]),
        "SAMPLE3": ("回撤样本三", [8, 8.5, 8.2, 9, 9.5, 10, 9.2, 8.8, 9.7, 10.4, 10, 11, 10.5]),
    }
    output: dict[str, list[dict]] = {}
    for symbol, (name, closes) in symbols.items():
        bars = []
        for index, close in enumerate(closes):
            bars.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "trade_date": f"2024-01-{index + 1:02d}",
                    "open": float(close) * 0.99,
                    "high": float(close) * 1.03,
                    "low": float(close) * 0.97,
                    "close": float(close),
                    "volume": 100000 + index * 1000,
                    "amount": float(close) * (100000 + index * 1000),
                    "source": "sample",
                    "is_adjusted": True,
                }
            )
        output[symbol] = compute_expma_signals(bars, warmup=0)
    return output

