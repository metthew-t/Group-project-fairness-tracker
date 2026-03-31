import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../api/auth';
import toast from 'react-hot-toast';
import './Auth.css';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) { toast.error('Please enter your email.'); return; }
    setLoading(true);
    try {
      await authAPI.resetPasswordRequest(email);
      setSent(true);
      toast.success('Password reset email sent!');
    } catch (err) {
      toast.error(err.response?.data?.email?.[0] || 'Failed to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-bg-glow" />
      <div className="auth-card animate-fade-in">
        <div className="auth-logo">
          <div className="auth-logo-icon">⚖️</div>
          <div>
            <h1 className="auth-brand">FairnessTracker</h1>
            <p className="auth-tagline">Balanced collaboration, measured fairly</p>
          </div>
        </div>

        {sent ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📬</div>
            <h2 className="auth-title">Check your email</h2>
            <p className="auth-subtitle">
              We sent a password reset link to <strong style={{ color: 'var(--primary-400)' }}>{email}</strong>.
              Check your inbox and follow the instructions.
            </p>
            <div style={{ marginTop: '28px' }}>
              <Link to="/login" className="btn btn-secondary btn-full">Back to Login</Link>
            </div>
          </div>
        ) : (
          <>
            <h2 className="auth-title">Reset password</h2>
            <p className="auth-subtitle">Enter your email and we'll send you a reset link.</p>
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input className="form-input" type="email" placeholder="your@email.com"
                  value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
              </div>
              <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
                {loading ? <><div className="spinner" /> Sending...</> : 'Send Reset Link →'}
              </button>
            </form>
            <div style={{ marginTop: '24px', textAlign: 'center' }}>
              <Link to="/login" className="auth-link">← Back to Login</Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
