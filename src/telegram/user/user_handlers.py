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
                 "HOW CAN I HELP?!", reply_markup=BotUserKeyboard.help_links())


@bot.message_handler(regexp=captions.MY_SERVICES)
def my_services(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = user.accounts

    if not my_accounts:
        bot.reply_to(message, "No accounts", reply_markup=BotUserKeyboard.confirm_action(action='restart'))
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

    file_name = "pyqrcode/" + account_id + ".png"

    # url = pyqrcode.QRCode("https://sub.rirashop.top/api/sub?uuid=0e05d65d-b742-435e-9b83-23f0fe6f1406")
    # url.png('qrcode.png', scale=15)
    img = qrcode.make("https://sub.rirashop.top/api/sub?uuid=0e05d65d-b742-435e-9b83-23f0fe6f1406")
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

    logger.info("Create telegram_user for:" + str(telegram_user))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.send_message(
        text=messages.MY_ACCOUNT_MESSAGE.format(captions.ENABLE if account.enable else captions.DISABLE,
                                                account.id, utils.get_readable_size(account.used_traffic),
                                                utils.get_readable_size(account.data_limit),
                                                round((account.used_traffic / account.data_limit) * 100, 2)
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
