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

    await message.answer("♻️ Рестартую systemd сервис...")

    # ⏱ даём время отправиться сообщению
    asyncio.create_task(_delayed_restart())

async def _delayed_restart():
    await asyncio.sleep(1)
    try:
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
    except Exception as e:
        logging.exception("Ошибка при рестарте systemd")
