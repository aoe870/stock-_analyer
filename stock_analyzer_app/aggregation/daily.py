import json

from stock_analyzer_app.strategies.expma import STRATEGY_KEY, compute_expma_signals


OHLC_FIELDS = ("open", "high", "low", "close")


def normalize_daily_bar(row: dict) -> dict:
    missing_ohlc = [field for field in OHLC_FIELDS if row.get(field) is None]
    if missing_ohlc:
        raise ValueError(f"missing required OHLC fields: {', '.join(missing_ohlc)}")
    return {
        "symbol": str(row["symbol"]).strip(),
        "trade_date": str(row["trade_date"]),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": float(row.get("volume", 0)),
        "amount": float(row.get("amount", 0)),
        "source": str(row.get("source", "")),
        "is_adjusted": bool(row.get("is_adjusted", False)),
    }


def aggregate_analysis_bars(daily_bars: list[dict], adjustment_factors: list[dict]) -> list[dict]:
    factor_by_key = {
        (row["symbol"], str(row["trade_date"])): float(row["adj_factor"])
        for row in adjustment_factors
        if row.get("adj_factor") is not None
    }
    analysis_rows: list[dict] = []
    for raw in daily_bars:
        bar = normalize_daily_bar(raw)
        factor = factor_by_key.get((bar["symbol"], bar["trade_date"]))
        if factor is None:
            multiplier = 1.0
            price_mode = "unadjusted"
            quality = "missing_adj_factor"
        else:
            multiplier = factor
            price_mode = "forward_adjusted"
            quality = "ok"
        analysis_rows.append(
            {
                **bar,
                "open": bar["open"] * multiplier,
                "high": bar["high"] * multiplier,
                "low": bar["low"] * multiplier,
                "close": bar["close"] * multiplier,
                "adj_factor": factor,
                "price_mode": price_mode,
                "data_quality": quality,
            }
        )
    return sorted(analysis_rows, key=lambda row: (row["symbol"], row["trade_date"]))


def compute_recompute_start(trading_dates: list[str], earliest_changed_date: str, warmup_rows: int = 60) -> str:
    ordered = sorted(trading_dates)
    try:
        changed_index = ordered.index(earliest_changed_date)
    except ValueError:
        ordered.append(earliest_changed_date)
        ordered.sort()
        changed_index = ordered.index(earliest_changed_date)
    return ordered[max(0, changed_index - warmup_rows)]


def materialize_expma_analysis(analysis_bars: list[dict], warmup: int = 60) -> dict[str, list[dict]]:
    signal_rows = compute_expma_signals(analysis_bars, warmup=warmup)
    indicators: list[dict] = []
    signals: list[dict] = []
    for row in signal_rows:
        indicators.append(
            {
                "symbol": row["symbol"],
                "trade_date": row["trade_date"],
                "strategy_key": STRATEGY_KEY,
                "expma17": row["expma17"],
                "expma50": row["expma50"],
                "cross_price": row["cross_price"],
                "cross_in_kline": row["cross_in_kline"],
                "warmup_ready": row["warmup_ready"],
            }
        )
        signals.append(
            {
                "symbol": row["symbol"],
                "trade_date": row["trade_date"],
                "strategy_key": STRATEGY_KEY,
                "selected_signal": row["selected_signal"],
                "raw_flags_json": json.dumps(row["raw_flags"], sort_keys=True),
                "trend_state": _trend_state(float(row["close"]), row["expma17"], row["expma50"]),
            }
        )
    return {"indicators": indicators, "signals": signals}


def _trend_state(close: float, expma17: float | None, expma50: float | None) -> str:
    if expma17 is None or expma50 is None:
        return "insufficient"
    if close > expma17 > expma50:
        return "above_expma17_expma50"
    if expma17 > expma50:
        return "trend_up_pullback"
    if close < expma50:
        return "below_expma50"
    return "neutral"

