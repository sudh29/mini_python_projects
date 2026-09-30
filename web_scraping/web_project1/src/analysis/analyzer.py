import logging

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataAnalyzer:
    """A class for analyzing tweet data."""

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the DataAnalyzer.
        Args:
            df: A pandas DataFrame with a 'content' column.
        """
        self.df = df

    def perform_sentiment_analysis(self) -> pd.DataFrame:
        """
        Performs rule-based sentiment analysis on the tweet content.
        Returns:
            A pandas DataFrame with an added 'sentiment' column.
        """
        if "content" not in self.df.columns:
            logging.error("DataFrame must have a 'content' column.")
            return self.df

        positive_words = ["buy", "bullish", "profit", "up", "high", "rally"]
        negative_words = ["sell", "bearish", "loss", "down", "low", "crash"]

        def get_sentiment(text):
            score = sum(1 for word in positive_words if word in text)
            score -= sum(1 for word in negative_words if word in text)
            if score > 0:
                return "positive"
            elif score < 0:
                return "negative"
            else:
                return "neutral"

        self.df["sentiment"] = self.df["content"].apply(get_sentiment)
        logging.info("Sentiment analysis complete.")
        return self.df


class Visualizer:
    """A class for visualizing tweet data."""

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the Visualizer.
        Args:
            df: A pandas DataFrame with a 'sentiment' column.
        """
        self.df = df

    def visualize_sentiment_distribution(self, output_path: str):
        """
        Visualizes and saves the sentiment distribution.
        Args:
            output_path: The path to save the output plot.
        """
        if "sentiment" not in self.df.columns:
            logging.error("DataFrame needs a 'sentiment' column for visualization.")
            return

        sentiment_counts = self.df["sentiment"].value_counts()
        plt.figure(figsize=(8, 6))
        sentiment_counts.plot(kind="bar", color=["green", "red", "blue"])
        plt.title("Sentiment Distribution of Tweets")
        plt.xlabel("Sentiment")
        plt.ylabel("Number of Tweets")
        plt.xticks(rotation=0)
        plt.savefig(output_path)
        logging.info(f"Sentiment distribution plot saved to {output_path}")
        plt.close()
