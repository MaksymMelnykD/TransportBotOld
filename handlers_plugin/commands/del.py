from loguru import logger
from pyrogram import filters
from pyrogram import Client
from pyrogram.types import Message

import config
from costum_filters import chat_admin_filter
from func import auto_delete
from func import logger


@Client.on_message(filters.command("del", prefixes=config.prefix) & (chat_admin_filter | filters.user(config.admins)))
async def dels(app: Client, message: Message):
    logger.loggers(message, text="used !del")
    #logger.info(f'chat_id = {message.chat.id} | user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !del')
    if message.reply_to_message:
        await app.delete_messages(message.chat.id, [message.reply_to_message_id, message.id])
    else:
        mes = await message.reply("Ви не здійснили відповіді на запитання")
        await auto_delete.delete_command([mes, message])
        return
