/**
 * Bot detail page — full bot info, run history, live logs, screenshots.
 */

import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, Square, RefreshCw } from 'lucide-react';
import Header from '../components/Header';
import BotStatusBadge from '../components/BotStatusBadge';
import LogViewer from '../components/LogViewer';
import ScreenshotViewer from '../components/ScreenshotViewer';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchBot, fetchBotRuns, fetchLogs, fetchScreenshots, runBot, stopBot } from '../services/api';
import type { Bot, BotRun, LogEntry } from '../types';
import { useState, useCallback } from 'react';
import './BotDetail.css';

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function formatDuration(start: string | null, end: string | null): string {
  if (!start) return '—';
  const s = new Date(start).getTime();
  const e = end ? new Date(end).getTime() : Date.now();
  const diff = Math.floor((e - s) / 1000);
  const mins = Math.floor(diff / 60);
  const secs = diff % 60;
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

export default function BotDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const { data: bot, loading: botLoading, refetch: refetchBot } = useApi<Bot>(
    () => fetchBot(id!),
    [id]
  );

  const { data: runsData, loading: runsLoading, refetch: refetchRuns } = useApi(
    () => fetchBotRuns(id!, 20),
    [id]
  );

  const effectiveRunId = selectedRunId || runsData?.runs?.[0]?.id;

  const { data: logsData, loading: logsLoading, refetch: refetchLogs } = useApi(
    () => effectiveRunId ? fetchLogs(effectiveRunId) : Promise.resolve({ logs: [], total: 0 }),
    [effectiveRunId]
  );

  const { data: screenshotsData, loading: ssLoading } = useApi(
    () => effectiveRunId ? fetchScreenshots(effectiveRunId) : Promise.resolve({ screenshots: [], run_id: '' }),
    [effectiveRunId]
  );

  const { isConnected } = useWebSocket({
    onStatusUpdate: useCallback(() => {
      refetchBot();
      refetchRuns();
      refetchLogs();
    }, [refetchBot, refetchRuns, refetchLogs]),
  });

  const isRunning = bot?.current_status === 'running' || bot?.current_status === 'pending';

  const handleRun = async () => {
    if (!id) return;
    try {
      await runBot(id);
      refetchBot();
      refetchRuns();
    } catch (err) {
      console.error('Failed to run bot:', err);
    }
  };

  const handleStop = async () => {
    if (!id) return;
    try {
      await stopBot(id);
      refetchBot();
      refetchRuns();
    } catch (err) {
      console.error('Failed to stop bot:', err);
    }
  };

  if (botLoading) {
    return (
      <div className="bot-detail">
        <Header title="Loading..." isConnected={isConnected} />
        <div className="bot-detail__loading">Loading bot details...</div>
      </div>
    );
  }

  if (!bot) {
    return (
      <div className="bot-detail">
        <Header title="Not Found" isConnected={isConnected} />
        <div className="bot-detail__loading">Bot not found</div>
      </div>
    );
  }

  return (
    <div className="bot-detail" id="page-bot-detail">
      <Header title={bot.name} subtitle={bot.process_name} isConnected={isConnected} />

      <div className="bot-detail__content">
        {/* Top bar: Back + Actions */}
        <div className="bot-detail__topbar">
          <button className="bot-detail__back" onClick={() => navigate('/')}>
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <div className="bot-detail__actions">
            <BotStatusBadge status={bot.current_status} />
            {isRunning ? (
              <button className="btn btn--danger" onClick={handleStop} id="btn-stop">
                <Square size={14} /> Stop
              </button>
            ) : (
              <button className="btn btn--primary" onClick={handleRun} id="btn-run">
                <Play size={14} /> Run Now
              </button>
            )}
          </div>
        </div>

        {/* Bot Info */}
        <div className="bot-detail__info-grid">
          <div className="info-card">
            <span className="info-card__label">Process Name</span>
            <span className="info-card__value">{bot.process_name}</span>
          </div>
          <div className="info-card">
            <span className="info-card__label">Total Runs</span>
            <span className="info-card__value">{bot.total_runs}</span>
          </div>
          <div className="info-card">
            <span className="info-card__label">Success Rate</span>
            <span className="info-card__value">{bot.success_rate}%</span>
          </div>
          <div className="info-card">
            <span className="info-card__label">Last Run</span>
            <span className="info-card__value">{formatDate(bot.last_run_at)}</span>
          </div>
        </div>

        {bot.description && (
          <div className="bot-detail__description">
            <p>{bot.description}</p>
          </div>
        )}

        {/* Two-column layout: Runs + Logs */}
        <div className="bot-detail__columns">
          {/* Run History */}
          <div className="bot-detail__panel">
            <div className="panel-header">
              <h3>Run History</h3>
              <button className="panel-header__action" onClick={refetchRuns}>
                <RefreshCw size={14} />
              </button>
            </div>
            <div className="run-history">
              {runsLoading ? (
                <div className="run-history__empty">Loading runs...</div>
              ) : !runsData?.runs.length ? (
                <div className="run-history__empty">No runs yet</div>
              ) : (
                runsData.runs.map((run: BotRun) => (
                  <div
                    key={run.id}
                    className={`run-row ${effectiveRunId === run.id ? 'run-row--selected' : ''}`}
                    onClick={() => setSelectedRunId(run.id)}
                  >
                    <BotStatusBadge status={run.status} size="sm" />
                    <span className="run-row__time">{formatDate(run.start_time)}</span>
                    <span className="run-row__duration">
                      {formatDuration(run.start_time, run.end_time)}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Live Logs */}
          <div className="bot-detail__panel bot-detail__panel--logs">
            <LogViewer
              logs={(logsData?.logs || []) as LogEntry[]}
              loading={logsLoading}
            />
          </div>
        </div>

        {/* Screenshots */}
        <ScreenshotViewer
          screenshots={screenshotsData?.screenshots || []}
          loading={ssLoading}
        />
      </div>
    </div>
  );
}
