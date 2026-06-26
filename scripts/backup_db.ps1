param(
    [Alias('Host')][string]$DbHost = $(if ($env:STOCK_ANALYZER_DB_HOST) { $env:STOCK_ANALYZER_DB_HOST } else { "127.0.0.1" }),
    [int]$Port = $(if ($env:STOCK_ANALYZER_DB_PORT) { [int]$env:STOCK_ANALYZER_DB_PORT } else { 3306 }),
    [string]$Database = $(if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }),
    [string]$User = $(if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }),
    [string]$Password = $(if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" }),
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$file = Join-Path $OutputDir "$Database-$stamp.sql"
mysqldump -h $DbHost -P $Port -u $User "-p$Password" --single-transaction --routines --triggers $Database > $file
Write-Host "Backup written to $file"
