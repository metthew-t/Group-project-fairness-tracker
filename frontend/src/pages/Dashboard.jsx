import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { teamsAPI } from '../api/teams';
import { projectsAPI } from '../api/projects';
import { tasksAPI } from '../api/tasks';
import { contributionsAPI } from '../api/contributions';
import { notificationsAPI } from '../api/notifications';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ teams: 0, projects: 0, tasks: 0, contributions: 0 });
  const [contributions, setContributions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teams, projects, tasks, contribs, notifs] = await Promise.allSettled([
          teamsAPI.list(), projectsAPI.list(), tasksAPI.list(),
          contributionsAPI.list(), notificationsAPI.list(),
        ]);
        setStats({
          teams: teams.value?.data?.length ?? 0,
          projects: projects.value?.data?.length ?? 0,
          tasks: tasks.value?.data?.length ?? 0,
          contributions: contribs.value?.data?.length ?? 0,
        });
        setContributions((contribs.value?.data || []).slice(0, 5));
        setNotifications((notifs.value?.data || []).filter((n) => !n.is_read).slice(0, 4));
      } catch {}
      finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  const statusBadge = (s) => {
    const map = {
      pending: 'badge-warning', approved: 'badge-success', rejected: 'badge-danger',
      active: 'badge-success', completed: 'badge-info', archived: 'badge-neutral',
    };
    return map[s] || 'badge-neutral';
  };

  return (
    <div className="dashboard animate-fade-in">
      {/* Header */}
      <div className="dashboard-hero">
        <div>
          <h1 className="page-title">
            {greeting}, <span className="gradient-text">{user?.username || 'there'}</span> 👋
          </h1>
          <p className="page-subtitle">Here's what's happening across your teams today.</p>
        </div>
        <div className="dashboard-hero-actions">
          <Link to="/dashboard/contributions" className="btn btn-primary">+ Log Contribution</Link>
          <Link to="/dashboard/projects" className="btn btn-secondary">View Projects</Link>
        </div>
      </div>

      {/* Stats */}
      {loading ? (
        <div className="grid-4">
          {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{ height: '140px' }} />)}
        </div>
      ) : (
        <div className="grid-4 dashboard-stats">
          <StatCard icon="👥" color="#6366f1" label="Teams" value={stats.teams} to="/dashboard/teams" />
          <StatCard icon="📁" color="#06b6d4" label="Projects" value={stats.projects} to="/dashboard/projects" />
          <StatCard icon="✅" color="#22c55e" label="Tasks" value={stats.tasks} to="/dashboard/tasks" />
          <StatCard icon="💡" color="#f59e0b" label="Contributions" value={stats.contributions} to="/dashboard/contributions" />
        </div>
      )}

      {/* Bottom grid */}
      <div className="dashboard-grid">
        {/* Recent Contributions */}
        <div className="card">
          <div className="card-header">
            <h3 style={{ fontSize: '1.05rem' }}>Recent Contributions</h3>
            <Link to="/dashboard/contributions" className="btn btn-ghost btn-sm">View all →</Link>
          </div>
          <div className="card-body" style={{ padding: '0' }}>
            {contributions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">💡</div>
                <h3>No contributions yet</h3>
                <p>Start logging your work contributions</p>
                <Link to="/dashboard/contributions" className="btn btn-primary btn-sm" style={{ marginTop: '12px' }}>
                  Add Contribution
                </Link>
              </div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {contributions.map((c) => (
                    <tr key={c.id}>
                      <td style={{ color: 'var(--text-primary)', maxWidth: '240px' }}>
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {c.description || 'Contribution'}
                        </div>
                      </td>
                      <td><span className={`badge ${statusBadge(c.status)}`}>{c.status}</span></td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>{c.hours_spent || 0}h</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Notifications */}
        <div className="card">
          <div className="card-header">
            <h3 style={{ fontSize: '1.05rem' }}>
              Unread Notifications
              {notifications.length > 0 && (
                <span className="badge badge-danger" style={{ marginLeft: '8px' }}>{notifications.length}</span>
              )}
            </h3>
            <Link to="/dashboard/notifications" className="btn btn-ghost btn-sm">View all →</Link>
          </div>
          <div className="card-body" style={{ padding: notifications.length ? '8px 0' : '24px' }}>
            {notifications.length === 0 ? (
              <div className="empty-state" style={{ padding: '40px 24px' }}>
                <div className="empty-state-icon">🔔</div>
                <h3>All caught up!</h3>
                <p>No unread notifications</p>
              </div>
            ) : (
              <div className="notif-list">
                {notifications.map((n) => (
                  <div className="notif-item" key={n.id}>
                    <div className="notif-dot" />
                    <div>
                      <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '2px' }}>
                        {n.message}
                      </p>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                        {new Date(n.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, color, label, value, to }) {
  return (
    <Link to={to} style={{ textDecoration: 'none' }}>
      <div className="stat-card" style={{ '--card-color': color }}>
        <div className="stat-icon" style={{ background: `${color}22`, color }}>
          {icon}
        </div>
        <div className="stat-value" style={{ color }}>{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </Link>
  );
}
