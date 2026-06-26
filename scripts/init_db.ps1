param(
    [Alias('Host')][string]$DbHost = $env:STOCK_ANALYZER_DB_HOST,
    [int]$Port = $(if ($env:STOCK_ANALYZER_DB_PORT) { [int]$env:STOCK_ANALYZER_DB_PORT } else { 3306 }),
    [string]$Database = $(if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }),
    [string]$AppUser = $(if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }),
    [string]$AppPassword = $(if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" }),
    [string]$AdminUser = "root",
    [string]$AdminPassword = $env:STOCK_ANALYZER_MYSQL_ROOT_PASSWORD
)

$ErrorActionPreference = "Stop"
if (-not $DbHost) { $DbHost = "127.0.0.1" }
if (-not $AdminPassword) { $AdminPassword = "root-change-me" }

$createSql = @"
CREATE DATABASE IF NOT EXISTS ``$Database`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$AppUser'@'%' IDENTIFIED BY '$AppPassword';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES ON ``$Database``.* TO '$AppUser'@'%';
FLUSH PRIVILEGES;
"@

$createSql | mysql -h $DbHost -P $Port -u $AdminUser "-p$AdminPassword"
& "$PSScriptRoot\migrate_db.ps1" -Host $DbHost -Port $Port -Database $Database -User $AppUser -Password $AppPassword
& "$PSScriptRoot\seed_db.ps1" -Host $DbHost -Port $Port -Database $Database -User $AppUser -Password $AppPassword
