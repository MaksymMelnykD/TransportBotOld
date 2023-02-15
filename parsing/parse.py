import asyncio
import os
import re
import time
import traceback

import cssutils

from bs4 import BeautifulSoup
import httplib2
import requests
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pyrogram import Client

import config
import db
from func import global_vars
from parsing import create_image

first_bas_row = 10

first_electric_transport_row = 2
last_crop_electric_transport_row = -3


def get_service_simple():
    return build('sheets', 'v4', developerKey='AIzaSyBdWHx2mZkIkppfF7EPw-PMtxjWzNtYwQA')


def get_service_sacc():
    """
    Используется сервисный аккаунт:
    transport-table-parsing@transportparser.iam.gserviceaccount.com
    """
    # https://t1p.de/9y1xc
    creds_json = os.path.join(
        'parsing', 'rozklad-dnipro-bot-f515f89d3ff9.json')
    # creds_json = 'transportparser-daec56150554.json'
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def transport_parse():
    service = get_service_sacc()
    sheet = service.spreadsheets()

    sheet_id = "1WEoger7elt-flQN-hhsMzQ3QkwTbtvVojcb8xEa45Y4"

    resp = sheet.values().batchGet(spreadsheetId=sheet_id,
                                   ranges=["Автобусні маршрути"])
    data = resp.execute()
    all_buses = data['valueRanges'][0]['values'][first_bas_row - 1:]
    try:
        all_buses = bus_parse(all_buses)
    except Exception as e:
        print(e)

    return all_buses


def bus_parse(buses):
    data_bus = []
    previous = None
    for way_data in buses:
        way_time = time_data = interval_data = way_place = intervals = None
        add_data = []
        if way_data[0] == '':
            way_data[0] = previous[0]
        previous = way_data
        way_data = [i.strip() for i in way_data]
        add_data += [way_data[0].split()[0].lower()]
        if len(way_data) == 4:
            if way_data[3].lower() == 'тимчасово не обслуговується':
                add_data += [None, None, None, None, None, 0]
                data_bus.append(add_data)
                continue
            else:
                if len(way_data[3].split('\n')) == 3:
                    time_way = '\n'.join(
                        [way_data[3].split('\n')[1], way_data[3].split('\n')[2]])
                    time_data = way_data[3].split('\n')[0]
                else:
                    time_way = way_data[3]
                add_data += [way_data[2], time_way, time_data, None, None, 1]
                data_bus.append(add_data)
                continue
        elif len(way_data) >= 5:
            time_data_list = way_data[3].split('\n')
            way_place = way_data[2]
            if len(time_data_list) == 3:
                time_data = time_data_list[0]
                way_time = '\n'.join([time_data_list[1], time_data_list[2]])
            elif len(time_data_list) == 2:
                time_data = None
                way_time = '\n'.join([time_data_list[0], time_data_list[1]])
            elif len(time_data_list) == 1:
                time_data = None
                way_place = way_data[2].replace('\n', ' ')
                way_time = time_data_list[0]

            if len(way_data) == 5:
                interval_data = way_data[4]
            else:
                intervals = ';'.join(way_data[-4:])
        add_data += [way_place, way_time,
                     time_data, intervals, interval_data, 1]
        data_bus.append(add_data)

    return data_bus


electric_transport = {"tram": ["1", "4", "5", "6", "7", "9", "11", "12", "14", "15", "16", "17", "18", "19"],
                      "trol": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "15", "16", "17",
                               "19", "20", "21", "a", "b"]}

