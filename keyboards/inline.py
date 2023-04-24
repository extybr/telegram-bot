from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

FLAG = dict()


def create_pagination_keyboard(page, length) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    btn = ['<<', f'{page}/{length}   в начало   ', '>>']
    buttons = [InlineKeyboardButton(text=i, callback_data=i) for i in btn]
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()


async def process_beginning_command(message: Message):
    links = FLAG[message.chat.id]['links']
    text = links[0]
    await message.answer(
        text=text, reply_markup=create_pagination_keyboard(1, len(links)))
