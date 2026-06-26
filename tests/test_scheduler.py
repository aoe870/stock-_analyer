from stock_analyzer_app.config import AppSettings, DatabaseSettings
from stock_analyzer_app.sync.service import InMemorySyncRepository
from stock_analyzer_app.tasks.scheduler import SchedulerService


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

