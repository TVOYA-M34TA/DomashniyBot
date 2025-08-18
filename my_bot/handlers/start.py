from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import get_main_kb, get_accept_kb
from utils.message_store import message_store

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    # Удаляем ВСЕ предыдущие сообщения
    await message_store.clean_chat(message.bot, message.from_user.id, message.chat.id)
    
    # Отправляем правила
    rules_msg = await message.answer(
        "🔹 <b>Правила использования:</b>\n"
        "1. Запрещён спам\n"
        "2. Соблюдайте законы\n"
        "3. Будьте вежливы",
        parse_mode="HTML",
        reply_markup=get_accept_kb()
    )
    await message_store.add_bot_message(message.from_user.id, rules_msg.message_id)

@router.message(F.text == "✅ Я согласен")
async def accept_rules(message: types.Message):
    # Удаляем ВСЕ сообщения (правила и кнопку согласия)
    await message_store.clean_chat(message.bot, message.from_user.id, message.chat.id)
    
    # Отправляем соцсети
    social_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Instagram", url="https://instagram.com/ваш_аккаунт")],
        [InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/ваш_канал")]
    ])
    
    social_msg = await message.answer(
        "Спасибо за согласие!\n\nНаши соцсети:",
        reply_markup=social_kb
    )
    
    # Отправляем главное меню
    menu_msg = await message.answer(
        "Выберите действие:",
        reply_markup=get_main_kb()
    )
    
    # Сохраняем новые сообщения бота
    await message_store.add_bot_message(message.from_user.id, social_msg.message_id)
    await message_store.add_bot_message(message.from_user.id, menu_msg.message_id)