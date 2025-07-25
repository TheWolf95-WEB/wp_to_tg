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

    await message.answer("♻️ Перезапускай systemd сервис...")

    # Выполнить перезапуск с задержкой
    asyncio.create_task(_restart_and_report(message))


async def _restart_and_report(message: types.Message):
    await asyncio.sleep(1)

    cmd = f"sleep 1 && systemctl restart {SERVICE_NAME}"
    try:
        subprocess.Popen(["bash", "-c", cmd])
        await message.answer("✅ Сервер успешно перезапущен.")
    except Exception as e:
        logging.exception("Ошибка при перезапуске systemd")
        await message.answer(f"❌ Ошибка:\n<code>{e}</code>", parse_mode="HTML")
