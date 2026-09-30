# YouTube Analytics & Clinical Web Scraping

A collection of web data extraction notebooks and exploratory data analysis (EDA) pipelines focusing on media analytics (YouTube view distributions) and healthcare directory scraping.

---

## Notebooks & Modules

| File | Description | Technologies |
|:---|:---|:---|
| `1_clinic_data.ipynb` | Healthcare clinic directory scraping, extracting contact info and location metadata | `requests`, `beautifulsoup4`, `pandas` |
| `2_download_image.ipynb` | Automated batch image downloading and asset pipeline | `requests`, `PIL` |
| `2_youtube_views.ipynb` | YouTube video metadata scraping, view count parsing, and cleaning | `requests`, `regex`, `pandas` |
| `4_youtube_views.ipynb` | Exploratory data analysis, view distribution modeling, and metrics calculation | `matplotlib`, `seaborn`, `pandas` |
| `validate_data.py` | Headless Python dataset validator checking schema integrity and metrics | `pandas` |
| `youtube_views.csv` | Extracted dataset of 64 YouTube videos with parsed titles, URLs, raw views, and normalized integer view counts | Tabular CSV |

---

## Dataset Schema (`youtube_views.csv`)

| Column | Type | Description | Example |
|:---|:---|:---|:---|
| `title` | `str` | Video title | `"The ACTUALLY GOOD YOUTUBERS Iceberg"` |
| `video_url` | `str` | Canonical YouTube URL | `"https://www.youtube.com/watch?v=-dcuAAMUicw"` |
| `views` | `str` | Formatted YouTube view string | `"671K views"` |
| `video_age` | `str` | Upload age string | `"1 month ago"` |
| `clean_views`| `int` | Cleaned integer view count for numerical analysis | `671000` |

---

## Validation & Headless Execution

To validate the dataset integrity headlessly:

```bash
uv run python web_scraping/web_project0/validate_data.py
```

To use programmatic loading in Python:

```python
from web_scraping.web_project0 import load_youtube_dataset

df = load_youtube_dataset()
print(f"Loaded {len(df)} videos. Max views: {df['clean_views'].max():,}")
```
