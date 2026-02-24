from telebot.types import Message

import logging

from config import bot
from database import *
from keyboards import *
from parsers.api import validate_city


logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def start_handler(message):
    """Обработчик команды /start, начало игры с выбором города"""

    bot.send_message(
        message.chat.id,
        """🌅 <b>🚀 WELCOME TO Утренний Дайджест!</b>

    💥 <b>ЭТО ТВОЙ НОВЫЙ УТРЕННИЙ РИТУАЛ:</b>
    ☕ <b>КОФЕ + НОВОСТИ + ПОГОДА = ПРОДУКТИВНЫЙ ДЕНЬ</b>

<b>🔧 НАСТРОЙ СВОЙ БОТ (3 шага):</b>
1️⃣ <b>ВЫБЕРИ ГОРОД</b> → персональная погода ☀️
2️⃣ <b>/interests</b> → <b>выбери интересные темы: технологии 💻, спорт ⚽</b>
3️⃣ <b>/time</b> → выбери время рассылки (5:00-10:00) ⏰
4️⃣ <b>/digest</b> → <b>персональные новости по интересам!</b> 🔥

    <b>🏆 УРОВНИ И СЕРИЯ:</b>
    🌱 <b>Читатель</b> → 1 пачка/день  
    📈 <b>Активный</b> → 2 пачки
    🌟 <b>Профи дня</b> → 3+ пачки!
    🔥 <b>+ Серия дней подряд = 🏆</b>

    👇 <b>ПЕРВЫЙ ШАГ: Выбери город!</b>""",
        parse_mode='HTML',
        reply_markup=city_keyboard_func()
    )
    user_id = message.from_user.id
    user_name = message.from_user.username or "User"
    logger.info(f"👤 Новый пользователь {user_id}")
    set_user_progress(user_id, user_name, 0)
    return

@bot.callback_query_handler(func=lambda call: True)
def handle_city_selection(call):
    """Обрабатывает выбор города с клавиатуры"""

    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    user_name = call.from_user.username or call.from_user.first_name

    if call.data == 'other':
        bot.reply_to(call.message, "🌍 <b>📝 Напиши название города:</b>")
        bot.register_next_step_handler(call.message, handle_manual_city)
        return

    if set_user_city(user_id, user_name, call.data):
        bot.send_message(
            call.from_user.id,
            f"""🎉 <b>🏆 {call.data.upper()} - ГОРОД ПРИНЯТ! ⚔️</b>

✅ <b>ГОРОД: {call.data}</b> ☀️ <i>Погода готова!</i>

<b>🔥 ЧТО ДЕЛАТЬ ДАЛЬШЕ (2 минуты):</b>
2️⃣ <b>/interests</b> → <b>выбери интересные темы: технологии 💻, спорт ⚽</b>
3️⃣ <b>/time</b> → выбери время рассылки (5:00-10:00) ⏰
4️⃣ <b>/digest</b> → <b>персональные новости по интересам!</b> 🔥🔥

<b>📊 /profile</b> → твой профиль + серия дней 🏆""",
            parse_mode='HTML'
        )


def handle_manual_city(message):
    """Сохраняет город введённый вручную"""

    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name
    city = message.text.strip()

    is_valid = validate_city(city)

    if is_valid:
        if set_user_city(user_id, user_name, city):
            bot.send_message(
                message.from_user.id,
                f"""🎉 <b>🏆 {city.upper()} - ГОРОД ПРИНЯТ! </b>

            ✅ <b>ГОРОД: {city}</b> ☀️ <i>Погода готова!</i>

            <b>🔥 ЧТО ДЕЛАТЬ ДАЛЬШЕ (2 минуты):</b>
            2️⃣ <b>/interests</b> → <b>выбери интересные темы: технологии 💻, спорт ⚽</b>
            3️⃣ <b>/time</b> → выбери время рассылки (5:00-10:00) ⏰
            4️⃣ <b>/digest</b> → <b>персональные новости по интересам!</b> 🔥🔥

            <b>📊 /profile</b> → твой профиль + серия дней 🏆""",
                parse_mode='HTML'
            )

        else:
            bot.send_message(
                message.chat.id,
                "❌ <b>⚠️ Сбой процесса</b>\n🔄 <code>/start</code> — новый заход!",
                parse_mode='HTML'
            )
    else:
        bot.reply_to(
            message,
            f"""❌ <b>🌍 {city} НЕ НАЙДЕН! Введи другой город. </b>

🔄 <b>Попробуй:</b>
• Правильное написание
• Минск, Москва, Киев
• <code>/start</code> — популярные города""",
            parse_mode='HTML'
        )
        bot.register_next_step_handler(message, handle_manual_city)

