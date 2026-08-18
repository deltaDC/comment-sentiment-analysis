"""One-time ML stack check before running notebooks. Run: python model/smoke_test.py"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")

    import torch
    import transformers

    print(f"torch: {torch.__version__}")
    print(f"transformers: {transformers.__version__}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    from model.config import LABELED_CSV_PATH, LABELED_JSON_PATH

    import pandas as pd

    df = pd.read_csv(LABELED_CSV_PATH)
    print(f"labeled CSV: {len(df)} rows @ {LABELED_CSV_PATH.name}")
    print(f"labeled JSON mirror: {LABELED_JSON_PATH.name}")
    print("OK — ready for notebook 00")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
