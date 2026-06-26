param(
    [switch]$Install,
    [switch]$SkipDocker,
    [switch]$SkipMigrations,
    [switch]$SkipSeed,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Python virtual environment missing at $python. Create it first or run scripts\deploy_local.ps1."
}

if (-not $env:STOCK_ANALYZER_DB_HOST) { $env:STOCK_ANALYZER_DB_HOST = "127.0.0.1" }
if (-not $env:STOCK_ANALYZER_DB_PORT) { $env:STOCK_ANALYZER_DB_PORT = "3306" }
if (-not $env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME = "stock_analyzer" }
if (-not $env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER = "stock_analyzer" }
if (-not $env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD = "change-me" }

if (-not $SkipDocker) {
    docker compose -f (Join-Path $root "docker-compose.yml") up -d mysql
}

if ($Install) {
    & $python -m pip install -r (Join-Path $root "requirements.txt")
}

if (-not $SkipMigrations) {
    & (Join-Path $PSScriptRoot "migrate_db.ps1")
}

if (-not $SkipSeed) {
    & (Join-Path $PSScriptRoot "seed_db.ps1")
}

Write-Host "Starting Stock Analyzer at http://127.0.0.1:8000"
Write-Host "Health endpoint: http://127.0.0.1:8000/api/health"

if ($OpenBrowser) {
    Start-Process "http://127.0.0.1:8000"
}

& $python -m stock_analyzer_app
