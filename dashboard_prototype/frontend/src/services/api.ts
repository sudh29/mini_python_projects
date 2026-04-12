/**
 * API service — centralized HTTP client for the FastAPI backend.
 *
 * Falls back to bundled dummy data when the backend is unreachable,
 * so the dashboard is always demo-able.
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

import {
  getDummyBots,
  getDummyBot,
  getDummyBotRuns,
  getDummyLogs,
  getDummyScreenshots,
  getDummyMetrics,
} from './dummyData';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// ── Demo Mode Detection ─────────────────────────────────────────
// Tracks whether the backend is available. After the first failure
// we stop hitting the network for the rest of the session.
let _useDummyData: boolean | null = null;   // null = not yet tested

async function isDemoMode(): Promise<boolean> {
  if (_useDummyData !== null) return _useDummyData;
  try {
    const res = await fetch(`${API_BASE}/api/health`, {
      signal: AbortSignal.timeout(2000),
    });
    _useDummyData = !res.ok;
  } catch {
    _useDummyData = true;
  }
  if (_useDummyData) {
    console.info(
      '%c⚡ Demo Mode — using built-in sample data (backend unreachable)',
      'color:#3b82f6;font-weight:bold',
    );
  }
  return _useDummyData;
}

/** Force demo mode on/off (useful for dev toggling). */
export function setDemoMode(enabled: boolean) {
  _useDummyData = enabled;
}

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
  // Demo mode: accept known dev credentials
  if (await isDemoMode()) {
    if (
      (username === 'admin' && password === 'admin') ||
      (username === 'viewer' && password === 'viewer')
    ) {
      const demoUser = {
        id: 'demo-user-001',
        username,
        role: username.startsWith('admin') ? ('admin' as const) : ('viewer' as const),
        client_id: 'c1000000-0000-0000-0000-000000000001',
      };
      const resp: LoginResponse = {
        access_token: 'demo-token',
        token_type: 'bearer',
        user: demoUser,
      };
      setAuthToken(resp.access_token);
      localStorage.setItem('rpa_user', JSON.stringify(demoUser));
      return resp;
    }
    throw new Error('Invalid credentials');
  }

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
  if (await isDemoMode()) return getDummyBots();
  return apiFetch<Bot[]>('/api/bots/status');
}

export async function fetchBot(botId: string): Promise<Bot> {
  if (await isDemoMode()) {
    const bot = getDummyBot(botId);
    if (!bot) throw new Error('Bot not found');
    return bot;
  }
  // Use the status endpoint and filter
  const bots = await fetchBots();
  const bot = bots.find(b => b.id === botId);
  if (!bot) throw new Error('Bot not found');
  return bot;
}

export async function runBot(botId: string, parameters?: Record<string, unknown>): Promise<BotRun> {
  if (await isDemoMode()) {
    // Simulate a run start in demo mode
    const now = new Date().toISOString();
    return {
      id: `demo-run-${Date.now()}`,
      bot_id: botId,
      client_id: 'c1000000-0000-0000-0000-000000000001',
      celery_task_id: `demo-task-${Date.now()}`,
      status: 'pending',
      start_time: now,
      end_time: null,
      error_message: null,
      retry_count: 0,
      artifacts_path: null,
      created_at: now,
    };
  }
  return apiFetch<BotRun>('/api/bots/run', {
    method: 'POST',
    body: JSON.stringify({ bot_id: botId, parameters }),
  });
}

export async function stopBot(botId: string, runId?: string): Promise<{ status: string; run_id: string }> {
  if (await isDemoMode()) {
    return { status: 'cancelled', run_id: runId || `demo-run-${Date.now()}` };
  }
  return apiFetch('/api/bots/stop', {
    method: 'POST',
    body: JSON.stringify({ bot_id: botId, run_id: runId }),
  });
}

// ── Bot Runs ─────────────────────────────────────────────────────
export async function fetchBotRuns(botId: string, limit = 20, offset = 0): Promise<BotRunList> {
  if (await isDemoMode()) return getDummyBotRuns(botId, limit, offset);
  return apiFetch<BotRunList>(`/api/bots/${botId}/runs?limit=${limit}&offset=${offset}`);
}

// ── Logs ─────────────────────────────────────────────────────────
export async function fetchLogs(runId: string, level?: string): Promise<LogList> {
  if (await isDemoMode()) {
    const data = getDummyLogs(runId);
    if (level) {
      const filtered = data.logs.filter(l => l.level === level);
      return { logs: filtered, total: filtered.length };
    }
    return data;
  }
  const params = new URLSearchParams();
  if (level) params.set('level', level);
  const qs = params.toString();
  return apiFetch<LogList>(`/api/logs/${runId}${qs ? `?${qs}` : ''}`);
}

// ── Screenshots ──────────────────────────────────────────────────
export async function fetchScreenshots(runId: string): Promise<{ screenshots: Screenshot[]; run_id: string }> {
  if (await isDemoMode()) return getDummyScreenshots(runId);
  return apiFetch(`/api/screenshots/${runId}`);
}

// ── Metrics ──────────────────────────────────────────────────────
export async function fetchMetrics(): Promise<DashboardMetrics> {
  if (await isDemoMode()) return getDummyMetrics();
  return apiFetch<DashboardMetrics>('/api/metrics');
}

// ── Health ───────────────────────────────────────────────────────
export async function checkHealth(): Promise<{ status: string; version: string }> {
  if (await isDemoMode()) return { status: 'demo', version: '0.1.0-demo' };
  return apiFetch('/api/health');
}
