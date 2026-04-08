/**
 * Dummy / historical data for the RPA Dashboard.
 *
 * When the backend is unreachable, the frontend falls back to this data
 * so the UI is always demo-able with realistic content.
 */

import type {
  Bot,
  BotRun,
  BotRunList,
  DashboardMetrics,
  LogEntry,
  LogList,
  Screenshot,
} from '../types';

// ── Stable IDs ──────────────────────────────────────────────────
const CLIENT_ID = 'c1000000-0000-0000-0000-000000000001';

const BOT_IDS = {
  claimsProcessor: 'b1000000-0000-0000-0000-000000000001',
  eligibilityChecker: 'b1000000-0000-0000-0000-000000000002',
  denialManager: 'b1000000-0000-0000-0000-000000000003',
  paymentPoster: 'b1000000-0000-0000-0000-000000000004',
};

// ── Helpers ─────────────────────────────────────────────────────
function daysAgo(days: number, hoursOffset = 0): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  d.setHours(d.getHours() - hoursOffset);
  return d.toISOString();
}

function minutesAgo(mins: number): string {
  return new Date(Date.now() - mins * 60_000).toISOString();
}

function uid(seed: number): string {
  const hex = seed.toString(16).padStart(12, '0');
  return `r0000000-${hex.slice(0, 4)}-${hex.slice(4, 8)}-0000-${hex}`;
}

// ── Bots ────────────────────────────────────────────────────────
export const DUMMY_BOTS: Bot[] = [
  {
    id: BOT_IDS.claimsProcessor,
    client_id: CLIENT_ID,
    name: 'Claims Processor',
    process_name: 'claims_processing',
    description:
      'Processes incoming insurance claims via the portal, validates data, and submits to adjudication queue.',
    script_path: 'bots/acme/claims_processor.py',
    is_active: true,
    created_at: daysAgo(45),
    updated_at: daysAgo(0, 3),
    current_status: 'running',
    last_run_at: minutesAgo(3),
    total_runs: 342,
    success_rate: 94.7,
    active_run_id: uid(9000),
  },
  {
    id: BOT_IDS.eligibilityChecker,
    client_id: CLIENT_ID,
    name: 'Eligibility Checker',
    process_name: 'eligibility_verification',
    description:
      'Verifies patient eligibility against payer databases using the clearinghouse portal.',
    script_path: 'bots/acme/eligibility_checker.py',
    is_active: true,
    created_at: daysAgo(38),
    updated_at: daysAgo(0, 6),
    current_status: 'success',
    last_run_at: minutesAgo(47),
    total_runs: 219,
    success_rate: 97.3,
    active_run_id: null,
  },
  {
    id: BOT_IDS.denialManager,
    client_id: CLIENT_ID,
    name: 'Denial Manager',
    process_name: 'denial_management',
    description:
      'Monitors denied claims, categorizes denial reasons, and initiates appeal workflows.',
    script_path: 'bots/acme/denial_manager.py',
    is_active: true,
    created_at: daysAgo(30),
    updated_at: daysAgo(1),
    current_status: 'failed',
    last_run_at: daysAgo(0, 2),
    total_runs: 156,
    success_rate: 88.5,
    active_run_id: null,
  },
  {
    id: BOT_IDS.paymentPoster,
    client_id: CLIENT_ID,
    name: 'Payment Poster',
    process_name: 'payment_posting',
    description:
      'Posts ERA/EOB payments to patient accounts in the billing system.',
    script_path: 'bots/acme/payment_poster.py',
    is_active: true,
    created_at: daysAgo(25),
    updated_at: daysAgo(0, 12),
    current_status: 'idle',
    last_run_at: daysAgo(1, 8),
    total_runs: 87,
    success_rate: 96.6,
    active_run_id: null,
  },
];

