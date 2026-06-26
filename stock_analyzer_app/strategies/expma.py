from collections.abc import Iterable

from stock_analyzer_app.indicators import cross, ema


STRATEGY_KEY = "expma_17_50"
SIGNAL_PRIORITY = (
    ("clear_2", "CLEAR_2"),
    ("clear_1", "CLEAR_1"),
    ("half_sell", "HALF_SELL"),
    ("buy", "BUY"),
    ("re_buy", "RE_BUY"),
    ("re_buy_50", "RE_BUY_50"),
)


def select_signal(flags: dict[str, bool]) -> str | None:
    for key, signal in SIGNAL_PRIORITY:
        if flags.get(key):
            return signal
    return None


def compute_expma_signals(
    bars: Iterable[dict],
    short: int = 17,
    long: int = 50,
    warmup: int = 60,
) -> list[dict]:
    rows = sorted((dict(bar) for bar in bars), key=lambda item: item["trade_date"])
    closes = [float(row["close"]) for row in rows]
    short_expma = ema(closes, short)
    long_expma = ema(closes, long)
    golden_cross = cross(short_expma, long_expma)
    death_cross = cross(long_expma, short_expma)

    output: list[dict] = []
    for index, row in enumerate(rows):
        close = closes[index]
        prev_close = closes[index - 1] if index > 0 else None
        expma_short = short_expma[index]
        expma_long = long_expma[index]
        prev_short = short_expma[index - 1] if index > 0 else None
        prev_long = long_expma[index - 1] if index > 0 else None
        trend_up = expma_short is not None and expma_long is not None and expma_short > expma_long

        flags = {
            "buy": golden_cross[index] and trend_up,
            "half_sell": (
                index > 0
                and trend_up
                and close < expma_short
                and prev_close is not None
                and prev_short is not None
                and prev_close >= prev_short
            ),
            "re_buy": (
                index > 0
                and trend_up
                and close > expma_short
                and close > expma_long
                and prev_close is not None
                and prev_short is not None
                and prev_close <= prev_short
            ),
            "clear_1": trend_up and close < expma_long,
            "clear_2": death_cross[index],
            "re_buy_50": (
                index > 0
                and trend_up
                and close > expma_long
                and prev_close is not None
                and prev_long is not None
                and prev_close <= prev_long
            ),
        }
        signal = select_signal(flags) if index + 1 >= warmup else None
        cross_price = _cross_price(expma_short, expma_long, prev_short, prev_long)

        output.append(
            {
                **row,
                "strategy_key": STRATEGY_KEY,
                "expma17": expma_short,
                "expma50": expma_long,
                "golden_cross": golden_cross[index],
                "death_cross": death_cross[index],
                "cross_price": cross_price,
                "cross_in_kline": (
                    cross_price is not None
                    and float(row["low"]) <= cross_price <= float(row["high"])
                ),
                "raw_flags": flags,
                "signal": signal,
                "selected_signal": signal,
                "warmup_ready": index + 1 >= warmup,
            }
        )
    return output


def _cross_price(
    expma_short: float | None,
    expma_long: float | None,
    prev_short: float | None,
    prev_long: float | None,
) -> float | None:
    if None in (expma_short, expma_long, prev_short, prev_long):
        return None
    if (prev_short <= prev_long and expma_short >= expma_long) or (
        prev_short >= prev_long and expma_short <= expma_long
    ):
        return (expma_short + expma_long) / 2
    return None

