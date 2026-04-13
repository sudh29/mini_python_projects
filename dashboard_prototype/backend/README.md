# ⚙️ Backend — FastAPI Control Plane

The control plane API server that sits between the React dashboard and the Celery workers. Handles authentication, request validation, task dispatching, real-time WebSocket updates, and metrics exposure.

> **Back to** [root README](../README.md)

---

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py             # Environment-based settings (pydantic-settings)
│   ├── database.py           # SQLAlchemy async engine + session factory
│   ├── celery_app.py         # Celery instance configuration
│   ├── seed.py               # Database seeding with demo data
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── client.py         #   └─ Client, User (multi-tenant + RBAC)
│   │   ├── bot.py            #   └─ Bot
│   │   ├── bot_run.py        #   └─ BotRun (execution history)
│   │   └── log.py            #   └─ Log (structured log entries)
│   ├── schemas/              # Pydantic v2 request/response models
│   │   ├── bot.py
│   │   ├── bot_run.py
│   │   └── log.py
│   ├── api/                  # REST API route modules
│   │   ├── bots.py           #   └─ /api/bots/* (CRUD, run, stop, status)
│   │   ├── logs.py           #   └─ /api/logs/* + internal worker endpoints
│   │   ├── screenshots.py    #   └─ /api/screenshots/*
│   │   └── metrics.py        #   └─ /api/metrics (dashboard KPIs)
│   ├── auth/                 # Authentication & authorization
│   │   └── dependencies.py   #   └─ JWT + API Key auth, role guards
│   ├── ws/                   # WebSocket handlers
│   │   └── status.py         #   └─ /ws/status (real-time bot updates)
│   └── tasks/                # Celery task definitions
│       └── bot_tasks.py      #   └─ run_bot, stop_bot tasks
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata (uv)
├── Dockerfile                # Container build
└── README.md                 # You are here
```

---

## Setup

```bash
cd backend
uv venv --python 3.14
source .venv/bin/activate.fish
uv pip install -r requirements.txt
```

### Seed Demo Data

```bash
python -m app.seed
```

This creates:
- **2 clients**: Acme Healthcare, Pinnacle Insurance
- **3 users**: admin@acme, viewer@acme, admin@pinnacle
- **7 bots**: Claims Processor, Eligibility Checker, Denial Manager, etc.
- **50+ bot runs** with mixed statuses and timestamps
- **Sample log entries** for the active run

### Run the API Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

---

## Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `clients` | Tenant registry | `id`, `name`, `api_key`, `is_active` |
| `users` | User accounts | `id`, `client_id` (FK), `username`, `role` |
| `bots` | Bot definitions | `id`, `client_id` (FK), `name`, `process_name` |
| `bot_runs` | Execution history | `id`, `bot_id` (FK), `client_id` (FK), `status`, `celery_task_id` |
| `logs` | Structured logs | `id`, `run_id` (FK), `client_id` (FK), `level`, `message` |

### Key Design Decisions

- **`client_id` on every table** — enforces tenant isolation at the query level
- **Denormalized `client_id`** on `bot_runs` and `logs` — eliminates JOINs on hot queries
- **Composite indexes** — `(client_id, status)`, `(bot_id, created_at DESC)` for common access patterns
- **`RunStatus` enum** — `pending → running → success | failed | cancelled | retrying`

---

## Auth

Two auth mechanisms supported simultaneously:

| Method | Use Case | Header |
|--------|----------|--------|
| **JWT Bearer** | Dashboard UI sessions | `Authorization: Bearer <token>` |
| **API Key** | Programmatic / dev access | `X-API-Key: <key>` |

Roles: `admin` (full access), `viewer` (read-only)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./rpa_platform.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `SECRET_KEY` | `dev-secret-key-...` | JWT signing key |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `ARTIFACT_STORAGE_PATH` | `./artifacts` | Screenshot/artifact storage path |

---

## Related

- [Frontend Documentation](../frontend/README.md) — React dashboard
- [Monitoring Documentation](../monitoring/README.md) — Prometheus + Grafana
