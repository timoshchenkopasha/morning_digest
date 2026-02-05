from telebot.types import BotCommand
from config import MENU_COMMANDS


def set_bot_commands(bot):
    bot.set_my_commands([BotCommand(*command) for command in MENU_COMMANDS])