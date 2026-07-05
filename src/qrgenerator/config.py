from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _get_app_root()

load_dotenv(PROJECT_ROOT / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "y", "on"}


APP_NAME = os.getenv("APP_NAME", "QR Code Generator")

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / os.getenv("DEFAULT_OUTPUT_DIR", "output")

QR_BOX_SIZE = int(os.getenv("QR_BOX_SIZE", "10"))
QR_BORDER = int(os.getenv("QR_BORDER", "0"))
QR_FILL_COLOR = os.getenv("QR_FILL_COLOR", "black")
QR_BACK_COLOR = os.getenv("QR_BACK_COLOR", "white")
QR_TRANSPARENT_BACKGROUND = _get_bool("QR_TRANSPARENT_BACKGROUND", True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
