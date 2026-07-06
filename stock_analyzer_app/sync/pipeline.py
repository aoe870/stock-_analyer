from concurrent.futures import ThreadPoolExecutor, as_completed

from stock_analyzer_app.aggregation.daily import aggregate_analysis_bars, materialize_expma_analysis
from stock_analyzer_app.data_provider.base import StockDataProvider


class DailySyncPipeline:
    def __init__(
        self,
        repository: object,
        providers: list[StockDataProvider],
        max_workers: int = 1,
        include_optional_metadata: bool = True,
    ) -> None:
        self.repository = repository
        self.providers = providers
        self.max_workers = max(1, int(max_workers))
        self.include_optional_metadata = include_optional_metadata

    def run_full_daily_pipeline(self, start_date: str, end_date: str, requested_by: str = "manual", symbols: list[str] | None = None) -> dict:
        provider_names = [provider.name for provider in self.providers]
        job = self.repository.create_job("full_daily_pipeline", requested_by, provider_names)
        self.repository.mark_job_running(job["id"])
        summary = {"success": 0, "skipped": 0, "failed": 0, "retryable": 0, "provider_fallback": 0, "metadata_errors": 0, "index_quotes": 0, "sector_quotes": 0}

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
            self._persist_provider_profiles(universe)
            self._persist_raw_payloads()
            summary["metadata_errors"] += self._persist_trading_calendars(universe, start_date, end_date)
            if self.max_workers > 1 and len(universe) > 1:
                for result in self._run_symbol_workers(job["id"], universe, start_date, end_date):
                    summary["success"] += result["success"]
                    summary["failed"] += result["failed"]
                    summary["retryable"] += result["retryable"]
                    summary["provider_fallback"] += result["provider_fallback"]
                    summary["metadata_errors"] += result["metadata_errors"]
            else:
                for stock in universe:
                    result = self._process_symbol(job["id"], stock, start_date, end_date)
                    summary["success"] += result["success"]
                    summary["failed"] += result["failed"]
                    summary["retryable"] += result["retryable"]
                    summary["provider_fallback"] += result["provider_fallback"]
                    summary["metadata_errors"] += result["metadata_errors"]
            market_snapshot_counts = self._persist_market_dashboard_quote_snapshots()
            summary["index_quotes"] += market_snapshot_counts["index_quotes"]
            summary["sector_quotes"] += market_snapshot_counts["sector_quotes"]
            status = "completed_with_errors" if summary["success"] and summary["failed"] else "failed" if summary["failed"] else "completed"
            return self.repository.finish_job(job["id"], status, summary)
        except Exception as exc:
            return self.repository.finish_job(job["id"], "failed", {**summary, "error": str(exc)})

    def run_fundamental_refresh_pipeline(self, requested_by: str = "manual", symbols: list[str] | None = None) -> dict:
        provider_names = [provider.name for provider in self.providers]
        job = self.repository.create_job("fundamental_refresh_pipeline", requested_by, provider_names)
        self.repository.mark_job_running(job["id"])
        summary = {"success": 0, "failed": 0, "metadata_errors": 0}
        try:
            if not symbols:
                symbols = [row["symbol"] for row in self._fetch_stock_universe()]
            for symbol in symbols:
                try:
                    errors = self._persist_fundamental_rows(symbol)
                    summary["metadata_errors"] += errors
                    status = "success" if errors == 0 else "completed_with_errors"
                    self.repository.add_item(job["id"], {"symbol": symbol, "status": status, "attempt_count": 1})
                    summary["success"] += 1
                except Exception as exc:  # noqa: BLE001
                    self.repository.add_item(job["id"], {"symbol": symbol, "status": "failed", "attempt_count": len(self.providers), "error_message": str(exc)})
                    summary["failed"] += 1
            status = "completed_with_errors" if summary["success"] and summary["failed"] else "failed" if summary["failed"] else "completed"
            return self.repository.finish_job(job["id"], status, summary)
        except Exception as exc:
            return self.repository.finish_job(job["id"], "failed", {**summary, "error": str(exc)})

    def run_market_structure_pipeline(self, requested_by: str = "manual") -> dict:
        provider_names = [provider.name for provider in self.providers]
        job = self.repository.create_job("market_structure_pipeline", requested_by, provider_names)
        self.repository.mark_job_running(job["id"])
        summary = {"success": 0, "failed": 0, "metadata_errors": 0, "indexes": 0, "sectors": 0}
        try:
            for provider in self.providers:
                try:
                    indexes = provider.fetch_index_list() if hasattr(provider, "fetch_index_list") else []
                    sectors = provider.fetch_sector_list() if hasattr(provider, "fetch_sector_list") else []
                    if indexes and hasattr(self.repository, "upsert_market_indexes"):
                        self.repository.upsert_market_indexes(indexes)
                    if sectors and hasattr(self.repository, "upsert_market_sectors"):
                        self.repository.upsert_market_sectors(sectors)
                    index_constituents = []
                    if hasattr(provider, "fetch_index_constituents"):
                        for row in indexes:
                            index_constituents.extend(provider.fetch_index_constituents(row["index_code"]))
                    sector_constituents = []
                    if hasattr(provider, "fetch_sector_constituents"):
                        for row in sectors:
                            sector_constituents.extend(provider.fetch_sector_constituents(row["sector_code"]))
                    if index_constituents and hasattr(self.repository, "upsert_index_constituents"):
                        self.repository.upsert_index_constituents(index_constituents)
                    if sector_constituents and hasattr(self.repository, "upsert_sector_constituents"):
                        self.repository.upsert_sector_constituents(sector_constituents)
                    summary["indexes"] += len(indexes)
                    summary["sectors"] += len(sectors)
                    summary["success"] += 1
                    self.repository.add_item(job["id"], {"status": "success", "provider": provider.name, "attempt_count": 1})
                    break
                except Exception as exc:  # noqa: BLE001
                    summary["failed"] += 1
                    self.repository.add_item(job["id"], {"status": "failed", "provider": provider.name, "attempt_count": 1, "error_message": str(exc)})
            status = "completed_with_errors" if summary["success"] and summary["failed"] else "failed" if summary["failed"] and not summary["success"] else "completed"
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

    def _persist_market_dashboard_quote_snapshots(self) -> dict[str, int]:
        counts = {"index_quotes": 0, "sector_quotes": 0}
        for provider in self.providers:
            try:
                index_rows = provider.fetch_index_rankings(sort="changeRate", order="DESC") if hasattr(provider, "fetch_index_rankings") else []
                sector_rows = provider.fetch_sector_rankings(sort="changeRate", order="DESC") if hasattr(provider, "fetch_sector_rankings") else []
                if index_rows and hasattr(self.repository, "upsert_market_indexes"):
                    self.repository.upsert_market_indexes(index_rows)
                if sector_rows and hasattr(self.repository, "upsert_market_sectors"):
                    self.repository.upsert_market_sectors(sector_rows)
                if index_rows and hasattr(self.repository, "upsert_latest_index_quotes"):
                    self.repository.upsert_latest_index_quotes(index_rows)
                    counts["index_quotes"] = len(index_rows)
                if sector_rows and hasattr(self.repository, "upsert_latest_sector_quotes"):
                    self.repository.upsert_latest_sector_quotes(sector_rows)
                    counts["sector_quotes"] = len(sector_rows)
                if index_rows or sector_rows:
                    return counts
            except Exception:  # noqa: BLE001 - market dashboard snapshots should not block daily stock sync.
                continue
        return counts

    def _fetch_daily_data(self, symbol: str, start_date: str, end_date: str) -> tuple[list[dict], list[dict], list[dict], str, int]:
        bundle_errors = []
        for index, provider in enumerate(self.providers):
            if not hasattr(provider, "fetch_daily_bar_bundle"):
                continue
            try:
                bundle = provider.fetch_daily_bar_bundle(symbol, start_date, end_date)
                return (
                    bundle.get("bars", []),
                    bundle.get("factors", []),
                    bundle.get("adjusted_bars", []),
                    provider.name,
                    index,
                )
            except Exception as exc:  # noqa: BLE001
                bundle_errors.append(f"{provider.name}: {exc}")

        bars, bar_provider, bar_fallback = self._fetch_first("fetch_daily_bars", symbol, start_date, end_date)
        factors, _, factor_fallback = self._fetch_first("fetch_adjustment_factors", symbol, start_date, end_date)
        provider = self._provider_by_name(bar_provider)
        adjusted_bars = []
        if provider is not None and hasattr(provider, "fetch_adjusted_daily_bars"):
            adjusted_bars = provider.fetch_adjusted_daily_bars(symbol, start_date, end_date)
        return bars, factors, adjusted_bars, bar_provider, bar_fallback + factor_fallback

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

    def _persist_stock_status(self, symbol: str, trade_date: str, provider: StockDataProvider | None = None) -> int:
        if not hasattr(self.repository, "upsert_stock_status"):
            return 0
        candidates = [provider, *[item for item in self.providers if item is not provider]]
        for candidate in candidates:
            if candidate is None or not hasattr(candidate, "fetch_stock_status"):
                continue
            try:
                rows = candidate.fetch_stock_status([symbol], trade_date)
                self.repository.upsert_stock_status(rows)
                return 0
            except Exception:  # noqa: BLE001 - metadata should not block symbol-level sync.
                continue
        return 1

    def _persist_provider_profiles(self, universe: list[dict]) -> None:
        if not hasattr(self.repository, "upsert_stock_provider_profiles"):
            return
        rows = [row for row in universe if row.get("provider") and row.get("provider_symbol")]
        if rows:
            self.repository.upsert_stock_provider_profiles(rows)

    def _persist_optional_provider_rows(self, provider: StockDataProvider | None, symbol: str, trade_date: str) -> int:
        if not self.include_optional_metadata:
            return 0
        if provider is None:
            return 0
        error_count = 0
        optional_calls = [
            ("fetch_company_profiles", "upsert_stock_company_profiles", (symbol,)),
            ("fetch_corporate_actions", "upsert_corporate_actions", (symbol,)),
            ("fetch_share_capital_history", "upsert_share_capital_history", (symbol,)),
            ("fetch_daily_money_flow", "upsert_daily_money_flow", (symbol, trade_date)),
        ]
        for fetch_name, persist_name, args in optional_calls:
            if not hasattr(provider, fetch_name) or not hasattr(self.repository, persist_name):
                continue
            try:
                rows = getattr(provider, fetch_name)(*args)
                if rows:
                    getattr(self.repository, persist_name)(rows)
            except Exception:  # noqa: BLE001 - optional metadata should not block price sync.
                error_count += 1
        return error_count

    def _persist_fundamental_rows(self, symbol: str) -> int:
        error_count = 0
        calls = [
            ("fetch_company_profiles", "upsert_stock_company_profiles"),
            ("fetch_corporate_actions", "upsert_corporate_actions"),
            ("fetch_share_capital_history", "upsert_share_capital_history"),
            ("fetch_income_statements", "upsert_income_statements"),
            ("fetch_balance_sheets", "upsert_balance_sheets"),
            ("fetch_cashflow_statements", "upsert_cashflow_statements"),
            ("fetch_top10_holders", "upsert_stock_top10_holders"),
            ("fetch_company_officers", "upsert_stock_company_officers"),
            ("fetch_officer_rewards", "upsert_stock_officer_rewards"),
        ]
        for fetch_name, persist_name in calls:
            if not hasattr(self.repository, persist_name):
                continue
            try:
                rows, _, _ = self._fetch_first(fetch_name, symbol)
                if rows:
                    getattr(self.repository, persist_name)(rows)
            except Exception:  # noqa: BLE001 - one research endpoint should not block the whole stock.
                error_count += 1
        self._persist_raw_payloads()
        return error_count

    def _persist_raw_payloads(self) -> None:
        if not hasattr(self.repository, "save_raw_provider_payload"):
            return
        for provider in self.providers:
            if not hasattr(provider, "drain_raw_payloads"):
                continue
            for payload in provider.drain_raw_payloads():
                try:
                    self.repository.save_raw_provider_payload(**payload)
                except Exception:  # noqa: BLE001 - raw archival should not block normalized persistence.
                    pass

    def _provider_by_name(self, provider_name: str) -> StockDataProvider | None:
        return next((provider for provider in self.providers if provider.name == provider_name), None)

    def _run_symbol_workers(self, job_id: int, universe: list[dict], start_date: str, end_date: str) -> list[dict]:
        results: list[dict] = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(universe))) as executor:
            future_map = {
                executor.submit(self._process_symbol, job_id, stock, start_date, end_date): stock["symbol"]
                for stock in universe
            }
            for future in as_completed(future_map):
                try:
                    results.append(future.result())
                except Exception as exc:  # noqa: BLE001 - worker failure should be recorded as a failed symbol.
                    results.append(
                        {
                            "success": 0,
                            "failed": 1,
                            "retryable": 0,
                            "provider_fallback": 0,
                            "metadata_errors": 0,
                            "error": str(exc),
                        }
                    )
        return results

    def _process_symbol(self, job_id: int, stock: dict, start_date: str, end_date: str) -> dict:
        symbol = stock["symbol"]
        provider_name = None
        fallback_count = 0
        try:
            bars, factors, adjusted_bars, bar_provider, fallback_count = self._fetch_daily_data(symbol, start_date, end_date)
            provider_name = bar_provider
            provider = self._provider_by_name(bar_provider)
            self.repository.upsert_daily_bars(bars)
            if adjusted_bars:
                self.repository.upsert_daily_bars(adjusted_bars)
            self.repository.upsert_adjustment_factors(factors)
            analysis_rows = aggregate_analysis_bars(bars, factors)
            self.repository.upsert_analysis_daily_bars(analysis_rows)
            materialized = materialize_expma_analysis(analysis_rows)
            self.repository.upsert_daily_indicators(materialized["indicators"])
            self.repository.upsert_strategy_signals(materialized["signals"])
            metadata_errors = self._persist_stock_status(symbol, end_date, provider)
            metadata_errors += self._persist_optional_provider_rows(provider, symbol, end_date)
            self._persist_raw_payloads()
            self.repository.add_item(
                job_id,
                {
                    "symbol": symbol,
                    "date_start": start_date,
                    "date_end": end_date,
                    "status": "success",
                    "provider": provider_name,
                    "attempt_count": 1 + fallback_count,
                },
            )
            return {
                "success": 1,
                "failed": 0,
                "retryable": 0,
                "provider_fallback": fallback_count,
                "metadata_errors": metadata_errors,
            }
        except Exception as exc:  # noqa: BLE001 - symbol-level isolation.
            self.repository.add_item(
                job_id,
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
            self._persist_raw_payloads()
            return {
                "success": 0,
                "failed": 1,
                "retryable": 0,
                "provider_fallback": fallback_count,
                "metadata_errors": 0,
            }


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SH") or symbol.startswith("6"):
        return "SH"
    if symbol.endswith(".SZ") or symbol.startswith(("0", "3")):
        return "SZ"
    return "UNKNOWN"
