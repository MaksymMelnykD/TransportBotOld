import json
import os
import re
import time
from datetime import timedelta, datetime
from typing import Union, Optional

from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram import filters, types, Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import CallbackQuery, Message

import db
from func import global_vars, auto_delete


async def link_filter_func(_, client: Client, message: types.Message):
    if not message.text and not message.caption:
        return False
    else:
        text = (message.text or message.caption).lower()
    if not message.entities:
        return False
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False
    if db.get_links_whitelist_status(message.chat.id) is False:
        return False
    if message.from_user.id in db.get_chat_admins(message.chat.id, int_list=True):
        return False
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user and user.status is ChatMemberStatus.OWNER or (user.privileges and user.privileges.can_promote_members):
        db.add_admin(message.chat.id, message.from_user.id)
        return False
    good_links = db.get_chat_links_whitelist(message.chat.id, raw_links=True)
    for entity in message.entities:
        if entity.url:
            link = entity.url.split('//')[-1].replace("/", "") if entity.url.split('//')[-1][-1] == "/" else \
                entity.url.split('//')[-1]
            if link not in good_links:
                return True
        elif entity.type == MessageEntityType.URL:
            link_in_text = text[entity.offset:entity.length + entity.offset]
            if link_in_text.split('//')[-1] not in good_links:
                return True
        elif entity.type == MessageEntityType.MENTION:
            pass
    return False


link_filter = filters.create(link_filter_func)


async def words_blacklist(_, client, message: types.Message):
    if not message.text and not message.caption:
        return False
    else:
        text = message.text or message.caption
        text = text.lower()
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return False
    if message.from_user.id in db.get_chat_admins(message.chat.id, int_list=True):
        return False
    try:
        chat_user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if (chat_user.status and chat_user.status is ChatMemberStatus.OWNER) or (
                chat_user.privileges and chat_user.privileges.can_promote_members):
            db.add_admin(message.chat.id, message.from_user.id)
            return False

    except Exception:
        pass

    blacklist = db.get_chat_blacklist(message.chat.id)
    if not blacklist:
        return False
    for i in range(0, len(blacklist)):
        if blacklist[i] == "" or blacklist[i] == " ":
            blacklist.pop(i)
    for word in blacklist:
        if re.search(rf"(\W|\b){word}(\W|\b)", text, flags=re.I):
            print(re.search(rf"(\W|\b){word}(\W|\b)", text, re.I))
            return True
    return False


words_blacklist_filter = filters.create(words_blacklist)


async def chat_admin(_, client: Client, message: types.Message):
    if isinstance(message, CallbackQuery):
        chat = message.message.chat.id
    elif isinstance(message, Message):
        chat = message.chat.id
    else:
        raise ValueError(f"This filter doesn't work with {type(message)}")
    if message.from_user.id in db.get_chat_admins(chat, int_list=True):
        return True
    user = await client.get_chat_member(chat, message.from_user.id)
    if user.status is ChatMemberStatus.OWNER or (user.privileges and user.privileges.can_promote_members):
        db.add_admin(chat, message.from_user.id)
        return True
    else:
        if isinstance(message, CallbackQuery):
            await message.answer("Вибачайте, ця команда працює тільки для адміністрації чату", show_alert=True)
        elif isinstance(message, Message):
            mes = await message.reply("Вибачте, але ця команда працює виключно для адміністрації чату.")
            await auto_delete.delete_command([mes, message])
        return False


chat_admin_filter = filters.create(chat_admin)


async def work_user_command(_, client: Client, message: Message):

    # Бан пользователей ТУТ
    if message.from_user.id in [1398764450, 5262827959, 666445915, 499291442]:
        return False

    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    status = data["user_commands_work"]
    if status is False:
        if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            await message.reply("Вибачте, але ця функція тимчасово недоступна. Проводиться оновлення даних.")
        return False
    else:
        return True


user_command = filters.create(work_user_command)


async def work_admin_command(_, client: Client, message: Message):
    with open(os.path.join("data", "settings.json"), "r") as f:
        data = json.load(f)
    status = data["admins_commands_work"]
    if status is False:
        await message.reply("Вибачте, але ця функція тимчасово недоступна. Проводиться оновлення даних.")
        return False
    else:
        return True


admin_command = filters.create(work_admin_command)

states = {}
infos = {}


def state_filter(conversation_level):
    def func(_, __, message: Message):
        if isinstance(message, CallbackQuery):
            chat_id = message.message.chat.id
        else:
            chat_id = message.chat.id
        data = states.get(f"{message.from_user.id};{chat_id}")
        if data and conversation_level == "*":
            return True
        return data == conversation_level

    return filters.create(func, "ConversationFilter")


def set_state(chat_id: int, user_id: int, state: Optional[str]):
    if state is None:
        states.pop(f"{user_id};{chat_id}")
    else:
        states.update({f"{user_id};{chat_id}": state})


def update_data(chat_id: int, user_id: int, **data):
    infos.update({f"{user_id};{chat_id}": {**data}})


def get_data(chat_id: int, user_id: int):
    return infos.get(f"{user_id};{chat_id}")


async def parse_filter(_, client, message: types.Message):
    if global_vars.status.get_parsing_status():
        mes = await message.reply(
            "Проводиться оновлення даних. Будь ласка, повторіть спробу запиту за 2-3 хвилини. Дякуємо.")
        await auto_delete.delete_command([mes], 15)
        return False
    else:
        return True


not_parse = filters.create(parse_filter)


async def group_filter(_, client, message: types.Message):
    if not await filters.group_filter(_, client, message):
        await message.reply("Просимо вибачення, але ця команда працює тільки в чатах. Дякуємо за розуміння.")
        return False
    else:
        return True


group = filters.create(group_filter)
