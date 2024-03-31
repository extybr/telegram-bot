import asyncio
from aiohttp import ClientSession
from aiofiles import open
from json import loads
from loguru import logger
from pathlib import Path
from aiogram import Bot
from aiogram.types import Message


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def read_temperature():
    temperature = ''
    thermal = Path('/sys/class/thermal/thermal_zone0/temp')
    if thermal.exists():
        async with open(thermal, 'r') as temp:
            degree = round(int(await temp.read()) / 1000, 2)
            temperature = f"Температура = {degree} 'C"
    return temperature


async def exchange(message: Message, bot: Bot) -> None:
    """ Парсит курсы валют, показывает температуру RaspberryPi """
    try:
        async with ClientSession() as session:

            urls = ['https://api.binance.com/api/v1/ticker/24hr',
                    'https://www.cbr-xml-daily.ru/latest.js']

            tasks = [asyncio.create_task(fetch(session, url)) for url in urls]
            task3 = asyncio.create_task(read_temperature())
            result = await asyncio.gather(*tasks, task3)

            binance = loads(result[0])
            price_btc, price_eth = 0, 0
            for coin in binance:
                if coin['symbol'] == 'BTCUSDT':
                    price_btc = int(float(coin.get('lastPrice', 0)))
                elif coin['symbol'] == 'ETHUSDT':
                    price_eth = int(float(coin.get('lastPrice', 0)))
            result_binance = f'BTCUSDT - {price_btc}  /  ETHUSDT - {price_eth}'

            bank = loads(result[1])
            usd = 1 / bank["rates"]['USD']
            eur = 1 / bank["rates"]['EUR']
            result_bank = 'USD - {:.3f}  /  EUR - {:.3f}'.format(usd, eur)

            output = (f'<b>Центробанк РФ:   {result_bank}\nБиржа Binance:   '
                      f'{result_binance}\n{result[2]}</b>')

            await bot.send_message(message.chat.id, output, parse_mode='HTML')

    except OSError:
        logger.error('Сервер недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
