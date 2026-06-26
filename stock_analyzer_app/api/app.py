from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import pymysql

from stock_analyzer_app.backtest import CoverageError, run_backtest_from_repository
from stock_analyzer_app.config import AppSettings
from stock_analyzer_app.data.sample import sample_symbol_bars
from stock_analyzer_app.data_provider.demo_provider import DemoAshareProvider
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain
from stock_analyzer_app.screening import screen_from_repository, screen_latest
from stock_analyzer_app.storage.repositories import InMemoryAnalysisRepository
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available
from stock_analyzer_app.sync import InMemorySyncRepository, SyncService
from stock_analyzer_app.sync.pipeline import DailySyncPipeline
from stock_analyzer_app.tasks.scheduler import SchedulerService


PUBLIC_DIR = Path(__file__).resolve().parents[2] / "public"


class RuntimeState:
    def __init__(self) -> None:
        self.settings = AppSettings.from_env()
        self.analysis_repository = InMemoryAnalysisRepository()
        self.sync_repository = InMemorySyncRepository()
        self.sync_service = SyncService(self.sync_repository, providers=[])
        self.screening_tasks: dict[str, dict] = {}
        self.backtest_tasks: dict[str, dict] = {}
        self.backtest_runs: list[dict] = []
        self.scheduler_service: SchedulerService | None = None
        self.configure_repositories()

    def configure_repositories(self) -> None:
        self.settings = AppSettings.from_env()
        if mysql_available(self.settings):
            repository = MySqlRepository(self.settings)
            self.analysis_repository = repository
            self.sync_repository = repository
        else:
            self.analysis_repository = InMemoryAnalysisRepository()
            self.sync_repository = InMemorySyncRepository()
        self.sync_service = SyncService(self.sync_repository, providers=[])
        self.scheduler_service = SchedulerService(
            self.settings,
            self.sync_repository,
            pipeline_factory=self.make_daily_pipeline,
        )

    def start_scheduler(self) -> None:
        if self.scheduler_service:
            self.scheduler_service.start()

    def build_sync_providers(self):
        providers = build_provider_chain(self.settings).providers
        return providers or [DemoAshareProvider()]

    def make_daily_pipeline(self) -> DailySyncPipeline:
        return DailySyncPipeline(self.sync_repository, self.build_sync_providers())


runtime = RuntimeState()


class SyncJobRequest(BaseModel):
    job_type: str
    symbols: list[str] = Field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None


class ScreenRequest(BaseModel):
    trade_date: str | None = None
    symbols: list[str] | None = None
    signal_filter: str = "all"
    price_mode: str = "forward_adjusted"


class BacktestRequest(BaseModel):
    symbols: list[str] | None = None
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    initial_capital: float = Field(default=100000, gt=0)
    fee_rate: float = Field(default=0.0003, ge=0)
    slippage_rate: float = Field(default=0.0005, ge=0)
    price_mode: str = "forward_adjusted"
    allow_partial_coverage: bool = False


