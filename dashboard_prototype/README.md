# 🤖 Jorie AI — RPA Orchestration & Monitoring

A production-grade platform for orchestrating and monitoring Python-based automation bots (Selenium / PyAutoGUI) across virtual machines. Supports multi-tenant deployments with real-time dashboards, centralized logging, and observability.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Dashboard                          │
│                     (frontend/ — Vite + TS)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                    FastAPI Control Plane                         │
│                   (backend/ — Python 3.14)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ REST API │  │WebSocket │  │   Auth   │  │  Prometheus    │  │
│  │ /api/*   │  │ /ws/*    │  │  (JWT)   │  │  /metrics      │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
└────────┬───────────────────────────┬────────────────────────────┘
         │                           │
    ┌────▼────┐                 ┌────▼────┐
    │ PostgreSQL│               │  Redis  │
    │ (Database)│               │ (Broker)│
    └─────────┘                 └────┬────┘
                                     │ Celery
                            ┌────────▼────────┐
                            │  Bot Workers     │
                            │ (worker/ — VMs)  │
                            │                  │
                            │ Selenium/PyAutoGUI│
                            └──────────────────┘
                                     │
                            ┌────────▼────────┐
                            │  Observability   │
                            │ (monitoring/)    │
                            │ Prometheus       │
                            │ + Grafana        │
                            └──────────────────┘
```

---

## Project Structure

```
dashboard_prototype/
├── backend/           → FastAPI control plane + Celery tasks
├── frontend/          → React dashboard (Vite + TypeScript)
├── worker/            → Celery workers & bot scripts
├── monitoring/        → Prometheus + Grafana configs
├── .gitignore
└── README.md          → You are here
```

| Directory | Description | README |
|-----------|-------------|--------|
| [`backend/`](./backend/) | FastAPI API server, database models, auth, Celery integration | [backend/README.md](./backend/README.md) |
| [`frontend/`](./frontend/) | React + Vite + TypeScript dashboard with real-time updates | [frontend/README.md](./frontend/README.md) |
| [`worker/`](./worker/) | Celery worker processes, bot scripts, and execution utilities | [worker/README.md](./worker/README.md) |
| [`monitoring/`](./monitoring/) | Prometheus scrape config and Grafana dashboard definitions | [monitoring/README.md](./monitoring/README.md) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, TypeScript, Lucide Icons |
| Backend | FastAPI, SQLAlchemy (async), Pydantic v2 |
| Task Queue | Celery + Redis |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Bots | Python — Selenium, PyAutoGUI |
| Monitoring | Prometheus + Grafana |
| Auth | JWT (Bearer) + API Key |
| Package Manager | uv (Python), npm (Node.js) |
| Deployment | VMs (current) → Docker + Kubernetes (planned) |

---

## Quick Start

### Prerequisites

- Python 3.14+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Redis (for Celery broker)
- PostgreSQL (or SQLite for dev)

### 1. Backend

```bash
cd backend
uv venv --python 3.14
source .venv/bin/activate      # or .venv/bin/activate.fish
uv pip install -r requirements.txt
python -m app.seed             # Seed demo data
uvicorn app.main:app --reload  # http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

### 3. Worker (requires Redis)

```bash
cd worker
uv venv --python 3.14
source .venv/bin/activate
uv pip install -r requirements.txt
celery -A celery_worker.celery_app worker --loglevel=info --queues=bots
```

### 4. Monitoring (Docker)

```bash
cd frontend
docker compose up prometheus grafana -d
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3001 (admin/admin)
```

---

## Data Flow

```
User clicks "Run Bot" (React)
  → FastAPI validates request + checks auth
  → BotRun record created in PostgreSQL (status: pending)
  → Task enqueued in Celery via Redis
  → Worker VM picks up task
  → Bot executes (Selenium/PyAutoGUI)
  → Logs + screenshots pushed to control plane
  → Status updated in PostgreSQL + Redis
  → WebSocket pushes real-time update to UI
  → Prometheus scrapes /metrics
  → Grafana visualizes trends
```

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/auth/login` | Public | Authenticate and receive JWT |
| `GET` | `/api/bots/status` | Bearer/Key | List all bots with status |
| `POST` | `/api/bots/run` | Admin | Trigger bot execution |
| `POST` | `/api/bots/stop` | Admin | Cancel running bot |
| `GET` | `/api/bots/{id}/runs` | Bearer/Key | Bot run history |
| `GET` | `/api/logs/{run_id}` | Bearer/Key | Fetch run logs |
| `GET` | `/api/screenshots/{run_id}` | Bearer/Key | List run screenshots |
| `GET` | `/api/metrics` | Bearer/Key | Dashboard metrics summary |
| `GET` | `/api/health` | Public | Health check |
| `WS` | `/ws/status` | Token | Real-time status updates |

---

## Hard Design Rules

1. **Bots NEVER communicate directly with the UI** — all traffic goes through the API
2. **Task execution ALWAYS goes through Celery** — no direct bot invocation from API
3. **ALL artifacts (logs, screenshots, status) are stored centrally**, not on worker VMs
4. **Strict separation**: Control (FastAPI) → Execution (Workers) → Monitoring (Grafana)
5. **Every DB table and API endpoint includes `client_id`** for tenant isolation

---

## Demo Credentials

| Username | Password | Role | Client |
|----------|----------|------|--------|
| `admin@acme` | `admin123` | Admin | Acme Healthcare |
| `viewer@acme` | `viewer123` | Viewer | Acme Healthcare |
| `admin@pinnacle` | `admin123` | Admin | Pinnacle Insurance |

API Key: `acme-api-key-dev-001` (Acme Healthcare)

---

## License

Private — Internal use only.
