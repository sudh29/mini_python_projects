import { Bell, RefreshCw, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import './Header.css';

interface HeaderProps {
  title: string;
  subtitle?: string;
  isConnected?: boolean;
}

interface Notification {
  id: string;
  type: 'error' | 'success' | 'info';
  message: string;
  time: string;
  isRead: boolean;
}

const MOCK_NOTIFICATIONS: Notification[] = [
  { id: '1', type: 'error', message: 'Bot AO-CLM-0 has failed: Connection Timeout', time: '5m ago', isRead: false },
  { id: '2', type: 'success', message: 'Claims report generated successfully', time: '1h ago', isRead: false },
  { id: '3', type: 'info', message: 'System maintenance scheduled for 12:00 AM', time: '3h ago', isRead: true },
];

export default function Header({ title, subtitle }: HeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState(MOCK_NOTIFICATIONS);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showNotifications]);

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  };

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
        
        <div className="notifications-wrapper" ref={dropdownRef}>
          <button 
            className={`header__icon-btn ${showNotifications ? 'header__icon-btn--active' : ''}`} 
            id="btn-notifications"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell size={18} />
            {unreadCount > 0 && <span className="header__badge">{unreadCount}</span>}
          </button>

          {showNotifications && (
            <div className="notifications-dropdown">
              <div className="notifications-dropdown__header">
                <h3>Notifications</h3>
                <button onClick={markAllRead}>Mark all read</button>
              </div>
              <div className="notifications-dropdown__list">
                {notifications.length > 0 ? (
                  notifications.map(n => (
                    <div key={n.id} className={`notification-item ${n.isRead ? '' : 'notification-item--unread'}`}>
                      <div className={`notification-item__icon notification-item__icon--${n.type}`}>
                        {n.type === 'error' ? <AlertCircle size={14} /> : <CheckCircle2 size={14} />}
                      </div>
                      <div className="notification-item__content">
                        <p className="notification-item__msg">{n.message}</p>
                        <div className="notification-item__meta">
                          <Clock size={10} />
                          <span>{n.time}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="notifications-dropdown__empty">No notifications</div>
                )}
              </div>
              <div className="notifications-dropdown__footer">
                <button>View all activity</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

