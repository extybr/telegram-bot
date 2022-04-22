from time import sleep
import requests
import telebot
from loguru import logger
from telebot import types
import RPi.GPIO as GPIO
from script_job_raspberry import search_jobs

token = 'bla-bla-bla'  # полученный токен бота
bot = telebot.TeleBot(token)
bot.remove_webhook()
# USER_X - id telegram ниже в коде изменены
USER_1 = 332458533
USER_2 = 558054155
USER_3 = 778054177
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
    url = 'https://skyteach.ru/wp-content/cache/thumb/d7/81a695a40a5dfd7_730x420.jpg'
    bot.send_photo(message.chat.id, photo=url, reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message) -> None:
    """
    Функция, обрабатывает нажатие кнопок бота
    Логирование в терминал
    Парсит курсы валют
    Запуск по условию: включение светодиода (реле), парсера вакансий, остановка бота
    """
    logger.info(message.text)
    if message.text == '💲 USD - EUR 💲':
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
            bot.send_message(message.chat.id,
                             f'Центробанк РФ:   {result_bank}\nБиржа Binance:   {result_binance}')
        except OSError:
            print('Сервер недоступен')
            bot.send_message(message.chat.id, 'Сервер недоступен')
    elif message.text == "🐷 Водички? 🐷":
        url_img = ("https://bestwine24.ru/image/cache/catalog/vodka"
                   "/eef2e315f762519e75aba64a800b63e9-540x720.jpg")
        bot.send_photo(message.chat.id, photo=url_img)
    elif message.text == "😎 read file 😎":
        if message.chat.id in (USER_1, USER_2):
            send_vacancies(message)
        else:
            bot.send_message(message.chat.id, 'Вам запрещено читать локальный файл 😄')
    elif message.text == "🌼 led on 🌼":
        if message.chat.id == USER_2:
            GPIO.output(25, GPIO.HIGH)
            bot.send_message(USER_2, 'Включаю чайник 😄')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено включать чайник 😄')
    elif message.text == "🌼 led off 🌼":
        if message.chat.id == USER_2:
            GPIO.output(25, GPIO.LOW)
            bot.send_message(USER_2, 'Выключаю чайник 😄')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено выключать чайник 😄')
    elif message.text == "🤓 мой id 🤓":
        bot.send_message(message.chat.id, f'id - {message.chat.id}\nИмя - '
                                          f'{message.from_user.full_name}'
                                          f'\nПользователь - {message.chat.username}')
    elif message.text == "🚷 bot_stop 🚷":
        if message.chat.id == USER_1:
            bot.send_message(message.chat.id, 'Выключение бота 😄')
            try:
                # bot.stop_polling()
                bot.stop_bot()
            except RuntimeError:
                print('Выключение бота')
        else:
            bot.send_message(message.chat.id, 'Вам запрещено выключать бота 😄')
    elif message.text == "🙏 работа 🙏":
        if message.chat.id in (USER_1, USER_2):
            search_jobs(message.chat.id, '96', '', '22', '1')
        elif message.chat.id == USER_3:
            search_jobs(message.chat.id, '', 'графический дизайнер', '22', '30')
        else:
            search_jobs(message.chat.id, '', '', '1979', '1')
        count = 0
        text = f'vacancies/{message.chat.id}.txt'  # путь к файлу и имя файла
        with open(text, 'r', encoding='utf-8') as txt:
            count += int(txt.readline().strip()[20:])
        if count > 10:
            send_vacancies(message)
        else:
            with open(text, 'r', encoding='utf-8') as txt:
                bot.send_message(message.chat.id, f'{txt.read()}')
    elif message.text == '🚷 stop 🚷':
        global NEW
        NEW[f'{message.chat.id}'] = 1
    else:
        bot.send_message(message.chat.id, f'Не надо баловаться 😡 {message.chat.first_name}\n\n'
                                          f'😜 И тебе того же:   {message.text}')


def send_vacancies(message) -> None:
    """ Читает локальный файл с вакансиями """
    text = f'vacancies/{message.chat.id}.txt'  # путь к файлу и имя файла
    count = 0
    count_local = 0
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
        count_local += int(txt.read().strip().count('🚘'))
    count_spam = count - count_local
    if message.chat.id in (USER_1, USER_2):
        bot.send_message(message.chat.id, f'Всего вакансий за сутки: {count}. В локальной базе: '
                                          f'{count_local}. Удаленных вакансий-спама: {count_spam}.')
    elif message.chat.id == USER_3:
        bot.send_message(message.chat.id, f'Число вакансий:  {count_local}')
    else:
        bot.send_message(message.chat.id, f'Число вакансий за сутки:  {count_local}\nБудут показаны'
                                          f' вакансии опубликованные за сутки с зарплатой не менее '
                                          f'70тыс. рублей\nПовторы и спам ({count_spam}шт.) будут '
                                          f'проигнорированы.')
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


@logger.catch
def telegram_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except BaseException as error:
            logger.error(error)
            sleep(30)
            continue
        finally:
            GPIO.cleanup()


if __name__ == '__main__':
    telegram_bot()
