from pathlib import Path
from typing import Any
from datetime import date, datetime, timedelta, timezone

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
from stock_analyzer_app.screening import screen_from_repository
from stock_analyzer_app.storage.repositories import InMemoryAnalysisRepository
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available
from stock_analyzer_app.sync import InMemorySyncRepository
from stock_analyzer_app.sync.pipeline import DailySyncPipeline
from stock_analyzer_app.tasks.scheduler import SchedulerService


PUBLIC_DIR = Path(__file__).resolve().parents[2] / "public"


class RuntimeState:
    def __init__(self) -> None:
        self.settings = AppSettings.from_env()
        self.analysis_repository = InMemoryAnalysisRepository()
        self.sync_repository = InMemorySyncRepository()
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
        return DailySyncPipeline(
            self.sync_repository,
            self.build_sync_providers(),
            max_workers=self.settings.sync_max_workers,
            include_optional_metadata=self.settings.sync_include_optional_metadata,
        )


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
            "sync_max_workers": runtime.settings.sync_max_workers,
            "sync_retry_max_workers": runtime.settings.sync_retry_max_workers,
            "sync_retry_rounds": runtime.settings.sync_retry_rounds,
            "sync_include_optional_metadata": runtime.settings.sync_include_optional_metadata,
            "miana_max_requests_per_minute": runtime.settings.miana_max_requests_per_minute,
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

    @app.post("/api/sync/jobs", status_code=202)
    def create_sync_job(request: SyncJobRequest) -> dict[str, Any]:
        scope = {
            "symbols": request.symbols,
            "start_date": request.start_date,
            "end_date": request.end_date,
        }
        queued = _enqueue_sync_request(
            request.job_type,
            dataset=request.job_type,
            scope={key: value for key, value in scope.items() if value not in (None, [])},
            priority=50,
            reason="manual",
        )
        return {**queued, "request_id": queued["id"]}

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

    @app.post("/api/sync/jobs/{job_id}/retry", status_code=202)
    def retry_sync_job(job_id: int) -> dict[str, Any]:
        try:
            source_job = runtime.sync_repository.get_job(job_id)
        except (KeyError, AttributeError):
            raise HTTPException(status_code=404, detail="sync job not found")
        retry_request = _failed_retry_request(job_id)
        if not retry_request["symbols"]:
            raise HTTPException(status_code=409, detail="sync job has no failed items to retry")
        queued = _enqueue_sync_request(
            source_job["job_type"],
            dataset=source_job["job_type"],
            scope=retry_request,
            priority=90,
            reason=f"retry:{job_id}",
        )
        return {**queued, "request_id": queued["id"]}

    @app.get("/api/sync/requests")
    def list_sync_requests() -> dict[str, Any]:
        if hasattr(runtime.sync_repository, "list_sync_requests"):
            return {"requests": runtime.sync_repository.list_sync_requests()}
        return {"requests": []}

    @app.get("/api/sync/requests/{request_id}")
    def get_sync_request(request_id: int) -> dict[str, Any]:
        try:
            return runtime.sync_repository.get_sync_request(request_id)
        except (KeyError, AttributeError):
            raise HTTPException(status_code=404, detail="sync request not found")

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

    @app.get("/api/sync/readiness")
    def sync_readiness() -> dict[str, Any]:
        return _sync_readiness()

    @app.get("/api/market/dashboard")
    def market_dashboard() -> dict[str, Any]:
        data_status = _dashboard_data_status()
        if hasattr(runtime.analysis_repository, "market_dashboard_snapshot"):
            dashboard = _enrich_market_dashboard(runtime.analysis_repository.market_dashboard_snapshot())
            dashboard["data_status"] = data_status
            return dashboard
        readiness = _sync_readiness()
        rows = runtime.analysis_repository.latest_screening_rows("9999-12-31")
        ranked = sorted(rows, key=lambda row: float(row.get("amount") or 0), reverse=True)[:20]
        dashboard = _enrich_market_dashboard({
            "indexes": [],
            "sectors": [],
            "rankings": {
                "gainers": [],
                "losers": [],
                "amount": ranked,
            },
            "breadth": {
                "up": 0,
                "down": 0,
                "flat": len(rows),
            },
            "freshness": {
                "latest_trade_date": readiness.get("latest_trade_date"),
                "ready_for_analysis": readiness.get("ready_for_analysis", False),
                "updated_symbols": readiness.get("updated_symbols", 0),
                "expected_symbols": readiness.get("expected_symbols", 0),
            },
        })
        dashboard["data_status"] = data_status
        return dashboard

    @app.get("/api/data-center/coverage")
    def data_center_coverage() -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "data_center_coverage"):
            return runtime.analysis_repository.data_center_coverage()
        coverage = sync_coverage()
        readiness = _sync_readiness()
        return {
            "core": coverage,
            "research": {
                "financial_statements": {"symbols": 0, "rows": 0},
                "capital_flow": {"symbols": 0, "rows": 0},
                "company_profiles": {"symbols": 0, "rows": 0},
                "corporate_actions": {"symbols": 0, "rows": 0},
                "share_capital": {"symbols": 0, "rows": 0},
                "holders": {"symbols": 0, "rows": 0},
                "officers": {"symbols": 0, "rows": 0},
                "officer_rewards": {"symbols": 0, "rows": 0},
            },
            "market_structure": {
                "indexes": {"rows": 0},
                "sectors": {"rows": 0},
                "index_constituents": {"rows": 0},
                "sector_constituents": {"rows": 0},
            },
            "sync": {
                "readiness": readiness,
                "jobs": _list_sync_jobs()[:10],
            },
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

    @app.get("/api/stocks/{symbol}/overview")
    def stock_overview(symbol: str, refresh_missing: bool = False) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "stock_research_snapshot"):
            snapshot = runtime.analysis_repository.stock_research_snapshot(symbol)
            if refresh_missing and _needs_enterprise_refresh(snapshot):
                _enqueue_enterprise_on_demand_request(symbol)
            return snapshot
        stock = next((row for row in runtime.analysis_repository.list_stocks() if row["symbol"] == symbol), None)
        if not stock:
            raise HTTPException(status_code=404, detail="stock not found")
        bars = runtime.analysis_repository.bars(symbol)
        latest_bar = bars[-1] if bars else None
        return {
            "stock": stock,
            "latest_bar": latest_bar,
            "company_profile": None,
            "share_capital": [],
            "corporate_actions": [],
            "holders": [],
            "officers": [],
            "officer_rewards": [],
            "data_quality": {
                "has_bars": bool(bars),
                "has_research_data": False,
                "enterprise_modules": {
                    "company_profile": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "share_capital": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "corporate_actions": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "holders": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "officers": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "officer_rewards": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                    "capital_flow": {"rows": 0, "status": "missing", "newest_date": None, "provider": None},
                },
            },
        }

    @app.get("/api/stocks/{symbol}/financials")
    def stock_financials(symbol: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "stock_financials"):
            return runtime.analysis_repository.stock_financials(symbol)
        return {"symbol": symbol, "income": [], "balance": [], "cashflow": [], "summary": {"latest_report_date": None, "income_rows": 0, "balance_rows": 0, "cashflow_rows": 0}}

    @app.get("/api/stocks/{symbol}/capital-flow")
    def stock_capital_flow(symbol: str) -> dict[str, Any]:
        if hasattr(runtime.analysis_repository, "stock_capital_flow"):
            return runtime.analysis_repository.stock_capital_flow(symbol)
        return {"symbol": symbol, "rows": [], "summary": {"latest_trade_date": None, "rows": 0}}

    @app.get("/api/stocks/{symbol}/bars")
    def stock_bars(symbol: str, refresh: bool = False) -> list[dict]:
        if refresh:
            today = date.today().isoformat()
            existing_bars = runtime.analysis_repository.bars(symbol)
            latest_trade_date = max((str(row["trade_date"]) for row in existing_bars), default=None)
            start_date = (date.fromisoformat(latest_trade_date) + timedelta(days=1)).isoformat() if latest_trade_date else today
            _enqueue_sync_request(
                "full_daily_pipeline",
                dataset="stock_bars",
                scope={"start_date": start_date, "end_date": today, "symbols": [symbol]},
                priority=80,
                reason=f"detail:{symbol}",
            )
        return runtime.analysis_repository.bars(symbol)

    @app.get("/api/stocks/{symbol}/indicators")
    def stock_indicators(symbol: str) -> list[dict]:
        return runtime.analysis_repository.indicators(symbol)

    @app.get("/api/stocks/{symbol}/signals")
    def stock_signals(symbol: str) -> list[dict]:
        return runtime.analysis_repository.signals(symbol)

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


