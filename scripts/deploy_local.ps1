$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $root ".venv"))) { py -3.12 -m venv (Join-Path $root ".venv") }
& (Join-Path $root ".venv\Scripts\python.exe") -m pip install -r (Join-Path $root "requirements.txt")
& "$PSScriptRoot\init_db.ps1"
$health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -ErrorAction SilentlyContinue
Write-Host "Deployment prepared. Browser URL: http://127.0.0.1:8000"
Write-Host "Health endpoint: http://127.0.0.1:8000/api/health"

