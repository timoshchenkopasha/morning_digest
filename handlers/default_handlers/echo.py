from telebot.types import Message

from config import bot


@bot.message_handler(content_types=['text'])
def echo_handler(message: Message) -> None:
    """Обрабатывает ВСЕ непонятные сообщения + приветствия"""

    text = message.text.lower().strip()

    greetings = ['привет', 'здравствуй', 'добрый день', 'доброе утро',
                 'добрый вечер', 'hi', 'hello', 'hey', ' приветствую']

    if any(greeting in text for greeting in greetings):
        bot.reply_to(message,
                     """<b>🚀 MorningDigest — ТВОË НАЧАЛО ДНЯ! ⚡</b>
 
     <code>/start</code> — выбери город для погоды 🌤️
     <code>/digest</code> — новости прямо сейчас 📰  
     <code>/help</code> — все команды
 
     📅 <b>Каждое утро 7:00:</b> погода + топ новости!""",
                     parse_mode='HTML')
        return

    bot.reply_to(message,
                 """❓ <b>Не понял 😅</b>
 
    <b>🎮 ДОСТУПНЫЕ КОМАНДЫ:</b>
    <code>/start</code> — 🏙️ Выбери город (погода персональная!)
    <code>/digest</code> — 📰 <b>Следующая пачка</b> новостей (кэш/свежее)
    <code>/profile</code> — 📊 <b>Твоя статистика</b> (уровни+серия)
    <code>/help</code> — ❓ Возможности бота""",
                 parse_mode='HTML')
