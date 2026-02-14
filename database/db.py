import json
from peewee import SqliteDatabase, Model, CharField, IntegerField, DateTimeField, ForeignKeyField, TextField
import os
from datetime import datetime


os.makedirs(os.path.join('..', 'data'), exist_ok=True)
db_path = os.path.join('data', 'subscribers.db')
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    """Таблица пользователей в бд"""

    id = IntegerField(primary_key=True)
    user_id = IntegerField(unique=True)
    user_name = CharField(max_length=100, null=True)
    subscribed = IntegerField(default=0)
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
    last_pack = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)


class NewsPacks(BaseModel):
    """Пачки новостей (кэш для /more)"""

    day = CharField(max_length=10)
    pack_num = IntegerField()
    news_json = TextField()
    updated_at = DateTimeField(default=datetime.now)


def get_user_progress(user_id: int) -> int:
    """Возвращает прогресс пользователя"""

    today = datetime.now().strftime('%Y-%m-%d')
    try:
        progress = (
            UsersNewsProgress.select()
            .join(Users, on=(UsersNewsProgress.user == Users.id))
            .where(
                (Users.user_id == user_id) &
                (UsersNewsProgress.day == today)
            )
            .order_by(UsersNewsProgress.updated_at.desc())
            .first()
        )
        return progress.last_pack if progress else 0
    except Exception as error:
        print(error)
        return 0

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

        print(f"Прогресс пользователя: ✅ [{last_pack}] {user_name} ({user_id})") #для отладки
    except Exception as error:
        print(f'❌ Ошибка сохранения прогресса пользователя {user_id}: {error}')

def reset_user_progress(user_id: int):
    """Сбрасывает прогресс пользователя за сегодня"""

    today = datetime.now().strftime('%Y-%m-%d')
    try:
        # 1. Находим объект пользователя по user_id
        user = Users.get(Users.user_id == user_id)

        # 2. Удаляем ВСЕ записи прогресса этого пользователя за сегодня
        deleted = UsersNewsProgress.delete().where(
            (UsersNewsProgress.user == user.id) &  # Только поле user (ForeignKey)
            (UsersNewsProgress.day == today)
        ).execute()

        print(f"🗑️ Сброс {user_id}: удалено {deleted} записей")
    except Users.DoesNotExist:
        print(f"ℹ️ Пользователь {user_id} не найден")
    except Exception as error:
        print(f'❌ Ошибка сброса: {error}')

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


def init_db():
    db.connect()
    db.create_tables([Users, UsersNewsProgress, NewsPacks], safe=True)
    db.close()



