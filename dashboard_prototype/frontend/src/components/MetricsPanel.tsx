/**
 * Metrics panel — summary cards showing key dashboard KPIs.
 */

import { Bot, CheckCircle, XCircle, Zap, Clock, TrendingUp } from 'lucide-react';
import type { DashboardMetrics } from '../types';
import './MetricsPanel.css';

interface MetricsPanelProps {
  metrics: DashboardMetrics | null;
  loading?: boolean;
}

export default function MetricsPanel({ metrics, loading = false }: MetricsPanelProps) {
  if (loading || !metrics) {
    return (
      <div className="metrics-panel" id="metrics-panel">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="metric-card metric-card--skeleton">
            <div className="skeleton skeleton--icon" />
            <div className="skeleton skeleton--text" />
            <div className="skeleton skeleton--value" />
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: 'Total Bots',
      value: metrics.total_bots,
      icon: <Bot size={20} />,
      color: 'accent',
    },
    {
      label: 'Active Runs',
      value: metrics.active_runs,
      icon: <Zap size={20} />,
      color: 'info',
    },
    {
      label: 'Total Runs',
      value: metrics.total_runs,
      icon: <TrendingUp size={20} />,
      color: 'accent',
    },
    {
      label: 'Successful',
      value: metrics.successful_runs,
      icon: <CheckCircle size={20} />,
      color: 'success',
    },
    {
      label: 'Failed',
      value: metrics.failed_runs,
      icon: <XCircle size={20} />,
      color: 'danger',
    },
    {
      label: 'Success Rate',
      value: `${metrics.success_rate}%`,
      icon: <TrendingUp size={20} />,
      color: metrics.success_rate >= 90 ? 'success' : metrics.success_rate >= 70 ? 'warning' : 'danger',
    },
  ];

  return (
    <div className="metrics-panel" id="metrics-panel">
      {cards.map((card, i) => (
        <div key={i} className={`metric-card metric-card--${card.color}`}>
          <div className="metric-card__icon">{card.icon}</div>
          <span className="metric-card__label">{card.label}</span>
          <span className="metric-card__value">{card.value}</span>
        </div>
      ))}
    </div>
  );
}
