@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0\.."

echo === JARVIS build ===
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo Python not found in PATH
  exit /b 1
)

echo [1/4] Installing build deps...
python -m pip install -q --upgrade pip
python -m pip install -q pyinstaller Pillow
python -m pip install -q -r requirements.txt

echo [2/4] Generating icon...
python packaging\make_icon.py

echo [3/4] PyInstaller...
if exist dist\JARVIS rmdir /s /q dist\JARVIS
if exist build rmdir /s /q build
python -m PyInstaller packaging\jarvis.spec --noconfirm
if errorlevel 1 (
  echo PyInstaller failed
  exit /b 1
)

echo [4/4] Done.
echo.
echo EXE folder: dist\JARVIS\JARVIS.exe
echo.
echo To create installer:
echo   1. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php
echo   2. Open packaging\installer.iss and Compile
echo   3. Output: dist\installer\JARVIS-Setup-0.2.1.exe
echo.
pause
