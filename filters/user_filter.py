from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command, CommandStart, Text
from loguru import logger
from job.hh_raspberry import search_job, region_id
from job.read_vacancies import send_vacancies, send_less_vacancies
from utils.download_from_youtube import download_video_audio
from utils.exchange_rate import exchange
from utils.random_image import resource_link_availability
from utils.system_info import get_system_info
from utils.led_on_off import Led
from utils.screenshot import get_screenshot
from utils.shell import shell_cmd
from keyboards.keyboard import commands
from config_files.config import Config, load_config
from keyboards.inline import create_pagination_keyboard, FLAG

config: Config = load_config('config_files/.env')
admin: config = config.tg_bot.admin_ids
user: config = config.tg_bot.user_ids
bot: Bot = Bot(token=config.tg_bot.token)
dp: Dispatcher = Dispatcher()
router: Router = Router()


@router.message(CommandStart())
async def start_message(message: Message):
    """ Функция вывода при старте: приветствие """
    logger.info(f'{message.chat.id}: Старт бота')
    origin = ('Ну что готов к поиску работы? 😄\nЖми кнопки-команды внизу\n'
              '[✔️ работа ✔️] - Подробнее о поиске вакансий с сайта hh.ru\n'
              'Кинув ссылку с youtube, вам будет скачано видео по ссылке '
              '(до 50MB), а если после ссылки через пробел дописать audio, '
              'скачана аудио дорожка\n[ /help ] - Подробная справка по командам')
    await bot.send_photo(message.chat.id, photo=FSInputFile(path='img/job.jpg'),
                         caption=origin, reply_markup=(await commands())[0])


@router.message(Command(commands=['help']))
async def start_message(message: Message):
    """ Функция вывода справки """
    logger.info(f'{message.chat.id}: помощь')
    origin = ('<b>[✔️ работа ✔️] - Подробнее о поиске вакансий с сайта hh.ru'
              '\n\n[❌ stop ❌] - Остановка вывода вакансий по работе\n\n'
              '[💲 USD - EUR 💲] - Курс валют USD, EUR, BTC, ETH\n\n'
              '[⚙️ мой id ⚙️] - Информация пользователя телеграм\n\n'
              '[🧜 Картинку? 🧚‍] - Вывод случайной картинки\n\n'
              'Кинув ссылку с youtube, вам будет скачано видео по ссылке '
              '(до 50MB), а если после ссылки через пробел дописать audio, '
              'скачана аудио дорожка</b>')
    await bot.send_message(message.chat.id, origin, parse_mode='HTML')


@router.message(F.content_type.in_({'photo', 'video', 'video_note', 'animation',
                                    'sticker', 'audio', 'voice', 'document'}))
async def text_message(message: Message):
    """ Удаление спама (фото, видео, аудио, стикеров, анимации) """
    await message.delete()


@router.callback_query(Text(endswith='   в начало   '))
async def beginning_command(callback: CallbackQuery):
    logger.info(f'{callback.message.text}')
    if (callback.from_user.id in FLAG) and (
            FLAG[callback.from_user.id]["page"] != 1):
        FLAG[callback.from_user.id]["page"] = 1
        text = FLAG[callback.from_user.id]['links'][0]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                FLAG[callback.from_user.id]["page"],
                len(FLAG[callback.from_user.id]['links'])))


@router.callback_query(Text(text='>>'))
async def process_forward_press(callback: CallbackQuery):
    logger.info(f'{callback.message.text}')
    if (callback.from_user.id in FLAG) and (
            FLAG[callback.from_user.id]["page"] < len(
            FLAG[callback.from_user.id]['links'])):
        FLAG[callback.from_user.id]["page"] += 1
        text = (FLAG[callback.from_user.id]['links']
        [FLAG[callback.from_user.id]["page"] - 1])
        if callback.message.text == text:
            FLAG[callback.from_user.id]["page"] += 1
            text = (FLAG[callback.from_user.id]['links']
            [FLAG[callback.from_user.id]["page"] - 1])
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                FLAG[callback.from_user.id]["page"],
                len(FLAG[callback.from_user.id]['links'])))


@router.callback_query(Text(text='<<'))
async def process_backward_press(callback: CallbackQuery):
    logger.info(f'{callback.message.text}')
    if (callback.from_user.id in FLAG) and (
            FLAG[callback.from_user.id]["page"] > 1):
        FLAG[callback.from_user.id]["page"] -= 1
        text = (FLAG[callback.from_user.id]['links']
        [FLAG[callback.from_user.id]["page"] - 1])
        if callback.message.text == text:
            FLAG[callback.from_user.id]["page"] -= 1
            text = (FLAG[callback.from_user.id]['links']
            [FLAG[callback.from_user.id]["page"] - 1])
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                FLAG[callback.from_user.id]["page"],
                len(FLAG[callback.from_user.id]['links'])))


