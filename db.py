import json
import os
import pymysql
import sys
from pprint import pprint
from typing import List, Union, Tuple, Optional
import pymysql
import config


class ConnectionData:
    with open(os.path.join("data", "db_password.json")) as f:
        data = json.load(f)
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            connection_data = data["test"]
        else:
            connection_data = data["default"]
    else:
        connection_data = data["default"]


connection_data = ConnectionData()

words_blacklist = ["жид", "хач", "даун", "аутист", "калека", "мудак", "смиття", "смитя", "сміття", "смітя",
                   "издевательство", "обкурились", "скотское", "скотское", "эуропа", "мы вас кормим", "cкотовозка",
                   "душегубка", "душекубках", "Крысы", "Душегубку", "душегубке", "душегубки", "Маршрутное такси",
                   "душегубках", "Скотовозках", "издеваетесь", "издеваетесь", "бричка", "брычка", "издевательства",
                   "хуевый", "хуёвый", "пыточная", "аквариум", "аквариумы", "дрова", "скот", "вяканья", "свинарник",
                   "Свинарнике", "Обосрался", "Дерьмо", "Аквариума", "помои", "сука", "уроды", "корыто", "беспредел",
                   "беспридел", "безпредел", "безпридел", "Издеваться", "геноцид", "смитутю", "смиттутю", "телеги",
                   "скотовозками", "неадекватный", "букмекерская", "лоховозка", "лоховозка", "иихаил тонконогий",
                   "керманычей", "скотовоз", "тонконогий", "тонконог", "тупого", "тупой", "дебил", "корыта", "корытам",
                   "долбаный", "свинья", "чушь", "водиле", "свинство", "издевательство", "дебилы", "@PribatBank24_bot", "поширити"]
default_admins = [29764093, 594165498, 456401560]
links_whitelist = ["https://dniprorada.gov.ua", "https://t.me/DepTrDMR", "https://t1p.de/9y1xc", "https://t1p.de/cp4p",
                   "https://det-dnipro.dp.ua", "https://metro.dp.ua"]
report_chat_dp = -621426266


def prepare_db():
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS chats(
            id BIGINT PRIMARY KEY,
            admins TEXT,/*admin1 admin2 admin3*/
            links_whitelist TEXT,/*link1;link2;link3*/
            links_whitelist_status BOOL, /*1-вкл, 0-выкл*/
            words_blacklist TEXT,/*word1;word2;word3*/
            night_mode_on VARCHAR(5),/*23 00*/
            night_mode_off VARCHAR(5),/*5 00*/
            night_mode_status BOOL, /*1-вкл, 0-выкл*/
            report_chat BIGINT,/*если 0 то отправляется всем админам*/
            auto_delete_commands_time INTEGER,/*время автоудаления команд в сек, 0 = не удалять*/
            auto_delete_timetables_time INTEGER/*время автоудаления расписания в сек, 0 = не удалять*/
            );/*Это просто были примеры*/""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS warns(
            chat_id BIGINT,
            user_id BIGINT,
            warns TEXT); /*warn1;;warn2;;warn3*/""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(id BIGINT PRIMARY KEY,
            mail BOOL);""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS buses(
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            num_route TINYTEXT, /* номер маршрута, если есть буква, то в нижнем регистре*/
            way_place TEXT, /*шлях прямування, также как и в таблице*/
            way_time TEXT, /*время первого и последнего рейса, также как и в таблице, но без доп инфы*/
            different_time_data TEXT, /*если есть обозначения дня недели(выходной, рабочие и тд), иначе None*/
            intervals TEXT, /*если 3 последних калони разделены, пример данных 20;15;20, иначе None*/
            interval_data TEXT, /*текст который записан в трёх последних колонках, при условии что они объеденины, иначе None*/
            work BOOL /*1-работает, 0-не работает*/
            );""")
            # conn.commit()
            cursor.execute("SELECT * FROM chats WHERE id=%s",
                           (config.chat_dp_id,))
            chat = cursor.fetchone()
            if chat is not None:
                return
            args = (
                config.chat_dp_id, ' '.join(
                    list(map(str, default_admins))), ';'.join(links_whitelist), 1,
                ';'.join(words_blacklist), '23 00', '5 00', 1, report_chat_dp, 120, 900)
            cursor.execute(
                """INSERT INTO chats VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", args)
            conn.commit()


