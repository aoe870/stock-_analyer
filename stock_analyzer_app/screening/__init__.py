from collections.abc import Mapping

from stock_analyzer_app.strategies import compute_expma_signals


BUY_LIKE = {"BUY", "RE_BUY", "RE_BUY_50"}
RISK_REDUCTION = {"HALF_SELL", "CLEAR_1", "CLEAR_2"}


def screen_from_repository(
    repository: object,
    trade_date: str,
    symbols: list[str] | None = None,
    price_mode: str = "forward_adjusted",
    signal_filter: str = "all",
) -> dict:
    rows = repository.latest_screening_rows(trade_date, symbols=symbols, price_mode=price_mode)
    requested = set(symbols or [row["symbol"] for row in rows])
    seen = {row["symbol"] for row in rows}
    results = [_screen_row(row) for row in rows]
    results = [row for row in results if _passes_filter(row, signal_filter)]
    return {
        "summary": {
            "evaluated": len(rows),
            "skipped": 0,
            "missing": len(requested - seen),
            "error": 0,
            "price_mode": price_mode,
        },
        "results": sorted(results, key=lambda item: item["symbol"]),
    }


def screen_latest(
    symbol_bars: Mapping[str, list[dict]],
    trade_date: str | None = None,
    signal_filter: str = "all",
) -> dict:
    results: list[dict] = []
    summary = {"success": 0, "skipped": 0, "failed": 0, "stale": 0}

    for symbol, bars in symbol_bars.items():
        try:
            rows = _ensure_signals(bars)
            candidates = [row for row in rows if trade_date is None or row["trade_date"] <= trade_date]
            if not candidates:
                summary["skipped"] += 1
                continue
            latest = candidates[-1]
            result = _screen_row(latest)
            if _passes_filter(result, signal_filter):
                results.append(result)
            summary["success"] += 1
        except Exception as exc:  # noqa: BLE001
            summary["failed"] += 1
            results.append({"symbol": symbol, "error": str(exc)})

    return {
        "summary": summary,
        "results": sorted(results, key=lambda item: (item.get("signal") or "", item.get("symbol") or "")),
    }


def _ensure_signals(bars: list[dict]) -> list[dict]:
    if not bars:
        return []
    if "expma17" in bars[-1] and "raw_flags" in bars[-1]:
        return sorted(bars, key=lambda row: row["trade_date"])
    return compute_expma_signals(bars)


def _screen_row(row: dict) -> dict:
    close = float(row["close"])
    expma17 = row.get("expma17")
    expma50 = row.get("expma50")
    return {
        "symbol": row["symbol"],
        "name": row.get("name", ""),
        "trade_date": row["trade_date"],
        "close": close,
        "high": float(row["high"]),
        "low": float(row["low"]),
        "expma17": expma17,
        "expma50": expma50,
        "trend_state": row.get("trend_state") or _trend_state(close, expma17, expma50),
        "signal": row.get("signal") or row.get("selected_signal"),
        "selected_signal": row.get("selected_signal") or row.get("signal"),
        "raw_flags": row.get("raw_flags", {}),
        "source": row.get("source", ""),
        "data_quality": row.get("data_quality", "unknown"),
        "error": None,
        "stale": False,
    }


def _trend_state(close: float, expma17: float | None, expma50: float | None) -> str:
    if expma17 is None or expma50 is None:
        return "insufficient"
    if close > expma17 > expma50:
        return "above_expma17_expma50"
    if close > expma50 and expma17 > expma50:
        return "pullback_uptrend"
    if close < expma50:
        return "below_expma50"
    return "neutral"


def _passes_filter(row: dict, signal_filter: str) -> bool:
    signal = row.get("selected_signal") or row.get("signal")
    if signal_filter == "buy_like":
        return signal in BUY_LIKE
    if signal_filter == "risk_reduction":
        return signal in RISK_REDUCTION
    if signal_filter == "trend_up":
        return bool(row.get("expma17") and row.get("expma50") and row["expma17"] > row["expma50"])
    return True