def create_app() -> FastAPI:
    app = FastAPI(title="EXPMA Stock Analyzer")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if PUBLIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")

    @app.get("/", response_model=None)
    def index():
        index_file = PUBLIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"status": "ui not built"}

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        jobs = _list_sync_jobs()
        latest_success = next((job for job in jobs if job["status"] == "completed"), None)
        db_health = _database_health(runtime.settings)
        return {
            "api": "ok",
            "database": db_health["database"],
            "migrations": db_health["migrations"],
            "scheduler": runtime.scheduler_service.status() if runtime.scheduler_service else {"enabled": False, "running": False, "jobs": []},
            "latest_successful_sync_job": latest_success,
        }

    @app.get("/api/settings")
    def get_settings() -> dict[str, Any]:
        return {
            "mysql": {
                "host": runtime.settings.db.host,
                "port": runtime.settings.db.port,
                "database": runtime.settings.db.name,
                "user": runtime.settings.db.user,
            },
            "data_source_priority": runtime.settings.provider_priority,
            "tushare_token_configured": bool(runtime.settings.tushare_token),
            "sync_enabled": runtime.settings.sync_enabled,
            "sync_time": runtime.settings.sync_time,
            "fee_rate": 0.0003,
            "slippage_rate": 0.0005,
            "default_price_mode": "forward_adjusted",
        }

    @app.put("/api/settings")
    def put_settings(settings: dict[str, Any]) -> dict[str, Any]:
        return {"saved": True, "settings": settings}

    @app.get("/api/strategies")
    def strategies() -> list[dict[str, Any]]:
        return [
            {
                "id": "expma_17_50",
                "name": "EXPMA17/50 Trend Pullback",
                "signals": ["BUY", "HALF_SELL", "RE_BUY", "CLEAR_1", "CLEAR_2", "RE_BUY_50"],
            }
        ]

    @app.get("/api/sample")
    def sample() -> dict[str, Any]:
        return {"symbols": sample_symbol_bars()}

    @app.post("/api/sync/jobs")
    def create_sync_job(request: SyncJobRequest) -> dict[str, Any]:
        if request.job_type == "full_daily_pipeline":
            pipeline = runtime.make_daily_pipeline()
            start_date = request.start_date or "2024-01-01"
            end_date = request.end_date or "2024-12-31"
            job = pipeline.run_full_daily_pipeline(start_date=start_date, end_date=end_date, requested_by="manual", symbols=request.symbols or None)
            return {**job, "task_id": str(job["id"])}
        job = runtime.sync_repository.create_job(request.job_type, "manual", runtime.settings.provider_priority)
        runtime.sync_repository.mark_job_running(job["id"])
        summary = {"success": 0, "skipped": len(request.symbols), "failed": 0, "retryable": 0, "provider_fallback": 0}
        for symbol in request.symbols:
            runtime.sync_repository.add_item(
                job["id"],
                {
                    "symbol": symbol,
                    "date_start": request.start_date,
                    "date_end": request.end_date,
                    "status": "skipped",
                    "provider": None,
                    "attempt_count": 0,
                    "error_message": "no live provider configured in local test runtime",
                },
            )
        finished = runtime.sync_repository.finish_job(job["id"], "completed", summary)
        return {**finished, "task_id": str(finished["id"])}

    @app.get("/api/sync/jobs")
    def list_sync_jobs() -> dict[str, Any]:
        return {"jobs": _list_sync_jobs()}

    @app.get("/api/sync/jobs/{job_id}")
    def get_sync_job(job_id: int) -> dict[str, Any]:
        try:
            job = runtime.sync_repository.get_job(job_id)
        except (KeyError, AttributeError):
            raise HTTPException(status_code=404, detail="sync job not found")
        return job

    @app.get("/api/sync/jobs/{job_id}/items")
    def get_sync_job_items(job_id: int) -> dict[str, Any]:
        if hasattr(runtime.sync_repository, "get_job_items"):
            return {"job_id": job_id, "items": runtime.sync_repository.get_job_items(job_id)}
        return {"job_id": job_id, "items": runtime.sync_repository.items.get(job_id, [])}

    @app.post("/api/sync/jobs/{job_id}/retry")
    def retry_sync_job(job_id: int) -> dict[str, Any]:
        try:
            runtime.sync_repository.get_job(job_id)
        except (KeyError, AttributeError):
            raise HTTPException(status_code=404, detail="sync job not found")
        return {"task_id": str(job_id), "status": "retry_queued"}

    @app.get("/api/sync/coverage")
    def sync_coverage() -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "coverage"):
            return runtime.analysis_repository.coverage()
        rows = sum(len(rows) for rows in runtime.analysis_repository.rows.values())
        return {
            "analysis_daily_bars": {"symbols": len(runtime.analysis_repository.rows), "rows": rows, "price_mode": "forward_adjusted"},
            "daily_indicators": {"rows": rows},
            "strategy_signals": {"rows": rows},
        }

    @app.get("/api/stocks")
    def list_stocks() -> dict[str, Any]:
        return {"stocks": runtime.analysis_repository.list_stocks()}

    @app.get("/api/stocks/{symbol}")
    def get_stock(symbol: str) -> dict[str, Any]:
        stock = runtime.analysis_repository.get_stock(symbol)
        if not stock:
            raise HTTPException(status_code=404, detail="stock not found")
        return stock

    @app.get("/api/stocks/{symbol}/bars")
    def stock_bars(symbol: str) -> list[dict]:
        return runtime.analysis_repository.bars(symbol)

    @app.get("/api/stocks/{symbol}/indicators")
    def stock_indicators(symbol: str) -> list[dict]:
        return runtime.analysis_repository.indicators(symbol)

    @app.get("/api/stocks/{symbol}/signals")
    def stock_signals(symbol: str) -> list[dict]:
        return runtime.analysis_repository.signals(symbol)

    @app.post("/api/screen")
    def screen_legacy(request: ScreenRequest) -> dict[str, Any]:
        return screen_latest(sample_symbol_bars(), trade_date=request.trade_date, signal_filter=request.signal_filter)

    @app.post("/api/screenings")
    def create_screening(request: ScreenRequest) -> dict[str, Any]:
        trade_date = request.trade_date or "9999-12-31"
        persisted_run = None
        if hasattr(runtime.analysis_repository, "create_screening_run"):
            persisted_run = runtime.analysis_repository.create_screening_run(
                strategy_key="expma_17_50",
                trade_date=trade_date,
                universe=request.symbols or [stock["symbol"] for stock in runtime.analysis_repository.list_stocks()],
                filters={"signal_filter": request.signal_filter, "price_mode": request.price_mode},
            )
        result = screen_from_repository(
            runtime.analysis_repository,
            trade_date=trade_date,
            symbols=request.symbols,
            price_mode=request.price_mode,
            signal_filter=request.signal_filter,
        )
        if persisted_run is not None:
            runtime.analysis_repository.finish_screening_run(persisted_run["id"], result["summary"], result["results"])
            task_id = str(persisted_run["id"])
        else:
            task_id = str(len(runtime.screening_tasks) + 1)
        task = {"task_id": task_id, "status": "completed", "request": request.model_dump(), **result}
        runtime.screening_tasks[task_id] = task
        return task

    @app.get("/api/screenings/{task_id}")
    def get_screening(task_id: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "get_screening_run"):
            try:
                run = runtime.analysis_repository.get_screening_run(int(task_id))
                return {"task_id": task_id, "status": run["status"], "summary": run["summary"], "request": {"trade_date": str(run["trade_date"]), "symbols": run["universe"], **run["filters"]}}
            except (KeyError, ValueError):
                pass
        task = runtime.screening_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="screening task not found")
        return {key: value for key, value in task.items() if key != "results"}

    @app.get("/api/screenings/{task_id}/results")
    def get_screening_results(task_id: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "get_screening_results"):
            try:
                run = runtime.analysis_repository.get_screening_run(int(task_id))
                return {"task_id": task_id, "results": runtime.analysis_repository.get_screening_results(int(task_id)), "summary": run["summary"]}
            except (KeyError, ValueError):
                pass
        task = runtime.screening_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="screening task not found")
        return {"task_id": task_id, "results": task["results"], "summary": task["summary"]}

    @app.post("/api/backtest")
    def backtest_legacy(request: BacktestRequest) -> dict[str, Any]:
        return _run_backtest_request(request)

    @app.post("/api/backtests")
    def create_backtest(request: BacktestRequest) -> dict[str, Any]:
        persisted_run = None
        symbols = request.symbols or [stock["symbol"] for stock in runtime.analysis_repository.list_stocks()]
        if hasattr(runtime.analysis_repository, "create_backtest_run"):
            persisted_run = runtime.analysis_repository.create_backtest_run(
                strategy_key="expma_17_50",
                symbols=symbols,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital,
                fee_rate=request.fee_rate,
                slippage_rate=request.slippage_rate,
                price_mode=request.price_mode,
                allow_partial_coverage=request.allow_partial_coverage,
            )
        result = _run_backtest_request(request)
        if persisted_run is not None:
            runtime.analysis_repository.finish_backtest_run(
                persisted_run["id"],
                summary=result["summary"],
                coverage=result.get("coverage", {}),
                trades=result.get("trades", []),
                equity=result.get("equity", []),
            )
            task_id = str(persisted_run["id"])
        else:
            task_id = str(len(runtime.backtest_tasks) + 1)
        task = {"task_id": task_id, "status": "completed", "request": request.model_dump(), **result}
        runtime.backtest_tasks[task_id] = task
        runtime.backtest_runs.append(task)
        return task

    @app.get("/api/backtests/runs")
    def backtest_runs() -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "list_backtest_runs"):
            return {"runs": runtime.analysis_repository.list_backtest_runs()}
        return {"runs": [{key: value for key, value in run.items() if key not in {"trades", "equity", "positions"}} for run in runtime.backtest_runs]}

    @app.get("/api/backtests/runs/{run_id}")
    def backtest_run(run_id: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "get_backtest_run"):
            try:
                run = runtime.analysis_repository.get_backtest_run(int(run_id))
                return {"task_id": run_id, "status": run["status"], **run}
            except (KeyError, ValueError):
                pass
        task = runtime.backtest_tasks.get(run_id)
        if not task:
            raise HTTPException(status_code=404, detail="backtest run not found")
        return task

    @app.get("/api/backtests/{task_id}")
    def get_backtest(task_id: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "get_backtest_run"):
            try:
                run = runtime.analysis_repository.get_backtest_run(int(task_id), include_details=False)
                return {"task_id": task_id, "status": run["status"], **run}
            except (KeyError, ValueError):
                pass
        task = runtime.backtest_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="backtest task not found")
        return {key: value for key, value in task.items() if key not in {"trades", "equity", "positions"}}

    return app


