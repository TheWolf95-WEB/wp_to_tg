import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wp_users (
            telegram_id INTEGER PRIMARY KEY,
            wp_url TEXT,
            wp_username TEXT,
            wp_password TEXT,
            tg_channel TEXT,
            wp_categories TEXT  -- добавляем поле для категорий
        )
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS post_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        title TEXT,
        link TEXT,
        published_at TEXT
    )""")
    conn.commit()
    conn.close()

def save_user_config(tg_id, wp_url, wp_user, wp_pass, channel, categories):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        REPLACE INTO wp_users (telegram_id, wp_url, wp_username, wp_password, tg_channel, wp_categories)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tg_id, wp_url, wp_user, wp_pass, channel, categories))
    conn.commit()
    conn.close()


def get_user_config(tg_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT wp_url, wp_username, wp_password, tg_channel, wp_categories FROM wp_users WHERE telegram_id = ?", (tg_id,))
    row = cur.fetchone()
    conn.close()
    return row  # теперь возвращает 5 значений, не 4!


def save_post_log(user_id, title, link):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO post_logs (telegram_id, title, link, published_at)
        VALUES (?, ?, ?, datetime('now', 'localtime'))
    """, (user_id, title, link))
    conn.commit()
    conn.close()

def get_last_posts(user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT title, link, published_at FROM post_logs
        WHERE telegram_id = ?
        ORDER BY published_at DESC
        LIMIT ?
    """, (user_id, limit))
    posts = cur.fetchall()
    conn.close()
    return posts
