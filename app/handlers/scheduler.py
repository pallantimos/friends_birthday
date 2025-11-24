from app.database.request import get_upcoming_birthdays
from app.config import NOTIFY_TIME
from aiogram import Bot


async def birthday_job(bot: Bot):
    """ "Отправка уведомления о ближайших днях рождения"""
    data = await get_upcoming_birthdays()
    if data:
        text = ""
        for person in data:
            text = text + (f"Скоро день рождения {person.name} {person.date_birth}\n")
        await bot.send_message(
            chat_id=person.user_id,
            text=text,
        )
