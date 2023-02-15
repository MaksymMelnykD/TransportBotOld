import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
import db
from func import logger


@Client.on_message(filters.command("mailer") & filters.reply & filters.user([594165498, 666445915,1398764450]))
async def mailer(app: Client, message: Message):
    users = db.get_all_users()
    a = time.time()
    fail = 0
    correct = 0
    await message.reply("Розсилка почалася\nВсього користувачів: {}".format(len(users)))
    for user in users:
        try:
            await app.copy_message(user, message.chat.id, message.reply_to_message_id)
        except Exception as e:
            fail += 1
            #print(e)
        else:
            correct += 1
        await asyncio.sleep(.05)
    b = time.time()
    await message.reply("Надіслано всім користувачам бота протягом " + str(b - a) + " секунд\nВсього юзерів: " + str(len(users)) + "\nУспішно: " + str(correct) + "\nНевдало: " + str(fail))
