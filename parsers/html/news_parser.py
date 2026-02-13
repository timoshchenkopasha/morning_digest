import requests
import logging
from typing import List, Dict
from bs4 import BeautifulSoup

#TODO оставил для примера


logger = logging.getLogger(__name__)

def parse_ria_news(top_n: int = 3) -> List[Dict]:
    """Функция парсинга новостей"""

    try:
        url = "https://ria.ru/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; '
                          'Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        # articles = soup.find_all('a', class_='m-title-link')[:top_n]    #список всех найденных тегов
        # МНОГО ВАРИАНТОВ - найдём ТОП новости!
        selectors = [
            'a[href*="/20"][href*="/"]',  # Ссылки с датой /20260207/news/
            '.main-news a',  # Главные новости
            '.list-item__title a',  # Список новостей
            'h3 a',  # Заголовки h3
            '.article__title a'  # Статьи
        ]

        articles = []
        for selector in selectors:
            articles = soup.select(selector)[:top_n]
            if articles:
                print(f"НАЙДЕН селектор: {selector} → {len(articles)} новостей")
                break

        news = []
        for article in articles:
            title = article.get_text(strip=True)      # Текст внутри <a> 'В Москве снегопад' (без тегов + пробелов)
            link = article.get('href')                # Атрибут href, get('href') - '/20260207/moskva/' или 'https://ria.ru/moskva/'

            if link and not link.startswith('http'):
                link = 'https://ria.ru' + link

            if link and title:
                news.append({
                    'title': title[:100] + '...' if len(title) > 100 else title,
                    'url': link
                })
        logger.info(f"✅ Парсер: {len(news)} новостей")                          # вывод в терминал + в файл логов
        return news
    except Exception as e:
        logger.error(f"❌ Парсер ошибка: {e}")
        return []

