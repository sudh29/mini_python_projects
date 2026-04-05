/**
 * Sidebar navigation component.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  Activity,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useState } from 'react';
import { logout } from '../services/api';
import './Sidebar.css';

interface SidebarProps {
  username?: string;
  clientName?: string;
}

export default function Sidebar({ username = 'admin@acme', clientName = 'Acme Healthcare' }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <aside className={`sidebar ${collapsed ? 'sidebar--collapsed' : ''}`} id="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__logo">
          <Activity size={24} />
        </div>
        {!collapsed && (
          <div className="sidebar__brand-text">
            <span className="sidebar__title">RPA Control</span>
            <span className="sidebar__subtitle">{clientName}</span>
          </div>
        )}
        <button
          className="sidebar__toggle"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      <nav className="sidebar__nav">
        <NavLink to="/" end className="sidebar__link" id="nav-dashboard">
          <LayoutDashboard size={20} />
          {!collapsed && <span>Dashboard</span>}
        </NavLink>
        <NavLink to="/bots" className="sidebar__link" id="nav-bots">
          <Bot size={20} />
          {!collapsed && <span>Bots</span>}
        </NavLink>
        <NavLink to="/settings" className="sidebar__link" id="nav-settings">
          <Settings size={20} />
          {!collapsed && <span>Settings</span>}
        </NavLink>
      </nav>

      <div className="sidebar__footer">
        {!collapsed && (
          <div className="sidebar__user">
            <div className="sidebar__avatar">
              {username.charAt(0).toUpperCase()}
            </div>
            <span className="sidebar__username">{username}</span>
          </div>
        )}
        <button className="sidebar__logout" onClick={handleLogout} id="btn-logout">
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
