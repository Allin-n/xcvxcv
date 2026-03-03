import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    fetchStats();
    fetchRecentActivity();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchRecentActivity = async () => {
    try {
      const response = await axios.get('/api/recent-activity');
      setRecentActivity(response.data);
    } catch (error) {
      console.error('Error fetching recent activity:', error);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  const countryData = Object.entries(stats.countries).map(([name, value]) => ({ name, value }));

  const timelineData = [
    { date: 'Mon', victims: 4, logs: 23 },
    { date: 'Tue', victims: 7, logs: 45 },
    { date: 'Wed', victims: 12, logs: 78 },
    { date: 'Thu', victims: 15, logs: 92 },
    { date: 'Fri', victims: 18, logs: 110 },
    { date: 'Sat', victims: 22, logs: 135 },
    { date: 'Sun', victims: 25, logs: 150 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="dashboard">
      <h1>📊 Dashboard</h1>

      <div className="stats-cards">
        <div className="stat-card">
          <h3>Total Victims</h3>
          <p className="stat-value">{stats.total_victims}</p>
        </div>
        <div className="stat-card">
          <h3>Online Now</h3>
          <p className="stat-value">{stats.online_victims}</p>
        </div>
        <div className="stat-card">
          <h3>Total Logs</h3>
          <p className="stat-value">{stats.total_logs}</p>
        </div>
        <div className="stat-card">
          <h3>Total Files</h3>
          <p className="stat-value">{stats.total_files}</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h2>Victims Timeline</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="victims" stroke="#8884d8" strokeWidth={2} />
              <Line type="monotone" dataKey="logs" stroke="#82ca9d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h2>Victims by Country</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={countryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={entry => entry.name}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {countryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-container">
        <h2>Recent Activity</h2>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Victim</th>
              <th>Type</th>
              <th>Content</th>
            </tr>
          </thead>
          <tbody>
            {recentActivity.map((activity, i) => (
              <tr key={i}>
                <td>{new Date(activity.timestamp).toLocaleString()}</td>
                <td>{activity.victim_id}</td>
                <td>{activity.type}</td>
                <td>{activity.content}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;