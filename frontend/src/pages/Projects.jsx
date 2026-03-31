import { useEffect, useState } from 'react';
import { projectsAPI } from '../api/projects';
import { teamsAPI } from '../api/teams';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './Page.css';

const STATUS_COLORS = {
  active: 'badge-success',
  planning: 'badge-warning',
  completed: 'badge-info',
  archived: 'badge-neutral',
};

const PHASE_COLORS = {
  Proposal: 'badge-neutral',
  Development: 'badge-info',
  Review: 'badge-warning',
  Finalization: 'badge-success',
};

export default function Projects() {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editProject, setEditProject] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', team: '', deadline: '', phase: 'Proposal' });
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    try {
      const [p, t] = await Promise.all([projectsAPI.list(), teamsAPI.list()]);
      setProjects(p.data); setTeams(t.data);
    } catch { toast.error('Failed to load data'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setForm({ title: '', description: '', team: teams[0]?.id || '', deadline: '', phase: 'Proposal' });
    setEditProject(null);
    setShowCreate(true);
  };

  const openEdit = (p) => {
    setForm({ 
      title: p.title, 
      description: p.description || '', 
      team: p.team, 
      deadline: p.deadline || '',
      phase: p.phase || 'Proposal'
    });
    setEditProject(p);
    setShowCreate(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.team) { toast.error('Title and team are required'); return; }
    setSubmitting(true);
    try {
      if (editProject) {
        await projectsAPI.update(editProject.id, form);
        toast.success('Project updated!');
      } else {
        await projectsAPI.create(form);
        toast.success('Project created!');
      }
      setShowCreate(false);
      load();
    } catch (err) {
      toast.error(err.response?.data?.title?.[0] || 'Operation failed');
    } finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete project? This cannot be undone.')) return;
    try { await projectsAPI.delete(id); toast.success('Project deleted'); load(); }
    catch { toast.error('Failed to delete project'); }
  };

  const handleStatus = async (id, status) => {
    try { await projectsAPI.setStatus(id, status); toast.success('Status updated'); load(); }
    catch { toast.error('Failed to update status'); }
  };

  const handleDownloadMerged = async (id, title) => {
    try {
      const res = await projectsAPI.downloadMerged(id);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${title}_merged.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      toast.error('Failed to download merged project');
    }
  };

  return (
    <div className="page-content animate-fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">Projects</h1>
            <p className="page-subtitle">Track your team's project progress</p>
          </div>
          {user?.user_type !== 'STUDENT' && (
            <button className="btn btn-primary" onClick={openCreate}>+ New Project</button>
          )}
        </div>

      {loading ? (
        <div className="grid-3">
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '220px', borderRadius: '16px' }} />)}
        </div>
      ) : projects.length === 0 ? (
        <div className="empty-state card" style={{ padding: '80px 24px' }}>
          <div className="empty-state-icon">📁</div>
          <h3>No projects found</h3>
          <p>{user?.user_type === 'STUDENT' ? 'Your team lead hasn\'t started any projects yet.' : 'Create a project to start organizing your team\'s work.'}</p>
          {user?.user_type !== 'STUDENT' && (
            <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={openCreate}>Create Project</button>
          )}
        </div>
      ) : (
        <div className="grid-3">
          {projects.map((p) => (
            <div className="card feature-card animate-fade-in" key={p.id}>
              <div className="feature-card-header">
                <div className="feature-card-icon" style={{ background: 'rgba(6,182,212,0.15)', color: 'var(--accent-400)' }}>
                  📁
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <h4 className="feature-card-title">{p.title}</h4>
                        <span className={`badge ${PHASE_COLORS[p.phase] || 'badge-neutral'}`} style={{ fontSize: '0.65rem' }}>{p.phase}</span>
                    </div>
                  <p className="feature-card-sub">{p.description || 'No description'}</p>
                </div>
              </div>
              <div className="feature-card-body">
                <div className="feature-card-meta" style={{ marginBottom: '12px' }}>
                  <span className={`badge ${STATUS_COLORS[p.status.toLowerCase()] || 'badge-neutral'}`}>{p.status}</span>
                  {p.deadline && (
                    <span className="badge badge-neutral">📅 {new Date(p.deadline).toLocaleDateString()}</span>
                  )}
                </div>
                {user?.user_type !== 'STUDENT' && (
                  <div className="form-group">
                    <select className="form-select" value={p.status.toLowerCase()}
                      onChange={(e) => handleStatus(p.id, e.target.value)}
                      style={{ fontSize: '0.8rem', padding: '6px 10px' }}>
                      <option value="active">Active</option>
                      <option value="planning">Planning</option>
                      <option value="completed">Completed</option>
                      <option value="archived">Archived</option>
                    </select>
                  </div>
                )}
              </div>
              {user?.user_type !== 'STUDENT' && (
                <div className="feature-card-actions">
                  <button className="btn btn-secondary btn-sm" onClick={() => openEdit(p)}>Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>Delete</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editProject ? 'Edit Project' : 'Create New Project'}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Project Title *</label>
                  <input className="form-input" value={form.title} placeholder="e.g. API Redesign"
                    onChange={(e) => setForm(p => ({ ...p, title: e.target.value }))} autoFocus />
                </div>
                <div className="form-group">
                  <label className="form-label">Team *</label>
                  <select className="form-select" value={form.team}
                    onChange={(e) => setForm(p => ({ ...p, team: e.target.value }))}>
                    <option value="">Select a team</option>
                    {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Deadline</label>
                    <input className="form-input" type="date" value={form.deadline}
                      onChange={(e) => setForm(p => ({ ...p, deadline: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Phase</label>
                    <select className="form-select" value={form.phase}
                      onChange={(e) => setForm(p => ({ ...p, phase: e.target.value }))}>
                      <option value="Proposal">Proposal</option>
                      <option value="Development">Development</option>
                      <option value="Review">Review</option>
                      <option value="Finalization">Finalization</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-textarea" value={form.description}
                    placeholder="Describe the project..."
                    onChange={(e) => setForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? <><div className="spinner" /> Saving...</> : editProject ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
