"""Scrape YouTube comments for configured VinFast videos."""

import json
import logging
import re
import time
from datetime import date
from pathlib import Path
from typing import Iterator

from youtube_comment_downloader import YoutubeCommentDownloader

from scripts.config import (
    COMMENTS_PER_VIDEO,
    SCRAPE_SLEEP_SECONDS,
    VIDEO_SOURCES_PATH,
    YOUTUBE_SORT_BY_POPULAR,
)
from scripts.models import RawComment, VideoSource

logger = logging.getLogger(__name__)

# Valid YouTube video IDs are 11 characters.
VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


class VideoSourceLoader:
    """Load and validate the curated video list."""

    def load(self, path: Path) -> list[VideoSource]:
        """
        Read video sources from a JSON file.

        Args:
            path: Path to video_sources.json.

        Returns:
            List of valid VideoSource objects.
        """
        raw_items = self._read_json_file(path)
        sources: list[VideoSource] = []

        for item in raw_items:
            source = self._parse_item(item)
            if source is not None:
                sources.append(source)

        return sources

    def _read_json_file(self, path: Path) -> list[dict]:
        """
        Load JSON array from disk.

        Args:
            path: File path to read.

        Returns:
            List of dictionary items from the JSON file.
        """
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON array in {path}")

        return data

    def _parse_item(self, item: dict) -> VideoSource | None:
        """
        Parse one JSON object into a VideoSource.

        Skips entries with missing fields or placeholder video IDs.

        Args:
            item: One object from video_sources.json.

        Returns:
            VideoSource if valid, otherwise None.
        """
        video_id = str(item.get("video_id", "")).strip()

        if not VIDEO_ID_PATTERN.match(video_id):
            title = item.get("title", "unknown")
            logger.warning("Skipping invalid video_id for '%s': %s", title, video_id)
            return None

        required_fields = ("title", "model", "source_type", "url")
        for field_name in required_fields:
            if not item.get(field_name):
                logger.warning("Skipping video %s: missing field '%s'", video_id, field_name)
                return None

        return VideoSource(
            video_id=video_id,
            title=str(item["title"]),
            model=str(item["model"]),
            source_type=str(item["source_type"]),
            url=str(item["url"]),
        )


class YouTubeScraper:
    """Fetch comments from YouTube for each configured video."""

    def __init__(self, downloader: YoutubeCommentDownloader | None = None) -> None:
        """
        Create a scraper instance.

        Args:
            downloader: Optional downloader for testing; creates default if omitted.
        """
        if downloader is None:
            downloader = YoutubeCommentDownloader()

        self._downloader = downloader
        self._loader = VideoSourceLoader()

    def scrape_all(self, sources_path: Path = VIDEO_SOURCES_PATH) -> list[RawComment]:
        """
        Scrape comments for every video in the sources file.

        Args:
            sources_path: Path to video_sources.json.

        Returns:
            Combined list of raw comments from all videos.
        """
        sources = self._loader.load(sources_path)

        if not sources:
            raise ValueError(
                f"No valid videos found in {sources_path}. "
                "Add real YouTube video_id values (11 characters)."
            )

        all_comments: list[RawComment] = []
        scraped_at = date.today().isoformat()

        for index, source in enumerate(sources):
            logger.info(
                "Scraping video %s/%s: %s (%s)",
                index + 1,
                len(sources),
                source.title,
                source.model,
            )

            video_comments = self.scrape_video(source, scraped_at)
            all_comments.extend(video_comments)

            if index < len(sources) - 1:
                time.sleep(SCRAPE_SLEEP_SECONDS)

        logger.info("Scraped %s raw comments from %s videos.", len(all_comments), len(sources))
        return all_comments

    def scrape_video(self, source: VideoSource, scraped_at: str) -> list[RawComment]:
        """
        Scrape comments from a single YouTube video.

        Args:
            source: Video metadata from video_sources.json.
            scraped_at: ISO date string for this scrape run.

        Returns:
            Raw comments from this video (may be empty on failure).
        """
        comments: list[RawComment] = []

        try:
            comment_stream = self._fetch_comments(source.url)
        except Exception as error:
            logger.error("Failed to scrape %s: %s", source.video_id, error)
            return comments

        for item in comment_stream:
            text = str(item.get("text", "")).strip()
            if not text:
                continue

            raw_comment = RawComment(
                comment=text,
                video_id=source.video_id,
                model=source.model,
                author=str(item.get("author", "")),
                likes=str(item.get("votes", "0")),
                scraped_at=scraped_at,
            )
            comments.append(raw_comment)

            if len(comments) >= COMMENTS_PER_VIDEO:
                break

        logger.info("Collected %s comments from %s.", len(comments), source.video_id)
        return comments

    def _fetch_comments(self, youtube_url: str) -> Iterator[dict]:
        """
        Call the youtube-comment-downloader library.

        Args:
            youtube_url: Full YouTube watch URL.

        Returns:
            Iterator of comment dictionaries from the library.
        """
        return self._downloader.get_comments_from_url(
            youtube_url,
            sort_by=YOUTUBE_SORT_BY_POPULAR,
            sleep=0.05,
        )

    def save_raw_comments(
        self,
        comments: list[RawComment],
        output_path: Path,
    ) -> None:
        """
        Write raw comments to a JSON file.

        Args:
            comments: List of scraped comments.
            output_path: Destination JSON path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = [comment.to_dict() for comment in comments]
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

        logger.info("Saved %s raw comments to %s.", len(comments), output_path)
