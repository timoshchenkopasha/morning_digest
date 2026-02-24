import telebot
from telebot.types import Message

from config import bot


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    """Показывает все доступные команды бота"""

    help_text = """<b>🚀 MorningDigest — ТВОЙ УТРЕННИЙ РИТУАЛ! ⚡</b>

    🎮 <b> КАК ЭТО РАБОТАЕТ? (30 секунд → ПРОДУКТИВНЫЙ ДЕНЬ)</b>

    <b>1️⃣ ВЫБЕРИ ГОРОД</b> ☀️
    <code>/start</code> → Минск/Москва/Киев → <b>персональная погода</b>

    <b>2️⃣ ВЫБЕРИ ИНТЕРЕСЫ</b> 📰  
    <code>/interests</code> → технологии/политика/спорт → <b>твои новости</b>

    <b>3️⃣ ПОЛУЧАЙ НОВОСТИ</b> 📈
    • <code>/digest</code> → <b>5 новостей ПО ТВОИМ ИНТЕРЕСАМ</b> + погода
    • <b>07:00 КАЖДЫЙ ДЕНЬ</b> → авто-рассылка новостей + погода

    <b>🏆 ИГРА = МОТИВАЦИЯ!</b>
    📦 <b>1 пачка/день</b> → 🌱 Читатель
    📦 <b>2 пачки</b> → 📈 Активный  
    📦 <b>3+ пачки</b> → 🌟 Профи дня!
    🔥 <b>Серия дней подряд</b> = 🏅 достижения!

    <b>📊 ТВОИ КОМАНДЫ:</b>
    <code>/start</code> — 🏙️ город (погода персональная!)
    <code>/interests</code> — 🏷️ твои темы новостей  
    <code>/digest</code> — 📰 <b>следующая пачка</b> (кэш/свежее)
    <code>/profile</code> — 📊 <b>статистика + серия</b>
    <code>/help</code> — ❓ эта справка

    <i>💥 ПЕРВЫЙ ШАГ: <code>/start</code> → Погнали! 🚀</i>"""

    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='HTML'
    )
