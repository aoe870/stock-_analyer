from stock_analyzer_app.aggregation.daily import aggregate_analysis_bars, materialize_expma_analysis
from stock_analyzer_app.data_provider.base import StockDataProvider


class DailySyncPipeline:
    def __init__(self, repository: object, providers: list[StockDataProvider]) -> None:
        self.repository = repository
        self.providers = providers

    def run_full_daily_pipeline(self, start_date: str, end_date: str, requested_by: str = "manual", symbols: list[str] | None = None) -> dict:
        provider_names = [provider.name for provider in self.providers]
        job = self.repository.create_job("full_daily_pipeline", requested_by, provider_names)
        self.repository.mark_job_running(job["id"])
        summary = {"success": 0, "skipped": 0, "failed": 0, "retryable": 0, "provider_fallback": 0, "metadata_errors": 0}

        try:
            if symbols:
                universe = [
                    {
                        "symbol": symbol,
                        "exchange": _exchange_from_symbol(symbol),
                        "name": symbol,
                        "source": provider_names[0] if provider_names else "manual",
                    }
                    for symbol in symbols
                ]
            else:
                universe = self._fetch_stock_universe()
            self.repository.upsert_stocks(universe)
            summary["metadata_errors"] += self._persist_trading_calendars(universe, start_date, end_date)
            for stock in universe:
                symbol = stock["symbol"]
                try:
                    bars, bar_provider, bar_fallback = self._fetch_first("fetch_daily_bars", symbol, start_date, end_date)
                    factors, _, factor_fallback = self._fetch_first("fetch_adjustment_factors", symbol, start_date, end_date)
                    summary["provider_fallback"] += bar_fallback + factor_fallback
                    self.repository.upsert_daily_bars(bars)
                    self.repository.upsert_adjustment_factors(factors)
                    analysis_rows = aggregate_analysis_bars(bars, factors)
                    self.repository.upsert_analysis_daily_bars(analysis_rows)
                    materialized = materialize_expma_analysis(analysis_rows)
                    self.repository.upsert_daily_indicators(materialized["indicators"])
                    self.repository.upsert_strategy_signals(materialized["signals"])
                    summary["metadata_errors"] += self._persist_stock_status(symbol, end_date)
                    self.repository.add_item(
                        job["id"],
                        {
                            "symbol": symbol,
                            "date_start": start_date,
                            "date_end": end_date,
                            "status": "success",
                            "provider": bar_provider,
                            "attempt_count": 1 + bar_fallback,
                        },
                    )
                    summary["success"] += 1
                except Exception as exc:  # noqa: BLE001 - symbol-level isolation.
                    self.repository.add_item(
                        job["id"],
                        {
                            "symbol": symbol,
                            "date_start": start_date,
                            "date_end": end_date,
                            "status": "failed",
                            "provider": None,
                            "attempt_count": len(self.providers),
                            "error_message": str(exc),
                        },
                    )
                    summary["failed"] += 1
            status = "completed_with_errors" if summary["success"] and summary["failed"] else "failed" if summary["failed"] else "completed"
            return self.repository.finish_job(job["id"], status, summary)
        except Exception as exc:
            return self.repository.finish_job(job["id"], "failed", {**summary, "error": str(exc)})

    def _fetch_stock_universe(self) -> list[dict]:
        errors = []
        for provider in self.providers:
            try:
                rows = provider.fetch_stock_universe()
                return [{**row, "source": row.get("source", provider.name)} for row in rows]
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("; ".join(errors) or "no providers configured")

    def _fetch_first(self, method_name: str, *args) -> tuple[list[dict], str, int]:
        errors = []
        for index, provider in enumerate(self.providers):
            try:
                return getattr(provider, method_name)(*args), provider.name, index
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("; ".join(errors) or f"no provider succeeded for {method_name}")

    def _persist_trading_calendars(self, universe: list[dict], start_date: str, end_date: str) -> int:
        if not hasattr(self.repository, "upsert_trading_calendar"):
            return 0
        error_count = 0
        for exchange in sorted({stock.get("exchange") or _exchange_from_symbol(stock["symbol"]) for stock in universe}):
            try:
                rows, _, _ = self._fetch_first("fetch_trading_calendar", exchange, start_date, end_date)
                self.repository.upsert_trading_calendar(rows)
            except Exception:  # noqa: BLE001 - metadata should not block symbol-level sync.
                error_count += 1
        return error_count

    def _persist_stock_status(self, symbol: str, trade_date: str) -> int:
        if not hasattr(self.repository, "upsert_stock_status"):
            return 0
        try:
            rows, _, _ = self._fetch_first("fetch_stock_status", [symbol], trade_date)
            self.repository.upsert_stock_status(rows)
            return 0
        except Exception:  # noqa: BLE001 - metadata should not block symbol-level sync.
            return 1


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SH") or symbol.startswith("6"):
        return "SH"
    if symbol.endswith(".SZ") or symbol.startswith(("0", "3")):
        return "SZ"
    return "UNKNOWN"
