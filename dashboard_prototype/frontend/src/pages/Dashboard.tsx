/**
 * Dashboard page — main overview with metrics and bot grid.
 */

import { useCallback } from 'react';
import Header from '../components/Header';
import MetricsPanel from '../components/MetricsPanel';
import BotCard from '../components/BotCard';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchBots, fetchMetrics, runBot, stopBot } from '../services/api';
import type { Bot } from '../types';
import './Dashboard.css';

export default function Dashboard() {
  const { data: bots, loading: botsLoading, refetch: refetchBots } = useApi<Bot[]>(fetchBots);
  const { data: metrics, loading: metricsLoading, refetch: refetchMetrics } = useApi(fetchMetrics);

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    onStatusUpdate: useCallback(() => {
      refetchBots();
      refetchMetrics();
    }, [refetchBots, refetchMetrics]),
  });

  const handleRun = async (botId: string) => {
    try {
      await runBot(botId);
      refetchBots();
      refetchMetrics();
    } catch (err) {
      console.error('Failed to run bot:', err);
    }
  };

  const handleStop = async (botId: string) => {
    try {
      await stopBot(botId);
      refetchBots();
      refetchMetrics();
    } catch (err) {
      console.error('Failed to stop bot:', err);
    }
  };

  return (
    <div className="dashboard" id="page-dashboard">
      <Header
        title="Dashboard"
        subtitle="Bot overview and metrics"
        isConnected={isConnected}
      />

      <div className="dashboard__content">
        <section className="dashboard__section">
          <h2 className="dashboard__section-title">Overview</h2>
          <MetricsPanel metrics={metrics} loading={metricsLoading} />
        </section>

        <section className="dashboard__section">
          <div className="dashboard__section-header">
            <h2 className="dashboard__section-title">Bots</h2>
            <span className="dashboard__section-count">
              {bots?.length || 0} registered
            </span>
          </div>

          {botsLoading ? (
            <div className="dashboard__grid">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bot-card bot-card--skeleton">
                  <div className="skeleton" style={{ width: '60%', height: 16 }} />
                  <div className="skeleton" style={{ width: '40%', height: 12 }} />
                  <div className="skeleton" style={{ width: '100%', height: 40 }} />
                  <div className="skeleton" style={{ width: '50%', height: 32 }} />
                </div>
              ))}
            </div>
          ) : bots && bots.length > 0 ? (
            <div className="dashboard__grid">
              {bots.map(bot => (
                <BotCard
                  key={bot.id}
                  bot={bot}
                  onRun={handleRun}
                  onStop={handleStop}
                />
              ))}
            </div>
          ) : (
            <div className="dashboard__empty">
              <p>No bots found. Make sure the API server is running and seeded.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
