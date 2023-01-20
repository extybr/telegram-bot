from PIL import ImageGrab
from aiogram import types
from os import remove


async def get_screenshot(message: types.Message, bot):
    """ Функция делает скриншот и выводит пользователю """
    screen = ImageGrab.grab(bbox=None, all_screens=True)
    screen.save('screenshot.png')
    await bot.send_photo(message.chat.id, photo=types.InputFile('screenshot.png'))
    remove('screenshot.png')
