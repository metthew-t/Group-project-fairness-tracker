import { useEffect, useState } from 'react';
import { notificationsAPI } from '../api/notifications';
import toast from 'react-hot-toast';
import './Page.css';

export default function Notifications() {
  const [notifs, setNotifs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await notificationsAPI.list();
      setNotifs(res.data);
    } catch { toast.error('Failed to load notifications'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleMarkRead = async (id) => {
    try {
      await notificationsAPI.markRead(id);
      setNotifs(p => p.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsAPI.markAllRead();
      setNotifs(p => p.map(n => ({ ...n, is_read: true })));
      toast.success('All marked as read');
    } catch {}
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-subtitle">Stay updated on team activity</p>
        </div>
        <button className="btn btn-secondary" onClick={handleMarkAllRead}>Mark all read</button>
      </div>

      {loading ? (
        <div className="skeleton" style={{ height: '300px', borderRadius: '16px' }} />
      ) : notifs.length === 0 ? (
        <div className="empty-state card">
          <div className="empty-state-icon">🔔</div>
          <h3>All caught up</h3>
          <p>No notifications to show.</p>
        </div>
      ) : (
        <div className="card">
          <div className="notif-list">
            {notifs.map(n => (
              <div className={`notif-item ${n.is_read ? 'read' : 'unread'}`} key={n.id} onClick={() => !n.is_read && handleMarkRead(n.id)}>
                <div className={`notif-dot ${n.is_read ? 'invisible' : ''}`} />
                <div style={{ flex: 1 }}>
                  <p className="text-primary" style={{ marginBottom: '4px' }}>{n.message}</p>
                  <span className="text-tertiary text-xs">{new Date(n.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
