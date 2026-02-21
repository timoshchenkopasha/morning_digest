"""MorningDigest Bot — Утренний дайджест новостей"""

import signal
import sys

from config import bot
from database.db import *
import handlers
from utils import *
from parsers import *

scheduler = None


def signal_handler(sig, frame):
    print("🛑 Graceful shutdown...")
    if scheduler:
        scheduler.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    print("🤖 MorningDigest бот запущен!")

    init_db()
    set_bot_commands(bot)
    scheduler = start_scheduler()

    # Регистрируем обработчики СЛЕДУЮЩИМИ
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        bot.infinity_polling(none_stop=True, interval=1, timeout=20)
    except KeyboardInterrupt:
        print("🛑 KeyboardInterrupt...")
        if scheduler:
            scheduler.shutdown()
    finally:
        if scheduler:
            scheduler.shutdown()
            print("✅ Бот остановлен корректно!")





# git add .
# git commit -m "fix: баг с погодой"
# git push