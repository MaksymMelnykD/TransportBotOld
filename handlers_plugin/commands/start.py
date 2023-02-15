from loguru import logger
from pyrogram import filters, enums
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message

import db
from func import auto_delete
from func import logger
from keyboards import inline


@Client.on_message(filters.command("start"))
async def start(app, message: Message):
    logger.loggers(message, text="used !start is private chat")
    mes_text = '''Для здійснення запиту розкладу автобуса - напишіть наступну команду:
Автобус [номер маршруту]
— Автобус 151а
— Автобус 77
— Автобус 1
Для здійснення запиту розкладу тролейбуса - напишіть наступну команду:
Тролейбус [номер маршруту]
— Тролейбус 1
— Тролейбус 5
— Тролейбус Б
Для здійснення запиту розкладу трамвая - напишіть наступну команду:
Трамвай [номер маршруту]
— Трамвай 1
— Трамвай 9
— Трамвай 19
Для здійснення запиту про команди для адміністрації груп, напишить /help'''
    if inline.donate_kb():
        mes_text += "\n\nВи можете підтримати ЗСУ за кнопкою нижче"
    if message.chat.type is ChatType.PRIVATE:
        db.add_user(message.from_user.id)
        if db.get_user_mail(message.from_user.id) is False:
            mes_text += "\nДля отримання актуальної інформації про зміни руху транспорту Ви можете здійснити підписку на розсилку командою /mail"
    elif message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        if db.check_chat(message.chat.id):
            administrators = []
            async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                administrators.append(m.user.id)
            db.add_chat(message.chat.id, administrators)
    mes = await app.send_message(message.chat.id, mes_text, reply_markup=inline.donate_kb())
    await auto_delete.delete_command([message, mes])
