import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './Auth.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const queryParams = new URLSearchParams(location.search);
  const role = queryParams.get('role');
  const isManager = role === 'admin' || role === 'manager';

  const roleTitle = isManager ? 'Manager Portal' : 'Member Portal';
  const roleSubtitle = isManager 
    ? 'Access administrative tools and team analytics'
    : 'Track your contributions and collaborate';

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) { setError('Please fill in all fields.'); return; }
    setLoading(true);
    try {
      await login(form);
      toast.success('Welcome back! 🎉');
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.error || 'Invalid credentials. Please try again.';
      setError(msg);
      toast.error('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-bg-glow" />
      <div className="auth-card animate-fade-in">
        {/* Logo */}
        <div className="auth-logo">
          <div className="auth-logo-icon">⚖️</div>
          <div>
            <h1 className="auth-brand">FairnessTracker</h1>
            <p className="auth-tagline">Balanced collaboration, measured fairly</p>
          </div>
        </div>

        {/* Back to portal */}
        <Link to="/" className="auth-link" style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          ← Back to selection
        </Link>

        <h2 className="auth-title">{roleTitle}</h2>
        <p className="auth-subtitle">{roleSubtitle}</p>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '16px' }}>
            <span>⚠️</span> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              className={`form-input ${error ? 'error' : ''}`}
              type="text"
              name="username"
              placeholder="Enter your username"
              value={form.username}
              onChange={handleChange}
              autoFocus
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className={`form-input ${error ? 'error' : ''}`}
              type="password"
              name="password"
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
            />
          </div>

          <div className="auth-forgot">
            <Link to="/forgot-password" className="auth-link">Forgot password?</Link>
          </div>

          <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
            {loading ? <><div className="spinner" /> Signing in...</> : 'Sign In →'}
          </button>
        </form>

        <div className="divider-with-text" style={{ margin: '24px 0' }}>OR</div>

        <p className="auth-footer-text">
          Don't have an account? {' '}
          <Link to="/register" className="auth-link">Create one free</Link>
        </p>
      </div>
    </div>
  );
}
