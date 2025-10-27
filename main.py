import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.methods import DeleteMessage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Хранилище сообщений
class MessageStore:
    def __init__(self):
        self.user_messages = {}

    async def add_message(self, user_id: int, message_id: int):
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append(message_id)

    async def clean_chat(self, bot: Bot, user_id: int, chat_id: int):
        if user_id not in self.user_messages:
            return
            
        messages_to_remove = []
        for msg_id in self.user_messages[user_id]:
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=msg_id))
                messages_to_remove.append(msg_id)
            except:
                continue
        
        for msg_id in messages_to_remove:
            if msg_id in self.user_messages[user_id]:
                self.user_messages[user_id].remove(msg_id)

message_store = MessageStore()

# Клавиатуры
def rules_full_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Подробнее", url="http://dom.banya.dacha.tilda.ws/info")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Правила", callback_data="show_rules")],
        [InlineKeyboardButton(text="🛠️ Инструкции", callback_data="show_instructions")],
        [InlineKeyboardButton(text="🏛️ Интересные места", callback_data="show_places")],
        [InlineKeyboardButton(text="👤 Связь", callback_data="show_contacts")]
    ])

def instructions_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Дверь", callback_data="instruction_door")],
        [InlineKeyboardButton(text="🔥 Плита", callback_data="instruction_stove")],
        [InlineKeyboardButton(text="🔒 Блокировка плиты", callback_data="instruction_stove_lock")],
        [InlineKeyboardButton(text="🚧 Ворота", callback_data="instruction_gate")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def contact_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 WhatsApp", url="https://wa.me/79958847694")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def social_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Instagram", url="https://www.instagram.com/dom.banya.dacha?igsh=MWNzbWhhbHA3MGo3Ng==")],
        [InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/dom_banya_dacha")]
    ])

def places_kb(current_index: int, total: int, url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"place_prev_{current_index}"),
            InlineKeyboardButton(text=f"{current_index+1}/{total}", callback_data="place_counter"),
            InlineKeyboardButton(text="➡️", callback_data=f"place_next_{current_index}")
        ],
        [InlineKeyboardButton(text="🌐 Сайт заведения", url=url)],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])

# Обработчики
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message_store.clean_chat(bot, message.from_user.id, message.chat.id)
    await message_store.add_message(message.from_user.id, message.message_id)
    
    rules_text = (
        "📋 <b>ПРАВИЛА ПРОЖИВАНИЯ</b>\n\n"
        "🚨 <b>ВНИМАНИЕ!</b>\n\n"
        "🔥 <b>Теплые полы:</b>\n"
        "• Только для комфорта ног\n"
        "• Не выше 26°C\n"
        "• НЕ оставлять вещи на полу - ЭТО ПОЖАРООПАСНО\n"
        "• НЕ двигать мебель\n\n"
        "🚗 <b>Парковка:</b>\n"
        "• Только в пределах парковочных мест\n"
        "• Рассчитана на 2 авто\n"
        "• Заезд на газон - штраф в размере депозита\n\n"
        "🏠 <b>Имущество:</b>\n"
        "• Сообщайте о повреждениях заранее\n"
        "• Белое постельное белье - бережное отношение\n"
        "• Порча имущества - компенсация стоимости\n"
        "• Доп. комплект белья - 1000 руб. (за 4 часа)\n\n"
        "🧹 <b>Чистота:</b>\n"
        "• Помыть посуду - от 500 руб.\n"
        "• Вынести мусор - от 500 руб.\n"
        "• Уборка территории - от 1000 руб.\n"
        "• Уборка за питомцем - от 2000 руб.\n\n"
        "🚭 <b>Курение:</b>\n"
        "• В доме и на веранде - ЗАПРЕЩЕНО\n"
        "• Курение в доме - штраф 10.000 руб. за озонирование\n"
        "• Окурки только в пепельницы\n\n"
        "⚠️ <b>Безопасность:</b>\n"
        "• Костер только в зоне мангала\n"
        "• НЕ отключать электрощиток, камеры, bойлер\n"
        "• НЕ сушить одежду на теплом полу и конвекторах\n"
        "• Дрова - 500 руб. за 5 колотых дров\n\n"
        "<b>Соблюдение правил - залог вашей безопасности и комфортного отдых</b>\n"
        "<i>Нажмите '✅ Я согласен' для продолжения</i>"
    )
    
    rules_msg = await message.answer(
        rules_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я согласен", callback_data="accept_rules")]
        ])
    )
    await message_store.add_message(message.from_user.id, rules_msg.message_id)

