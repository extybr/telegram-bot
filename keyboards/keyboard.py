from aiogram import Bot
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def set_default_commands(bot: Bot) -> None:
    """ Дефолтные команды основного меню """
    menu = [BotCommand(command="start", description="Перезапустить бота"),
            BotCommand(command="help",
                       description="Подробная справка по командам бота")]
    await bot.set_my_commands(menu)


async def commands() -> (ReplyKeyboardMarkup, ReplyKeyboardMarkup):
    """ Функция вывода при старте: определение кнопок """
    button_1 = KeyboardButton(text='💲 USD - EUR 💲')
    button_2 = KeyboardButton(text='✔️ работа ✔️')
    button_3 = KeyboardButton(text='❌ stop ❌')
    button_4 = KeyboardButton(text='⚙️ мой id ⚙️')
    button_5 = KeyboardButton(text='🧜 Картинку? 🧚‍')
    button_6 = KeyboardButton(text='🔐 admin 🔐')
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(button_1, button_2, button_3, button_4, button_5, button_6, width=3)
    user: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    button_7 = KeyboardButton(text='✳️ read file ✳️')
    button_8 = KeyboardButton(text='💡 led on 💡')
    button_9 = KeyboardButton(text='💡 led off 💡')
    button_10 = KeyboardButton(text='✅Скриншот')
    button_11 = KeyboardButton(text='⛔️reboot⛔️')
    button_12 = KeyboardButton(text='🖥О сервере')
    button_13 = KeyboardButton(text='⏪Назад⏪')
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(button_7, button_3, button_8, button_9, button_10, button_11,
                button_12, button_13, width=4)
    root: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    return user, root
