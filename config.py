import os
import telebot
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
MENU_COMMANDS = (
    ('start', "Запустить бота"),
    ('subscribe', "Подписаться"),
    ('unsubscribe', "Отписаться"),
    ('status', "Проверить подписку")
)




