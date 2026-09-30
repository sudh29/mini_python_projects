"""Unit tests for web_project1 (Stock Market Tweet Sentiment Pipeline)."""

import pandas as pd

from web_scraping.web_project1.src.analysis.analyzer import DataAnalyzer, Visualizer
from web_scraping.web_project1.src.collection.collector import DataCollector
from web_scraping.web_project1.src.main import Pipeline
from web_scraping.web_project1.src.processing.processor import DataProcessor


def test_data_collector_generates_tweets():
    """Verify DataCollector creates expected DataFrame structure."""
    collector = DataCollector(
        hashtags=["#nifty50", "#sensex"],
        since_date="2026-09-20",
        limit=15,
    )
    df = collector.generate_mock_tweets()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 15
    for col in ["username", "timestamp", "content", "likes", "hashtags"]:
        assert col in df.columns


def test_data_processor(tmp_path):
    """Verify DataProcessor cleaning and Parquet export."""
    raw_data = pd.DataFrame(
        [
            {
                "username": "u1",
                "timestamp": "2026-09-28 10:00:00",
                "content": "BULLISH #nifty50",
            },
            {
                "username": "u1",
                "timestamp": "2026-09-28 10:00:00",
                "content": "BULLISH #nifty50",
            },  # duplicate
            {
                "username": "u2",
                "timestamp": "2026-09-28 11:00:00",
                "content": "Bearish crash #sensex",
            },
        ]
    )

    processor = DataProcessor(raw_data)
    processed = processor.process_tweets()

    # Deduplicated from 3 to 2
    assert len(processed) == 2
    assert processed.iloc[0]["content"] == "bullish #nifty50"

    # Parquet export
    pq_path = tmp_path / "tweets.parquet"
    processor.save_to_parquet(str(pq_path))
    assert pq_path.exists()

    loaded = pd.read_parquet(pq_path)
    assert len(loaded) == 2


def test_data_analyzer_sentiment():
    """Verify rule-based sentiment tagging."""
    df = pd.DataFrame(
        [
            {"content": "huge profit buy now high rally"},
            {"content": "market crash loss down bear"},
            {"content": "regular trading day nifty"},
        ]
    )

    analyzer = DataAnalyzer(df)
    analyzed = analyzer.perform_sentiment_analysis()

    assert analyzed.iloc[0]["sentiment"] == "positive"
    assert analyzed.iloc[1]["sentiment"] == "negative"
    assert analyzed.iloc[2]["sentiment"] == "neutral"


def test_visualizer_renders_chart(tmp_path):
    """Verify Visualizer creates PNG chart headlessly."""
    df = pd.DataFrame({"sentiment": ["positive", "positive", "negative", "neutral"]})
    chart_path = tmp_path / "chart.png"
    visualizer = Visualizer(df)
    visualizer.visualize_sentiment_distribution(str(chart_path))

    assert chart_path.exists()
    assert chart_path.stat().st_size > 0


def test_pipeline_end_to_end(tmp_path):
    """Verify entire Pipeline execution in an isolated directory."""
    pipeline = Pipeline(
        hashtags=["#nifty50", "#intraday"],
        since_date="2026-09-25",
        limit=20,
        data_dir=str(tmp_path),
    )

    success = pipeline.run()
    assert success is True
    assert (tmp_path / "processed_tweets.parquet").exists()
    assert (tmp_path / "sentiment_distribution.png").exists()
