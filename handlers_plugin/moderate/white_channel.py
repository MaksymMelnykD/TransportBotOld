import pyrogram.enums
from loguru import logger
from pyrogram import filters
from pyrogram import Client
from pyrogram.types import Message
from func import logger

import config


@Client.on_message(filters.chat(config.chat_dp_id) & filters.forwarded)
async def white_list_channel(app, message: Message):
    try:
        if message.forward_from_chat.id in (config.chat_dp_id, config.channel_dp_id):
            logger.loggers(message, text=f"использован Оффициальный канал ({message.forward_from_chat.title})")
        elif message.forward_from_chat.type is not pyrogram.enums.ChatType.PRIVATE:
            logger.loggers(message, text=f"Использован не Оффициальный канал ({message.forward_from_chat.title})")
            await app.delete_messages(message.chat.id, message.id)
    except Exception as e:
        print(e)
