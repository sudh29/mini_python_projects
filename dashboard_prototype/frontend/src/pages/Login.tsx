/**
 * Login page — simple auth form.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Eye, EyeOff } from 'lucide-react';
import { login } from '../services/api';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await login(username, password);
      localStorage.setItem('rpa_user', JSON.stringify(res.user));
      navigate('/');
    } catch {
      setError('Invalid credentials. Try admin@acme / admin123');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page" id="page-login">
      <div className="login-card">
        <div className="login-card__header">
          <div className="login-card__logo">
            <Activity size={28} />
          </div>
          <h1>RPA Control</h1>
          <p>Sign in to your dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="login-card__form">
          {error && <div className="login-card__error">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="admin@acme"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="form-group__password">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                className="form-group__toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" className="login-card__submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="login-card__footer">
          <p>Demo: <code>admin@acme</code> / <code>admin123</code></p>
        </div>
      </div>
    </div>
  );
}
