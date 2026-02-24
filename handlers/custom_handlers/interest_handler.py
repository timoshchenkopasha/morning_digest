import logging

from telebot import types

from config import bot
from database.db import Users, UsersNewsProgress
from datetime import datetime
from keyboards import create_interests_keyboard


logger = logging.getLogger(__name__)

# Словарь для нормализации интересов
INTERESTS_RU_EN = {
    'технологии': 'tech',
    'технологии и гаджеты': 'tech',
    'технологии+гаджеты': 'tech',
    'гаджеты': 'tech',
    'it': 'tech',
    'программирование': 'tech',

    'спорт': 'sport',
    'футбол': 'sport',
    'хоккей': 'sport',
    'теннис': 'sport',

    'политика': 'politics',
    'политические новости': 'politics',

    'бизнес': 'business',
    'экономика': 'business',
    'финансы': 'business',

    'искусственный интеллект': 'ai',
    'ии': 'ai',
    'нейросети': 'ai',
    'машинное обучение': 'ai',

    'наука': 'science',
    'астрономия': 'science',
    'физика': 'science',

    'здоровье': 'health',
    'медицина': 'health',

    'путешествия': 'travel',
    'туризм': 'travel'
}

AVAILABLE_INTERESTS = {
    'tech': '🚀 Технологии',
    'sport': '⚽ Спорт',
    'politics': '🏛️ Политика',
    'business': '💰 Бизнес',
    'ai': '🤖 ИИ',
    'science': '🔬 Наука',
    'health': '🏥 Здоровье',
    'travel': '✈️ Путешествия'
}

user_interests = {}  # Временное хранилище выбора пользователя


@bot.message_handler(commands=['interests'])
def interests_handler(message: types.Message):
    """Выбор интересов пользователя"""

    user_id = message.from_user.id
    user_name = message.from_user.username or "User"

    # Инициализируем выбор пользователя
    user_interests[user_id] = []

    keyboard = create_interests_keyboard()

    bot.send_message(
        message.chat.id,
        """🤔 <b>🎯 ВЫБЕРИ СВОИ ИНТЕРЕСЫ</b>

<b>Как это работает:</b>
• Выбери <b>2-4</b> темы (максимум)
• /digest будет показывать новости <b>ТОЛЬКО</b> по твоим темам
• <b>УТРОМ</b> - рассылка новостей из <b>ТВОЕЙ СТРАНЫ</b> (всегда)

3️⃣ <b>/time</b> → выбери время рассылки (5:00-10:00) ⏰
4️⃣ <b>/digest</b> → <b>персональные новости по интересам!</b> 🔥🔥

<i>👇 Выбирай кнопками снизу и нажми <b>СОХРАНИТЬ</b>👇</i>""",
        parse_mode='HTML',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('interest_'))
def handle_interest_selection(call):
    """Обрабатывает выбор/снятие интересов"""

    user_id = call.from_user.id
    data = call.data

    bot.answer_callback_query(call.id)

    if user_id not in user_interests:
        user_interests[user_id] = []

    current_selection = user_interests[user_id]

    if data.startswith('interest_add_'):
        interest_key = data.replace('interest_add_', '')
        if interest_key not in current_selection and len(current_selection) < 4:
            current_selection.append(interest_key)

    elif data.startswith('interest_remove_'):
        interest_key = data.replace('interest_remove_', '')
        if interest_key in current_selection:
            current_selection.remove(interest_key)

    elif data == 'interest_clear':
        current_selection.clear()

    elif data == 'interest_save':
        # Сохраняем интересы
        save_user_interests(user_id, current_selection)
        bot.edit_message_text(
            f"🎉 <b>✅ ИНТЕРЕСЫ СОХРАНЕНЫ!</b>\n\n"
            f"📋 <b>Твои темы:</b> {', '.join([AVAILABLE_INTERESTS[i] for i in current_selection])}\n\n"
            f"🔥 <b>Теперь /digest</b> = новости <b>только по ТВОИМ ИНТЕРЕСЕМ!</b>\n"
            f"📦 Утро = общие новости из <b>ТВОЕЙ СТРАНЫ</b>\n"
            f"3️⃣ <b>/time</b> → выбери время рассылки (5:00-10:00) ⏰\n"
            f"4️⃣ <b>/digest</b> → <b>персональные новости по интересам!</b> 🔥",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )
        return

    # Обновляем клавиатуру
    new_keyboard = create_interests_keyboard(current_selection)
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=new_keyboard
    )

    # Показываем статус выбора
    selected_names = [AVAILABLE_INTERESTS[i] for i in current_selection]
    status_text = f"✅ Выбрано: {len(selected_names)}/4\n" + ', '.join(
        selected_names) if selected_names else "❌ Ничего не выбрано"

    bot.answer_callback_query(
        call.id,
        status_text,
        show_alert=True
    )


def save_user_interests(user_id: int, interests: list):
    """Сохраняет интересы пользователя в БД"""

    try:
        user = Users.get(Users.user_id == user_id)
        today = datetime.now().strftime('%Y-%m-%d')

        # СОХРАНЯЕМ В ПРАВИЛЬНОЕ МЕСТО!
        user.interests = '+'.join(interests) if interests else 'general'  # ← Users.interests!
        user.save()

        # Опционально: прогресс тоже
        progress, created = UsersNewsProgress.get_or_create(
            user=user, day=today, defaults={'last_pack': 0}
        )
        progress.updated_at = datetime.now()
        progress.save()

        user_interests.pop(user_id, None)
        logger.info(f"✅ Интересы {user_id}: {interests} → '{user.interests}'")

    except Exception as e:
        logger.error(f"❌ Интересы {user_id}: {e}")