def add_transport(transport_list: Union[List[Union[Tuple, List]], Tuple[Union[Tuple, List]]], del_all=True):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            if del_all:
                cursor.execute("""DELETE FROM buses""")
            for data in transport_list:
                cursor.execute(
                    """INSERT INTO buses VALUES(%s, %s, %s, %s, %s, %s, %s)""", data)
            conn.commit()


def get_transport(num_route: str) -> Optional[List]:
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT num_route,way_place,way_time,different_time_data,intervals,interval_data,work FROM buses WHERE num_route = %s""",
                           (num_route,))
            return cursor.fetchall()


def get_similar_transport(route: str):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT num_route, work FROM buses WHERE num_route LIKE %s""",
                           (route+"%",))
            nums = []
            for i in cursor.fetchall():
                if i[1] == 1:
                    nums.append(i[0])
            return nums


def get_all_nums() -> List:
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT num_route FROM buses""")
            nums = []
            for i in cursor.fetchall():
                nums.append(i[0])
            return nums


def add_user(user_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if user is None:
                cursor.execute(
                    "INSERT INTO users Values (%s, %s)", (user_id, False))
                conn.commit()
                return True
            else:
                return False


def add_chat(chat_id: int, admins: List, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM chats WHERE id=%s", (chat_id,))
            chat = cursor.fetchone()
            if chat is None:
                if chat_id != config.chat_dp_id:
                    args = (chat_id, ' '.join(list(map(str, admins))), '', 0,
                            '', '23 00', '5 00', 0, 0, 0, 0)
                else:
                    args = (
                        config.chat_dp_id, ' '.join(
                            list(map(str, default_admins))),
                        ';'.join(links_whitelist), 1,
                        ';'.join(words_blacklist), '23 00', '5 00', 1, report_chat_dp, 600, 3600)
                cursor.execute(
                    """INSERT INTO chats VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", args)
                conn.commit()
                return True
            else:
                return False


def del_chat(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""DELETE FROM chats WHERE id = %s""", (chat_id,))
            conn.commit()


def get_all_chats():
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM chats""")
            return cursor.fetchall()


