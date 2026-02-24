from datetime import datetime
import threading
import logging
from telebot import types

from config import bot
from parsers.api import *
from database.db import *


logger = logging.getLogger(__name__)
recent_users = set()

@bot.message_handler(commands=['digest'])
def digest_handler(message: types.Message) -> None:
    """Обработчик команды новостей"""

    user_id = message.from_user.id
    logger.info(f"📨 /digest от {user_id}")

    today = datetime.now().strftime('%Y-%m-%d')
    user_progress = (UsersNewsProgress
                     .select()
                     .join(Users)
                     .where((Users.user_id == user_id) & (UsersNewsProgress.day == today))
                     .order_by(UsersNewsProgress.updated_at.desc())
                     .first()
                     )

    if not user_progress:
        logger.info(f"👤 Новый пользователь {user_id}")
        user_name = message.from_user.username or "User"
        set_user_progress(user_id, user_name, 0)
        bot.send_message(
            message.chat.id,
            f"""<b>🚀 MorningDigest — ТВОË НАЧАЛО ДНЯ! ⚡</b>

<b>Введи - /start</b>
<i>💥 Новости обещают быть интересными! 🌅</i>""",
            parse_mode='HTML'
        )
        return

    if user_id in recent_users:
        logger.warning(f"⏳ Rate limit для {user_id}")
        bot.send_message(message.chat.id,
                         "⚡ <b>СУПЕРСКОРОСТЬ!</b> ⏳ Подожди 3 сек...",
                         parse_mode='HTML')
        return

    recent_users.add(user_id)
    logger.info(f"✅ /digest разрешен для {user_id}")

    user_interest = get_user_interests(user_id)
    next_pack = user_progress.last_pack + 1
    logger.info(f"📦 Пачка {next_pack} для {user_id}")

    if pack_exists(today, user_interest, next_pack):
        news_pack = get_news_pack(today, user_interest, next_pack)
        logger.info(f"✅ Пачка {next_pack} из БД: {len(news_pack) if news_pack else 0} новостей")
    else:
        logger.info("🌐 Качаем свежие новости...")
        news_pack = news_api_interests(user_interest, 5)
        if news_pack:
            save_news_pack(today, user_interest, next_pack, news_pack)
            logger.info(f"💾 Сохранена пачка {next_pack}: {len(news_pack)} новостей")
        else:
            logger.error("❌ news_api вернул пусто")
            recent_users.discard(user_id)
            return

    if news_pack and len(news_pack) > 0:
        logger.info(f"📤 Отправляем {len(news_pack)} новостей")

        # ОТПРАВЛЯЕМ НОВОСТИ
        sent_count = 0
        for i, news in enumerate(news_pack, 1):
            title = news['title'][:100]
            caption = f'{i}. <b>{title}</b>\n\n🔗 {news["url"]}'

            try:
                if 'image_url' in news and news['image_url']:
                    bot.send_photo(chat_id=user_id, photo=news['image_url'],
                                   caption=caption, parse_mode='HTML')
                    logger.debug(f"🖼️  Новость {i} с фото")
                else:
                    bot.send_message(user_id, caption, parse_mode='HTML')
                    logger.debug(f"📄 Новость {i} текстом")
                sent_count += 1
            except Exception as e:
                logger.error(f"❌ Ошибка отправки {i}: {e}")
                bot.send_message(user_id, caption, parse_mode='HTML')

        # Обновляем прогресс
        user_progress.last_pack = next_pack
        user_progress.updated_at = datetime.now()
        streak_grew = update_streak(user_id)
        logger.info(f"🔥 streak_grew: {streak_grew}")

        logger.info(f"💾 Прогресс: пачка {user_progress.last_pack}, стрик {user_progress.streak_current}")
        user_progress.save()

        bot.send_message(user_id, "<b>/digest</b> → следующая пачка новостей!", parse_mode='HTML')

        # Проверка уровня
        new_level, level_name = calculate_daily_level(user_progress.last_pack)
        if new_level > user_progress.daily_level:
            user_progress.daily_level = new_level
            bot.send_message(user_id,
                             f"🎉 <b>🏆 НОВЫЙ УРОВЕНЬ!</b>\n{level_name} ⭐\n📦 <b>{user_progress.last_pack}</b> пачек сегодня!",
                             parse_mode='HTML')
            user_progress.save()
            logger.info(f"🎉 Уровень {new_level} для {user_id}")

        bot.send_message(user_id,
                         f"📊 <b>ТВОЙ ПРОГРЕСС:</b>\n"
                         f"📦 Сегодня: <b>{user_progress.last_pack}</b> пачек\n"
                         f"🔥 Серия: <b>{user_progress.streak_current}</b> дней\n"
                         f"🏅 /profile → полный профиль!",
                         parse_mode='HTML')
        logger.info(f"✅ /digest завершен: {sent_count}/{len(news_pack)} новостей отправлено")

    else:
        logger.error(f"💥 Пустая пачка {next_pack}, retry...")
        recent_users.discard(user_id)
        return

    # Rate limit timer
    def remove_rate_limit(uid):
        recent_users.discard(uid)
        logger.debug(f"⏰ Rate limit снят для {uid}")

    threading.Timer(3.0, remove_rate_limit, args=[user_id]).start()
