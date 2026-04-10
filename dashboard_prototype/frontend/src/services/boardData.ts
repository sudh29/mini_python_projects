/**
 * Board Activity Monitoring — Dummy Data Service
 *
 * Provides realistic client/process/board data for the dashboard.
 * Structured to mirror a real API so swapping to live endpoints is trivial.
 */

import type {
  Client,
  Process,
  Board,
  BoardStatus,
  BoardMetrics,
  BoardFilter,
  HistoricalDataPoint,
  ClientTrendPoint,
  ReportRow,
} from '../types';

// ── Clients ─────────────────────────────────────────────────────
const CLIENTS: Client[] = [
  { id: 'cl-autoone', name: 'AutoOne', code: 'AO' },
  { id: 'cl-ent', name: 'ENT', code: 'ENT' },
  { id: 'cl-venables', name: 'Venables', code: 'VEN' },
];

// ── Processes ───────────────────────────────────────────────────
const PROCESSES: Process[] = [
  // AutoOne
  { id: 'p-ao-claims', clientId: 'cl-autoone', name: 'Claims Processing', code: 'CLM' },
  { id: 'p-ao-eligibility', clientId: 'cl-autoone', name: 'Eligibility Verification', code: 'ELG' },
  { id: 'p-ao-payment', clientId: 'cl-autoone', name: 'Payment Posting', code: 'PAY' },
  { id: 'p-ao-denial', clientId: 'cl-autoone', name: 'Denial Management', code: 'DEN' },
  // ENT
  { id: 'p-ent-claims', clientId: 'cl-ent', name: 'Claims Processing', code: 'CLM' },
  { id: 'p-ent-remittance', clientId: 'cl-ent', name: 'Remittance Advice', code: 'REM' },
  { id: 'p-ent-preauth', clientId: 'cl-ent', name: 'Pre-Authorization', code: 'PRA' },
  { id: 'p-ent-enrollment', clientId: 'cl-ent', name: 'Member Enrollment', code: 'ENR' },
  // Venables
  { id: 'p-ven-claims', clientId: 'cl-venables', name: 'Claims Processing', code: 'CLM' },
  { id: 'p-ven-eligibility', clientId: 'cl-venables', name: 'Eligibility Verification', code: 'ELG' },
  { id: 'p-ven-billing', clientId: 'cl-venables', name: 'Billing Reconciliation', code: 'BIL' },
];

