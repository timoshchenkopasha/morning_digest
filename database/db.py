import aiosqlite
import os
from pathlib import Path


# Путь к файлу базы данных
DB_PATH = Path(os.path.join(os.path.dirname(__file__), "../data/subscribers.db"))

async def init_db():
    """Асинхронная функция. Асинхронно подключается к нашей базе данных
    и создаёт таблицу users ПРИ ПЕРВОМ ЗАПУСКЕ. Вызывается 1 раз в main.py"""

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""                                    
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            subscribed BOOLEAN DEFAULT 0,
            timezone TEXT DEFAULT 'UTC+3',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        print(f"✅ База данных инициализирована: {DB_PATH}")


# async def - эта функция работает ФОНОМ, не блокирует бота
# await - 'подожди результат этой фоновой работы (ПОДОЖДИ пока база создаст таблицу)
# Важно! После добавления, изменения или удаления записей необходимо внести изменения с помощью метода commit у объекта db,
# иначе не сохранится