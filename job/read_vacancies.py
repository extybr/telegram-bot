from os.path import exists
from loguru import logger
from time import sleep
from aiogram import Bot
from aiogram.types import Message, FSInputFile
from config_files.config import Config, load_config
from keyboards.inline import process_beginning_command, FLAG


async def send_less_vacancies(message: Message, bot: Bot) -> None:
    """ Читает и передает локальный файл с вакансиями """
    logger.info(f'{message.chat.id}: {message.text}')
    if message.chat.id not in FLAG:
        FLAG[message.chat.id] = {'flag': 0, 'page': 1, 'links': []}
    count = 0
    text = f'vacancies/{message.chat.id}.txt'
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
    if count > 10:
        await send_vacancies(message, bot)
    else:
        with open(text, 'r', encoding='utf-8') as txt:
            await bot.send_message(message.chat.id, f'{txt.read()}')
        await create_links(message)
        if len(FLAG[message.chat.id]['links']) > 0:
            await process_beginning_command(message)
    if exists(f'vacancies/{message.chat.id}.txt'):
        await bot.send_document(message.chat.id,
                                FSInputFile(f'vacancies/{message.chat.id}.txt'))


async def send_vacancies(message: Message, bot: Bot) -> None:
    """ Читает локальный файл с вакансиями """
    logger.info(f'{message.chat.id}: {message.text}')
    config: Config = load_config('config_files/.env')
    if message.chat.id not in FLAG:
        FLAG[message.chat.id] = {'flag': 0, 'page': 1, 'links': []}
    text = f'vacancies/{message.chat.id}.txt'
    count = 0
    count_local = 0
    with open(text, 'r', encoding='utf-8') as txt:
        count += int(txt.readline().strip()[20:])
        count_local += int(txt.read().strip().count('🚘'))
    count_spam = count - count_local
    if message.chat.id in config.tg_bot.user_ids:
        user_text = (f'Всего вакансий: {count}. В локальной базе: '
                     f'{count_local}. Удаленных вакансий-спама: {count_spam}.')
        await bot.send_message(message.chat.id, user_text)
    else:
        await bot.send_message(message.chat.id, f'Число вакансий:  {count_local}')
    sleep(3)
    FLAG[message.chat.id]['flag'] = 0
    if count > 0:
        with open(text, 'r', encoding='utf-8') as txt:
            for line in txt.readlines():
                if FLAG[message.chat.id]['flag'] == 1:
                    await bot.send_message(message.chat.id,
                                           'Принудительная остановка вывода '
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
    FLAG[message.chat.id]['flag'] = 0
    logger.info(f'{FLAG}')
    await create_links(message)
    if len(FLAG[message.chat.id]['links']) > 0:
        await process_beginning_command(message)


async def create_links(message: Message):
    logger.info(f'{message.chat.id}: {message.text}')
    text = f'vacancies/{message.chat.id}.txt'
    job_lnk = []
    with open(text, 'r', encoding='utf-8') as txt:
        for line in txt.readlines():
            if line.find('https://') != -1:
                job_lnk.append(f'{line[12:].strip()}')
        FLAG[message.chat.id]['links'] = job_lnk
    logger.info(f'{FLAG}')
