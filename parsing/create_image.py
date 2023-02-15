import math
import os
import time
import textwrap
from PIL import Image, ImageFont, ImageDraw

# (1182, 1280)
from func.translit import translit

names = {"trol": "Тролейбус", "tram": "Трамвай"}
black = '#000000'
white = '#ffffff'
text_color = black
letters = {"a": "А", "b": "Б"}


# day_row 545

# row 53
# col 41

def render(data: dict):
    files = os.listdir(os.path.join("parsing", "photos"))
    files = list(filter(lambda x: x.startswith(f"{data['num_way']}{data['transport']}"), files))
    for file in files:
        os.remove(os.path.join("parsing", "photos", file))
    a = time.time()
    font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'ClearSans-Regular.ttf'), size=25)
    subtitle_font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'ClearSans-Medium.ttf'), size=30)
    title_font = ImageFont.truetype(os.path.join('parsing', 'fonts', 'ClearSans-Bold.ttf'), size=43)
    stops = {}
    for day in data["data"]:
        day_data = data["data"][day]
        if day_data["stops"] != {}:
            for stop in day_data["stops"]:
                if stops.get(stop, None) is None:
                    stops.update({stop: day})
                else:
                    stops.update({stop: -1})
    if stops == {} and data["data"][0]['text'] == data["data"][1]['text']:
        text = data["data"][0]['text'].strip()
        text_image = Image.new("RGB", (900, 600), white)
        draw_for_text = ImageDraw.Draw(text_image)
        w, h = draw_for_text.textsize(text, font=title_font)
        draw_for_text.multiline_text(((900 - w) / 2, (600 - h) / 2), text,
                                     font=title_font,
                                     fill=black,
                                     align="center")
        text_image.save(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}.png"), 'PNG')
        return
    for stop in stops:
        image = Image.open(os.path.join("parsing", 'original.png'))
        draw = ImageDraw.Draw(image)
        draw.text((77, 62),
                  f'{names.get(data["transport"])} {letters.get(data["num_way"], None) if letters.get(data["num_way"], None) else data["num_way"]}',
                  font=title_font, fill=black)
        draw.text((515, 68), stop.split('_')[0], font=subtitle_font, fill=black)
        draw.text((545, 109), stop.split('_')[1], font=subtitle_font, fill=black)
        for day in data["data"]:
            text = data["data"][day]['text']
            if text:
                text = text.strip()
                width, height = (550, 950)
                text_image = Image.new("RGB", (width, height), white)
                draw_for_text = ImageDraw.Draw(text_image)
                w, h = draw_for_text.textsize(text, font=title_font)
                if w > width:
                    text = textwrap.wrap(text, width=20)
                    text = '\n'.join(text)
                    w, h = draw_for_text.textsize(text, font=title_font)
                draw_for_text.multiline_text(((width - w) / 2, 200), text, font=title_font, fill=black,
                                             align="center")
                image.paste(text_image, (32 + 568 * day, 200))
                continue
            if day != stops.get(stop) and stops.get(stop) != -1:
                continue
            for row_num, minutes in enumerate(data['data'][day]['stops'][stop]['time'].values()):
                if len(minutes) > 8:
                    draw.text((139 + 545 * day, 257 + row_num * 41.39), "кожні 5-7 хвилин", font=font, fill=text_color)
                    continue
                for num, minute in enumerate(minutes):
                    draw.text((139 + 545 * day + 53 * num, 257 + row_num * 41.39), minute, font=font, fill=text_color)
        direction = stop.split('_')[1].replace('"', "'").replace("/", "слеш").replace(
            "\\", "bsl")
        stop = stop.split('_')[0].replace('"', "'").replace("/", "слеш")
        name = f"{stop}_{direction}"
        image.save(os.path.join("parsing", "photos", f"{data['num_way']}{data['transport']}_{name}.png"), "PNG")
        # image.show()
    b = time.time()
    # print(f"{b - a}сек")


if __name__ == '__main__':
    pass
