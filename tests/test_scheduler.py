from datetime import date as real_date, datetime, timedelta, timezone

import stock_analyzer_app.tasks.scheduler as scheduler_module
from stock_analyzer_app.config import AppSettings, DatabaseSettings
from stock_analyzer_app.sync.service import InMemorySyncRepository
from stock_analyzer_app.tasks.scheduler import SchedulerService


def test_settings_default_sync_time_is_midnight(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("STOCK_ANALYZER_SYNC_TIME", raising=False)

    settings = AppSettings.from_env()

    assert settings.sync_time == "00:00"


def settings(sync_enabled=True):
    return AppSettings(
        db=DatabaseSettings("127.0.0.1", 3306, "stock_analyzer", "u", "p"),
        provider_priority=["demo"],
        tushare_token="",
        sync_enabled=sync_enabled,
        sync_time="18:30",
        timezone="Asia/Shanghai",
        log_level="INFO",
    )


def test_scheduler_service_stays_disabled_when_config_says_disabled():
    service = SchedulerService(settings(False), InMemorySyncRepository(), pipeline_factory=lambda: None)

    service.start()

    assert service.status() == {"enabled": False, "running": False, "jobs": []}


def test_scheduler_service_registers_full_daily_pipeline_job_when_enabled():
    service = SchedulerService(settings(True), InMemorySyncRepository(), pipeline_factory=lambda: None)

    service.start()
    status = service.status()
    service.shutdown()

    assert status["enabled"] is True
    assert status["running"] is True
    assert "full_daily_pipeline" in status["jobs"]


def test_scheduler_service_does_not_run_pipeline_when_same_job_is_running():
    repository = InMemorySyncRepository()
    job = repository.create_job("full_daily_pipeline", "scheduler", ["demo"])
    repository.mark_job_running(job["id"])
    called = {"count": 0}

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by):
            called["count"] += 1

    service = SchedulerService(settings(True), repository, pipeline_factory=lambda: Pipeline())
    service.run_daily_pipeline_once()

    assert called["count"] == 0


def test_scheduler_daily_pipeline_syncs_previous_calendar_day(monkeypatch):
    class FixedDate:
        @classmethod
        def today(cls):
            return real_date(2026, 7, 5)

    captured = {}

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            captured.update({"start_date": start_date, "end_date": end_date, "requested_by": requested_by, "symbols": symbols})
            return {"id": 1, "status": "completed", "summary": {"success": 1, "failed": 0}}

    monkeypatch.setattr(scheduler_module, "date", FixedDate)
    service = SchedulerService(settings(True), InMemorySyncRepository(), pipeline_factory=lambda: Pipeline())

    service.run_daily_pipeline_once()

    assert captured == {
        "start_date": "2026-07-04",
        "end_date": "2026-07-04",
        "requested_by": "scheduler",
        "symbols": None,
    }


def test_scheduler_retries_failed_items_after_scheduled_job(monkeypatch):
    class FixedDate:
        @classmethod
        def today(cls):
            return real_date(2026, 7, 5)

    repository = InMemorySyncRepository()
    calls = []

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            calls.append({"start_date": start_date, "end_date": end_date, "requested_by": requested_by, "symbols": symbols})
            if requested_by == "scheduler":
                job = repository.create_job("full_daily_pipeline", requested_by, ["fake"])
                repository.finish_job(job["id"], "completed_with_errors", {"success": 1, "failed": 1})
                repository.add_item(
                    job["id"],
                    {
                        "symbol": "BBB.SZ",
                        "date_start": start_date,
                        "date_end": end_date,
                        "status": "failed",
                        "provider": None,
                        "attempt_count": 1,
                        "error_message": "temporary",
                    },
                )
                return repository.get_job(job["id"])
            return {"id": 99, "status": "completed", "summary": {"success": 1, "failed": 0}}

    monkeypatch.setattr(scheduler_module, "date", FixedDate)
    service = SchedulerService(settings(True), repository, pipeline_factory=lambda: Pipeline())

    service.run_daily_pipeline_once()

    assert calls == [
        {"start_date": "2026-07-04", "end_date": "2026-07-04", "requested_by": "scheduler", "symbols": None},
        {"start_date": "2026-07-04", "end_date": "2026-07-04", "requested_by": "retry:1", "symbols": ["BBB.SZ"]},
    ]


def test_scheduler_guard_allows_start_after_stale_running_job():
    repository = InMemorySyncRepository()
    job = repository.create_job("full_daily_pipeline", "scheduler", ["demo"])
    repository.mark_job_running(job["id"])
    repository.jobs[job["id"]]["started_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

    service = SchedulerService(settings(True), repository, pipeline_factory=lambda: None)

    assert service.guard_can_start("full_daily_pipeline") is True
    assert repository.get_job(job["id"])["status"] == "failed"
