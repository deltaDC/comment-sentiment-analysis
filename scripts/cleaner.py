"""Clean and deduplicate scraped YouTube comments."""

import json
import logging
import re
from pathlib import Path

from scripts.config import (
    MAX_EXPORT_ROWS,
    MAX_SHARE_PER_VIDEO,
    MIN_COMMENT_LENGTH,
    MIN_EXPORT_ROWS,
    SPAM_PATTERNS,
)
from scripts.models import CleanComment, RawComment

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)
EMOJI_ONLY_PATTERN = re.compile(
    r"^[\U0001F300-\U0001FAFF\U00002600-\U000027BF\s]+$",
    re.UNICODE,
)


class CommentCleaner:
    """Filter spam and duplicates from raw comments."""

    def load_raw_comments(self, path: Path) -> list[RawComment]:
        """
        Load raw comments from a JSON file.

        Args:
            path: Path to raw_comments.json.

        Returns:
            List of RawComment objects.
        """
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        comments: list[RawComment] = []
        for item in data:
            comments.append(
                RawComment(
                    comment=str(item["comment"]),
                    video_id=str(item["video_id"]),
                    model=str(item["model"]),
                    author=str(item.get("author", "")),
                    likes=str(item.get("likes", "0")),
                    scraped_at=str(item.get("scraped_at", "")),
                )
            )

        return comments

    def clean(self, raw_comments: list[RawComment]) -> list[CleanComment]:
        """
        Apply all cleaning rules and return deduplicated comments.

        Args:
            raw_comments: Comments straight from the scraper.

        Returns:
            Cleaned comments ready for export.
        """
        kept_comments: list[CleanComment] = []
        seen_normalized_text: set[str] = set()

        for raw in raw_comments:
            if not self._should_keep(raw.comment):
                continue

            normalized = self._normalize_text(raw.comment)
            if normalized in seen_normalized_text:
                continue

            seen_normalized_text.add(normalized)
            kept_comments.append(
                CleanComment(
                    comment=raw.comment.strip(),
                    model=raw.model,
                    video_id=raw.video_id,
                )
            )

        logger.info(
            "Cleaning done: %s kept from %s raw comments.",
            len(kept_comments),
            len(raw_comments),
        )
        return kept_comments

    def trim_to_target_size(self, comments: list[CleanComment]) -> list[CleanComment]:
        """
        Cap row count while keeping a mix across videos.

        If there are more than MAX_EXPORT_ROWS, keep a balanced subset
        so no single video dominates the dataset.

        Args:
            comments: Cleaned comments after dedupe.

        Returns:
            Trimmed list (800-1000 rows when enough data exists).
        """
        if len(comments) <= MAX_EXPORT_ROWS:
            return comments

        per_video: dict[str, list[CleanComment]] = {}
        for comment in comments:
            bucket = per_video.setdefault(comment.video_id, [])
            bucket.append(comment)

        max_per_video = int(MAX_EXPORT_ROWS * MAX_SHARE_PER_VIDEO)
        trimmed: list[CleanComment] = []

        for video_id, video_comments in per_video.items():
            selected = video_comments[:max_per_video]
            trimmed.extend(selected)
            logger.info(
                "Trimmed video %s: kept %s of %s comments.",
                video_id,
                len(selected),
                len(video_comments),
            )

        if len(trimmed) > MAX_EXPORT_ROWS:
            trimmed = trimmed[:MAX_EXPORT_ROWS]

        logger.info("Final trimmed count: %s comments.", len(trimmed))
        return trimmed

    def validate_export_size(self, comments: list[CleanComment]) -> None:
        """
        Warn if the dataset is smaller than the assignment target.

        Args:
            comments: Final cleaned comments before export.

        Raises:
            ValueError: If count is below MIN_EXPORT_ROWS.
        """
        count = len(comments)
        if count < MIN_EXPORT_ROWS:
            raise ValueError(
                f"Only {count} comments after cleaning (need {MIN_EXPORT_ROWS}-{MAX_EXPORT_ROWS}). "
                "Add more videos to data/video_sources.json and scrape again."
            )

        if count > MAX_EXPORT_ROWS:
            logger.warning(
                "Comment count %s exceeds max %s; trim step should have handled this.",
                count,
                MAX_EXPORT_ROWS,
            )

    def save_cleaned_comments(
        self,
        comments: list[CleanComment],
        output_path: Path,
    ) -> None:
        """
        Write cleaned comments to JSON for the export step.

        Args:
            comments: Cleaned comment list.
            output_path: Destination path (cleaned_comments.json).
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = [comment.to_dict() for comment in comments]
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

        logger.info("Saved %s cleaned comments to %s.", len(comments), output_path)

    def _should_keep(self, text: str) -> bool:
        """
        Decide whether one comment passes all filter rules.

        Args:
            text: Raw comment text.

        Returns:
            True if the comment should be kept.
        """
        stripped = text.strip()
        if not stripped:
            return False

        if len(stripped) < MIN_COMMENT_LENGTH:
            return False

        if self._is_spam(stripped):
            return False

        if self._is_link_only(stripped):
            return False

        if self._is_emoji_only(stripped):
            return False

        return True

    def _is_spam(self, text: str) -> bool:
        """
        Check comment against known spam phrase patterns.

        Args:
            text: Comment text.

        Returns:
            True if text matches a spam pattern.
        """
        lowered = text.lower()
        for pattern in SPAM_PATTERNS:
            if pattern in lowered:
                return True
        return False

    def _is_link_only(self, text: str) -> bool:
        """
        Detect comments that are only a URL.

        Args:
            text: Comment text.

        Returns:
            True if the comment is essentially just a link.
        """
        if not URL_PATTERN.search(text):
            return False

        without_url = URL_PATTERN.sub("", text).strip()
        return len(without_url) < MIN_COMMENT_LENGTH

    def _is_emoji_only(self, text: str) -> bool:
        """
        Detect comments made of emoji only.

        Args:
            text: Comment text.

        Returns:
            True if comment has no meaningful letters or digits.
        """
        if EMOJI_ONLY_PATTERN.match(text):
            return True

        letters_and_digits = re.sub(r"[\W_]+", "", text, flags=re.UNICODE)
        return len(letters_and_digits) == 0

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for duplicate detection.

        Args:
            text: Raw comment text.

        Returns:
            Lowercase string with collapsed whitespace.
        """
        lowered = text.lower().strip()
        collapsed = re.sub(r"\s+", " ", lowered)
        return collapsed
