from collections import defaultdict
from collections.abc import Mapping


TARGET_BY_SIGNAL = {
    "BUY": 1.0,
    "HALF_SELL": 0.5,
    "RE_BUY": 1.0,
    "CLEAR_1": 0.0,
    "CLEAR_2": 0.0,
    "RE_BUY_50": 1.0,
}


class CoverageError(ValueError):
    pass


def run_backtest_from_repository(
    repository: object,
    symbols: list[str],
    start_date: str,
    end_date: str,
    price_mode: str = "forward_adjusted",
    allow_partial_coverage: bool = False,
    initial_capital: float = 100000,
    fee_rate: float = 0.0003,
    slippage_rate: float = 0.0005,
) -> dict:
    symbol_bars = repository.analysis_bars_with_signals(symbols, start_date, end_date, price_mode)
    missing = [symbol for symbol in symbols if not symbol_bars.get(symbol)]
    if missing and not allow_partial_coverage:
        raise CoverageError(f"missing analysis coverage for symbols: {', '.join(missing)}")

    covered = {symbol: rows for symbol, rows in symbol_bars.items() if rows}
    result = run_backtest(covered, initial_capital=initial_capital, fee_rate=fee_rate, slippage_rate=slippage_rate)
    result["coverage"] = {
        "requested_symbols": symbols,
        "evaluated_symbols": sorted(covered),
        "missing_symbols": missing,
        "price_mode": price_mode,
        "allow_partial_coverage": allow_partial_coverage,
    }
    return result


def run_backtest(
    symbol_bars: Mapping[str, list[dict]],
    initial_capital: float = 100000,
    fee_rate: float = 0.0003,
    slippage_rate: float = 0.0005,
) -> dict:
    if not symbol_bars:
        return _empty_result(initial_capital)

    allocation = initial_capital / len(symbol_bars)
    all_trades: list[dict] = []
    all_unfilled: list[dict] = []
    symbol_equity: dict[str, list[dict]] = {}

    for symbol, bars in symbol_bars.items():
        rows = sorted((dict(row) for row in bars), key=lambda row: row["trade_date"])
        result = _run_symbol(symbol, rows, allocation, fee_rate, slippage_rate)
        all_trades.extend(result["trades"])
        all_unfilled.extend(result["unfilled_signals"])
        symbol_equity[symbol] = result["equity"]

    portfolio_equity = _aggregate_equity(symbol_equity)
    summary = _summary(initial_capital, portfolio_equity, all_trades)

    return {
        "summary": summary,
        "trades": sorted(all_trades, key=lambda trade: (trade["trade_date"], trade["symbol"])),
        "equity": portfolio_equity,
        "positions": _aggregate_positions(symbol_equity),
        "unfilled_signals": sorted(all_unfilled, key=lambda item: (item["signal_date"], item["symbol"])),
    }


def _run_symbol(
    symbol: str,
    rows: list[dict],
    initial_cash: float,
    fee_rate: float,
    slippage_rate: float,
) -> dict:
    cash = initial_cash
    shares = 0.0
    position = 0.0
    trades: list[dict] = []
    unfilled: list[dict] = []
    equity_rows: list[dict] = []

    pending = _pending_orders(rows)
    for index, row in enumerate(rows):
        trade_date = row["trade_date"]
        if index in pending:
            signal_date, signal = pending[index]
            target_position = _target_position(signal, position)
            if target_position != position:
                open_price = float(row["open"])
                side = "BUY" if target_position > position else "SELL"
                execution_price = open_price * (1 + slippage_rate if side == "BUY" else 1 - slippage_rate)
                close_value = cash + shares * execution_price
                target_value = close_value * target_position
                current_value = shares * execution_price
                delta_value = target_value - current_value
                quantity = delta_value / execution_price
                gross = abs(quantity * execution_price)
                cost = gross * fee_rate

                cash -= quantity * execution_price
                cash -= cost
                shares += quantity
                position = target_position
                trades.append(
                    {
                        "symbol": symbol,
                        "signal_date": signal_date,
                        "trade_date": trade_date,
                        "signal": signal,
                        "side": side,
                        "price": execution_price,
                        "quantity": quantity,
                        "gross": gross,
                        "cost": cost,
                        "target_position": target_position,
                    }
                )

        close = float(row["close"])
        equity_rows.append(
            {
                "symbol": symbol,
                "trade_date": trade_date,
                "cash": cash,
                "shares": shares,
                "position": position,
                "equity": cash + shares * close,
            }
        )

    for index, row in enumerate(rows):
        signal = row.get("signal") or row.get("selected_signal")
        if signal in TARGET_BY_SIGNAL and index == len(rows) - 1:
            unfilled.append(
                {
                    "symbol": symbol,
                    "signal_date": row["trade_date"],
                    "signal": signal,
                    "reason": "missing next bar",
                }
            )

    return {"trades": trades, "equity": equity_rows, "unfilled_signals": unfilled}


