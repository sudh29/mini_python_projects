# 📊 Monitoring — Prometheus + Grafana

Observability layer for the RPA platform. Collects metrics from the FastAPI control plane and visualizes them in pre-built Grafana dashboards.

> **Back to** [root README](../README.md)

---

## Directory Structure

```
monitoring/
├── prometheus.yml                          # Prometheus scrape configuration
├── grafana/
│   └── dashboards/
│       └── rpa_overview.json               # Pre-built Grafana dashboard
├── pyproject.toml                          # Project metadata
└── README.md                              # You are here
```

---

## Setup

### With Docker Compose (recommended)

From the `frontend/` directory:

```bash
docker compose up prometheus grafana -d
```

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3001 | admin / admin |

### Standalone

```bash
# Prometheus
prometheus --config.file=monitoring/prometheus.yml

# Grafana (import dashboard manually)
# Import monitoring/grafana/dashboards/rpa_overview.json
```

---

## Prometheus Metrics

Metrics are exposed by the FastAPI backend at `GET /metrics`.

### Bot Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `rpa_bot_runs_total` | Counter | `client_id`, `bot_name`, `status` | Total bot executions |
| `rpa_bot_failures_total` | Counter | `client_id`, `bot_name`, `error_type` | Total failures by error type |
| `rpa_bot_duration_seconds` | Histogram | `client_id`, `bot_name` | Execution duration distribution |
| `rpa_active_runs` | Gauge | `client_id` | Currently running bots |

### API Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `rpa_api_requests_total` | Counter | `method`, `endpoint`, `status_code` | HTTP request count |
| `rpa_api_request_duration_seconds` | Histogram | `method`, `endpoint` | Request latency distribution |

### Business Metrics (planned)

| Metric | Type | Description |
|--------|------|-------------|
| `rpa_claims_processed_total` | Counter | Claims processed by bots |
| `rpa_denials_total` | Counter | Denied claims detected |
| `rpa_collections_amount` | Counter | Dollar amount collected |

---

## Grafana Dashboard

The pre-built dashboard (`rpa_overview.json`) includes:

| Panel | Type | Shows |
|-------|------|-------|
| Active Bot Runs | Gauge | Current number of running bots with threshold colors |
| Bot Runs Total | Time series | Execution rate over time by bot and status |
| Bot Execution Duration | Histogram | p95 execution time per bot |
| Failure Rate | Time series | Failure rate over time per bot |
| API Request Rate | Time series | HTTP request throughput by method and endpoint |
| API Latency (p95) | Time series | 95th percentile response time per endpoint |
| Success Rate by Bot | Stat | Per-bot success percentage with threshold colors |

### Importing the Dashboard

1. Open Grafana → Dashboards → Import
2. Upload `monitoring/grafana/dashboards/rpa_overview.json`
3. Select your Prometheus data source
4. Dashboard auto-refreshes every 10 seconds

---

## Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rpa-api'
    static_configs:
      - targets: ['api:8000']       # Docker service name
    metrics_path: '/metrics'
    scrape_interval: 10s
```

For local development (no Docker), change the target:

```yaml
    static_configs:
      - targets: ['localhost:8000']
```

---

## Alerting (planned)

Future alerting rules to be added:

| Alert | Condition | Severity |
|-------|-----------|----------|
| Bot failure spike | `rate(rpa_bot_failures_total[5m]) > 0.5` | Warning |
| Bot stuck running | `rpa_active_runs > 0` for 30m+ | Critical |
| API high latency | `p95 > 2s` for 5m | Warning |
| Worker down | Celery heartbeat missing | Critical |

---

## Related

- [Backend README](../backend/README.md) — FastAPI control plane (exposes `/metrics`)
- [Frontend README](../frontend/README.md) — React dashboard
- [Worker README](../worker/README.md) — Celery bot workers
