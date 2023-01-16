from loguru import logger
from aiogram import types
from time import sleep
import os.path
from config import *


async def send_vacancies(message: types.Message, bot) -> None:
    """ Читает локальный файл с вакансиями """
    logger.info(f'{message.chat.id}: {message.text}')
    text = f'vacancies/{message.chat.id}.txt'
    count = 0
    count_local = 0
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
        count_local += int(txt.read().strip().count('🚘'))
    count_spam = count - count_local
    if message.chat.id in (USER_5, USER_6):
        user_text = (f'Всего вакансий: {count}. В локальной базе: {count_local}. Удаленных '
                     f'вакансий-спама: {count_spam}.')
        await bot.send_message(message.chat.id, user_text)
    else:
        await bot.send_message(message.chat.id, f'Число вакансий:  {count_local}')
    sleep(3)
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


async def send_less_vacancies(message: types.Message, bot) -> None:
    """ Читает и передает локальный файл с вакансиями """
    logger.info(f'{message.chat.id}: {message.text}')
    count = 0
    text = f'vacancies/{message.chat.id}.txt'
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
    if count > 10:
        await send_vacancies(message, bot)
    else:
        with open(text, 'r', encoding='utf-8') as txt:
            await bot.send_message(message.chat.id, f'{txt.read()}')
    if os.path.exists(f'vacancies/{message.chat.id}.txt'):
        download_file = open(f'vacancies/{message.chat.id}.txt', 'rb')
        await bot.send_document(message.chat.id, download_file)
