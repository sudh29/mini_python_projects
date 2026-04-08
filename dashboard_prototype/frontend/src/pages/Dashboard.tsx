/**
 * Dashboard page — main overview with metrics and bot grid.
 */

import { useCallback } from 'react';
import Header from '../components/Header';
import MetricsPanel from '../components/MetricsPanel';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchBots, fetchMetrics } from '../services/api';
import './Dashboard.css';

export default function Dashboard() {
  const { refetch: refetchBots } = useApi(fetchBots);
  const { data: metrics, loading: metricsLoading, refetch: refetchMetrics } = useApi(fetchMetrics);

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    onStatusUpdate: useCallback(() => {
      refetchBots();
      refetchMetrics();
    }, [refetchBots, refetchMetrics]),
  });

  return (
    <div className="dashboard" id="page-dashboard">
      <Header
        title="Dashboard"
        subtitle="Bot overview and metrics"
        isConnected={isConnected}
      />

      <div className="dashboard__content">
        <section className="dashboard__section">
          <h2 className="dashboard__section-title">Revenue Cycle Overview</h2>
          <MetricsPanel metrics={metrics} loading={metricsLoading} />
        </section>

        <section className="dashboard__section dashboard__section--alert">
          <div className="dashboard__section-header">
            <h2 className="dashboard__section-title text-danger">Exceptions Requiring Review (HITL)</h2>
            <span className="dashboard__section-count alert-count">
              2 pending
            </span>
          </div>
          <div className="hitl-queue">
            <div className="hitl-item">
              <div className="hitl-item__details">
                <strong>Claim Denied - Missing Auth</strong>
                <span>Bot: Auth Verification #4521</span>
              </div>
              <button className="hitl-item__action">Review Now</button>
            </div>
            <div className="hitl-item">
              <div className="hitl-item__details">
                <strong>Payer Portal Timeout</strong>
                <span>Bot: Claims Submission #9910</span>
              </div>
              <button className="hitl-item__action">Review Now</button>
            </div>
          </div>
        </section>


      </div>
    </div>
  );
}
