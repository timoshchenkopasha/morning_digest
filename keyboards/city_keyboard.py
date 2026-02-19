from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def city_keyboard_func() -> InlineKeyboardMarkup:
    """Клавиатура популярных городов"""

    markup = InlineKeyboardMarkup(row_width=2)

    cities = [
        ('🇧🇾 Минск', 'Минск'),
        ('🇷🇺 Москва', 'Москва'),
        ('🇺🇦 Киев', 'Киев'),
        ('🇷🇺 СПб', 'Санкт-Петербург'),
        ('🇰🇿 Алматы', 'Алматы'),
        ('🇷🇺 Екатеринбург', 'Екатеринбург'),
        ('📝 Другой город...', 'other')
    ]

    #список рядов по 2 кнопки
    keyboard = []
    for i in range(0, len(cities) - 1, 2):  # По парам
        row = [
            InlineKeyboardButton(cities[i][0], callback_data=cities[i][1]),
            InlineKeyboardButton(cities[i + 1][0], callback_data=cities[i + 1][1])
        ]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(cities[-1][0], callback_data=cities[-1][1])])  # Последняя

    markup.keyboard = keyboard  # Прямое присвоение!
    return markup


