SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN company_name VARCHAR(256) NULL AFTER provider',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'company_name';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN found_date DATE NULL AFTER region',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'found_date';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN registered_capital DECIMAL(24, 4) NULL AFTER found_date',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'registered_capital';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN employee_count INT NULL AFTER registered_capital',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'employee_count';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN accounting_firm VARCHAR(256) NULL AFTER employee_count',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'accounting_firm';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN legal_adviser VARCHAR(256) NULL AFTER accounting_firm',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'legal_adviser';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE stock_company_profiles ADD COLUMN company_profile TEXT NULL AFTER org_profile',
    'SELECT 1'
) INTO @sql
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_company_profiles' AND COLUMN_NAME = 'company_profile';
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
