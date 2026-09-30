"""Data validation utility for web_project0 datasets."""

import logging
import sys
from pathlib import Path

from web_scraping.web_project0 import load_youtube_dataset

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def validate():
    """Validate youtube_views.csv dataset integrity."""
    csv_file = Path(__file__).parent / "youtube_views.csv"
    logger.info(f"Validating dataset: {csv_file}")

    try:
        df = load_youtube_dataset(csv_file)
        logger.info(f"Loaded {len(df)} records.")

        null_titles = df["title"].isnull().sum()
        null_views = df["clean_views"].isnull().sum()

        logger.info(f"Null titles: {null_titles}, Null views: {null_views}")
        logger.info(f"Mean view count: {df['clean_views'].mean():,.0f}")
        logger.info(
            f"Top video by views: '{df.loc[df['clean_views'].idxmax(), 'title']}' ({df['clean_views'].max():,} views)"
        )

        assert len(df) > 0, "Dataset cannot be empty"
        assert null_views == 0, "All rows must have parsed numerical views"
        logger.info("Dataset validation passed successfully!")
        return True
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
