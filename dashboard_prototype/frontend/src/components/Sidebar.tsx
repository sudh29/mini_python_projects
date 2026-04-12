/**
 * Sidebar navigation component.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileBarChart,
  TrendingUp,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Activity,
  Moon,
  Sun,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { logout } from '../services/api';
import './Sidebar.css';

interface SidebarProps {
  username?: string;
}

export default function Sidebar({ username = 'admin@acme' }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark' || 
           (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

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
            <span className="sidebar__title">Board Monitor</span>
            <span className="sidebar__subtitle">Activity Dashboard</span>
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
        <NavLink to="/reports" className="sidebar__link" id="nav-reports">
          <FileBarChart size={20} />
          {!collapsed && <span>Reports</span>}
        </NavLink>
        <NavLink to="/trends" className="sidebar__link" id="nav-trends">
          <TrendingUp size={20} />
          {!collapsed && <span>Trends & Metrics</span>}
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
        <button className="sidebar__action" onClick={toggleTheme} id="btn-theme-toggle">
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
          {!collapsed && <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>}
        </button>
        <button className="sidebar__action sidebar__action--danger" onClick={handleLogout} id="btn-logout">
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
