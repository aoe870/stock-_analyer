from pathlib import Path
import re


def _service_block(compose: str, service_name: str) -> str:
    marker = f"  {service_name}:\n"
    start = compose.index(marker)
    match = re.search(r"\n  [A-Za-z0-9_-]+:\n", compose[start + len(marker) :])
    return compose[start:] if not match else compose[start : start + len(marker) + match.start()]


def test_docker_compose_splits_api_and_collector_services():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "  api:\n" in compose
    assert "  collector:\n" in compose

    api = _service_block(compose, "api")
    collector = _service_block(compose, "collector")

    assert "python -m stock_analyzer_app api" in api
    assert "python -m stock_analyzer_app collector" in collector
    for mount in ["./stock_analyzer_app:/app/stock_analyzer_app", "./public:/app/public", "./db:/app/db"]:
        assert mount in api
        assert mount in collector
    for key in [
        "STOCK_ANALYZER_PROVIDER_PRIORITY",
        "STOCK_ANALYZER_MIANA_TOKEN",
        "STOCK_ANALYZER_MIANA_BASE_URL",
        "STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE",
        "STOCK_ANALYZER_MIANA_REQUEST_TIMEOUT_SECONDS",
        "STOCK_ANALYZER_TUSHARE_TOKEN",
    ]:
        assert key in api
        assert key in collector
