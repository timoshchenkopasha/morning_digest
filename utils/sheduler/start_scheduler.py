from apscheduler.schedulers.background import BackgroundScheduler
import logging
from database.db import Users, reset_daily_progress

# ✅ ГЛОБАЛЬНЫЙ ПЛАННИРОВЩИК
scheduler = None
logger = logging.getLogger(__name__)


def start_scheduler():
    """Создает и запускает планировщик задач"""
    global scheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_digest_and_weather,  # Импорт ниже!
        'cron',
        hour=7,
        minute=0,
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


def schedule_user_digest(user_id: int, hour: int):
    """📅 Планирует индивидуальную рассылку"""
    global scheduler

    try:
        scheduler.remove_job(f'user_digest_{user_id}')
    except:
        pass

    # ✅ НОВАЯ ФУНКЦИЯ!
    from utils.sheduler.send_digest import send_individual_digest
    scheduler.add_job(
        send_individual_digest,
        'cron',
        hour=hour,
        minute=0,
        args=[user_id],
        id=f'user_digest_{user_id}',
        replace_existing=True
    )
    logger.info(f"⏰ Пользователь {user_id}: {hour}:00")


def schedule_all_users():
    """📅 Планирует ВСЕХ пользователей"""
    global scheduler
    if not scheduler:
        logger.error("❌ Scheduler не запущен!")
        return

    users = Users.select()
    for user in users:
        schedule_user_digest(user.user_id, user.daily_send_hour)
        logger.info(f"⏰ Загружена задача: {user.user_name or user.user_id} → {user.daily_send_hour}:00")


# ✅ ЛЕНИВЫЕ ИМПОРТЫ (после определения функций)
from .send_digest import send_daily_digest_and_weather
