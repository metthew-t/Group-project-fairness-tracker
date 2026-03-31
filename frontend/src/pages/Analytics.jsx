import { useEffect, useState } from 'react';
import { analyticsAPI } from '../api/analytics';
import { teamsAPI } from '../api/teams';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import toast from 'react-hot-toast';
import './Page.css';

const COLORS = ['#6366f1', '#06b6d4', '#4ade80', '#fbbf24', '#f87171', '#a855f7'];

export default function Analytics() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await teamsAPI.list();
        setTeams(res.data);
        if (res.data.length > 0) setSelectedTeam(res.data[0].id);
      } catch { toast.error('Failed to load teams'); }
    };
    fetchTeams();
  }, []);

  useEffect(() => {
    if (!selectedTeam) return;
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const res = await analyticsAPI.team(selectedTeam);
        setData(res.data);
      } catch { toast.error('Failed to load analytics'); }
      finally { setLoading(false); }
    };
    fetchAnalytics();
  }, [selectedTeam]);

  const contributionChart = data?.contribution_stats || [
    { name: 'John', value: 40 },
    { name: 'Jane', value: 30 },
    { name: 'Bob', value: 20 },
    { name: 'Alice', value: 10 },
  ];

  const timelineData = data?.timeline_stats || [
    { date: '2024-03-01', John: 2, Jane: 3, Bob: 1, Alice: 4 },
    { date: '2024-03-02', John: 4, Jane: 2, Bob: 5, Alice: 1 },
    { date: '2024-03-03', John: 3, Jane: 5, Bob: 2, Alice: 3 },
    { date: '2024-03-04', John: 5, Jane: 3, Bob: 4, Alice: 2 },
  ];

  const imbalances = data?.imbalances || [
    { type: 'High Workload', member: 'Jane', severity: 'medium', message: 'Assigned to 5 tasks simultanously' },
    { type: 'Stalled Progress', member: 'Bob', severity: 'low', message: 'No contributions logged in last 48h' },
  ];

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics Dashboard</h1>
          <p className="page-subtitle">Visualizing team performance and fairness scores</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
             <button className="btn btn-secondary" onClick={async () => {
               if (!selectedTeam) return;
               try {
                 const res = await analyticsAPI.exportCSV(selectedTeam);
                 const url = window.URL.createObjectURL(new Blob([res.data]));
                 const link = document.createElement('a');
                 link.href = url;
                 link.setAttribute('download', `fairness_report_${selectedTeam}.csv`);
                 document.body.appendChild(link);
                 link.click();
                 toast.success('Report downloaded');
               } catch { toast.error('Failed to download report'); }
             }}>Export CSV</button>
            <select className="form-select" style={{ maxWidth: '240px' }} value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)}>
              {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
        </div>
      </div>

      {loading ? (
        <div className="skeleton" style={{ height: '400px', borderRadius: '16px' }} />
      ) : (
        <>
            <div className="grid-2">
            {/* Contribution Share (Pie) */}
            <div className="card">
                <div className="card-header"><h3>Contribution Distribution</h3></div>
                <div className="card-body" style={{ height: '320px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                    <Pie data={contributionChart} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
                        {contributionChart.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                    </PieChart>
                </ResponsiveContainer>
                </div>
            </div>

            {/* Timeline (Line) */}
            <div className="card">
                <div className="card-header"><h3>Performance Over Time</h3></div>
                <div className="card-body" style={{ height: '320px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timelineData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis dataKey="date" stroke="var(--text-tertiary)" fontSize={12} />
                        <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                        <Tooltip />
                        <Legend />
                        {Object.keys(timelineData[0]).filter(k => k !== 'date').map((k, i) => (
                            <Line key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={{ r: 4 }} />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
                </div>
            </div>
            </div>

            <div className="grid-2 mt-4">
                {/* Efficiency Bar Chart */}
                <div className="card">
                <div className="card-header"><h3>Team Efficiency Index</h3></div>
                <div className="card-body" style={{ height: '320px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={contributionChart}>
                        <XAxis dataKey="name" stroke="var(--text-tertiary)" fontSize={12} />
                        <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                        <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} />
                        <Bar dataKey="value" fill="url(#barGradient)" radius={[4, 4, 0, 0]} />
                        <defs>
                        <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#6366f1" stopOpacity={1} />
                            <stop offset="100%" stopColor="#06b6d4" stopOpacity={1} />
                        </linearGradient>
                        </defs>
                    </BarChart>
                    </ResponsiveContainer>
                </div>
                </div>

                {/* Fairness Alerts */}
                <div className="card">
                    <div className="card-header"><h3>Imbalance Warning Alerts</h3></div>
                    <div className="card-body">
                        {imbalances.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {imbalances.map((alert, i) => (
                                    <div key={i} className={`alert alert-${alert.severity || 'info'}`} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                        <div className="alert-icon">⚠️</div>
                                        <div className="alert-content">
                                            <div className="alert-title"><b>{alert.type}</b>: {alert.member}</div>
                                            <div className="alert-message">{alert.message}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-state" style={{ padding: '20px' }}>
                                <h3>No imbalances detected</h3>
                                <p>This team is working very fairly.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="card mt-4">
            <div className="card-header"><h3>Fairness Score: <span style={{ color: 'var(--primary)' }}>{data?.fairness_score || 85}%</span></h3></div>
            <div className="card-body">
                <p>This team has a <b>{data?.gini_coefficient < 0.2 ? 'Excellent' : 'Good'}</b> fairness rating. {data?.summary || 'The workload distribution is balanced and predictable. Individual effort aligns with the project timeline.'}</p>
                <div className="progress-bar mt-2" style={{ height: '12px' }}>
                    <div className="progress-fill" style={{ width: `${data?.fairness_score || 85}%` }} />
                </div>
            </div>
            </div>
        </>
      )}
    </div>
  );
}
