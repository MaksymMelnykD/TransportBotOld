import json
from typing import Literal, Optional
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from func.translit import translit


def electric_transport_kb(transport: Literal["trol", "tram"], num: str) -> Optional[InlineKeyboardMarkup]:
    files = list(filter(lambda x: x.startswith(f"{num}{transport}"), os.listdir(os.path.join("parsing", "photos"))))
    if len(files) == 1:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join("parsing", "photos", x)))
    kb = []
    for file in files:
        file = file.replace(".png", "").replace("'", '"').replace("бслеш", "\\").replace("слеш", "/")
        name = file.split('_')
        name = f"{name[1]} {('(до ' + name[2] + ')') if name[2] != '' else ''}"
        file = translit(file)
        button = InlineKeyboardButton(name, callback_data=file)
        kb.append([button])
    return InlineKeyboardMarkup(kb) if kb else None


def del_mute_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton("Зняти мут", callback_data=f"unmute_{user_id}")]]
    return InlineKeyboardMarkup(kb)


def donate_kb() -> Optional[InlineKeyboardMarkup]:
    if config.donate_link == "":
        return None
    kb = [[InlineKeyboardButton("Донатити", url=config.donate_link)]]
    return InlineKeyboardMarkup(kb)


def stats_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton("За сьогодні", callback_data="stat_today"),
         InlineKeyboardButton("За вчора", callback_data="stat_yesterday")],
        [InlineKeyboardButton("За цей місяць", callback_data="stat_this_month"),
         InlineKeyboardButton("За минулий місяць", callback_data="stat_last_month")],
        [InlineKeyboardButton("За увесь час", callback_data="stat_all_time")],
        [InlineKeyboardButton("Довільний проміжок часу", callback_data="stat_costum_stat")]
    ]
    return InlineKeyboardMarkup(kb)


cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Скасувати", callback_data="cancel")]])


def repair_kb() -> InlineKeyboardMarkup:
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    kb = [
        [InlineKeyboardButton(f"{'🟢Вимкнути' if data['user_commands_work'] else '🔴Увімкнути'} юзер команди",
                              callback_data="change_user_commands_work")],
        [InlineKeyboardButton(f"{'🟢Вимкнути' if data['admins_commands_work'] else '🔴Увімкнути'} адмін команди",
                              callback_data="change_admins_commands_work")],
        [InlineKeyboardButton(f"{'Вимкнути' if data['admins_commands_work'] and data['user_commands_work']  else 'Увімкнути'} всі команди",
                              callback_data="change_all_commands_work")],
    ]
    return InlineKeyboardMarkup(kb)
