param(
    [string]$HealthUrl = $(if ($env:STOCK_ANALYZER_HEALTH_URL) { $env:STOCK_ANALYZER_HEALTH_URL } else { "http://127.0.0.1:8000/api/health" })
)

$ErrorActionPreference = "Stop"
$root = Split-Path $MyInvocation.MyCommand.Path -Parent
Set-Location $root

$compose = if ($env:DOCKER_COMPOSE) { $env:DOCKER_COMPOSE } else { "docker compose" }
$envFile = Join-Path $root ".env"
$envExample = Join-Path $root ".env.example"

if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "Created .env from .env.example. Edit provider tokens before running large sync jobs."
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -notmatch "=") { return }
    $parts = $_ -split "=", 2
    [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
}

$dbName = if ($env:STOCK_ANALYZER_DB_NAME) { $env:STOCK_ANALYZER_DB_NAME } else { "stock_analyzer" }
$dbUser = if ($env:STOCK_ANALYZER_DB_USER) { $env:STOCK_ANALYZER_DB_USER } else { "stock_analyzer" }
$dbPassword = if ($env:STOCK_ANALYZER_DB_PASSWORD) { $env:STOCK_ANALYZER_DB_PASSWORD } else { "change-me" }

function Invoke-Compose {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & powershell -NoProfile -Command "$compose $($Args -join ' ')"
    if ($LASTEXITCODE -ne 0) { throw "docker compose command failed: $($Args -join ' ')" }
}

function Invoke-MysqlInput {
    param([string]$Sql)
    $Sql | docker compose exec -T -e "MYSQL_PWD=$dbPassword" mysql mysql -u $dbUser $dbName
    if ($LASTEXITCODE -ne 0) { throw "mysql command failed" }
}

function Invoke-MysqlFile {
    param([string]$Path)
    Get-Content -Raw $Path | docker compose exec -T -e "MYSQL_PWD=$dbPassword" mysql mysql -u $dbUser $dbName
    if ($LASTEXITCODE -ne 0) { throw "mysql file command failed: $Path" }
}

function Wait-ForMysql {
    Write-Host "Waiting for MySQL..."
    for ($i = 0; $i -lt 60; $i++) {
        "SELECT 1;" | docker compose exec -T -e "MYSQL_PWD=$dbPassword" mysql mysql -u $dbUser $dbName *> $null
        if ($LASTEXITCODE -eq 0) { return }
        Start-Sleep -Seconds 2
    }
    throw "MySQL did not become ready in time."
}

function Invoke-Migrate {
    Write-Host "Running migrate..."
    Invoke-MysqlInput "CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(64) PRIMARY KEY, checksum CHAR(64) NOT NULL, applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    Get-ChildItem (Join-Path $root "db\migrations") -Filter "*.sql" | Sort-Object Name | ForEach-Object {
        $version = $_.Name
        $checksum = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash.ToLowerInvariant()
        $applied = docker compose exec -T -e "MYSQL_PWD=$dbPassword" mysql mysql -N -B -u $dbUser $dbName -e "SELECT checksum FROM schema_migrations WHERE version='$version';"
        if ($LASTEXITCODE -ne 0) { throw "mysql query failed" }
        if ($applied) {
            if ($applied.Trim().ToLowerInvariant() -ne $checksum) { throw "Migration checksum mismatch: $version" }
            return
        }
        Invoke-MysqlFile $_.FullName
        Invoke-MysqlInput "INSERT INTO schema_migrations (version, checksum) VALUES ('$version', '$checksum');"
    }
}

function Invoke-Seed {
    Write-Host "Running seed..."
    Invoke-MysqlFile (Join-Path $root "db\seeds\001_default_settings.sql")
}

function Wait-ForHealth {
    Write-Host "Waiting for app health..."
    for ($i = 0; $i -lt 60; $i++) {
        try {
            Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 5 *> $null
            return
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "App health check failed: $HealthUrl"
}

docker compose build
if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }
docker compose up -d mysql
if ($LASTEXITCODE -ne 0) { throw "docker compose up -d mysql failed" }
Wait-ForMysql
Invoke-Migrate
Invoke-Seed
docker compose up -d api collector
if ($LASTEXITCODE -ne 0) { throw "docker compose up -d api collector failed" }
Wait-ForHealth

Write-Host "Deployment complete."
Write-Host "URL: http://127.0.0.1:8000"
Write-Host "Health: $HealthUrl"
