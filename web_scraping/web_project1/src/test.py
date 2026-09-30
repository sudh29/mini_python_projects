#!/usr/bin/env python3
"""
Collect tweets for Indian stock-market hashtags using snscrape or synthetic generator.
Saves deduplicated results to a Parquet file.
"""

import logging
import signal
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

try:
    import snscrape.modules.twitter as sntwitter
except ImportError:
    sntwitter = None

# Config
HASHTAGS = ["#nifty50", "#sensex", "#intraday", "#banknifty"]
TARGET_COUNT = 2000
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BATCH_WRITE_SIZE = 500  # flush to disk every N tweets
RETRY_BACKOFF_BASE = 2
MAX_RETRIES = 5

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Graceful shutdown
shutdown_flag = False


def handle_sigint(signum, frame):
    global shutdown_flag
    shutdown_flag = True
    logger.info("Received interrupt; will stop after current batch.")


signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigint)


def build_query():
    since_date = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    # include all hashtags OR'ed, restrict to last 24h using since:
    q = " OR ".join(HASHTAGS) + f" since:{since_date}"
    # exclude retweets to reduce duplicates if desired:
    q += " -filter:retweets"
    return q


def tweet_to_record(tweet):
    # tweet is a snscrape Tweet object
    return {
        "tweet_id": tweet.id,
        "username": tweet.user.username if tweet.user else None,
        "timestamp": tweet.date.astimezone(UTC).isoformat(),
        "content": tweet.content,
        "likeCount": tweet.likeCount,
        "retweetCount": tweet.retweetCount,
        "replyCount": tweet.replyCount,
        "quoteCount": tweet.quoteCount,
        "hashtags": tweet.hashtags if tweet.hashtags else [],
        "mentions": [u.username for u in (tweet.mentionedUsers or [])],
        "language": getattr(tweet, "lang", None),  # may be None
    }


def write_parquet(df, file_path):
    # use pyarrow via pandas
    df.to_parquet(file_path, index=False)
    logger.info(f"Wrote {len(df)} rows to {file_path}")


def collect_tweets(
    target_count=TARGET_COUNT, batch_size=BATCH_WRITE_SIZE, output_dir=OUTPUT_DIR
):
    if sntwitter is None:
        logger.warning(
            "snscrape is not installed or supported on this Python environment. "
            "Using DataCollector mock tweet generation fallback."
        )
        try:
            from web_scraping.web_project1.src.collection.collector import DataCollector
        except ImportError:
            from collection.collector import DataCollector

        collector = DataCollector(
            HASHTAGS,
            (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d"),
            min(target_count, 100),
        )
        df = collector.generate_mock_tweets()
        out_file = (
            output_dir
            / f"stock_tweets_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.parquet"
        )
        write_parquet(df, out_file)
        return

    q = build_query()
    logger.info(f"Query: {q}")
    scraper = sntwitter.TwitterSearchScraper(q)

    records = []
    seen_ids = set()
    total_collected = 0
    batch_index = 0
    retries = 0

    iterator = scraper.get_items()

    try:
        for tweet in iterator:
            if shutdown_flag:
                logger.info("Shutdown flag set, stopping collection loop.")
                break

            # Defensive filtering: ensure tweet within last 24 hours
            if tweet.date < datetime.now(UTC) - timedelta(days=1):
                continue

            rec = tweet_to_record(tweet)
            if rec["tweet_id"] in seen_ids:
                continue
            seen_ids.add(rec["tweet_id"])
            records.append(rec)
            total_collected += 1

            if total_collected % 100 == 0:
                logger.info(f"Collected {total_collected} tweets so far...")

            # Write in batches to avoid memory blowup
            if len(records) >= batch_size:
                batch_index += 1
                df = pd.DataFrame(records)
                out_file = (
                    output_dir
                    / f"tweets_batch_{batch_index}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.parquet"
                )
                write_parquet(df, out_file)
                records = []  # reset records

            if total_collected >= target_count:
                logger.info(f"Target reached: {total_collected} tweets")
                break

        # final flush
        if records:
            batch_index += 1
            df = pd.DataFrame(records)
            out_file = (
                output_dir
                / f"tweets_batch_{batch_index}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.parquet"
            )
            write_parquet(df, out_file)

    except Exception as e:
        logger.exception("Exception during scraping: %s", e)
        while retries < MAX_RETRIES and not shutdown_flag:
            wait = RETRY_BACKOFF_BASE**retries
            logger.info(f"Retrying after {wait}s (attempt {retries + 1}/{MAX_RETRIES})")
            time.sleep(wait)
            retries += 1
            try:
                scraper = sntwitter.TwitterSearchScraper(q)
                for tweet in scraper.get_items():
                    if tweet.id in seen_ids:
                        continue
                    if tweet.date < datetime.now(UTC) - timedelta(days=1):
                        continue
                    rec = tweet_to_record(tweet)
                    seen_ids.add(rec["tweet_id"])
                    records.append(rec)
                    total_collected += 1
                    if len(records) >= batch_size:
                        batch_index += 1
                        df = pd.DataFrame(records)
                        out_file = (
                            output_dir
                            / f"tweets_batch_{batch_index}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}.parquet"
                        )
                        write_parquet(df, out_file)
                        records = []
                    if total_collected >= target_count:
                        break
                if total_collected >= target_count:
                    break
            except Exception as e2:
                logger.exception("Retry attempt failed: %s", e2)
                continue

    files = sorted(output_dir.glob("tweets_batch_*.parquet"))
    if files:
        logger.info("Combining batch files and deduplicating...")
        dfs = [pd.read_parquet(f) for f in files]
        combined = pd.concat(dfs, ignore_index=True)
        combined.drop_duplicates(subset=["tweet_id"], inplace=True)
        final_file = (
            output_dir
            / f"stock_tweets_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.parquet"
        )
        write_parquet(combined, final_file)
        logger.info(f"Final dataset rows: {len(combined)}. Saved to {final_file}")
    else:
        logger.warning("No batch files found to combine.")


if __name__ == "__main__":
    collect_tweets()
