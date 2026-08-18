"""Data models for the step 1 pipeline."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class VideoSource:
    """A YouTube video to scrape comments from."""

    video_id: str
    title: str
    model: str
    source_type: str
    url: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this video source to a plain dictionary.

        Returns:
            Dictionary ready for JSON serialization.
        """
        return asdict(self)


@dataclass
class RawComment:
    """A comment as scraped from YouTube (before cleaning)."""

    comment: str
    video_id: str
    model: str
    author: str
    likes: str
    scraped_at: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this raw comment to a plain dictionary.

        Returns:
            Dictionary ready for JSON serialization.
        """
        return asdict(self)


@dataclass
class CleanComment:
    """A comment after cleaning, ready for CSV export."""

    comment: str
    model: str
    video_id: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this clean comment to a plain dictionary.

        Returns:
            Dictionary ready for JSON serialization.
        """
        return asdict(self)


@dataclass
class UnlabeledRow:
    """One row in the unlabeled CSV file."""

    comment: str
    sentiment: str
    model: str
    video_id: str
    reviewed: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this row to a plain dictionary for pandas export.

        Returns:
            Dictionary with CSV column keys.
        """
        return asdict(self)
