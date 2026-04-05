/**
 * Core TypeScript types for the RPA Dashboard.
 */

// ── Bot Types ───────────────────────────────────────────────────
export type BotStatus = 'idle' | 'pending' | 'running' | 'success' | 'failed' | 'cancelled' | 'retrying';

export interface Bot {
  id: string;
  client_id: string;
  name: string;
  process_name: string;
  description: string | null;
  script_path: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  current_status: BotStatus;
  last_run_at: string | null;
  total_runs: number;
  success_rate: number;
  active_run_id: string | null;
}

// ── Bot Run Types ───────────────────────────────────────────────
export interface BotRun {
  id: string;
  bot_id: string;
  client_id: string;
  celery_task_id: string | null;
  status: BotStatus;
  start_time: string | null;
  end_time: string | null;
  error_message: string | null;
  retry_count: number;
  artifacts_path: string | null;
  created_at: string;
}

export interface BotRunList {
  runs: BotRun[];
  total: number;
}

// ── Log Types ───────────────────────────────────────────────────
export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical';

export interface LogEntry {
  id: string;
  run_id: string;
  level: LogLevel;
  message: string;
  metadata_json: Record<string, unknown> | null;
  timestamp: string;
}

export interface LogList {
  logs: LogEntry[];
  total: number;
}

// ── Metrics Types ───────────────────────────────────────────────
export interface DashboardMetrics {
  total_bots: number;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  active_runs: number;
  pending_runs: number;
  success_rate: number;
  avg_duration_seconds: number;
}

// ── Auth Types ──────────────────────────────────────────────────
export interface AuthUser {
  id: string;
  username: string;
  role: 'admin' | 'viewer';
  client_id: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

// ── WebSocket Types ─────────────────────────────────────────────
export interface WSMessage {
  type: 'connected' | 'heartbeat' | 'status_update' | 'log_entry';
  bot_id?: string;
  run_id?: string;
  status?: BotStatus;
  message?: string;
  client_id?: string;
}

// ── Screenshot Types ────────────────────────────────────────────
export interface Screenshot {
  filename: string;
  url: string;
  size_bytes: number;
}
