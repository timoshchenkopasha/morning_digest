_city_country_cache = {}  # Глобальный кэш


def get_country_by_city(city: str) -> str:
    """Кэш популярных городов + fallback"""

    if city in _city_country_cache:
        return _city_country_cache[city]

    city_lower = city.lower()
    popular_cities = {
        # ТВОЙ КОД БЕЗ ИЗМЕНЕНИЙ!
        'минск': 'by', 'гродно': 'by', 'брест': 'by', 'витебск': 'by', 'гомель': 'by',
        'могилев': 'by', 'бобруйск': 'by', 'барановичи': 'by', 'полоцк': 'by', 'орша': 'by',
        'москва': 'ru', 'санкт-петербург': 'ru', 'питер': 'ru', 'спб': 'ru', 'новосибирск': 'ru',
        'екатеринбург': 'ru', 'казань': 'ru', 'нижний новгород': 'ru', 'челябинск': 'ru', 'омск': 'ru',
        'самара': 'ru', 'ростов-на-дону': 'ru', 'уфа': 'ru', 'красноярск': 'ru', 'воронеж': 'ru',
        'киев': 'ua', 'харьков': 'ua', 'одесса': 'ua', 'днепр': 'ua', 'львов': 'ua'
    }

    result = popular_cities.get(city_lower, 'ru')
    _city_country_cache[city] = result
    return result