import argparse
import json
import re
from pathlib import Path

from stock_analyzer_app.config import AppSettings
from stock_analyzer_app.data_provider.provider_chain import build_provider_chain
from stock_analyzer_app.storage.mysql import MySqlRepository
from stock_analyzer_app.sync.pipeline import DailySyncPipeline


SYMBOL_PATTERN = re.compile(r"^[0-9]{6}\.(SH|SZ|BJ)$")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols-file", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--requested-by", default="manual_remaining")
    parser.add_argument("--max-workers", type=int, default=None)
    args = parser.parse_args()

    symbols = [
        line.strip()
        for line in Path(args.symbols_file).read_text(encoding="utf-8-sig").splitlines()
        if SYMBOL_PATTERN.match(line.strip())
    ]
    if not symbols:
        raise SystemExit("no valid symbols to sync")

    settings = AppSettings.from_env()
    repository = MySqlRepository(settings)
    providers = build_provider_chain(settings).providers
    pipeline = DailySyncPipeline(repository, providers, max_workers=args.max_workers or settings.sync_max_workers)
    job = pipeline.run_full_daily_pipeline(
        start_date=args.start_date,
        end_date=args.end_date,
        requested_by=args.requested_by,
        symbols=symbols,
    )
    print(json.dumps(job, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
