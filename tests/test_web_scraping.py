"""Unit tests for web_scraping module."""

import json

import pytest
import requests_mock

from web_scraping.web_scraping import WebScraper


def test_invalid_url_raises():
    """Verify ValueError on unsupported URL schemes."""
    scraper = WebScraper()
    with pytest.raises(ValueError, match="Invalid URL"):
        scraper.fetch_page("ftp://ftp.example.com")


def test_fetch_page_success():
    """Verify successful page fetching."""
    scraper = WebScraper(rate_limit=0.0)
    test_url = "https://example.com/test-page"

    with requests_mock.Mocker() as m:
        m.get(
            test_url,
            text="<html><body><h1>Hello Test</h1></body></html>",
            status_code=200,
        )
        html = scraper.fetch_page(test_url)
        assert html is not None
        assert "Hello Test" in html


def test_fetch_page_retry_and_recover():
    """Verify retry logic on transient HTTP errors."""
    scraper = WebScraper(max_retries=3, retry_delay=0.01, rate_limit=0.0)
    test_url = "https://example.com/flaky"

    with requests_mock.Mocker() as m:
        m.register_uri(
            "GET",
            test_url,
            [
                {"status_code": 500, "text": "Server Error"},
                {"status_code": 200, "text": "Recovered Payload"},
            ],
        )
        html = scraper.fetch_page(test_url)
        assert html == "Recovered Payload"


def test_fetch_page_max_retries_failure():
    """Verify None returned when max retries are exceeded."""
    scraper = WebScraper(max_retries=2, retry_delay=0.01, rate_limit=0.0)
    test_url = "https://example.com/fail"

    with requests_mock.Mocker() as m:
        m.get(test_url, status_code=503)
        html = scraper.fetch_page(test_url)
        assert html is None


def test_extract_articles():
    """Verify CSS selector data extraction."""
    scraper = WebScraper()
    sample_html = """
    <html>
      <body>
        <article class="post">
          <h2 class="title">First Article</h2>
          <a class="url" href="https://example.com/1">Read more</a>
        </article>
        <article class="post">
          <h2 class="title">Second Article</h2>
          <a class="url" href="https://example.com/2">Read more</a>
        </article>
      </body>
    </html>
    """
    soup = scraper.parse_page(sample_html)
    assert soup is not None

    selectors = {
        "container": "article.post",
        "title": "h2.title",
        "link": "a.url",
    }
    articles = scraper.extract_articles(soup, selectors)
    assert len(articles) == 2
    assert articles[0]["title"] == "First Article"
    assert articles[0]["link"] == "https://example.com/1"
    assert articles[1]["title"] == "Second Article"


def test_scrape_and_export(tmp_path):
    """Verify end-to-end scrape and export to JSON and CSV."""
    scraper = WebScraper(rate_limit=0.0)
    test_url = "https://example.com/news"
    sample_html = """
    <div class="card">
        <h3>News Headline</h3>
        <a href="/news/1">Link</a>
    </div>
    """

    json_out = tmp_path / "news.json"
    csv_out = tmp_path / "news.csv"

    with requests_mock.Mocker() as m:
        m.get(test_url, text=sample_html)
        selectors = {"container": "div.card", "title": "h3", "link": "a"}

        # Scrape to JSON
        articles = scraper.scrape(
            test_url, selectors, output_file=str(json_out), format="json"
        )
        assert len(articles) == 1
        assert json_out.exists()
        saved_data = json.loads(json_out.read_text(encoding="utf-8"))
        assert saved_data[0]["title"] == "News Headline"

        # Export to CSV
        scraper._save_results(articles, str(csv_out), format="csv")
        assert csv_out.exists()
        assert "News Headline" in csv_out.read_text(encoding="utf-8")


def test_context_manager():
    """Verify WebScraper context manager lifecycle."""
    with WebScraper() as scraper:
        assert scraper.session is not None
