import os
from dataclasses import dataclass


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

    @classmethod
    def from_env(cls) -> "AppSettings":
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
            sync_enabled=os.getenv("STOCK_ANALYZER_SYNC_ENABLED", "true").lower() not in {"0", "false", "no"},
            sync_time=os.getenv("STOCK_ANALYZER_SYNC_TIME", "18:30"),
            timezone=os.getenv("STOCK_ANALYZER_TIMEZONE", "Asia/Shanghai"),
            log_level=os.getenv("STOCK_ANALYZER_LOG_LEVEL", "INFO"),
        )

