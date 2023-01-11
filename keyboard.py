from aiogram import types


async def commands():
    """ Функция вывода при старте: определение кнопок """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton('💲 USD - EUR 💲')
    button_2 = types.KeyboardButton('✔️ работа ✔️')
    button_3 = types.KeyboardButton('❌ stop ❌')
    button_4 = types.KeyboardButton('⚙️ мой id ⚙️')
    button_5 = types.KeyboardButton('🐷 Водички? 🐷')
    button_6 = types.KeyboardButton('🔐 admin 🔐')
    markup.row(button_1, button_2, button_3)
    markup.row(button_4, button_5, button_6)
    root = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_7 = types.KeyboardButton('✳️ read file ✳️')
    button_8 = types.KeyboardButton('💡 led on 💡')
    button_9 = types.KeyboardButton('💡 led off 💡')
    button_10 = types.KeyboardButton('✅Скриншот')
    button_11 = types.KeyboardButton('⛔️reboot⛔️')
    button_12 = types.KeyboardButton('🖥О компьютере')
    button_13 = types.KeyboardButton('⏪Назад⏪')
    root.row(button_7, button_3, button_8, button_9)
    root.row(button_10, button_11, button_12, button_13)
    return markup, root
