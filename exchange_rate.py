from loguru import logger
from requests import get
from aiogram import types


async def exchange(message: types.Message, bot):
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
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp:
            temperature = round(int(temp.read()) / 1000, 2)
            temperature = f"Температура = {temperature} 'C"
        output = f'*Центробанк РФ:   {result_bank}\nБиржа Binance:   {result_binance}\n{temperature}*'
        await bot.send_message(message.chat.id, output, parse_mode='Markdown')
    except OSError:
        logger.error('Сервер недоступен')
        await bot.send_message(message.chat.id, 'Сервер недоступен')
        
        
async def link_image(message: types.Message, bot):
    """ Парсит курсы валют, показывает температуру RaspberryPi """
    try:
        from random import choices
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
            await bot.send_photo(message.chat.id, photo=types.InputFile('img/vodka.jpg'))
