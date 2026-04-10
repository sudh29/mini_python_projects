/**
 * FilterBar — Reusable client/process/status filter component.
 */

import { useState, useEffect } from 'react';
import { Filter, X } from 'lucide-react';
import { getClients, getProcesses } from '../services/boardData';
import type { BoardFilter, BoardStatus } from '../types';
import './FilterBar.css';

interface FilterBarProps {
  filter: BoardFilter;
  onFilterChange: (filter: BoardFilter) => void;
  showDateRange?: boolean;
  showStatus?: boolean;
}

const STATUS_OPTIONS: { value: BoardStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'live', label: 'Live' },
  { value: 'success', label: 'Success' },
  { value: 'failed', label: 'Failed' },
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
];

const DATE_RANGE_OPTIONS: { value: BoardFilter['dateRange']; label: string }[] = [
  { value: 'today', label: 'Today' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: '90d', label: 'Last 90 Days' },
];

export default function FilterBar({
  filter,
  onFilterChange,
  showDateRange = false,
  showStatus = true,
}: FilterBarProps) {
  const clients = getClients();
  const [processes, setProcesses] = useState(getProcesses(filter.clientId));

  useEffect(() => {
    setProcesses(getProcesses(filter.clientId));
    // Reset process if client changes
    if (filter.processId) {
      const validProcess = getProcesses(filter.clientId).find(p => p.id === filter.processId);
      if (!validProcess) {
        onFilterChange({ ...filter, processId: null });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter.clientId]);

  const hasAnyFilter = filter.clientId || filter.processId || filter.status;

  const clearFilters = () => {
    onFilterChange({
      clientId: null,
      processId: null,
      status: null,
      dateRange: filter.dateRange,
    });
  };

  return (
    <div className="filter-bar" id="filter-bar">
      <div className="filter-bar__icon">
        <Filter size={16} />
      </div>

      <select
        className="filter-bar__select"
        id="filter-client"
        value={filter.clientId || ''}
        onChange={e => onFilterChange({
          ...filter,
          clientId: e.target.value || null,
          processId: null,
        })}
      >
        <option value="">All Clients</option>
        {clients.map(c => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>

      <select
        className="filter-bar__select"
        id="filter-process"
        value={filter.processId || ''}
        onChange={e => onFilterChange({
          ...filter,
          processId: e.target.value || null,
        })}
      >
        <option value="">All Processes</option>
        {processes.map(p => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>

      {showStatus && (
        <select
          className="filter-bar__select"
          id="filter-status"
          value={filter.status || ''}
          onChange={e => onFilterChange({
            ...filter,
            status: (e.target.value as BoardStatus) || null,
          })}
        >
          {STATUS_OPTIONS.map(s => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      )}

      {showDateRange && (
        <select
          className="filter-bar__select filter-bar__select--date"
          id="filter-date-range"
          value={filter.dateRange}
          onChange={e => onFilterChange({
            ...filter,
            dateRange: e.target.value as BoardFilter['dateRange'],
          })}
        >
          {DATE_RANGE_OPTIONS.map(d => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
      )}

      {hasAnyFilter && (
        <button className="filter-bar__clear" onClick={clearFilters} title="Clear all filters">
          <X size={14} />
          Clear
        </button>
      )}
    </div>
  );
}