def _needs_enterprise_refresh(snapshot: dict[str, Any]) -> bool:
    modules = snapshot.get("data_quality", {}).get("enterprise_modules", {})
    if not modules:
        return False
    watched_modules = ["holders", "officers", "officer_rewards"]
    return not any(int((modules.get(key) or {}).get("rows") or 0) > 0 for key in watched_modules)


def _list_sync_jobs() -> list[dict]:
    if hasattr(runtime.sync_repository, "list_jobs"):
        return runtime.sync_repository.list_jobs()
    return sorted(runtime.sync_repository.jobs.values(), key=lambda item: item["id"], reverse=True)


def _failed_retry_request(job_id: int) -> dict[str, Any]:
    if not hasattr(runtime.sync_repository, "get_job_items"):
        return {"symbols": [], "start_date": None, "end_date": None}
    failed_items = [
        item
        for item in runtime.sync_repository.get_job_items(job_id)
        if item.get("status") == "failed" and item.get("symbol")
    ]
    symbols = sorted({item["symbol"] for item in failed_items})
    start_dates = [str(item["date_start"]) for item in failed_items if item.get("date_start")]
    end_dates = [str(item["date_end"]) for item in failed_items if item.get("date_end")]
    return {
        "symbols": symbols,
        "start_date": min(start_dates) if start_dates else "2024-01-01",
        "end_date": max(end_dates) if end_dates else "2024-12-31",
    }


