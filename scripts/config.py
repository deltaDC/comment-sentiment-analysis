"""Paths and limits for the step 1 data pipeline."""

from pathlib import Path

# Project root is one level above the scripts package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

VIDEO_SOURCES_PATH = DATA_DIR / "video_sources.json"
RAW_COMMENTS_PATH = DATA_DIR / "raw_comments.json"
CLEANED_COMMENTS_PATH = DATA_DIR / "cleaned_comments.json"
UNLABELED_CSV_PATH = DATA_DIR / "comments_unlabeled.csv"

# Scraping limits
COMMENTS_PER_VIDEO = 300
SCRAPE_SLEEP_SECONDS = 1.0
# 0 = popular/top comments (usually more rows per video)
YOUTUBE_SORT_BY_POPULAR = 0

# Cleaning limits
MIN_COMMENT_LENGTH = 10
MAX_EXPORT_ROWS = 1000
# Assignment requires 500–1,000; 800+ is a stretch goal when videos have few comments
MIN_EXPORT_ROWS = 500
MAX_SHARE_PER_VIDEO = 0.25

# Spam patterns (lowercase match)
SPAM_PATTERNS = (
    "sub cho",
    "ai xem tới đây",
    "ai xem den day",
    "cho xin 1 tim",
    "like và sub",
    "like va sub",
    "zalo.me",
    "nhóm cập nhật và tư vấn mua xe",
)

# CSV columns for unlabeled export
CSV_COLUMNS = (
    "comment",
    "sentiment",
    "model",
    "video_id",
    "reviewed",
)
