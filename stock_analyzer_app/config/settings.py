import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str


@dataclass(frozen=True)
class AppSettings:
    db: DatabaseSettings
    provider_priority: list[str]
    tushare_token: str
    sync_enabled: bool
    sync_time: str
    timezone: str
    log_level: str
    miana_token: str = ""
    miana_base_url: str = "http://124.222.142.232:9876/api"
    sync_max_workers: int = 8
    miana_max_requests_per_minute: int = 500
    sync_retry_max_workers: int = 4
    sync_retry_rounds: int = 3
    sync_include_optional_metadata: bool = False
    enterprise_refresh_ttl_days: int = 7

    @classmethod
    def from_env(cls) -> "AppSettings":
        load_dotenv(dotenv_path=Path.cwd() / ".env")
        priority = [
            item.strip()
            for item in os.getenv("STOCK_ANALYZER_PROVIDER_PRIORITY", "tushare,akshare,eastmoney").split(",")
            if item.strip()
        ]
        return cls(
            db=DatabaseSettings(
                host=os.getenv("STOCK_ANALYZER_DB_HOST", "127.0.0.1"),
                port=int(os.getenv("STOCK_ANALYZER_DB_PORT", "3306")),
                name=os.getenv("STOCK_ANALYZER_DB_NAME", "stock_analyzer"),
                user=os.getenv("STOCK_ANALYZER_DB_USER", "stock_analyzer"),
                password=os.getenv("STOCK_ANALYZER_DB_PASSWORD", "change-me"),
            ),
            provider_priority=priority,
            tushare_token=os.getenv("STOCK_ANALYZER_TUSHARE_TOKEN", ""),
            miana_token=os.getenv("STOCK_ANALYZER_MIANA_TOKEN", ""),
            miana_base_url=os.getenv("STOCK_ANALYZER_MIANA_BASE_URL", "http://124.222.142.232:9876/api"),
            sync_max_workers=int(os.getenv("STOCK_ANALYZER_SYNC_MAX_WORKERS", "8")),
            miana_max_requests_per_minute=int(os.getenv("STOCK_ANALYZER_MIANA_MAX_REQUESTS_PER_MINUTE", "500")),
            sync_retry_max_workers=int(os.getenv("STOCK_ANALYZER_SYNC_RETRY_MAX_WORKERS", "4")),
            sync_retry_rounds=int(os.getenv("STOCK_ANALYZER_SYNC_RETRY_ROUNDS", "3")),
            sync_include_optional_metadata=os.getenv("STOCK_ANALYZER_SYNC_INCLUDE_OPTIONAL_METADATA", "false").lower() in {"1", "true", "yes"},
            enterprise_refresh_ttl_days=int(os.getenv("STOCK_ANALYZER_ENTERPRISE_REFRESH_TTL_DAYS", "7")),
            sync_enabled=os.getenv("STOCK_ANALYZER_SYNC_ENABLED", "true").lower() not in {"0", "false", "no"},
            sync_time=os.getenv("STOCK_ANALYZER_SYNC_TIME", "00:00"),
            timezone=os.getenv("STOCK_ANALYZER_TIMEZONE", "Asia/Shanghai"),
            log_level=os.getenv("STOCK_ANALYZER_LOG_LEVEL", "INFO"),
        )
