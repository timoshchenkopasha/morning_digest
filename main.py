"""MorningDigest Bot — Утренний дайджест новостей !"""

import logging
import sys

from config import bot
from database.db import *
import handlers
from utils.sheduler import *
from utils import *
from parsers import *

# ГЛОБАЛЬНАЯ НАСТРОЙКА ЛОГОВ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # ✅ КОНСОЛЬ
        logging.FileHandler('bot.log', mode='a')  # ✅ ФАЙЛ
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("🤖 MorningDigest бот запускается...")
        logger.info("📱 Готов к работе 24/7!")

        init_db()
        logger.info("✅ База данных готова")

        set_bot_commands(bot)
        logger.info("✅ Команды бота установлены")

        scheduler = start_scheduler()
        schedule_all_users()
        logger.info("🕐 Планировщик запущен: 07:00 рассылка + 00:00 reset!")

        logger.info("🚀 Бот полностью готов!")
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=20
        )

    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка бота: {e}", exc_info=True)
    finally:
        logger.info("🛑 Завершение работы...")



# git add .
# git commit -m "fix: all"
# git push origin main

