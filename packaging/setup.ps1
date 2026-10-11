#Requires -Version 5.1
<#
.SYNOPSIS
  JARVIS installer — installs Python (if needed), dependencies, and creates shortcuts.
#>

$ErrorActionPreference = "Stop"
$AppName = "JARVIS"
$AppVersion = "0.2.2"
$RepoZip = "https://github.com/G1drohz/Jarvis/archive/refs/heads/main.zip"
$InstallRoot = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$PythonMin = [version]"3.10.0"
$PythonPreferred = "3.11"

function Write-Step($msg) {
  Write-Host ""
  Write-Host "==> $msg" -ForegroundColor Cyan
}
function Write-Ok($msg) { Write-Host "  OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ! $msg" -ForegroundColor Yellow }

function Find-Python {
  $candidates = @()
  foreach ($cmd in @("py", "python", "python3")) {
    try {
      $p = Get-Command $cmd -ErrorAction SilentlyContinue
      if ($p) { $candidates += $p.Source }
    } catch {}
  }
  $paths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:ProgramFiles\Python311\python.exe",
    "$env:ProgramFiles\Python312\python.exe"
  )
  foreach ($path in $paths) {
    if (Test-Path $path) { $candidates += $path }
  }

  foreach ($exe in ($candidates | Select-Object -Unique)) {
    try {
      $verOut = & $exe -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
      if (-not $verOut) { continue }
      $ver = [version]($verOut.Trim())
      if ($ver -ge $PythonMin) {
        return @{ Exe = $exe; Version = $ver }
      }
    } catch {}
  }
  return $null
}

function Install-Python {
  Write-Step "Installing Python $PythonPreferred..."

  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($winget) {
    Write-Host "  Using winget..."
    try {
      & winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --scope user
      Start-Sleep -Seconds 3
      $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                  [System.Environment]::GetEnvironmentVariable("Path", "User")
      $found = Find-Python
      if ($found) { Write-Ok "Python $($found.Version)"; return $found }
    } catch {
      Write-Warn "winget failed: $_"
    }
  }

  Write-Host "  Downloading official Python installer..."
  $installer = Join-Path $env:TEMP "python-3.11.9-amd64.exe"
  $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
  Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
  $args = "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 SimpleInstall=1"
  Start-Process -FilePath $installer -ArgumentList $args -Wait
  Start-Sleep -Seconds 2

  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
              [System.Environment]::GetEnvironmentVariable("Path", "User")

  $found = Find-Python
  if ($found) {
    Write-Ok "Python $($found.Version)"
    return $found
  }
  throw "Python installation failed. Install Python 3.10+ from https://www.python.org/downloads/ and re-run setup."
}

function Ensure-Venv($pythonExe, $venvDir) {
  if (-not (Test-Path (Join-Path $venvDir "Scripts\python.exe"))) {
    Write-Step "Creating virtual environment..."
    & $pythonExe -m venv $venvDir
    Write-Ok $venvDir
  }
  return (Join-Path $venvDir "Scripts\python.exe")
}

function Install-AppFiles {
  Write-Step "Downloading JARVIS sources..."
  New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
  $zip = Join-Path $env:TEMP "jarvis-src.zip"
  Invoke-WebRequest -Uri $RepoZip -OutFile $zip -UseBasicParsing
  $extract = Join-Path $env:TEMP "jarvis-extract"
  if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
  Expand-Archive -Path $zip -DestinationPath $extract -Force

  $src = Get-ChildItem $extract -Directory | Select-Object -First 1
  $dataBackup = $null
  $dataPath = Join-Path $InstallRoot "data"
  if (Test-Path $dataPath) {
    $dataBackup = Join-Path $env:TEMP "jarvis-data-backup"
    if (Test-Path $dataBackup) { Remove-Item $dataBackup -Recurse -Force }
    Copy-Item $dataPath $dataBackup -Recurse
  }

  Get-ChildItem $src.FullName | ForEach-Object {
    $dest = Join-Path $InstallRoot $_.Name
    if ($_.Name -eq "data" -and (Test-Path $dest)) { return }
    Copy-Item $_.FullName $dest -Recurse -Force
  }

  if ($dataBackup -and (Test-Path $dataBackup)) {
    New-Item -ItemType Directory -Force -Path $dataPath | Out-Null
    Copy-Item "$dataBackup\*" $dataPath -Recurse -Force -ErrorAction SilentlyContinue
  }

  Write-Ok $InstallRoot
}

