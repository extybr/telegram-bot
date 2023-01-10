#!/usr/bin/env python3
import os.path
from time import sleep
import requests
from aiogram import *
from aiogram.utils.exceptions import NetworkError
from pytube import YouTube
from loguru import logger
import RPi.GPIO as GPIO
from config import *
from script_job_raspberry import search_jobs, region_id

bot = Bot(TOKEN)
dp = Dispatcher(bot)
NEW = dict()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    """ Функция вывода при старте: определение кнопок, приветствие """
    logger.info(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton('💲 USD - EUR 💲')
    button_2 = types.KeyboardButton('🐷 Водички? 🐷')
    button_3 = types.KeyboardButton('🙏 работа 🙏')
    button_4 = types.KeyboardButton('🚷 bot_stop 🚷')
    button_5 = types.KeyboardButton('😎 read file 😎')
    button_6 = types.KeyboardButton('🌼 led on 🌼')
    button_7 = types.KeyboardButton('🌼 led off 🌼')
    button_8 = types.KeyboardButton('🤓 мой id 🤓')
    button_9 = types.KeyboardButton('🚷 stop 🚷')
    markup.row(button_1, button_3, button_9, button_8)
    markup.row(button_2, button_5, button_6, button_7, button_4)
    await bot.send_message(message.chat.id, 'Ну что готов к поиску работы? 😄 Жми кнопки-команды '
                                            'внизу', reply_markup=markup)
    try:
        url = 'https://skyteach.ru/wp-content/cache/thumb/d7/81a695a40a5dfd7_730x420.jpg'
        await bot.send_photo(message.chat.id, photo=url, reply_markup=markup)
    except Exception as er:
        logger.info(er)
        if str(er).find('Error code: 400'):
            img_file = open(f'vacancies/job.jpg', 'rb')
            await bot.send_document(message.chat.id, img_file)


@dp.message_handler()
async def text_message(message: types.Message):
    """
    Функция, обрабатывает нажатие кнопок бота
    Логирование в терминал
    Парсит курсы валют
    Запуск по условию: включение светодиода (реле), парсера вакансий, остановка бота
    """
    logger.info(message.text)
    if message.text.startswith('*'):
        hr = message.text.split(' ')
        profession = ''
        if (hr[0] or hr[1]) in ['Республика', 'республика', 'край', 'область']:
            hr[0] = hr[0] + ' ' + hr.pop(1)
        for i in hr:
            if i == hr[0]:
                continue
            if i == hr[len(hr) - 1]:
                break
            profession += ''.join(i + ' ')
        profession = profession.strip()
        region = region_id(hr[0][1:])
        days = hr[-1]
        if region is None:
            await bot.send_message(message.chat.id, 'Вы неправильно ввели название города')
        elif len(days) != 2 or not days.isdigit() or days == '00':
            await bot.send_message(message.chat.id, 'Вы неправильно ввели дату для поиска')
        else:
            if int(days) > 30:
                days = '30'
            search_jobs(message.chat.id, '', f'{profession}', f'{region}', f'{days}')
            count = 0
            text = f'vacancies/{message.chat.id}.txt'
            with open(text, 'r', encoding='utf-8') as txt:
                count += int(txt.readline().strip()[20:])
            if count > 10:
                await send_vacancies(message)
            else:
                with open(text, 'r', encoding='utf-8') as txt:
                    await bot.send_message(message.chat.id, f'{txt.read()}')
            if os.path.exists(f'vacancies/{message.chat.id}.txt'):
                download_file = open(f'vacancies/{message.chat.id}.txt', 'rb')
                await bot.send_document(message.chat.id, download_file)
    elif message.text.startswith('#'):
        import shlex
        import subprocess
        command = message.text[1:]
        args = command.split(' ')
        args.pop(0)
        clean = [shlex.quote(i) for i in args]
        full_command = shlex.split(f"{command} {''.join(clean)}")
        try:
            result = subprocess.run(full_command, capture_output=True).stdout.decode()
            await bot.send_message(message.chat.id, f"{result}")
        except Exception as error:
            logger.error(error)
    elif message.text == '💲 USD - EUR 💲':
        try:
            binance = requests.get('https://api.binance.com/api/v1/ticker/24hr').json()
            price_btc, price_eth = 0, 0
            for coin in binance:
                if coin['symbol'] == 'BTCUSDT':
                    price_btc = int(float(coin.get('lastPrice', 0)))
                elif coin['symbol'] == 'ETHUSDT':
                    price_eth = int(float(coin.get('lastPrice', 0)))
            result_binance = f'BTCUSDT - {price_btc}  /  ETHUSDT - {price_eth}'
            bank = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()
            bank_1 = round(1 / bank["rates"]['USD'], 3)
            bank_2 = round(1 / bank["rates"]['EUR'], 3)
            result_bank = f'USD - {bank_1}  /  EUR - {bank_2}'
            temperature = ''
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as termal:
                temperature = round(int(termal.read()) / 1000, 2)
                temperature = f"Температура = {temperature} 'C"
            await bot.send_message(message.chat.id, f'Центробанк РФ:   {result_bank}\n'
                                                    f'Биржа Binance:   {result_binance}\n'
                                                    f'{temperature}')
        except OSError:
            logger.error('Сервер недоступен')
            await bot.send_message(message.chat.id, 'Сервер недоступен')
    elif message.text == "🐷 Водички? 🐷":
        try:
            url_img = ("https://bestwine24.ru/image/cache/catalog/vodka"
                       "/eef2e315f762519e75aba64a800b63e9-540x720.jpg")
            await bot.send_photo(message.chat.id, photo=url_img)
        except Exception as error:
            logger.error(error)
            if str(error).find('Error code: 400'):
                img_file = open(f'vacancies/vodka.jpg', 'rb')
                await bot.send_document(message.chat.id, img_file)
    elif message.text == "😎 read file 😎":
        if message.chat.id in (USER_1, USER_2):
            await send_vacancies(message)
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено читать локальный файл 😄')
    elif message.text == "🌼 led on 🌼":
        if message.chat.id == USER_2:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(25, GPIO.OUT)
            GPIO.output(25, GPIO.HIGH)
            await bot.send_message(USER_2, 'Включаю чайник 😄')
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено включать чайник 😄')
    elif message.text == "🌼 led off 🌼":
        if message.chat.id == USER_2:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(25, GPIO.OUT)
            GPIO.output(25, GPIO.LOW)
            await bot.send_message(USER_2, 'Выключаю чайник 😄')
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено выключать чайник 😄')
    elif message.text == "🤓 мой id 🤓":
        await bot.send_message(message.chat.id, f'id - {message.chat.id}\nИмя - '
                                                f'{message.from_user.full_name}\nПользователь - '
                                                f'{message.chat.username}')
    elif message.text == "🚷 bot_stop 🚷":
        if message.chat.id == USER_1:
            await bot.send_message(message.chat.id, 'Выключаю бота 😄')
            try:
                await bot.stop_poll(message.chat.id, 1)
            except RuntimeError:
                logger.error('Выключение бота')
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено выключать бота 😄')
    elif message.text == "🙏 работа 🙏":
        if message.chat.id in (USER_5, USER_6):
            search_jobs(message.chat.id, '', 'парикмахер', '1979', '30')
            count = 0
            text = f'vacancies/{message.chat.id}.txt'
            with open(text, 'r', encoding='utf-8') as txt:
                count += int(txt.readline().strip()[20:])
            if count > 10:
                await send_vacancies(message)
            else:
                with open(text, 'r', encoding='utf-8') as txt:
                    await bot.send_message(message.chat.id, f'{txt.read()}')
        else:
            await bot.send_message(message.chat.id, '*Введите данные для поиска в таком порядке*:'
                                                    '\n\n`*`*[город] [профессия с желаемой '
                                                    'зарплатой] [число дней публикации объявлений '
                                                    '(max=30)]\n\nПримеры*:\n`*Воронеж водитель '
                                                    '10`\n`*Хабаровский край парикмахер 30`'
                                                    '\n`*Красноярск учитель истории 50000 07`'
                                                    '\n\nгде `*` - обязательный символ в начале,\n'
                                                    '`Красноярск` - это город, вакансии по которому'
                                                    ' будут искаться,\n`учитель истории` - '
                                                    'профессия для поиска,\n`50000` - минимальный'
                                                    ' уровень зарплаты для поиска,\n`07` - поиск'
                                                    ' за последние 7 дней.', parse_mode='Markdown')
    elif message.text == '🚷 stop 🚷':
        global NEW
        NEW[f'{message.chat.id}'] = 1
        logger.info(f'{NEW}')
    elif [i for i in ['https://youtu.be/', 'https://www.youtu.be/', 'https://youtube.com/',
                      'https://www.youtube.com/'] if message.text.startswith(i)]:
        yt = YouTube(message.text)
        await bot.send_message(message.chat.id, f'*Начинаю загрузку видео*: *{yt.title}*\n'
                                                f'*С канала*: [{yt.author}]({yt.channel_url})',
                               parse_mode='Markdown')
        await download_video(message)
    else:
        await bot.send_message(message.chat.id, f'*Не надо баловаться* 😡 *{message.chat.first_name}*'
                                                f'\n\n😜 *И тебе того же:   {message.text}*',
                               parse_mode='Markdown')


async def download_video(message: types.Message) -> None:
    """ Скачивает видео с youtube """
    logger.info(message.text)
    user_id = message.from_user.id
    yt = YouTube(message.text)
    stream = yt.streams.filter(progressive=True, file_extension='mp4')
    try:
        stream.get_highest_resolution().download(f'{user_id}', f'{user_id}_{yt.title}.mp4')
        with open(f'{user_id}/{user_id}_{yt.title}.mp4', 'rb') as video:
            await bot.send_video(user_id, video, caption=f'*Готово. Ваше видео*: *{yt.title}*',
                                 parse_mode='Markdown')
            os.remove(f'{user_id}/{user_id}_{yt.title}.mp4')
    except NetworkError as error:
        await bot.send_message(message.chat.id, '*Ограничение!!! Лимит на закачку ботом 50MB*.',
                               parse_mode='Markdown')
        os.remove(f'{user_id}/{user_id}_{yt.title}.mp4')
        logger.error(error)


async def send_vacancies(message: types.Message) -> None:
    """ Читает локальный файл с вакансиями """
    logger.info(message.text)
    text = f'vacancies/{message.chat.id}.txt'
    count = 0
    count_local = 0
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
        count_local += int(txt.read().strip().count('🚘'))
    count_spam = count - count_local
    if message.chat.id in (USER_5, USER_6):
        await bot.send_message(message.chat.id, f'Всего вакансий: {count}. В локальной базе: '
                                                f'{count_local}. Удаленных вакансий-спама: '
                                                f'{count_spam}.')
    else:
        await bot.send_message(message.chat.id, f'Число вакансий:  {count_local}')
    sleep(3)
    global NEW
    NEW[f'{message.chat.id}'] = 0
    if count > 0:
        with open(text, 'r', encoding='utf-8') as txt:
            for line in txt.readlines():
                if NEW[f'{message.chat.id}'] == 1:
                    await bot.send_message(message.chat.id, 'Принудительная остановка вывода '
                                                            'вакансий')
                    break
                elif len(line) < 3:
                    continue
                elif line.count('*') > 2:
                    await bot.send_message(message.chat.id, line.strip())
                elif line.find('https://') != -1:
                    await bot.send_message(message.chat.id, line.strip())
                elif line.startswith('🚘'):
                    sleep(5)
    NEW[f'{message.chat.id}'] = 0
    logger.info(f'{NEW}')


if __name__ == '__main__':
    executor.start_polling(dp)
