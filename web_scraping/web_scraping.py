"""
Web scraping utility for collecting data from websites.

This module provides a flexible web scraping framework with support for:
- HTTP requests with proper headers and timeouts
- HTML parsing with Beautiful Soup
- Retry logic with exponential backoff
- Session management and context manager protocol
- JSON/CSV export
- Error handling and logging

Usage:
    from web_scraping import WebScraper

    with WebScraper() as scraper:
        data = scraper.scrape(url='https://example.com', selectors={'title': 'h1'})
"""

import csv
import json
import logging
import random
import sys
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WebScraper:
    """A robust web scraper with error handling and retry logic."""

    # Common user agents to rotate
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit: float = 1.0,
    ):
        """
        Initialize the web scraper.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            rate_limit: Delay between requests in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENTS[0]})
        self.last_request_time = 0.0

    def __enter__(self) -> "WebScraper":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _get_user_agent(self) -> str:
        """Get a random user agent from the list."""
        return random.choice(self.USER_AGENTS)

    def _respect_rate_limit(self) -> None:
        """Respect rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def fetch_page(self, url: str) -> str | None:
        """
        Fetch a webpage with retry logic.

        Args:
            url: URL to fetch

        Returns:
            str: HTML content, or None if fetch fails

        Raises:
            ValueError: If URL is invalid
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

        self._respect_rate_limit()
        headers = {"User-Agent": self._get_user_agent()}

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})"
                )

                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()

                logger.info(f"Successfully fetched {url}")
                return response.text

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    logger.warning(f"Request failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to fetch {url} after {self.max_retries} attempts"
                    )
                    return None
        return None

    def parse_page(
        self, html: str, parser: str = "html.parser"
    ) -> BeautifulSoup | None:
        """
        Parse HTML content with Beautiful Soup.

        Args:
            html: HTML content to parse
            parser: Parser to use (default: html.parser)

        Returns:
            BeautifulSoup: Parsed soup object, or None if parsing fails
        """
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return None

    def extract_articles(
        self, soup: BeautifulSoup, selectors: dict[str, str]
    ) -> list[dict[str, Any]]:
        """
        Extract article data using CSS selectors.

        Args:
            soup: BeautifulSoup object
            selectors: Dict of field names to CSS selectors

        Returns:
            List of dictionaries with extracted data
        """
        articles: list[dict[str, Any]] = []

        container_selector = selectors.get("container", "article")
        containers = soup.find_all(container_selector)

        if not containers:
            # If no containers matched, try select on the document level
            selected = soup.select(container_selector)
            containers = selected if selected else [soup]

        logger.info(f"Found {len(containers)} containers")

        for container in containers:
            article: dict[str, Any] = {}

            for field, selector in selectors.items():
                if field == "container":
                    continue

                try:
                    element = container.select_one(selector)
                    if element:
                        if field == "link":
                            article[field] = element.get("href", "")
                        else:
                            article[field] = element.get_text(strip=True)
                    else:
                        article[field] = None
                except Exception as e:
                    logger.debug(f"Error extracting {field}: {str(e)}")
                    article[field] = None

            if any(v is not None for v in article.values()):
                articles.append(article)

        return articles

    def scrape(
        self,
        url: str,
        selectors: dict[str, str],
        output_file: str | None = None,
        format: str = "json",
    ) -> list[dict[str, Any]]:
        """
        Scrape a webpage and optionally save results.

        Args:
            url: URL to scrape
            selectors: CSS selectors for data extraction
            output_file: Optional file to save results
            format: Output format ('json' or 'csv')

        Returns:
            List of extracted data dictionaries
        """
        try:
            # Fetch page
            html = self.fetch_page(url)
            if not html:
                return []

            # Parse page
            soup = self.parse_page(html)
            if not soup:
                return []

            # Extract data
            articles = self.extract_articles(soup, selectors)
            logger.info(f"Extracted {len(articles)} articles")

            # Save results
            if output_file and articles:
                self._save_results(articles, output_file, format)

            return articles

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []

    def _save_results(
        self, data: list[dict[str, Any]], output_file: str, format: str = "json"
    ) -> None:
        """Save scraped data to file."""
        try:
            if format.lower() == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            elif format.lower() == "csv":
                if data:
                    keys = list(data[0].keys())
                    with open(output_file, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(data)

            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

    def close(self) -> None:
        """Close the session."""
        self.session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web scraping utility")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument(
        "--selectors",
        type=str,
        default='{"container": "article", "title": "h2", "link": "a"}',
        help="JSON string of CSS selectors",
    )
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Output format"
    )

    args = parser.parse_args()

    try:
        selectors = json.loads(args.selectors)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in selectors")
        sys.exit(1)

    with WebScraper() as scraper:
        articles = scraper.scrape(
            url=args.url,
            selectors=selectors,
            output_file=args.output,
            format=args.format,
        )

    print(f"\nFound {len(articles)} articles")
    for article in articles[:3]:
        print(f"- {article}")
