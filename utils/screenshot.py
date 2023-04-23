from os import remove
from PIL import ImageGrab
from aiogram import Bot
from aiogram.types import Message, FSInputFile


async def get_screenshot(message: Message, bot: Bot) -> None:
    """ Функция делает скриншот и выводит пользователю """
    screen = ImageGrab.grab(bbox=None, all_screens=True)
    screen.save('screenshot.png')
    await bot.send_photo(message.from_user.id, photo=FSInputFile('screenshot.png'))
    remove('screenshot.png')
