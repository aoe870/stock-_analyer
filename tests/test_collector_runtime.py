from stock_analyzer_app.sync import InMemorySyncRepository


def test_api_mode_runs_uvicorn_without_starting_scheduler(monkeypatch):
    import stock_analyzer_app.__main__ as main_module

    calls = {"scheduler": 0, "uvicorn": 0}

    monkeypatch.setattr(main_module.runtime, "start_scheduler", lambda: calls.__setitem__("scheduler", calls["scheduler"] + 1))
    monkeypatch.setattr(main_module.uvicorn, "run", lambda *args, **kwargs: calls.__setitem__("uvicorn", calls["uvicorn"] + 1))

    main_module.main(["api"])

    assert calls == {"scheduler": 0, "uvicorn": 1}


def test_collector_processes_pending_full_daily_request():
    from stock_analyzer_app.collector import CollectorService

    repository = InMemorySyncRepository()
    request = repository.create_sync_request(
        "full_daily_pipeline",
        dataset="market_dashboard",
        scope={"start_date": "2026-07-05", "end_date": "2026-07-05"},
        reason="dashboard:auto",
    )
    calls = []

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            calls.append({"start_date": start_date, "end_date": end_date, "requested_by": requested_by, "symbols": symbols})
            return {"id": 7, "status": "completed", "summary": {"success": 1, "failed": 0}}

    collector = CollectorService(repository=repository, pipeline_factory=lambda: Pipeline())

    processed = collector.process_pending_requests(limit=1)

    assert processed == 1
    assert repository.get_sync_request(request["id"])["status"] == "completed"
    assert calls == [
        {"start_date": "2026-07-05", "end_date": "2026-07-05", "requested_by": f"sync_request:{request['id']}", "symbols": None}
    ]


def test_collector_skips_completed_requests_without_starving_pending_work():
    from stock_analyzer_app.collector import CollectorService

    repository = InMemorySyncRepository()
    completed = repository.create_sync_request("full_daily_pipeline", scope={"start_date": "2024-01-01", "end_date": "2024-01-01"}, priority=100)
    repository.finish_sync_request(completed["id"], "completed")
    pending = repository.create_sync_request("full_daily_pipeline", scope={"start_date": "2026-07-05", "end_date": "2026-07-05"}, priority=50)
    calls = []

    class Pipeline:
        def run_full_daily_pipeline(self, start_date, end_date, requested_by, symbols=None):
            calls.append(start_date)

    processed = CollectorService(repository=repository, pipeline_factory=lambda: Pipeline()).process_pending_requests(limit=1)

    assert processed == 1
    assert repository.get_sync_request(pending["id"])["status"] == "completed"
    assert calls == ["2026-07-05"]


def test_collector_enqueues_missing_enterprise_research_batch_before_processing():
    from stock_analyzer_app.collector import CollectorService

    class Repository(InMemorySyncRepository):
        def list_symbols_missing_enterprise_data(self, limit, excluded_symbols=None):
            excluded = set(excluded_symbols or [])
            return [symbol for symbol in ["AAA.SZ", "BBB.SZ"] if symbol not in excluded][:limit]

    repository = Repository()
    calls = []

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            calls.append({"requested_by": requested_by, "symbols": symbols})

    collector = CollectorService(repository=repository, pipeline_factory=lambda: Pipeline(), fundamental_batch_size=2)

    processed = collector.process_pending_requests(limit=1)

    requests = repository.list_sync_requests()
    assert processed == 1
    assert requests[0]["status"] == "completed"
    assert requests[0]["request_type"] == "fundamental_refresh_pipeline"
    assert requests[0]["scope"]["symbols"] == ["AAA.SZ", "BBB.SZ"]
    assert calls == [{"requested_by": f"sync_request:{requests[0]['id']}", "symbols": ["AAA.SZ", "BBB.SZ"]}]


