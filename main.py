import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
)
from aiogram.exceptions import TelegramBadRequest
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Хранилище сообщений для очистки чата ===
class MessageStore:
    def __init__(self):
        self.user_messages = {}

    async def add(self, user_id: int, message_id: int):
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        if message_id not in self.user_messages[user_id]:
            self.user_messages[user_id].append(message_id)

    async def clean(self, bot: Bot, user_id: int, chat_id: int):
        if user_id not in self.user_messages:
            return
        for message_id in self.user_messages[user_id][:]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except TelegramBadRequest:
                pass
            except Exception as e:
                logging.error(f"Ошибка удаления {message_id}: {e}")
        self.user_messages[user_id].clear()

message_store = MessageStore()

# === Клавиатуры ===
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Правила", callback_data="show_rules")],
        [InlineKeyboardButton(text="🛠️ Инструкции", callback_data="show_instructions")],
        [InlineKeyboardButton(text="🏛️ Интересные места", callback_data="show_places")],
        [InlineKeyboardButton(text="👤 Связь", callback_data="show_contacts")],
        [InlineKeyboardButton(text="💰 Дополнительно можно", callback_data="show_extra_services")],
        [InlineKeyboardButton(text="🔥 Правила парной", callback_data="show_sauna_rules")]
    ])

def rules_full_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def instructions_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Дверь", callback_data="instruction_door")],
        [InlineKeyboardButton(text="🔥 Варочная панель", callback_data="instruction_stove")],
        [InlineKeyboardButton(text="⚠️ Ошибка на варочной панели", callback_data="instruction_stove_error")],
        [InlineKeyboardButton(text="🔥 Банная печь", callback_data="instruction_sauna_stove")],
        [InlineKeyboardButton(text="☕ Кофемашина", callback_data="instruction_coffee")],
        [InlineKeyboardButton(text="🍳 Духовка", callback_data="instruction_oven")],
        [InlineKeyboardButton(text="🧼 Посудомойка", callback_data="instruction_dishwasher")],
        [InlineKeyboardButton(text="🚧 Ворота", callback_data="instruction_gate")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def contact_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 WhatsApp", url="https://wa.me/79958847694")],
        [InlineKeyboardButton(text="📲 Telegram", url="https://t.me/+79958847694")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def social_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Instagram", url="https://www.instagram.com/dom.banya.dacha")],
        [InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/dom_banya_dacha")]
    ])

def places_kb(index: int, total: int, url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"place_prev_{index}"),
            InlineKeyboardButton(text=f"{index+1}/{total}", callback_data="ignore"),
            InlineKeyboardButton(text="➡️", callback_data=f"place_next_{index}")
        ],
        [InlineKeyboardButton(text="🌐 Сайт заведения", url=url)],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])

# === Данные мест ===
PLACES_DATA = [
    {"image": "pic/1.png", "url": "https://pt-zapovednik.ru/"},
    {"image": "pic/2.png", "url": "https://straus.ru/"},
    {"image": "pic/3.png", "url": "https://buninriver.ru/"},
    {"image": "pic/4.png", "url": "https://greenclub-dubechino.ru/"},
    {"image": "pic/5.png", "url": "https://www.freezone.net/"},
    {"image": "pic/6.png", "url": "https://dikie-belki.ru/"},
    {"image": "pic/7.png", "url": "https://akvapark-serpuhov.ru/"},
    {"image": "pic/8.png", "url": "https://kart-factory.ru/"},
    {"image": "pic/9.png", "url": "https://serpuhov-museum.ru/"},
    {"image": "pic/10.png", "url": "https://icedollhouse.ru/"},
    {"image": "pic/11.png", "url": "https://chekhovmuseum.com/"},
    {"image": "pic/12.png", "url": "http://gorteatr.ru/"},
    {"image": "pic/13.png", "url": "https://polenovo.ru/"},
    {"image": "pic/14.png", "url": "http://www.davidova-pustyn.ru/"},
    {"image": "pic/15.png", "url": "https://talezh1.ru/"},
    {"image": "pic/16.png", "url": "https://visotskymonastir.ru/"},
]

