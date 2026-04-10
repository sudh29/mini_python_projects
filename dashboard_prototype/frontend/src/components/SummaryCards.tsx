/**
 * SummaryCards — Top-level KPI cards showing board metrics.
 */

import {
  Radio,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
} from 'lucide-react';
import type { BoardMetrics } from '../types';
import './SummaryCards.css';

interface SummaryCardsProps {
  metrics: BoardMetrics;
  loading?: boolean;
}

export default function SummaryCards({ metrics, loading = false }: SummaryCardsProps) {
  if (loading) {
    return (
      <div className="summary-cards" id="summary-cards">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="summary-card summary-card--skeleton">
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
      label: 'Total Boards',
      value: metrics.totalBoards,
      icon: <BarChart3 size={20} />,
      color: 'info',
    },
    {
      label: 'Live Now',
      value: metrics.liveBoards,
      icon: <Radio size={20} />,
      color: 'live',
      pulse: metrics.liveBoards > 0,
    },
    {
      label: 'Processed',
      value: metrics.successBoards,
      icon: <CheckCircle2 size={20} />,
      color: 'success',
    },
    {
      label: 'Failed',
      value: metrics.failedBoards,
      icon: <XCircle size={20} />,
      color: 'danger',
    },
    {
      label: 'Success Rate',
      value: `${metrics.successRate}%`,
      icon: <TrendingUp size={20} />,
      color: metrics.successRate >= 90 ? 'success' : metrics.successRate >= 75 ? 'warning' : 'danger',
    },
    {
      label: 'Avg Duration',
      value: `${Math.floor(metrics.avgDuration / 60)}m ${metrics.avgDuration % 60}s`,
      icon: <Clock size={20} />,
      color: 'muted',
    },
  ];

  return (
    <div className="summary-cards" id="summary-cards">
      {cards.map((card, i) => (
        <div
          key={i}
          className={`summary-card summary-card--${card.color} ${card.pulse ? 'summary-card--pulse' : ''}`}
        >
          <div className="summary-card__header">
            <div className="summary-card__icon">{card.icon}</div>
            <span className="summary-card__label">{card.label}</span>
          </div>
          <span className="summary-card__value">{card.value}</span>
        </div>
      ))}
    </div>
  );
}
