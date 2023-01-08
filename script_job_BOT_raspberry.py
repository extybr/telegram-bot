#!/usr/bin/env python3
import os.path
from time import sleep
import requests
import telebot
from loguru import logger
from telebot import types
import RPi.GPIO as GPIO
from script_job_raspberry import search_jobs, region_id

token = 'bla-bla-bla'  # полученный токен бота
bot = telebot.TeleBot(token)
bot.remove_webhook()

USER_1 = 100000001
USER_2 = 100000002
USER_3 = 100000003
USER_4 = 100000004
USER_5 = 100000005
USER_6 = 100000006
NEW = dict()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)


@bot.message_handler(commands=['start'])
def start(message) -> None:
    """ Функция вывода при старте: определение кнопок, приветствие """
    bot.clear_step_handler(message)
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
    bot.send_message(message.chat.id, 'Ну что готов к поиску работы? 😄 Жми кнопки-команды внизу',
                     reply_markup=markup)
    try:
        url = 'https://skyteach.ru/wp-content/cache/thumb/d7/81a695a40a5dfd7_730x420.jpg'
        bot.send_photo(message.chat.id, photo=url, reply_markup=markup)
    except Exception as er:
        logger.info(er)
        if str(er).find('Error code: 400'):
            img_file = open(f'vacancies/job.jpg', 'rb')
            bot.send_document(message.chat.id, img_file)


@bot.message_handler(content_types='text')
def message_reply(message) -> None:
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
        for i in hr:
            if i == hr[0]:
                continue
            if i == hr[len(hr) - 1]:
                break
            profession += ''.join(i + ' ')
        profession = profession.strip()
        region = region_id(hr[0][1:])
        days = hr[len(hr) - 1]
        if region is None:
            bot.send_message(message.chat.id, 'Вы неправильно ввели название города')
        elif len(days) != 2:
            bot.send_message(message.chat.id, 'Вы неправильно ввели дату для поиска')
        else:
            search_jobs(message.chat.id, '', f'{profession}', f'{region}', f'{days}')
            count = 0
            text = f'vacancies/{message.chat.id}.txt'
            with open(text, 'r', encoding='utf-8') as txt:
                count += int(txt.readline().strip()[20:])
            if count > 10:
                send_vacancies(message)
            else:
                with open(text, 'r', encoding='utf-8') as txt:
                    bot.send_message(message.chat.id, f'{txt.read()}')
            if os.path.exists(f'vacancies/{message.chat.id}.txt'):
                download_file = open(f'vacancies/{message.chat.id}.txt', 'rb')
                bot.send_document(message.chat.id, download_file)
    elif message.text.startswith('@'):
        import shlex
        import subprocess
        command = message.text[1:]
        args = command.split(' ')
        args.pop(0)
        clean = [shlex.quote(i) for i in args]
        full_command = shlex.split(f"{command} {''.join(clean)}")
        result = subprocess.run(full_command, capture_output=True).stdout.decode()
        bot.send_message(message.chat.id, f"{result}")
    elif message.text == '💲 USD - EUR 💲':
        # bot.send_message(message.chat.id, "https://cbr.ru/key-indicators/")
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
            bot.send_message(message.chat.id, f'Центробанк РФ:   {result_bank}\nБиржа Binance:   '
                                              f'{result_binance}\n{temperature}')
        except OSError:
            print('Сервер недоступен')
            bot.send_message(message.chat.id, 'Сервер недоступен')
    elif message.text == "🐷 Водички? 🐷":
        try:
            url_img = ("https://bestwine24.ru/image/cache/catalog/vodka"
                       "/eef2e315f762519e75aba64a800b63e9-540x720.jpg")
            bot.send_photo(message.chat.id, photo=url_img)
        except Exception as er:
            logger.info(er)
            if str(er).find('Error code: 400'):
                img_file = open(f'vacancies/vodka.jpg', 'rb')
                bot.send_document(message.chat.id, img_file)
    elif message.text == "😎 read file 😎":
        if message.chat.id in (USER_1, USER_2):
            send_vacancies(message)
        else:
            bot.send_message(message.chat.id, 'Вам запрещено читать локальный файл 😄')
    elif message.text == "🌼 led on 🌼":
        if message.chat.id == USER_2:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(25, GPIO.OUT)
            GPIO.output(25, GPIO.HIGH)
            bot.send_message(USER_2, 'Включаю чайник 😄')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено включать чайник 😄')
    elif message.text == "🌼 led off 🌼":
        if message.chat.id == USER_2:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(25, GPIO.OUT)
            GPIO.output(25, GPIO.LOW)
            bot.send_message(USER_2, 'Выключаю чайник 😄')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено выключать чайник 😄')
    elif message.text == "🤓 мой id 🤓":
        bot.send_message(message.chat.id, f'id - {message.chat.id}\nИмя - {message.from_user.full_name}'
                                          f'\nПользователь - {message.chat.username}')
    elif message.text == "🚷 bot_stop 🚷":
        if message.chat.id == USER_1:
            bot.send_message(message.chat.id, 'Выключаю бота 😄')
            try:
                # bot.stop_polling()
                bot.stop_bot()
            except RuntimeError:
                print('Выключение бота')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено выключать бота 😄')
    elif message.text == "🙏 работа 🙏":
        if message.chat.id in (USER_5, USER_6):
            search_jobs(message.chat.id, '', 'парикмахер', '1979', '30')
            count = 0
            text = f'vacancies/{message.chat.id}.txt'
            with open(text, 'r', encoding='utf-8') as txt:
                count += int(txt.readline().strip()[20:])
            if count > 10:
                send_vacancies(message)
            else:
                with open(text, 'r', encoding='utf-8') as txt:
                    bot.send_message(message.chat.id, f'{txt.read()}')
        else:
            bot.send_message(message.chat.id, 'Введите данные для поиска в таком порядке:\n\n'
                                              '*[город] [профессия с желаемой зарплатой] [число '
                                              'дней публикации объявлений (max=30)]\n\nПримеры:\n\n'
                                              '*Воронеж водитель 30\n\n'
                                              '*Красноярск учитель истории 50000 07\n\n'
                                              'где <*> - обязательный символ в начале,\n'
                                              '<Красноярск> - это город, вакансии по которому '
                                              'будут искаться,\n<учитель истории> - профессия для '
                                              'поиска,\n<50000> - минимальный уровень зарплаты для '
                                              'поиска,\nа <07> - поиск за последние 7 дней.')
    elif message.text == '🚷 stop 🚷':
        global NEW
        NEW[f'{message.chat.id}'] = 1
    else:
        bot.send_message(message.chat.id, f'Не надо баловаться 😡 {message.chat.first_name}\n\n'
                                          f'😜 И тебе того же:   {message.text}')


