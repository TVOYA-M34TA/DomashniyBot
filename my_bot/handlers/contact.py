from aiogram import Router, types, F
from keyboards.main_kb import get_main_kb
from keyboards.contact_kb import get_contact_kb
from utils.message_store import message_store

router = Router()

@router.message(F.text == "👤 Связь")
async def show_contacts(message: types.Message):
    # Удаляем ВСЕ предыдущие сообщения
    await message_store.clean_chat(message.bot, message.from_user.id, message.chat.id)
    
    # Отправляем контакты
    contact_msg = await message.answer(
        "Выберите способ связи:",
        reply_markup=get_contact_kb()
    )
    await message_store.add_bot_message(message.from_user.id, contact_msg.message_id)

@router.message(F.text == "⬅️ Назад")
async def back_handler(message: types.Message):
    # Удаляем ВСЕ сообщения
    await message_store.clean_chat(message.bot, message.from_user.id, message.chat.id)
    
    # Возвращаем в главное меню
    menu_msg = await message.answer(
        "Главное меню:",
        reply_markup=get_main_kb()
    )
    await message_store.add_bot_message(message.from_user.id, menu_msg.message_id)

@router.message(F.text.in_(["📱 WhatsApp", "📨 Telegram"]))
async def send_contact_link(message: types.Message):
    # Удаляем предыдущие сообщения
    await message_store.clean_chat(message.bot, message.from_user.id, message.chat.id)
    
    # Отправляем ссылку
    links = {
        "📱 WhatsApp": "https://wa.me/79001234567",
        "📨 Telegram": "https://t.me/username"
    }
    link_msg = await message.answer(links[message.text])
    await message_store.add_bot_message(message.from_user.id, link_msg.message_id)
    
    # Добавляем кнопку назад
    back_msg = await message.answer(
        "Нажмите кнопку чтобы вернуться:",
        reply_markup=get_contact_kb()
    )
    await message_store.add_bot_message(message.from_user.id, back_msg.message_id)