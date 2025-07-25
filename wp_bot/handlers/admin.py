from aiogram import Router, types
from aiogram.filters import Command
import subprocess
import logging
from config import ADMIN_IDS, SERVICE_NAME

router = Router()

@router.message(Command("restart"))
async def restart_bot(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("♻️ Рестартую сервис...")
    try:
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
    except Exception as e:
        logging.exception("Ошибка при рестарте systemd")
        await message.answer(f"❌ Ошибка: {e}")
