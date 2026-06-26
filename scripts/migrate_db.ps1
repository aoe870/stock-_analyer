param(
    [Alias('Host')][string]$DbHost = $(if ($env:STOCK_ANALYZER_DB_HOST) { $env:STOCK_ANALYZER_DB_HOST } else { "127.0.0.1" }),
    [int]$Port = $(if ($env:STOCK_ANALYZER_DB_PORT) { [int]$env:STOCK_ANALYZER_DB_PORT } else { 3306 }),
    [string]$Database = $(if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }),
    [string]$User = $(if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }),
    [string]$Password = $(if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" })
)

$ErrorActionPreference = "Stop"
$migrationDir = Join-Path (Split-Path $PSScriptRoot -Parent) "db\migrations"

function Invoke-MySqlInput {
    param([string]$Sql)
    if (Get-Command mysql -ErrorAction SilentlyContinue) {
        $Sql | mysql -h $DbHost -P $Port -u $User "-p$Password" $Database
    } else {
        $Sql | docker exec -i stock_analyzer_mysql mysql -u $User "-p$Password" $Database
    }
    if ($LASTEXITCODE -ne 0) { throw "mysql command failed with exit code $LASTEXITCODE" }
}

function Invoke-MySqlQuery {
    param([string]$Sql)
    if (Get-Command mysql -ErrorAction SilentlyContinue) {
        $result = mysql -N -B -h $DbHost -P $Port -u $User "-p$Password" $Database -e $Sql
    } else {
        $result = docker exec stock_analyzer_mysql mysql -N -B -u $User "-p$Password" $Database -e $Sql
    }
    if ($LASTEXITCODE -ne 0) { throw "mysql query failed with exit code $LASTEXITCODE" }
    return $result
}

$ensure = "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(64) PRIMARY KEY, checksum CHAR(64) NOT NULL, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
Invoke-MySqlInput $ensure

$applied = @{}
$rows = Invoke-MySqlQuery "SELECT version, checksum FROM schema_migrations;"
foreach ($row in $rows) {
    $parts = $row -split "`t"
    if ($parts.Length -eq 2) { $applied[$parts[0]] = $parts[1] }
}

$appliedCount = 0
$skippedCount = 0
foreach ($file in Get-ChildItem $migrationDir -Filter "*.sql" | Sort-Object Name) {
    $checksum = (Get-FileHash -Algorithm SHA256 -Path $file.FullName).Hash.ToLowerInvariant()
    if ($applied.ContainsKey($file.Name)) {
        if ($applied[$file.Name].ToLowerInvariant() -ne $checksum) {
            throw "checksum mismatch for migration $($file.Name)"
        }
        $skippedCount += 1
        continue
    }
    Invoke-MySqlInput (Get-Content -Raw -Path $file.FullName)
    $insert = "INSERT INTO schema_migrations (version, checksum) VALUES ('$($file.Name)', '$checksum');"
    Invoke-MySqlInput $insert
    $appliedCount += 1
}

Write-Host "Migrations applied=$appliedCount skipped=$skippedCount failed=0"
