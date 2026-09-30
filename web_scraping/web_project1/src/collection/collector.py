import logging
import random
from datetime import UTC, datetime, timedelta

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataCollector:
    """A class to collect mock tweet data."""

    def __init__(self, hashtags: list[str], since_date: str, limit: int):
        """
        Initializes the DataCollector.
        Args:
            hashtags: A list of hashtags for mock tweets.
            since_date: The start date for mock tweets (YYYY-MM-DD).
            limit: The number of mock tweets to generate.
        """
        self.hashtags = hashtags
        self.since_date = since_date
        self.limit = limit

    def generate_mock_tweets(self) -> pd.DataFrame:
        """
        Generates a DataFrame of mock tweets.
        Returns:
            A pandas DataFrame with the mock tweets.
        """
        logging.info("Generating mock tweet data.")
        tweets = []
        start_date_obj = datetime.strptime(self.since_date, "%Y-%m-%d").replace(
            tzinfo=UTC
        )

        positive_words = ["buy", "bullish", "profit", "up", "high", "rally"]
        negative_words = ["sell", "bearish", "loss", "down", "low", "crash"]

        for _ in range(self.limit):
            timestamp = start_date_obj + timedelta(
                hours=random.randint(0, 23), minutes=random.randint(0, 59)
            )
            hashtag = random.choice(self.hashtags)
            sentiment_type = random.choice(["positive", "negative", "neutral"])

            if sentiment_type == "positive":
                extra_word = random.choice(positive_words)
                content = (
                    f"Mock tweet about {hashtag}. Feeling {extra_word}. #stockmarket"
                )
            elif sentiment_type == "negative":
                extra_word = random.choice(negative_words)
                content = (
                    f"Mock tweet about {hashtag}. Feeling {extra_word}. #stockmarket"
                )
            else:
                content = f"Mock tweet about {hashtag}. #stockmarket"

            tweets.append(
                {
                    "username": f"user_{random.randint(1, 1000)}",
                    "timestamp": timestamp,
                    "content": content,
                    "likes": random.randint(0, 1000),
                    "retweets": random.randint(0, 500),
                    "replies": random.randint(0, 100),
                    "quotes": random.randint(0, 50),
                    "hashtags": ["stockmarket", hashtag.strip("#")],
                    "mentions": [f"expert_{random.randint(1, 10)}"],
                }
            )

        df = pd.DataFrame(tweets)
        logging.info(f"Generated {len(df)} mock tweets.")
        return df
