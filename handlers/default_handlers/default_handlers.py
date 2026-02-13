import asyncio
from telebot.types import Message
from config import bot
from database import *


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "🌅 *MorningDigest*\n\n"
        "📰 /digest — 5 свежих новостей\n"
        "📬 Рассылка каждое утро в 8:00",
        parse_mode='Markdown')
