import os

import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
MENU_COMMANDS = (
    ('start', 'Запустить бота'),
    ('digest', 'Получить актуальные новости'),
    ('profile', 'Посмотреть свою статистику'),
    ('help', 'Узнать возможности бота')
)




