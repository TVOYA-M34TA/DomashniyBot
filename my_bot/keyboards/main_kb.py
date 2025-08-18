from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📜 Правила")],
            [KeyboardButton(text="🛠️ Инструкции")],
            [KeyboardButton(text="👤 Связь")]
        ],
        resize_keyboard=True
    )

def get_accept_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Я согласен")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
