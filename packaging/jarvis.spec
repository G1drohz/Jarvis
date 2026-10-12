# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
_here = Path(SPECPATH).resolve()
project = _here.parent if (_here.parent / "jarvis").is_dir() else _here

# Bundle every jarvis.* submodule (monitor, scenarios, voice, …)
hidden = collect_submodules("jarvis")
hidden += collect_submodules("config")
hidden += [
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
    "piper",
    "onnxruntime",
    "psutil",
    "PIL",
    "PIL.ImageGrab",
]

datas = [
    (str(project / "config" / "default.yaml"), "config"),
    (str(project / "data" / "commands.json"), "data"),
    (str(project / "jarvis" / "plugins"), "jarvis/plugins"),
]
for name in ("main_window_body.py", "_main_window_cache.py"):
    p = project / "jarvis" / "ui" / name
    if p.exists():
        datas.append((str(p), "jarvis/ui"))

a = Analysis(
    [str(project / "jarvis" / "main.py")],
    pathex=[str(project)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    excludes=["tkinter", "matplotlib"],
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
    console=False,
    icon=str(project / "packaging" / "jarvis.ico")
    if (project / "packaging" / "jarvis.ico").exists()
    else None,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="JARVIS")
