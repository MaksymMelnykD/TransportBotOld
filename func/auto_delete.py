import asyncio
from typing import List, Union, Tuple

from pyrogram.enums import ChatType
from pyrogram.types import Message

import db


async def delete_command(messages_: Union[Message, List[Message], Tuple[Message]], time: int = None):
    async def delete_command_func(messages: List[Message]):
        a = None
        for i in messages_:
            if i is None:
                continue
            else:
                a = i
                break
        if a and a.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            if not db.check_chat(messages[0].chat.id):
                return
            if time is None:
                seconds = db.get_auto_delete_commands_time(messages[0].chat.id)
                if seconds == 0:
                    return
            else:
                seconds = time
            await asyncio.sleep(seconds)
            for message in messages:
                if message:
                    try:
                        await message.delete()
                    except Exception:
                        pass

    if isinstance(messages_, Message):
        messages_ = [messages_]
    asyncio.create_task(delete_command_func(messages_))


async def delete_timetable(messages_: Union[Message, List[Message], Tuple[Message]], time: int = None):
    async def delete_timetable_func(messages: List[Message]):
        if messages[0].chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            if time is None:
                seconds = db.get_auto_delete_timetables_time(messages[0].chat.id)
                if seconds == 0:
                    return
            else:
                seconds = time
            await asyncio.sleep(seconds)
            for message in messages:
                if message:
                    try:
                        await message.delete()
                    except Exception as e:
                        print(e)
    if isinstance(messages_, Message):
        messages_ = [messages_]
    asyncio.create_task(delete_timetable_func(messages_))
