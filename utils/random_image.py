from loguru import logger
from requests import get, exceptions
from random import choices, randint
from aiogram import Bot
from aiogram.types import Message, FSInputFile


async def resource_link_availability(message, bot):
    source = {get_link_scenery: 'https://scenery.cx',
              get_link_unsplash: 'https://source.unsplash.com/random'}
    for key, value in source.items():
        try:
            response = get(value, timeout=1.5).status_code
            if response == 200:
                logger.info(f'Запрос к ресурсу: {value}')
                return await key(message, bot)
        except exceptions.ReadTimeout:
            logger.error(f'Timeout: {value}')
            continue
        except exceptions.ConnectionError:
            logger.error(f'ConnectionError: {value}')
            continue
    await bot.send_message(message.chat.id, 'Сервер изображений недоступен')


async def get_link_unsplash(message: Message, bot: Bot) -> None:
    """ Парсит случайные изображения """
    _resource = 'source.unsplash.com'
    try:
        _choice = ['river', 'nature', 'lake', 'animals', 'mountain']
        # choice = ['cats', 'town', 'cosmos', 'planet', 'sea', 'dog', 'car', 'people']
        # choice = ['sexy', 'sexual', 'beauty', 'eyes', 'lips', 'kiss', 'love', 'girl', 'woman']
        _result = choices(_choice)
        _link = get(f'https://{_resource}/random/?{_result}').url
        await bot.send_photo(message.chat.id, photo=_link)
    except Exception as error:
        logger.error(f'Сервер {_resource} недоступен')
        await bot.send_message(message.chat.id, f'Сервер {_resource} недоступен')
        if str(error).find('Error code: 400'):
            await bot.send_photo(message.chat.id,
                                 photo=FSInputFile(path='img/vodka.jpg'))


async def get_link_scenery(message: Message, bot: Bot) -> None:
    """ Парсит случайные изображения """
    _resource = 'scenery.cx'
    try:
        choice = randint(1, 207295)
        api_scenery = f"https://api.{_resource}/get_image_info/{choice}"
        link_scenery = f"https://{_resource}/images/{choice}.jpg"
        api = get(api_scenery).text
        if api == "null":
            print(api)
            return await get_link_scenery(message, bot)
        link = link_scenery.format(choice)
        await bot.send_photo(message.chat.id, photo=link)
    except Exception:
        logger.error(f'Низкая скорость доступа к серверу {_resource} ... попытка')
        await bot.send_message(message.chat.id, f'Низкая скорость доступа к '
                                                f'серверу {_resource} ... попытка')
        await resource_link_availability(message, bot)
