# Web Scraping & Data Analytics Suite

A comprehensive collection of web scraping frameworks, media analytics notebooks, and automated data pipelines.

---

## Directory Overview

```
web_scraping/
├── README.md               # Master web scraping documentation
├── web_scraping.py         # Reusable WebScraper class with exponential backoff & rate limiting
├── web_project0/           # YouTube metrics analysis & healthcare clinic directory extraction
│   ├── README.md           # Dedicated project guide
│   ├── validate_data.py    # Headless dataset schema validator
│   ├── youtube_views.csv   # Structured YouTube metrics dataset
│   └── *.ipynb             # Exploratory analysis & scraping Jupyter notebooks
└── web_project1/           # Real-time Indian Stock Market sentiment analysis pipeline
    ├── README.md           # Dedicated pipeline architecture guide
    ├── main.py             # Canonical pipeline launcher
    └── src/                # Pipeline modules (collection, processing, analysis, visualization)
```

---

## Component Highlights

### 1. General Web Scraper (`web_scraping.py`)

A production-ready web scraper featuring:
- **Resilient Requests:** Automatic retry with exponential backoff (`2^attempt * delay`).
- **Polite Crawling:** Configurable rate limiting (`rate_limit=1.0s`) and rotating User-Agents.
- **BeautifulSoup Integration:** HTML parsing with CSS selector extraction.
- **Context Manager Protocol:** Clean `with WebScraper() as scraper:` lifecycle.
- **Multi-Format Export:** Seamless saving to JSON or CSV.

```bash
uv run python web_scraping/web_scraping.py "https://news.ycombinator.com" --selectors '{"container": "tr.athing", "title": "span.titleline > a", "link": "span.titleline > a"}' --output hn.json
```

### 2. YouTube Analytics & Clinic Scraping (`web_project0/`)

- Analysis of video performance metrics, view count parsing, and clean numerical transformation.
- Healthcare clinic directory extraction notebooks.
- Automated validation via `uv run python web_scraping/web_project0/validate_data.py`.

### 3. Financial Sentiment Pipeline (`web_project1/`)

- Modular financial intelligence pipeline for Indian stock market hashtags (`#nifty50`, `#sensex`, `#banknifty`).
- Cleans and deduplicates social media data.
- Exports to columnar Apache Parquet (`processed_tweets.parquet`).
- Runs rule-based financial sentiment scoring and outputs visual distribution graphs.

```bash
uv run python web_scraping/web_project1/main.py
```

---

## Testing

Run tests across all web scraping components:

```bash
uv run pytest tests/test_web_scraping.py tests/test_web_project0.py tests/test_web_project1.py
```
