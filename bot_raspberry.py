#!/usr/bin/env python3
from asyncio import run
from aiogram import Dispatcher
from filters.user_filter import bot, router
from keyboards.keyboard import set_default_commands


async def main():
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
