import asyncio
from telebot.types import Message
from config import bot
from database import *


@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    bot.reply_to(message,
        "🌅 Вас приветствует MorningDigest бот!\n\n"
        "/subscribe — Подписаться на дайджесты\n"
        "/unsubscribe — Отписаться\n"
        "/status — Проверить статус")

@bot.message_handler(commands=['subscribe'])
def subscribe_handler(message: Message):
    asyncio.run(add_user(message.from_user.id))
    bot.reply_to(message, "✅ Ты подписался на утренние дайджесты!")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_handler(message: Message):
    asyncio.run(unsubscribe_user(message.from_user.id))
    bot.reply_to(message, "❌ Ты отписался от дайджестов.")

@bot.message_handler(commands=['status'])
def status_handler(message: Message):
    if asyncio.run(is_subscribed(message.from_user.id)):
        bot.reply_to(message, "✅ Ты подписан на дайджесты!")
    else:
        bot.reply_to(message, "❌ Ты не подписан.\nНапиши /subscribe")