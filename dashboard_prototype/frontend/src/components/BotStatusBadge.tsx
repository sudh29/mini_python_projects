/**
 * Bot status badge — color-coded pill with pulse animation for running.
 */

import type { BotStatus } from '../types';
import './BotStatusBadge.css';

interface BotStatusBadgeProps {
  status: BotStatus;
  size?: 'sm' | 'md';
}

const STATUS_CONFIG: Record<BotStatus, { label: string; className: string }> = {
  idle: { label: 'Idle', className: 'badge--idle' },
  pending: { label: 'Pending', className: 'badge--pending' },
  running: { label: 'Running', className: 'badge--running' },
  success: { label: 'Success', className: 'badge--success' },
  failed: { label: 'Failed', className: 'badge--failed' },
  cancelled: { label: 'Cancelled', className: 'badge--cancelled' },
  retrying: { label: 'Retrying', className: 'badge--retrying' },
};

export default function BotStatusBadge({ status, size = 'md' }: BotStatusBadgeProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.idle;

  return (
    <span className={`badge ${config.className} badge--${size}`}>
      <span className="badge__dot" />
      {config.label}
    </span>
  );
}
