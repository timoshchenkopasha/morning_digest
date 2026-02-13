from telebot import types
from config import bot
from parsers.api import *
from database.db import *
from datetime import datetime
import threading


recent_users = set()

@bot.message_handler(commands=['digest'])
def send_news_digest(message: types.Message) -> None:
    """Обработчик команды новостей. Определяем наличие нужной пачки для пользователя в бд,
    если есть - оправляем пользоветелю, если нет - делаем запрос к апи и потом оправляем пользоветелю."""

    user_id = message.from_user.id
    if user_id in recent_users:
        bot.send_message(message.chat.id, "⏳ Подождите 3 секунды...")
        return
    recent_users.add(user_id)

    today = datetime.now().strftime('%Y-%m-%d')
    next_pack = get_user_progress(user_id) + 1
    if pack_exists(today, next_pack):
        news_pack = get_news_pack(today, next_pack)
        print(f"📦 [{user_id}] pack_{next_pack} из кэша")
    else:
        news_pack = news_api(5)
        save_news_pack(today, next_pack, news_pack)
        print('использована новая')

    if news_pack:
        user_name = message.from_user.username or "User"
        set_user_progress(user_id, user_name, next_pack)
        for i, news in enumerate(news_pack, 1):
            title = news['title'][:100]
            caption = f'{i}. <b>{title}</b>\n\n🔗 {news["url"]}'
            if 'image_url' in news and news['image_url']:
                try:
                    bot.send_photo(
                        chat_id=user_id,
                        photo=news['image_url'],
                        caption=caption,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f'❌Ошибка в отправке фотографии: {e}')
                    bot.send_message(user_id, caption, parse_mode='HTML')
            else:
                bot.send_message(user_id, caption, parse_mode='HTML')

        bot.send_message(user_id, "<b>➕ Остальные новости:</b> /digest", parse_mode='HTML')

    threading.Timer(3.0, lambda uid=user_id: recent_users.discard(uid)).start()



