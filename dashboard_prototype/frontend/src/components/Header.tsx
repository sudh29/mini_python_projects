/**
 * Header bar component with page title and connection status.
 */

import { Bell, RefreshCw } from 'lucide-react';
import './Header.css';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isConnected?: boolean;
}

export default function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="header" id="header">
      <div className="header__left">
        <h1 className="header__title">{title}</h1>
        {subtitle && <span className="header__subtitle">{subtitle}</span>}
      </div>
      <div className="header__right">
        <div className="header__live-indicator">
          <span className="header__live-dot" />
          <span>Live</span>
        </div>
        <button className="header__icon-btn" id="btn-refresh" title="Refresh data">
          <RefreshCw size={16} />
        </button>
        <button className="header__icon-btn" id="btn-notifications">
          <Bell size={18} />
          <span className="header__badge">2</span>
        </button>
      </div>
    </header>
  );
}
