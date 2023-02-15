import datetime
import io
import os

from pandas import Series, DataFrame

import costum_filters
from func import logger
import random
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InputMediaDocument
import pandas as pd
import config
from keyboards.inline import stats_kb, cancel_keyboard

names = {"trol": "Тролейбус", "tram": "Трамвай", "bus": "Автобус"}


def create_files_in_memort(df: DataFrame):
    df_bus = df[df.transport == "bus"].groupby("num")["num"].count().sort_values(ascending=False)
    df_tram = df[df.transport == "tram"].groupby("num")["num"].count().sort_values(ascending=False)
    df_trol = df[df.transport == "trol"].groupby("num")["num"].count().sort_values(ascending=False)
    transport = [df_trol, df_tram, df_bus]
    output_files = []
    for i in range(len(transport)):
        output = io.BytesIO()
        data = transport[i].to_dict()
        name = list(names.values())[i]
        for element in data:
            output.write(f"{name} {element}: {data.get(element)}\n".encode("utf-8"))
        output.name = f"{list(names.keys())[i]}.txt"
        output_files.append(InputMediaDocument(output))
    output_files_copy = output_files.copy()
    for i in output_files_copy:
        media = i.media
        media.seek(0)
        if media.read() == b"":
            output_files.pop(output_files.index(i))
    return output_files


@Client.on_message(filters.command("stats") & filters.user(config.admins))
async def stat(app: Client, message: Message):
    await message.reply("Оберіть проміжок за який ви хочете дізнатися статистику", reply_markup=stats_kb())


@Client.on_callback_query(filters.regex(r"stat_.+") & filters.user(config.admins))
async def send_stats(app: Client, callback_query: CallbackQuery):
    df = pd.read_csv(logger.statistics_log_path, sep=',')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.set_index(['date'])
    callback_data = callback_query.data
    if callback_data.endswith("costum_stat"):
        await callback_query.message.edit("Введіть діапазон дат\n<b>Формат:</b> <code>ДД/ММ/ГГ-ДД/ММ/ГГ</code>",
                                          reply_markup=cancel_keyboard)
        costum_filters.set_state(callback_query.message.chat.id, callback_query.from_user.id, "date_range")
        return

    elif callback_data.endswith("today"):
        start_date = end_date = datetime.datetime.date(datetime.datetime.now()).strftime("%Y-%m-%d")
    elif callback_data.endswith("yesterday"):
        start_date = end_date = datetime.date.fromordinal(datetime.datetime.today().toordinal() - 1).strftime(
            "%Y-%m-%d")
    elif callback_data.endswith("this_month"):
        next_month = datetime.datetime.now().replace(day=28) + datetime.timedelta(days=4)
        next_month = next_month - datetime.timedelta(days=next_month.day)
        end_date = next_month.strftime("%Y-%m-%d")
        start_date = next_month.replace(day=1).strftime("%Y-%m-%d")
    elif callback_data.endswith("last_month"):
        prev_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)
        end_date = prev_month.strftime("%Y-%m-%d")
        start_date = prev_month.replace(day=1).strftime("%Y-%m-%d")
    else:
        start_date = end_date = None
    df = df.sort_index().loc[start_date:end_date]
    output_files = create_files_in_memort(df)
    if not output_files:
        await callback_query.message.edit("На обраному часовому проміжку не знайдено запитів")
        return
    await app.send_media_group(callback_query.message.chat.id, output_files)
    await callback_query.message.delete()


@Client.on_message(costum_filters.state_filter("date_range"))
async def read_date_range(app: Client, message: Message):
    date_range = message.text.replace(' ', "")
    date_range = date_range.split("-")
    try:
        start_date = datetime.datetime.strptime(date_range[0], '%d/%m/%y').strftime("%Y-%m-%d")
        end_date = datetime.datetime.strptime(date_range[1], '%d/%m/%y').strftime("%Y-%m-%d")
    except Exception:
        await message.reply("Невірний формат\n<b>Формат:</b> <code>ДД/ММ/ГГ-ДД/ММ/ГГ</code>\nВведіть ще раз",reply_markup=cancel_keyboard)
        return
    df = pd.read_csv(logger.statistics_log_path, sep=',')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.set_index(['date'])
    df = df.sort_index().loc[start_date:end_date]
    output_files = create_files_in_memort(df)
    if not output_files:
        await message.reply("На обраному часовому проміжку не знайдено запитів")
        return
    await app.send_media_group(message.chat.id, output_files)
