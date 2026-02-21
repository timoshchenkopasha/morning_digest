import os
from typing import List, Dict
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
logger = logging.getLogger(__name__)


def news_api(top_n: int = 5, country: str = 'ru') -> List[Dict]:
    """Парсинг новостей с NewsAPI.org"""

    if not NEWS_API_KEY:
        logger.error('❌ NEWS_API_KEY не найден в .env')
        return []

    try:
        # 🔥 НОВЫЙ NewsAPI.org endpoint
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'country': country,  # ru, ua, gb, kz
            'apiKey': NEWS_API_KEY,
            'pageSize': top_n,
            'language': 'ru',  # опционально
            'sortBy': 'publishedAt'
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # NewsAPI.org формат ответа
        if data.get('status') != 'ok':
            logger.error(f"❌ NewsAPI: {data.get('message', 'Unknown error')}")
            return []

        news = []
        for article in data.get('articles', [])[:top_n]:
            news.append({
                'title': (article.get('title', '') or 'No title')[:100] + '...'
                if len(article.get('title', '')) > 100 else article.get('title', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'date': article.get('publishedAt', ''),
                'image_url': article.get('urlToImage', ''),
            })

        logger.info(f'✅ NewsAPI.org: {len(news)} новостей ({country})')
        return news

    except Exception as e:
        logger.error(f'❌ NewsAPI.org ошибка: {e}')
        return []




























# import os
# from typing import List, Dict
#
# import json
# import requests
# from dotenv import load_dotenv
# import logging
#
#
#
# load_dotenv()
# NEWS_API_KEY = os.getenv('NEWS_API_KEY')
# logger = logging.getLogger(__name__)
#
#
# def news_api(top_n: int = 5, country: str = 'ru') -> List[Dict]:
#     """Парсинг новостей с api https://newsdata.io"""
#
#     if not NEWS_API_KEY:
#         logger.error('❌ NEWS_API_KEY не найден в .env')
#         return []
#
#     try:
#         url = 'https://newsdata.io/api/1/news'
#         params = {
#             'apikey': NEWS_API_KEY,
#             'country': country,  # ru, ua, by, kz
#             'language': 'ru',
#             'size': top_n
#         }
#
#         response = requests.get(url, params=params, timeout=10)
#         data = response.json()                  # 'преобразовать JSON строку в Python словарь (десериализация)'
#
#         if data['status'] != 'success':
#             logger.error(f"❌ NewsAPI: {data.get('message')}")
#             return []
#
#         # для отладки
#         # with open('news_json.json', 'w', encoding='utf-8') as f:
#         #     json.dump(data, f, ensure_ascii=False, indent=4)
#
#         news = []
#         for article in data.get('results', [])[:top_n]:
#             news.append({
#                 'title': article.get('title', '')[:100] + '...' if len(article.get('title', '')) > 100 else article.get('title', ''),
#                 'url': article.get('link', ''),
#                 'source': article.get('source_id', 'Unknown'),
#                 'date': article.get('pubDate', ''),
#                 'image_url': article.get('image_url', ''),
#             })
#
#         logger.info(f'✅ NewsAPI: {len(news)} новостей ({country})')
#         return news
#     except Exception as e:
#         print(e)
#         logger.error(f'❌ NewsAPI ошибка: {e}')
#         return []
