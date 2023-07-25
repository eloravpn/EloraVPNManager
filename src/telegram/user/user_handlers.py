import random

import qrcode as qrcode
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
    bot.reply_to(message,
                 messages.USAGE_HELP_MESSAGE, reply_markup=BotUserKeyboard.help_links(),
                 parse_mode='html'
                 )


@bot.message_handler(regexp=captions.PRICE_LIST)
def price_list(message):
    bot.reply_to(message,
                 messages.PRICE_LIST,
                 parse_mode='html'
                 )


@bot.message_handler(regexp=captions.SUPPORT)
def support(message):
    telegram_user = message.from_user

    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.reply_to(message,
                 text=messages.WELCOME_MESSAGE.format(telegram_user.full_name, config.TELEGRAM_ADMIN_USER_NAME),
                 parse_mode='markdown'
                 )


@bot.message_handler(regexp=captions.MY_SERVICES)
def my_services(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = user.accounts

    if not my_accounts:
        bot.reply_to(message, messages.NO_ACCOUNT_MESSAGE)
    else:
        bot.reply_to(message, messages.ACCOUNT_LIST_MESSAGE,
                     reply_markup=BotUserKeyboard.my_accounts(accounts=my_accounts),
                     parse_mode='markdown'
                     )


@bot.message_handler(regexp=captions.BUY_NEW_SERVICE)
def buy_service(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    available_services = config.AVAILABLE_SERVICES

    if not available_services:
        bot.reply_to(message, messages.BUY_NEW_SERVICE_HELP)
    else:
        bot.reply_to(message, messages.BUY_NEW_SERVICE_HELP,
                     reply_markup=BotUserKeyboard.available_services(available_services),
                     parse_mode='html',
                     disable_web_page_preview=True
                     )


@bot.callback_query_handler(func=lambda call: call.data.startswith('main_menu:'))
def main_menu(call: types.CallbackQuery):
    telegram_user = call.from_user

    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.send_message(chat_id=call.from_user.id,
                     text=messages.WELCOME_MESSAGE.format(telegram_user.full_name, config.TELEGRAM_ADMIN_USER_NAME),
                     disable_web_page_preview=True, reply_markup=BotUserKeyboard.main_menu(), parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('online_payment:'))
def buy_service_step_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    bot.answer_callback_query(
        callback_query_id=call.id, show_alert=True, text=messages.ONLINE_PAYMENT_IS_DISABLED
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_service_step_1:'))
def buy_service_step_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    month = call.data.split(':')[1]
    name = call.data.split(':')[2]
    traffic = call.data.split(':')[3]
    price = call.data.split(':')[4]

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_CONFIRMATION.format(month, traffic, price),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_1(call.data),
        parse_mode='html'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_service_step_2:'))
def account_qrcode(call: types.CallbackQuery):
    telegram_user = call.from_user

    order_id = random.randint(10000, 90000)

    month = call.data.split(':')[1]
    name = call.data.split(':')[2]
    traffic = call.data.split(':')[3]
    price = call.data.split(':')[4]

    bot.send_message(
        text=messages.NEW_ORDER_ADMIN_ALERT.format(order_id, telegram_user.id, telegram_user.full_name,
                                                   month, traffic, price),
        chat_id=config.TELEGRAM_ADMIN_ID,
        # reply_markup=BotUserKeyboard.my_account(account_id),
        parse_mode='html'
    )

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_FINAL.format(order_id, config.TELEGRAM_ADMIN_USER_NAME),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_2(data=call.data),
        parse_mode='html'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('qrcode:'))
def account_qrcode(call: types.CallbackQuery):
    telegram_user = call.from_user
    account_id = call.data.split(':')[1]
    account = utils.get_account(account_id)

    file_name = "./pyqrcode/" + account_id + ".png"

    img = qrcode.make("{}/{}".format(config.SUBSCRIPTION_BASE_URL, account.uuid))
    type(img)  # qrcode.image.pil.PilImage
    img.save(file_name)

    bot.send_chat_action(call.from_user.id, 'upload_document')
    bot.send_photo(caption=captions.ACCOUNT_LIST_ITEM.format(utils.get_readable_size_short(account.data_limit),
                                                             account.id,
                                                             utils.get_jalali_date(account.expired_at.timestamp()),
                                                             captions.ENABLE if account.enable else captions.DISABLE),
                   chat_id=call.from_user.id, photo=open(file_name, 'rb'))


@bot.callback_query_handler(func=lambda call: call.data.startswith('account_detail:'))
def account_detail(call: types.CallbackQuery):
    telegram_user = call.from_user

    account_id = call.data.split(':')[1]

    account = utils.get_account(account_id)

    user = utils.add_or_get_user(telegram_user=telegram_user)

    percent_traffic_usage = round((account.used_traffic / account.data_limit) * 100,
                                  2) if account.data_limit > 0 else "Unlimited"
    bot.send_message(
        text=messages.MY_ACCOUNT_MESSAGE.format(captions.ENABLE if account.enable else captions.DISABLE,
                                                account.id, utils.get_readable_size(account.used_traffic),
                                                utils.get_readable_size(account.data_limit),
                                                percent_traffic_usage
                                                , utils.get_jalali_date(account.expired_at.timestamp()),
                                                config.SUBSCRIPTION_BASE_URL, account.uuid),
        chat_id=telegram_user.id,
        reply_markup=BotUserKeyboard.my_account(account_id),
        parse_mode='html'
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
