import json
import logging
import os

from pyrogram import Client
from loguru import logger
import config
import db
from parsing.parse import transport_parse, electric_transport_parse, bus_parse_func
from schedulers import on_night_mode, off_night_mode, night_mode_scheduler, bus_parse_scheduler, \
    electric_transport_scheduler
logger.add("logs/logger.log", rotation="15 MB", level=5,
           backtrace=True, diagnose=True, enqueue=True)

if not os.path.exists(os.path.join("data", "night_messages.json")):
    with open(os.path.join("data", "night_messages.json"), "w") as f:
        f.write("{}")
if not os.path.exists(os.path.join("data", "settings.json")):
    with open(os.path.join("data", "settings.json"), "w") as f:
        settings = {"user_commands_work": True, "admins_commands_work": True}
        json.dump(settings, f)
if not os.path.exists(os.path.join("parsing", "photos")):
    os.mkdir(os.path.join("parsing", "photos"))

plugins = dict(
    root="handlers_plugin",
    include=[
        "admins_handlers.restart",
        "admins_handlers.change_work",
        "moderate.white_channel",
        "admins_handlers.get_statistics",
        "admins_handlers.change_work",
        "moderate.all_usr",
        "commands.start",
        "commands.stop",
        "commands.del",
        "admins_handlers.send_log",
        "transport_requests.bus_func",
        "transport_requests.electric_transport_func",
        "join_left_chat_member.self_join_left",
        "join_left_chat_member.left_chat_member",
        "join_left_chat_member.new_chat_members",
        "moderate.delete_sticker_voice_audio_animation_game_location",
        "moderate.forbidden_word",
        "moderate.white_link",
        "moderate.change_group_settings",
        "admins_handlers.parse_by_command",
        "moderate.report_warns",
        "commands.mailer",
        "commands.cancel",
    ]
)

app = Client(
    config.name_session,
    bot_token=config.TOKEN,
    api_id=config.api_id,
    api_hash=config.api_hash,
    plugins=plugins)
"""
-1001417204242 - Флуд из чата департамента транспорта Днепра.
-1001221698253 - Департамент транспорту ДМР (чат)
-1001334085013 - Департамент транспорту ДМР (канал)
"""

db.prepare_db()
for chat in db.get_all_chats():
    if chat[7] == 0:
        continue
    night_mode_scheduler.add_job(on_night_mode, "cron", args=(chat[0], app), id=f"{chat[0]}_start",
                                 hour=chat[5].split()[0], minute=chat[5].split()[1])
    night_mode_scheduler.add_job(off_night_mode, "cron", args=(chat[0], app), id=f"{chat[0]}_stop",
                                 hour=chat[6].split()[0], minute=chat[6].split()[1])
logger.info('------------------------------')
logger.info('Prepearing a telegram bot')
night_mode_scheduler.start()
bus_parse_scheduler.add_job(bus_parse_func, "interval", hours=2)
bus_parse_scheduler.start()
electric_transport_scheduler.add_job(
    electric_transport_parse, "cron", hour=4, minute=0)
electric_transport_scheduler.add_job(
    electric_transport_parse, "cron", hour=13, minute=0)
electric_transport_scheduler.start()
try:
    db.add_transport(transport_parse())
except Exception as e:
    logger.exception(e)

logger.info('Starting a telegram bot')
app.run()
