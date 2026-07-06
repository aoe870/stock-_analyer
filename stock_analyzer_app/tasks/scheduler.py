from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


@dataclass(frozen=True)
class SyncSchedulerGuard:
    repository: object

    def can_start(self, job_type: str) -> bool:
        return not self.repository.has_running_job(job_type)


class SchedulerService:
    def __init__(self, settings, repository, pipeline_factory) -> None:
        self.settings = settings
        self.repository = repository
        self.pipeline_factory = pipeline_factory
        self.scheduler: BackgroundScheduler | None = None

    def start(self) -> None:
        if not self.settings.sync_enabled:
            return
        if self.scheduler and self.scheduler.running:
            return
        hour, minute = [int(part) for part in self.settings.sync_time.split(":", 1)]
        self.scheduler = BackgroundScheduler(timezone=self.settings.timezone)
        self.scheduler.add_job(
            self.run_daily_pipeline_once,
            CronTrigger(hour=hour, minute=minute, timezone=self.settings.timezone),
            id="full_daily_pipeline",
            replace_existing=True,
            max_instances=1,
        )
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def status(self) -> dict:
        if not self.settings.sync_enabled:
            return {"enabled": False, "running": False, "jobs": []}
        jobs = [job.id for job in self.scheduler.get_jobs()] if self.scheduler else []
        return {"enabled": True, "running": bool(self.scheduler and self.scheduler.running), "jobs": jobs}

    def run_daily_pipeline_once(self) -> None:
        if not self.guard_can_start("full_daily_pipeline"):
            return
        target_date = (date.today() - timedelta(days=1)).isoformat()
        job = self.pipeline_factory().run_full_daily_pipeline(start_date=target_date, end_date=target_date, requested_by="scheduler")
        self.retry_failed_job(job)

    def guard_can_start(self, job_type: str, stale_after: timedelta = timedelta(minutes=30)) -> bool:
        if not hasattr(self.repository, "list_jobs"):
            return SyncSchedulerGuard(self.repository).can_start(job_type)
        for job in self.repository.list_jobs():
            if job.get("job_type") != job_type or job.get("status") not in {"pending", "running"}:
                continue
            if self._job_has_recent_activity(job, stale_after):
                return False
            summary = {**job.get("summary", {}), "stale_cancelled": True, "error": "stale running job cancelled by scheduler"}
            self.repository.finish_job(job["id"], "failed", summary)
        return True

    def retry_failed_job(self, job: dict) -> None:
        current_job = job
        for _ in range(max(0, int(getattr(self.settings, "sync_retry_rounds", 1)))):
            retry_job = self._retry_failed_job_once(current_job)
            if retry_job is None:
                return
            current_job = retry_job

    def _retry_failed_job_once(self, job: dict) -> dict | None:
        job_id = job.get("id")
        if not job_id or not hasattr(self.repository, "get_job_items"):
            return None
        failed_items = [
            item
            for item in self.repository.get_job_items(job_id)
            if item.get("status") == "failed" and item.get("symbol")
        ]
        if not failed_items:
            return None
        symbols = sorted({item["symbol"] for item in failed_items})
        start_dates = [str(item["date_start"]) for item in failed_items if item.get("date_start")]
        end_dates = [str(item["date_end"]) for item in failed_items if item.get("date_end")]
        pipeline = self.pipeline_factory()
        retry_workers = getattr(self.settings, "sync_retry_max_workers", None)
        if retry_workers and hasattr(pipeline, "max_workers"):
            pipeline.max_workers = max(1, min(int(pipeline.max_workers), int(retry_workers)))
        return pipeline.run_full_daily_pipeline(
            start_date=min(start_dates) if start_dates else (date.today() - timedelta(days=1)).isoformat(),
            end_date=max(end_dates) if end_dates else (date.today() - timedelta(days=1)).isoformat(),
            requested_by=f"retry:{job_id}",
            symbols=symbols,
        )

    def _job_has_recent_activity(self, job: dict, stale_after: timedelta) -> bool:
        timestamps = [job.get("started_at")]
        if job.get("status") == "pending":
            timestamps.append(job.get("created_at"))
        try:
            if hasattr(self.repository, "get_job_items"):
                timestamps.extend(item.get("updated_at") for item in self.repository.get_job_items(job["id"]))
        except Exception:  # noqa: BLE001 - stale detection should not break scheduler execution.
            pass
        parsed = [_parse_timestamp(value) for value in timestamps if value]
        if not parsed:
            return True
        return datetime.now(timezone.utc) - max(parsed) <= stale_after


def _parse_timestamp(value) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
