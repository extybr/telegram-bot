from loguru import logger
from requests import get
from aiogram import types


async def exchange(message: types.Message, bot):
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
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as termal:
            temperature = round(int(termal.read()) / 1000, 2)
            temperature = f"Температура = {temperature} 'C"
        output = f'*Центробанк РФ:   {result_bank}\nБиржа Binance:   {result_binance}\n{temperature}*'
        await bot.send_message(message.chat.id, output, parse_mode='Markdown')
    except OSError:
        logger.error('Сервер недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
