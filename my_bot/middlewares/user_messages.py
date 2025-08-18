from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from utils.message_store import message_store

class UserMessagesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Сохраняем сообщения пользователя
        if isinstance(event, Message):
            await message_store.add_user_message(
                event.from_user.id,
                event.message_id
            )
        # Сохраняем нажатия на кнопки
        elif isinstance(event, CallbackQuery) and event.message:
            await message_store.add_user_message(
                event.from_user.id,
                event.message.message_id
            )
        
        return await handler(event, data)