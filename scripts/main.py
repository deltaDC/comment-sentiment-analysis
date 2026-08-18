"""CLI entry point for the step 1 data pipeline."""

import argparse
import logging
import sys

from scripts.cleaner import CommentCleaner
from scripts.config import (
    CLEANED_COMMENTS_PATH,
    RAW_COMMENTS_PATH,
    UNLABELED_CSV_PATH,
    VIDEO_SOURCES_PATH,
)
from scripts.exporter import CsvExporter
from scripts.scraper import YouTubeScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_scrape() -> None:
    """
    Scrape YouTube comments and save raw JSON.

    Reads data/video_sources.json and writes data/raw_comments.json.
    """
    scraper = YouTubeScraper()
    comments = scraper.scrape_all(VIDEO_SOURCES_PATH)
    scraper.save_raw_comments(comments, RAW_COMMENTS_PATH)
    logger.info("Scrape finished.")


def run_clean() -> None:
    """
    Clean raw comments and save intermediate JSON.

    Reads data/raw_comments.json and writes data/cleaned_comments.json.
    """
    cleaner = CommentCleaner()
    raw_comments = cleaner.load_raw_comments(RAW_COMMENTS_PATH)
    cleaned = cleaner.clean(raw_comments)
    trimmed = cleaner.trim_to_target_size(cleaned)
    cleaner.validate_export_size(trimmed)
    cleaner.save_cleaned_comments(trimmed, CLEANED_COMMENTS_PATH)
    logger.info("Clean finished.")


def run_export() -> None:
    """
    Export cleaned comments to unlabeled CSV.

    Reads data/cleaned_comments.json and writes data/comments_unlabeled.csv.
    """
    exporter = CsvExporter()
    cleaned = exporter.load_cleaned_comments(CLEANED_COMMENTS_PATH)
    exporter.export(cleaned, UNLABELED_CSV_PATH)
    logger.info("Export finished.")


def run_all() -> None:
    """
    Run scrape, clean, and export in sequence.
    """
    run_scrape()
    run_clean()
    run_export()
    logger.info(
        "Pipeline complete. Label data/comments_unlabeled.csv in Cursor, "
        "then save as data/comments.csv."
    )


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Step 1: scrape VinFast YouTube comments and export unlabeled CSV.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scrape", help="Scrape comments from video_sources.json")
    subparsers.add_parser("clean", help="Clean raw_comments.json")
    subparsers.add_parser("export", help="Export cleaned_comments.json to CSV")
    subparsers.add_parser("run-all", help="Run scrape, clean, and export")

    return parser


def main() -> None:
    """Parse CLI args and run the selected command."""
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "scrape": run_scrape,
        "clean": run_clean,
        "export": run_export,
        "run-all": run_all,
    }

    try:
        command_fn = commands[args.command]
        command_fn()
    except (ValueError, FileNotFoundError) as error:
        logger.error("%s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