@dp.callback_query(F.data == "accept_rules")
async def accept_rules(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    welcome_msg = await callback.message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Подпишитесь на наши соцсети:",
        parse_mode="HTML",
        reply_markup=social_kb()
    )
    
    menu_msg = await callback.message.answer(
        "Выберите действие:",
        reply_markup=main_menu_kb()
    )
    
    await message_store.add_message(callback.from_user.id, welcome_msg.message_id)
    await message_store.add_message(callback.from_user.id, menu_msg.message_id)
    
    try:
        await callback.message.delete()
    except:
        pass

@dp.callback_query(F.data == "show_rules")
async def show_rules(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    rules_text = (
        "📋 <b>ПРАВИЛА ПРОЖИВАНИЯ</b>\n\n"
        "🚨 <b>ВНИМАНИЕ!</b>\n\n"
        "🔥 <b>Теплые полы:</b>\n"
        "• Только для комфорта ног\n"
        "• Не выше 26°C\n"
        "• НЕ оставлять вещи на полу - ЭТО ПОЖАРООПАСНО\n"
        "• НЕ двигать мебель\n\n"
        "🚗 <b>Парковка:</b>\n"
        "• Только в пределах парковочных мест\n"
        "• Рассчитана на 2 авто\n"
        "• Заезд на газон - штраф в размере депозита\n\n"
        "🏠 <b>Имущество:</b>\n"
        "• Сообщайте о повреждениях заранее\n"
        "• Белое постельное белье - бережное отношение\n"
        "• Порча имущества - компенсация стоимости\n"
        "• Доп. комплект белья - 1000 руб. (за 4 часа)\n\n"
        "🧹 <b>Чистота:</b>\n"
        "• Помыть посуду - от 500 руб.\n"
        "• Вынести мусор - от 500 руб.\n"
        "• Уборка территории - от 1000 руб.\n"
        "• Уборка за питомцем - от 2000 руб.\n\n"
        "🚭 <b>Курение:</b>\n"
        "• В доме и на веранде - ЗАПРЕЩЕНО\n"
        "• Курение в доме - штраф 10.000 руб. за озонирование\n"
        "• Окурки только в пепельницы\n\n"
        "⚠️ <b>Безопасность:</b>\n"
        "• Костер только в зоне мангала\n"
        "• НЕ отключать электрощиток, камеры, bойлер\n"
        "• НЕ сушить одежду на теплом полу и конвекторах\n"
        "• Дрова - 500 руб. за 5 колотых дров\n\n"
        "<i>Соблюдение правил - залог вашей безопасности и комфортного отдыха!</i>"
    )
    
    rules_msg = await callback.message.answer(
        rules_text,
        parse_mode="HTML",
        reply_markup=rules_full_kb()
    )
    await message_store.add_message(callback.from_user.id, rules_msg.message_id)
    
    try:
        await callback.message.delete()
    except:
        pass

@dp.callback_query(F.data == "show_instructions")
async def show_instructions_menu(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    instructions_msg = await callback.message.answer(
        "📚 <b>Инструкции</b>\n\nВыберите нужную вам инструкцию:",
        parse_mode="HTML",
        reply_markup=instructions_kb()
    )
    await message_store.add_message(callback.from_user.id, instructions_msg.message_id)
    
    try:
        await callback.message.delete()
    except:
        pass

@dp.callback_query(F.data.startswith("instruction_"))
async def handle_instruction(callback: types.CallbackQuery):
    instruction_data = callback.data.split('_')[1]
    captions = {
        'door': "🚪 <b>Инструкция: Как открыть/закрыть дверь</b>",
        'stove': "🔥 <b>Инструкция: Включение плиты</b>",
        'stove_lock': "🔒 <b>Инструкция: Блокировка плиты</b>",
        'gate': "🚧 <b>Инструкция: Блокировка ворот</b>"
    }
    
    try:
        video = types.FSInputFile(f"videos/{instruction_data}_instruction.mp4")
        video_msg = await callback.message.answer_video(
            video=video,
            caption=captions.get(instruction_data, "Инструкция"),
            parse_mode="HTML"
        )
        await message_store.add_message(callback.from_user.id, video_msg.message_id)
    except Exception as e:
        error_msg = await callback.message.answer("❌ Видеоинструкция временно недоступна")
        await message_store.add_message(callback.from_user.id, error_msg.message_id)
    await callback.answer()

@dp.callback_query(F.data == "show_contacts")
async def show_contacts(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    contacts_msg = await callback.message.answer(
        "👤 <b>Связь с нами:</b>\n\nНажмите на кнопку для мгновенной связи:",
        parse_mode="HTML",
        reply_markup=contact_kb()
    )
    await message_store.add_message(callback.from_user.id, contacts_msg.message_id)
    
    try:
        await callback.message.delete()
    except:
        pass

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    welcome_msg = await callback.message.answer(
        "👋 <b>Добро пожаловать!</b>\n\nПодпишитесь на наши соцсети:",
        parse_mode="HTML",
        reply_markup=social_kb()
    )
    
    menu_msg = await callback.message.answer(
        "Выберите действие:",
        reply_markup=main_menu_kb()
    )
    
    await message_store.add_message(callback.from_user.id, welcome_msg.message_id)
    await message_store.add_message(callback.from_user.id, menu_msg.message_id)

PLACES_DATA = [
    {
        "image": "pic/1.png",
        "url": "https://pt-zapovednik.ru/"
    },
    {
        "image": "pic/2.png", 
        "url": "https://straus.ru/"
    },
    {
        "image": "pic/3.png",
        "url": "https://buninriver.ru/"
    },
    {
        "image": "pic/4.png",
        "url": "https://greenclub-dubechino.ru/"
    },
    {
        "image": "pic/5.png",
        "url": "https://www.freezone.net/"
    },
    {
        "image": "pic/6.png",
        "url": "https://dikie-belki.ru/"
    },
    {
        "image": "pic/7.png",
        "url": "https://akvapark-serpuhov.ru/"
    },
    {
        "image": "pic/8.png",
        "url": "https://kart-factory.ru/"
    },
    {
        "image": "pic/9.png",
        "url": "https://serpuhov-museum.ru/"
    },
    {
        "image": "pic/10.png",
        "url": "https://icedollhouse.ru/"
    },
    {
        "image": "pic/11.png",
        "url": "https://chekhovmuseum.com/"
    },
    {
        "image": "pic/12.png",
        "url": "http://gorteatr.ru/"
    },
    {
        "image": "pic/13.png",
        "url": "https://polenovo.ru/"
    },
    {
        "image": "pic/14.png",
        "url": "http://www.davidova-pustyn.ru/"
    },
    {
        "image": "pic/15.png",
        "url": "https://talezh1.ru/"
    },
    {
        "image": "pic/16.png",
        "url": "https://visotskymonastir.ru/"
    }
]

@dp.callback_query(F.data == "show_places")
async def show_places_menu(callback: types.CallbackQuery):
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    
    # Показываем первую картинку
    await show_place(callback, 0)
    
    try:
        await callback.message.delete()
    except:
        pass

async def show_place(callback: types.CallbackQuery, index: int):
    place = PLACES_DATA[index]
    
    try:
        photo = types.FSInputFile(place["image"])
        photo_msg = await callback.message.answer_photo(
            photo=photo,
            reply_markup=places_kb(index, len(PLACES_DATA), place["url"])
        )
        await message_store.add_message(callback.from_user.id, photo_msg.message_id)
    except Exception as e:
        error_msg = await callback.message.answer(
            f"❌ Не удалось загрузить изображение",
            reply_markup=places_kb(index, len(PLACES_DATA), place["url"])
        )
        await message_store.add_message(callback.from_user.id, error_msg.message_id)

@dp.callback_query(F.data.startswith("place_"))
async def handle_place_navigation(callback: types.CallbackQuery):
    data_parts = callback.data.split('_')
    
    if len(data_parts) < 3:
        await callback.answer()
        return
        
    action = data_parts[1]  # "prev" или "next"
    current_index = int(data_parts[2])
    
    if action == "prev":
        new_index = (current_index - 1) % len(PLACES_DATA)
    elif action == "next":
        new_index = (current_index + 1) % len(PLACES_DATA)
    else:
        await callback.answer()
        return
    
    await message_store.clean_chat(bot, callback.from_user.id, callback.message.chat.id)
    await show_place(callback, new_index)
    await callback.answer()

# Запуск бота
async def main():
    ascii_art = """

░░██╗██╗░█████╗░███████╗░█████╗░  ████████╗███████╗░█████╗░███╗░░░███╗
░██╔╝██║██╔══██╗██╔════╝██╔══██╗  ╚══██╔══╝██╔════╝██╔══██╗████╗░████║
██╔╝░██║╚██████║██████╗░╚█████╔╝  ░░░██║░░░█████╗░░███████║██╔████╔██║
███████║░╚═══██║╚════██╗██╔══██╗  ░░░██║░░░██╔══╝░░██╔══██║██║╚██╔╝██║
╚════██║░█████╔╝██████╔╝╚█████╔╝  ░░░██║░░░███████╗██║░░██║██║░╚═╝░██║
░░░░░╚═╝░╚════╝░╚═════╝░░╚════╝░  ░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝
    """
    print(ascii_art)
    print("code by TBOYA_M34TA")
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())