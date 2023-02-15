from datetime import timedelta, datetime

from pyrogram import Client
from pyrogram.errors import UserAdminInvalid, ChannelInvalid, ChatAdminRequired
from pyrogram.types import ChatPermissions

import costum_filters
import db
from func import auto_delete
from func import logger


@Client.on_message(costum_filters.link_filter)
async def white_list_link(app, message):
    try:
        await message.delete()
    except Exception as e:
        print(e)
    logger.loggers(message, text="использовано запрещённое слово")
