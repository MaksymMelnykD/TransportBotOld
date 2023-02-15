import os
from datetime import datetime

from loguru import logger


def loggers(message, text):
    logger.trace(
        f'chat_id = {message.chat.id} | user_id = {message.from_user.id} | first_name = {message.from_user.first_name} | last_name = {message.from_user.last_name} | {text}')


statistics_log_path = os.path.join("data", "statistics.csv")
if os.path.exists(statistics_log_path) is False:
    with open(statistics_log_path, 'w', encoding="utf-8") as file:
        file.write("date,id,transport,num\n")


def log_transport(transport, num, user_id):
    date = datetime.date(datetime.now()).strftime("%d-%m-%y")
    with open(statistics_log_path, "a", encoding="utf-8") as f:
        f.write(f"{date},{user_id},{transport},{num}\n")
