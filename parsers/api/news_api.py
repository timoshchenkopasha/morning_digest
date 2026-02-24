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
    """Общие новости (fallback) — https://newsdata.io"""
    return news_api_interests('general', top_n, country)


def news_api_interests(interest_str: str = 'general', top_n: int = 5, country: str = None, is_morning: bool = False) -> \
List[Dict]:
    """📰 Логика: /digest=все страны | 07:00=только страна"""

    logger.info(f"🔑 interest='{interest_str}' | country={country} | morning={is_morning}")

    if not NEWS_API_KEY:
        logger.error('❌ NEWS_API_KEY не найден')
        return generate_fallback_news(interest_str, top_n)

    try:
        url = 'https://newsdata.io/api/1/latest'
        params = {
            'apikey': NEWS_API_KEY,
            'language': 'ru',
            'timezone': 'europe/minsk',
            'image': 1,
            'size': top_n
        }

        # ✅ НОВЫЕ ПРАВИЛА:
        if is_morning:  # 07:00 рассылка
            params['country'] = country  # ТОЛЬКО страна!
            params['category'] = 'general,politics,business'  # Общие новости
            logger.info("🌅 УТРЕННИЙ РЕЖИМ: только страна + общие категории")
        else:  # /digest днём
            if interest_str == 'general':
                params['category'] = 'politics,science,sports,technology'
            else:
                # ✅ /digest: интересы по всему миру!
                single_interest = interest_str.split('+')[0]  # Первая тема
                params['q'] = single_interest
            logger.info("📱 ДНЕВНОЙ РЕЖИМ: интересы по всему миру")

        logger.info(f"📡 Запрос: {params}")
        response = requests.get(url, params=params, timeout=10)

        logger.info(f"📊 Status: {response.status_code}")
        data = response.json()
        logger.info(f"📊 Результат: {data.get('status')} | {len(data.get('results', []))} новостей")

        if data.get('status') != 'success' or not data.get('results'):
            logger.warning("🔄 API пустой → fallback")
            return generate_fallback_news(interest_str, top_n)

        # Парсинг...
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

        logger.info(f"✅ NewsAPI ({interest_str}): {len(news)} новостей")
        return news

    except Exception as e:
        logger.error(f'❌ NewsAPI Error: {e}')
        return generate_fallback_news(interest_str, top_n)


def generate_fallback_news(interest: str, count: int = 5) -> List[Dict]:
    """🧪 Тестовые новости для отладки"""
    topics = {
        'general': ['Мир', 'Политика', 'Экономика', 'Беларусь'],
        'технологии': ['Apple', 'Google', 'ИИ', 'Гаджеты'],
        'спорт': ['Футбол', 'Хоккей', 'Теннис'],
        'политика': ['Выборы', 'Правительство']
    }

    topic_list = topics.get(interest, topics['general'])
    news = []
    for i in range(count):
        news.append({
            'title': f"📰 {topic_list[i % len(topic_list)]}: Актуальные новости #{i + 1}",
            'url': f"https://news.example.com/{interest}-{i + 1}",
            'source': f"{interest.title()} News",
            'date': "2026-02-24T16:00:00Z",
            'image_url': "",
        })
    logger.info(f"✅ FALLBACK: {count} тестовых новостей ({interest})")
    return news