// ── Bot Runs (historical for each bot) ──────────────────────────
function generateRuns(botId: string, count: number, startSeed: number): BotRun[] {
  const statuses: Array<BotRun['status']> = [
    'success', 'success', 'success', 'success', 'success',
    'success', 'failed', 'success', 'success', 'cancelled',
    'success', 'success', 'success', 'failed', 'success',
    'success', 'success', 'success', 'success', 'success',
  ];
  const errors = [
    'TimeoutError: Element not found after 30s wait',
    'ConnectionError: Portal returned 503 Service Unavailable',
    'ValidationError: Missing required field — diagnosis_code',
    'SessionExpired: Login session timed out after 15 min inactivity',
  ];

  const runs: BotRun[] = [];
  for (let i = 0; i < count; i++) {
    const s = statuses[i % statuses.length];
    const start = daysAgo(Math.floor(i * 0.4), i * 3);
    const durationMs = (120 + (i % 5) * 180 + (i * 11) % 60) * 1000;
    const end =
      s === 'cancelled'
        ? new Date(new Date(start).getTime() + 15_000).toISOString()
        : new Date(new Date(start).getTime() + durationMs).toISOString();

    runs.push({
      id: uid(startSeed + i),
      bot_id: botId,
      client_id: CLIENT_ID,
      celery_task_id: uid(startSeed + i + 5000),
      status: s,
      start_time: start,
      end_time: s === 'running' ? null : end,
      error_message: s === 'failed' ? errors[i % errors.length] : null,
      retry_count: s === 'failed' ? 1 : 0,
      artifacts_path: `artifacts/${CLIENT_ID}/${botId}/${i}`,
      created_at: start,
    });
  }

  // If this bot is "running", make the first entry the running one
  const bot = DUMMY_BOTS.find(b => b.id === botId);
  if (bot?.current_status === 'running') {
    runs[0] = {
      ...runs[0],
      id: bot.active_run_id || uid(9000),
      status: 'running',
      start_time: minutesAgo(3),
      end_time: null,
      error_message: null,
      retry_count: 0,
      created_at: minutesAgo(3),
    };
  }

  return runs;
}

const ALL_RUNS: Record<string, BotRun[]> = {
  [BOT_IDS.claimsProcessor]: generateRuns(BOT_IDS.claimsProcessor, 18, 100),
  [BOT_IDS.eligibilityChecker]: generateRuns(BOT_IDS.eligibilityChecker, 14, 200),
  [BOT_IDS.denialManager]: generateRuns(BOT_IDS.denialManager, 12, 300),
  [BOT_IDS.paymentPoster]: generateRuns(BOT_IDS.paymentPoster, 8, 400),
};

