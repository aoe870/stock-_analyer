import os
import argparse

import uvicorn
from stock_analyzer_app.api.app import runtime
from stock_analyzer_app.collector import CollectorService


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="stock_analyzer_app")
    parser.add_argument("mode", nargs="?", choices=["api", "collector", "collect"], default="api")
    parser.add_argument("--once", action="store_true", help="process pending collector requests once and exit")
    parser.add_argument("--limit", type=int, default=10, help="maximum queued requests to process in one collector pass")
    parser.add_argument(
        "--fundamental-batch-size",
        type=int,
        default=int(os.getenv("STOCK_ANALYZER_FUNDAMENTAL_BATCH_SIZE", "20")),
        help="number of missing enterprise-research symbols to enqueue per collector pass",
    )
    args = parser.parse_args(argv)
    if args.mode == "api":
        run_api()
        return
    if args.mode == "collector":
        run_collector(once=args.once, limit=args.limit, fundamental_batch_size=args.fundamental_batch_size)
        return
    run_collect_once(limit=args.limit, fundamental_batch_size=args.fundamental_batch_size)


def run_api() -> None:
    host = os.getenv("STOCK_ANALYZER_HOST", "0.0.0.0")
    port = int(os.getenv("STOCK_ANALYZER_PORT", "8000"))
    uvicorn.run("stock_analyzer_app.api:app", host=host, port=port, reload=False)


def run_collector(once: bool = False, limit: int = 10, fundamental_batch_size: int = 20) -> None:
    runtime.start_scheduler()
    collector = CollectorService(runtime.sync_repository, runtime.make_daily_pipeline, fundamental_batch_size=fundamental_batch_size)
    collector.recover_claimed_requests()
    if once:
        collector.process_pending_requests(limit=limit)
        return
    collector.run_forever()


def run_collect_once(limit: int = 10, fundamental_batch_size: int = 20) -> None:
    collector = CollectorService(runtime.sync_repository, runtime.make_daily_pipeline, fundamental_batch_size=fundamental_batch_size)
    collector.recover_claimed_requests()
    collector.process_pending_requests(limit=limit)


if __name__ == "__main__":
    main()
