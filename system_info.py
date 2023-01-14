from aiogram import types
from loguru import logger
from requests import get
import platform
from sys import version
from json import dumps
from os import getlogin


async def get_system_info(message: types.Message, bot):
    """ Информация о системе сервера """
    try:
        ip = get('https://api.ipify.org').text
        information = get(url=f'http://ip-api.com/json/{ip}').json()
        full = dumps(information, indent=4)
        uname = getlogin()
        system = platform.platform()
        info = 'OS info:\n{}\n\nPython version is {} {}'.format(platform.uname(), version,
                                                                platform.architecture())
        await bot.send_message(message.chat.id, f"*Пользователь: {uname}*\n*IP:* {ip}\n*ОС: "
                                                f"{system}*\n*{info[:9]+info[21:]}*\n*{full}*",
                               parse_mode="markdown")
    except Exception as error:
        await bot.send_message(message.chat.id, 'Информационный сервер недоступен')
        logger.error(error)
