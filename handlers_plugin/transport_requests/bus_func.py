import asyncio
import re
from pyrogram import Client
from pyrogram import filters
from pyrogram import enums
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import costum_filters
import db
from func import logger

import config
from func import auto_delete
from parsing.text_creater import get_text, get_text_new


async def message_deleter(message, time: int = 180):
    await asyncio.sleep(time)
    try:
        await message.delete()
    except Exception:
        pass


avtobus_nn = r"(^|\b)((автобус|маршрут|маршрутка) +\d+ ?[абг]?)|(\d+ ?[абг]? +(автобус|маршрут|маршрутка))(^|\b)"


@Client.on_message(filters.regex(avtobus_nn, re.I) & costum_filters.user_command)
async def autobus_request(app: Client, message: Message):
    for match in message.matches:
        logger.loggers(message, text=f"маршрут = {match.group()}")
        num = None
        for index, element in enumerate(match.group().strip().split()):
            if element.lower() in ("автобус", "маршрут", "маршрутка"):
                num = match.group().strip().split()[index - 1]

        if message.from_user.id in [0]:
            mes = await app.send_message(message.chat.id, get_text_new(num, 'Автобус'),
                                         reply_to_message_id=message.reply_to_message_id or message.id,
                                         disable_web_page_preview=True, parse_mode=ParseMode.HTML)
        else:
            mes = await app.send_message(message.chat.id, get_text(num, 'Автобус'),
                                         reply_to_message_id=message.reply_to_message_id or message.id,
                                         disable_web_page_preview=True, parse_mode=ParseMode.HTML)

        if num.lower() in db.get_all_nums():
            logger.log_transport("bus", num.lower(), message.from_user.id)
        messages = [mes]
        if message.text == match.group().strip():
            messages.append(message)
        await auto_delete.delete_timetable(messages)


regex_for_incorrect_input = r"^(1|2|4|5|6|7|9|10|15|18|20|21|21а|21б|22|23|25|27|29|31|32|33|34|35|36|37|38|39|40|41|42|43|44|48|50|51|54|55|56|57а|58|59|60|62|64|64г|70|73|75|77|82|85|86|87а|87б|88|90|91|92|95|95а|96|98|100|101а|106|107|108|109|111|113|115|118|119|120|121|124а|125|127|134|136|136а|137|141|146|146а|146б|149|151а|152|153|155|156|156а|157а|158|177)$"


@Client.on_message(filters.regex(regex_for_incorrect_input, re.I) & (filters.chat(config.chat_dp_id) | filters.private))
async def incorrect_input(app: Client, message: Message):
    logger.loggers(message, text=f"маршрут = [НЕВЕРНО]")
    mes = await message.reply_text(
        "Просимо дотримуватись Правил користування ботом. Будь ласка, надішліть запит згідно з шаблоном, що наведений нижче,\n\nнапишіть:\nавтобус [номер автобуса]\n— автобус 151а\n— автобус 77\n— автобус 1")

    messages = [mes]
    if message.text == message.matches[0].group():
        messages.append(message)
    await auto_delete.delete_command(messages)


# @Client.on_message(filters.regex(r"(^|\b)(маршрутк\w*) +\d+[АБГ]?(^|\b)", re.I) & costum_filters.user_command)
# async def incorrect_input(app: Client, message: Message):
#     logger.loggers(message, text=f"маршрут = [Маршруток нет, есть автобус]")
#     mes = await message.reply(
#         "Доводимо до Вашого відома, що “маршруток” у м. Дніпрі не існує. Натомість, існують автобуси. Будь ласка, здійсніть запит згідно з шаблоном, наприклад\n\nнапишіть:\nавтобус [номер автобуса]\n— автобус 151а\n— автобус 77\n— автобус 1")
#     messages = [mes]
#     if message.text == message.matches[0].group():
#         messages.append(message)
#     await auto_delete.delete_command(messages)


avtobus_wrong = r"(^|\b)(маршрутом|маршрут|маршрутка|автобус|маршрутки) +(100|102|105|106|107|109|110|112|115|117|120|121|122|123|124|126|126А|127|128|129|129а|131|132|200|201|204|205|206|207|208|209|210|211|212|213|215|216|217|218|221|222|223|225|226|227|228|229|235|236|237|238|239|240|241|242|243|244|245|246|259|260|261|262|263|264|265|266|267|268|269|270|271|272|400|401|402|403|404|405|407|409|410|412|413|414|416|420|422|423|423А|424|425|426|426а|427|428|431|434|435|437|439|441|442|444|445|446|447|450|452|463|464|466|479|480|481|482|483|484|487|489|490|492|493|496|497а|501|504|560|600|602|608|609|613|619|620|621|621а|626|630|631|632|633|634|635|636|637|638|639|640|641|642|643|644|646|647|655|656|657|658|661|712|717|718|719|720|721|724|725|728|729|730|731|732|733|734|735|737|739|740|747|749|750|751|755|757|759|762|764|766|769|770|771|774|800а|809|810|811|812|813|815|819|820|821|822|825|826|826а|827|829|830|831|835|837|838|839|10001|10005|10007|10011|10013|10025|10037|10041|10047|10051|10059|10063|10069|10077|10085|10087|10091|10115|10117|10129|10137|10149|10165|10171|10177|10181|10195|10209|10233|10267|10281|10287|10299|10303|10307|10311|10319|10325|10329|10333|10335|10341|10345|10353|10361|10365|10367|10375|10379|10391|10395|10397|10405|10407|10411|10417|10425|10431|10439|10445|10451|10457|10459|10467|10471|10475|10479|10485|10487|10491|10495|10513|10515|10517|10519|10567|10581|10585|10591|10597|10627|10631|10635|10651|10655|10699|10705|10707|10715|10723|10733|10743|10749|10753|10757|10761|10763|10769|10771|10777|10781|10785|10791|10799|10801|10805|10809|10817|10821|10825|10829|10833|10839|10847|10849|10851|10855|10869|10877|10881|10885|10889|10893|10901|10925|11019|11115|11139|11209|11211|11217|11221|11229|11389|11391|11395|11483|11487|11519|11523|11541|11571|11575|11579|11583|11587|11591|11595|11619|11623|11633|11651|11655|11661|11671|11687|11689|11691|11693|11699|11707|11711|11719|11723|11733|11737|11749|11787|11847|11851|11857|11859|11861|11941|11989|11993|12009|12013|12501|12507|12515)(^|\b)"


@Client.on_message(filters.regex(avtobus_wrong, re.I) & costum_filters.user_command)
async def wrong_autobus_request(app, message):
    text = message.matches[0].group().lower().split()[-1]
    logger.loggers(
        message, text=f"маршрут =  {text} не входить до маршрутів міста Дніпро")
    mes = await app.send_message(message.chat.id,
                                 'Даний маршрут відсутній у маршрутній мережі м. Дніпро. На жаль, ми не змогли отримати інформацію щодо його розкладу. Інформацію щодо розкладу приміських автобусних маршрутів можна отримати за телефоном Гарячої лінії Дніпропетровської ОДА - 0800505600. Дзвінок безкоштовний.',
                                 reply_to_message_id=message.reply_to_message_id or message.id,
                                 disable_web_page_preview=True)
    messages = [mes]
    if message.text == message.matches[0].group():
        messages.append(message)
    await auto_delete.delete_command(messages)
