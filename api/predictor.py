"""Load PhoBERT once and run single-text inference."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import torch
from pyvi.ViTokenizer import tokenize
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from api.config import MODEL_PATH, TOKENIZER_MAX_LENGTH

logger = logging.getLogger(__name__)

_ABBREV_MAP = {
    "ko": "không",
    "k": "không",
    "kh": "không",
    "hong": "không",
    "dc": "được",
    "đc": "được",
    "duoc": "được",
    "vs": "với",
    "j": "gì",
    "ns": "nói",
    "bn": "bạn",
    "ng": "người",
}
_ABBREV_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(_ABBREV_MAP, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE,
)


def _expand_abbrev(text: str) -> str:
    # ponytail: skip ambiguous keys like "bt" to avoid bad automatic replacements.
    return _ABBREV_PATTERN.sub(lambda m: _ABBREV_MAP[m.group(0).lower()], text)


def _preprocess(text: str) -> str:
    normalized = " ".join(str(text).split())
    normalized = _expand_abbrev(normalized)
    return tokenize(normalized)


class Predictor:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.id2label: dict[int, str] = {}
        self.device = "cpu"
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        weights = self.model_path / "model.safetensors"
        if not weights.exists():
            raise FileNotFoundError(f"No model weights at {self.model_path}")

        with (self.model_path / "label_map.json").open(encoding="utf-8") as f:
            self.id2label = {int(k): v for k, v in json.load(f).items()}

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"

        self.model.to(self.device)
        self.model.eval()
        self._loaded = True
        logger.info("Model loaded from %s on %s", self.model_path, self.device)

    def predict(self, text: str) -> dict:
        if not self._loaded:
            raise RuntimeError("Model not loaded")

        inputs = self.tokenizer(
            _preprocess(text),
            return_tensors="pt",
            truncation=True,
            max_length=TOKENIZER_MAX_LENGTH,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits

        probs = torch.softmax(logits, dim=-1).squeeze().tolist()
        pred_id = int(logits.argmax(dim=-1).item())
        sentiment = self.id2label[pred_id]
        confidence = round(float(probs[pred_id]), 2)

        probabilities = {
            self.id2label[i]: round(float(score), 2) for i, score in enumerate(probs)
        }

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "probabilities": probabilities,  
        }
