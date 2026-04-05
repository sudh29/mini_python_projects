/**
 * Bot card — dashboard tile showing bot status, stats, and quick actions.
 */

import { useNavigate } from 'react-router-dom';
import { Play, Square, Clock, TrendingUp, BarChart3 } from 'lucide-react';
import type { Bot } from '../types';
import BotStatusBadge from './BotStatusBadge';
import './BotCard.css';

interface BotCardProps {
  bot: Bot;
  onRun?: (botId: string) => void;
  onStop?: (botId: string) => void;
}

function formatTimeAgo(dateStr: string | null): string {
  if (!dateStr) return 'Never';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function BotCard({ bot, onRun, onStop }: BotCardProps) {
  const navigate = useNavigate();
  const isRunning = bot.current_status === 'running' || bot.current_status === 'pending';

  return (
    <div
      className={`bot-card ${isRunning ? 'bot-card--active' : ''}`}
      id={`bot-card-${bot.id}`}
      onClick={() => navigate(`/bots/${bot.id}`)}
      role="button"
      tabIndex={0}
    >
      <div className="bot-card__header">
        <div className="bot-card__info">
          <h3 className="bot-card__name">{bot.name}</h3>
          <span className="bot-card__process">{bot.process_name}</span>
        </div>
        <BotStatusBadge status={bot.current_status} />
      </div>

      {bot.description && (
        <p className="bot-card__desc">{bot.description}</p>
      )}

      <div className="bot-card__stats">
        <div className="bot-card__stat">
          <BarChart3 size={14} />
          <span>{bot.total_runs} runs</span>
        </div>
        <div className="bot-card__stat">
          <TrendingUp size={14} />
          <span>{bot.success_rate}%</span>
        </div>
        <div className="bot-card__stat">
          <Clock size={14} />
          <span>{formatTimeAgo(bot.last_run_at)}</span>
        </div>
      </div>

      <div className="bot-card__actions" onClick={e => e.stopPropagation()}>
        {isRunning ? (
          <button
            className="bot-card__btn bot-card__btn--stop"
            onClick={() => onStop?.(bot.id)}
            id={`btn-stop-${bot.id}`}
          >
            <Square size={14} />
            Stop
          </button>
        ) : (
          <button
            className="bot-card__btn bot-card__btn--run"
            onClick={() => onRun?.(bot.id)}
            id={`btn-run-${bot.id}`}
          >
            <Play size={14} />
            Run
          </button>
        )}
      </div>
    </div>
  );
}
