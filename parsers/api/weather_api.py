import os
from typing import Dict

import requests
import json
from dotenv import load_dotenv
import logging


load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
logger = logging.getLogger(__name__)

from functools import lru_cache

@lru_cache(maxsize=128)
def validate_city(city: str) -> bool:
    """Проверка города на наличие в openweatherapi"""

    return bool(get_daily_forecast(city))


def get_daily_forecast(city: str = 'Минск') -> Dict:
    """Запрос к openweatherapi, получение информации о погоде и её парсинг (работа с информаций)"""

    if not OPENWEATHER_API_KEY:
        logger.error('❌ OPENWEATHER_API_KEY не найден в .env')
        return {}

    try:
        url = 'https://api.openweathermap.org/data/2.5/forecast'
        response = requests.get(f'{url}?q={city}&appid={OPENWEATHER_API_KEY}', timeout=10)
        if response.status_code != 200:
            raise ValueError('Ошибка в api')
        weather_data: Dict = response.json()['list'][:8]

        temps_day = [t['main']['temp'] - 273.15 for t in weather_data[2:6]]
        temps_night = [t['main']['temp'] - 273.15 for t in weather_data[6:8] + weather_data[0:2]]

        weather_info = {
            'city': city,
            'day_temp': f"от {int(min(temps_day))} до {int(max(temps_day))}",
            'night_temp': f"от {int(min(temps_night))} до {int(max(temps_night))}",
            'day_desc': weather_data[4]['weather'][0]['main'].split()[0].capitalize(),  # "пасмурно"
            'humidity': weather_data[0]['main']['humidity'],
            'wind_speed': int(weather_data[0]['wind']['speed'])
        }

        return weather_info
    except Exception as e:
        logger.error(f'❌ OpenWeatherAPI ({city}): {e}')
        return {}
