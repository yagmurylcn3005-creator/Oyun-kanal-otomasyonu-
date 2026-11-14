from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_GAME = "CS2"
DEFAULT_PLATFORM = "PC"
DEFAULT_STYLE = "eğlenceli ve hızlı"
DEFAULT_TONE = "heyecanlı"
DEFAULT_DURATION = 8
ALLOWED_MODES = ("plan", "script", "meta", "thumbnail", "all")
VALID_OUTPUT_FORMATS = ("text", "json")


def get_google_api_key() -> str | None:
    return os.getenv("GOOGLE_API_KEY")


def get_project_root() -> Path:
    return PROJECT_ROOT


def ensure_output_dir(path: str | Path | None = None) -> Path:
    target = Path(path) if path else PROJECT_ROOT / "output"
    target.mkdir(parents=True, exist_ok=True)
    return target
