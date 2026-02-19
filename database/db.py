import os
from datetime import datetime, date, timedelta

import json
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField, ForeignKeyField, TextField
from pathlib import Path


# АБСОЛЮТНЫЙ ПУТЬ К data/ из корня проекта!
BASE_DIR = Path(__file__).parent.parent # MorningDigest_bot/
DATA_DIR = BASE_DIR / "data" # MorningDigest_bot/data/
DATA_DIR.mkdir(exist_ok=True)  # Создаем data/

db_path = DATA_DIR / "subscribers.db"
db = SqliteDatabase(db_path)  # ✅ Абсолютный путь!


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    """Таблица пользователей в бд"""

    id = IntegerField(primary_key=True)
    user_id = IntegerField(unique=True)
    user_name = CharField(max_length=100, null=True)
    city = CharField(max_length=100, null=True)
    timezone = CharField(null=True, default='UTC+3')
    created_at = DateTimeField(default=datetime.now)


class UsersNewsProgress(BaseModel):
    """Таблица прогресса просмотра новостей пользователя"""

    user = ForeignKeyField(
        Users,
        backref='news_progress',
        on_delete='CASCADE'
    )
    day = CharField(max_length=10)

    # Дневная система
    last_pack = IntegerField(default=0)         # Пачки за сегодня (и последняя пачка)
    daily_level = IntegerField(default=0)       # Уровень за день
    last_active_date = DateTimeField(null=True) # Последняя активность

    #Серия
    streak_current = IntegerField(default=0)    # Текущая серия
    streak_max = IntegerField(default=0)        # Лучшая серия

    updated_at = DateTimeField(default=datetime.now)


class NewsPacks(BaseModel):
    """Пачки новостей (кэш для /more)"""

    day = CharField(max_length=10)
    pack_num = IntegerField()
    news_json = TextField()
    updated_at = DateTimeField(default=datetime.now)


def set_user_progress(user_id: int, user_name, last_pack: int):
    """Сохраняем или создаем прогресс пользователя"""

    today = datetime.now().strftime('%Y-%m-%d')
    try:
        user, created = Users.get_or_create(
            user_id=user_id,
            defaults={'user_name': user_name}
        )
        progress, created = UsersNewsProgress.get_or_create(
            user=user,
            day=today,
            defaults={'last_pack': last_pack}
        )
        if not created:
            progress.last_pack = last_pack
            progress.updated_at = datetime.now()
            progress.save()

        print(f"Новый пользователь (прогресс/имя/id): ✅ [{progress.last_pack}] {user_name} ({user_id})")
    except Exception as error:
        print(f'❌ Ошибка сохранения прогресса пользователя {user_id}: {error}')

def save_news_pack(day: str, pack_num: int, news_list: list):
    """Сохранаяет пачку в бд"""

    try:
        NewsPacks.get_or_create(                #метод возвращает объект NewsPacks
            day=day,
            pack_num=pack_num,
            defaults={'news_json': json.dumps(news_list)}
        )
        print(f"✅ Сохранена {day} pack_{pack_num}")
    except Exception as e:
        print(f"❌ Ошибка сохранения пачки: {e}")

def get_news_pack(day: str, pack_num: int):
    """Получаем пачку из базы данных"""

    try:
        news_pack = NewsPacks.get_or_none(      #метод возвращает объект NewsPacks или None
            NewsPacks.day==day,
            NewsPacks.pack_num==pack_num
        )
        return json.loads(news_pack.news_json) if news_pack else None
    except Exception as e:
        print(f"❌ Ошибка при получении пачки из базы данных: {e}")
        return None

def pack_exists(day: str, pack_num: int):
    """Проверка пачки в кэше"""

    return NewsPacks.get_or_none(
        NewsPacks.day==day,
        NewsPacks.pack_num==pack_num) is not None

def set_user_city(user_id: int, user_name, city_name: str):
    """Сохраняет город у старого или нового пользователя"""

    try:
        user, created = Users.get_or_create(
            user_id=user_id,
            defaults={         # Только для создания!
                'user_name': user_name,
                'city': city_name,
                'timezone': 'UTC+3',
                'created_at': datetime.now()
            }
        )
        if created:
            print(f"✅ Новый пользователь {user_id} - {city_name}")
        else:
            user.city = city_name
            user.save()
            print(f"✅ Обновлён город {user_id} → {city_name}")

        return True
    except Exception as error:
        print(f"❌ Ошибка сохранения {user_id}: {error}")


"""Функции управления уровнями"""

def reset_daily_progress():
    """Сброс дневного прогресса в 00:00"""

    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # Сбрасываем ТОЛЬКО вчерашние записи
    UsersNewsProgress.update(last_pack=0, daily_level=0).where(
        UsersNewsProgress.day == yesterday_str
    ).execute()

    print(f"✅ Сброшены вчерашние записи последних пачек и дневного левела пользователей: {yesterday_str}")

def calculate_daily_level(packs_today: int) -> tuple:
    """Уровень за день по пачкам"""

    if packs_today >= 3:
        return 3, "🌟 Профи дня"
    elif packs_today >= 2:
        return 2, "📈 Активный"
    elif packs_today >= 1:
        return 1, "🌱 Читатель"
    return 0, "😴 Спит"

def update_streak(user_id: int) -> bool:
    """Возвращает True если серия растет"""
    today_date = date.today()
    today_str = today_date.strftime('%Y-%m-%d')

    user_progress = (UsersNewsProgress
                     .select()
                     .join(Users)
                     .where((Users.user_id == user_id) & (UsersNewsProgress.day == today_str))
                     .order_by(UsersNewsProgress.updated_at.desc())
                     .first()
                     )
    if not user_progress:
        return False

    last_active = user_progress.last_active_date.date() if user_progress.last_active_date else None

    # Проверяем пропуск дня
    if last_active and last_active < (today_date - timedelta(days=1)):
        user_progress.streak_current = 0
        print(f"Серия сброшена у {user_id}")

    # Сегодня активен → +1 к серии (если не был)
    if last_active != today_date:
        user_progress.streak_current += 1
        user_progress.streak_max = max(user_progress.streak_max, user_progress.streak_current)
        print(f"Серия {user_id}: {user_progress.streak_current}")

    user_progress.last_active_date = datetime.now()
    user_progress.updated_at = datetime.now()
    user_progress.save()

    return user_progress.streak_current > 0

def get_user_level(packs_viewed: int) -> tuple:
    """Возвращает (уровень, название, сообщение)"""
    if packs_viewed < 3:
        return 1, "🌱 Новичок", "Первый дайджест! Добро пожаловать! 🌅"
    elif packs_viewed < 6:
        return 2, "🌿 Подросток", "3 пачки! Ты растёшь! 📈"
    elif packs_viewed < 9:
        return 3, "🌳 Дерево", "6 пачек! Стабильный читатель! 💪"
    elif packs_viewed < 12:
        return 4, "🌲 Лес", "9 пачек! Ты в теме! 🔥"
    else:
        return 5, "🌍 MorningMaster", "12+ пачек! Мастер утра! 🏆"

def init_db():
    db.connect()
    db.create_tables([Users, UsersNewsProgress, NewsPacks], safe=True)
    db.close()

