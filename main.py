import asyncio
import logging
import os

# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Dispatcher, Bot
from handlers.admin import admin
from handlers.tasks import user
from dotenv import load_dotenv
from data.bot import bot  # импортируем объект bot из bot.py


load_dotenv()
scheduler = AsyncIOScheduler()


async def main():
    dp = Dispatcher()
    dp.include_router(admin)
    dp.include_router(user)
    await bot.delete_webhook(drop_pending_updates=True)
    # Тем самым, сообщения, которые были отправлены боту, когда он был выключен, при включении будут игнорироваться

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("Bot stopped")