def _sync_readiness() -> dict[str, Any]:
    if hasattr(runtime.analysis_repository, "sync_readiness"):
        return runtime.analysis_repository.sync_readiness()
    stocks = runtime.analysis_repository.list_stocks()
    expected_symbols = sorted({stock["symbol"] for stock in stocks if stock.get("is_active", True)})
    rows = runtime.analysis_repository.latest_screening_rows("9999-12-31", symbols=expected_symbols or None)
    latest_trade_date = max((str(row["trade_date"]) for row in rows), default=None)
    updated_symbols = sorted({row["symbol"] for row in rows if latest_trade_date and str(row["trade_date"]) == latest_trade_date})
    updated_symbol_set = set(updated_symbols)
    missing_symbols = [symbol for symbol in expected_symbols if symbol not in updated_symbol_set]
    latest_job = next((job for job in _list_sync_jobs() if job.get("job_type") == "full_daily_pipeline"), None)
    failed_symbols: list[str] = []
    if latest_job and hasattr(runtime.sync_repository, "get_job_items"):
        failed_symbols = sorted(
            {
                item["symbol"]
                for item in runtime.sync_repository.get_job_items(latest_job["id"])
                if item.get("status") == "failed" and item.get("symbol")
            }
        )
    return {
        "latest_trade_date": latest_trade_date,
        "expected_symbols": len(expected_symbols),
        "updated_symbols": len(updated_symbols),
        "missing_symbol_count": len(missing_symbols),
        "missing_symbols": missing_symbols,
        "failed_symbol_count": len(failed_symbols),
        "failed_symbols": failed_symbols,
        "latest_sync_job": latest_job,
        "ready_for_analysis": bool(expected_symbols) and not missing_symbols and not failed_symbols,
    }


def _enqueue_sync_request(
    request_type: str,
    dataset: str | None = None,
    scope: dict | None = None,
    priority: int = 50,
    reason: str | None = None,
    requested_by: str = "api",
) -> dict:
    if not hasattr(runtime.sync_repository, "create_sync_request"):
        raise HTTPException(status_code=501, detail="sync request queue is not configured")
    return runtime.sync_repository.create_sync_request(
        request_type=request_type,
        dataset=dataset or request_type,
        scope=scope or {},
        priority=priority,
        requested_by=requested_by,
        reason=reason,
    )


