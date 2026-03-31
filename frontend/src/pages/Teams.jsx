import { useEffect, useState } from 'react';
import { teamsAPI } from '../api/teams';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './Page.css';

function TeamCard({ team, onLeave, onDelete }) {
  const { user } = useAuth();
  const isCreator = team.created_by === user?.id;

  return (
    <div className="card feature-card animate-fade-in">
      <div className="feature-card-header">
        <div className="feature-card-icon" style={{ background: 'rgba(99,102,241,0.18)', color: 'var(--primary-400)' }}>
          👥
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h4 className="feature-card-title">{team.name}</h4>
          {team.description && (
            <p className="feature-card-sub" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {team.description}
            </p>
          )}
        </div>
      </div>
      <div className="feature-card-body">
        <div className="feature-card-meta">
          <span className="badge badge-primary">Code: {team.join_code}</span>
          {isCreator && <span className="badge badge-info">Owner</span>}
        </div>
      </div>
      <div className="feature-card-actions" style={{ display: 'flex', gap: '8px' }}>
        <button className="btn btn-primary btn-sm" onClick={() => window.location.href = `/dashboard/teams/${team.id}/chat`}>
          💬 Chat
        </button>
        {isCreator ? (
          <button className="btn btn-danger btn-sm" onClick={() => onDelete(team.id)}>Delete</button>
        ) : (
          <button className="btn btn-secondary btn-sm" onClick={() => onLeave(team.id)}>Leave</button>
        )}
      </div>
    </div>
  );
}

export default function Teams() {
  const { user } = useAuth();
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showJoin, setShowJoin] = useState(false);
  const [createForm, setCreateForm] = useState({ name: '', description: '' });
  const [joinCode, setJoinCode] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchTeams = async () => {
    try {
      const res = await teamsAPI.list();
      setTeams(res.data);
    } catch { toast.error('Failed to load teams'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchTeams(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!createForm.name) { toast.error('Team name required'); return; }
    setSubmitting(true);
    try {
      await teamsAPI.create(createForm);
      toast.success('Team created!');
      setShowCreate(false);
      setCreateForm({ name: '', description: '' });
      fetchTeams();
    } catch (err) {
      toast.error(err.response?.data?.name?.[0] || 'Failed to create team');
    } finally { setSubmitting(false); }
  };

  const handleJoin = async (e) => {
    e.preventDefault();
    if (!joinCode) { toast.error('Enter a join code'); return; }
    setSubmitting(true);
    try {
      await teamsAPI.join({ join_code: joinCode });
      toast.success('Joined team!');
      setShowJoin(false);
      setJoinCode('');
      fetchTeams();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to join team');
    } finally { setSubmitting(false); }
  };

  const handleLeave = async (id) => {
    if (!window.confirm('Leave this team?')) return;
    try {
      await teamsAPI.leave(id);
      toast.success('Left team');
      fetchTeams();
    } catch { toast.error('Failed to leave team'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this team? This cannot be undone.')) return;
    try {
      await teamsAPI.delete(id);
      toast.success('Team deleted');
      fetchTeams();
    } catch { toast.error('Failed to delete team'); }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Teams</h1>
          <p className="page-subtitle">Manage your teams and collaborations</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={() => setShowJoin(true)}>Join Team</button>
          {user?.user_type !== 'STUDENT' && (
            <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Team</button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="grid-3">
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '200px', borderRadius: '16px' }} />)}
        </div>
      ) : teams.length === 0 ? (
        <div className="empty-state card" style={{ padding: '80px 24px' }}>
          <div className="empty-state-icon">👥</div>
          <h3>No teams yet</h3>
          <p>{user?.user_type === 'STUDENT' ? 'Join a team using a code from your lead.' : 'Create a new team or join an existing one with a code.'}</p>
          <div className="flex gap-2" style={{ marginTop: '16px' }}>
            {user?.user_type !== 'STUDENT' && (
              <button className="btn btn-primary" onClick={() => setShowCreate(true)}>Create Team</button>
            )}
            <button className="btn btn-secondary" onClick={() => setShowJoin(true)}>Join with Code</button>
          </div>
        </div>
      ) : (
        <div className="grid-3">
          {teams.map((team) => (
            <TeamCard key={team.id} team={team} onLeave={handleLeave} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Team</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Team Name *</label>
                  <input className="form-input" value={createForm.name} placeholder="e.g. Backend Team"
                    onChange={(e) => setCreateForm(p => ({ ...p, name: e.target.value }))} autoFocus />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-textarea" value={createForm.description}
                    placeholder="What does this team work on?"
                    onChange={(e) => setCreateForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? <><div className="spinner" /> Creating...</> : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Modal */}
      {showJoin && (
        <div className="modal-overlay" onClick={() => setShowJoin(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Join a Team</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowJoin(false)}>✕</button>
            </div>
            <form onSubmit={handleJoin}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Join Code *</label>
                  <input className="form-input" value={joinCode} placeholder="6-digit code"
                    onChange={(e) => setJoinCode(e.target.value)} maxLength={6} autoFocus
                    style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', letterSpacing: '0.1em', textAlign: 'center' }} />
                  <span className="form-hint">Ask your team lead for the join code.</span>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowJoin(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? <><div className="spinner" /> Joining...</> : 'Join Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
