from dataclasses import dataclass
from datetime import date

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
        guard = SyncSchedulerGuard(self.repository)
        if not guard.can_start("full_daily_pipeline"):
            return
        today = date.today().isoformat()
        self.pipeline_factory().run_full_daily_pipeline(start_date=today, end_date=today, requested_by="scheduler")
