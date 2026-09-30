"""
Entry point for web_project1: Indian Stock Market Sentiment Pipeline.

Executes data generation, cleaning, Parquet export, rule-based sentiment
analysis, and matplotlib visualization.
"""

import sys

from web_scraping.web_project1.src.main import run_default_pipeline


def main():
    """Run default sentiment analysis pipeline."""
    success = run_default_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
