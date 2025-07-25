from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import get_user_config, get_last_posts

router = Router()

@router.message(Command("profile"))
async def profile(message: Message):
    config = get_user_config(message.from_user.id)
    if not config:
        await message.answer("Сначала настройся через /connect.")
        return
    wp_url, wp_user, wp_pass, tg_channel, categories = config
    text = f"🌐 WordPress: {wp_url}\n👤 Логин: {wp_user}\n🔐 App Password: {wp_pass}\n📢 Канал: {tg_channel}"
    await message.answer(text)

@router.message(Command("logs"))
async def logs(message: Message):
    posts = get_last_posts(message.from_user.id)
    if not posts:
        await message.answer("Логи пусты.")
        return
    text = "📝 Последние публикации:\n"
    for title, link, published_at in posts:
        text += f"\n<b>{title}</b>\n{link}\n🕒 {published_at}\n"
    await message.answer(text, parse_mode="HTML")



@router.message(Command("stats"))
async def stats(message: Message):
    import sqlite3
    from config import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Всего пользователей
    cur.execute("SELECT COUNT(*) FROM wp_users")
    users_count = cur.fetchone()[0]

    # Всего постов
    cur.execute("SELECT COUNT(*) FROM post_logs")
    posts_count = cur.fetchone()[0]

    # Постов от текущего пользователя
    cur.execute("SELECT COUNT(*) FROM post_logs WHERE telegram_id = ?", (message.from_user.id,))
    user_posts = cur.fetchone()[0]

    conn.close()

    text = (
        f"📊 <b>Статистика</b>:\n"
        f"👤 Подключено пользователей: <b>{users_count}</b>\n"
        f"📝 Всего опубликовано постов: <b>{posts_count}</b>\n"
        f"📌 Ваши публикации: <b>{user_posts}</b>"
    )
    await message.answer(text, parse_mode="HTML")

