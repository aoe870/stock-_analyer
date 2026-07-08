param(
    [switch]$Install,
    [switch]$UseDocker
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if ($UseDocker) { docker compose -f (Join-Path $root "docker-compose.yml") up -d mysql }
if (-not (Test-Path (Join-Path $root ".venv\Scripts\python.exe"))) { throw "Python virtual environment missing at .venv" }
if ($Install) { & (Join-Path $root ".venv\Scripts\python.exe") -m pip install -r (Join-Path $root "requirements.txt") }
& "$PSScriptRoot\migrate_db.ps1"
& (Join-Path $root ".venv\Scripts\python.exe") -m stock_analyzer_app api
