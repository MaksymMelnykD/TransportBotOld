from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

import costum_filters


@Client.on_callback_query(filters.regex("cancel") & costum_filters.state_filter("*"))
async def cancel(app: Client, callback_query: CallbackQuery):
    await callback_query.answer("Скасовано")
    await callback_query.message.edit("<b>Скасовано</b>")
    costum_filters.set_state(callback_query.message.chat.id, callback_query.from_user.id, None)
