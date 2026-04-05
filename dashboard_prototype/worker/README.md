# 🔧 Worker — Celery Bot Workers

Celery workers that execute Python automation bots on virtual machines. Each worker listens for tasks dispatched by the FastAPI control plane, manages the full bot lifecycle, and reports status back centrally.

> **Back to** [root README](../README.md)

---

## Directory Structure

```
worker/
├── celery_worker.py           # Worker entry point
├── bots/                      # Bot scripts (per client)
│   └── sample_bot.py          #   └─ Demo bot simulating RPA workflow
├── utils/                     # Shared worker utilities
│   ├── screenshot.py          #   └─ Screenshot capture (Selenium/PyAutoGUI)
│   ├── logger.py              #   └─ Structured JSON logger
│   └── status_reporter.py     #   └─ Status updates to control plane
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata (uv)
└── README.md                  # You are here
```

---

## Setup

```bash
cd worker
uv venv --python 3.14
source .venv/bin/activate.fish
uv pip install -r requirements.txt
```

### Start Worker

Requires Redis running at `localhost:6379`:

```bash
celery -A celery_worker.celery_app worker \
  --loglevel=info \
  --queues=bots \
  --concurrency=2 \
  --hostname=worker@%h
```

Or use the Python entry point:

```bash
python celery_worker.py
```

---

## Bot Lifecycle

```
PENDING → RUNNING → SUCCESS
                  → FAILED → RETRY (up to 3x with exponential backoff)
                  → CANCELLED
```

### On each state transition:
1. **PostgreSQL** — `bot_runs` table updated via internal API
2. **Redis** — Real-time status cached at `bot:{id}`
3. **WebSocket** — Status push published to connected dashboard clients

---

## Bot Contract

Every bot script must follow this contract:

```python
class MyBot:
    def __init__(self, run_id: str, client_id: str, artifacts_dir: Path):
        self.run_id = run_id
        self.client_id = client_id
        self.artifacts_dir = artifacts_dir

    def execute(self, parameters: dict | None = None) -> dict:
        """
        Run the automation workflow.
        
        Must:
          - Emit structured logs (via utils/logger.py)
          - Capture screenshots on failure (via utils/screenshot.py)
          - Return a summary dict with at least {"status": "success"|"failed"}
        
        Raises:
          - Any exception triggers auto-retry via Celery
        """
        ...
```

### Sample Bot

The `bots/sample_bot.py` demonstrates the contract with a simulated RPA workflow: login → navigate → process items → capture screenshots → cleanup.

---

## Utilities

### `utils/screenshot.py` — ScreenshotCapture

Supports multiple capture methods with graceful fallbacks:

| Method | When to Use |
|--------|-------------|
| `capture_selenium(driver, name)` | Bot uses Selenium WebDriver |
| `capture_pyautogui(name, region)` | Full-screen or region capture |
| `capture_on_error(driver, name)` | Error handler — tries all methods |

### `utils/logger.py` — BotLogger

Structured JSON logger that outputs to:
1. **Local JSONL file** — per run, for local debugging
2. **stdout** — standard Python logging
3. **Control plane API** — `POST /api/internal/runs/{run_id}/logs`

```python
logger = BotLogger(run_id="...", client_id="...", bot_name="claims")
logger.info("Processing claim #1234")
logger.warning("Slow response detected")
logger.error("Element not found", selector="#submit-btn")
logger.flush_to_api()  # Bulk-post to control plane
```

### `utils/status_reporter.py` — StatusReporter

Fire-and-forget status updates to the control plane:

```python
reporter = StatusReporter()
reporter.running(run_id)
reporter.success(run_id)
reporter.failed(run_id, error="Timeout after 30s")
reporter.cancelled(run_id)
```

---

## Task Configuration

Celery tasks are configured with production-grade defaults:

| Setting | Value | Why |
|---------|-------|-----|
| `autoretry_for` | `(Exception,)` | Auto-retry on any error |
| `retry_backoff` | `True` | Exponential backoff between retries |
| `retry_backoff_max` | `300s` (5 min) | Cap on backoff interval |
| `max_retries` | `3` | Max retry attempts |
| `acks_late` | `True` | Acknowledge after execution (crash safety) |
| `worker_prefetch_multiplier` | `1` | One task at a time per process |

---

## Adding a New Bot

1. Create `bots/<client>/<bot_name>.py` with a class following the bot contract
2. Register the bot in the `bots` database table via the seed script or API
3. The Celery task resolver will load and execute it on dispatch

---

## Related

- [Backend README](../backend/README.md) — FastAPI control plane
- [Frontend README](../frontend/README.md) — React dashboard
- [Monitoring README](../monitoring/README.md) — Prometheus + Grafana
