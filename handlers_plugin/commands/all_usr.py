from loguru import logger
from pyrogram import filters
from pyrogram import Client
import conf
import sqlite3

@Client.on_message()
async def dels(сlient, message):
	#logger.info(f'user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !del')
	#logger.info(f'chat_id = {message.chat.id} | user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | used !del')