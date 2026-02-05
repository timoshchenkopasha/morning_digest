import aiosqlite
from pathlib import Path
import os
from typing import List


DB_PATH = Path(os.path.join(os.path.dirname(__file__), '..', 'data', "subscribers.db"))

async def add_user(user_id: int) -> None:
    """Добавляет нового пользователя (подписывает)"""
    async with aiosqlite.connect(DB_PATH) as db:
        # ✅ UPSERT: INSERT или UPDATE
        await db.execute('''
            INSERT INTO users (user_id, subscribed) 
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET subscribed = 1
        ''', (user_id,))
        await db.commit()

async def get_subscribers() -> List[int]:
    """Возвращает ВСЕХ подписанных пользователей [123456, 789012]"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users WHERE subscribed = 1') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def unsubscribe_user(user_id: int) -> None:
    """Отписывает пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET subscribed = 0 WHERE user_id = ?', (user_id,))
        await db.commit()

async def is_subscribed(user_id: int) -> bool:
    """Проверяет подписан ли пользователь"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT subscribed FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] == 1 if result else False


# await НУЖЕН ТОЛЬКО перед асинхронными операциями!
# await = 'ПОДОЖДИ результат медленной фоновой работы'