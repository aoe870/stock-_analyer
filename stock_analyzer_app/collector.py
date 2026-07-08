from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Callable


class CollectorService:
    def __init__(self, repository, pipeline_factory: Callable, fundamental_batch_size: int = 20) -> None:
        self.repository = repository
        self.pipeline_factory = pipeline_factory
        self.fundamental_batch_size = max(0, int(fundamental_batch_size))

    def process_pending_requests(self, limit: int = 10) -> int:
        self.enqueue_missing_enterprise_research()
        processed = 0
        for request in self.repository.list_sync_requests(limit):
            if request.get("status") != "pending":
                continue
            claimed = self.repository.claim_sync_request(request["id"])
            if claimed.get("status") != "claimed":
                continue
            try:
                self._run_request(claimed)
            except Exception as exc:  # noqa: BLE001 - collector records request-level failures and continues.
                self.repository.finish_sync_request(claimed["id"], "failed", str(exc))
            else:
                self.repository.finish_sync_request(claimed["id"], "completed")
            processed += 1
        return processed

    def recover_claimed_requests(self) -> int:
        if hasattr(self.repository, "recover_claimed_sync_requests"):
            return int(self.repository.recover_claimed_sync_requests())
        return 0

    def enqueue_missing_enterprise_research(self) -> int:
        if self.fundamental_batch_size <= 0:
            return 0
        if not hasattr(self.repository, "list_symbols_missing_enterprise_data"):
            return 0
        if not hasattr(self.repository, "create_sync_request") or not hasattr(self.repository, "list_sync_requests"):
            return 0
        queued_symbols = self._queued_enterprise_symbols()
        symbols = self.repository.list_symbols_missing_enterprise_data(
            limit=self.fundamental_batch_size,
            excluded_symbols=queued_symbols,
        )
        if not symbols:
            return 0
        self.repository.create_sync_request(
            "fundamental_refresh_pipeline",
            dataset="stock_research_context",
            scope={"symbols": symbols},
            priority=40,
            requested_by="collector",
            reason="enterprise:auto:missing",
        )
        return 1

    def _queued_enterprise_symbols(self) -> set[str]:
        symbols: set[str] = set()
        for request in self.repository.list_sync_requests(1000):
            if request.get("request_type") != "fundamental_refresh_pipeline":
                continue
            if request.get("status") not in {"pending", "claimed"}:
                continue
            scope = request.get("scope") or {}
            symbols.update(str(symbol) for symbol in scope.get("symbols") or [] if symbol)
        return symbols

    def run_forever(self, poll_seconds: float = 5.0) -> None:
        while True:
            self.process_pending_requests()
            time.sleep(poll_seconds)

    def _run_request(self, request: dict) -> None:
        request_type = request.get("request_type")
        scope = request.get("scope") or {}
        pipeline = self.pipeline_factory()
        requested_by = f"sync_request:{request['id']}"
        if request_type in {"full_daily_pipeline", "sync_daily_bars"}:
            pipeline.run_full_daily_pipeline(
                start_date=scope.get("start_date") or "2024-01-01",
                end_date=scope.get("end_date") or scope.get("start_date") or "2024-12-31",
                requested_by=requested_by,
                symbols=scope.get("symbols") or None,
            )
            return
        if request_type == "fundamental_refresh_pipeline":
            symbols = scope.get("symbols") or None
            if request.get("reason") == "enterprise:auto:missing":
                symbols = self._filter_recent_enterprise_attempts(symbols or [])
                if not symbols:
                    return
            pipeline.run_fundamental_refresh_pipeline(requested_by=requested_by, symbols=symbols)
            return
        if request_type == "market_structure_pipeline":
            pipeline.run_market_structure_pipeline(requested_by=requested_by)
            return
        raise ValueError(f"unsupported sync request type: {request_type}")

    def _filter_recent_enterprise_attempts(self, symbols: list[str]) -> list[str]:
        return [symbol for symbol in symbols if not self._recent_enterprise_attempt(symbol)]

    def _recent_enterprise_attempt(self, symbol: str) -> bool:
        if not hasattr(self.repository, "get_dataset_freshness"):
            return False
        record = self.repository.get_dataset_freshness("stock_research_context", symbol)
        if not record:
            return False
        last_attempt = _parse_timestamp(record.get("last_attempt_at"))
        if last_attempt is None:
            return False
        ttl_days = max(0, int(getattr(getattr(self.repository, "settings", None), "enterprise_refresh_ttl_days", 7)))
        return datetime.now(timezone.utc) - last_attempt <= timedelta(days=ttl_days)


def _parse_timestamp(value) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
