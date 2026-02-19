import os
from typing import List, Dict

import json
import requests
from dotenv import load_dotenv
import logging



load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
logger = logging.getLogger(__name__)


def news_api(top_n: int = 5, country: str = 'ru') -> List[Dict]:
    """Парсинг новостей с api https://newsdata.io"""

    if not NEWS_API_KEY:
        logger.error('❌ NEWS_API_KEY не найден в .env')
        return []

    try:
        url = 'https://newsdata.io/api/1/news'
        params = {
            'apikey': NEWS_API_KEY,
            'country': country,  # ru, ua, by, kz
            'language': 'ru',
            'size': top_n
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()                  # 'преобразовать JSON строку в Python словарь (десериализация)'

        if data['status'] != 'success':
            logger.error(f"❌ NewsAPI: {data.get('message')}")
            return []

        # для отладки
        # with open('news_json.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)

        news = []
        for article in data.get('results', [])[:top_n]:
            news.append({
                'title': article.get('title', '')[:100] + '...' if len(article.get('title', '')) > 100 else article.get('title', ''),
                'url': article.get('link', ''),
                'source': article.get('source_id', 'Unknown'),
                'date': article.get('pubDate', ''),
                'image_url': article.get('image_url', ''),
            })

        logger.info(f'✅ NewsAPI: {len(news)} новостей ({country})')
        return news
    except Exception as e:
        print(e)
        logger.error(f'❌ NewsAPI ошибка: {e}')
        return []
