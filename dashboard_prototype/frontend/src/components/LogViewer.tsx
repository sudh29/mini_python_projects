/**
 * Log viewer — scrollable, filterable log output with level-based coloring.
 */

import { useState, useEffect, useRef } from 'react';
import { Filter, Download, Trash2 } from 'lucide-react';
import type { LogEntry, LogLevel } from '../types';
import './LogViewer.css';

interface LogViewerProps {
  logs: LogEntry[];
  loading?: boolean;
  onFilterChange?: (level: LogLevel | null) => void;
  autoScroll?: boolean;
}

const LEVEL_COLORS: Record<string, string> = {
  debug: 'log--debug',
  info: 'log--info',
  warning: 'log--warning',
  error: 'log--error',
  critical: 'log--critical',
};

export default function LogViewer({ logs, loading = false, onFilterChange, autoScroll = true }: LogViewerProps) {
  const [activeFilter, setActiveFilter] = useState<LogLevel | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleFilterClick = (level: LogLevel | null) => {
    setActiveFilter(level);
    onFilterChange?.(level);
  };

  const formatTime = (ts: string) => {
    return new Date(ts).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="log-viewer" id="log-viewer">
      <div className="log-viewer__toolbar">
        <div className="log-viewer__filters">
          <Filter size={14} />
          <button
            className={`log-filter ${!activeFilter ? 'log-filter--active' : ''}`}
            onClick={() => handleFilterClick(null)}
          >
            All
          </button>
          {(['info', 'warning', 'error', 'debug'] as LogLevel[]).map(level => (
            <button
              key={level}
              className={`log-filter log-filter--${level} ${activeFilter === level ? 'log-filter--active' : ''}`}
              onClick={() => handleFilterClick(level)}
            >
              {level}
            </button>
          ))}
        </div>
        <span className="log-viewer__count">{logs.length} entries</span>
      </div>

      <div className="log-viewer__output" ref={containerRef}>
        {loading ? (
          <div className="log-viewer__empty">Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="log-viewer__empty">No log entries</div>
        ) : (
          logs.map(log => (
            <div key={log.id} className={`log-entry ${LEVEL_COLORS[log.level] || ''}`}>
              <span className="log-entry__time">{formatTime(log.timestamp)}</span>
              <span className={`log-entry__level log-entry__level--${log.level}`}>
                {log.level.toUpperCase().padEnd(8)}
              </span>
              <span className="log-entry__msg">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
