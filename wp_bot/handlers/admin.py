import asyncio
import subprocess
import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_IDS, SERVICE_NAME

router = Router()

@router.message(Command("restart"))
async def restart_service(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    notice = await message.answer("♻️ Рестартую systemd сервис...")

    try:
        # ⏳ ждём и рестартим
        await asyncio.sleep(1)
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
        result_msg = "✅ Сервис успешно перезапущен."
    except Exception as e:
        logging.exception("Ошибка при рестарте systemd")
        result_msg = f"❌ Ошибка при перезапуске:\n<code>{e}</code>"

    # Удаляем "рестартую..." и отправляем результат
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=notice.message_id)
    except:
        pass  # вдруг оно уже удалено или недоступно

    await message.answer(result_msg, parse_mode="HTML")
