"""Export cleaned comments to an unlabeled CSV file."""

import json
import logging
from pathlib import Path

import pandas as pd

from scripts.config import CSV_COLUMNS, UNLABELED_CSV_PATH
from scripts.models import CleanComment, UnlabeledRow

logger = logging.getLogger(__name__)


class CsvExporter:
    """Write cleaned comments to CSV for manual labeling."""

    def load_cleaned_comments(self, path: Path) -> list[CleanComment]:
        """
        Load cleaned comments from a JSON file.

        Args:
            path: Path to cleaned_comments.json.

        Returns:
            List of CleanComment objects.
        """
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        comments: list[CleanComment] = []
        for item in data:
            comments.append(
                CleanComment(
                    comment=str(item["comment"]),
                    model=str(item["model"]),
                    video_id=str(item["video_id"]),
                )
            )

        return comments

    def build_rows(self, comments: list[CleanComment]) -> list[UnlabeledRow]:
        """
        Convert clean comments into unlabeled CSV rows.

        The sentiment column is left empty for Cursor agent labeling.

        Args:
            comments: Cleaned comments.

        Returns:
            Rows ready for pandas DataFrame export.
        """
        rows: list[UnlabeledRow] = []

        for comment in comments:
            row = UnlabeledRow(
                comment=comment.comment,
                sentiment="",
                model=comment.model,
                video_id=comment.video_id,
                reviewed="false",
            )
            rows.append(row)

        return rows

    def export(
        self,
        comments: list[CleanComment],
        output_path: Path = UNLABELED_CSV_PATH,
    ) -> None:
        """
        Write unlabeled CSV to disk.

        Args:
            comments: Cleaned comments to export.
            output_path: Destination CSV path.
        """
        rows = self.build_rows(comments)
        records = [row.to_dict() for row in rows]

        dataframe = pd.DataFrame(records, columns=list(CSV_COLUMNS))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(output_path, index=False, encoding="utf-8")

        logger.info("Exported %s rows to %s.", len(rows), output_path)
