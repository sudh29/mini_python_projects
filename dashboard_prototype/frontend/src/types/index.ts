/**
 * Core TypeScript types for the Board Activity Monitoring Dashboard.
 */

// ── Board Types ─────────────────────────────────────────────────
export type BoardStatus = 'live' | 'success' | 'failed' | 'pending' | 'processing';

export interface Client {
  id: string;
  name: string;
  code: string; // short code e.g. "AO", "ENT", "VEN"
}

export interface Process {
  id: string;
  clientId: string;
  name: string;
  code: string;
}

export interface Board {
  id: string;
  name: string;
  clientId: string;
  clientName: string;
  processId: string;
  processName: string;
  status: BoardStatus;
  lastProcessedAt: string | null;
  processingDate: string; // The data date being processed (e.g. "2026-04-10")
  startedAt: string | null;
  completedAt: string | null;
  duration: number | null; // seconds
  failureReason: string | null;
  failureDate: string | null; // specific date that caused the failure
  recordsProcessed: number;
  recordsTotal: number;
}

export interface BoardMetrics {
  totalBoards: number;
  liveBoards: number;
  successBoards: number;
  failedBoards: number;
  pendingBoards: number;
  processingBoards: number;
  successRate: number;
  avgDuration: number; // seconds
}

export interface BoardFilter {
  clientId: string | null;
  processId: string | null;
  status: BoardStatus | null;
  dateRange: 'today' | '7d' | '30d' | '90d' | 'custom';
  startDate: string | null; // YYYY-MM-DD
  endDate: string | null;   // YYYY-MM-DD
}

// ── Historical / Trend Types ────────────────────────────────────
export interface HistoricalDataPoint {
  date: string;
  totalBoards: number;
  success: number;
  failed: number;
  successRate: number;
  avgDuration: number;
}

export interface ClientTrendPoint {
  date: string;
  client: string;
  volume: number;
  successRate: number;
}

// ── Report Types ────────────────────────────────────────────────
export interface ReportRow {
  boardName: string;
  client: string;
  process: string;
  status: string;
  processingDate: string;
  startedAt: string;
  completedAt: string;
  duration: string;
  recordsProcessed: number;
  recordsTotal: number;
  failureReason: string;
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
  status?: string;
  message?: string;
  client_id?: string;
}

// ── Legacy types kept for compatibility ─────────────────────────
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

export interface Screenshot {
  filename: string;
  url: string;
  size_bytes: number;
}
