import time
from concurrent.futures import ThreadPoolExecutor

from database.db import *
from parsers.api.news_api import *
from parsers.api.weather_api import get_daily_forecast
from config import bot
from utils import get_country_by_city

logger = logging.getLogger(__name__)


def get_subscribers() -> List:
    """Возвращает всех подписчиков бота"""

    try:
        users = Users.select()
        return [(user.user_id, user.city, user.user_name or 'User') for user in users]
    except Exception as e:
        logger.error(f'❌ get_subscribers: {e}')
        return []

def format_weather_message(forecast: Dict) -> str:
    """Красивая погода с прогнозом день/ночь"""

    city = forecast['city']
    day_range = forecast['day_temp']
    night_range = forecast['night_temp']
    day_desc_en = forecast['day_desc']
    humidity = forecast['humidity']
    wind_speed = forecast['wind_speed']

    ru_desc = {
        'Clear': '☀️ ясно', 'Clouds': '☁️ облачно', 'Rain': '🌧️ дождь',
        'Snow': '❄️ снег', 'Drizzle': '🌦️ морось', 'Thunderstorm': '⛈️ гроза',
        'Mist': '🌫️ туман', 'Fog': '🌫️ туман', 'Haze': '🌫️ дымка', 'Dust': '🌫️ пыль'
    }
    desc_ru = ru_desc.get(day_desc_en, '🌤️ переменная')

    return f"""🌅 <b>Доброе утро, {city}!</b>

<b>📊 Днем:</b> {day_range}°C {desc_ru}
<b>🌙 Ночью:</b> {night_range}°C

💨 <b>Ветер:</b> {wind_speed} м/с
💧 <b>Влажность:</b> {humidity}%"""


def send_daily_digest_and_weather():
    """КЭШ ПО СТРАНАМ! 1 API = 100 пользователей!"""

    logger.info("🔔 07:00 — утренняя рассылка новостей!")
    today = datetime.now().strftime('%Y-%m-%d')

    subscribers = get_subscribers()
    if not subscribers:
        logger.warning("❌ Нет подписчиков!")
        return

    logger.info(f"👥 Всего пользователей: {len(subscribers)}")

    # ШАГ 1: ГРУППИРУЕМ ПО СТРАНАМ
    country_users = {}
    for user_id, user_city, user_name in subscribers:
        country = get_country_by_city(user_city)
        country_users.setdefault(country, []).append((user_id, user_city, user_name))

    logger.info(f"🌍 По странам: {dict((k, len(v)) for k, v in country_users.items())}")

    # ШАГ 2: 1 API НА СТРАНУ (КЭШ!)
    country_news_cache = {}  # { 'by': [news_pack], 'ru': [news_pack] }

    for country, users in country_users.items():
        interest_hash = f"morning_{country}"

        logger.info(f"🌐 {country}: {len(users)} пользователей, interest_hash={interest_hash}")

        # Проверяем КЭШ
        if pack_exists(today, interest_hash, 1):
            logger.info(f"✅ {country}: пачка из КЭША")
            news_pack = get_news_pack(today, interest_hash, 1)
        else:
            logger.info(f"🌐 {country}: API запрос...")
            news_pack = news_api_interests('general', 5, country)
            if news_pack:
                save_news_pack(today, interest_hash, 1, news_pack)
                logger.info(f"💾 {country}: пачка сохранена в КЭШ")
            else:
                logger.error(f"❌ {country}: API не работает!")
                continue

        country_news_cache[country] = news_pack

    # ШАГ 3: РАССЫЛКА ИЗ КЭША (параллельно)
    def send_to_user(user_data):
        user_id, user_city, user_name = user_data
        country = get_country_by_city(user_city)
        news_pack = country_news_cache.get(country)

        if not news_pack:
            logger.error(f"❌ Нет новостей для {country} ({user_id})")
            return

        try:
            # Погода (персональная)
            weather_info = get_daily_forecast(user_city)
            if weather_info:
                bot.send_message(user_id, format_weather_message(weather_info), parse_mode='HTML')
            else:
                bot.send_message(user_id, "🌤️ <b>ПОГОДА НЕ ВАЖНА</b>\n☀️ Хорошего дня ❤️", parse_mode='HTML')

            # Новости ИЗ КЭША
            bot.send_message(user_id, "⚔️ <b>УТРЕННЯЯ АТАКА НОВОСТЕЙ!</b>\n🔥 <b>ПЕРВАЯ ПАЧКА ДЛЯ ТВОЕЙ СТРАНЫ</b>",
                             parse_mode='HTML')

            for i, news in enumerate(news_pack, 1):
                title = news['title'][:100]
                caption = f'{i}. <b>{title}</b>\n\n🔗 {news["url"]}'
                if 'image_url' in news and news['image_url']:
                    try:
                        bot.send_photo(user_id, news['image_url'], caption=caption, parse_mode='HTML')
                    except Exception as e:
                        logger.error(f"❌ Фото {user_id}: {e}")
                        bot.send_message(user_id, caption, parse_mode='HTML')
                else:
                    bot.send_message(user_id, caption, parse_mode='HTML')
                time.sleep(0.05)  # Антифлуд

            # Прогресс
            set_user_progress(user_id, user_name, 1)
            bot.send_message(user_id,
                             "🎉 <b>ПЕРВАЯ ПАЧКА ЗАГРУЖЕНА!</b>\n"
                             f"📦 <b>/digest</b> → <b>ТВОИ ИНТЕРЕСЫ</b>!\n"
                             "📊 <b>/profile</b> → твой прогресс!",
                             parse_mode='HTML')

        except Exception as e:
            logger.error(f"❌ Рассылка {user_id}: {e}")
        finally:
            time.sleep(0.1)

    # ПАРАЛЛЕЛЬНАЯ РАССЫЛКА
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(send_to_user, subscribers)

    logger.info("✅ Утренняя рассылка завершена!")
