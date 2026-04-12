/**
 * Reports — Report generation with CSV download.
 */

import { useState, useMemo } from 'react';
import {
  Download,
  FileSpreadsheet,
  Calendar,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';
import Header from '../components/Header';
import FilterBar from '../components/FilterBar';
import StatusBadge from '../components/StatusBadge';
import type { BoardFilter, BoardStatus } from '../types';
import {
  generateReportRows,
  reportRowsToCSV,
  downloadCSV,
  getBoardMetrics,
} from '../services/boardData';
import './Reports.css';

export default function Reports() {
  const [filter, setFilter] = useState<BoardFilter>({
    clientId: null,
    processId: null,
    status: null,
    dateRange: 'today',
    startDate: null,
    endDate: null,
  });
  const [isHistorical, setIsHistorical] = useState(false);

  // When toggling to historical, change date range
  const effectiveFilter = useMemo(() => ({
    ...filter,
    dateRange: isHistorical ? filter.dateRange : 'today' as const,
  }), [filter, isHistorical]);

  const reportRows = useMemo(() => generateReportRows(effectiveFilter), [effectiveFilter]);
  const metrics = useMemo(() => getBoardMetrics(effectiveFilter), [effectiveFilter]);

  const handleDownload = () => {
    const csv = reportRowsToCSV(reportRows);
    const dateStr = new Date().toISOString().slice(0, 10);
    const clientSuffix = filter.clientId ? `-${filter.clientId}` : '';
    downloadCSV(`board-report${clientSuffix}-${dateStr}.csv`, csv);
  };

  return (
    <div className="reports" id="page-reports">
      <Header
        title="Reports"
        subtitle="Generate and download dashboard reports"
      />

      <div className="reports__content">
        {/* Report Controls */}
        <section className="reports__controls">
          <div className="reports__toggle-group">
            <button
              className={`reports__toggle ${!isHistorical ? 'reports__toggle--active' : ''}`}
              onClick={() => setIsHistorical(false)}
              id="btn-current"
            >
              <Calendar size={15} />
              Current Data
            </button>
            <button
              className={`reports__toggle ${isHistorical ? 'reports__toggle--active' : ''}`}
              onClick={() => setIsHistorical(true)}
              id="btn-historical"
            >
              {isHistorical ? <ToggleRight size={15} /> : <ToggleLeft size={15} />}
              Historical Data
            </button>
          </div>

          <FilterBar
            filter={filter}
            onFilterChange={setFilter}
            showDateRange={isHistorical}
            showStatus={true}
          />
        </section>

        {/* Report Summary */}
        <section className="reports__summary">
          <div className="reports__summary-card">
            <span className="reports__summary-label">Total Records</span>
            <span className="reports__summary-value">{reportRows.length}</span>
          </div>
          <div className="reports__summary-card reports__summary-card--success">
            <span className="reports__summary-label">Successful</span>
            <span className="reports__summary-value">{metrics.successBoards}</span>
          </div>
          <div className="reports__summary-card reports__summary-card--danger">
            <span className="reports__summary-label">Failed</span>
            <span className="reports__summary-value">{metrics.failedBoards}</span>
          </div>
          <div className="reports__summary-card reports__summary-card--accent">
            <span className="reports__summary-label">Success Rate</span>
            <span className="reports__summary-value">{metrics.successRate}%</span>
          </div>
        </section>

        {/* Download Button */}
        <div className="reports__actions">
          <button className="reports__download-btn" onClick={handleDownload} id="btn-download-csv">
            <Download size={16} />
            Download CSV
          </button>
          <span className="reports__row-count">
            <FileSpreadsheet size={14} />
            {reportRows.length} rows ready for export
          </span>
        </div>

        {/* Preview Table */}
        <section className="reports__table-section">
          <h2 className="reports__table-title">Preview</h2>
          <div className="reports__table-wrapper">
            <table className="reports__table" id="report-table">
              <thead>
                <tr>
                  <th>Board Name</th>
                  <th>Client</th>
                  <th>Process</th>
                  <th>Status</th>
                  <th>Processing Date</th>
                  <th>Duration</th>
                  <th>Records</th>
                  <th>Failure Reason</th>
                </tr>
              </thead>
              <tbody>
                {reportRows.map((row, i) => (
                  <tr key={i}>
                    <td className="reports__cell--name">{row.boardName}</td>
                    <td>{row.client}</td>
                    <td>{row.process}</td>
                    <td>
                      <StatusBadge status={row.status as BoardStatus} size="sm" />
                    </td>
                    <td>{row.processingDate}</td>
                    <td>{row.duration}</td>
                    <td>{row.recordsProcessed.toLocaleString()} / {row.recordsTotal.toLocaleString()}</td>
                    <td className="reports__cell--failure">{row.failureReason || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