def _pending_orders(rows: list[dict]) -> dict[int, tuple[str, str]]:
    pending: dict[int, tuple[str, str]] = {}
    for index, row in enumerate(rows):
        signal = row.get("signal") or row.get("selected_signal")
        if signal in TARGET_BY_SIGNAL and index + 1 < len(rows):
            pending[index + 1] = (row["trade_date"], signal)
    return pending


def _target_position(signal: str, current_position: float) -> float:
    if signal == "HALF_SELL" and current_position != 1.0:
        return current_position
    if signal == "RE_BUY" and current_position != 0.5:
        return current_position
    return TARGET_BY_SIGNAL[signal]


def _aggregate_equity(symbol_equity: Mapping[str, list[dict]]) -> list[dict]:
    by_date: dict[str, dict[str, float]] = defaultdict(lambda: {"equity": 0.0, "position_total": 0.0, "count": 0})
    for rows in symbol_equity.values():
        for row in rows:
            bucket = by_date[row["trade_date"]]
            bucket["equity"] += row["equity"]
            bucket["position_total"] += row["position"]
            bucket["count"] += 1

    return [
        {
            "trade_date": trade_date,
            "equity": values["equity"],
            "exposure": values["position_total"] / values["count"] if values["count"] else 0,
        }
        for trade_date, values in sorted(by_date.items())
    ]


def _aggregate_positions(symbol_equity: Mapping[str, list[dict]]) -> list[dict]:
    positions: list[dict] = []
    for rows in symbol_equity.values():
        positions.extend(
            {
                "symbol": row["symbol"],
                "trade_date": row["trade_date"],
                "position": row["position"],
                "shares": row["shares"],
                "cash": row["cash"],
                "equity": row["equity"],
            }
            for row in rows
        )
    return sorted(positions, key=lambda item: (item["trade_date"], item["symbol"]))


def _summary(initial_capital: float, equity: list[dict], trades: list[dict]) -> dict:
    if not equity:
        return {
            "initial_capital": initial_capital,
            "final_equity": initial_capital,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "win_rate": 0.0,
            "average_trade_return": 0.0,
            "exposure": 0.0,
            "turnover": 0.0,
        }

    final_equity = equity[-1]["equity"]
    peak = equity[0]["equity"]
    max_drawdown = 0.0
    for row in equity:
        peak = max(peak, row["equity"])
        if peak:
            max_drawdown = min(max_drawdown, row["equity"] / peak - 1)

    turnover = sum(trade["gross"] for trade in trades) / initial_capital if initial_capital else 0
    return {
        "initial_capital": initial_capital,
        "final_equity": final_equity,
        "total_return": final_equity / initial_capital - 1 if initial_capital else 0,
        "max_drawdown": max_drawdown,
        "trade_count": len(trades),
        "win_rate": 0.0,
        "average_trade_return": 0.0,
        "exposure": sum(row["exposure"] for row in equity) / len(equity),
        "turnover": turnover,
    }


def _empty_result(initial_capital: float) -> dict:
    return {
        "summary": _summary(initial_capital, [], []),
        "trades": [],
        "equity": [],
        "positions": [],
        "unfilled_signals": [],
    }
