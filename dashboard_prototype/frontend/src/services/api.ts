/**
 * API service — centralized HTTP client for the FastAPI backend.
 */

import type {
  Bot,
  BotRun,
  BotRunList,
  DashboardMetrics,
  LogList,
  LoginResponse,
  Screenshot,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// ── Auth Token Storage ──────────────────────────────────────────
let authToken: string | null = localStorage.getItem('rpa_token');

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem('rpa_token', token);
  } else {
    localStorage.removeItem('rpa_token');
  }
}

export function getAuthToken(): string | null {
  return authToken;
}

// ── Fetch Wrapper ───────────────────────────────────────────────
async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  // Fallback: use demo API key if no JWT
  if (!authToken) {
    headers['X-API-Key'] = 'acme-api-key-dev-001';
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// ── Auth ─────────────────────────────────────────────────────────
export async function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  const data: LoginResponse = await response.json();
  setAuthToken(data.access_token);
  return data;
}

export function logout() {
  setAuthToken(null);
  localStorage.removeItem('rpa_user');
}

// ── Bots ─────────────────────────────────────────────────────────
export async function fetchBots(): Promise<Bot[]> {
  return apiFetch<Bot[]>('/api/bots/status');
}

export async function fetchBot(botId: string): Promise<Bot> {
  // Use the status endpoint and filter
  const bots = await fetchBots();
  const bot = bots.find(b => b.id === botId);
  if (!bot) throw new Error('Bot not found');
  return bot;
}

export async function runBot(botId: string, parameters?: Record<string, unknown>): Promise<BotRun> {
  return apiFetch<BotRun>('/api/bots/run', {
    method: 'POST',
    body: JSON.stringify({ bot_id: botId, parameters }),
  });
}

export async function stopBot(botId: string, runId?: string): Promise<{ status: string; run_id: string }> {
  return apiFetch('/api/bots/stop', {
    method: 'POST',
    body: JSON.stringify({ bot_id: botId, run_id: runId }),
  });
}

// ── Bot Runs ─────────────────────────────────────────────────────
export async function fetchBotRuns(botId: string, limit = 20, offset = 0): Promise<BotRunList> {
  return apiFetch<BotRunList>(`/api/bots/${botId}/runs?limit=${limit}&offset=${offset}`);
}

// ── Logs ─────────────────────────────────────────────────────────
export async function fetchLogs(runId: string, level?: string): Promise<LogList> {
  const params = new URLSearchParams();
  if (level) params.set('level', level);
  const qs = params.toString();
  return apiFetch<LogList>(`/api/logs/${runId}${qs ? `?${qs}` : ''}`);
}

// ── Screenshots ──────────────────────────────────────────────────
export async function fetchScreenshots(runId: string): Promise<{ screenshots: Screenshot[]; run_id: string }> {
  return apiFetch(`/api/screenshots/${runId}`);
}

// ── Metrics ──────────────────────────────────────────────────────
export async function fetchMetrics(): Promise<DashboardMetrics> {
  return apiFetch<DashboardMetrics>('/api/metrics');
}

// ── Health ───────────────────────────────────────────────────────
export async function checkHealth(): Promise<{ status: string; version: string }> {
  return apiFetch('/api/health');
}
