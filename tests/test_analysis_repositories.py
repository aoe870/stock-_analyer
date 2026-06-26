import pytest

from stock_analyzer_app.backtest import CoverageError, run_backtest_from_repository
from stock_analyzer_app.screening import screen_from_repository


class FakeAnalysisRepository:
    def __init__(self):
        self.called = []
        self.rows = {
            "AAA": [
                {
                    "symbol": "AAA",
                    "name": "Alpha",
                    "trade_date": "2024-01-01",
                    "open": 10,
                    "high": 11,
                    "low": 9,
                    "close": 10,
                    "volume": 100,
                    "amount": 1000,
                    "price_mode": "forward_adjusted",
                    "source": "mysql",
                    "data_quality": "ok",
                    "expma17": 10.5,
                    "expma50": 9.5,
                    "selected_signal": "BUY",
                    "raw_flags": {"buy": True},
                    "trend_state": "above_expma17_expma50",
                },
                {
                    "symbol": "AAA",
                    "name": "Alpha",
                    "trade_date": "2024-01-02",
                    "open": 11,
                    "high": 13,
                    "low": 10,
                    "close": 12,
                    "volume": 100,
                    "amount": 1200,
                    "price_mode": "forward_adjusted",
                    "source": "mysql",
                    "data_quality": "ok",
                    "expma17": 11,
                    "expma50": 10,
                    "selected_signal": None,
                    "raw_flags": {},
                    "trend_state": "above_expma17_expma50",
                },
            ],
            "BBB": [],
        }

    def latest_screening_rows(self, trade_date, symbols=None, price_mode="forward_adjusted"):
        self.called.append(("latest_screening_rows", trade_date, tuple(symbols or []), price_mode))
        rows = []
        for symbol in symbols or self.rows:
            candidates = [row for row in self.rows.get(symbol, []) if row["trade_date"] <= trade_date]
            if candidates:
                rows.append(candidates[-1])
        return rows

    def analysis_bars_with_signals(self, symbols, start_date, end_date, price_mode="forward_adjusted"):
        self.called.append(("analysis_bars_with_signals", tuple(symbols), start_date, end_date, price_mode))
        return {
            symbol: [
                row
                for row in self.rows.get(symbol, [])
                if start_date <= row["trade_date"] <= end_date and row["data_quality"] == "ok"
            ]
            for symbol in symbols
        }


def test_screening_reads_latest_materialized_rows_from_repository():
    repository = FakeAnalysisRepository()

    result = screen_from_repository(repository, trade_date="2024-01-02", symbols=["AAA", "BBB"])

    assert repository.called[0][0] == "latest_screening_rows"
    assert result["summary"]["evaluated"] == 1
    assert result["summary"]["missing"] == 1
    assert result["results"][0]["symbol"] == "AAA"
    assert result["results"][0]["data_quality"] == "ok"


def test_backtest_repository_entry_rejects_missing_coverage_by_default():
    repository = FakeAnalysisRepository()

    with pytest.raises(CoverageError) as exc:
        run_backtest_from_repository(repository, ["AAA", "BBB"], "2024-01-01", "2024-01-02")

    assert "BBB" in str(exc.value)


def test_backtest_repository_entry_allows_partial_coverage_when_requested():
    repository = FakeAnalysisRepository()

    result = run_backtest_from_repository(
        repository,
        ["AAA", "BBB"],
        "2024-01-01",
        "2024-01-02",
        allow_partial_coverage=True,
        initial_capital=1000,
        fee_rate=0,
        slippage_rate=0,
    )

    assert result["coverage"]["evaluated_symbols"] == ["AAA"]
    assert result["coverage"]["missing_symbols"] == ["BBB"]
    assert result["summary"]["initial_capital"] == 1000

