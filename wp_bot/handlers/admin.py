from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_IDS, SERVICE_NAME

import subprocess

router = Router()

@router.message(Command("restart"))
async def restart_service(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
        await message.answer("♻️ Бот успешно перезапущен.")
    except subprocess.CalledProcessError as e:
        await message.answer(f"❌ Ошибка при перезапуске:\n<code>{e}</code>", parse_mode="HTML")