@router.message(F.text)
async def text_message(message: Message):
    """
    Функция, обрабатывает нажатие кнопок бота
    Логирование в терминал
    """
    logger.info(f'{message.chat.id}: {message.text}')
    if message.text.startswith('*'):
        hr = message.text.split(' ')
        profession = ''
        if (hr[0] or hr[1]) in ['Республика', 'республика', 'край', 'область']:
            hr[0] = hr[0] + ' ' + hr.pop(1)
        for i in hr:
            if i == hr[0]:
                continue
            if i == hr[len(hr) - 1]:
                break
            profession += ''.join(i + ' ')
        profession = profession.strip()
        region = await region_id(hr[0][1:])
        days = hr[-1]
        if region is None:
            await bot.send_message(message.chat.id,
                                   'Вы неправильно ввели название города')
        elif len(days) != 2 or not days.isdigit() or days == '00':
            await bot.send_message(message.chat.id,
                                   'Вы неправильно ввели дату для поиска')
        else:
            if int(days) > 30:
                days = '30'
            await search_job(message.chat.id, '', f'{profession}', f'{region}',
                             f'{days}')
            await send_less_vacancies(message, bot)

    elif message.text.startswith('#'):
        if message.chat.id in admin:
            await shell_cmd(message, bot)

    elif message.text == '💲 USD - EUR 💲':
        await exchange(message, bot)

    elif message.text == "🧜 Картинку? 🧚‍":
        await resource_link_availability(message, bot)

    elif message.text == "✳️ read file ✳️":
        if message.chat.id in admin:
            await send_vacancies(message, bot)
        else:
            await bot.send_message(message.chat.id,
                                   'Вам запрещено читать локальный файл 😄')

    elif message.text == "💡 led on 💡":
        if message.chat.id in admin:
            led = Led()
            led.set_led_on_off(True)
            await bot.send_message(message.chat.id, 'Включаю чайник 😄')
        else:
            await bot.send_message(message.chat.id,
                                   'Вам запрещено включать чайник 😄')
    elif message.text == "💡 led off 💡":
        if message.chat.id in admin:
            led = Led()
            led.set_led_on_off(False)
            await bot.send_message(message.chat.id, 'Выключаю чайник 😄')
        else:
            await bot.send_message(message.from_user.id,
                                   'Вам запрещено выключать чайник 😄')

    elif message.text == "⚙️ мой id ⚙️":
        ids = f'id - {message.chat.id}'
        if message.from_user.id != message.chat.id:
            ids = (f'chat_id = {message.chat.id},\n'
                   f'user_id - {message.from_user.id}')
        user_information = (f'<b>{ids}\n'
                            f'Имя - {message.chat.full_name}\n'
                            f'Пользователь - @{message.chat.username}</b>')
        await bot.send_message(message.chat.id, user_information,
                               parse_mode='HTML')

    elif message.text == "🔐 admin 🔐":
        if message.chat.id in admin:
            await bot.send_message(message.chat.id, "❇️ Админ панель",
                                   reply_markup=(await commands())[1])
        else:
            await bot.send_message(message.chat.id,
                                   'Эта кнопка только для администратора 😄')
            alert = (f"<b>Кто-то пытался задать команду: {message.text}\n\n"
                     f"user id: {message.chat.id}\n"
                     f"first name: {message.from_user.first_name}\n"
                     f"last name: {message.from_user.last_name}\n"
                     f"fullname: {message.chat.full_name}\n"
                     f"username: @{message.chat.username}</b>")
            await bot.send_message(admin[0], alert, parse_mode='HTML')

    elif message.text == "✔️ работа ✔️":
        if message.chat.id in user:
            await search_job(message.chat.id, '', 'парикмахер', '1979', '30')
            await send_less_vacancies(message, bot)
        else:
            example_search = ('*Введите данные для поиска в таком порядке*:\n\n'
                              '`*`*[город] [профессия с желаемой зарплатой] '
                              '[число дней публикации объявлений (max=30)]\n\n'
                              'Примеры*:\n`*Воронеж водитель 10`\n`*Хабаровский'
                              ' край парикмахер 30`\n`*Россия инженер асу'
                              ' 150000 05`\n`*Красноярск учитель '
                              'истории 50000 07`\n\nгде `*` - обязательный '
                              'символ в начале,\n`Красноярск` - это город, '
                              'вакансии по которому будут искаться,\n`учитель '
                              'истории` - профессия для поиска,\n`50000` - '
                              'минимальный уровень зарплаты для поиска,\n`07` '
                              '- поиск за последние 7 дней.')
            await bot.send_message(message.chat.id, example_search,
                                   parse_mode='Markdown')

    elif message.text == '❌ stop ❌':
        if message.chat.id in FLAG:
            FLAG[message.chat.id]['flag'] = 1

    elif list(filter(lambda x: message.text.startswith(x), [
        'https://youtu.be/',
        'https://www.youtu.be/',
        'https://youtube.com/',
        'https://www.youtube.com/'
    ])):
        await download_video_audio(message, bot)

    elif message.text == "⛔️reboot⛔️":
        if message.chat.id in admin:
            await bot.send_message(message.chat.id, 'Выключаю 😄')
            try:
                from os import system
                system('reboot')
            except RuntimeError:
                logger.error('Перезагрузка')

    elif message.text == "🖥О сервере":
        await get_system_info(message, bot)

    elif message.text == "✅Скриншот":
        await get_screenshot(message, bot)

    elif message.text == "⏪Назад⏪":
        await bot.send_message(message.chat.id, "❗️ Главная панель",
                               reply_markup=(await commands())[0])

    else:
        fail = (f'<b>Не надо баловаться* 😡 {message.chat.first_name}\n\n'
                f'😜 И тебе того же:   {message.text}</b>')
        await message.answer(text=fail, parse_mode='HTML')
        await message.delete()
