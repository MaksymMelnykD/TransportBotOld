import sys
from pyrogram import filters
from pyrogram import Client
import config
from func import logger


@Client.on_message(filters.command("stop", prefixes=config.prefix) & filters.user(config.admins))
async def stop(app, message):
    logger.loggers(message, text="used !stop")
    sys.exit(0)
