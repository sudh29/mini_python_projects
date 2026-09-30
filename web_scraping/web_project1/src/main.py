"""End-to-end data collection, processing, and sentiment analysis pipeline."""

import logging
import os
from datetime import UTC, datetime, timedelta

try:
    from web_scraping.web_project1.src.analysis.analyzer import DataAnalyzer, Visualizer
    from web_scraping.web_project1.src.collection.collector import DataCollector
    from web_scraping.web_project1.src.processing.processor import DataProcessor
except ImportError:
    from analysis.analyzer import DataAnalyzer, Visualizer
    from collection.collector import DataCollector
    from processing.processor import DataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Pipeline:
    """A class to run the data collection, processing, and analysis pipeline."""

    def __init__(
        self, hashtags: list[str], since_date: str, limit: int, data_dir: str = "data"
    ):
        """
        Initializes the Pipeline.

        Args:
            hashtags: A list of hashtags for mock tweets.
            since_date: The start date for mock tweets (YYYY-MM-DD).
            limit: The number of mock tweets to generate.
            data_dir: The directory to store output files.
        """
        self.hashtags = hashtags
        self.since_date = since_date
        self.limit = limit
        self.data_dir = data_dir
        self.processed_data_path = os.path.join(
            self.data_dir, "processed_tweets.parquet"
        )
        self.visualization_path = os.path.join(
            self.data_dir, "sentiment_distribution.png"
        )

    def run(self) -> bool:
        """
        Executes the entire data pipeline.

        Returns:
            bool: True if pipeline completed successfully, False otherwise.
        """
        logger.info("Starting the data pipeline.")
        os.makedirs(self.data_dir, exist_ok=True)

        # 1. Data Collection
        collector = DataCollector(self.hashtags, self.since_date, self.limit)
        raw_tweets_df = collector.generate_mock_tweets()
        if raw_tweets_df.empty:
            logger.error("No tweets were collected. Exiting.")
            return False

        # 2. Data Processing
        processor = DataProcessor(raw_tweets_df)
        processed_tweets_df = processor.process_tweets()
        if processed_tweets_df.empty:
            logger.error("No tweets left after processing. Exiting.")
            return False
        processor.save_to_parquet(self.processed_data_path)

        # 3. Analysis and Visualization
        analyzer = DataAnalyzer(processed_tweets_df)
        analyzed_df = analyzer.perform_sentiment_analysis()
        visualizer = Visualizer(analyzed_df)
        visualizer.visualize_sentiment_distribution(self.visualization_path)

        logger.info("Pipeline finished successfully.")
        return True


def run_default_pipeline(
    limit: int = 200, output_dir: str = "web_scraping/web_project1/src/data"
) -> bool:
    """Run the pipeline with default configuration."""
    hashtags = ["#nifty50", "#sensex", "#intraday", "#banknifty"]
    start_date = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    pipeline = Pipeline(hashtags, start_date, limit, data_dir=output_dir)
    return pipeline.run()


if __name__ == "__main__":
    success = run_default_pipeline()
    exit(0 if success else 1)
