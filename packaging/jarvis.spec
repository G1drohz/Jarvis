# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for JARVIS

from pathlib import Path

block_cipher = None

_here = Path(SPECPATH).resolve()
if (_here.parent / "jarvis").is_dir():
    project = _here.parent
elif (_here / "jarvis").is_dir():
    project = _here
else:
    project = _here.parent

a = Analysis(
    [str(project / "jarvis" / "main.py")],
    pathex=[str(project)],
    binaries=[],
    datas=[
        (str(project / "config" / "default.yaml"), "config"),
        (str(project / "data" / "commands.json"), "data"),
        (str(project / "jarvis" / "plugins"), "jarvis/plugins"),
    ],
    hiddenimports=[
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "yaml",
        "pydantic",
        "httpx",
        "speech_recognition",
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "edge_tts",
        "pygame",
        "psutil",
        "PIL",
        "PIL.ImageGrab",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="JARVIS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project / "packaging" / "jarvis.ico") if (project / "packaging" / "jarvis.ico").exists() else None,
    version=str(project / "packaging" / "version_info.txt") if (project / "packaging" / "version_info.txt").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JARVIS",
)
