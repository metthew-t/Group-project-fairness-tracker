import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function LoginPortal() {
  const { user } = useAuth();

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }
  return (
    <div className="auth-wrapper">
      <div className="auth-bg-glow" />
      <div className="auth-card animate-fade-in" style={{ maxWidth: '600px' }}>
        <div className="auth-logo">
          <div className="auth-logo-icon">⚖️</div>
          <div>
            <h1 className="auth-brand">FairnessTracker</h1>
            <p className="auth-tagline">Select your login portal</p>
          </div>
        </div>

        <h2 className="auth-title">Welcome</h2>
        <p className="auth-subtitle">Please select which account type you'd like to sign in with.</p>

        <div className="portal-grid">
          <Link to="/login?role=admin" className="portal-option">
            <div className="portal-icon">🏢</div>
            <div className="portal-info">
              <h3>Admin / Instructor</h3>
              <p>Manage teams, track overall progress, and review analytics.</p>
            </div>
            <div className="portal-arrow">→</div>
          </Link>

          <Link to="/login?role=member" className="portal-option">
            <div className="portal-icon">👥</div>
            <div className="portal-info">
              <h3>Team Member</h3>
              <p>Log your contributions, track tasks, and collaborate with your team.</p>
            </div>
            <div className="portal-arrow">→</div>
          </Link>
        </div>

        <div className="divider" style={{ margin: '32px 0' }} />
        
        <p className="auth-footer-text">
          New to FairnessTracker? <Link to="/register" className="auth-link">Create an account</Link>
        </p>
      </div>

      <style>{`
        .portal-grid {
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-top: 8px;
        }
        .portal-option {
          display: flex;
          align-items: center;
          gap: 20px;
          padding: 24px;
          background: var(--bg-elevated);
          border: 1px solid var(--border-default);
          border-radius: var(--border-radius-lg);
          text-decoration: none;
          transition: var(--transition-normal);
        }
        .portal-option:hover {
          transform: translateY(-2px);
          border-color: var(--primary-500);
          background: var(--bg-card);
          box-shadow: var(--shadow-md), 0 0 20px rgba(99,102,241,0.1);
        }
        .portal-icon {
          font-size: 2.5rem;
          width: 64px;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(99,102,241,0.1);
          border-radius: 12px;
          flex-shrink: 0;
        }
        .portal-info {
          flex: 1;
        }
        .portal-info h3 {
          font-size: 1.15rem;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        .portal-info p {
          font-size: 0.85rem;
          color: var(--text-tertiary);
          line-height: 1.4;
        }
        .portal-arrow {
          font-size: 1.5rem;
          color: var(--text-muted);
          transition: var(--transition-fast);
        }
        .portal-option:hover .portal-arrow {
          color: var(--primary-400);
          transform: translateX(4px);
        }
      `}</style>
    </div>
  );
}
