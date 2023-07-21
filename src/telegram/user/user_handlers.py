from telebot import types

from src import logger
from src.telegram import bot, utils
from src.telegram.user.keyboard import BotUserKeyboard


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
   Hi there, I am EchoBot.
   I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
   """, reply_markup=BotUserKeyboard.main_menu())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


@bot.callback_query_handler(func=lambda call: call.data == 'restart')
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info("Create telegram_user for:" + str(telegram_user))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    print(user.first_name)\
@bot.callback_query_handler(func=lambda call: call.data == 'user_info')
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info("Create telegram_user for:" + str(telegram_user))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    print(user.first_name)

