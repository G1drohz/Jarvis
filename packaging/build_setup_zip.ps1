# Pack setup scripts + minimal bootstrap into JARVIS-Setup.zip for release
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root "dist"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$stage = Join-Path $env:TEMP "jarvis-setup-stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

Copy-Item (Join-Path $PSScriptRoot "setup.bat") $stage
Copy-Item (Join-Path $PSScriptRoot "setup.ps1") $stage
Copy-Item (Join-Path $PSScriptRoot "README-SETUP.txt") $stage -ErrorAction SilentlyContinue

$zip = Join-Path $outDir "JARVIS-Setup-0.2.1.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force
Write-Host "Created $zip"
