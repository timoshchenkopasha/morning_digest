import telebot
from telebot.types import Message

from config import bot


@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    """Показывает все доступные команды бота"""
    help_text = """<b>🚀 MorningDigest — ТВОË НАЧАЛО ДНЯ!</b>

🎮 <b>КАК ЭТО РАБОТАЕТ? (2 минуты → ПРОДУКТИВНЫЙ ДЕНЬ)</b>

<b>🔧 НАСТРОЙКА (выполни по порядку):</b>
1️⃣ <code>/start</code> → <b>🏙️ Город</b> ☀️ персональная погода
2️⃣ <code>/interests</code> → <b>📰 Интересы:</b> технологии/спорт/ИИ
3️⃣ <code>/time</code> → <b>⏰ Время:</b> 5:00-10:00 (авто-рассылка)
4️⃣ <code>/digest</code> → <b>🔥 АКТУАЛЬНЫЕ НОВОСТИ!</b>

<b>📱 НОВОСТИ:</b>
• <code>/digest</code> → <b>5 новостей ПО ТВОИМ ИНТЕРЕСАМ</b> (кэш/свежее)
• <b>ТВОЕ ВРЕМЯ (5-10:00)</b> → авто-рассылка + погода

<b>🏆 ИГРА = МОТИВАЦИЯ:</b>
📦 <b>1 пачка</b> → 🌱 <b>Читатель</b>
📦 <b>2 пачки</b> → 📈 <b>Активный</b>
📦 <b>3+ пачки</b> → 🌟 <b>Профи дня</b>!
🔥 <b>Серия дней</b> = 🏅 рекорд!

<b>📊 КОМАНДЫ:</b>
<code>/start</code> — 🏙️ добавить город + погоду
<code>/interests</code> — 📰 выбрать интересные темы (ИИ/спорт/политика)
<code>/time</code> — ⏰ выбрать время утренней рассылки
<code>/digest</code> — 📰 <b>новости по ТВОИМ интересам!</b>
<code>/profile</code> — 📊 твой профиль 🏆
<code>/help</code> — ❓ помощь

<i>💥 <b>НАЧНИ:</b> /start → город → /interests → /time → /digest 🚀</i>"""

    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='HTML'
    )



