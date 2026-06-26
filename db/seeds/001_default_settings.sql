INSERT INTO settings (setting_key, setting_value, is_sensitive) VALUES
    ('provider_priority', 'tushare,akshare,eastmoney', FALSE),
    ('sync_schedule_time', '18:30', FALSE),
    ('default_fee_rate', '0.0003', FALSE),
    ('default_slippage_rate', '0.0005', FALSE),
    ('default_strategy_key', 'expma_17_50', FALSE),
    ('default_price_mode', 'forward_adjusted', FALSE)
ON DUPLICATE KEY UPDATE
    setting_value = VALUES(setting_value),
    is_sensitive = VALUES(is_sensitive);

