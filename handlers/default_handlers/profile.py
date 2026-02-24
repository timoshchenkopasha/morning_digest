from telebot.types import Message
from datetime import datetime


from config import bot
from database import UsersNewsProgress, Users
from database.db import calculate_daily_level


import logging
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['profile'])
def profile_handler(message: Message):
    user_id = message.from_user.id
    today = datetime.today().strftime('%Y-%m-%d')

    # 1. ПРОГРЕСС
    progress = (UsersNewsProgress
                .select()
                .join(Users)
                .where((Users.user_id == user_id) & (UsersNewsProgress.day == today))
                .first())

    # 2. ПОЛЬЗОВАТЕЛЬ
    user = Users.get_or_none(Users.user_id == user_id)

    # Безопасные значения
    packs = progress.last_pack if progress else 0
    streak_current = progress.streak_current if progress else 0
    streak_max = progress.streak_max if progress else 0
    level, level_name = calculate_daily_level(packs)

    # ПРАВИЛЬНОЕ время рассылки
    send_time = f"{user.daily_send_hour}:00" if user and user.daily_send_hour else 'Не настроена'

    logger.info(f"🔍 DEBUG profile {user_id}:")
    logger.info(f"  user.interests = '{user.interests}'")
    logger.info(f"  user.interests is None? {user.interests is None}")
    logger.info(f"  len(user.interests) = {len(user.interests) if user.interests else 'None'}")



    profile_text = f"""
🏆 <b>ТВОЙ ПРОФИЛЬ: {user.user_name or 'User'} 🏅</b>

📊 <b>🎯 СТАТИСТИКА ДНЯ:</b>
📦 Пачек: <b>{packs}</b> 
⭐ Уровень: <b>{level}</b> {level_name}

🔥 <b>🏅 ТВОЯ СЕРИЯ:</b>
📅 Текущая: <b>{streak_current}</b> дней
🏆 Рекорд: <b>{streak_max}</b> дней

🌍 <b>Город:</b> {user.city if user else 'Не установлен'}
⏰ <b>Рассылка:</b> {send_time}
📰 <b>Интересы:</b> {user.interests if user else 'general'}
"""

    bot.send_message(message.chat.id, profile_text, parse_mode='HTML')