def send_vacancies(message) -> None:
    """ Читает локальный файл с вакансиями """
    text = f'vacancies/{message.chat.id}.txt'
    count = 0
    count_local = 0
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
        count_local += int(txt.read().strip().count('🚘'))
    count_spam = count - count_local
    if message.chat.id in (USER_5, USER_6):
        bot.send_message(message.chat.id, f'Всего вакансий: {count}. В локальной базе: '
                                          f'{count_local}. Удаленных вакансий-спама: {count_spam}.')
    else:
        bot.send_message(message.chat.id, f'Число вакансий:  {count_local}')
    sleep(3)
    global NEW
    NEW[f'{message.chat.id}'] = 0
    if count > 0:
        with open(text, 'r', encoding='utf-8') as txt:
            for line in txt.readlines():
                if NEW[f'{message.chat.id}'] == 1:
                    bot.send_message(message.chat.id, 'Принудительная остановка вывода вакансий')
                    break
                elif len(line) < 3:
                    continue
                elif line.count('*') > 2:
                    bot.send_message(message.chat.id, line.strip())
                elif line.find('https://') != -1:
                    bot.send_message(message.chat.id, line.strip())
                elif line.startswith('🚘'):
                    sleep(5)
    NEW[f'{message.chat.id}'] = 0
    print(NEW)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except BaseException as error:
            print(error)
            sleep(30)
            continue
        finally:
            GPIO.cleanup()
