"""
Custom Prometheus metrics for the application.
"""
from prometheus_client import Counter, Gauge

# Count of total bot executions triggered
BOT_RUNS_TOTAL = Counter(
    "bot_runs_total",
    "Total number of bot executions triggered",
    ["client_id", "bot_id"]
)

# Current active runs
BOT_RUNS_ACTIVE = Gauge(
    "bot_runs_active",
    "Number of currently active/running bot processes",
    ["client_id", "bot_id"]
)

# Completed runs with status
BOT_RUNS_COMPLETED = Counter(
    "bot_runs_completed_total",
    "Total number of completed bot executions by status",
    ["client_id", "bot_id", "status"]
)
