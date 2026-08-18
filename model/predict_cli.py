"""Test fine-tuned PhoBERT from the terminal.

Usage:
  python model/predict_cli.py "Quá ngon so tầm giá"
  python model/predict_cli.py          # interactive — type comments, empty line to quit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from pyvi.ViTokenizer import tokenize
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from model.config import PHOBERT_ARTIFACTS_DIR

MAX_LENGTH = 128


def preprocess(text: str) -> str:
    return tokenize(" ".join(str(text).split()))


def load_model():
    weights = PHOBERT_ARTIFACTS_DIR / "model.safetensors"
    if not weights.exists():
        raise FileNotFoundError(
            f"No model at {PHOBERT_ARTIFACTS_DIR}. Run notebook 01 export first."
        )

    with (PHOBERT_ARTIFACTS_DIR / "label_map.json").open(encoding="utf-8") as f:
        id2label = {int(k): v for k, v in json.load(f).items()}

    tokenizer = AutoTokenizer.from_pretrained(PHOBERT_ARTIFACTS_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(PHOBERT_ARTIFACTS_DIR)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model.to(device)
    model.eval()
    return model, tokenizer, id2label, device


def predict(text: str, model, tokenizer, id2label, device):
    inputs = tokenizer(
        preprocess(text),
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).squeeze().tolist()
    pred_id = int(logits.argmax(dim=-1).item())
    return id2label[pred_id], probs


def print_result(text: str, label: str, probs: list[float], id2label: dict[int, str]) -> None:
    print(f"Comment:   {text}")
    print(f"Sentiment: {label}")
    print("Scores:")
    for i, score in enumerate(probs):
        print(f"  {id2label[i]:8s} {score:.1%}")


def main() -> int:
    parser = argparse.ArgumentParser(description="PhoBERT sentiment CLI")
    parser.add_argument("comment", nargs="?", help="One comment to classify")
    args = parser.parse_args()

    print("Loading model...")
    model, tokenizer, id2label, device = load_model()
    print(f"Ready ({device})\n")

    if args.comment:
        label, probs = predict(args.comment, model, tokenizer, id2label, device)
        print_result(args.comment, label, probs, id2label)
        return 0

    print("Interactive mode — empty line to quit.")
    while True:
        try:
            text = input("Comment> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            break
        label, probs = predict(text, model, tokenizer, id2label, device)
        print_result(text, label, probs, id2label)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
