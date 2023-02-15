import json
import os
import time

from pyrogram import Client, filters
from pyrogram.types import Message

import config
from func import auto_delete
from func import logger


@Client.on_message(filters.command("repair") & filters.user([]))
async def change_work(app: Client, message: Message):
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    data["work"] = data["work"] is False
    with open(os.path.join("data", "settings.json"), "w") as f:
        json.dump(data, f)
    await message.reply(
        f"Успешно изменён режим: {'бот работает нормально' if data['work'] else 'бот на тех обслуживании'}")
    try:
        if data["work"] is False:
            await app.send_message(config.chat_dp_id,
                               "Вибачте, але бот тимчасово не експлуатується\n\nз однієї або кількох причин:\n-- Вийшла з ладу одна з функцій\n-- профілактичні виправлення текстів\n-- Оновлення даних та/або конфігурації, коду бота.")
    except Exception as e:
        print(e)


@Client.on_message(filters.command("ping"))
async def ping(app: Client, message: Message):
    a = time.time()
    mes = await message.reply("Pong!")
    b = time.time()
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    await mes.edit(
        f"<b>Ping:</b> {round(b - a, 3)}sec.\nСтатус: {'бот працює нормально' if data['work'] else 'бот на тех. обслуговуванні'}")
    await auto_delete.delete_command([mes, message])
    return