time_transport = ["5:00", " 6:00", " 7:00", " 8:00", " 9:00", " 10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
                  "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "00:00"]


def electric_transport_parse():
    link = None
    global_vars.status.set_parsing_status(True)
    try:
        for transport in electric_transport:
            for num_way in electric_transport.get(transport):
                data = {}
                link = f"https://det-dnipro.dp.ua/{num_way}-{transport + 'vaj' if transport == 'tram' else transport}"
                # link = "https://det-dnipro.dp.ua/1-tramvaj/"
                print(f"Request to {link}")
                q = time.time()
                r = requests.get(link)
                soup = BeautifulSoup(r.text, "lxml")
                links_to_table = [link['src']
                                  for link in soup.find_all('iframe')]
                data['transport'] = transport[:4]
                data['num_way'] = num_way
                data['data'] = {}
                for day, link_to_table in enumerate(links_to_table):
                    data['data'][day] = {}
                    data['data'][day]['stops'] = {}
                    data['data'][day]['text'] = None
                    table_r = requests.get(link_to_table)
                    soup = BeautifulSoup(table_r.text, "lxml")
                    css = soup.find("style", type="text/css").text
                    css = cssutils.parseString(css).cssRules
                    active = []
                    stop_classes = ["s1"]
                    for i in css:
                        if i.style.color == '#000':
                            active.append(i.selectorText.replace(
                                '.', '').split()[-1])
                            continue
                    table = soup.find("table", class_="waffle")
                    table_body = table.find('tbody')
                    rows = table_body.find_all('tr')
                    if len(rows) <= 8:
                        text = []
                        for i in rows:
                            cols = i.find_all('td')
                            for x in cols:
                                if x.text != '':
                                    text.append(x.text)
                                else:
                                    pass
                        text = '\n'.join(text)
                        data['data'][day]['text'] = text
                        # print(text)
                        continue
                    rows = rows[:last_crop_electric_transport_row]
                    skip = True
                    stop = None
                    direction = None
                    for row in rows:
                        if skip:
                            skip = False
                            continue
                        cols = row.find_all('td')
                        find = None
                        if len(cols) == 1:
                            for class_ in stop_classes:
                                find = row.find("td", class_=class_)
                                if find:
                                    break
                            if find and find.text:
                                skip = True
                                stop = find or cols[0]
                                direction = re.search(
                                    r'(?<=(\(напрямок до)).+(?=\))', stop.text)
                                if direction:
                                    direction = direction.group().strip()
                                else:
                                    direction = ''
                                stop = stop.text.split('(')[0].strip()
                                data['data'][day]['stops'][f"{stop}_{direction}"] = {
                                }
                                continue
                            else:
                                continue
                        if stop is None:
                            raise Exception
                        element_index = 0
                        for col in cols:
                            minute = col.text
                            class_ = col["class"][0].split()[0]
                            if len(col['class']) > 1 and col['class'][1] == 'softmerge':
                                minute = col.find('div').text
                            elif class_ not in active or col.text == '':
                                minute = None
                            minutes = data['data'][day]['stops'][f"{stop}_{direction}"].get('time', {
                            })
                            data['data'][day]['stops'][f"{stop}_{direction}"]['time'] = minutes
                            minutes = data['data'][day]['stops'][f"{stop}_{direction}"]['time'].get(
                                time_transport[element_index], [])
                            if minute is not None:
                                minutes.append(minute)
                            data['data'][day]['stops'][f"{stop}_{direction}"]['time'][
                                time_transport[element_index]] = minutes
                            # pprint(data)
                            element_index += 1
                w = time.time()
                create_image.render(data)
                print(r, w - q, 'сек')
    except Exception as e:
        for tech_admin in config.admins:
            try:
                a = requests.post(
                    f"https://api.telegram.org/bot{config.TOKEN}/sendMessage?chat_id={tech_admin}&text=Ошибка при парсинге {link}\n\n{traceback.format_exc()}")
                print(a)
            except Exception as e:
                print(e)
        global_vars.status.set_parsing_status(False)
        raise e
    global_vars.status.set_parsing_status(False)


def bus_parse_func():
    # db.add_transport(transport_parse())
    pass


if __name__ == '__main__':
    a = time.time()
    transport_parse()
    b = time.time()
    print(b - a)
