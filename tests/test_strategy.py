from stock_analyzer_app.strategies import compute_expma_signals, select_signal


def bars_from_closes(closes):
    return [
        {
            "symbol": "TEST",
            "trade_date": f"2024-01-{index + 1:02d}",
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": 1000,
            "amount": close * 1000,
            "source": "unit",
            "is_adjusted": True,
        }
        for index, close in enumerate(closes)
    ]


def signal_rows(closes):
    return compute_expma_signals(bars_from_closes(closes), short=2, long=4, warmup=0)


def selected_signals(closes):
    return [row["signal"] for row in signal_rows(closes)]


def test_select_signal_uses_documented_priority():
    flags = {
        "buy": True,
        "half_sell": True,
        "re_buy": True,
        "clear_1": True,
        "clear_2": True,
        "re_buy_50": True,
    }

    assert select_signal(flags) == "CLEAR_2"

    flags["clear_2"] = False
    assert select_signal(flags) == "CLEAR_1"

    flags["clear_1"] = False
    assert select_signal(flags) == "HALF_SELL"


def test_buy_requires_short_expma_crossing_above_long_expma():
    signals = selected_signals([10, 9, 8, 14])

    assert signals[-1] == "BUY"


def test_half_sell_requires_close_crossing_below_expma17_while_trend_up():
    signals = selected_signals([10, 9, 8, 14, 11])

    assert signals[-1] == "HALF_SELL"


def test_re_buy_requires_close_crossing_back_above_expma17_and_expma50():
    signals = selected_signals([10, 9, 8, 14, 10, 11])

    assert signals[-1] == "RE_BUY"


def test_clear_1_requires_close_below_expma50_while_short_above_long():
    signals = selected_signals([10, 9, 8, 14, 10])

    assert signals[-1] == "CLEAR_1"


def test_clear_2_requires_long_expma_crossing_above_short_expma():
    signals = selected_signals([10, 9, 8, 14, 7])

    assert signals[-1] == "CLEAR_2"


def test_re_buy_50_requires_close_crossing_back_above_expma50():
    signals = selected_signals([10, 9, 8, 14, 15, 11, 12])

    assert signals[-1] == "RE_BUY_50"


def test_warmup_suppresses_tradable_signal_but_keeps_diagnostics():
    rows = compute_expma_signals(bars_from_closes([10, 9, 8, 14]), short=2, long=4, warmup=10)

    assert rows[-1]["raw_flags"]["buy"] is True
    assert rows[-1]["signal"] is None
    assert rows[-1]["expma17"] is not None
    assert rows[-1]["expma50"] is not None
