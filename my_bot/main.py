import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.start import router as start_router
from handlers.contact import router as contact_router
from middlewares.user_messages import UserMessagesMiddleware

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Подключаем middleware для сохранения сообщений пользователя
dp.message.middleware(UserMessagesMiddleware())
dp.callback_query.middleware(UserMessagesMiddleware())

dp.include_router(start_router)
dp.include_router(contact_router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())