from loguru import logger
from requests import get
import platform
from sys import version
from json import dumps
from os import getlogin
from config import *


async def get_system_info(bot):
    """ Информация о системе сервера """
    try:
        ip = get('http://ip.42.pl/raw').text
        information = get(url=f'http://ip-api.com/json/{ip}').json()
        full = dumps(information, indent=4)
        uname = getlogin()
        system = platform.platform()
        info = 'OS info:\n{}\n\nPython version is {} {}'.format(platform.uname(), version,
                                                                platform.architecture())
        await bot.send_message(USER_1, f"*Пользователь: {uname}*\n*IP:* {ip}\n*ОС: {system}*\n"
                                       f"*{info[:9]+info[21:]}*\n*{full}*", parse_mode="markdown")
    except Exception as error:
        await bot.send_message(USER_1, 'Информационный сервер недоступен')
        logger.error(error)
