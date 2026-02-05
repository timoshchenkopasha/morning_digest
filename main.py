from config import bot
import asyncio
from database import *
import handlers
from utils import *


if __name__ == "__main__":
    set_bot_commands(bot)
    asyncio.run(init_db())
    print("🤖 MorningDigest бот запущен!")
    bot.polling()



