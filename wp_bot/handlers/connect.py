from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from db import save_user_config
from wordpress import get_all_categories
import re, sqlite3
from config import DB_PATH

router = Router()

class UserConnect(StatesGroup):
    waiting_for_url = State()
    waiting_for_user = State()
    waiting_for_pass = State()
    waiting_for_channel = State()
    waiting_for_categories = State()

class EditProfile(StatesGroup):
    waiting_for_url = State()
    waiting_for_user = State()
    waiting_for_pass = State()
    waiting_for_channel = State()
    waiting_for_categories = State()

# --- Валидация ---
def is_valid_url(url):
    return re.match(r'^https?://[\w\.-]+', url)

def is_valid_username(username):
    return len(username) > 2

def is_valid_app_password(password):
    return len(password) >= 16

def is_valid_channel(channel):
    return channel.startswith('@') or re.match(r'^-\d+$', channel)

# --- Категории (выбор по ID) ---
def build_category_keyboard(categories, prefix):
    buttons = []
    for cat in categories:
        if cat['id'] == 5:
            continue  # исключаем категорию "Новости" по ID
        callback_data = f"{prefix}{cat['id']}"
        if len(callback_data.encode('utf-8')) <= 64:
            buttons.append([InlineKeyboardButton(text=cat['name'], callback_data=callback_data)])
    buttons.append([InlineKeyboardButton(text="✅ Готово", callback_data=f"{prefix}done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Команда /connect ---
@router.message(Command("connect"))
async def connect_cmd(message: Message, state: FSMContext):
    await message.answer("\U0001F310 Введи URL сайта WordPress (https://example.com):")
    await state.set_state(UserConnect.waiting_for_url)

@router.message(UserConnect.waiting_for_url)
async def get_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not is_valid_url(url):
        return await message.answer("\u274C Неверный URL. Пример: https://example.com")
    await state.update_data(url=url)
    await message.answer("\U0001F464 Введи логин WordPress:")
    await state.set_state(UserConnect.waiting_for_user)

@router.message(UserConnect.waiting_for_user)
async def get_user(message: Message, state: FSMContext):
    user = message.text.strip()
    if not is_valid_username(user):
        return await message.answer("\u274C Логин слишком короткий.")
    await state.update_data(user=user)
    await message.answer("\U0001F510 Введи App Password WordPress:")
    await state.set_state(UserConnect.waiting_for_pass)

@router.message(UserConnect.waiting_for_pass)
async def get_pass(message: Message, state: FSMContext):
    passwd = message.text.strip()
    if not is_valid_app_password(passwd):
        return await message.answer("\u274C Неверный App Password.")
    await state.update_data(passwd=passwd)
    await message.answer("\U0001F4E2 Введи username канала или ID группы (например, @mychannel):")
    await state.set_state(UserConnect.waiting_for_channel)

@router.message(UserConnect.waiting_for_channel)
async def get_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    if not is_valid_channel(channel):
        return await message.answer("\u274C Неверный канал.")
    await state.update_data(channel=channel)
    data = await state.get_data()
    try:
        categories = [
            cat for cat in get_all_categories(data['url'], data['user'], data['passwd'])
            if cat.get("parent")
        ]
    except Exception as e:
        await state.clear()
        return await message.answer(f"\u26A0\uFE0F Не удалось получить категории: {e}")
    keyboard = build_category_keyboard(categories, prefix="cat_connect_")
    await message.answer(
        "<b>📂 По умолчанию пост публикуется в категорию 'Новости'.</b>\nВыбери подкатегории (можно несколько):",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(UserConnect.waiting_for_categories)

@router.callback_query(F.data.startswith("cat_connect_"))
async def select_category_connect(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("cat_connect_", "")
    data = await state.get_data()
    selected = list(data.get("categories", []))
    
    if cat_id == "done":
        if not selected:  # Если ничего не выбрано, добавляем "Новости" по умолчанию
            selected.append("5")
        
        # Сохраняем конфигурацию
        save_user_config(
            tg_id=callback.from_user.id,
            wp_url=data['url'],
            wp_user=data['user'],
            wp_pass=data['passwd'],
            channel=data['channel'],
            categories=','.join(selected)
        )
        
        # Формируем список названий выбранных категорий
        try:
            all_categories = get_all_categories(data['url'], data['user'], data['passwd'])
            selected_names = [
                cat['name'] for cat in all_categories 
                if str(cat['id']) in selected
            ]
            categories_list = "\n".join(f"• {name}" for name in selected_names)
        except Exception:
            categories_list = ", ".join(selected)
        
        await state.clear()
        await callback.message.edit_reply_markup()
        return await callback.message.edit_text(
            f"✅ <b>Подключение завершено!</b>\n\n"
            f"<b>Выбранные категории:</b>\n{categories_list}\n\n"
            f"Теперь вы можете публиковать посты в эти категории.",
            parse_mode="HTML"
        )

    # Обновляем список выбранных категорий
    if cat_id in selected:
        selected.remove(cat_id)
    else:
        selected.append(cat_id)
    
    await state.update_data(categories=selected)
    
    # Формируем текст с выбранными категориями
    if selected:
        try:
            all_categories = get_all_categories(data['url'], data['user'], data['passwd'])
            selected_names = [
                cat['name'] for cat in all_categories 
                if str(cat['id']) in selected
            ]
            selection_text = "✅ <b>Выбрано:</b>\n" + "\n".join(f"• {name}" for name in selected_names)
        except Exception:
            selection_text = f"✅ Выбраны ID: {', '.join(selected)}"
    else:
        selection_text = "ℹ️ Пока ничего не выбрано"
    
    await callback.answer()
    await callback.message.edit_text(
        text=f"<b>📂 Выберите подкатегории (можно несколько):</b>\n\n"
             f"{selection_text}\n\n"
             f"Нажмите <b>✅ Готово</b> когда закончите выбор.",
        reply_markup=build_category_keyboard(
            [cat for cat in get_all_categories(data['url'], data['user'], data['passwd']) if cat.get("parent")],
            prefix="cat_connect_"
        ),
        parse_mode="HTML"
    )

# --- Команда /edit_profile ---
@router.message(Command("edit_profile"))
async def edit_profile(message: Message, state: FSMContext):
    await message.answer("\U0001F310 Введите новый URL сайта WordPress:")
    await state.set_state(EditProfile.waiting_for_url)

@router.message(EditProfile.waiting_for_url)
async def edit_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not is_valid_url(url):
        return await message.answer("\u274C Неверный URL.")
    await state.update_data(url=url)
    await message.answer("\U0001F464 Введите логин:")
    await state.set_state(EditProfile.waiting_for_user)

@router.message(EditProfile.waiting_for_user)
async def edit_user(message: Message, state: FSMContext):
    user = message.text.strip()
    if not is_valid_username(user):
        return await message.answer("\u274C Логин слишком короткий.")
    await state.update_data(user=user)
    await message.answer("\U0001F510 Введите App Password:")
    await state.set_state(EditProfile.waiting_for_pass)

@router.message(EditProfile.waiting_for_pass)
async def edit_pass(message: Message, state: FSMContext):
    passwd = message.text.strip()
    if not is_valid_app_password(passwd):
        return await message.answer("\u274C Неверный App Password.")
    await state.update_data(passwd=passwd)
    await message.answer("\U0001F4E2 Введите username канала или ID:")
    await state.set_state(EditProfile.waiting_for_channel)

@router.message(EditProfile.waiting_for_channel)
async def edit_channel(message: Message, state: FSMContext):
    channel = message.text.strip()
    if not is_valid_channel(channel):
        return await message.answer("\u274C Неверный формат канала.")
    await state.update_data(channel=channel)
    data = await state.get_data()
    try:
        categories = get_all_categories(data['url'], data['user'], data['passwd'])
    except Exception as e:
        await state.clear()
        return await message.answer(f"\u26A0\uFE0F Не удалось получить категории: {e}")
    keyboard = build_category_keyboard(categories, prefix="cat_edit_")
    await message.answer(
    "<b>📂 По умолчанию пост публикуется в категорию 'Новости'.</b>\nВыбери подкатегории (можно несколько):",
    reply_markup=keyboard,
    parse_mode="HTML"
    )

    await state.set_state(EditProfile.waiting_for_categories)

@router.callback_query(F.data.startswith("cat_edit_"))
async def edit_category(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("cat_edit_", "")
    data = await state.get_data()
    selected = list(data.get("categories", []))
    
    if cat_id == "done":
        if not selected:  # Если ничего не выбрано, добавляем "Новости" по умолчанию
            selected.append("5")
        
        # Сохраняем конфигурацию
        save_user_config(
            tg_id=callback.from_user.id,
            wp_url=data['url'],
            wp_user=data['user'],
            wp_pass=data['passwd'],
            channel=data['channel'],
            categories=','.join(selected)
        )
        
        # Формируем список названий выбранных категорий
        try:
            all_categories = get_all_categories(data['url'], data['user'], data['passwd'])
            selected_names = [
                cat['name'] for cat in all_categories 
                if str(cat['id']) in selected
            ]
            categories_list = "\n".join(f"• {name}" for name in selected_names)
        except Exception:
            categories_list = ", ".join(selected)
        
        await state.clear()
        await callback.message.edit_reply_markup()
        return await callback.message.edit_text(
            f"✅ <b>Профиль успешно обновлен!</b>\n\n"
            f"<b>Теперь посты будут публиковаться в:</b>\n{categories_list}",
            parse_mode="HTML"
        )

    # Обновляем список выбранных категорий
    if cat_id in selected:
        selected.remove(cat_id)
    else:
        selected.append(cat_id)
    
    await state.update_data(categories=selected)
    
    # Формируем текст с выбранными категориями
    if selected:
        try:
            all_categories = get_all_categories(data['url'], data['user'], data['passwd'])
            selected_names = [
                cat['name'] for cat in all_categories 
                if str(cat['id']) in selected
            ]
            selection_text = "✅ <b>Выбрано:</b>\n" + "\n".join(f"• {name}" for name in selected_names)
        except Exception:
            selection_text = f"✅ Выбраны ID: {', '.join(selected)}"
    else:
        selection_text = "ℹ️ Пока ничего не выбрано"
    
    await callback.answer()
    await callback.message.edit_text(
        text=f"<b>📂 Выберите подкатегории (можно несколько):</b>\n\n"
             f"{selection_text}\n\n"
             f"Нажмите <b>✅ Готово</b> когда закончите выбор.",
        reply_markup=build_category_keyboard(
            [cat for cat in get_all_categories(data['url'], data['user'], data['passwd']) if cat.get("parent")],
            prefix="cat_edit_"
        ),
        parse_mode="HTML"
    )

# --- Удаление подключения ---
@router.message(Command("remove_site"))
async def remove_site_confirm(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_remove"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_remove"),
        ]
    ])
    await message.answer("\u26A0\uFE0F Вы действительно хотите удалить подключение к WordPress?", reply_markup=keyboard)

@router.callback_query(F.data == "confirm_remove")
async def handle_confirm_remove(callback: CallbackQuery):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM wp_users WHERE telegram_id = ?", (callback.from_user.id,))
    conn.commit()
    conn.close()
    await callback.message.edit_reply_markup()
    await callback.message.edit_text("\U0001F5D1\uFE0F Данные сайта удалены.")

@router.callback_query(F.data == "cancel_remove")
async def handle_cancel_remove(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.edit_text("\u274C Удаление отменено.")