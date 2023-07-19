import importlib.util
from os.path import dirname
from threading import Thread
from src.config import TELEGRAM_API_TOKEN, TELEGRAM_PROXY_URL
from src import app
from telebot import TeleBot, apihelper

bot = None


if TELEGRAM_API_TOKEN:
    apihelper.proxy = {'http': TELEGRAM_PROXY_URL, 'https': TELEGRAM_PROXY_URL}
    bot = TeleBot(TELEGRAM_API_TOKEN)
#
# handler_names = ["admin", "report", "user"]

@app.on_event("startup")
def start_bot():
    print("Start Bot")

    # Handle '/start' and '/help'
    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        bot.reply_to(message, """\
    Hi there, I am EchoBot.
    I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
    """)

    # Handle all other messages with content_type 'text' (content_types defaults to ['text'])
    @bot.message_handler(func=lambda message: True)
    def echo_message(message):
        bot.reply_to(message, message.text)

    bot.infinity_polling()
# if bot:
#     handler_dir = dirname(__file__) + "/handlers/"
#     for name in handler_names:
#         spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
#         spec.loader.exec_module(importlib.util.module_from_spec(spec))
#
#     from app.telegram import utils # setup custom handlers
#     utils.setup()
#
#     thread = Thread(target=bot.infinity_polling, daemon=True)
#     thread.start()


# from .handlers.report import (  # noqa
#     report,
#     report_new_user,
#     report_user_modification,
#     report_user_deletion,
#     report_status_change
# )
#
# __all__ = [
#     "bot",
#     "report",
#     "report_new_user",
#     "report_user_modification",
#     "report_user_deletion",
#     "report_status_change"
# ]
