param(
    [Alias('Host')][string]$DbHost = $(if ($env:STOCK_ANALYZER_DB_HOST) { $env:STOCK_ANALYZER_DB_HOST } else { "127.0.0.1" }),
    [int]$Port = $(if ($env:STOCK_ANALYZER_DB_PORT) { [int]$env:STOCK_ANALYZER_DB_PORT } else { 3306 }),
    [string]$Database = $(if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }),
    [string]$User = $(if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }),
    [string]$Password = $(if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" })
)

$ErrorActionPreference = "Stop"
$seed = Join-Path (Split-Path $PSScriptRoot -Parent) "db\seeds\001_default_settings.sql"
# Seed SQL uses ON DUPLICATE KEY UPDATE so reruns are idempotent.
$sql = Get-Content -Raw -Path $seed
if (Get-Command mysql -ErrorAction SilentlyContinue) {
    $sql | mysql -h $DbHost -P $Port -u $User "-p$Password" $Database
} else {
    $sql | docker exec -i stock_analyzer_mysql mysql -u $User "-p$Password" $Database
}
Write-Host "Seed data applied"
