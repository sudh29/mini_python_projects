/**
 * Header bar component with connection status indicator.
 */

import { Wifi, WifiOff, Bell, Search } from 'lucide-react';
import './Header.css';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isConnected?: boolean;
}

export default function Header({ title, subtitle, isConnected = false }: HeaderProps) {
  return (
    <header className="header" id="header">
      <div className="header__left">
        <h1 className="header__title">{title}</h1>
        {subtitle && <span className="header__subtitle">{subtitle}</span>}
      </div>
      <div className="header__filters">
        <select className="header__select" defaultValue="all">
          <option value="all">All Clients</option>
          <option value="othone">Othone</option>
          <option value="gce">GCE</option>
          <option value="hampton">Hampton</option>
        </select>
        <select className="header__select" defaultValue="all">
          <option value="all">All Processes</option>
          <option value="ev">EV</option>
          <option value="preauth">Pre-Auth</option>
          <option value="payment">Payment Posting</option>
        </select>
      </div>
      <div className="header__right">
        <div className="header__search" id="header-search">
          <Search size={16} />
          <input type="text" placeholder="Search bots..." />
        </div>
        <button className="header__icon-btn" id="btn-notifications">
          <Bell size={18} />
          <span className="header__badge">3</span>
        </button>
        <div className={`header__connection ${isConnected ? 'header__connection--active' : ''}`}>
          {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
          <span>{isConnected ? 'Live' : 'Offline'}</span>
        </div>
      </div>
    </header>
  );
}
