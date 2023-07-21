from telebot import types

from src import logger, config
from src.telegram import bot, utils
from src.telegram.user import captions, messages
from src.telegram.user.keyboard import BotUserKeyboard


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message: types.Message):
    telegram_user = message.from_user

    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.send_message(chat_id=message.from_user.id,
                     text=messages.WELCOME_MESSAGE.format(telegram_user.full_name, config.TELEGRAM_ADMIN_USER_NAME),
                     disable_web_page_preview=True, reply_markup=BotUserKeyboard.main_menu(), parse_mode='markdown')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(regexp=captions.HELP)
def help_command(message):
    bot.reply_to(message, "HOW CAN I HELP?!", reply_markup=BotUserKeyboard.confirm_action(action='restart'))


@bot.message_handler(regexp=captions.MY_SERVICES)
def help_command(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = user.accounts

    if not my_accounts:
        bot.reply_to(message, "No accounts", reply_markup=BotUserKeyboard.confirm_action(action='restart'))
    else:
        bot.reply_to(message, "accounts", reply_markup=BotUserKeyboard.my_accounts(accounts=my_accounts))





@bot.callback_query_handler(func=lambda call: call.data == 'restart')
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info("Create telegram_user for:" + str(telegram_user))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.edit_message_text(
        "Create User successfully!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=BotUserKeyboard.main_menu()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'user_info')
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info(f"Telegram user {telegram_user.full_name} Call {call.data}")

    bot.edit_message_text(
        call.data,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=BotUserKeyboard.main_menu()
    )
