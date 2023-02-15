import os

from pyrogram import filters
from pyrogram import Client
import config
from func import logger


@Client.on_message(filters.command("send_log", prefixes=config.prefix) & filters.user(config.admins))
async def send_log(app, message):
    logger.loggers(message, text="send logs")
    # logger.info(f'chat_id = {message.chat.id} | user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | send logs')
    await app.send_document(message.chat.id, os.path.join("logs", "logger.log"))
