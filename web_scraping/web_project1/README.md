# Indian Stock Market Intelligence System (`web_project1`)

A modular, real-time data collection, cleaning, Parquet storage, rule-based sentiment analysis, and visualization pipeline targeting Indian financial market sentiment (`#nifty50`, `#sensex`, `#banknifty`, `#intraday`).

---

## Architecture & Data Flow

```
[ Data Collection ]  ──> [ Data Processing ]  ──> [ Parquet Export ]
(Mock/Live Tweets)        (Deduplicate/Clean)       (pyarrow Columnar)
                                │
                                └──> [ Sentiment Analysis ] ──> [ Visualization ]
                                     (Lexical Rule Scorer)      (Matplotlib PNG)
```

### Module Breakdown

- **Data Collection (`src/collection/collector.py`):** Configurable generator producing realistic tweet payloads with usernames, timestamps, financial hashtags, and sentiment seed words.
- **Data Processing (`src/processing/processor.py`):** Deduplication on `(content, username, timestamp)`, ASCII text normalization, UTC timestamp parsing, and columnar storage export to Parquet.
- **Sentiment Analysis & Visualization (`src/analysis/analyzer.py`):** Financial lexicon sentiment categorization (`positive`, `negative`, `neutral`) and headless matplotlib bar chart generation.
- **Pipeline Runner (`src/main.py` & `main.py`):** Unified execution entrypoint orchestrating the entire lifecycle.

---

## Directory Structure

```
web_project1/
├── main.py                     # Canonical CLI pipeline launcher
├── README.md                   # Dedicated technical documentation
└── src/
    ├── main.py                 # Pipeline class and execution orchestrator
    ├── collection/
    │   └── collector.py        # DataCollector engine
    ├── processing/
    │   └── processor.py        # DataProcessor and Parquet exporter
    ├── analysis/
    │   └── analyzer.py         # DataAnalyzer & Visualizer
    └── data/                   # Generated pipeline artifacts
        ├── processed_tweets.parquet
        └── sentiment_distribution.png
```

---

## Execution Guide

Run the pipeline using `uv`:

```bash
# Execute canonical launcher
uv run python web_scraping/web_project1/main.py
```

### Programmatic Python Usage

```python
from web_scraping.web_project1 import Pipeline, run_default_pipeline

# Run default pipeline (200 records)
run_default_pipeline(limit=500, output_dir="outputs/sentiment")

# Custom pipeline configuration
pipeline = Pipeline(
    hashtags=["#nifty50", "#reliance", "#tcs"],
    since_date="2026-09-25",
    limit=100,
    data_dir="custom_output",
)
success = pipeline.run()
```

---

## Testing

Run unit tests covering collection, cleaning, parquet export, and sentiment classification:

```bash
uv run pytest tests/test_web_project1.py
```
