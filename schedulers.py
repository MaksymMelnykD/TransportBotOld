import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.types import ChatPermissions

import db


async def on_night_mode(chat_id: int, app: Client):
    try:
        await app.set_chat_permissions(chat_id, ChatPermissions(
            can_send_messages=False,  # Запрещено отправлять текстовые сообщения, контакты, места и места
            can_send_media_messages=False,
            # Запрещено отправлять аудио, документы, фотографии, видео, видеозаметки и голосовые заметки
            can_send_other_messages=False,  # Запрещено отправлять анимации, игры, стикеры
            can_send_polls=False,  # Запрещено отправлять опросы
            can_add_web_page_previews=False,  # Запрещено добавлять превью веб-страницы
            can_change_info=False,  # Запрещено изменять заголовок чата, фото и другие настройки
            can_invite_users=True,  # Разрешено приглашать новых пользователей в чат.
            can_pin_messages=False)  # Запрещено закреплять сообщения
                                       )
        message = await app.send_message(chat_id,
                                         f"""<b>Попри те, що комендантська година починається за годину - чат зачиняється о 23:00. Транспорт у цей час вже не працює.
Робота чату буде відновлена по закінченню комендантської години - о 5 ранку.
З розкладами руху можна ознайомитись за посиланням -  [<a href="https://t.me/DepTransDMR/109820">Натисніть, щоб перейти</a>]

Закликаємо дотримуватися правил особистої безпеки. Все буде Україна!
🇺🇦 Допомагаємо ЗСУ 🇺🇦 ! Разом ми переможемо! 🇺🇦
Слава Україні!
</b>
З розкладами ознайомитись можно за посиланням - [<a href="https://t.me/DepTransDMR/109820">Натисніть, щоб перейти</a>]
Щоб дізнатись розклад автобусного/трамвайного/тролейбусного маршруту напишіть особисто боту.
        """, disable_web_page_preview=True)

        with open(os.path.join("data", "night_messages.json"), "r") as f:
            message_ids = json.load(f)
        message_ids.update({str(chat_id): message.id})
        with open(os.path.join("data", "night_messages.json"), "w") as f:
            json.dump(message_ids, f)
    except Exception as e:
        print(e)


# Отключение ночного режима
async def off_night_mode(chat_id: int, app: Client):
    try:
        await app.set_chat_permissions(chat_id, ChatPermissions(
            can_send_messages=True,  # разрешено отправлять текстовые сообщения, контакты, места и места
            can_send_media_messages=True,
            # разрешено отправлять аудио, документы, фотографии, видео, видеозаметки и голосовые заметки
            can_send_other_messages=True,  # разрешено отправлять анимации, игры, стикеры
            can_send_polls=True,  # разрешено отправлять опросы
            can_add_web_page_previews=True,  # разрешено добавлять превью веб-страницы
            can_change_info=False,  # Запрещено изменять заголовок чата, фото и другие настройки
            can_invite_users=True,  # разрешено приглашать новых пользователей в чат.
            can_pin_messages=False)  # Запрещено закреплять сообщения
                                       )
        with open(os.path.join("data", "night_messages.json"), "r") as f:
            message_ids = json.load(f)
        await app.delete_messages(int(chat_id), int(message_ids[str(chat_id)]))
    except Exception as e:
        print(e)


night_mode_scheduler = AsyncIOScheduler(timezone="Europe/Kiev")

bus_parse_scheduler = AsyncIOScheduler(timezone="Europe/Kiev")


electric_transport_scheduler = BackgroundScheduler(timezone="Europe/Kiev")


