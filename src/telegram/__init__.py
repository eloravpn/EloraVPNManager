import glob
import importlib.util
from os.path import basename, dirname, join
from threading import Thread

from telebot import TeleBot, apihelper

from src import app
from src.logger import logger

from src.config import (
    TELEGRAM_API_TOKEN,
    TELEGRAM_PROXY_URL,
    TELEGRAM_PAYMENT_API_TOKEN,
)

bot = None
payment_bot = None

if TELEGRAM_API_TOKEN or TELEGRAM_PAYMENT_API_TOKEN:
    apihelper.proxy = {"http": TELEGRAM_PROXY_URL, "https": TELEGRAM_PROXY_URL}

if TELEGRAM_API_TOKEN:
    bot = TeleBot(TELEGRAM_API_TOKEN)

    @app.on_event("startup")
    def start_bot():
        logger.info("Start telegram bot")
        handler = glob.glob(join(dirname(__file__), "**/**.py"), recursive=True)
        for file in handler:
            name = basename(file).replace(".py", "")

            if name.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(name, file)
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

        thread = Thread(target=bot.infinity_polling, daemon=True)
        thread.start()

else:
    logger.warn("Telegram Bot not set!")

if TELEGRAM_PAYMENT_API_TOKEN:
    payment_bot = TeleBot(TELEGRAM_PAYMENT_API_TOKEN)

    @app.on_event("startup")
    def start_bot():
        logger.info("Start payment telegram bot")

        thread = Thread(target=payment_bot.infinity_polling, daemon=True)
        thread.start()

else:
    logger.warn("Telegram Payment Bot not set!")
