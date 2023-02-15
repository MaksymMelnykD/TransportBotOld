from pyrogram import Client, filters
from pyrogram.types import Message
import config
import os
from func import logger


@Client.on_message(filters.command("restart") & filters.user(config.admins))
async def restart(app: Client, message: Message):
    logger.loggers(message, text="used restart cmd")
    await message.reply("Бот зараз буде перезапущений і оновлений...")
    os.system("sudo bash /home/gernetsoffical/github_script.sh")
