import asyncio
import re
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, ChannelInvalid
from pyrogram.types import Message, ChatPermissions, CallbackQuery

import config
import costum_filters
import db
from func import auto_delete
from func import logger
from keyboards.inline import del_mute_kb


async def message_deleter(message, time: int = 180):
    await asyncio.sleep(time)
    try:
        await message.delete()
    except Exception as e:
        print(e)


@Client.on_message(
    filters.command("report", prefixes=["/", "!"]) & costum_filters.group & filters.reply & costum_filters.user_command)
async def report(app: Client, message: Message):
    await message.delete()
    report_chat = db.get_report_chat(message.chat.id)
    if report_chat == 0:
        chats = db.get_chat_admins(message.chat.id)
    else:
        chats = [report_chat]
    for chat in chats:
        try:
            await app.send_message(chat,
                                   f"Виклик адміністрації\nВиклик команди здійснив: {message.from_user.mention} на {message.reply_to_message.from_user.mention}\n\nПосилання на повідомлення:\n{message.reply_to_message.link}")
        except Exception as e:
            print(e)
    mes = await message.reply("Дякуємо, Ваше повідомлення надіслано адміністрації")
    messages = [mes, message]
    await auto_delete.delete_command(messages)


@Client.on_message(filters.command("report", prefixes=["/", "!"]) & costum_filters.group & ~filters.reply)
async def err_report(app: Client, message: Message):
    mes = await message.reply("На жаль, Ви не відповіли на повідомлення.")
    messages = [mes, message]
    await auto_delete.delete_command(messages, 10)


@Client.on_message(filters.command(["warn", "w"], prefixes=["/",
                                                            "!"]) & costum_filters.group & filters.reply & costum_filters.chat_admin_filter)
async def warn(app: Client, message: Message):
    if message.sender_chat:
        logger.loggers(message, text="used !warn [Попередження неможливе: користувач пише не від свого імені.]")
        return await message.reply("Попередження неможливе: користувач пише не від свого імені.")
    mes1 = None
    if len(message.command) < 2:
        logger.loggers(message, text="used !warn [Ви не вказали аргументи]")
        mes = await message.reply("Ви не вказали аргументи")
        await auto_delete.delete_command([mes, message], 10)
        return
    arg = message.command[1]
    if arg == 'del' and len(message.command) > 2:
        if not message.command[2].isdigit():
            logger.loggers(message, text="used !warn_del [Невірний номер варна]")
            mes = await message.reply("Невірний номер варна")
            await auto_delete.delete_command([mes, message], 10)
            return
        status = db.del_warn(message.chat.id, message.reply_to_message.from_user.id, int(message.command[2]))
        if status:
            logger.loggers(message, text="used !warn_del:status [Варн успішно видалений]")
            mes = await message.reply("Варн успішно видалений",
                                      reply_markup=del_mute_kb(message.reply_to_message.from_user.id))
        else:
            logger.loggers(message, text="used !warn_del:status [Невірний номер варна]")
            mes = await message.reply("Невірний номер варна")
    else:
        await message.delete()
        reason = message.text.split(maxsplit=1)[1]
        num_warn = db.add_warn(message.chat.id, message.reply_to_message.from_user.id, reason)
        if num_warn == 1:
            hours = 6
        elif num_warn == 2:
            hours = 24 * 3
        else:
            hours = 24 * 9

        try:
            await app.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, ChatPermissions(),
                                           datetime.now() + timedelta(hours=hours))
        except (UserAdminInvalid, ChatAdminRequired):
            logger.loggers(message, text="used !warn: [варн додано, але у бота немає прав на мут]")
            mes1 = await message.reply('варн додано, але у бота немає прав на мут')
            punishment = "немає"
        except ChannelInvalid:
            logger.loggers(message, text="used !warn: [Варн доданий, але мут працює тільки в супергрупах]")
            mes1 = await message.reply('Варн доданий, але мут працює тільки в супергрупах')
            punishment = "немає"
        else:
            punishment = f"read-only {hours}год."
            logger.loggers(message,
                           text=f"used !warn: [Вам видано попередження. Всього Ви маєте:  {num_warn}\nПричина: {reason}\nПокарання: {punishment}]")
        mes = await app.send_message(message.chat.id,
                                     f"{message.reply_to_message.from_user.mention}, Вам було видано попередження\nКількість попереджень: {num_warn}\nПричина попередження: {reason}\nШтраф: {punishment}",
                                     reply_to_message_id=message.reply_to_message_id)
    try:
        await message.reply_to_message.delete()
    except Exception:
        pass
    await auto_delete.delete_command([mes, message, mes1])


@Client.on_message(filters.command(commands=["warn", "w"], prefixes=["/", "!"]) & costum_filters.group & ~filters.reply)
async def err_report(app: Client, message: Message):
    mes = await message.reply("На жаль, Ви не відповіли на повідомлення")
    messages = [mes, message]
    await auto_delete.delete_command(messages, 10)


@Client.on_message(
    filters.command(["info"], prefixes=["/", "!"]))
async def info(app: Client, message: Message):
    logger.loggers(message, text="used !info")
    chat = None
    if message.reply_to_message and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        user = message.reply_to_message.from_user
        if message.from_user.id not in config.admins:
            chat = message.chat.id
        else:
            chat = message.chat.id
    elif len(message.text.split()) > 1:
        if message.from_user.id not in config.admins:
            chat = message.chat.id
        user = await app.get_users(message.text.split()[1])
    else:
        user = message.from_user

    warns = db.get_warns(user.id, chat)
    text = f"Юзер: {user.mention}\nID: <code>{user.id}</code>"
    text_warns = []
    if not warns:
        text_warns = ["Варнів нема"]
    for chat_id in warns:
        chat = await app.get_chat(chat_id)
        chat = ("@" + chat.username) if chat.username else chat.title
        chat_warns = warns.get(chat_id)
        txt = [f"Чат: {chat}"]
        for num, warn in enumerate(chat_warns, start=1):
            txt.append(f"\t{num}. {warn}")
        text_warns.append("\n".join(txt))

    text_warns = '\n'.join(text_warns)
    mes = await message.reply(f"{text}\n\nВарни:\n{text_warns}\n")
    await auto_delete.delete_command([mes, message])


@Client.on_callback_query(filters.regex(r"unmute_\d+", re.I) & costum_filters.chat_admin_filter)
async def unmute(app: Client, callback_query: CallbackQuery):
    user = int(callback_query.data.split('_')[-1])
    try:
        await app.restrict_chat_member(callback_query.message.chat.id, user, callback_query.message.chat.permissions)
    except (UserAdminInvalid, ChatAdminRequired):
        await callback_query.message.edit(f"{callback_query.message.text}\n<i>У бота нема прав</i>")
        return
    await callback_query.message.edit(f"{callback_query.message.text}\nМут знято")
