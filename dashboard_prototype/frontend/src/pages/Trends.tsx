/**
 * Trends — Performance charts and analytics.
 */

import { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import Header from '../components/Header';
import FilterBar from '../components/FilterBar';
import type { BoardFilter } from '../types';
import {
  getHistoricalData,
  getClientTrends,
  getClients,
  getBoardMetrics,
} from '../services/boardData';
import './Trends.css';

export default function Trends() {
  const [filter, setFilter] = useState<BoardFilter>({
    clientId: null,
    processId: null,
    status: null,
    dateRange: '30d',
    startDate: null,
    endDate: null,
  });

  const historicalData = useMemo(() => getHistoricalData(filter), [filter.dateRange, filter.startDate, filter.endDate]);
  const clientTrends = useMemo(() => getClientTrends(filter), [filter.dateRange, filter.startDate, filter.endDate]);
  const clients = getClients();
  const metrics = useMemo(() => getBoardMetrics(filter), [filter]);

  // Aggregate client volume per date for stacked bar
  const clientVolumeByDate = useMemo(() => {
    const dateMap: Record<string, Record<string, number>> = {};
    for (const pt of clientTrends) {
      if (!dateMap[pt.date]) dateMap[pt.date] = {};
      dateMap[pt.date][pt.client] = pt.volume;
    }
    return Object.entries(dateMap)
      .map(([date, volumes]) => ({ date: formatDateLabel(date), ...volumes }))
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [clientTrends]);

  // Client success rate lines
  const clientSuccessRates = useMemo(() => {
    const dateMap: Record<string, Record<string, number>> = {};
    for (const pt of clientTrends) {
      if (!dateMap[pt.date]) dateMap[pt.date] = {};
      dateMap[pt.date][pt.client] = pt.successRate;
    }
    return Object.entries(dateMap)
      .map(([date, rates]) => ({ date: formatDateLabel(date), ...rates }))
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [clientTrends]);

  const formattedHistory = useMemo(() =>
    historicalData.map(d => ({
      ...d,
      date: formatDateLabel(d.date),
    })),
    [historicalData]
  );

  const CLIENT_COLORS = ['#0ea5e9', '#10b981', '#f59e0b'];

  return (
    <div className="trends" id="page-trends">
      <Header
        title="Trends & Metrics"
        subtitle="Performance analytics over time"
      />

      <div className="trends__content">
        {/* Filters */}
        <FilterBar
          filter={filter}
          onFilterChange={setFilter}
          showDateRange={true}
          showStatus={false}
        />

        {/* Stats Strip */}
        <div className="trends__stats-strip">
          <div className="trends__stat">
            <span className="trends__stat-label">Avg Daily Boards</span>
            <span className="trends__stat-value">
              {historicalData.length > 0
                ? Math.round(historicalData.reduce((s, d) => s + d.totalBoards, 0) / historicalData.length)
                : 0}
            </span>
          </div>
          <div className="trends__stat">
            <span className="trends__stat-label">Avg Success Rate</span>
            <span className="trends__stat-value trends__stat-value--success">
              {historicalData.length > 0
                ? (historicalData.reduce((s, d) => s + d.successRate, 0) / historicalData.length).toFixed(1)
                : 0}%
            </span>
          </div>
          <div className="trends__stat">
            <span className="trends__stat-label">Total Failures</span>
            <span className="trends__stat-value trends__stat-value--danger">
              {historicalData.reduce((s, d) => s + d.failed, 0)}
            </span>
          </div>
          <div className="trends__stat">
            <span className="trends__stat-label">Avg Duration</span>
            <span className="trends__stat-value">
              {metrics.avgDuration > 0 ? `${Math.floor(metrics.avgDuration / 60)}m` : '—'}
            </span>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="trends__charts">
          {/* Success/Failure Trend */}
          <div className="trends__chart-card">
            <h3 className="trends__chart-title">Success vs Failure Trend</h3>
            <div className="trends__chart-wrapper">
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={formattedHistory}>
                  <defs>
                    <linearGradient id="gradSuccess" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gradFailed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                  <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--card-bg)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="success"
                    stroke="#10b981"
                    strokeWidth={2}
                    fill="url(#gradSuccess)"
                    name="Success"
                  />
                  <Area
                    type="monotone"
                    dataKey="failed"
                    stroke="#ef4444"
                    strokeWidth={2}
                    fill="url(#gradFailed)"
                    name="Failed"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Processing Volume by Client */}
          <div className="trends__chart-card">
            <h3 className="trends__chart-title">Processing Volume by Client</h3>
            <div className="trends__chart-wrapper">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={clientVolumeByDate}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                  <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--card-bg)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend />
                  {clients.map((client, i) => (
                    <Bar
                      key={client.id}
                      dataKey={client.name}
                      fill={CLIENT_COLORS[i % CLIENT_COLORS.length]}
                      radius={[4, 4, 0, 0]}
                      stackId="volume"
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Success Rate Over Time by Client */}
          <div className="trends__chart-card trends__chart-card--full">
            <h3 className="trends__chart-title">Success Rate by Client</h3>
            <div className="trends__chart-wrapper">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={clientSuccessRates}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                  <YAxis
                    domain={[60, 100]}
                    tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                    tickFormatter={(v: number) => `${v}%`}
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--card-bg)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(value) => [`${value}%`, '']}
                  />
                  <Legend />
                  {clients.map((client, i) => (
                    <Line
                      key={client.id}
                      type="monotone"
                      dataKey={client.name}
                      stroke={CLIENT_COLORS[i % CLIENT_COLORS.length]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Helpers ─────────────────────────────────────────────────────
function formatDateLabel(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
