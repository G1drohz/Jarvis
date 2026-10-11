#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== JARVIS build ==="
python -m pip install -q --upgrade pip pyinstaller Pillow
python -m pip install -q -r requirements.txt
python packaging/make_icon.py || true

rm -rf dist/JARVIS build
python -m PyInstaller packaging/jarvis.spec --noconfirm
echo "Output: dist/JARVIS/"
