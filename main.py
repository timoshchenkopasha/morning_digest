"""MorningDigest Bot — Утренний дайджест новостей"""

from config import bot
from database.db import *
import handlers
from utils import *
from parsers import *


if __name__ == "__main__":
    print("🤖 MorningDigest бот запущен!")
    init_db()
    set_bot_commands(bot)
    scheduler = start_scheduler()
    bot.infinity_polling(none_stop=True, interval=1, timeout=20)







