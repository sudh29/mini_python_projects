import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, CheckCircle2, Moon, Sun } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import botLogo from '../assets/JORIE_BOT.png';
import companyLogo from '../assets/jorie.png';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Invalid credentials. Try admin / admin');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-container" id="page-login">
      {/* Visual / Branding Side */}
      <div className="login-showcase">
        <div className="login-showcase__content">
          <div className="login-showcase__logo">
            <img src={botLogo} alt="Jorie Bot" style={{ height: 320, objectFit: 'contain' }} />
          </div>

          <h1 className="login-showcase__title">
            Intelligent RPA Orchestration
          </h1>
          <p className="login-showcase__desc">
            Monitor, manage, and scale your automated workflows with real-time analytics and clinical-grade precision.
          </p>
          <ul className="login-showcase__features">
            <li><CheckCircle2 size={18} /> Real-time execution telemetry</li>
            <li><CheckCircle2 size={18} /> Automated exception handling</li>
            <li><CheckCircle2 size={18} /> Advanced performance metrics</li>
          </ul>
        </div>
        <div className="login-showcase__bg-elements">
          <div className="glow-orb orb-1"></div>
          <div className="glow-orb orb-2"></div>
        </div>
      </div>

      {/* Login Form Side */}
      <div className="login-form-side">
        <button className="theme-toggle-btn" onClick={toggleTheme} aria-label="Toggle theme">
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        <div className="login-form-wrapper">
          <div className="login-header">
            <img src={companyLogo} alt="Jorie AI" style={{ height: 200, marginBottom: '24px' }} />
            <h2>Welcome back</h2>
            <p>Please enter your details to sign in.</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && <div className="login-error">{error}</div>}

            <div className="form-group">
              <label htmlFor="username">Email or Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="admin"
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-wrapper">
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
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="form-options">
              <label className="remember-me">
                <input type="checkbox" />
                <span>Remember me</span>
              </label>
              <a href="#" className="forgot-password">Forgot password?</a>
            </div>

            <button type="submit" className="login-submit" disabled={loading}>
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
