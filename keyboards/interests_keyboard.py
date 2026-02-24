from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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

def create_interests_keyboard(selected=None):
    """Создаёт клавиатуру интересов"""

    if selected is None:
        selected = []

    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []

    for interest_key, interest_name in AVAILABLE_INTERESTS.items():
        if interest_key in selected:
            # Уже выбрано — кнопка "убрать"
            btn = InlineKeyboardButton(
                f"✅ {interest_name}",
                callback_data=f"interest_remove_{interest_key}"
            )
        else:
            # Доступно для выбора
            btn = InlineKeyboardButton(
                interest_name,
                callback_data=f"interest_add_{interest_key}"
            )
        buttons.append(btn)

    # Кнопки управления
    row1 = [
        InlineKeyboardButton("🔄 Очистить всё", callback_data="interest_clear"),
        InlineKeyboardButton("✅ Сохранить", callback_data="interest_save")
    ]

    keyboard.add(*buttons)
    keyboard.row(*row1)

    return keyboard

def interests_keyboard():
    """Клавиатура с кнопкой интересов для основного меню"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton('/interests'), KeyboardButton('/digest'))

    return keyboard