// ── Helpers ─────────────────────────────────────────────────────
function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function daysAgoStr(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

function hoursAgoISO(hours: number): string {
  return new Date(Date.now() - hours * 3600_000).toISOString();
}

function minutesAgoISO(mins: number): string {
  return new Date(Date.now() - mins * 60_000).toISOString();
}

function randomBetween(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const FAILURE_REASONS = [
  'Connection timeout to payer portal after 30s',
  'Invalid date format in source file — expected MM/DD/YYYY',
  'Duplicate record detected — primary key violation',
  'Authentication token expired during processing',
  'Source data file not found for scheduled date',
  'Database connection pool exhausted — max 50 connections',
  'Missing required field: diagnosis_code',
  'Payer portal returned 503 Service Unavailable',
  'Data validation failed — CPT code not recognized',
  'Rate limit exceeded on clearinghouse API',
];

// ── Board Generation ────────────────────────────────────────────
function generateBoards(): Board[] {
  const boards: Board[] = [];
  const todayStr = today();
  let boardIndex = 0;

  const statusDistributions: Record<string, BoardStatus[]> = {
    'cl-autoone': ['live', 'success', 'success', 'failed'],
    'cl-ent': ['live', 'live', 'success', 'failed', 'success', 'pending', 'success', 'processing'],
    'cl-venables': ['success', 'success', 'failed', 'success', 'success', 'live'],
  };

  for (const client of CLIENTS) {
    const clientProcesses = PROCESSES.filter(p => p.clientId === client.id);
    const statuses = statusDistributions[client.id] || ['success'];

    for (let pi = 0; pi < clientProcesses.length; pi++) {
      const proc = clientProcesses[pi];
      // Each process spawns 2-3 boards (e.g. different data dates or sub-batches)
      const numBoards = pi === 0 ? 3 : 2;

      for (let bi = 0; bi < numBoards; bi++) {
        const statusIdx = (boardIndex) % statuses.length;
        const status = statuses[statusIdx];
        const recordsTotal = randomBetween(150, 2500);
        const isFailed = status === 'failed';
        const isLive = status === 'live';
        const isProcessing = status === 'processing';
        const isPending = status === 'pending';
        const isComplete = status === 'success';

        const processingDate = bi === 0 ? todayStr : daysAgoStr(bi);
        const durationSec = isFailed
          ? randomBetween(30, 180)
          : isComplete
            ? randomBetween(120, 900)
            : null;

        const startOffset = bi === 0 ? randomBetween(1, 4) : randomBetween(4 + bi * 2, 8 + bi * 3);

        boards.push({
          id: `brd-${client.code.toLowerCase()}-${proc.code.toLowerCase()}-${bi}`,
          name: `${client.code}-${proc.code}-${processingDate}`,
          clientId: client.id,
          clientName: client.name,
          processId: proc.id,
          processName: proc.name,
          status,
          lastProcessedAt: isComplete || isFailed ? minutesAgoISO(randomBetween(5, 120)) : null,
          processingDate,
          startedAt: !isPending ? hoursAgoISO(startOffset) : null,
          completedAt: isComplete || isFailed ? minutesAgoISO(randomBetween(2, 90)) : null,
          duration: durationSec,
          failureReason: isFailed ? FAILURE_REASONS[boardIndex % FAILURE_REASONS.length] : null,
          failureDate: isFailed ? processingDate : null,
          recordsProcessed: isComplete
            ? recordsTotal
            : isFailed
              ? Math.floor(recordsTotal * 0.3 + Math.random() * recordsTotal * 0.4)
              : isLive || isProcessing
                ? Math.floor(recordsTotal * Math.random() * 0.7)
                : 0,
          recordsTotal,
        });

        boardIndex++;
      }
    }
  }

  return boards;
}

// Cache boards so they're stable within a session
let _cachedBoards: Board[] | null = null;
function getGeneratedBoards(): Board[] {
  if (!_cachedBoards) {
    _cachedBoards = generateBoards();
  }
  return _cachedBoards;
}

// ── Historical Data Generation ──────────────────────────────────
function generateHistoricalData(days: number): HistoricalDataPoint[] {
  const data: HistoricalDataPoint[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const dateStr = daysAgoStr(i);
    const total = randomBetween(22, 32);
    const failed = randomBetween(1, 5);
    const success = total - failed;
    data.push({
      date: dateStr,
      totalBoards: total,
      success,
      failed,
      successRate: Math.round((success / total) * 1000) / 10,
      avgDuration: randomBetween(180, 600),
    });
  }
  return data;
}

function generateClientTrends(days: number): ClientTrendPoint[] {
  const points: ClientTrendPoint[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const dateStr = daysAgoStr(i);
    for (const client of CLIENTS) {
      points.push({
        date: dateStr,
        client: client.name,
        volume: randomBetween(6, 14),
        successRate: randomBetween(78, 99),
      });
    }
  }
  return points;
}

let _cachedHistory: HistoricalDataPoint[] | null = null;
let _cachedClientTrends: ClientTrendPoint[] | null = null;

// ── Public API ──────────────────────────────────────────────────

export function getClients(): Client[] {
  return CLIENTS;
}

export function getProcesses(clientId?: string | null): Process[] {
  if (!clientId) return PROCESSES;
  return PROCESSES.filter(p => p.clientId === clientId);
}

export function getBoards(filter?: BoardFilter): Board[] {
  let boards = getGeneratedBoards();

  if (filter?.clientId) {
    boards = boards.filter(b => b.clientId === filter.clientId);
  }
  if (filter?.processId) {
    boards = boards.filter(b => b.processId === filter.processId);
  }
  if (filter?.status) {
    boards = boards.filter(b => b.status === filter.status);
  }

  return boards;
}

export function getBoardMetrics(filter?: BoardFilter): BoardMetrics {
  const boards = getBoards(filter);
  const total = boards.length;
  const live = boards.filter(b => b.status === 'live').length;
  const success = boards.filter(b => b.status === 'success').length;
  const failed = boards.filter(b => b.status === 'failed').length;
  const pending = boards.filter(b => b.status === 'pending').length;
  const processing = boards.filter(b => b.status === 'processing').length;
  const completed = success + failed;
  const durations = boards
    .filter(b => b.duration !== null)
    .map(b => b.duration!);
  const avgDuration = durations.length
    ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
    : 0;

  return {
    totalBoards: total,
    liveBoards: live,
    successBoards: success,
    failedBoards: failed,
    pendingBoards: pending,
    processingBoards: processing,
    successRate: completed > 0 ? Math.round((success / completed) * 1000) / 10 : 0,
    avgDuration,
  };
}

export function getFailedBoards(filter?: BoardFilter): Board[] {
  return getBoards(filter).filter(b => b.status === 'failed');
}

export function getHistoricalData(range: BoardFilter['dateRange']): HistoricalDataPoint[] {
  const days = range === '7d' ? 7 : range === '30d' ? 30 : range === '90d' ? 90 : 1;
  if (!_cachedHistory || _cachedHistory.length !== days) {
    _cachedHistory = generateHistoricalData(days);
  }
  return _cachedHistory;
}

export function getClientTrends(range: BoardFilter['dateRange']): ClientTrendPoint[] {
  const days = range === '7d' ? 7 : range === '30d' ? 30 : range === '90d' ? 90 : 1;
  if (!_cachedClientTrends || _cachedClientTrends.length !== days * CLIENTS.length) {
    _cachedClientTrends = generateClientTrends(days);
  }
  return _cachedClientTrends;
}

// ── CSV Report Generation ───────────────────────────────────────
export function generateReportRows(filter?: BoardFilter): ReportRow[] {
  const boards = getBoards(filter);
  return boards.map(b => ({
    boardName: b.name,
    client: b.clientName,
    process: b.processName,
    status: b.status,
    processingDate: b.processingDate,
    startedAt: b.startedAt || '—',
    completedAt: b.completedAt || '—',
    duration: b.duration ? `${Math.floor(b.duration / 60)}m ${b.duration % 60}s` : '—',
    recordsProcessed: b.recordsProcessed,
    recordsTotal: b.recordsTotal,
    failureReason: b.failureReason || '',
  }));
}

export function reportRowsToCSV(rows: ReportRow[]): string {
  const headers = [
    'Board Name', 'Client', 'Process', 'Status', 'Processing Date',
    'Started At', 'Completed At', 'Duration', 'Records Processed',
    'Records Total', 'Failure Reason',
  ];
  const csvLines = [headers.join(',')];

  for (const row of rows) {
    csvLines.push([
      `"${row.boardName}"`,
      `"${row.client}"`,
      `"${row.process}"`,
      `"${row.status}"`,
      `"${row.processingDate}"`,
      `"${row.startedAt}"`,
      `"${row.completedAt}"`,
      `"${row.duration}"`,
      row.recordsProcessed,
      row.recordsTotal,
      `"${row.failureReason}"`,
    ].join(','));
  }

  return csvLines.join('\n');
}

export function downloadCSV(filename: string, csvContent: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
