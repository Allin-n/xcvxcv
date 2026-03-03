import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function VictimsList() {
  const [victims, setVictims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchVictims();
    const interval = setInterval(fetchVictims, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchVictims = async () => {
    try {
      const response = await axios.get('/api/victims');
      setVictims(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching victims:', error);
    }
  };

  const filteredVictims = victims.filter(victim =>
    victim.victim_id.toLowerCase().includes(search.toLowerCase()) ||
    victim.hostname?.toLowerCase().includes(search.toLowerCase()) ||
    victim.country?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="loading">Loading victims...</div>;

  return (
    <div>
      <h1>📋 Victims List</h1>

      <div style={{ margin: '1rem 0' }}>
        <input
          type="text"
          placeholder="Search by ID, hostname, country..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '0.5rem',
            width: '300px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        />
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Victim ID</th>
              <th>Hostname</th>
              <th>IP Address</th>
              <th>Country</th>
              <th>Last Seen</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredVictims.map(victim => (
              <tr key={victim.victim_id}>
                <td>
                  <span className={`status-badge ${victim.is_online ? 'online' : 'offline'}`}>
                    {victim.is_online ? 'ONLINE' : 'OFFLINE'}
                  </span>
                </td>
                <td>{victim.victim_id.substring(0, 16)}...</td>
                <td>{victim.hostname || 'Unknown'}</td>
                <td>{victim.ip_address || 'Unknown'}</td>
                <td>{victim.country || 'Unknown'}</td>
                <td>{new Date(victim.last_seen).toLocaleString()}</td>
                <td>
                  <Link to={`/victim/${victim.victim_id}`}>
                    <button className="btn btn-primary">View</button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default VictimsList;