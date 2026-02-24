from apscheduler.schedulers.background import BackgroundScheduler

import logging

from . import send_daily_digest_and_weather
from database.db import reset_daily_progress


logger = logging.getLogger(__name__)

def start_scheduler():
    """Создает и запускает планировщик задач"""

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_digest_and_weather,
        'cron',
        hour=7,
        minute=00,
        id='daily_digest',
        replace_existing=True
    )
    scheduler.add_job(
        reset_daily_progress,
        'cron',
        hour=0,
        minute=0,
        id='reset_daily_progress'
    )

    scheduler.start()
    logger.info("🕐 Планировщик запущен: 07:00 рассылка + 00:00 сброс")
    return scheduler