// ── Logs (for the currently-running bot + recent completed runs) ─
function generateLogs(runId: string, botName: string, status: string): LogEntry[] {
  const claimsLogs: Array<[LogEntry['level'], string]> = [
    ['info', 'Bot started — initializing browser session'],
    ['info', 'Navigating to claims portal: https://portal.acme-health.example.com'],
    ['info', 'Login successful — session established'],
    ['info', 'Navigating to claims queue — 47 pending claims found'],
    ['info', 'Processing claim #CLM-2024-00893 — patient: John D.'],
    ['debug', 'Filling form field: diagnosis_code = E11.65'],
    ['info', 'Claim #CLM-2024-00893 submitted successfully'],
    ['warning', 'Slow page load detected — portal response > 5s'],
    ['info', 'Processing claim #CLM-2024-00894 — patient: Sarah M.'],
    ['info', 'Screenshot captured: claim_894_submission.png'],
    ['info', 'Claim #CLM-2024-00894 submitted successfully'],
    ['info', 'Processing claim #CLM-2024-00895 — patient: Robert K.'],
    ['debug', 'Performing OCR on scanned document: denial_letter_895.pdf'],
    ['info', 'Claim #CLM-2024-00895 submitted successfully'],
    ['info', 'Processing claim #CLM-2024-00896 — patient: Emily W.'],
    ['warning', 'Duplicate claim detected — CLM-2024-00896 matches #CLM-2024-00847'],
    ['info', 'Skipped duplicate claim, logging to audit trail'],
    ['info', 'Processing claim #CLM-2024-00897 — patient: Michael T.'],
    ['info', 'Claim #CLM-2024-00897 submitted successfully'],
    ['info', 'Batch complete — 4 of 47 claims processed, 1 duplicate skipped'],
  ];

  const eligibilityLogs: Array<[LogEntry['level'], string]> = [
    ['info', 'Bot started — initializing headless browser'],
    ['info', 'Loading clearinghouse portal: https://ch.acme-health.example.com'],
    ['info', 'Login successful — 2FA verification bypassed (saved session)'],
    ['info', 'Fetching patient roster — 23 pending verifications'],
    ['info', 'Verifying eligibility: Patient #PT-10234 — Aetna PPO'],
    ['info', 'Eligibility confirmed — coverage active through 2026-12-31'],
    ['info', 'Verifying eligibility: Patient #PT-10235 — UHC HMO'],
    ['warning', 'Eligibility expired — coverage ended 2026-03-15, flagging for review'],
    ['info', 'Verifying eligibility: Patient #PT-10236 — BCBS PPO'],
    ['info', 'Eligibility confirmed — coverage active, copay $25'],
    ['debug', 'Cache hit: payer Aetna config loaded from local store'],
    ['info', 'Batch complete — 3 verified, 1 flagged for manual review'],
  ];

  const denialLogs: Array<[LogEntry['level'], string]> = [
    ['info', 'Bot started — connecting to denial management queue'],
    ['info', 'Loaded 12 new denials since last run'],
    ['info', 'Categorizing denial #DEN-4501 — reason: Missing prior auth'],
    ['info', 'Auto-generating appeal letter for DEN-4501'],
    ['warning', 'Denial #DEN-4502 — unrecognized denial code: XR99'],
    ['error', 'Failed to process DEN-4503 — payer portal returned 500 Internal Server Error'],
    ['info', 'Retrying DEN-4503 in 30 seconds...'],
    ['info', 'DEN-4503 retry successful — categorized as: Timely filing'],
    ['info', 'Categorizing denial #DEN-4504 — reason: Non-covered service'],
    ['info', 'Batch complete — 4 denials processed, 1 required retry'],
  ];

  const paymentLogs: Array<[LogEntry['level'], string]> = [
    ['info', 'Bot started — checking for new ERA files'],
    ['info', 'Found 3 new ERA files from Aetna, BCBS, UHC'],
    ['info', 'Parsing ERA file: AETNA_ERA_20240315.835'],
    ['info', 'Matched 14 payments to patient accounts'],
    ['info', 'Posting payment $1,247.50 to account #AC-2024-0891'],
    ['info', 'Posting payment $892.00 to account #AC-2024-0893'],
    ['debug', 'Reconciliation check: batch total = $12,847.50, posted = $12,847.50 ✓'],
    ['info', 'All ERA payments posted successfully'],
  ];

  // Pick the right log set based on bot name
  let logSet = claimsLogs;
  if (botName.includes('Eligibility')) logSet = eligibilityLogs;
  else if (botName.includes('Denial')) logSet = denialLogs;
  else if (botName.includes('Payment')) logSet = paymentLogs;

  // For failed runs, add error logs at the end
  if (status === 'failed') {
    logSet = [
      ...logSet.slice(0, 5),
      ['error', 'Critical failure — unable to continue processing'],
      ['error', 'TimeoutError: Element #submit-btn not found after 30s wait'],
    ];
  }

  const baseTime = new Date(minutesAgo(logSet.length * 0.3));
  return logSet.map(([level, message], i) => ({
    id: `log-${runId}-${i}`,
    run_id: runId,
    level,
    message,
    metadata_json: null,
    timestamp: new Date(baseTime.getTime() + i * 18_000).toISOString(),
  }));
}

// Pre-generate logs for each bot's most recent run
const ALL_LOGS: Record<string, LogEntry[]> = {};
for (const bot of DUMMY_BOTS) {
  const runs = ALL_RUNS[bot.id];
  if (runs?.[0]) {
    ALL_LOGS[runs[0].id] = generateLogs(runs[0].id, bot.name, runs[0].status);
    // Also generate logs for a few more runs
    for (let i = 1; i < Math.min(3, runs.length); i++) {
      ALL_LOGS[runs[i].id] = generateLogs(runs[i].id, bot.name, runs[i].status);
    }
  }
}

// ── Metrics ─────────────────────────────────────────────────────
export const DUMMY_METRICS: DashboardMetrics = {
  total_bots: 4,
  total_runs: 804,
  successful_runs: 721,
  failed_runs: 58,
  active_runs: 1,
  pending_runs: 0,
  success_rate: 89.7,
  avg_duration_seconds: 462.3,
};

// ── Public API (matches the real service signatures) ────────────
export function getDummyBots(): Bot[] {
  return DUMMY_BOTS;
}

export function getDummyBot(botId: string): Bot | undefined {
  return DUMMY_BOTS.find(b => b.id === botId);
}

export function getDummyBotRuns(botId: string, limit = 20, offset = 0): BotRunList {
  const runs = ALL_RUNS[botId] || [];
  return {
    runs: runs.slice(offset, offset + limit),
    total: runs.length,
  };
}

export function getDummyLogs(runId: string): LogList {
  const logs = ALL_LOGS[runId] || [];
  return { logs, total: logs.length };
}

export function getDummyScreenshots(_runId: string): { screenshots: Screenshot[]; run_id: string } {
  // No real screenshots in dummy mode
  return { screenshots: [], run_id: _runId };
}

export function getDummyMetrics(): DashboardMetrics {
  return DUMMY_METRICS;
}