# === Обработчики ===
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message_store.clean(bot, user_id, chat_id)
    await message_store.add(user_id, message.message_id)

    rules_text = (
        "📋 <b>ПРАВИЛА ПРОЖИВАНИЯ</b>\n\n"
        "☀️ <b>Теплые полы:</b>\n"
        "• Только для комфорта ног\n"
        "• Не выше 27°C\n"
        "• НЕ оставлять вещи на полу - ЭТО ПОЖАРООПАСНО\n"
        "• НЕ передвигать мебель\n\n"
        "🚗 <b>Парковка:</b>\n"
        "• Только в пределах парковочных мест\n"
        "• Рассчитана на 2 авто\n\n"
        "🏠 <b>Имущество:</b>\n"
        "Если что-то случайно сломалось или разбилось, просим сообщить о произошедшем. Так мы сможем успеть купить или починить перед следующим заездом.\n"
        "• Намеренная или дорогостоящая порча имущества - высчитывается из депозита.\n\n"
        "🧹 <b>Чистота:</b>\n"
        "Просим вас перед отъездом помыть посуду, собрать и выбросить мусор в зеленый бак.\n"
        "Если вы не успеваете, то мы можем сделать это за вас:\n"
        "• Помыть посуду - от 300 руб.\n"
        "• Вынести мусор - от 500 руб.\n"
        "• Уборка территории от мусора - от 1000 руб.\n"
        "• Уборка за питомцем - от 2000 руб.\n"
        "• Убрать листья от веников - от 500 руб.\n"
        "• Отмыть стены и потолок от грязи в парной - от 5000 руб.\n\n"
        "🚭 <b>Курение:</b>\n"
        "• В доме и на веранде курение сигарет, кальянов и любых нагревательных систем под запретом\n"
        "• 10.000 руб. за озонирование\n"
        "• Окурки только в пепельницы\n\n"
        "⚠️ <b>Безопасность:</b>\n"
        "• Костер только в костровой зоне\n"
        "• НЕ отключать электрощиток, камеры, бойлер\n"
        "• НЕ сушить одежду на конвекторах\n\n"
        "<b>Соблюдение правил - залог вашей безопасности и комфортного отдыха!</b>\n\n"
        "<i>Нажмите «✅ Я согласен», чтобы продолжить</i>"
    )

    rules_msg = await message.answer(
        rules_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я согласен", callback_data="accept_rules")]
        ])
    )
    await message_store.add(user_id, rules_msg.message_id)

