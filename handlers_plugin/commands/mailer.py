import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
import db
from func import logger, auto_delete


@Client.on_message(filters.command("mailer") & filters.reply & filters.user([]))
async def mailer(app: Client, message: Message):
    logger.loggers(message, text="used !mailer")
    if len(message.command) < 2 or message.command[1] not in ("1", "0", "2"):
        await message.reply("Вкажіть аргументи\n<code>/mailer 0</code> –надіслати всім користувачам бота"
                            "\n<code>/mailer 1</code> – надіслати тільки підписникам бота")
        return

    users = db.get_all_users((int(message.command[1])))
    a = time.time()
    fail = 0
    correct = 0
    await message.reply("Розсилка розпочата\nУсього користувачів: {}".format(len(users)))
    for user in users:
        try:
            await app.copy_message(user, message.chat.id, message.reply_to_message_id)
        except Exception as e:
            fail += 1
            # print(e)
        else:
            correct += 1
        await asyncio.sleep(.05)
    b = time.time()
    await message.reply(
        "Надіслано користувачам бота протягом " + str(round(b - a, 2)) + " секунд\nУсього користувачів: " + str(
            len(users)) + "\nУспішно: " + str(correct) + "\nНевдало: " + str(fail))


@Client.on_message(filters.command("mail"))
async def sub_to_mail(app: Client, message: Message):
    logger.loggers(message, text="used !mail")
    db.add_user(message.from_user.id)
    data = db.get_user_mail(message.from_user.id)
    db.set_user_mail(message.from_user.id, data is False)
    if data:
        mes = await message.reply(
            "Нам дуже шкода, що Ви відписалися від розсилки. Якщо виникло бажання оновити підписку - відправте команду /mail ще раз")
    else:
        mes = await message.reply(
            "Дякуємо, що Ви з нами! Для того, щоб відписатися від розсилки - відправте команду /mail ще раз")

    await auto_delete.delete_command([message, mes])
