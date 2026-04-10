/**
 * Dashboard — Board Activity Home Page.
 *
 * Real-time overview of all boards, filtered by client/process.
 */

import { useState, useMemo } from 'react';
import { AlertTriangle } from 'lucide-react';
import Header from '../components/Header';
import SummaryCards from '../components/SummaryCards';
import FilterBar from '../components/FilterBar';
import BoardCard from '../components/BoardCard';
import type { BoardFilter } from '../types';
import {
  getBoards,
  getBoardMetrics,
  getFailedBoards,
} from '../services/boardData';
import './Dashboard.css';

export default function Dashboard() {
  const [filter, setFilter] = useState<BoardFilter>({
    clientId: null,
    processId: null,
    status: null,
    dateRange: 'today',
  });

  const boards = useMemo(() => getBoards(filter), [filter]);
  const metrics = useMemo(() => getBoardMetrics(filter), [filter]);
  const failedBoards = useMemo(() => getFailedBoards(filter), [filter]);

  // Group boards by status for display priority: live first, then processing, pending, failed, success
  const sortedBoards = useMemo(() => {
    const priority: Record<string, number> = {
      live: 0,
      processing: 1,
      pending: 2,
      failed: 3,
      success: 4,
    };
    return [...boards].sort((a, b) => (priority[a.status] ?? 5) - (priority[b.status] ?? 5));
  }, [boards]);

  return (
    <div className="dashboard" id="page-dashboard">
      <Header
        title="Board Activity"
        subtitle="Live monitoring & real-time status"
      />

      <div className="dashboard__content">
        {/* KPI Summary Cards */}
        <section className="dashboard__section">
          <SummaryCards metrics={metrics} />
        </section>

        {/* Filters */}
        <section className="dashboard__section">
          <FilterBar
            filter={filter}
            onFilterChange={setFilter}
            showStatus={true}
          />
        </section>

        {/* Board Grid */}
        <section className="dashboard__section">
          <div className="dashboard__section-header">
            <h2 className="dashboard__section-title">
              All Boards
            </h2>
            <span className="dashboard__section-count">
              {boards.length} board{boards.length !== 1 ? 's' : ''}
            </span>
          </div>

          {sortedBoards.length > 0 ? (
            <div className="dashboard__grid">
              {sortedBoards.map(board => (
                <BoardCard key={board.id} board={board} />
              ))}
            </div>
          ) : (
            <div className="dashboard__empty">
              No boards match the current filters.
            </div>
          )}
        </section>

        {/* Failure Details */}
        {failedBoards.length > 0 && (
          <section className="dashboard__section dashboard__section--failures">
            <div className="dashboard__section-header">
              <h2 className="dashboard__section-title dashboard__section-title--danger">
                <AlertTriangle size={18} />
                Failure Details
              </h2>
              <span className="dashboard__section-count dashboard__section-count--danger">
                {failedBoards.length} failed
              </span>
            </div>

            <div className="failure-list">
              {failedBoards.map(board => (
                <div key={board.id} className="failure-item">
                  <div className="failure-item__header">
                    <strong className="failure-item__name">{board.name}</strong>
                    <span className="failure-item__client">{board.clientName} — {board.processName}</span>
                  </div>
                  <div className="failure-item__details">
                    <div className="failure-item__reason">
                      <AlertTriangle size={14} />
                      <span>{board.failureReason}</span>
                    </div>
                    {board.failureDate && (
                      <span className="failure-item__date">
                        Failed on: {board.failureDate}
                      </span>
                    )}
                  </div>
                  <div className="failure-item__stats">
                    <span>{board.recordsProcessed.toLocaleString()} of {board.recordsTotal.toLocaleString()} records processed</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
