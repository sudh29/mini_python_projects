/**
 * StatusBadge — Color-coded board status indicator with micro-animations.
 */

import type { BoardStatus } from '../types';
import './StatusBadge.css';

interface StatusBadgeProps {
  status: BoardStatus;
  size?: 'sm' | 'md' | 'lg';
}

const STATUS_CONFIG: Record<BoardStatus, { label: string; className: string }> = {
  live: { label: 'Live', className: 'status-badge--live' },
  success: { label: 'Success', className: 'status-badge--success' },
  failed: { label: 'Failed', className: 'status-badge--failed' },
  pending: { label: 'Pending', className: 'status-badge--pending' },
  processing: { label: 'Processing', className: 'status-badge--processing' },
};

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];

  return (
    <span className={`status-badge status-badge--${size} ${config.className}`} id={`badge-${status}`}>
      <span className="status-badge__dot" />
      <span className="status-badge__label">{config.label}</span>
    </span>
  );
}
