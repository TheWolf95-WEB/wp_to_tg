import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from db import init_db
from handlers import connect, post, logs, common, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(connect.router)
    dp.include_router(post.router)
    dp.include_router(logs.router)
    dp.include_router(admin.router)  # ✅ подключение админских команд


    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
