from datetime import datetime
import threading

from telebot import types

from config import bot
from parsers.api import *
from database.db import *


recent_users = set()

@bot.message_handler(commands=['digest'])
def digest_handler(message: types.Message) -> None:
    """Обработчик команды новостей"""

    user_id = message.from_user.id
    today = datetime.now().strftime('%Y-%m-%d')
    user_progress = (UsersNewsProgress
                     .select()
                     .join(Users)
                     .where((Users.user_id == user_id) & (UsersNewsProgress.day == today))
                     .order_by(UsersNewsProgress.updated_at.desc())
                     .first()
                     )
    if not user_progress:
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
        bot.send_message(message.chat.id,
                         "⚡ <b>СУПЕРСКОРОСТЬ!</b> ⏳ Подожди 3 сек...",
                         parse_mode='HTML')
        return
    recent_users.add(user_id)

    next_pack = user_progress.last_pack + 1
    if pack_exists(today, next_pack):
        news_pack = get_news_pack(today, next_pack)
    else:
        news_pack = news_api(5)
        save_news_pack(today, next_pack, news_pack)

    if news_pack:
        user_name = message.from_user.username or "User"

        # ОТПРАВЛЯЕМ НОВОСТИ
        for i, news in enumerate(news_pack, 1):
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

        user_progress.last_pack = next_pack
        user_progress.updated_at = datetime.now()
        user_progress.save()

        bot.send_message(user_id,
                         "<b>/digest</b> → следующая пачка новостей!",
                         parse_mode='HTML')

    threading.Timer(3.0, lambda uid=user_id: recent_users.discard(uid)).start()

    # ОБНОВЛЯЕМ СЕРИЮ
    streak_grew = update_streak(user_id)

    user_progress = (UsersNewsProgress
                     .select()
                     .join(Users)
                     .where((Users.user_id == user_id) & (UsersNewsProgress.day == today))
                     .first()
                     )

    # ПРОВЕРЯЕМ УРОВЕНЬ
    new_level, level_name = calculate_daily_level(user_progress.last_pack)
    if new_level > user_progress.daily_level:
        user_progress.daily_level = new_level
        bot.send_message(user_id,
                         f"🎉 <b>🏆 НОВЫЙ УРОВЕНЬ!</b>\n"
                         f"{level_name} ⭐\n"
                         f"📦 <b>{user_progress.last_pack}</b> пачек сегодня!",
                         parse_mode='HTML'
                         )

    user_progress.save()

    bot.send_message(user_id,
                     f"📊 <b>ТВОЙ ПРОГРЕСС:</b>\n"
                     f"📦 Сегодня: <b>{user_progress.last_pack}</b> пачек\n"
                     f"🔥 Серия: <b>{user_progress.streak_current}</b> дней\n"
                     f"🏅 /profile → полный профиль!",
                     parse_mode='HTML'
                     )



