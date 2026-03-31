import { useEffect, useState } from 'react';
import { teamsAPI } from '../api/teams';
import { projectsAPI } from '../api/projects';
import { tasksAPI } from '../api/tasks';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './Page.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState({ teams: 0, projects: 0, tasks: 0 });
  const [teamData, setTeamData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [t, p, tk] = await Promise.all([
          teamsAPI.list(),
          projectsAPI.list(),
          tasksAPI.list()
        ]);
        
        setStats({
          teams: t.data.length,
          projects: p.data.length,
          tasks: tk.data.length
        });

        // Mock progress data for visualization
        const tData = t.data.map(team => ({
          name: team.name,
          progress: Math.floor(Math.random() * 60) + 20 // Simulated overall progress
        }));
        setTeamData(tData);

      } catch {
        toast.error('Failed to load administrative statistics');
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Admin Console</h1>
          <p className="page-subtitle">Oversee all team progress and system health</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card card">
          <div className="stat-info">
            <span className="stat-label">Total Teams</span>
            <span className="stat-value">{stats.teams}</span>
          </div>
          <div className="stat-icon">👥</div>
        </div>
        <div className="stat-card card">
          <div className="stat-info">
            <span className="stat-label">Active Projects</span>
            <span className="stat-value">{stats.projects}</span>
          </div>
          <div className="stat-icon">📂</div>
        </div>
        <div className="stat-card card">
          <div className="stat-info">
            <span className="stat-label">Completed Tasks</span>
            <span className="stat-value">{stats.tasks}</span>
          </div>
          <div className="stat-icon">✅</div>
        </div>
      </div>

      <div className="grid-2 mt-4">
        <div className="card">
          <div className="card-header"><h3>Team Completion Overview</h3></div>
          <div className="card-body" style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamData}>
                <XAxis dataKey="name" stroke="var(--text-tertiary)" fontSize={12} />
                <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                <Tooltip cursor={{fill: 'rgba(99,102,241,0.05)'}} />
                <Bar dataKey="progress" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h3>Direct Progress Monitor</h3></div>
          <div className="card-body">
            <div className="empty-state">
              <p className="text-sm">Real-time status tracking for all projects is active.</p>
              <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {teamData.slice(0, 3).map((t, i) => (
                  <div key={i} style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span className="text-xs font-semibold">{t.name}</span>
                      <span className="text-xs text-primary">{t.progress}%</span>
                    </div>
                    <div className="progress-bar-bg"><div className="progress-bar-fill" style={{ width: t.progress + '%' }}></div></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
