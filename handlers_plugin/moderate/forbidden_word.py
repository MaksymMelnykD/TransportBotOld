from datetime import datetime, timedelta

from loguru import logger
from pyrogram import filters
from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, ChannelInvalid
from pyrogram.types import ChatPermissions

import db
from costum_filters import words_blacklist_filter
from func import auto_delete
from func import logger


@Client.on_message(words_blacklist_filter & ~filters.forwarded)
async def text_mat(app, message):
    try:
        logger.loggers(message, text="used a forbidden word")
        await message.delete()
    except Exception as e:
        print(e)
