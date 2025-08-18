from typing import Dict, List
from aiogram.methods import DeleteMessage
from aiogram import Bot

class MessageStore:
    def __init__(self):
        self.bot_messages: Dict[int, List[int]] = {}
        self.user_messages: Dict[int, List[int]] = {}

    async def add_bot_message(self, user_id: int, message_id: int):
        """Добавляет сообщение бота в историю"""
        if user_id not in self.bot_messages:
            self.bot_messages[user_id] = []
        self.bot_messages[user_id].append(message_id)

    async def add_user_message(self, user_id: int, message_id: int):
        """Добавляет сообщение пользователя в историю"""
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append(message_id)

    async def clean_chat(self, bot: Bot, user_id: int, chat_id: int):
        """Удаляет ВСЕ сообщения (бота и пользователя)"""
        all_messages = []
        
        # Собираем сообщения бота
        if user_id in self.bot_messages:
            all_messages.extend(self.bot_messages[user_id])
            self.bot_messages[user_id] = []
            
        # Собираем сообщения пользователя
        if user_id in self.user_messages:
            all_messages.extend(self.user_messages[user_id])
            self.user_messages[user_id] = []
        
        # Удаляем все сообщения
        for msg_id in all_messages:
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=msg_id))
            except Exception as e:
                print(f"Ошибка при удалении сообщения {msg_id}: {e}")

message_store = MessageStore()