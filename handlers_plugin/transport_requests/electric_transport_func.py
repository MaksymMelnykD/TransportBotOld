import asyncio
import os
import re
from typing import List

from loguru import logger
from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery, InputMediaPhoto

import costum_filters
import func.translit
from func import auto_delete
from keyboards.inline import electric_transport_kb
from func import logger


async def message_deleter(messages: List[Message], time: int = 30):
    await asyncio.sleep(time)
    if messages[0].id in transport_requests:
        for message in messages:
            try:
                await message.delete()
            except Exception:
                pass


transport_requests = {}

troll_nn = r"(^|\b)((тро(лл|л)ейбус +(\d+|А|Б))|(трамвай +\d+))|(((\d+|А|Б) +тро(лл|л)ейбус)|(\d+ +трамвай))(^|\b)"


@Client.on_message(filters.regex(troll_nn, re.I) & costum_filters.user_command & costum_filters.not_parse)
async def tram_troll_request(app: Client, message: Message):
    for match in message.matches:
        logger.loggers(message, text=f"Электротранспорт = {match.group()}")
        num = None
        names = {"троллейбус": "trol", "тролейбус": "trol", "трамвай": "tram"}
        letters = {"б": "b", "а": "a"}
        for element in match.group().split():
            if element.isdigit() or element.lower() in letters:
                num = letters.get(element.lower(), None) or element
            else:
                name = names.get(element.lower())
        kb = electric_transport_kb(name, num)
        if kb is None:
            photo = list(filter(lambda x: x.startswith(f"{num}{name}"), os.listdir(os.path.join("parsing", "photos"))))
            if not photo:
                return
            else:
                logger.log_transport(name, num.lower(), message.from_user.id)
                photo = os.path.join("parsing", "photos", photo[0])
                caption = ''
        else:
            logger.log_transport(name, num.lower(), message.from_user.id)
            photo = os.path.join("data", "stop_choose.png")
            caption = ""
        mes = await app.send_photo(message.chat.id, photo,
                                   caption=caption,
                                   reply_to_message_id=message.reply_to_message_id or message.id,
                                   parse_mode=ParseMode.HTML,
                                   reply_markup=kb)
        if message.text == match.group():
            transport_requests.update({mes.id: [message.from_user.id, message]})
        else:
            transport_requests.update({mes.id: [message.from_user.id]})
        messages = [mes]
        if message.text == match.group():
            messages.append(message)
        asyncio.create_task(message_deleter(messages))


@Client.on_callback_query(filters.regex(r"(\d+|a|b)(trol|tram)", re.I))
async def change_stop(app: Client, callback_query: CallbackQuery):
    user = transport_requests.get(callback_query.message.id, None)
    if user:
        if user[0] == callback_query.from_user.id:
            transport_requests.pop(callback_query.message.id)
        else:
            await callback_query.answer("Це не для вас")
            return
    del_kb = True
    text = callback_query.data.replace(callback_query.matches[0].group(), '')
    text = func.translit.translit(text, True).replace('"', "'").replace("\\", "бслеш").replace("/", "слеш")
    photo = os.path.join("parsing", "photos", callback_query.matches[0].group() + text + '.png')
    if del_kb:
        await callback_query.message.edit_reply_markup(None)
    await callback_query.message.edit_media(InputMediaPhoto(photo))
    await auto_delete.delete_timetable(
        [callback_query.message, user[1] if user and len(user) > 1 else None])
