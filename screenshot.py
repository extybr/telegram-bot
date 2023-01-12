from PIL import ImageGrab
from aiogram import types
from os import remove


async def get_screenshot(message: types.Message, bot):
    """ Функция делает скриншот и выводит пользователю """
    screen = ImageGrab.grab(bbox=None, all_screens=True)
    screen.save('screenshot.png')
    img_file = open('screenshot.png', 'rb')
    await bot.send_photo(message.chat.id, img_file)
    remove('screenshot.png')
