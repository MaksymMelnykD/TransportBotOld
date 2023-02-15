import os

from pyrogram import filters
from pyrogram import Client
import config
from func import logger

@Client.on_message(filters.command("send_log", prefixes=config.prefix) & filters.user(config.default_admins))
async def send_log(app, message):
    await app.send_document(message.chat.id, os.path.join("logs", "logger.log"))
