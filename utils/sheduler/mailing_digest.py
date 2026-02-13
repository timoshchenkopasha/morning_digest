import time
from apscheduler.schedulers.background import BackgroundScheduler
from database.db import *
from datetime import datetime
from handlers.custom_handlers import *
from parsers.api.news_api import *
from config import bot


def get_subscribers() -> List:
    """Возврщает всех подписчиков рассылки (subscribed=1)"""

    try:
        users = Users.select()
        print(users)
        return [(user.user_id, user.user_name or 'User') for user in users]
    except Exception as e:
        print(f'Ошибка в при возврате подписчиков в get_subscribers(): {e}')
        return []

def send_daily_digest():
    """Рассылка свежих новостей каждое утро подсписчику"""

    print("🔔 8:00 — НАЧИНАЕМ УТРЕННИЙ ДАЙДЖЕСТ!")
    today = datetime.now().strftime('%Y-%m-%d')
    news_pack_1 = news_api(5)
    if not news_pack_1:
        print("❌ API не работает!")
        return
    save_news_pack(today, 1, news_pack_1)

    subscribers = get_subscribers()
    print(f"ТЕСТ: {len(subscribers)} пользователей в БД")
    if not subscribers:
        print("❌ БД ПУСТАЯ! Напиши /digest")
        return

    for user_id, user_name in subscribers:
        bot.send_message(user_id, "<b>🌅 Доброе утро!</b>\nЕжедневный дайджест:", parse_mode='HTML')
        try:
            for i, news in enumerate(news_pack_1, 1):
                title = news['title'][:100]
                caption = f'{i}. <b>{title}</b>\n\n🔗 {news["url"]}'
                if 'image_url' in news and news['image_url']:
                    try:
                        bot.send_photo(
                            chat_id=user_id,
                            photo=news['image_url'],
                            caption=caption,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        print(f'❌Ошибка в отправке фотографии: {e}')
                        bot.send_message(user_id, caption, parse_mode='HTML')

                else:
                    bot.send_message(user_id, caption, parse_mode='HTML')
            set_user_progress(user_id, user_name, 1)
            bot.send_message(user_id, "<b>➕ Остальные новости:</b> /digest", parse_mode='HTML')

            print(f"✅ Рассылка {user_name} ({user_id})")
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Ошибка рассылки {user_id}: {e}")

def start_scheduler():
    """Создает и запускает планировщик задач"""

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_digest,
        'cron',
        hour=17,
        minute=52, #для проверки
        id='daily_digest',
        replace_existing=True
    )

    scheduler.start()
    print("🕐 Планировщик запущен: ЕЖЕДНЕВНО 8:00")
    return scheduler