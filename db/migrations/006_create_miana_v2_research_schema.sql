CREATE TABLE IF NOT EXISTS income_statements (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    report_date DATE NOT NULL,
    notice_date DATE NULL,
    report_period VARCHAR(32) NOT NULL DEFAULT '',
    currency VARCHAR(16) NULL,
    revenue DECIMAL(24, 4) NULL,
    operating_revenue DECIMAL(24, 4) NULL,
    operating_profit DECIMAL(24, 4) NULL,
    total_profit DECIMAL(24, 4) NULL,
    net_profit DECIMAL(24, 4) NULL,
    net_profit_parent DECIMAL(24, 4) NULL,
    eps DECIMAL(18, 6) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, report_date, report_period),
    KEY idx_income_report_date (report_date),
    CONSTRAINT fk_income_statements_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS balance_sheets (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    report_date DATE NOT NULL,
    notice_date DATE NULL,
    report_period VARCHAR(32) NOT NULL DEFAULT '',
    currency VARCHAR(16) NULL,
    total_assets DECIMAL(24, 4) NULL,
    total_liabilities DECIMAL(24, 4) NULL,
    total_equity DECIMAL(24, 4) NULL,
    monetary_funds DECIMAL(24, 4) NULL,
    accounts_receivable DECIMAL(24, 4) NULL,
    inventory DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, report_date, report_period),
    KEY idx_balance_report_date (report_date),
    CONSTRAINT fk_balance_sheets_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cashflow_statements (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    report_date DATE NOT NULL,
    notice_date DATE NULL,
    report_period VARCHAR(32) NOT NULL DEFAULT '',
    currency VARCHAR(16) NULL,
    net_operating_cashflow DECIMAL(24, 4) NULL,
    net_investing_cashflow DECIMAL(24, 4) NULL,
    net_financing_cashflow DECIMAL(24, 4) NULL,
    cash_and_equivalents DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, report_date, report_period),
    KEY idx_cashflow_report_date (report_date),
    CONSTRAINT fk_cashflow_statements_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_top10_holders (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    report_date DATE NOT NULL,
    holder_name VARCHAR(255) NOT NULL,
    holder_rank INT NULL,
    hold_volume DECIMAL(24, 4) NULL,
    hold_ratio DECIMAL(18, 6) NULL,
    share_type VARCHAR(64) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, report_date, holder_name),
    KEY idx_top10_holders_report_date (report_date),
    CONSTRAINT fk_top10_holders_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_company_officers (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    start_date DATE NULL,
    end_date DATE NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, officer_name, title),
    CONSTRAINT fk_company_officers_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_officer_rewards (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    report_date DATE NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NULL,
    reward DECIMAL(24, 4) NULL,
    hold_volume DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider, report_date, officer_name),
    KEY idx_officer_rewards_report_date (report_date),
    CONSTRAINT fk_officer_rewards_stock FOREIGN KEY (symbol) REFERENCES stocks(symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS market_indexes (
    index_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    exchange_code VARCHAR(32) NULL,
    country_code VARCHAR(16) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (index_code, provider)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS index_constituents (
    index_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    weight DECIMAL(18, 6) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (index_code, provider, symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS index_daily_bars (
    index_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 4) NULL,
    high DECIMAL(18, 4) NULL,
    low DECIMAL(18, 4) NULL,
    close DECIMAL(18, 4) NULL,
    volume DECIMAL(24, 4) NULL,
    amount DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (index_code, provider, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS market_sectors (
    sector_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    market VARCHAR(64) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (sector_code, provider)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sector_constituents (
    sector_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    weight DECIMAL(18, 6) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (sector_code, provider, symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sector_daily_bars (
    sector_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(18, 4) NULL,
    high DECIMAL(18, 4) NULL,
    low DECIMAL(18, 4) NULL,
    close DECIMAL(18, 4) NULL,
    volume DECIMAL(24, 4) NULL,
    amount DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (sector_code, provider, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS latest_market_quotes (
    symbol VARCHAR(16) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    quote_time DATETIME NULL,
    price DECIMAL(18, 4) NULL,
    change_amount DECIMAL(18, 4) NULL,
    change_rate DECIMAL(18, 6) NULL,
    volume DECIMAL(24, 4) NULL,
    amount DECIMAL(24, 4) NULL,
    turnover DECIMAL(18, 6) NULL,
    market_value DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, provider)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS latest_sector_quotes (
    sector_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    quote_time DATETIME NULL,
    price DECIMAL(18, 4) NULL,
    change_amount DECIMAL(18, 4) NULL,
    change_rate DECIMAL(18, 6) NULL,
    amount DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (sector_code, provider)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS latest_index_quotes (
    index_code VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL,
    quote_time DATETIME NULL,
    price DECIMAL(18, 4) NULL,
    change_amount DECIMAL(18, 4) NULL,
    change_rate DECIMAL(18, 6) NULL,
    volume DECIMAL(24, 4) NULL,
    amount DECIMAL(24, 4) NULL,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (index_code, provider)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
