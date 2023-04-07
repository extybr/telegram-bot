from loguru import logger
from requests import get
from random import choices
from aiogram import Bot
from aiogram.types import Message, FSInputFile


async def get_link(message: Message, bot: Bot) -> None:
    """ Парсит курсы валют, показывает температуру RaspberryPi """
    try:
        choice = ['river', 'nature', 'lake', 'animals', 'mountain']
        # choice = ['cats', 'town', 'cosmos', 'planet', 'sea', 'dog', 'car', 'people']
        # choice = ['sexy', 'sexual', 'beauty', 'eyes', 'lips', 'kiss', 'love', 'girl', 'woman']
        result = choices(choice)
        link = get(f'https://source.unsplash.com/random/?{result}').url
        await bot.send_photo(message.chat.id, photo=link)
    except Exception as error:
        logger.error('Сервер недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/vodka.jpg'))
