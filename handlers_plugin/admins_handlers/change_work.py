import json
import os
import time

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

import config
from func import auto_delete
from func import logger
from keyboards.inline import repair_kb


# filters.user([1398764450, 666445915]

@Client.on_message(filters.command("repair") & filters.user(config.admins))
async def change_work(app: Client, message: Message):
    await message.reply("Оберіть потрібне", reply_markup=repair_kb())


@Client.on_callback_query(filters.regex("change_user_commands_work") & filters.user(config.admins))
async def change_work_query1(app: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    data["user_commands_work"] = data["user_commands_work"] is False
    with open(os.path.join("data", "settings.json"), "w") as f:
        json.dump(data, f)
    await callback_query.message.edit_reply_markup(repair_kb())


@Client.on_callback_query(filters.regex("change_admins_commands_work") & filters.user(config.admins))
async def change_work_query2(app: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    data["admins_commands_work"] = data["admins_commands_work"] is False
    with open(os.path.join("data", "settings.json"), "w") as f:
        json.dump(data, f)
    await callback_query.message.edit_reply_markup(repair_kb())


@Client.on_callback_query(filters.regex("change_all_commands_work") & filters.user(config.admins))
async def change_work_query3(app: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    data["user_commands_work"] = data["admins_commands_work"] = False if data['admins_commands_work'] and data[
        'user_commands_work'] else True
    with open(os.path.join("data", "settings.json"), "w") as f:
        json.dump(data, f)
    await callback_query.message.edit_reply_markup(repair_kb())


@Client.on_message(filters.command("ping"))
async def ping(app: Client, message: Message):
    logger.loggers(message, text="used !ping")
    a = time.time()
    mes = await message.reply("Pong!")
    b = time.time()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    await mes.edit(
        f"<b>Ping:</b> {round(b - a, 3)}sec.\nСтатус адмін команд: {'працює нормально' if data['admins_commands_work'] else 'тех. обслуговування'}\n"
        f"Статус юзер команд: {'працює нормально' if data['user_commands_work'] else 'тех. обслуговування'}")
    await auto_delete.delete_command([mes, message])
    return
