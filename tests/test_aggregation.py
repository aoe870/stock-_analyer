import pytest
from datetime import date, timedelta

from stock_analyzer_app.aggregation.daily import (
    aggregate_analysis_bars,
    compute_recompute_start,
    materialize_expma_analysis,
    normalize_daily_bar,
)


def test_normalize_daily_bar_rejects_missing_ohlc():
    with pytest.raises(ValueError, match="missing required OHLC"):
        normalize_daily_bar({"symbol": "AAA", "trade_date": "2024-01-02", "open": 10, "high": 11, "low": 9})


def test_adjustment_factors_produce_forward_adjusted_analysis_bars():
    rows = aggregate_analysis_bars(
        [
            {
                "symbol": "AAA",
                "trade_date": "2024-01-02",
                "open": 10,
                "high": 12,
                "low": 9,
                "close": 11,
                "volume": 100,
                "amount": 1100,
                "source": "tushare",
                "is_adjusted": False,
            }
        ],
        [{"symbol": "AAA", "trade_date": "2024-01-02", "adj_factor": 2.0, "source": "tushare"}],
    )

    assert rows[0]["price_mode"] == "forward_adjusted"
    assert rows[0]["open"] == 20
    assert rows[0]["close"] == 22
    assert rows[0]["adj_factor"] == 2.0
    assert rows[0]["data_quality"] == "ok"


def test_missing_adjustment_factor_falls_back_to_unadjusted_with_quality_marker():
    rows = aggregate_analysis_bars(
        [
            {
                "symbol": "AAA",
                "trade_date": "2024-01-02",
                "open": 10,
                "high": 12,
                "low": 9,
                "close": 11,
                "volume": 100,
                "amount": 1100,
                "source": "akshare",
                "is_adjusted": False,
            }
        ],
        [],
    )

    assert rows[0]["price_mode"] == "unadjusted"
    assert rows[0]["data_quality"] == "missing_adj_factor"


def test_recompute_start_uses_60_rows_before_changed_date():
    dates = [f"2024-01-{day:02d}" for day in range(1, 32)] + [f"2024-02-{day:02d}" for day in range(1, 32)]

    assert compute_recompute_start(dates, "2024-02-10", warmup_rows=60) == "2024-01-01"
    assert compute_recompute_start(dates, "2024-02-10", warmup_rows=5) == "2024-02-05"


def test_materialize_expma_analysis_splits_indicators_and_signals():
    bars = []
    closes = [10] * 30 + [9] * 20 + [15] * 20 + [13]
    start = date(2024, 1, 1)
    for index, close in enumerate(closes):
        bars.append(
            {
                "symbol": "AAA",
                "trade_date": (start + timedelta(days=index)).isoformat(),
                "open": close,
                "high": close + 1,
                "low": close - 1,
                "close": close,
                "volume": 100,
                "amount": close * 100,
                "source": "unit",
                "price_mode": "forward_adjusted",
                "data_quality": "ok",
            }
        )

    materialized = materialize_expma_analysis(bars, warmup=0)

    assert materialized["indicators"][-1]["strategy_key"] == "expma_17_50"
    assert "expma17" in materialized["indicators"][-1]
    assert materialized["signals"][-1]["selected_signal"] == "HALF_SELL"
    assert "raw_flags_json" in materialized["signals"][-1]