def check_chat(chat_id: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM chats WHERE id=%s", (chat_id,))
            return cursor.fetchone()


#################################


def add_admin(chat_id: int, admin_id, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            admins = get_chat_admins(chat_id, int_list=False)
            if str(admin_id) in admins:
                return False
            admins.append(str(admin_id))
            cursor.execute(
                """UPDATE chats SET admins = %s WHERE id = %s""", (' '.join(admins), chat_id))
            conn.commit()
            return True


def get_chat_admins(chat_id: int, int_list: bool = True, ) -> Union[List[str], List[int]]:
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT admins FROM chats WHERE id=%s", (chat_id,))
            admins = cursor.fetchone()
            if admins is None:
                add_chat(chat_id, [])
                return []
            admins = admins[0]
            admins = admins.split()
            a = False
            for admin in admins:
                if not admin.isdigit():
                    a = True
                    admins.pop(admins.index(admin))
            if a:
                cursor.execute(
                    "UPDATE chats SET admins = %s WHERE id = %s", (' '.join(admins), chat_id))
            if int_list:
                return list(map(int, admins))
            return admins


def del_admin(chat_id: int, admin_id, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            admins = get_chat_admins(chat_id, int_list=False)
            try:
                index = admins.index(str(admin_id))
            except ValueError:
                return False
            admins.pop(index)
            cursor.execute(
                """UPDATE chats SET admins = %s WHERE id = %s""", (' '.join(admins), chat_id))
            conn.commit()
            return True


#########################


def get_chat_blacklist(chat_id: int, ) -> List[str]:
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT words_blacklist FROM chats WHERE id=%s", (chat_id,))
            blacklist = cursor.fetchone()[0]
            if blacklist == '':
                return []
            return blacklist.split(';')


def add_word_to_blacklist(chat_id: int, word: str, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            words_blacklist = get_chat_blacklist(chat_id)
            word = word.strip()
            if str(word) in words_blacklist:
                return False
            words_blacklist.append(word)
            cursor.execute("""UPDATE chats SET words_blacklist = %s WHERE id = %s""",
                           (';'.join(words_blacklist), chat_id))
            conn.commit()
            return True


def del_word_from_blacklist(chat_id: int, word: str, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            words_blacklist = get_chat_blacklist(chat_id)
            word = word.strip()
            try:
                index = words_blacklist.index(word)
            except ValueError:
                return False
            words_blacklist.pop(index)
            cursor.execute("""UPDATE chats SET words_blacklist = %s WHERE id = %s""",
                           (';'.join(words_blacklist), chat_id))
            conn.commit()
            return True


######################


def get_chat_links_whitelist(chat_id: int, raw_links: bool = False, ) -> List[str]:
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT links_whitelist FROM chats WHERE id=%s", (chat_id,))
            links_whitelist = cursor.fetchone()[0]
            if links_whitelist == '':
                return []
            links = links_whitelist.split(';')
            if raw_links:
                links = list(map(lambda x: x.split('//')[-1], links))
            return links


def add_link_to_whitelist(chat_id: int, link: str, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            links_whitelist = get_chat_links_whitelist(chat_id)
            link = link.strip()
            if str(link) in links_whitelist:
                return False
            links_whitelist.append(link)
            cursor.execute("""UPDATE chats SET links_whitelist = %s WHERE id = %s""",
                           (';'.join(links_whitelist), chat_id))
            conn.commit()
            return True


def del_link_from_whitelist(chat_id: int, link: str, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            links_whitelist = get_chat_links_whitelist(chat_id)
            link = link.strip()
            try:
                index = links_whitelist.index(link)
            except ValueError:
                return False
            links_whitelist.pop(index)
            cursor.execute("""UPDATE chats SET links_whitelist = %s WHERE id = %s""",
                           (';'.join(links_whitelist), chat_id))
            conn.commit()
            return True


def get_links_whitelist_status(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT links_whitelist_status FROM chats WHERE id = %s""", (chat_id,))
            return bool(cursor.fetchone()[0])


def enable_links_whitelist_mode(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET links_whitelist_status = %s WHERE id = %s""", (1, chat_id))
            conn.commit()


def disable_links_whitelist_mode(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET links_whitelist_status = %s WHERE id = %s""", (0, chat_id))
            conn.commit()


######################


def get_night_mode(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT night_mode_on, night_mode_off, night_mode_status FROM chats WHERE id = %s""",
                           (chat_id,))
            return cursor.fetchone()


def change_night_mode_time(chat_id: int, change: str, set_time: str, ):
    """Argument "change" can be only "start" or "stop\""""
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            if change == 'start':
                cursor.execute(
                    """UPDATE chats SET night_mode_on = %s WHERE id = %s""", (set_time, chat_id))
            elif change == 'stop':
                cursor.execute(
                    """UPDATE chats SET night_mode_off = %s WHERE id = %s""", (set_time, chat_id))
            else:
                return False
            conn.commit()
            return True


def enable_night_mode(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET night_mode_status = %s WHERE id = %s""", (1, chat_id))
            conn.commit()


def disable_nigh_mode(chat_id: int, ):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET night_mode_status = %s WHERE id = %s""", (0, chat_id))
            conn.commit()


###############

def get_report_chat(chat_id: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT report_chat FROM chats WHERE id = %s""", (chat_id,))
            return cursor.fetchone()[0]


def set_report_chat(chat_id: int, report_chat: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET report_chat = %s WHERE id = %s""", (report_chat, chat_id))
            conn.commit()


###############

def get_auto_delete_commands_time(chat_id: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT auto_delete_commands_time FROM chats WHERE id = %s""", (chat_id,))
            return cursor.fetchone()[0]


def get_auto_delete_timetables_time(chat_id: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT auto_delete_timetables_time FROM chats WHERE id = %s""", (chat_id,))
            return cursor.fetchone()[0]


def set_auto_delete_commands_time(chat_id: int, seconds: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET auto_delete_commands_time = %s WHERE id = %s""", (seconds, chat_id))
            conn.commit()


def set_auto_delete_timetables_time(chat_id: int, seconds: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE chats SET auto_delete_timetables_time = %s WHERE id = %s""", (seconds, chat_id))
            conn.commit()


###############
###############
###############

def add_warn(chat_id: int, user_id: int, text: str):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT warns FROM warns WHERE chat_id = %s and user_id = %s""",
                           (chat_id, user_id))
            warns = cursor.fetchone()
            if warns is None:
                cursor.execute(
                    """INSERT INTO warns VALUES (%s, %s, %s)""", (chat_id, user_id, text))
                conn.commit()
                return 1
            elif warns[0] == '':
                warns = []
            else:
                warns = warns[0].split(";;")
            warns.append(text)
            cursor.execute("""UPDATE warns SET warns = %s WHERE chat_id = %s and user_id = %s""",
                           (';;'.join(warns), chat_id, user_id))
            conn.commit()
            return len(warns)


def del_warn(chat_id: int, user_id: int, num: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT warns FROM warns WHERE chat_id = %s and user_id = %s""",
                           (chat_id, user_id))
            warns = cursor.fetchone()
            if warns is None:
                cursor.execute(
                    """INSERT INTO warns VALUES (%s, %s, %s)""", (chat_id, user_id, ''))
                conn.commit()
                return False

            elif warns[0] == '':
                return False
            else:
                warns = warns[0].split(";;")
            if num <= 0 or num > len(warns):
                return False
            else:
                warns.pop(num - 1)
            cursor.execute("""UPDATE warns SET warns = %s WHERE chat_id = %s and user_id = %s""",
                           (';;'.join(warns), chat_id, user_id))
            conn.commit()
            return True


def get_warns(user_id: int, chat_id: int,):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            if chat_id is not None:
                cursor.execute("""SELECT chat_id, warns FROM warns WHERE chat_id = %s and user_id = %s""",
                               (chat_id, user_id))
            else:
                cursor.execute("""SELECT chat_id, warns FROM warns WHERE user_id = %s""",
                               (user_id,))
            warns = cursor.fetchall()
            if warns is None and chat_id is not None:
                cursor.execute(
                    """INSERT INTO warns VALUES (%s, %s, %s)""", (chat_id, user_id, ''))
                conn.commit()
                return {}
            elif warns is None:
                return {}
            d_warns = {}
            for i in warns:
                if i[1] == "":
                    continue
                d_warns.update({i[0]: i[1].split(';;')})
            return d_warns


##################

def get_all_users(mode: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            if mode == 1:
                cursor.execute("""SELECT id FROM users WHERE mail = True""")
            elif mode == 0:
                cursor.execute("""SELECT id FROM users""")
            elif mode == 2:
                cursor.execute("""SELECT id FROM users WHERE mail != True""")
            else:
                raise Exception("Wrong mode")
            users = cursor.fetchall()
            data = []
            for each in users:
                data.append(each[0])
            return data


def set_user_mail(user_id: int, mail: bool):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE users SET mail = %s WHERE id = %s""", (mail, user_id))
            conn.commit()


def get_user_mail(user_id: int):
    with pymysql.connect(**connection_data.connection_data) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT mail FROM users WHERE id = %s""", (user_id,))
            return bool(cursor.fetchone()[0])
