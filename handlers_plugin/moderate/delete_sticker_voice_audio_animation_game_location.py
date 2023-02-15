from loguru import logger
from pyrogram import filters
from pyrogram import Client
import config
from func import logger

@Client.on_message(filters.chat(config.chat_dp_id) & (filters.voice | filters.audio | filters.sticker | filters.animation | filters.game | filters.location))
async def delete_sticker_voice_audio_animation_game_location(app, message):
	try:
		if message.sticker:
			logger.loggers(message, text="send sticker")
		elif message.voice:
			logger.loggers(message, text="send voice")
		elif message.audio:
			logger.loggers(message, text="send audio")
		elif message.animation:
			logger.loggers(message, text="send animation")
		elif message.game:
			logger.loggers(message, text="send game")
		elif message.location:
			logger.loggers(message, text="send location")
		await message.delete()
	except Exception as e:
		print(e)