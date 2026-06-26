CREATE TABLE IF NOT EXISTS analysis_daily_bars (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 6) NOT NULL,
    high DECIMAL(18, 6) NOT NULL,
    low DECIMAL(18, 6) NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    volume DECIMAL(24, 4) NOT NULL,
    amount DECIMAL(24, 4) NOT NULL,
    adj_factor DECIMAL(18, 8) NULL,
    price_mode VARCHAR(32) NOT NULL,
    source VARCHAR(32) NOT NULL,
    data_quality VARCHAR(32) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, price_mode),
    KEY idx_analysis_date_mode (trade_date, price_mode),
    KEY idx_analysis_quality (data_quality),
    CONSTRAINT fk_analysis_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS daily_indicators (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    strategy_key VARCHAR(64) NOT NULL,
    expma17 DECIMAL(18, 6) NULL,
    expma50 DECIMAL(18, 6) NULL,
    cross_price DECIMAL(18, 6) NULL,
    cross_in_kline BOOLEAN NOT NULL DEFAULT FALSE,
    warmup_ready BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, strategy_key),
    KEY idx_indicators_date_strategy (trade_date, strategy_key),
    CONSTRAINT fk_indicators_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS strategy_signals (
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    strategy_key VARCHAR(64) NOT NULL,
    selected_signal VARCHAR(32) NULL,
    raw_flags_json JSON NOT NULL,
    trend_state VARCHAR(64) NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, trade_date, strategy_key),
    KEY idx_signals_date_strategy_signal (trade_date, strategy_key, selected_signal),
    CONSTRAINT fk_signals_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

