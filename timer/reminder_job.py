# timer/reminder_job.py

import asyncio
from datetime import datetime
from dateutil import parser  # или dateparser, если ты используешь свободный текст


async def send_reminder(tg_bot, chat_id: int, text: str, end_time_str: str):
    # Преобразуем строку в datetime
    end_time = parser.parse(end_time_str)  # ← если строка вида "15/06/2025 21:30:00"

    # Вычисляем задержку
    delay = (end_time - datetime.now()).total_seconds()

    if delay > 0:
        await asyncio.sleep(delay)

    await tg_bot.send_message(chat_id, f"⏰ Напоминание: {text}")
