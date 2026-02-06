Папка data (скрыта от внешнего репозитория - gitlab)
содержит - файлы б.д.:
1. subscribers.db - данные о пользователях


Пакет database
содержит:
1. базовый файл __init__.py
2. файл db.py, в нем содержится функция первого и единственного создания таблицы в subscribers.db
3. файл users.py, содержатся базовые функции для работы с базой данных subscribers.db.
такие как: add_user(), get_subscribers(), unsubscribe_user(), is_subscribed()


Пакет handlers
содержит:
1. базовый файл __init__.py
2. файл default_handlers в нем обработчики комманд: start_handler(), subscribe_handler(), 
unsubscribe_handler(), status_handler() - в этих функциях-обработчиках 
- вызываются базовые функции для работы с базой данных subscribers.db.


Пакет utils
содержит:
1. базовый файл __init__.py
2. файл set_bot_commands - устанавливает нужные команды внутри меню приложения telegram# test
