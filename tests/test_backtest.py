import pytest

from stock_analyzer_app.backtest import run_backtest


def make_bars(symbol, rows):
    return [
        {
            "symbol": symbol,
            "trade_date": date,
            "open": open_price,
            "high": max(open_price, close_price),
            "low": min(open_price, close_price),
            "close": close_price,
            "volume": 1000,
            "amount": close_price * 1000,
            "signal": signal,
            "source": "unit",
            "is_adjusted": True,
        }
        for date, open_price, close_price, signal in rows
    ]


def test_backtest_executes_signal_on_next_trading_day_open():
    bars = make_bars(
        "AAA",
        [
            ("2024-01-01", 10, 10, "BUY"),
            ("2024-01-02", 11, 12, None),
            ("2024-01-03", 13, 13, None),
        ],
    )

    result = run_backtest({"AAA": bars}, initial_capital=1000, fee_rate=0, slippage_rate=0)

    assert result["trades"][0]["trade_date"] == "2024-01-02"
    assert result["trades"][0]["price"] == pytest.approx(11)
    assert result["trades"][0]["target_position"] == pytest.approx(1.0)
    assert result["equity"][-1]["equity"] == pytest.approx(1000 / 11 * 13)


def test_backtest_applies_position_transitions_and_costs():
    bars = make_bars(
        "AAA",
        [
            ("2024-01-01", 10, 10, "BUY"),
            ("2024-01-02", 10, 10, "HALF_SELL"),
            ("2024-01-03", 12, 12, "RE_BUY"),
            ("2024-01-04", 8, 8, "CLEAR_1"),
            ("2024-01-05", 9, 9, "RE_BUY_50"),
            ("2024-01-06", 10, 10, "CLEAR_2"),
            ("2024-01-07", 11, 11, None),
        ],
    )

    result = run_backtest({"AAA": bars}, initial_capital=1000, fee_rate=0.001, slippage_rate=0.01)

    assert [trade["target_position"] for trade in result["trades"]] == [1.0, 0.5, 1.0, 0.0, 1.0, 0.0]
    assert result["trades"][0]["price"] == pytest.approx(10 * 1.01)
    assert result["trades"][3]["price"] == pytest.approx(9 * 0.99)
    assert all(trade["cost"] > 0 for trade in result["trades"])
    assert result["summary"]["trade_count"] == 6


def test_backtest_records_unfilled_signal_when_no_next_bar_exists():
    bars = make_bars(
        "AAA",
        [
            ("2024-01-01", 10, 10, None),
            ("2024-01-02", 11, 11, "BUY"),
        ],
    )

    result = run_backtest({"AAA": bars}, initial_capital=1000, fee_rate=0, slippage_rate=0)

    assert result["trades"] == []
    assert result["unfilled_signals"] == [
        {"symbol": "AAA", "signal_date": "2024-01-02", "signal": "BUY", "reason": "missing next bar"}
    ]


def test_backtest_aggregates_equal_weight_multi_symbol_portfolio():
    result = run_backtest(
        {
            "AAA": make_bars(
                "AAA",
                [
                    ("2024-01-01", 10, 10, "BUY"),
                    ("2024-01-02", 10, 12, None),
                ],
            ),
            "BBB": make_bars(
                "BBB",
                [
                    ("2024-01-01", 20, 20, "BUY"),
                    ("2024-01-02", 20, 18, None),
                ],
            ),
        },
        initial_capital=1000,
        fee_rate=0,
        slippage_rate=0,
    )

    assert result["summary"]["total_return"] == pytest.approx(0.05)
    assert result["summary"]["exposure"] == pytest.approx(0.5)
    assert len(result["equity"]) == 2

