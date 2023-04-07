from loguru import logger
from requests import get
from pathlib import Path
from aiogram import Bot
from aiogram.types import Message


async def exchange(message: Message, bot: Bot) -> None:
    """ Парсит курсы валют, показывает температуру RaspberryPi """
    try:
        binance = get('https://api.binance.com/api/v1/ticker/24hr').json()
        price_btc, price_eth = 0, 0
        for coin in binance:
            if coin['symbol'] == 'BTCUSDT':
                price_btc = int(float(coin.get('lastPrice', 0)))
            elif coin['symbol'] == 'ETHUSDT':
                price_eth = int(float(coin.get('lastPrice', 0)))
        result_binance = f'BTCUSDT - {price_btc}  /  ETHUSDT - {price_eth}'
        bank = get('https://www.cbr-xml-daily.ru/latest.js').json()
        bank_1 = round(1 / bank["rates"]['USD'], 3)
        bank_2 = round(1 / bank["rates"]['EUR'], 3)
        result_bank = f'USD - {bank_1}  /  EUR - {bank_2}'
        temperature = ''
        thermal = Path('/sys/class/thermal/thermal_zone0/temp')
        if thermal.exists():
            with open(thermal, 'r') as temp:
                temperature = round(int(temp.read()) / 1000, 2)
                temperature = f"Температура = {temperature} 'C"
        output = (f'<b>Центробанк РФ:   {result_bank}\nБиржа Binance:   '
                  f'{result_binance}\n{temperature}</b>')
        await bot.send_message(message.chat.id, output, parse_mode='HTML')
    except OSError:
        logger.error('Сервер недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