@dp.callback_query(F.data == "accept_rules")
async def accept_rules(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    await message_store.clean(bot, user_id, chat_id)

    welcome = await callback.message.answer(
        "👋 <b>Добро пожаловать!</b>\n\nПодпишитесь на наши соцсети:",
        parse_mode="HTML",
        reply_markup=social_kb()
    )
    menu = await callback.message.answer("Выберите действие:", reply_markup=main_menu_kb())

    await message_store.add(user_id, welcome.message_id)
    await message_store.add(user_id, menu.message_id)
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    await message_store.clean(bot, user_id, chat_id)

    welcome = await callback.message.answer(
        "👋 <b>Добро пожаловать!</b>\n\nПодпишитесь на наши соцсети:",
        parse_mode="HTML",
        reply_markup=social_kb()
    )
    menu = await callback.message.answer("Выберите действие:", reply_markup=main_menu_kb())

    await message_store.add(user_id, welcome.message_id)
    await message_store.add(user_id, menu.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_rules")
async def show_rules(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)

    rules_text = (
        "📋 <b>ПРАВИЛА ПРОЖИВАНИЯ</b>\n\n"
        "☀️ <b>Теплые полы:</b>\n• Только для комфорта ног\n• Не выше 27°C\n• НЕ оставлять вещи на полу - ЭТО ПОЖАРООПАСНО\n• НЕ передвигать мебель\n\n"
        "🚗 <b>Парковка:</b>\n• Только в пределах парковочных мест\n• Рассчитана на 2 авто\n\n"
        "🏠 <b>Имущество:</b>\nЕсли что-то случайно сломалось или разбилось, просим сообщить о произошедшем. Так мы сможем успеть купить или починить перед следующим заездом.\n• Намеренная или дорогостоящая порча имущества - высчитывается из депозита.\n\n"
        "🧹 <b>Чистота:</b>\nПросим вас перед отъездом помыть посуду, собрать и выбросить мусор в зеленый бак.\nЕсли вы не успеваете, то мы можем сделать это за вас:\n"
        "• Помыть посуду - от 300 руб.\n• Вынести мусор - от 500 руб.\n• Уборка территории от мусора - от 1000 руб.\n• Уборка за питомцем - от 2000 руб.\n• Убрать листья от веников - от 500 руб.\n• Отмыть стены и потолок от грязи в парной - от 5000 руб.\n\n"
        "🚭 <b>Курение:</b>\n• В доме и на веранде курение сигарет, кальянов и любых нагревательных систем под запретом\n• 10.000 руб. за озонирование\n• Окурки только в пепельницы\n\n"
        "⚠️ <b>Безопасность:</b>\n• Костер только в костровой зоне\n• НЕ отключать электрощиток, камеры, бойлер\n• НЕ сушить одежду на конвекторах\n\n"
        "<b>Соблюдение правил - залог вашей безопасности и комфортного отдыха!</b>"
    )

    msg = await callback.message.answer(rules_text, parse_mode="HTML", reply_markup=rules_full_kb())
    await message_store.add(callback.from_user.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_instructions")
async def show_instructions_menu(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    msg = await callback.message.answer(
        "📚 <b>Инструкции</b>\n\nВыберите нужную:",
        parse_mode="HTML",
        reply_markup=instructions_kb()
    )
    await message_store.add(callback.from_user.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data.startswith("instruction_"))
async def handle_instruction(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    instr = callback.data.split("_", 1)[1]

    captions = {
        'door': "🚪 <b>Инструкция: Как открыть/закрыть дверь</b>",
        'stove': "🔥 <b>Инструкция: Варочная панель</b>",
        'stove_error': "⚠️ <b>Ошибка на варочной панели</b>\nКак снять блокировку и сбросить ошибку",
        'sauna_stove': "🔥 <b>Инструкция: Банная печь</b>\nКак правильно топить и поддерживать жар",
        'coffee': "☕ <b>Инструкция: Кофемашина</b>\nПриготовление кофе и уход",
        'oven': "🍳 <b>Инструкция: Духовка</b>\nРежимы и безопасное использование",
        'dishwasher': "🧼 <b>Инструкция: Посудомоечная машина</b>\nЗагрузка и запуск",
        'gate': "🚧 <b>Инструкция: Ворота</b>\nОткрытие и блокировка"
    }

    video_files = {
        'door': "door_instruction.mp4",
        'stove': "stove_instruction.mp4",
        'stove_error': "stove_error_instruction.mp4",
        'sauna_stove': "sauna_stove_instruction.mp4",
        'coffee': "coffee_instruction.mp4",
        'oven': "oven_instruction.mp4",
        'dishwasher': "dishwasher_instruction.mp4",
        'gate': "gate_instruction.mp4"
    }

    filename = video_files.get(instr)
    if not filename:
        await callback.message.answer("❌ Инструкция не найдена")
        await callback.answer()
        return

    video_path = f"videos/{filename}"
    try:
        video = FSInputFile(video_path)
        sent = await callback.message.answer_video(
            video=video,
            caption=captions.get(instr, "<b>Видеоинструкция</b>"),
            parse_mode="HTML"
        )
        await message_store.add(callback.from_user.id, sent.message_id)
    except Exception:
        sent = await callback.message.answer("📹 <b>Видеоинструкция временно недоступна</b>")
        await message_store.add(callback.from_user.id, sent.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_contacts")
async def show_contacts(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    msg = await callback.message.answer(
        "👤 <b>Связь с нами:</b>\n\nВыберите удобный способ:",
        parse_mode="HTML",
        reply_markup=contact_kb()
    )
    await message_store.add(callback.from_user.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_extra_services")
async def show_extra_services(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    text = (
        "💰 <b>Дополнительно можно заказать:</b>\n\n"
        "🔥 <b>Помощь в растопке банной печи</b> — 2000 руб. (одна топка)\n"
        "🪵 <b>Дрова</b> — 500 руб. за 10 дров\n"
        "🛏️ <b>Доп. комплект постельного белья и полотенец</b> — 1500 руб.\n"
        "🛁 <b>Халат</b> — 400 руб.\n\n"
        "<i>Заказывайте заранее — сделаем отдых ещё комфортнее!</i>"
    )
    msg = await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
        ])
    )
    await message_store.add(callback.from_user.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_sauna_rules")
async def show_sauna_rules(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)

    text = (
        "🔥 <b>ПРАВИЛА ПАРНОЙ</b>\n\n"
        "🌿 <b>Веники</b> — можно!\n"
        "При условии, что вы:\n"
        "• Хорошо промоете веник перед использованием\n"
        "• Тщательно уберёте все листья после парения\n\n"
        "🪵 Запарки — можно использовать в запарнике\n\n"
        "❌ <b>Эфирные масла</b> — просим не использовать\n"
        "(у других гостей может быть аллергия)\n\n"
        "⚠️ <b>Важно:</b>\n"
        "Если веник не промыть и не убрать листья — он оставляет после себя очень много грязи 🪵\n\n"
        "Смотрите видео, как правильно топить банную печь 👇"
    )

    text_msg = await callback.message.answer(text, parse_mode="HTML")
    await message_store.add(callback.from_user.id, text_msg.message_id)

    video_path = "videos/sauna_stove_instruction.mp4"
    try:
        video = FSInputFile(video_path)
        video_msg = await callback.message.answer_video(
            video=video,
            caption="🔥 <b>Как правильно топить банную печь</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
            ])
        )
        await message_store.add(callback.from_user.id, video_msg.message_id)
    except Exception:
        error_msg = await callback.message.answer(
            "📹 Видео временно недоступно",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
            ])
        )
        await message_store.add(callback.from_user.id, error_msg.message_id)
    await callback.answer()

# === Места и навигация ===
@dp.callback_query(F.data == "show_places")
async def show_places_menu(callback: types.CallbackQuery):
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    await show_place(callback, 0)
    await callback.answer()

async def show_place(query: types.CallbackQuery, index: int):
    place = PLACES_DATA[index]
    user_id = query.from_user.id
    try:
        photo = FSInputFile(place["image"])
        sent = await query.message.answer_photo(
            photo=photo,
            reply_markup=places_kb(index, len(PLACES_DATA), place["url"])
        )
    except Exception:
        sent = await query.message.answer(
            f"❌ Изображение #{index+1} недоступно",
            reply_markup=places_kb(index, len(PLACES_DATA), place["url"])
        )
    await message_store.add(user_id, sent.message_id)

@dp.callback_query(F.data.startswith("place_"))
async def handle_place_navigation(callback: types.CallbackQuery):
    if callback.data == "ignore":
        await callback.answer()
        return
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.answer()
        return
    action = parts[1]
    current_index = int(parts[2])
    new_index = (current_index - 1) % len(PLACES_DATA) if action == "prev" else (current_index + 1) % len(PLACES_DATA)
    await message_store.clean(bot, callback.from_user.id, callback.message.chat.id)
    await show_place(callback, new_index)
    await callback.answer()

# === Запуск ===
async def main():
    print("🏡 Дом.Баня.Дача — Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())