def _enqueue_enterprise_on_demand_request(symbol: str) -> dict:
    existing = _active_enterprise_on_demand_request(symbol)
    if existing:
        return existing
    if _recent_enterprise_attempt(symbol):
        return {
            "request_type": "fundamental_refresh_pipeline",
            "dataset": "stock_research_context",
            "scope": {"symbols": [symbol]},
            "status": "skipped_recent",
            "reason": f"overview:on-demand:{symbol}",
        }
    return _enqueue_sync_request(
        "fundamental_refresh_pipeline",
        dataset="stock_research_context",
        scope={"symbols": [symbol]},
        priority=100,
        reason=f"overview:on-demand:{symbol}",
    )


def _active_enterprise_on_demand_request(symbol: str) -> dict | None:
    if not hasattr(runtime.sync_repository, "list_sync_requests"):
        return None
    for request in runtime.sync_repository.list_sync_requests(1000):
        if request.get("status") not in {"pending", "claimed"}:
            continue
        if request.get("request_type") != "fundamental_refresh_pipeline":
            continue
        if request.get("reason") != f"overview:on-demand:{symbol}":
            continue
        if (request.get("scope") or {}).get("symbols") == [symbol]:
            return request
    return None


def _recent_enterprise_attempt(symbol: str) -> bool:
    if not hasattr(runtime.sync_repository, "get_dataset_freshness"):
        return False
    record = runtime.sync_repository.get_dataset_freshness("stock_research_context", symbol)
    if not record:
        return False
    last_attempt = _parse_timestamp(record.get("last_attempt_at"))
    if last_attempt is None:
        return False
    ttl_days = max(0, int(getattr(runtime.settings, "enterprise_refresh_ttl_days", 7)))
    return datetime.now(timezone.utc) - last_attempt <= timedelta(days=ttl_days)


def _parse_timestamp(value: Any) -> datetime | None:
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


def _dashboard_data_status() -> dict[str, Any]:
    target_date = (date.today() - timedelta(days=1)).isoformat()
    readiness = _sync_readiness()
    latest_trade_date = readiness.get("latest_trade_date")
    if latest_trade_date and str(latest_trade_date) >= target_date:
        return {
            "dataset": "market_dashboard",
            "status": "synced",
            "latest_data_date": str(latest_trade_date),
            "pending_request_id": None,
            "message": None,
        }
    queued = _enqueue_sync_request(
        "full_daily_pipeline",
        dataset="market_dashboard",
        scope={"start_date": target_date, "end_date": target_date},
        priority=70,
        reason="dashboard:auto",
    )
    return {
        "dataset": "market_dashboard",
        "status": "stale" if latest_trade_date else "missing",
        "latest_data_date": str(latest_trade_date) if latest_trade_date else None,
        "pending_request_id": queued["id"],
        "message": "collector has not completed the latest trading day",
    }


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


def _enrich_market_dashboard(snapshot: dict[str, Any]) -> dict[str, Any]:
    enriched = {
        "indexes": snapshot.get("indexes", []),
        "sectors": snapshot.get("sectors", []),
        "rankings": {
            "gainers": [],
            "losers": [],
            "amount": [],
            **(snapshot.get("rankings") or {}),
        },
        "breadth": snapshot.get("breadth", {}),
        "freshness": snapshot.get("freshness", {}),
        "data_source_status": {
            "provider": "local",
            "stock_rankings": "local",
            "index_rankings": "local" if snapshot.get("indexes") else "empty",
            "sector_rankings": "local" if snapshot.get("sectors") else "empty",
            "full_market_realtime": "disabled",
            "errors": [],
        },
    }
    enriched["breadth"] = _market_breadth_from_rankings(enriched["rankings"], enriched["breadth"])
    return enriched


def _market_breadth_from_rankings(rankings: dict[str, list], fallback: dict[str, Any]) -> dict[str, Any]:
    rows = rankings.get("gainers") or rankings.get("amount") or []
    if not rows:
        return fallback
    up = sum(1 for row in rows if float(row.get("change_rate") or 0) > 0)
    down = sum(1 for row in rows if float(row.get("change_rate") or 0) < 0)
    flat = max(0, len(rows) - up - down)
    return {"up": up, "down": down, "flat": flat, "sample_size": len(rows)}
