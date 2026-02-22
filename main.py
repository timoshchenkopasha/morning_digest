"""MorningDigest Bot — Утренний дайджест новостей"""

from config import bot
from database.db import *
import handlers
from utils import *
from parsers import *

if __name__ == "__main__":
    try:
        print("🤖 MorningDigest бот запускается...")
        print("📱 Готов к работе 24/7!")

        init_db()
        print("✅ База данных готова")

        set_bot_commands(bot)
        print("✅ Команды бота установлены")

        scheduler = start_scheduler()
        print("🕐 Планировщик запущен: 07:00 рассылка + 00:00 reset!")

        print("🚀 Бот полностью готов!")
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=20
        )

    except KeyboardInterrupt:
        print("⏹️ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print("🛑 Завершение работы...")


# git add .
# git commit -m "fix: news_api, digest_handler"
# git push origin main

