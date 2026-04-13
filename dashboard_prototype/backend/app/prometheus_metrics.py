from prometheus_client import Counter, Histogram, Gauge

# ── Bot Metrics ──────────────────────────────────────────────────

RPA_BOT_RUNS_TOTAL = Counter(
    "rpa_bot_runs_total",
    "Total bot executions count",
    ["client_id", "bot_id", "bot_name", "status"]
)

RPA_BOT_FAILURES_TOTAL = Counter(
    "rpa_bot_failures_total",
    "Total bot execution failures by error type",
    ["client_id", "bot_id", "bot_name", "error_type"]
)

RPA_BOT_DURATION_SECONDS = Histogram(
    "rpa_bot_duration_seconds",
    "Bot execution duration in seconds",
    ["client_id", "bot_id", "bot_name"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)

RPA_ACTIVE_RUNS = Gauge(
    "rpa_active_runs",
    "Current number of running bots",
    ["client_id", "bot_id", "bot_name"]
)

# ── API Metrics ──────────────────────────────────────────────────
# (Instrumentator handles most, but we define these for completeness/custom tracking)

RPA_API_REQUESTS_TOTAL = Counter(
    "rpa_api_requests_total",
    "Total HTTP request count for the RPA API",
    ["method", "endpoint", "status_code"]
)

RPA_API_REQUEST_DURATION_SECONDS = Histogram(
    "rpa_api_request_duration_seconds",
    "RPA API request latency distribution",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10)
)
