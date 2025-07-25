import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "telegram_wp_users.db")
SERVICE_NAME = os.getenv("SERVICE_NAME", "wp_bot.service")
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "")

# 💡 Преобразуем строку в список чисел
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
