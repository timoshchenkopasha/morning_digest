import telebot
from telebot.types import Message

from config import bot
from database import UsersNewsProgress, Users
from database.db import calculate_daily_level


@bot.message_handler(commands=['profile'])
def profile_handler(message: Message) -> None:
    """Игровой профиль / статистика пользователя"""

    user_id = message.from_user.id
    user_progress = (UsersNewsProgress
                     .select()
                     .join(Users)
                     .where(Users.user_id == user_id)
                     .order_by(UsersNewsProgress.updated_at.desc())
                     .first())

    if not user_progress:
        bot.send_message(message.chat.id,
                         "🌱 <b>НОВИЧОК В MORNINGDOM!</b>\n\n"
                         "⚔️ <code>/start</code> → вступи в игру!\n"
                         "🔥 <code>/digest</code> → первая пачка!\n"
                         "<i>Пора качать утреннюю продуктивность! 💪</i>",
                         parse_mode='HTML')
        return

    user = user_progress.user
    daily_level_num, daily_level_name = calculate_daily_level(user_progress.last_pack)

    profile_text = f"""🏆 <b>⚔️ ТВОЙ ПРОФИЛЬ: {user.user_name}</b> 🏅

    📊 <b>🎯 СТАТИСТИКА ДНЯ:</b>
    📦 Пачек: <b>{user_progress.last_pack}</b> 
    ⭐ Уровень: <b>{daily_level_num}</b> <i>{daily_level_name}</i>

    🔥 <b>🏅 ТВОЯ СЕРИЯ:</b>
    📅 Текущая: <b>{user_progress.streak_current}</b> дней
    🏆 Рекорд: <b>{user_progress.streak_max}</b> дней

    🌍 Город: <code>{user.city}</code>"""

    bot.send_message(message.chat.id, profile_text, parse_mode='HTML')
