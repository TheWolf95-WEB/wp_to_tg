from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Привет! Введи /connect чтобы начать.")

@router.message(Command("help"))
async def help_cmd(message: Message):
    text = (
        "ℹ️ <b>Нужна помощь?</b>\n"
        "Если у вас возникли вопросы, предложения или что-то не работает — "
        "свяжитесь со мной: <a href='https://t.me/nd_admin95'>@nd_admin95</a>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("commands"))
async def commands_cmd(message: Message):
    text = (
        "<b>📘 Список команд:</b>\n"
        "/connect — подключить сайт WordPress\n"
        "/restart — рестарт сервера\n"
        "/edit_profile — изменить подключение\n"
        "/remove_site — удалить подключение\n"
        "/profile — посмотреть подключённый сайт\n"
        "/logs — последние публикации\n"
        "/stats — статистика публикаций\n"
        "/status — проверить работоспособность\n"
        "/help — поддержка\n"
        "/commands — список всех команд"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("status"))
async def status(message: Message):
    await message.answer("✅ Бот активен.")
