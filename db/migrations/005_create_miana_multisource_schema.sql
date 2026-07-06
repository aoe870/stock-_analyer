SET @ddl = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'raw_provider_payloads' AND COLUMN_NAME = 'request_params_json') = 0,
    'ALTER TABLE raw_provider_payloads ADD COLUMN request_params_json JSON NULL AFTER trade_date',
    'SELECT 1'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ddl = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'raw_provider_payloads' AND COLUMN_NAME = 'date_start') = 0,
    'ALTER TABLE raw_provider_payloads ADD COLUMN date_start DATE NULL AFTER request_params_json',
    'SELECT 1'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ddl = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'raw_provider_payloads' AND COLUMN_NAME = 'date_end') = 0,
    'ALTER TABLE raw_provider_payloads ADD COLUMN date_end DATE NULL AFTER date_start',
    'SELECT 1'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS stock_provider_profiles (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    provider_symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(8) NULL,
    name VARCHAR(128) NULL,
    industry VARCHAR(128) NULL,
    country_code VARCHAR(16) NULL,
    exchange_code VARCHAR(16) NULL,
    market VARCHAR(32) NULL,
    type VARCHAR(32) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_st BOOLEAN NOT NULL DEFAULT FALSE,
    raw_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider),
    KEY idx_provider_profiles_provider_symbol (provider, provider_symbol),
    CONSTRAINT fk_provider_profiles_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_company_profiles (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    industry VARCHAR(128) NULL,
    region VARCHAR(128) NULL,
    concepts TEXT NULL,
    address VARCHAR(512) NULL,
    legal_person VARCHAR(128) NULL,
    chairman VARCHAR(128) NULL,
    president VARCHAR(128) NULL,
    secretary VARCHAR(128) NULL,
    org_tel VARCHAR(128) NULL,
    org_email VARCHAR(256) NULL,
    org_web VARCHAR(256) NULL,
    org_profile TEXT NULL,
    main_business TEXT NULL,
    raw_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider),
    CONSTRAINT fk_company_profiles_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS corporate_actions (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    action_type VARCHAR(32) NOT NULL,
    currency VARCHAR(16) NULL,
    dividend DECIMAL(18, 8) NULL,
    split_factor DECIMAL(18, 8) NULL,
    notice_date DATE NOT NULL DEFAULT '1000-01-01',
    report_date VARCHAR(64) NOT NULL DEFAULT '',
    equity_record_date DATE NULL,
    ex_dividend_date DATE NULL,
    pay_cash_date DATE NULL,
    raw_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, action_type, report_date, notice_date),
    KEY idx_corporate_actions_ex_date (ex_dividend_date),
    CONSTRAINT fk_corporate_actions_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS share_capital_history (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    end_date DATE NOT NULL,
    total_shares DECIMAL(24, 4) NULL,
    floating_shares DECIMAL(24, 4) NULL,
    limited_shares DECIMAL(24, 4) NULL,
    change_reason VARCHAR(256) NULL,
    raw_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, end_date),
    CONSTRAINT fk_share_capital_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS daily_money_flow (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    trade_date DATE NOT NULL,
    amount DECIMAL(24, 4) NULL,
    main_net_inflow_amount DECIMAL(24, 4) NULL,
    main_net_ratio DECIMAL(18, 8) NULL,
    super_large_inflow DECIMAL(24, 4) NULL,
    super_large_outflow DECIMAL(24, 4) NULL,
    super_large_net_inflow DECIMAL(24, 4) NULL,
    super_large_net_ratio DECIMAL(18, 8) NULL,
    large_inflow DECIMAL(24, 4) NULL,
    large_outflow DECIMAL(24, 4) NULL,
    large_net_inflow DECIMAL(24, 4) NULL,
    large_net_ratio DECIMAL(18, 8) NULL,
    medium_inflow DECIMAL(24, 4) NULL,
    medium_outflow DECIMAL(24, 4) NULL,
    medium_net_inflow DECIMAL(24, 4) NULL,
    medium_net_ratio DECIMAL(18, 8) NULL,
    small_inflow DECIMAL(24, 4) NULL,
    small_outflow DECIMAL(24, 4) NULL,
    small_net_inflow DECIMAL(24, 4) NULL,
    small_net_ratio DECIMAL(18, 8) NULL,
    raw_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, trade_date),
    KEY idx_money_flow_date (trade_date),
    CONSTRAINT fk_money_flow_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
