"""YouTube Analytics and Clinical Data Scraping module."""

from pathlib import Path

import pandas as pd


def load_youtube_dataset(
    csv_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Load and validate the YouTube views dataset.

    Args:
        csv_path: Path to youtube_views.csv. If None, defaults to package dataset.

    Returns:
        pd.DataFrame: Cleaned DataFrame with title, video_url, views, and clean_views.
    """
    if csv_path is None:
        csv_path = Path(__file__).parent / "youtube_views.csv"

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"YouTube views dataset not found: {path}")

    df = pd.read_csv(path)
    # Ensure expected columns
    expected = {"title", "video_url", "views", "clean_views"}
    if not expected.issubset(set(df.columns)):
        raise ValueError(
            f"Dataset missing required columns. Expected at least {expected}"
        )

    # Ensure clean_views is numeric
    df["clean_views"] = pd.to_numeric(df["clean_views"], errors="coerce")
    return df
