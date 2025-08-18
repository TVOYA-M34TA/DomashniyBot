from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_contact_kb():  # Убедитесь, что функция называется именно так
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 WhatsApp")],
            [KeyboardButton(text="📨 Telegram")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )