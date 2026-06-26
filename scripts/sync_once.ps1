param(
    [ValidateSet("sync_calendar", "sync_stock_universe", "sync_daily_bars", "sync_adjustment_factors", "aggregate_daily", "compute_signals", "full_daily_pipeline")]
    [string]$JobType = "full_daily_pipeline",
    [string]$StartDate,
    [string]$EndDate,
    [string[]]$Symbols = @()
)

$ErrorActionPreference = "Stop"
$body = @{ job_type = $JobType; start_date = $StartDate; end_date = $EndDate; symbols = $Symbols } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/sync/jobs" -ContentType "application/json" -Body $body

