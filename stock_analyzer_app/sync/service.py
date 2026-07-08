from dataclasses import dataclass, field
from datetime import datetime, timezone

from stock_analyzer_app.data_provider.base import StockDataProvider


RUNNING_STATUSES = {"pending", "running"}


@dataclass
class InMemorySyncRepository:
    jobs: dict[int, dict] = field(default_factory=dict)
    items: dict[int, list[dict]] = field(default_factory=dict)
    sync_requests: dict[int, dict] = field(default_factory=dict)
    dataset_freshness: dict[tuple[str, str], dict] = field(default_factory=dict)
    daily_bars: list[dict] = field(default_factory=list)
    _next_id: int = 1
    _next_request_id: int = 1

    def create_job(self, job_type: str, requested_by: str, provider_priority: list[str]) -> dict:
        job = {
            "id": self._next_id,
            "job_type": job_type,
            "status": "pending",
            "requested_by": requested_by,
            "provider_priority": provider_priority,
            "summary": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "finished_at": None,
        }
        self.jobs[job["id"]] = job
        self.items[job["id"]] = []
        self._next_id += 1
        return dict(job)

    def mark_job_running(self, job_id: int) -> None:
        self.jobs[job_id]["status"] = "running"
        self.jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    def finish_job(self, job_id: int, status: str, summary: dict) -> dict:
        self.jobs[job_id]["status"] = status
        self.jobs[job_id]["summary"] = summary
        self.jobs[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
        return dict(self.jobs[job_id])

    def add_item(self, job_id: int, item: dict) -> None:
        self.items[job_id].append(dict(item))

    def get_job(self, job_id: int) -> dict:
        return dict(self.jobs[int(job_id)])

    def list_jobs(self) -> list[dict]:
        return sorted((dict(job) for job in self.jobs.values()), key=lambda item: item["id"], reverse=True)

    def get_job_items(self, job_id: int) -> list[dict]:
        return [dict(item) for item in self.items.get(int(job_id), [])]

    def upsert_daily_bars(self, bars: list[dict]) -> None:
        self.daily_bars.extend(dict(row) for row in bars)

    def has_running_job(self, job_type: str) -> bool:
        return any(job["job_type"] == job_type and job["status"] in RUNNING_STATUSES for job in self.jobs.values())

    def create_sync_request(
        self,
        request_type: str,
        dataset: str | None = None,
        scope: dict | None = None,
        priority: int = 50,
        requested_by: str = "api",
        reason: str | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        request = {
            "id": self._next_request_id,
            "request_type": request_type,
            "dataset": dataset or request_type,
            "scope": dict(scope or {}),
            "priority": int(priority),
            "status": "pending",
            "requested_by": requested_by,
            "reason": reason,
            "created_at": now,
            "claimed_at": None,
            "finished_at": None,
            "error_message": None,
        }
        self.sync_requests[request["id"]] = request
        self._next_request_id += 1
        return dict(request)

    def get_sync_request(self, request_id: int) -> dict:
        return dict(self.sync_requests[int(request_id)])

    def list_sync_requests(self, limit: int = 100) -> list[dict]:
        status_order = {"pending": 0, "claimed": 1, "failed": 2, "completed": 3, "cancelled": 4}
        requests = sorted(
            self.sync_requests.values(),
            key=lambda item: (status_order.get(str(item["status"]), 9), -int(item["priority"]), -int(item["id"])),
        )
        return [dict(item) for item in requests[:limit]]

    def claim_sync_request(self, request_id: int) -> dict:
        request = self.sync_requests[int(request_id)]
        if request["status"] != "pending":
            return dict(request)
        request["status"] = "claimed"
        request["claimed_at"] = datetime.now(timezone.utc).isoformat()
        return dict(request)

    def finish_sync_request(self, request_id: int, status: str, error_message: str | None = None) -> dict:
        request = self.sync_requests[int(request_id)]
        request["status"] = status
        request["error_message"] = error_message
        request["finished_at"] = datetime.now(timezone.utc).isoformat()
        return dict(request)

    def recover_claimed_sync_requests(self) -> int:
        recovered = 0
        for request in self.sync_requests.values():
            if request["status"] != "claimed":
                continue
            request["status"] = "pending"
            request["claimed_at"] = None
            recovered += 1
        return recovered

    def upsert_dataset_freshness(
        self,
        dataset: str,
        scope_key: str = "global",
        status: str = "missing",
        latest_data_date: str | None = None,
        rows: int = 0,
        missing_count: int = 0,
        failed_count: int = 0,
        owner_job_type: str | None = None,
        summary: dict | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "dataset": dataset,
            "scope_key": scope_key,
            "latest_data_date": latest_data_date,
            "last_success_at": now if status == "ready" else None,
            "last_attempt_at": now,
            "status": status,
            "rows": int(rows),
            "missing_count": int(missing_count),
            "failed_count": int(failed_count),
            "owner_job_type": owner_job_type,
            "summary": dict(summary or {}),
        }
        self.dataset_freshness[(dataset, scope_key)] = record
        return dict(record)

    def get_dataset_freshness(self, dataset: str, scope_key: str = "global") -> dict | None:
        record = self.dataset_freshness.get((dataset, scope_key))
        return dict(record) if record else None

    def list_symbols_missing_enterprise_data(self, limit: int = 100, excluded_symbols: set[str] | list[str] | None = None) -> list[str]:
        return []


class SyncService:
    def __init__(self, repository: InMemorySyncRepository, providers: list[StockDataProvider]) -> None:
        self.repository = repository
        self.providers = providers

    def sync_daily_bars(self, symbols: list[str], start_date: str, end_date: str, requested_by: str) -> dict:
        provider_names = [provider.name for provider in self.providers]
        job = self.repository.create_job("sync_daily_bars", requested_by, provider_names)
        self.repository.mark_job_running(job["id"])
        summary = {"success": 0, "skipped": 0, "failed": 0, "retryable": 0, "provider_fallback": 0}

        for symbol in symbols:
            item = {"symbol": symbol, "date_start": start_date, "date_end": end_date, "attempt_count": 0}
            try:
                bars, provider_name, fallback_count = self._fetch_with_fallback(symbol, start_date, end_date)
                summary["provider_fallback"] += fallback_count
                self.repository.upsert_daily_bars(bars)
                self.repository.add_item(job["id"], {**item, "status": "success", "provider": provider_name})
                summary["success"] += 1
            except Exception as exc:  # noqa: BLE001 - sync isolates symbol-level failures.
                self.repository.add_item(
                    job["id"],
                    {**item, "status": "failed", "provider": None, "error_message": str(exc), "attempt_count": len(self.providers)},
                )
                summary["failed"] += 1

        if summary["success"] and summary["failed"]:
            status = "completed_with_errors"
        elif summary["failed"]:
            status = "failed"
        else:
            status = "completed"
        return self.repository.finish_job(job["id"], status, summary)

    def _fetch_with_fallback(self, symbol: str, start_date: str, end_date: str) -> tuple[list[dict], str, int]:
        errors: list[str] = []
        for index, provider in enumerate(self.providers):
            try:
                return provider.fetch_daily_bars(symbol, start_date, end_date), provider.name, index
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
        raise RuntimeError("; ".join(errors) or "no providers configured")
