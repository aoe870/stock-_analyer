CREATE TABLE IF NOT EXISTS stock_daily_status (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    is_st BOOLEAN NOT NULL DEFAULT FALSE,
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, source),
    KEY idx_stock_status_date (trade_date),
    KEY idx_stock_status_flags (trade_date, is_st, is_suspended),
    CONSTRAINT fk_stock_status_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
