CREATE TABLE IF NOT EXISTS screening_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_key VARCHAR(64) NOT NULL,
    trade_date DATE NOT NULL,
    universe_json JSON NOT NULL,
    filters_json JSON NOT NULL,
    status VARCHAR(32) NOT NULL,
    summary_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    KEY idx_screening_runs_date (trade_date, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS screening_results (
    run_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    trade_date DATE NOT NULL,
    close DECIMAL(18, 6) NOT NULL,
    expma17 DECIMAL(18, 6) NULL,
    expma50 DECIMAL(18, 6) NULL,
    selected_signal VARCHAR(32) NULL,
    trend_state VARCHAR(64) NOT NULL,
    score DECIMAL(18, 6) NULL,
    reason_json JSON NULL,
    KEY idx_screening_results_run (run_id),
    KEY idx_screening_results_signal (selected_signal),
    CONSTRAINT fk_screening_results_run FOREIGN KEY (run_id) REFERENCES screening_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS backtest_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    strategy_key VARCHAR(64) NOT NULL,
    symbols_json JSON NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(24, 4) NOT NULL,
    fee_rate DECIMAL(18, 8) NOT NULL,
    slippage_rate DECIMAL(18, 8) NOT NULL,
    price_mode VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    summary_json JSON NULL,
    coverage_json JSON NULL,
    allow_partial_coverage BOOLEAN NOT NULL DEFAULT FALSE,
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    KEY idx_backtest_runs_created (created_at),
    KEY idx_backtest_runs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS backtest_trades (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    run_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    signal_date DATE NOT NULL,
    execution_date DATE NULL,
    `signal` VARCHAR(32) NOT NULL,
    `action` VARCHAR(32) NOT NULL,
    price DECIMAL(18, 6) NULL,
    quantity DECIMAL(24, 8) NULL,
    fee DECIMAL(18, 6) NOT NULL DEFAULT 0,
    slippage DECIMAL(18, 6) NOT NULL DEFAULT 0,
    position_before DECIMAL(8, 4) NOT NULL,
    position_after DECIMAL(8, 4) NOT NULL,
    is_filled BOOLEAN NOT NULL,
    KEY idx_backtest_trades_run (run_id),
    KEY idx_backtest_trades_symbol_date (symbol, signal_date),
    CONSTRAINT fk_backtest_trades_run FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS backtest_equity (
    run_id BIGINT NOT NULL,
    trade_date DATE NOT NULL,
    equity DECIMAL(24, 4) NOT NULL,
    cash DECIMAL(24, 4) NOT NULL,
    market_value DECIMAL(24, 4) NOT NULL,
    drawdown DECIMAL(18, 8) NOT NULL,
    positions_json JSON NOT NULL,
    PRIMARY KEY (run_id, trade_date),
    CONSTRAINT fk_backtest_equity_run FOREIGN KEY (run_id) REFERENCES backtest_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS settings (
    setting_key VARCHAR(128) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
