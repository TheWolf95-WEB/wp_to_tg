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
    asyncio.create_task(_delayed_restart(message, notice.message_id))

async def _delayed_restart(message: types.Message, message_id: int):
    await asyncio.sleep(1)

    try:
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        await message.answer("✅ Сервер успешно перезапущен.")
    except Exception as e:
        logging.exception("Ошибка при рестарте systemd")
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        await message.answer(
            f"❌ Ошибка при перезапуске:\n<code>{e}</code>",
            parse_mode="HTML"
        )
