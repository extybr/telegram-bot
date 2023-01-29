#!/usr/bin/env python3
from aiogram import types, Dispatcher, Bot, executor
from loguru import logger
from config import *
from hh_raspberry import search_job, region_id
from read_vacancies import send_vacancies, send_less_vacancies
from download_from_youtube import download_video_audio
from keyboard import commands
from exchange_rate import exchange, link_image
from system_info import get_system_info
from led_on_off import Led
from screenshot import get_screenshot
from shell import shell_cmd

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    """ Функция вывода при старте: приветствие """
    logger.info(f'{message.chat.id}: Старт бота')
    origin = ('Ну что готов к поиску работы? 😄\nЖми кнопки-команды внизу\n[✔️ работа ✔️] - '
              'Подробнее о поиске вакансий с сайта hh.ru\nКинув ссылку с youtube, вам будет скачано'
              ' видео по ссылке (до 50MB), а если после ссылки через пробел дописать audio, скачана'
              ' аудио дорожка\n[ /help ] - Подробная справка по командам')
    await bot.send_message(message.chat.id, origin, reply_markup=(await commands())[0])
    await bot.send_photo(message.chat.id, photo=types.InputFile('img/job.jpg'))


@dp.message_handler(commands=['help'])
async def start_message(message: types.Message):
    """ Функция вывода справки """
    logger.info(f'{message.chat.id}: помощь')
    origin = ('*[✔️ работа ✔️] - Подробнее о поиске вакансий с сайта hh.ru\n\n'
              '[❌ stop ❌] - Остановка вывода вакансий по работе\n\n'
              '[💲 USD - EUR 💲] - Курс валют USD, EUR, BTC, ETH\n\n'
              '[⚙️ мой id ⚙️] - Информация пользователя телеграм\n\n'
              '[🧜 Картинку? 🧚‍] - Вывод случайной картинки\n\n'
              'Кинув ссылку с youtube, вам будет скачано видео по ссылке (до 50MB), а если после '
              'ссылки через пробел дописать audio, скачана аудио дорожка*')
    await bot.send_message(message.chat.id, origin, parse_mode='Markdown')


@dp.message_handler()
async def text_message(message: types.Message):
    """
    Функция, обрабатывает нажатие кнопок бота
    Логирование в терминал
    """
    logger.info(f'{message.chat.id}: {message.text}')

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
        region = await region_id(hr[0][1:])
        days = hr[-1]
        if region is None:
            await bot.send_message(message.chat.id, 'Вы неправильно ввели название города')
        elif len(days) != 2 or not days.isdigit() or days == '00':
            await bot.send_message(message.chat.id, 'Вы неправильно ввели дату для поиска')
        else:
            if int(days) > 30:
                days = '30'
            await search_job(message.chat.id, '', f'{profession}', f'{region}', f'{days}')
            await send_less_vacancies(message, bot)

    elif message.text.startswith('#'):
        await shell_cmd(message, bot)

    elif message.text == '💲 USD - EUR 💲':
        await exchange(message, bot)

    elif message.text == "🧜 Картинку? 🧚‍":
        await link_image(message, bot)

    elif message.text == "✳️ read file ✳️":
        if message.chat.id in (USER_1, USER_2):
            await send_vacancies(message, bot)
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено читать локальный файл 😄')

    elif message.text == "💡 led on 💡":
        if message.chat.id in (USER_1, USER_2):
            led = Led()
            led.set_led_on_off(True)
            await bot.send_message(message.chat.id, 'Включаю чайник 😄')
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено включать чайник 😄')
    elif message.text == "💡 led off 💡":
        if message.chat.id in (USER_1, USER_2):
            led = Led()
            led.set_led_on_off(False)
            await bot.send_message(message.chat.id, 'Выключаю чайник 😄')
        else:
            await bot.send_message(message.chat.id, 'Вам запрещено выключать чайник 😄')

    elif message.text == "⚙️ мой id ⚙️":
        user_information = (f'*id - {message.chat.id}\nИмя - {message.from_user.full_name}\n'
                            f'Пользователь - @{message.chat.username}*')
        await bot.send_message(message.chat.id, user_information, parse_mode='Markdown')

    elif message.text == "🔐 admin 🔐":
        if message.chat.id in (USER_1, USER_2):
            await bot.send_message(message.chat.id, "❇️ Админ панель",
                                   reply_markup=(await commands())[1])
        else:
            await bot.send_message(message.chat.id, 'Эта кнопка только для администратора 😄')
            alert = (f"Кто-то пытался задать команду: {message.text}\n\nuser id: "
                     f"{message.from_user.id}\n"
                     f"first name: {message.from_user.first_name}\nlast name: "
                     f"{message.from_user.last_name}"
                     f"\nusername: @{message.from_user.username}")
            await bot.send_message(USER_1, alert)

    elif message.text == "✔️ работа ✔️":
        if message.chat.id in (USER_5, USER_6):
            await search_job(message.chat.id, '', 'парикмахер', '1979', '30')
            await send_less_vacancies(message, bot)
        else:
            example_search = ('*Введите данные для поиска в таком порядке*:\n\n`*`*[город] ['
                              'профессия с желаемой зарплатой] [число дней публикации объявлений '
                              '(max=30)]\n\nПримеры*:\n`*Воронеж водитель 10`\n`*Хабаровский край '
                              'парикмахер 30`\n`*Красноярск учитель истории 50000 07`\n\nгде `*` '
                              '- обязательный символ в начале,\n`Красноярск` - это город, вакансии '
                              'по которому будут искаться,\n`учитель истории` - профессия для '
                              'поиска,\n`50000` - минимальный уровень зарплаты для поиска,\n`07` - '
                              'поиск за последние 7 дней.')
            await bot.send_message(message.chat.id, example_search, parse_mode='Markdown')

    elif message.text == '❌ stop ❌':
        NEW[f'{message.chat.id}'] = 1
        logger.info(f'{NEW}')

    elif list(filter(lambda x: message.text.startswith(x), ['https://youtu.be/',
                                                            'https://www.youtu.be/',
                                                            'https://youtube.com/',
                                                            'https://www.youtube.com/'])):
        await download_video_audio(message, bot)

    elif message.text == "⛔️reboot⛔️":
        if message.chat.id in (USER_1, USER_2):
            await bot.send_message(message.chat.id, 'Выключаю 😄')
            try:
                from os import system
                system('reboot')
            except RuntimeError:
                logger.error('Перезагрузка')

    elif message.text == "🖥О сервере":
        await get_system_info(message, bot)

    elif message.text == "✅Скриншот":
        await get_screenshot(message, bot)

    elif message.text == "⏪Назад⏪":
        await bot.send_message(message.chat.id, "❗️ Главная панель",
                               reply_markup=(await commands())[0])

    else:
        fail = (f'*Не надо баловаться* 😡 *{message.chat.first_name}*\n\n😜 *И тебе того же:   '
                f'{message.text}*')
        await bot.send_message(message.chat.id, fail, parse_mode='Markdown')
        await message.delete()


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Перезапустить бота"),
        types.BotCommand("help", "Подробная справка по командам бота")
    ])

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=True)
