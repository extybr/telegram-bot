from aiogram.types import Message
from aiogram import Bot
from loguru import logger
from requests import get
from os import getlogin
from sys import version
from platform import platform, uname
from json import dumps


async def get_system_info(message: Message, bot: Bot):
    """ Информация о системе сервера """
    try:
        ip = get('https://api.ipify.org').text
        information = get(url=f'http://ip-api.com/json/{ip}').json()
        full = dumps(information, indent=4)
        name = f'{uname()}'[13:-1]
        info = (f"<b>Пользователь: {getlogin()}\nIP: {ip}\nОС: {platform()}\n"
                f"OS info: {name}\nPython version is {version}\n{full}</b>")
        await bot.send_message(message.from_user.id, info, parse_mode="HTML")
    except Exception as error:
        await bot.send_message(message.from_user.id,
                               'Информационный сервер недоступен')
        logger.error(error)
