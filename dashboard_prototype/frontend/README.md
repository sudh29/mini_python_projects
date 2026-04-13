# 🖥️ Frontend — React Dashboard

The web-based monitoring dashboard for the RPA platform. Provides real-time visibility into bot status, execution history, logs, screenshots, and system metrics.

> **Back to** [root README](../README.md)

---

## Directory Structure

```
frontend/
├── src/
│   ├── main.tsx               # React entry point
│   ├── App.tsx                # Router + layout shell
│   ├── App.css                # Layout styles
│   ├── index.css              # Design system (tokens, reset, theme)
│   ├── types/                 # TypeScript type definitions
│   │   └── index.ts           #   └─ Bot, BotRun, LogEntry, Metrics, etc.
│   ├── services/              # API client layer
│   │   └── api.ts             #   └─ Fetch wrapper, auth, all API calls
│   ├── hooks/                 # Custom React hooks
│   │   ├── useApi.ts          #   └─ Generic data-fetching with loading/error
│   │   └── useWebSocket.ts    #   └─ WebSocket with auto-reconnect
│   ├── components/            # Reusable UI components
│   │   ├── Sidebar.tsx/css    #   └─ Collapsible nav sidebar
│   │   ├── Header.tsx/css     #   └─ Top bar with search & connection status
│   │   ├── BotCard.tsx/css    #   └─ Bot status tile with quick actions
│   │   ├── BotStatusBadge.*   #   └─ Color-coded status pill
│   │   ├── LogViewer.tsx/css  #   └─ Filterable log output
│   │   ├── MetricsPanel.*     #   └─ KPI summary cards
│   │   └── ScreenshotViewer.* #   └─ Screenshot gallery + lightbox
│   └── pages/                 # Page-level components
│       ├── Dashboard.tsx/css  #   └─ Bot grid + metrics overview
│       ├── BotDetail.tsx/css  #   └─ Bot info, runs, logs, screenshots
│       └── Login.tsx/css      #   └─ Authentication form
├── public/                    # Static assets
├── index.html                 # HTML template
├── docker-compose.yml         # Full-stack Docker orchestration
├── package.json               # Node.js dependencies
├── vite.config.ts             # Vite build configuration
├── tsconfig*.json             # TypeScript configuration
└── README.md                  # You are here
```

---

## Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at: **http://localhost:5173**

### Build for Production

```bash
npm run build
npm run preview
```

---

## Design System

### Theme

The dashboard uses a **dark theme by default** with a cohesive design system defined in `src/index.css`:

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#0c0d11` | Page background |
| `--card-bg` | `#14151b` | Card/panel backgrounds |
| `--accent` | `#3b82f6` | Primary blue accent |
| `--accent-gradient` | `blue → purple` | Buttons, highlights |
| `--success` | `#22c55e` | Success states |
| `--danger` | `#ef4444` | Error/failure states |
| `--warning` | `#f59e0b` | Warning states |
| `--info` | `#06b6d4` | Running/active states |

### Typography

- **UI font**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono / system mono

### Key UI Patterns

- **Glassmorphic header** with `backdrop-filter: blur()`
- **Pulsing status dot** on running bots
- **Skeleton loading** for metrics cards
- **Lightbox** for screenshot gallery
- **Auto-scroll** on live log viewer

---

## Pages

### Dashboard (`/`)
Grid of bot cards with status badges, quick run/stop actions, and summary metrics (total bots, active runs, success rate, failed runs).

### Bot Detail (`/bots/:id`)
Two-column layout with:
- **Left**: Run history list (clickable to view logs)
- **Right**: Live log viewer with level filtering
- **Bottom**: Screenshot gallery with lightbox navigation
- **Top**: Bot info cards (process name, total runs, success rate, last run)

### Login (`/login`)
Simple auth form with demo credential hints. Stores JWT token in localStorage.

---

## API Integration

The `services/api.ts` module handles all communication with the backend:

- **Auth**: JWT Bearer token or fallback API key
- **Base URL**: `VITE_API_BASE` env var (default: `http://localhost:8000`)
- **Error handling**: Typed errors thrown from the fetch wrapper
- **WebSocket**: Auto-reconnecting connection at `/ws/status` for live updates

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000` | Backend API base URL |

---

## Docker Compose

The `docker-compose.yml` in this directory orchestrates the full stack:

```bash
docker compose up -d
```

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL 16 |
| `redis` | 6379 | Redis 7 (broker + cache) |
| `api` | 8000 | FastAPI control plane |
| `worker` | — | Celery bot worker |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Dashboards |

---

## Related

- [Backend Documentation](../backend/README.md) — FastAPI control plane
- [Monitoring Documentation](../monitoring/README.md) — Prometheus + Grafana
