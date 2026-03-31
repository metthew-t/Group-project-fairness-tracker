import { useEffect, useState } from 'react';
import { tasksAPI } from '../api/tasks';
import { projectsAPI } from '../api/projects';
import { teamsAPI } from '../api/teams';
import { contributionsAPI } from '../api/contributions';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './Page.css';

const PRIORITY_COLORS = { low: 'badge-neutral', medium: 'badge-warning', high: 'badge-danger' };
const STATUS_COLORS = { pending: 'badge-warning', in_progress: 'badge-info', done: 'badge-success' };

export default function Tasks() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showLog, setShowLog] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [form, setForm] = useState({ 
    title: '', 
    description: '', 
    project: '', 
    priority: 'MEDIUM', 
    deadline: '',
    estimated_effort: 1,
    assigned_to: []
  });
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState('all');

  const load = async () => {
    try {
      const [t, p] = await Promise.all([tasksAPI.list(), projectsAPI.list()]);
      setTasks(t.data); setProjects(p.data);
      
      // Fetch members for all involved teams (simplified for now)
      if (p.data.length > 0) {
        const teamIds = [...new Set(p.data.map(proj => proj.team))];
        const allMembers = await Promise.all(teamIds.map(id => teamsAPI.members(id)));
        setTeamMembers(allMembers.flatMap(res => res.data));
      }
    } catch { toast.error('Failed to load tasks'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const filteredTasks = filter === 'all' ? tasks : tasks.filter(t => t.status === filter);

  const openCreate = () => {
    setForm({ 
      title: '', 
      description: '', 
      project: projects[0]?.id || '', 
      priority: 'MEDIUM', 
      deadline: '',
      estimated_effort: 1,
      assigned_to: []
    });
    setEditTask(null);
    setShowCreate(true);
  };

  const openEdit = (task) => {
    setForm({ 
      title: task.title, 
      description: task.description || '', 
      project: task.project, 
      priority: task.priority || 'MEDIUM', 
      deadline: task.deadline || '',
      estimated_effort: task.estimated_effort || 1,
      assigned_to: task.assigned_to || []
    });
    setEditTask(task);
    setShowCreate(true);
  };

  const [contribForm, setContribForm] = useState({
    hours_spent: '', difficulty: 3, work_type: 'Coding', description: '', file: null
  });

  const handleLogContrib = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('task', selectedTask.id);
      formData.append('hours_spent', contribForm.hours_spent);
      formData.append('difficulty', contribForm.difficulty);
      formData.append('work_type', contribForm.work_type);
      formData.append('description', contribForm.description);
      if (contribForm.file) formData.append('proof_file', contribForm.file);

      await contributionsAPI.create(formData);
      toast.success('Contribution logged! Waiting for peer verification.');
      setShowLog(false);
      setContribForm({ hours_spent: '', difficulty: 3, work_type: 'Coding', description: '', file: null });
    } catch (err) {
      toast.error('Failed to log contribution');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.project) { toast.error('Title and project are required'); return; }
    setSubmitting(true);
    const payload = { ...form };
    if (!payload.deadline) payload.deadline = null;
    if (payload.assigned_to.length === 0) payload.assigned_to = [];
    payload.assigned_to = payload.assigned_to.map(id => parseInt(id, 10));

    try {
      if (editTask) { await tasksAPI.update(editTask.id, payload); toast.success('Task updated!'); }
      else { await tasksAPI.create(payload); toast.success('Task created!'); }
      setShowCreate(false);
      load();
    } catch (err) { 
        toast.error('Validation Error: ' + JSON.stringify(err.response?.data || err.message)); 
    }
    finally { setSubmitting(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this task?')) return;
    try { await tasksAPI.delete(id); toast.success('Task deleted'); load(); }
    catch { toast.error('Failed to delete task'); }
  };

  const handleStatusUpdate = async (id, currentStatus) => {
    const next = { TODO: 'IN_PROGRESS', IN_PROGRESS: 'COMPLETED', COMPLETED: 'TODO' };
    try { await tasksAPI.update(id, { status: next[currentStatus] || 'TODO' }); load(); }
    catch { toast.error('Failed to update status'); }
  };

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Tasks</h1>
          <p className="page-subtitle">Track and manage team tasks</p>
        </div>
        {user?.user_type !== 'STUDENT' && (
          <button className="btn btn-primary" onClick={openCreate}>+ New Task</button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="tabs" style={{ width: 'fit-content' }}>
        {['all', 'TODO', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED'].map(f => (
          <button key={f} className={`tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
            {f.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())}
            <span className="badge badge-neutral" style={{ marginLeft: '6px', fontSize: '0.7rem' }}>
              {f === 'all' ? tasks.length : tasks.filter(t => t.status === f).length}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '80px', borderRadius: '12px' }} />)}
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="empty-state card" style={{ padding: '60px 24px' }}>
          <div className="empty-state-icon">✅</div>
          <h3>No tasks found</h3>
          <p>{user?.user_type === 'STUDENT' ? 'Wait for your team lead to assign tasks.' : 'Create a task to assign work to your team members.'}</p>
          {user?.user_type !== 'STUDENT' && (
            <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={openCreate}>Create Task</button>
          )}
        </div>
      ) : (
        <div className="tasks-list">
          {filteredTasks.map((task) => (
            <div className="task-row card" key={task.id}>
              <button className="task-status-btn" onClick={() => handleStatusUpdate(task.id, task.status)}
                title="Click to advance status">
                <span className={`badge ${STATUS_COLORS[task.status.toLowerCase()] || 'badge-neutral'}`}>
                  {task.status?.replace('_', ' ') || 'TODO'}
                </span>
              </button>
              <div className="task-info">
                <span className="task-title">{task.title}</span>
                {task.description && <span className="task-desc">{task.description}</span>}
                <div className="assigned-avatars" style={{ display: 'flex', gap: '4px', marginTop: '8px' }}>
                  {task.assigned_to_details?.map(u => (
                    <div key={u.id} className="avatar avatar-sm" title={u.username}>
                      {u.username[0].toUpperCase()}
                    </div>
                  ))}
                </div>
              </div>
              <div className="task-meta">
                <span className={`badge ${PRIORITY_COLORS[task.priority.toLowerCase()] || 'badge-neutral'}`}>
                  {task.priority || 'medium'}
                </span>
                <span className="badge badge-primary">⚡ {task.estimated_effort} effort</span>
                {task.due_date && (
                  <span className="badge badge-neutral">📅 {new Date(task.due_date).toLocaleDateString()}</span>
                )}
              </div>
              <div className="task-actions">
                {user?.user_type === 'STUDENT' && (
                  <button className="btn btn-primary btn-sm" 
                    onClick={() => { setSelectedTask(task); setShowLog(true); }}>
                    Log Work
                  </button>
                )}
                {user?.user_type !== 'STUDENT' && (
                  <>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(task)} title="Edit">✏️</button>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => handleDelete(task.id)} title="Delete">🗑️</button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editTask ? 'Edit Task' : 'Create New Task'}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Title *</label>
                  <input className="form-input" value={form.title} placeholder="Task title"
                    onChange={e => setForm(p => ({ ...p, title: e.target.value }))} autoFocus />
                </div>
                <div className="form-group">
                  <label className="form-label">Project *</label>
                  <select className="form-select" value={form.project}
                    onChange={e => setForm(p => ({ ...p, project: e.target.value }))}>
                    <option value="">Select project</option>
                    {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
                  </select>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                   <div className="form-group">
                    <label className="form-label">Estimated Effort (1-10) *</label>
                    <input className="form-input" type="number" min="1" max="10" value={form.estimated_effort}
                      onChange={e => setForm(p => ({ ...p, estimated_effort: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Priority</label>
                    <select className="form-select" value={form.priority}
                      onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}>
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="CRITICAL">Critical</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                   <label className="form-label">Assigned To</label>
                   <select className="form-select" multiple value={form.assigned_to}
                     onChange={e => setForm(p => ({ ...p, assigned_to: Array.from(e.target.selectedOptions, o => o.value) }))}
                     style={{ height: '100px' }}>
                     {teamMembers.map(m => {
                       const u = m.user_details || {};
                       const displayName = u.first_name ? `${u.first_name} ${u.last_name || ''}`.trim() : u.username;
                       return (
                         <option key={u.id} value={u.id}>
                           {displayName} ({u.email}) - {m.role}
                         </option>
                       );
                     })}
                   </select>
                   <p className="form-hint">Hold Ctrl to select multiple</p>
                </div>
                <div className="form-group">
                  <label className="form-label">Due Date</label>
                  <input className="form-input" type="date" value={form.deadline}
                    onChange={e => setForm(p => ({ ...p, deadline: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-textarea" value={form.description}
                    placeholder="Describe the task..."
                    onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? <><div className="spinner" /> Saving...</> : editTask ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showLog && (
        <div className="modal-overlay" onClick={() => setShowLog(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Log Contribution for: {selectedTask?.title}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowLog(false)}>✕</button>
            </div>
            <form onSubmit={handleLogContrib}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Hours Spent *</label>
                    <input className="form-input" type="number" step="0.5" min="0.5" value={contribForm.hours_spent}
                      onChange={e => setContribForm(p => ({ ...p, hours_spent: e.target.value }))} autoFocus required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Difficulty (1-10) *</label>
                    <input className="form-input" type="number" min="1" max="10" value={contribForm.difficulty}
                      onChange={e => setContribForm(p => ({ ...p, difficulty: e.target.value }))} required />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Work Type</label>
                  <select className="form-select" value={contribForm.work_type}
                    onChange={e => setContribForm(p => ({ ...p, work_type: e.target.value }))}>
                    <option value="Coding">Coding</option>
                    <option value="Design">Design</option>
                    <option value="Research">Research</option>
                    <option value="Testing">Testing</option>
                    <option value="Documentation">Documentation</option>
                    <option value="Presentation">Presentation</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Proof of Work (PDF, Image, Doc)</label>
                  <input className="form-input" type="file" 
                    onChange={e => setContribForm(p => ({ ...p, file: e.target.files[0] }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Description / Merged Work Proof</label>
                  <textarea className="form-textarea" required value={contribForm.description}
                    placeholder="Describe exactly what you built, designed, or tested..."
                    onChange={e => setContribForm(p => ({ ...p, description: e.target.value }))} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowLog(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? <><div className="spinner" /> Submitting...</> : 'Submit Contribution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
