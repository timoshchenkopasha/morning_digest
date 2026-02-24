import os
from typing import List, Dict
import json
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # ✅ ИСПРАВЛЕНО: из .env!
logger = logging.getLogger(__name__)


def news_api(top_n: int = 5, country: str = 'ru') -> List[Dict]:
    """Общие новости (fallback) — https://newsdata.io"""
    return news_api_interests('general', top_n, country)  # ✅ Использует новую функцию


def news_api_interests(interest_str: str = 'general', top_n: int = 5, country: str = 'ru') -> List[Dict]:
    """🆕 Новости по интересам (главная функция!)"""

    if not NEWS_API_KEY:
        logger.error('❌ NEWS_API_KEY не найден в .env')
        return []

    try:
        url = 'https://newsdata.io/api/1/latest'
        params = {
            'apikey': NEWS_API_KEY,
            'q': interest_str if interest_str != 'general' else '',  # ✅ КЛЮЧЕВОЙ ПАРАМЕТР!
            'country': country,
            'language': 'ru',
            'size': top_n,
            'image': 1,
            'removeduplicate': 1,
            'timezone': 'europe/minsk'
        }

        logger.debug(f"🌐 API запрос: q='{interest_str}', country={country}")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data['status'] != 'success':
            logger.error(f"❌ NewsAPI ({interest_str}): {data.get('message')}")
            return []

        news = []
        for article in data.get('results', [])[:top_n]:
            title = article.get('title', '')[:100]
            news.append({
                'title': title + '...' if len(article.get('title', '')) > 100 else title,
                'url': article.get('link', ''),
                'source': article.get('source_id', 'Unknown'),
                'date': article.get('pubDate', ''),
                'image_url': article.get('image_url', ''),
            })

        logger.info(f'✅ NewsAPI ({interest_str}): {len(news)} новостей')
        return news

    except Exception as e:
        logger.error(f'❌ NewsAPI ({interest_str}): {e}')
        return []

