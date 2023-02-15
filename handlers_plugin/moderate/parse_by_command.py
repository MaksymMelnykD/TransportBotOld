import time

from pyrogram import Client, filters
from pyrogram.types import Message
import threading
import config
from parsing import parse
from func import logger


@Client.on_message(filters.command("parse") & filters.user(config.default_admins))
async def start_parse(app: Client, message: Message):
    await message.delete()
    try:
        parse.transport_parse()
    except Exception as e:
        await app.send_message(message.from_user.id, f"Помилка при парсингу автобусів:\n{e}")
    threading.Thread(target=parse.electric_transport_parse).start()
