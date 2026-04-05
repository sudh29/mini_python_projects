/**
 * App root — router + layout shell.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import BotDetail from './pages/BotDetail';
import Login from './pages/Login';
import { getAuthToken } from './services/api';
import './App.css';

function AppLayout() {
  const user = (() => {
    try {
      const stored = localStorage.getItem('rpa_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  })();

  return (
    <div className="app-layout">
      <Sidebar
        username={user?.username || 'admin@acme'}
        clientName="Acme Healthcare"
      />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bots/:id" element={<BotDetail />} />
          <Route path="/bots" element={<Dashboard />} />
          <Route path="/settings" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={<AppLayout />} />
      </Routes>
    </BrowserRouter>
  );
}
