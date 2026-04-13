# Architecture Diagram

This document reflects the current runtime architecture in the repository as of April 12, 2026.

## System Architecture

```mermaid
flowchart LR
    user[Operations User]

    subgraph browser[Browser]
        frontend[React Dashboard<br/>Vite + TypeScript]
    end

    subgraph control[Control Plane]
        api[FastAPI API<br/>REST + Auth + WebSocket + Metrics]
        ws[Connection Manager<br/>/ws/status]
        internal[Internal Worker Endpoints<br/>/api/internal/runs/*]
    end

    subgraph data[State and Messaging]
        db[(PostgreSQL<br/>or SQLite in local dev)]
        redis[(Redis<br/>broker + result backend)]
        artifacts[(Artifact Storage<br/>artifacts/&lt;client&gt;/&lt;run&gt;)]
    end

    subgraph execution[Execution Layer]
        worker[Celery Worker<br/>app.tasks.bot_tasks]
    end

    subgraph observability[Observability]
        prom[Prometheus]
        graf[Grafana]
    end

    user --> frontend
    frontend -->|REST /api/*| api
    frontend <-->|WebSocket /ws/status| ws

    api --> db
    api -->|enqueue bot tasks| redis
    worker -->|consume bot queue| redis
    worker -->|status + logs| internal
    internal --> db
    internal --> ws
    worker -. screenshots/artifacts .-> artifacts
    api <-->|serve screenshot metadata/files| artifacts

    prom -->|scrape /metrics| api
    graf -->|query metrics| prom
    frontend -. operator opens dashboards .-> graf
```

## Key Boundaries

- The frontend only talks to the backend API and WebSocket endpoint.
- Bot execution is asynchronous and runs in Celery workers, not inside FastAPI request handlers.
- Workers report status and logs back through internal API endpoints secured with an internal API key.
- Persistent state lives in the database; Redis is used for queueing and task coordination.
- Prometheus scrapes the FastAPI app, and Grafana reads from Prometheus rather than from the application database.

## Run Lifecycle

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Dashboard
    participant A as FastAPI
    participant D as Database
    participant R as Redis/Celery
    participant W as Worker
    participant P as Prometheus
    participant G as Grafana

    U->>F: Click "Run Bot"
    F->>A: POST /api/bots/run
    A->>D: Create BotRun(status=pending)
    A->>R: Enqueue Celery task
    R->>W: Deliver task
    W->>A: PUT /api/internal/runs/{id}/status
    W->>A: POST /api/internal/runs/{id}/logs
    A->>D: Persist status + logs
    A-->>F: WebSocket status_update
    P->>A: Scrape /metrics
    G->>P: Query dashboards
```
