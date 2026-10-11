@echo off
chcp 65001 >nul
title JARVIS Setup
cd /d "%~dp0"

echo.
echo   JARVIS Installer
echo   Will install Python (if needed), dependencies and shortcuts.
echo.

:: Prefer PowerShell 5+
where powershell >nul 2>&1
if errorlevel 1 (
  echo PowerShell not found. Please install from Microsoft Store or use portable ZIP.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 (
  echo.
  echo Setup finished with errors.
  pause
)
