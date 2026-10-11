"""Download and resolve offline Piper voice models (no runtime internet after first fetch)."""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

# HuggingFace rhasspy/piper-voices direct files
MODELS: dict[str, dict[str, str]] = {
    # British male — closest free offline "butler / AI" English tone
    "jarvis_en": {
        "id": "en_GB-alan-medium",
        "onnx": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "en/en_GB/alan/medium/en_GB-alan-medium.onnx"
        ),
        "json": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
        ),
    },
    # Russian male neural offline
    "jarvis_ru": {
        "id": "ru_RU-dmitri-medium",
        "onnx": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx"
        ),
        "json": (
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
            "ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json"
        ),
    },
}


def models_dir() -> Path:
    env = os.environ.get("JARVIS_ROOT")
    if env:
        root = Path(env)
    elif getattr(sys, "frozen", False):
        root = Path(sys.executable).resolve().parent
    else:
        root = Path(__file__).resolve().parents[2]
    d = root / "data" / "tts_models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def model_paths(key: str) -> tuple[Path, Path]:
    meta = MODELS[key]
    base = models_dir() / meta["id"]
    return base.with_suffix(".onnx"), Path(str(base) + ".onnx.json")


def ensure_model(key: str, on_status=None) -> Path:
    """Ensure onnx+json exist; download once if missing. Returns path to .onnx."""
    if key not in MODELS:
        key = "jarvis_en"
    onnx_path, json_path = model_paths(key)
    meta = MODELS[key]

    if onnx_path.exists() and json_path.exists() and onnx_path.stat().st_size > 1_000_000:
        return onnx_path

    def status(msg: str) -> None:
        if on_status:
            on_status(msg)
        print(f"[TTS models] {msg}")

    status(f"Downloading offline voice «{meta['id']}» (~60 MB, one-time)...")
    for url, dest in ((meta["onnx"], onnx_path), (meta["json"], json_path)):
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            urllib.request.urlretrieve(url, tmp)
            tmp.replace(dest)
        except Exception as e:
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download {url}: {e}") from e

    status(f"Voice ready: {onnx_path.name}")
    return onnx_path


def resolve_voice_key(prefer: str, lang: str) -> str:
    prefer = (prefer or "jarvis").lower()
    lang = (lang or "ru").lower()
    if prefer in ("jarvis_en", "en", "male_en", "alan"):
        return "jarvis_en"
    if prefer in ("jarvis_ru", "ru", "male_ru", "dmitri"):
        return "jarvis_ru"
    # jarvis / auto → by UI language
    if lang.startswith("en"):
        return "jarvis_en"
    return "jarvis_ru"
