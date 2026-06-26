CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(64) PRIMARY KEY,
    checksum CHAR(64) NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(16) PRIMARY KEY,
    exchange VARCHAR(8) NOT NULL,
    name VARCHAR(128) NOT NULL,
    industry VARCHAR(128) NULL,
    list_date DATE NULL,
    delist_date DATE NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_st BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_stocks_exchange_active (exchange, is_active),
    KEY idx_stocks_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS trading_calendar (
    exchange VARCHAR(8) NOT NULL,
    trade_date DATE NOT NULL,
    is_open BOOLEAN NOT NULL,
    previous_trade_date DATE NULL,
    next_trade_date DATE NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (exchange, trade_date),
    KEY idx_calendar_open_date (exchange, is_open, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS daily_bars (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 6) NOT NULL,
    high DECIMAL(18, 6) NOT NULL,
    low DECIMAL(18, 6) NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    volume DECIMAL(24, 4) NOT NULL,
    amount DECIMAL(24, 4) NOT NULL,
    source VARCHAR(32) NOT NULL,
    is_adjusted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, is_adjusted, source),
    KEY idx_daily_bars_date (trade_date),
    CONSTRAINT fk_daily_bars_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS adjustment_factors (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    adj_factor DECIMAL(18, 8) NOT NULL,
    source VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, source),
    KEY idx_adjustment_date (trade_date),
    CONSTRAINT fk_adjustment_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS raw_provider_payloads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(32) NOT NULL,
    endpoint VARCHAR(64) NOT NULL,
    symbol VARCHAR(16) NULL,
    trade_date DATE NULL,
    payload_hash CHAR(64) NOT NULL,
    payload_json JSON NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_raw_payload (provider, endpoint, symbol, trade_date, payload_hash),
    KEY idx_raw_payload_symbol_date (symbol, trade_date),
    KEY idx_raw_payload_fetched (fetched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sync_jobs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_type VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL,
    requested_by VARCHAR(32) NOT NULL,
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    provider_priority_json JSON NULL,
    summary_json JSON NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_sync_jobs_status (status, created_at),
    KEY idx_sync_jobs_type_created (job_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sync_job_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id BIGINT NOT NULL,
    symbol VARCHAR(16) NULL,
    trade_date DATE NULL,
    date_start DATE NULL,
    date_end DATE NULL,
    status VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NULL,
    attempt_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_sync_items_job_status (job_id, status),
    KEY idx_sync_items_symbol_date (symbol, trade_date),
    CONSTRAINT fk_sync_items_job FOREIGN KEY (job_id) REFERENCES sync_jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

