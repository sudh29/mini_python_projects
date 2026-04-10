/**
 * BoardCard — Individual board status card.
 */

import { Clock, FileText, AlertTriangle } from 'lucide-react';
import type { Board } from '../types';
import StatusBadge from './StatusBadge';
import './BoardCard.css';

interface BoardCardProps {
  board: Board;
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function formatTime(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

function progressPercent(board: Board): number {
  if (board.recordsTotal === 0) return 0;
  return Math.round((board.recordsProcessed / board.recordsTotal) * 100);
}

export default function BoardCard({ board }: BoardCardProps) {
  const progress = progressPercent(board);
  const isActive = board.status === 'live' || board.status === 'processing';

  return (
    <div
      className={`board-card ${isActive ? 'board-card--active' : ''} ${board.status === 'failed' ? 'board-card--failed' : ''}`}
      id={`board-${board.id}`}
    >
      <div className="board-card__header">
        <div className="board-card__title-group">
          <h3 className="board-card__name">{board.name}</h3>
          <span className="board-card__client">{board.clientName}</span>
        </div>
        <StatusBadge status={board.status} size="sm" />
      </div>

      <div className="board-card__meta">
        <span className="board-card__process">{board.processName}</span>
        <span className="board-card__separator">•</span>
        <span className="board-card__date">{board.processingDate}</span>
      </div>

      {/* Progress bar */}
      <div className="board-card__progress">
        <div className="board-card__progress-bar">
          <div
            className={`board-card__progress-fill board-card__progress-fill--${board.status}`}
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="board-card__progress-info">
          <span>{board.recordsProcessed.toLocaleString()} / {board.recordsTotal.toLocaleString()} records</span>
          <span className="board-card__progress-pct">{progress}%</span>
        </div>
      </div>

      {/* Footer details */}
      <div className="board-card__footer">
        {board.startedAt && (
          <div className="board-card__detail">
            <Clock size={13} />
            <span>Started {formatTime(board.startedAt)}</span>
          </div>
        )}
        {board.duration !== null && (
          <div className="board-card__detail">
            <FileText size={13} />
            <span>{formatDuration(board.duration)}</span>
          </div>
        )}
      </div>

      {/* Failure reason */}
      {board.failureReason && (
        <div className="board-card__failure">
          <AlertTriangle size={14} />
          <span>{board.failureReason}</span>
        </div>
      )}
    </div>
  );
}
