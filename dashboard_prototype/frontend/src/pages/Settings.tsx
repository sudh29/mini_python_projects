import { useState, useEffect } from 'react';
import Header from '../components/Header';
import { useAuth } from '../context/AuthContext';
import { 
  User, 
  Key, 
  Monitor, 
  ShieldCheck, 
  Heart,
  Copy,
  RefreshCw,
  Info
} from 'lucide-react';

import { checkHealth } from '../services/api';
import './Settings.css';

/**
 * Settings Page Component.
 * Unified interface for managing user profile, security keys, and UI preferences.
 */
export default function Settings() {
  const { user } = useAuth();
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unreachable' | 'checking'>('checking');
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  
  // Mock settings state
  const [notifications, setNotifications] = useState({
    email: true,
    browser: true,
    alerts: false
  });

  const [appearance, setAppearance] = useState({
    theme: localStorage.getItem('theme') || 'light',
    animations: true
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const status = await checkHealth();
        // Since health check logic in api.ts defaults to 'healthy' in demo, 
        // we'll treat it as such for the prototype.
        setHealthStatus(status.status === 'unreachable' ? 'unreachable' : 'healthy');
      } catch {
        setHealthStatus('unreachable');
      }
    };
    fetchHealth();
  }, []);

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText('acme-api-key-live-001');
    // In a real app, we'd use a toast notification here
  };

  return (
    <div className="settings-page" id="page-settings">
      <Header 
        title="Settings" 
        subtitle="Manage your profile and platform preferences" 
      />

      <div className="settings-content">
        {/* User Profile Section */}
        <section className="settings-section">
          <div className="settings-section__header">
            <User size={20} />
            <h2>User Profile</h2>
          </div>
          <div className="settings-card">
            <div className="profile-info">
              <div className="profile-info__avatar">
                {user?.username.charAt(0).toUpperCase() || 'A'}
              </div>
              <div className="profile-info__details">
                <div className="info-group">
                  <label>Full Name</label>
                  <span>{user?.username || 'Administrator'}</span>
                </div>
                <div className="info-group">
                  <label>Role</label>
                  <span className="role-badge">{user?.role || 'Admin'}</span>
                </div>
                <div className="info-group">
                  <label>Tenant ID</label>
                  <code>{user?.client_id || 'c1000...001'}</code>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* API & Integration Section */}
        <section className="settings-section">
          <div className="settings-section__header">
            <Key size={20} />
            <h2>API & Integrations</h2>
          </div>
          <div className="settings-card">
            <p className="card-desc">Authentication keys for programmatic access to the RPA Orchestration API.</p>
            <div className="api-key-manager">
              <div className="api-key-wrapper">
                <input 
                  type={apiKeyVisible ? 'text' : 'password'} 
                  value="acme-api-key-live-001" 
                  readOnly 
                />
                <button 
                  className="icon-btn" 
                  onClick={() => setApiKeyVisible(!apiKeyVisible)}
                  title="Toggle Visibility"
                >
                  <RefreshCw size={14} />
                </button>
              </div>
              <div className="api-key-actions">
                <button className="primary-btn" onClick={handleCopyApiKey}>
                  <Copy size={14} />
                  Copy Key
                </button>
                <button className="secondary-btn">Regenerate</button>
              </div>
            </div>
          </div>
        </section>

        {/* Preferences Section */}
        <section className="settings-section">
          <div className="settings-section__header">
            <Monitor size={20} />
            <h2>Platform Preferences</h2>
          </div>
          <div className="settings-grid">
            {/* Appearance Card */}
            <div className="settings-card">
              <h3>Appearance</h3>
              <div className="toggle-group">
                <div className="toggle-item">
                  <label>Interface Theme</label>
                  <select 
                    value={appearance.theme} 
                    onChange={(e) => setAppearance({...appearance, theme: e.target.value})}
                  >
                    <option value="light">Light Mode (Clinical)</option>
                    <option value="dark">Dark Mode (Performance)</option>
                  </select>
                </div>
                <div className="toggle-item">
                  <span>Enable Micro-animations</span>
                  <input 
                    type="checkbox" 
                    checked={appearance.animations} 
                    onChange={() => setAppearance({...appearance, animations: !appearance.animations})}
                  />
                </div>
              </div>
            </div>

            {/* Notifications Card */}
            <div className="settings-card">
              <h3>Notifications</h3>
              <div className="toggle-group">
                <div className="toggle-item">
                  <div className="toggle-label">
                    <span>Email Alerts</span>
                    <small>Get notified on bot failures</small>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={notifications.email} 
                    onChange={() => setNotifications({...notifications, email: !notifications.email})}
                  />
                </div>
                <div className="toggle-item">
                  <div className="toggle-label">
                    <span>System Toast Notifications</span>
                    <small>Direct browser feedback</small>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={notifications.browser} 
                    onChange={() => setNotifications({...notifications, browser: !notifications.browser})}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Security / About Section */}
        <section className="settings-section">
          <div className="settings-section__header">
            <ShieldCheck size={20} />
            <h2>Status & About</h2>
          </div>
          <div className="settings-card status-card">
            <div className="status-item">
              <div className="status-item__label">
                <Heart size={16} color={healthStatus === 'healthy' ? '#22c55e' : '#ef4444'} />
                <span>Backend Connectivity</span>
              </div>
              <span className={`status-badge status-badge--${healthStatus}`}>
                {healthStatus === 'healthy' ? 'Healthy' : 'Unreachable'}
              </span>
            </div>
            <div className="status-item footer-info">
              <Info size={14} />
              <span>Jorie AI RPA Orchestrator v0.1.0-prototype</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
