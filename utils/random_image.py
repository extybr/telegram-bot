from loguru import logger
from requests import get
from random import choices, randint
from aiogram import Bot
from aiogram.types import Message, FSInputFile


async def get_source_link(message: Message, bot: Bot) -> None:
    """ Парсит случайные изображения """
    try:
        _choice = ['river', 'nature', 'lake', 'animals', 'mountain']
        # choice = ['cats', 'town', 'cosmos', 'planet', 'sea', 'dog', 'car', 'people']
        # choice = ['sexy', 'sexual', 'beauty', 'eyes', 'lips', 'kiss', 'love', 'girl', 'woman']
        _result = choices(_choice)
        _link = get(f'https://source.unsplash.com/random/?{_result}').url
        await bot.send_photo(message.chat.id, photo=_link)
    except Exception as error:
        logger.error('Сервер 2 недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/vodka.jpg'))


async def get_link(message: Message, bot: Bot) -> None:
    """ Парсит случайные изображения """
    try:
        api_scenery = "https://api.scenery.cx/get_image_info/{0}"
        link_scenery = "https://scenery.cx/images/{0}.jpg"
        choice = randint(1, 193591)
        api = get(api_scenery.format(choice)).text
        if api == "null":
            print(api)
            return await get_link(message, bot)
        link = link_scenery.format(choice)
        await bot.send_photo(message.chat.id, photo=link)
    except Exception:
        logger.error('Сервер 1 недоступен')
        await get_source_link(message, bot)
