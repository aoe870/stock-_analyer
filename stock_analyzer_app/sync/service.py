from dataclasses import dataclass, field
from datetime import datetime, timezone

from stock_analyzer_app.data_provider.base import StockDataProvider


RUNNING_STATUSES = {"pending", "running"}


@dataclass
class InMemorySyncRepository:
    jobs: dict[int, dict] = field(default_factory=dict)
    items: dict[int, list[dict]] = field(default_factory=dict)
    daily_bars: list[dict] = field(default_factory=list)
    _next_id: int = 1

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
