from aiogram import Bot, Dispatcher
import asyncio
from app.handlers.handlers import router
from app.handlers.states import *
from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.handlers.scheduler import birthday_job
from app.config import NOTIFY_TIME


load_dotenv()


async def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    scheduler = AsyncIOScheduler()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await birthday_job(bot)
    scheduler.add_job(
        birthday_job,
        trigger=CronTrigger(hour=int(NOTIFY_TIME[:2]), minute=int(NOTIFY_TIME[3:])),
        args=[bot],
    )

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
