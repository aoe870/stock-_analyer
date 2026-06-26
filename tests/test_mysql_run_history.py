import pytest

from stock_analyzer_app.config import AppSettings
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available


pytestmark = pytest.mark.skipif(
    not mysql_available(AppSettings.from_env()),
    reason="MySQL test database is not available",
)


def repo():
    repository = MySqlRepository(AppSettings.from_env())
    repository.clear_test_data(["RUN001.SZ"])
    return repository


def test_mysql_repository_persists_screening_runs_and_results():
    repository = repo()

    run = repository.create_screening_run(
        strategy_key="expma_17_50",
        trade_date="2024-01-02",
        universe=["RUN001.SZ"],
        filters={"signal_filter": "all"},
    )
    repository.finish_screening_run(
        run["id"],
        summary={"evaluated": 1, "missing": 0},
        results=[
            {
                "symbol": "RUN001.SZ",
                "trade_date": "2024-01-02",
                "close": 11,
                "expma17": 10.5,
                "expma50": 9.5,
                "selected_signal": "BUY",
                "trend_state": "above_expma17_expma50",
                "score": 1,
                "reason": {"raw_flags": {"buy": True}},
            }
        ],
    )

    loaded = repository.get_screening_run(run["id"])
    results = repository.get_screening_results(run["id"])

    assert loaded["status"] == "completed"
    assert loaded["summary"]["evaluated"] == 1
    assert results[0]["symbol"] == "RUN001.SZ"
    assert results[0]["selected_signal"] == "BUY"


def test_mysql_repository_persists_backtest_runs_trades_and_equity():
    repository = repo()

    run = repository.create_backtest_run(
        strategy_key="expma_17_50",
        symbols=["RUN001.SZ"],
        start_date="2024-01-01",
        end_date="2024-01-31",
        initial_capital=100000,
        fee_rate=0.0003,
        slippage_rate=0.0005,
        price_mode="forward_adjusted",
        allow_partial_coverage=False,
    )
    repository.finish_backtest_run(
        run["id"],
        summary={"total_return": 0.1, "trade_count": 1},
        coverage={"evaluated_symbols": ["RUN001.SZ"], "missing_symbols": []},
        trades=[
            {
                "symbol": "RUN001.SZ",
                "signal_date": "2024-01-02",
                "trade_date": "2024-01-03",
                "signal": "BUY",
                "side": "BUY",
                "price": 10,
                "quantity": 100,
                "cost": 1,
                "target_position": 1.0,
            }
        ],
        equity=[
            {
                "trade_date": "2024-01-03",
                "equity": 100100,
                "cash": 0,
                "market_value": 100100,
                "drawdown": 0,
                "positions": {"RUN001.SZ": 1.0},
            }
        ],
    )

    loaded = repository.get_backtest_run(run["id"])
    runs = repository.list_backtest_runs()

    assert loaded["status"] == "completed"
    assert loaded["summary"]["trade_count"] == 1
    assert loaded["trades"][0]["symbol"] == "RUN001.SZ"
    assert loaded["equity"][0]["equity"] == 100100.0
    assert any(item["id"] == run["id"] for item in runs)

