param(
    [Parameter(Mandatory=$true)][string]$DumpFile,
    [switch]$ConfirmRestore,
    [Alias('Host')][string]$DbHost = $(if ($env:STOCK_ANALYZER_DB_HOST) { $env:STOCK_ANALYZER_DB_HOST } else { "127.0.0.1" }),
    [int]$Port = $(if ($env:STOCK_ANALYZER_DB_PORT) { [int]$env:STOCK_ANALYZER_DB_PORT } else { 3306 }),
    [string]$Database = $(if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }),
    [string]$User = $(if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }),
    [string]$Password = $(if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" })
)

$ErrorActionPreference = "Stop"
if (-not $ConfirmRestore) { throw "restore requires -ConfirmRestore to avoid accidental overwrite" }
if (-not (Test-Path $DumpFile)) { throw "dump file not found: $DumpFile" }
$sql = Get-Content -Raw -Path $DumpFile
if (Get-Command mysql -ErrorAction SilentlyContinue) {
    $sql | mysql -h $DbHost -P $Port -u $User "-p$Password" $Database
} else {
    $sql | docker exec -i stock_analyzer_mysql mysql -u $User "-p$Password" $Database
}
Write-Host "Restore completed into database $Database"
