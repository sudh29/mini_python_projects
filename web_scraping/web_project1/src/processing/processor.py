import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataProcessor:
    """A class to process tweet data."""

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the DataProcessor.
        Args:
            df: A pandas DataFrame containing tweet data.
        """
        self.df = df

    def process_tweets(self) -> pd.DataFrame:
        """
        Cleans and normalizes the DataFrame of tweets.
        Returns:
            A pandas DataFrame with cleaned and normalized data.
        """
        if self.df.empty:
            logging.warning("Input DataFrame is empty. No processing will be done.")
            return self.df

        # Handle duplicates and missing values
        self.df.drop_duplicates(
            subset=["content", "username", "timestamp"], inplace=True
        )
        self.df.fillna({"content": ""}, inplace=True)

        # Normalize text and convert timestamp
        self.df["content"] = self.df["content"].str.lower()
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["content"] = (
            self.df["content"].str.encode("ascii", "ignore").str.decode("ascii")
        )

        logging.info(f"Processed {len(self.df)} tweets.")
        return self.df

    def save_to_parquet(self, filepath: str):
        """
        Saves the DataFrame to a Parquet file.
        Args:
            filepath: The path to the output Parquet file.
        """
        try:
            self.df.to_parquet(filepath, index=False)
            logging.info(f"Data saved to {filepath}")
        except Exception as e:
            logging.error(f"Failed to save data to Parquet: {e}")
