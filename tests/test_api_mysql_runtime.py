import pytest
from fastapi.testclient import TestClient

from stock_analyzer_app.api.app import create_app, runtime
from stock_analyzer_app.config import AppSettings
from stock_analyzer_app.storage.mysql import MySqlRepository, mysql_available


pytestmark = pytest.mark.skipif(
    not mysql_available(AppSettings.from_env()),
    reason="MySQL test database is not available",
)


def test_api_runtime_can_use_mysql_repository_for_coverage():
    runtime.configure_repositories()
    assert isinstance(runtime.analysis_repository, MySqlRepository)

    client = TestClient(create_app())
    coverage = client.get("/api/sync/coverage").json()

    assert "analysis_daily_bars" in coverage
    assert "rows" in coverage["analysis_daily_bars"]

