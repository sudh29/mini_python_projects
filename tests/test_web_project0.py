"""Unit tests for web_project0 (YouTube and clinic data scraping)."""

import pandas as pd
import pytest

from web_scraping.web_project0 import load_youtube_dataset
from web_scraping.web_project0.validate_data import validate


def test_load_youtube_dataset_default():
    """Verify loading default YouTube views dataset."""
    df = load_youtube_dataset()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 50
    assert "title" in df.columns
    assert "clean_views" in df.columns
    assert "video_url" in df.columns


def test_youtube_views_numeric():
    """Verify clean_views column contains non-negative numbers without NaNs."""
    df = load_youtube_dataset()
    assert df["clean_views"].isnull().sum() == 0
    assert (df["clean_views"] >= 0).all()


def test_load_youtube_dataset_nonexistent(tmp_path):
    """Verify FileNotFoundError on nonexistent CSV file."""
    fake_csv = tmp_path / "not_there.csv"
    with pytest.raises(FileNotFoundError):
        load_youtube_dataset(fake_csv)


def test_validate_data_passes():
    """Verify validate() returns True on the genuine dataset."""
    assert validate() is True
