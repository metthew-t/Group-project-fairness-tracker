import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import toast from 'react-hot-toast';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/dashboard', icon: '🏠', label: 'Dashboard' },
  { to: '/dashboard/teams', icon: '👥', label: 'Teams' },
  { to: '/dashboard/projects', icon: '📁', label: 'Projects' },
  { to: '/dashboard/tasks', icon: '✅', label: 'Tasks' },
  { to: '/dashboard/contributions', icon: '💡', label: 'Contributions' },
  { to: '/dashboard/analytics', icon: '📊', label: 'Analytics' },
  { to: '/dashboard/notifications', icon: '🔔', label: 'Notifications' },
  { to: '/dashboard/profile', icon: '👤', label: 'Profile' },
];

export default function Sidebar({ collapsed, onCollapse }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch {
      navigate('/login');
    } finally {
      setLoggingOut(false);
    }
  };

  const initials = user?.username ? user.username.slice(0, 2).toUpperCase() : 'U';

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">⚖️</div>
        {!collapsed && (
          <div className="sidebar-brand-text">
            <span className="sidebar-brand-name">Fairness</span>
            <span className="sidebar-brand-sub">Tracker</span>
          </div>
        )}
        <button className="sidebar-collapse-btn" onClick={onCollapse} title={collapsed ? 'Expand' : 'Collapse'}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {[
          ...NAV_ITEMS.slice(0, 1),
          ...(user?.user_type === 'ADMIN' || user?.user_type === 'MANAGER' 
            ? [{ to: '/dashboard/admin', icon: '🏢', label: 'Admin Console' }] 
            : []),
          ...NAV_ITEMS.slice(1)
        ].map(({ to, icon, label }) => (
          <NavLink key={to} to={to} className="sidebar-link">
            <span className="sidebar-link-icon">{icon}</span>
            {!collapsed && <span className="sidebar-link-label">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="avatar">{initials}</div>
          {!collapsed && (
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user?.username || 'User'}</span>
              <span className="sidebar-user-email">{user?.email || ''}</span>
            </div>
          )}
        </div>
        <button
          className="sidebar-logout btn btn-ghost btn-icon"
          onClick={handleLogout}
          disabled={loggingOut}
          title="Logout"
        >
          {loggingOut ? <div className="spinner" /> : '🚪'}
        </button>
      </div>
    </aside>
  );
}
