"""Shared paths for step 2 model notebooks."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "model"
ARTIFACTS_DIR = MODEL_DIR / "artifacts"
NOTEBOOKS_DIR = MODEL_DIR / "notebooks"

# Latest human-reviewed labels (999 rows, same content in both files).
LABELED_CSV_PATH = DATA_DIR / "comments.csv"
LABELED_JSON_PATH = DATA_DIR / "comments.json"

# Notebook 00 writes split here; notebooks 01–03 read it.
SPLIT_INDICES_PATH = ARTIFACTS_DIR / "split_indices.json"

PHOBERT_ARTIFACTS_DIR = ARTIFACTS_DIR / "phobert_weighted"
BASELINE_PKL_PATH = ARTIFACTS_DIR / "baseline.pkl"
REPORT_PATH = MODEL_DIR / "report.md"
