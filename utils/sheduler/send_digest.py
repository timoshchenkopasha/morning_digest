import time
from datetime import datetime

from database.db import *
from handlers.custom_handlers import *
from parsers.api.news_api import *
from parsers.api.weather_api import get_daily_forecast
from config import bot


def get_subscribers() -> List:
    """Возврщает всех подписчиков бота"""

    try:
        users = Users.select()
        return [(user.user_id, user.city, user.user_name or 'User') for user in users]
    except Exception as e:
        print(f'Ошибка в при возврате подписчиков в get_subscribers(): {e}')
        return []

def format_weather_message(forecast: Dict) -> str:
    """Красивая погода с прогнозом день/ночь"""

    city = forecast['city']
    day_range = forecast['day_temp']
    night_range = forecast['night_temp']
    day_desc_en = forecast['day_desc']
    humidity = forecast['humidity']
    wind_speed = forecast['wind_speed']

    # Русские описания
    ru_desc = {
        'Clear': '☀️ ясно',
        'Clouds': '☁️ облачно',
        'Rain': '🌧️ дождь',
        'Snow': '❄️ снег',
        'Drizzle': '🌦️ морось',
        'Thunderstorm': '⛈️ гроза',
        'Mist': '🌫️ туман',
        'Fog': '🌫️ туман',
        'Haze': '🌫️ дымка',
        'Dust': '🌫️ пыль'
    }

    # Безопасный fallback
    desc_ru = ru_desc.get(day_desc_en, '🌤️ переменная')

    return f"""🌅 <b>Доброе утро, {city}!</b>

<b>📊 Днем:</b> {day_range}°C {desc_ru}
<b>🌙 Ночью:</b> {night_range}°C

💨 <b>Ветер:</b> {wind_speed} м/с
💧 <b>Влажность:</b> {humidity}%"""

def send_daily_digest_and_weather():
    """Обработчик команды новостей. Определяем наличие нужной пачки для пользователя в бд,
    если есть - оправляем пользоветелю, если нет - делаем запрос к апи и потом оправляем пользоветелю.
    Так же идет учет дневного прогресса новостей"""

    print("🔔 07:00 — утренняя рассылка новостей! 💥")
    today = datetime.now().strftime('%Y-%m-%d')
    news_pack_1 = news_api(5)
    if not news_pack_1:
        print("❌ API не работает!")
        return
    save_news_pack(today, 1, news_pack_1)

    subscribers = get_subscribers()
    print(f"кол-во пользователей: {len(subscribers)}!")
    if not subscribers:
        print("❌ БД ПУСТАЯ! Напиши /digest")
        return

    for user_id, user_city, user_name in subscribers:
        weather_info = get_daily_forecast(user_city)
        if weather_info:
            caption = format_weather_message(weather_info)
            bot.send_message(user_id, caption, parse_mode='HTML')
        else:
            bot.send_message(user_id,
                           "🌤️ <b>ПОГОДА НЕ ВАЖНА</b>\n☀️ Главное — твое настроение. Хорошего дня ❤️",
                           parse_mode='HTML')

        bot.send_message(user_id,
                        "⚔️ <b>УТРЕННЯЯ АТАКА НОВОСТЕЙ!</b>\n🔥 <b>ПЕРВАЯ ПАЧКА ДНЯ</b>",
                        parse_mode='HTML')

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
            bot.send_message(user_id,
                           "🎉 <b>ПЕРВАЯ ПАЧКА ЗАГРУЖЕНА!</b>\n"
                           "📦 <b>/digest</b> → вторая пачка!\n"
                           "📊 <b>/profile</b> → твой прогресс!",
                           parse_mode='HTML')
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Ошибка рассылки {user_id}: {e}")