from __future__ import annotations

import csv
import json
from pathlib import Path


FIELDNAMES = ["id", "comment", "sentiment", "model", "video_id", "reviewed"]


def load_rows(json_path: Path) -> list[dict]:
    with json_path.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    if not isinstance(rows, list):
        raise ValueError(f"{json_path.name} must contain a JSON array.")

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Row {index} must be a JSON object.")

    return rows


def to_csv_value(value: object) -> object:
    if isinstance(value, bool):
        return str(value)
    return value


def convert(json_path: Path, csv_path: Path) -> int:
    rows = load_rows(json_path)

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for row in rows:
            # ponytail: fixed columns keep output stable; if JSON schema grows, extend FIELDNAMES.
            writer.writerow(
                {field: to_csv_value(row.get(field, "")) for field in FIELDNAMES}
            )

    return len(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / "comments.json"
    csv_path = base_dir / "comments.csv"

    row_count = convert(json_path, csv_path)
    print(f"Wrote {row_count} rows to {csv_path}")


if __name__ == "__main__":
    main()
