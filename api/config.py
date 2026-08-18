"""API settings from env vars."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = Path(os.getenv("MODEL_PATH", PROJECT_ROOT / "model" / "artifacts" / "phobert_weighted"))
MAX_TEXT_LEN = int(os.getenv("MAX_TEXT_LEN", "512"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
MODEL_NAME = "phobert_weighted"
TOKENIZER_MAX_LENGTH = 128  # same as training notebook
