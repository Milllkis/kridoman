import telebot
from telebot import types
import requests
import boto3
import time
import json
from bs4 import BeautifulSoup
import urllib.request
import random
import re
import os

token = ''
bot = telebot.TeleBot(token)

key = ''

header = {'Authorization': 'Api-Key {}'.format(key)}

bucket_name = 'pytelegram'

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)

helpanite = '''Что я умею?
• Говорить ни о чем;
• Смотреть прогноз погоды;
• Присылать курс доллара/евро;
• Присылать мемы с Егором Кридом;
• Придумывать, что же приготовить сегодня;
• Присылать подборку книг/фильмов;
• Если вы любите манги, то может посоветовать парочку;
• Присылать смешные тиктоки (не исключаем наличие тиктоков с Егором Кридом).'''

DOLLAR_RUB = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4'
EURO_RUB = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE&aqs=chrome..69i57j0i433l4j0i457j0i402j0j0i433j0.9339j1j7&sourceid=chrome&ie=UTF-8'

def money(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    full_page_d = requests.get(url, headers=headers)
    soup = BeautifulSoup(full_page_d.content, 'html.parser')
    convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
    return convert[0].text


def weather(message):
    api_key = "e0f196e9b4e78318b8105ef0796ec24c"
    root_url = "http://api.openweathermap.org/data/2.5/weather?"
    if 'москв' in message:
        city_name = "Moscow,RU"
        url = f"{root_url}appid={api_key}&q={city_name}"
        r = requests.get(url,
                         params={'units': 'metric', 'lang': 'ru'})
        data = r.json()
        if data['cod'] == 200:
            temp = data['main']['temp']
            pressure = data['main']['pressure']
            descr = data['weather'][0]['description']
            wind = data['wind']['speed']
            city = f"Город : {city_name}"
            des = f"Погода: {descr}"
            t = f"Температура {temp} градуса по Цельсию"
            pr = f"Давление {pressure} hPa"
            wnd = f"Скорость ветра {wind} м/с "
        return city + '\n' + des + '\n' + t + '\n' + pr + '\n' + wnd
    else:
        return 'Крошка, а ты точно указала место? Если да, то прости, сердцеедка, я кроме Москвы ничего не знаю'


def recipes(message):
    resp = urllib.request.urlopen("https://eda.ru/recepty?page=1")
    soup = BeautifulSoup(resp, features="html.parser", from_encoding=resp.info().get_param('charset'))
    lnk = []
    rcp = []
    for link in soup.find_all('a', href=True):
        lnk.append(link['href'])
    for check in lnk:
        recep = re.findall(r'[\D\w._+-]+-\d{5}', check)
        if recep != []:
            for final in recep:
                fnl = 'https://eda.ru' + final
                rcp.append(fnl)
    return random.choice(rcp)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Ну здравствуй, крошка))')

@bot.message_handler(commands=['help'])
def help(message):
    helpani = '''Что я умею?
• Говорить ни о чем;
• Смотреть прогноз погоды;
• Присылать курс доллара/евро;
• Присылать мемы с Егором Кридом;
• Придумывать, что же приготовить сегодня;
• Присылать подборку книг/фильмов;
• Если вы любите манги, то может посоветовать парочку;
• Присылать смешные тиктоки (не исключаем наличие тиктоков с Егором Кридом).'''
    bot.send_message(message.chat.id, helpani)


@bot.message_handler(commands=['stop'])
def finish(message):
    bot.send_message(message.chat.id, 'Пока, сердцеедка, буду скучать, пиши еще')


@bot.message_handler(content_types=['voice'])
def speech_to_text(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
    file_key = 'audio' + str(message.chat.id) + '.ogg'
    filelink = 'https://storage.yandexcloud.net/pytelegram/' + file_key
    POST = 'https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize'
    body = {
        "config": {
            "specification": {
                "languageCode": "ru-RU"
            }
        },
        "audio": {
            "uri": filelink
        }
    }
    with open(file_key, 'wb') as f:
        f.write(file.content)
    s3.upload_file(file_key, bucket_name, file_key)
    if os.path.exists(file_key) == True:
        os.remove(file_key)

    for key in s3.list_objects(Bucket='pytelegram')['Contents']:
        print(key)
    req = requests.post(POST, headers=header, json=body)
    data = req.json()
    id = data['id']
    while True:
        time.sleep(1)
        GET = "https://operation.api.cloud.yandex.net/operations/{id}"
        req = requests.get(GET.format(id=id), headers=header)
        req = req.json()
        if req['done']:
            break
    for chunk in req['response']['chunks']:
        txt = chunk['alternatives'][0]['text']
        text = str(txt).lower()
        bot.send_message(message.chat.id, f'Ваш текст: ' + txt)

        if "курс" in str(text):
            if 'доллар' in str(text):
                bot.send_message(message.chat.id, 'Сейчас курс доллара: ' + money(DOLLAR_RUB) + ' RUB')
            if 'евро' in str(text):
                bot.send_message(message.chat.id, 'Сейчас курс евро: ' + money(EURO_RUB) + ' RUB')

        if "погод" in str(text):
            soob = weather(str(text))
            bot.send_message(message.chat.id, soob)

        if "манг" in str(text):
            file = open("manga.txt", "r", encoding="UTF-8")
            fname = file.read()
            bot.send_message(message.chat.id, fname)
            file.close()

        if "чита" in str(text):
            bot.send_message(message.chat.id, "https://eksmo.ru/podborki/")

        if "тик" and "ток" in str(text):
            with open("тикитоки.txt") as filik:
                lines = filik.readlines()
                random_line = random.choice(lines).strip()
                bot.send_message(message.chat.id, random_line)

        if 'привет' in str(text):
            bot.send_message(message.chat.id, 'Привет, пуссигерл')
        if 'как' in str(text):
            if "дела" in str(text):
                bot.send_message(message.chat.id, 'Все круто, как ты, сердцеедка???')
            if 'настро' in str(text):
                bot.send_message(message.chat.id, 'Все круто, как ты, сердцеедка???')
        if 'хорошо' in str(text):
            bot.send_message(message.chat.id, 'Я так рад! Спроси у меня еще что нибудь!!!')
        if ' ' in str(text):
            if 'делаешь' in str(text):
                bot.send_message(message.chat.id, 'Пишу новый трек про тебя! Скоро кину тебе демку, пуссигерл))')
        if 'сколько' in str(text):
            if 'лет' in str(text):
                bot.send_message(message.chat.id, 'Не спрашивай мой возраст, детка))')
        if 'когда' in str(text):
            if 'трек' in str(text):
                bot.send_message(message.chat.id, 'Очень скоро на всех площадках будет трек про тебя, сердцеедка')

        if "рецепт" in str(text):
            soob = recipes(str(text))
            bot.send_message(message.chat.id, soob)

        if "мем" in str(text):
            photo = open("мемы/" + random.choice(os.listdir("мемы")), "rb")
            bot.send_photo(message.chat.id, photo)

        if "фото" in str(text):
            if "егор" in str(text):
                photo = open("мемы/" + random.choice(os.listdir("мемы")), "rb")
                bot.send_photo(message.chat.id, photo)

        if "созда" in str(text):
            photo_creaters = open("создатели/" + random.choice(os.listdir("создатели")), "rb")
            bot.send_message(message.chat.id, "Этот бот создали две самые лучшие девочки в твоей жизни: Милена ака @Milkkisssss и Настя ака @pakh0m0va!!!")
            bot.send_photo(message.chat.id, photo_creaters)
            
bot.polling(none_stop=True, interval=0)