def _run_backtest_request(request: BacktestRequest) -> dict[str, Any]:
    symbols = request.symbols or [stock["symbol"] for stock in runtime.analysis_repository.list_stocks()]
    try:
        return run_backtest_from_repository(
            runtime.analysis_repository,
            symbols=symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            price_mode=request.price_mode,
            allow_partial_coverage=request.allow_partial_coverage,
            initial_capital=request.initial_capital,
            fee_rate=request.fee_rate,
            slippage_rate=request.slippage_rate,
        )
    except CoverageError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


app = create_app()


def _list_sync_jobs() -> list[dict]:
    if hasattr(runtime.sync_repository, "list_jobs"):
        return runtime.sync_repository.list_jobs()
    return sorted(runtime.sync_repository.jobs.values(), key=lambda item: item["id"], reverse=True)


def _database_health(settings: AppSettings) -> dict[str, Any]:
    configured = bool(settings.db.host and settings.db.name and settings.db.user)
    if not configured:
        return {
            "database": {"configured": False, "connected": False, "message": "database settings missing"},
            "migrations": {"applied": None, "status": "not_checked"},
        }
    try:
        connection = pymysql.connect(
            host=settings.db.host,
            port=settings.db.port,
            user=settings.db.user,
            password=settings.db.password,
            database=settings.db.name,
            connect_timeout=2,
            read_timeout=2,
            write_timeout=2,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM schema_migrations")
                migration_count = cursor.fetchone()["count"]
        return {
            "database": {"configured": True, "connected": True, "message": "ok"},
            "migrations": {"applied": migration_count, "status": "ok" if migration_count >= 3 else "incomplete"},
        }
    except Exception as exc:  # noqa: BLE001 - health should report failure, not crash.
        return {
            "database": {"configured": True, "connected": False, "message": str(exc)},
            "migrations": {"applied": None, "status": "not_checked"},
        }
