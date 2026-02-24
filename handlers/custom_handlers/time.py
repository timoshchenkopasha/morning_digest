from telebot import types
from config import bot
from database.db import Users
from utils.sheduler import *
from keyboards import city_keyboard_func

TIME_KEYBOARD = types.InlineKeyboardMarkup()
for hour in [5, 6, 7, 8, 9, 10]:
    TIME_KEYBOARD.row(
        types.InlineKeyboardButton(
            f"{hour}:00",
            callback_data=f"set_time_{hour}"
        )
    )


@bot.message_handler(commands=['time'])
def time_handler(message: types.Message):
    """⏰ Выбор времени рассылки"""
    user_id = message.from_user.id

    # ПРОВЕРКА: есть ли город?
    user = Users.get_or_none(Users.user_id == user_id)
    if not user or not user.city:
        bot.send_message(
            message.chat.id,
            "❌ <b>СНАЧАЛА ВЫБЕРИ ГОРОД!</b>\n\n"
            "👇 <b>Нажми 'Мой город' → Минск/Москва → /time</b>",
            parse_mode='HTML',
            reply_markup=city_keyboard_func()  # Добавь импорт!
        )
        return

    bot.send_message(
        message.chat.id,
        """⏰ <b>ВЫБЕРИ ВРЕМЯ РАССЫЛКИ:</b>

🔥 <b>Каждый день в ТОЧНОЕ время:</b>
• Погода твоего города ☀️
• 5 новостей из <b>ТВОЕЙ СТРАНЫ</b> 📰

👇 Выбери удобное время:""",
        reply_markup=TIME_KEYBOARD,
        parse_mode='HTML'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_time_'))
def set_time_callback(call):
    hour = int(call.data.split('_')[2])
    user_id = call.from_user.id

    # БЕЗОПАСНОЕ сохранение
    user = Users.get_or_none(Users.user_id == user_id)
    if not user:
        bot.answer_callback_query(call.id, "❌ Сначала выбери город!")
        return
    user.daily_send_hour = hour
    user.save()

    # Планируем задачу
    schedule_user_digest(user_id, hour)

    bot.answer_callback_query(call.id, f"✅ {hour}:00 установлено!")
    bot.edit_message_text(
        f"""🎉 <b>✅ РАССЫЛКА {hour}:00 НАСТРОЕНА!</b> ⚔️

⏰ <b>Каждый день в {hour}:00</b> получишь:
☀️ <b>Погода:</b> {user.city}
📰 <b>Новости:</b> {user.interests or 'general'}
📦 <b>+1</b> к прогрессу + серия дней!

📱 <b>ПРОВЕРЬ:</b>
/profile — твой профиль 🏆
/digest — новости СЕЙЧАС! 🔥""",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML'
    )