function Install-Deps($venvPython) {
  Write-Step "Installing dependencies (this may take a few minutes)..."
  & $venvPython -m pip install --upgrade pip
  $req = Join-Path $InstallRoot "requirements.txt"
  & $venvPython -m pip install -r $req

  Write-Host "  Installing PyAudio (microphone)..."
  try { & $venvPython -m pip install pipwin 2>$null } catch {}
  try { & $venvPython -m pipwin install pyaudio 2>$null } catch {}
  try { & $venvPython -m pip install pyaudio 2>$null } catch {
    Write-Warn "PyAudio not installed — voice input may need manual setup"
  }
  try { & $venvPython -m pip install pyautogui 2>$null } catch {}

  Write-Ok "Dependencies installed"
}

function Create-Shortcuts($venvPython) {
  Write-Step "Creating shortcuts..."
  $launcher = Join-Path $InstallRoot "run-jarvis.bat"
  $bat = @"
@echo off
cd /d "$InstallRoot"
"$venvPython" -m jarvis.main
if errorlevel 1 pause
"@
  Set-Content -Path $launcher -Value $bat -Encoding ASCII

  $wsh = New-Object -ComObject WScript.Shell
  $startDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$AppName"
  New-Item -ItemType Directory -Force -Path $startDir | Out-Null
  $lnk = $wsh.CreateShortcut((Join-Path $startDir "$AppName.lnk"))
  $lnk.TargetPath = $launcher
  $lnk.WorkingDirectory = $InstallRoot
  $lnk.Description = "$AppName v$AppVersion"
  $lnk.Save()

  $desk = [Environment]::GetFolderPath("Desktop")
  $lnk2 = $wsh.CreateShortcut((Join-Path $desk "$AppName.lnk"))
  $lnk2.TargetPath = $launcher
  $lnk2.WorkingDirectory = $InstallRoot
  $lnk2.Description = "$AppName v$AppVersion"
  $lnk2.Save()

  Write-Ok "Start Menu + Desktop shortcuts"
}

function Create-Uninstall {
  $un = Join-Path $InstallRoot "uninstall.bat"
  $content = @"
@echo off
echo Uninstalling JARVIS...
rmdir /s /q "$InstallRoot" 2>nul
del "%USERPROFILE%\Desktop\JARVIS.lnk" 2>nul
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\JARVIS" 2>nul
echo Done.
pause
"@
  Set-Content -Path $un -Value $content -Encoding ASCII
}

Write-Host ""
Write-Host "  $AppName Setup v$AppVersion" -ForegroundColor White
Write-Host "  Install path: $InstallRoot" -ForegroundColor DarkGray
Write-Host ""

try {
  $py = Find-Python
  if (-not $py) {
    $py = Install-Python
  } else {
    Write-Step "Found Python $($py.Version)"
    Write-Ok $py.Exe
  }

  Install-AppFiles
  $venvDir = Join-Path $InstallRoot ".venv"
  $venvPy = Ensure-Venv $py.Exe $venvDir
  Install-Deps $venvPy
  Create-Shortcuts $venvPy
  Create-Uninstall

  Write-Host ""
  Write-Host "========================================" -ForegroundColor Green
  Write-Host "  Installation complete!" -ForegroundColor Green
  Write-Host "========================================" -ForegroundColor Green
  Write-Host ""
  Write-Host "  Launch: Desktop shortcut «$AppName»"
  Write-Host "  Or run: $InstallRoot\run-jarvis.bat"
  Write-Host ""

  $launch = Read-Host "Start JARVIS now? (Y/n)"
  if ($launch -eq "" -or $launch -match "^[Yy]") {
    Start-Process -FilePath (Join-Path $InstallRoot "run-jarvis.bat")
  }
}
catch {
  Write-Host ""
  Write-Host "ERROR: $_" -ForegroundColor Red
  Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
  Write-Host ""
  Write-Host "Press Enter to close..."
  [void][System.Console]::ReadLine()
  exit 1
}