def test_collector_does_not_duplicate_already_queued_enterprise_symbols():
    from stock_analyzer_app.collector import CollectorService

    class Repository(InMemorySyncRepository):
        def list_symbols_missing_enterprise_data(self, limit, excluded_symbols=None):
            excluded = set(excluded_symbols or [])
            return [symbol for symbol in ["AAA.SZ", "BBB.SZ", "CCC.SZ"] if symbol not in excluded][:limit]

    repository = Repository()
    repository.create_sync_request(
        "fundamental_refresh_pipeline",
        dataset="stock_research_context",
        scope={"symbols": ["AAA.SZ"]},
        priority=80,
        reason="overview:auto:AAA.SZ",
    )

    collector = CollectorService(repository=repository, pipeline_factory=lambda: object(), fundamental_batch_size=2)
    created = collector.enqueue_missing_enterprise_research()

    pending_scopes = [
        request["scope"]["symbols"]
        for request in repository.list_sync_requests()
        if request["request_type"] == "fundamental_refresh_pipeline" and request["status"] == "pending"
    ]
    assert created == 1
    assert ["AAA.SZ"] in pending_scopes
    assert ["BBB.SZ", "CCC.SZ"] in pending_scopes


def test_collector_recovers_claimed_requests_left_by_previous_process():
    from stock_analyzer_app.collector import CollectorService

    repository = InMemorySyncRepository()
    request = repository.create_sync_request("fundamental_refresh_pipeline", scope={"symbols": ["AAA.SZ"]})
    repository.claim_sync_request(request["id"])

    recovered = CollectorService(repository=repository, pipeline_factory=lambda: object()).recover_claimed_requests()

    assert recovered == 1
    assert repository.get_sync_request(request["id"])["status"] == "pending"


def test_collector_processes_on_demand_enterprise_request_before_auto_batch():
    from stock_analyzer_app.collector import CollectorService

    repository = InMemorySyncRepository()
    auto = repository.create_sync_request(
        "fundamental_refresh_pipeline",
        dataset="stock_research_context",
        scope={"symbols": ["AUTO1.SZ", "AUTO2.SZ"]},
        priority=40,
        reason="enterprise:auto:missing",
    )
    on_demand = repository.create_sync_request(
        "fundamental_refresh_pipeline",
        dataset="stock_research_context",
        scope={"symbols": ["AAA.SZ"]},
        priority=100,
        reason="overview:on-demand:AAA.SZ",
    )
    calls = []

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            calls.append({"requested_by": requested_by, "symbols": symbols})

    processed = CollectorService(repository=repository, pipeline_factory=lambda: Pipeline(), fundamental_batch_size=0).process_pending_requests(limit=1)

    assert processed == 1
    assert repository.get_sync_request(on_demand["id"])["status"] == "completed"
    assert repository.get_sync_request(auto["id"])["status"] == "pending"
    assert calls == [{"requested_by": f"sync_request:{on_demand['id']}", "symbols": ["AAA.SZ"]}]


def test_collector_filters_recently_attempted_symbols_from_auto_enterprise_batch():
    from stock_analyzer_app.collector import CollectorService

    repository = InMemorySyncRepository()
    request = repository.create_sync_request(
        "fundamental_refresh_pipeline",
        dataset="stock_research_context",
        scope={"symbols": ["AAA.SZ", "BBB.SZ"]},
        priority=40,
        reason="enterprise:auto:missing",
    )
    repository.upsert_dataset_freshness(
        "stock_research_context",
        scope_key="AAA.SZ",
        status="empty",
        rows=0,
        owner_job_type="fundamental_refresh_pipeline",
    )
    calls = []

    class Pipeline:
        def run_fundamental_refresh_pipeline(self, requested_by, symbols=None):
            calls.append({"requested_by": requested_by, "symbols": symbols})

    processed = CollectorService(repository=repository, pipeline_factory=lambda: Pipeline(), fundamental_batch_size=0).process_pending_requests(limit=1)

    assert processed == 1
    assert repository.get_sync_request(request["id"])["status"] == "completed"
    assert calls == [{"requested_by": f"sync_request:{request['id']}", "symbols": ["BBB.SZ"]}]
