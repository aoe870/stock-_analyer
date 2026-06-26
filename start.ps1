param(
    [switch]$Install,
    [switch]$SkipDocker,
    [switch]$SkipMigrations,
    [switch]$SkipSeed,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$root = Split-Path $MyInvocation.MyCommand.Path -Parent
& (Join-Path $root "scripts\start_app.ps1") @PSBoundParameters
