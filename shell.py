from shlex import quote, split
from subprocess import run
from aiogram import types
from loguru import logger


async def shell_cmd(message: types.Message, bot):
    """ Выводит пользователю результат команды терминала (ограничение по длине вывода) """
    command = message.text[1:]
    args = command.split(' ')
    args.pop(0)
    clean = [quote(i) for i in args]
    full_command = split(f"{command} {''.join(clean)}")
    try:
        result = run(full_command, capture_output=True).stdout.decode()
        await bot.send_message(message.chat.id, f"{result}")
    except Exception as error:
        logger.error(error)
