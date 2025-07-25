from aiogram import Router, F, types
from db import get_user_config, save_post_log
from wordpress import upload_featured_image, publish_post
from PIL import Image
from io import BytesIO
import sqlite3
from config import DB_PATH
import re

router = Router()

def remove_emoji(text):
    emoji_pattern = re.compile("[" 
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002700-\U000027BF"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()

def generate_description(text, max_length=150):
    text = remove_emoji(text)
    text = re.sub(r'\s+', ' ', text.strip())
    if len(text) <= max_length:
        return text
    cutoff = text[:max_length].rfind(' ')
    return text[:cutoff] + '...'

@router.message(F.photo & F.caption)
async def on_message(message: types.Message):
    user_id = message.from_user.id
    cfg = get_user_config(user_id)
    if not cfg:
        return

    wp_url, wp_user, wp_pass, tg_channel = cfg[:4]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute("SELECT wp_categories FROM wp_users WHERE telegram_id = ?", (user_id,)).fetchone()
    conn.close()

    if row and row[0]:
        cat_ids = list(map(int, row[0].split(",")))
    else:
        cat_ids = [5]

    tg_cfg = tg_channel.strip().lower()
    if tg_cfg.startswith('@'):
        if not message.chat.username or ('@' + message.chat.username.lower()) != tg_cfg:
            return
    else:
        if str(message.chat.id) != tg_cfg:
            return

    parts = message.caption.split("\n", 1)
    title = remove_emoji(parts[0].strip())
    content = parts[1].strip() if len(parts) > 1 else ""
    description = generate_description(content)

    buf = BytesIO()
    file_id = message.photo[-1].file_id
    await message.bot.download(file_id, destination=buf)
    buf.seek(0)

    img = Image.open(buf)
    jpeg_buf = BytesIO()
    img.save(jpeg_buf, format="JPEG")
    jpeg_buf.seek(0)

    media_id = upload_featured_image(jpeg_buf, f"{message.message_id}.jpg", wp_url, wp_user, wp_pass)

    link = publish_post(
        title=title,
        content=content,
        media_id=media_id,
        wp_url=wp_url,
        wp_user=wp_user,
        wp_pass=wp_pass,
        category_ids=cat_ids,
        description=description  # 👈 добавляем description
    )

    save_post_log(user_id, title, link)
    await message.bot.send_message(
        chat_id=user_id,
        text=f"✅ Пост опубликован на сайте!\n🔗 <a href='{link}'>Ссылка на пост</a>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )
