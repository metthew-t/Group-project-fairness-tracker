import { useEffect, useState } from 'react';
import { contributionsAPI } from '../api/contributions';
import { tasksAPI } from '../api/tasks';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import Certificate from '../components/Certificate';
import './Page.css';

export default function Contributions() {
  const { user } = useAuth();
  const [contributions, setContributions] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedCert, setSelectedCert] = useState(null);
  const [form, setForm] = useState({ 
    task: '', 
    description: '', 
    hours_spent: '',
    work_type: 'Coding',
    difficulty: 3,
    proof_file: null
  });
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    try {
      const [c, t] = await Promise.all([contributionsAPI.list(), tasksAPI.list()]);
      setContributions(c.data);
      setTasks(t.data);
    } catch { toast.error('Failed to load contributions'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.task || !form.description || !form.hours_spent) {
      toast.error('Required fields: Task, Description, Hours');
      return;
    }
    setSubmitting(true);
    
    // Use FormData for file upload
    const formData = new FormData();
    formData.append('task', form.task);
    formData.append('description', form.description);
    formData.append('hours_spent', form.hours_spent);
    formData.append('work_type', form.work_type);
    formData.append('difficulty', form.difficulty);
    if (form.proof_file) {
      formData.append('proof_file', form.proof_file);
    }

    try {
      await contributionsAPI.create(formData);
      toast.success('Contribution logged!');
      setShowCreate(false);
      setForm({ task: '', description: '', hours_spent: '', work_type: 'Coding', difficulty: 3, proof_file: null });
      load();
    } catch (err) {
      toast.error('Failed to log contribution');
    } finally { setSubmitting(false); }
  };

  const statusBadge = (s) => {
    const map = { pending: 'badge-warning', approved: 'badge-success', rejected: 'badge-danger' };
    return map[s] || 'badge-neutral';
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Contributions</h1>
          <p className="page-subtitle">Track and verify team effort fairly</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Log Contribution</button>
      </div>

      {loading ? (
        <div className="skeleton" style={{ height: '300px', borderRadius: '16px' }} />
      ) : contributions.length === 0 ? (
        <div className="empty-state card">
          <div className="empty-state-icon">💡</div>
          <h3>No contributions yet</h3>
          <p>Start logging your work hours and activities.</p>
          <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => setShowCreate(true)}>
            Add Contribution
          </button>
        </div>
      ) : (
        <div className="card" style={{ overflow: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Type</th>
                <th>Contributor</th>
                <th>Description</th>
                <th>Hours</th>
                <th>Diff</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {contributions.map((c) => (
                <tr key={c.id}>
                  <td>{c.task_title || `Task #${c.task}`}</td>
                  <td><span className="badge badge-neutral">{c.work_type}</span></td>
                  <td>{c.username || 'User'}</td>
                  <td>{c.description}</td>
                  <td>{c.hours_spent}h</td>
                  <td>{'⭐'.repeat(c.difficulty)}</td>
                  <td><span className={`badge ${statusBadge(c.status)}`}>{c.status}</span></td>
                  <td style={{ display: 'flex', gap: '4px' }}>
                    {(c.proof_file || c.file_upload) && (
                      <a href={c.proof_file || c.file_upload} target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm" title="View Proof">📎</a>
                    )}
                    {c.status === 'approved' && (
                      <button className="btn btn-ghost btn-sm" onClick={() => setSelectedCert(c)} title="View Certificate">🏆</button>
                    )}
                    {c.status === 'pending' && c.user !== user.id && (
                       <button className="btn btn-ghost btn-sm" 
                         onClick={async () => {
                           try {
                             await contributionsAPI.verify(c.id, { decision: 'approved', comments: 'Peer verified' });
                             toast.success('Verification recorded');
                             load();
                           } catch (err) { toast.error('Verification failed: ' + JSON.stringify(err.response?.data || err.message)); }
                         }}>Peer Verify</button>
                    )}
                    {c.status === 'pending' && user?.user_type !== 'STUDENT' && (
                      <div className="flex gap-1">
                        <button className="btn btn-success btn-sm" 
                          onClick={async () => {
                            if (!window.confirm('Approve this contribution?')) return;
                            try {
                              await contributionsAPI.lead_action(c.id, { decision: 'approved' });
                              toast.success('Contribution Approved');
                              load();
                            } catch (err) { toast.error('Action failed: ' + JSON.stringify(err.response?.data || err.message)); }
                          }}>Approve</button>
                        <button className="btn btn-danger btn-sm" 
                          onClick={async () => {
                            if (!window.confirm('Reject this contribution?')) return;
                            try {
                              await contributionsAPI.lead_action(c.id, { decision: 'rejected' });
                              toast.success('Contribution Rejected');
                              load();
                            } catch (err) { toast.error('Action failed: ' + JSON.stringify(err.response?.data || err.message)); }
                          }}>Reject</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Log Contribution</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Task *</label>
                  <select className="form-select" value={form.task} onChange={e => setForm(p => ({ ...p, task: e.target.value }))}>
                    <option value="">Select a task</option>
                    {tasks.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
                  </select>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Work Type *</label>
                    <select className="form-select" value={form.work_type} onChange={e => setForm(p => ({ ...p, work_type: e.target.value }))}>
                      <option value="Coding">Coding</option>
                      <option value="Research">Research</option>
                      <option value="Design">Design</option>
                      <option value="Documentation">Documentation</option>
                      <option value="Testing">Testing</option>
                      <option value="Presentation">Presentation</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Difficulty (1-5) *</label>
                    <input className="form-input" type="number" min="1" max="5" value={form.difficulty}
                      onChange={e => setForm(p => ({ ...p, difficulty: e.target.value }))} />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Description *</label>
                  <textarea className="form-textarea" placeholder="What did you work on?"
                    value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Hours Spent *</label>
                    <input className="form-input" type="number" step="0.5" placeholder="e.g. 2.5"
                      value={form.hours_spent} onChange={e => setForm(p => ({ ...p, hours_spent: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Proof File</label>
                    <input className="form-input" type="file" onChange={e => setForm(p => ({ ...p, proof_file: e.target.files[0] }))}
                      style={{ padding: '8px' }} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? <div className="spinner" /> : 'Log Effort'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {selectedCert && <Certificate contribution={selectedCert} onClose={() => setSelectedCert(null)} />}
    </div>
  );
}
