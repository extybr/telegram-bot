#!/usr/bin/env python3
from asyncio import run
from filters import user_filter
from aiogram import Bot, Dispatcher
from config_files.config import Config, load_config
from keyboards.keyboard import set_default_commands


async def main():
    config: Config = load_config('config_files/.env')
    bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher()
    dp.include_router(user_filter.router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    run(main())
