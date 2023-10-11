import datetime
import random

import qrcode as qrcode
from telebot import types, custom_filters
from telebot.apihelper import ApiTelegramException

from src import logger, config
from src.telegram import bot, utils
from src.telegram.user import captions, messages
from src.telegram.user.keyboard import BotUserKeyboard


class IsSubscribedUser(custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = "is_subscribed_user"

    @staticmethod
    def check(message: types.Message):
        try:
            telegram_user = message.from_user
            utils.add_or_get_user(telegram_user=telegram_user)

            if not config.TELEGRAM_CHANNEL:
                return True
            else:
                result = bot.get_chat_member(
                    config.TELEGRAM_CHANNEL, user_id=message.from_user.id
                )
                if result.status not in ["administrator", "creator", "member"]:
                    bot.send_message(
                        chat_id=message.from_user.id,
                        text=messages.PLEASE_SUBSCRIBE_MESSAGE,
                        disable_web_page_preview=False,
                        reply_markup=BotUserKeyboard.channel_menu(),
                        parse_mode="markdown",
                    )
                    return False
                else:
                    return True
        except Exception as error:
            logger.error(error)

        return False


bot.add_custom_filter(IsSubscribedUser())


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"], is_subscribed_user=True)
def send_welcome(message: types.Message):
    bot.send_message(
        chat_id=message.from_user.id,
        text=messages.WELCOME_MESSAGE.format(config.TELEGRAM_ADMIN_USER_NAME),
        disable_web_page_preview=True,
        reply_markup=BotUserKeyboard.main_menu(),
        parse_mode="markdown",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(regexp=captions.HELP, is_subscribed_user=True)
def help_command(message):
    bot.reply_to(
        message,
        messages.USAGE_HELP_MESSAGE,
        reply_markup=BotUserKeyboard.help_links(),
        parse_mode="html",
    )


@bot.message_handler(regexp=captions.PRICE_LIST, is_subscribed_user=True)
def price_list(message):
    bot.reply_to(message, messages.PRICE_LIST, parse_mode="html")


@bot.message_handler(regexp=captions.SUPPORT, is_subscribed_user=True)
def support(message):
    bot.reply_to(
        message,
        text=messages.WELCOME_MESSAGE.format(config.TELEGRAM_ADMIN_USER_NAME),
        parse_mode="markdown",
    )


@bot.message_handler(regexp=captions.MY_SERVICES, is_subscribed_user=True)
def my_services(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = user.accounts

    if not my_accounts:
        bot.reply_to(message, messages.NO_ACCOUNT_MESSAGE)
    else:
        bot.reply_to(
            message,
            messages.ACCOUNT_LIST_MESSAGE,
            reply_markup=BotUserKeyboard.my_accounts(accounts=my_accounts),
            parse_mode="markdown",
        )


@bot.message_handler(regexp=captions.GET_TEST_SERVICE, is_subscribed_user=True)
def get_test_service(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    test_account = utils.get_last_test_account(user_id=user.id)

    if test_account:
        created_at = test_account.created_at

        logger.debug(f"Account created at {created_at}")

        first_valid_date = datetime.datetime.utcnow() - datetime.timedelta(
            days=config.TEST_ACCOUNT_LIMIT_INTERVAL_DAYS
        )

        allow_to_get_new_account = created_at < first_valid_date
    else:
        allow_to_get_new_account = True

    if allow_to_get_new_account:
        utils.add_test_account(user_id=user.id)

        bot.reply_to(
            message,
            messages.GET_TEST_SERVICE_SUCCESS.format(
                admin_id=config.TELEGRAM_ADMIN_USER_NAME
            ),
            # reply_markup="Test Service",
            parse_mode="html",
            disable_web_page_preview=True,
        )

        utils.send_message_to_admin(
            messages.GET_TEST_SERVICE_ADMIN_ALERT.format(
                chat_id=telegram_user.id, full_name=telegram_user.full_name
            ),
            disable_notification=True,
        )

    else:
        bot.reply_to(
            message,
            messages.GET_TEST_SERVICE_NOT_ALLOWED.format(
                day=config.TEST_ACCOUNT_LIMIT_INTERVAL_DAYS,
                admin_id=config.TELEGRAM_ADMIN_USER_NAME,
            ),
            # reply_markup="Test Service",
            parse_mode="html",
            disable_web_page_preview=True,
        )


@bot.message_handler(regexp=captions.BUY_NEW_SERVICE, is_subscribed_user=True)
def buy_service(message):
    available_services = config.AVAILABLE_SERVICES

    if not available_services:
        bot.reply_to(message, messages.BUY_NEW_SERVICE_HELP)
    else:
        bot.reply_to(
            message,
            messages.BUY_NEW_SERVICE_HELP,
            reply_markup=BotUserKeyboard.available_services(available_services),
            parse_mode="html",
            disable_web_page_preview=True,
        )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("main_menu:"), is_subscribed_user=True
)
def main_menu(call: types.CallbackQuery):
    bot.send_message(
        chat_id=call.from_user.id,
        text=messages.WELCOME_MESSAGE.format(config.TELEGRAM_ADMIN_USER_NAME),
        disable_web_page_preview=True,
        reply_markup=BotUserKeyboard.main_menu(),
        parse_mode="markdown",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("online_payment:"), is_subscribed_user=True
)
def buy_service_step_1(call: types.CallbackQuery):
    bot.answer_callback_query(
        callback_query_id=call.id,
        show_alert=True,
        text=messages.ONLINE_PAYMENT_IS_DISABLED,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_1:"),
    is_subscribed_user=True,
)
def buy_service_step_1(call: types.CallbackQuery):
    month = call.data.split(":")[1]
    name = call.data.split(":")[2]
    traffic = call.data.split(":")[3]
    price = call.data.split(":")[4]

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_CONFIRMATION.format(month, traffic, price),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_1(call.data),
        parse_mode="html",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_2:"),
    is_subscribed_user=True,
)
def account_qrcode(call: types.CallbackQuery):
    telegram_user = call.from_user

    order_id = random.randint(10000, 90000)

    month = call.data.split(":")[1]
    name = call.data.split(":")[2]
    traffic = call.data.split(":")[3]
    price = call.data.split(":")[4]

    bot.send_message(
        text=messages.NEW_ORDER_ADMIN_ALERT.format(
            order_id,
            telegram_user.id,
            telegram_user.id,
            telegram_user.full_name,
            month,
            traffic,
            price,
        ),
        chat_id=config.TELEGRAM_ADMIN_ID,
        parse_mode="html",
    )

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_FINAL.format(
            order_id, config.TELEGRAM_ADMIN_USER_NAME
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_2(data=call.data),
        parse_mode="html",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("qrcode:"), is_subscribed_user=True
)
def account_qrcode(call: types.CallbackQuery):
    account_id = call.data.split(":")[1]
    account = utils.get_account(account_id)

    file_name = "./pyqrcode/" + account_id + ".png"

    img = qrcode.make("{}/{}".format(config.SUBSCRIPTION_BASE_URL, account.uuid))
    type(img)  # qrcode.image.pil.PilImage
    img.save(file_name)

    expired_at = (
        "Unlimited"
        if not account.expired_at
        else utils.get_jalali_date(account.expired_at.timestamp())
    )

    bot.send_chat_action(call.from_user.id, "upload_document")
    bot.send_photo(
        caption=captions.ACCOUNT_LIST_ITEM.format(
            utils.get_readable_size_short(account.data_limit),
            expired_at,
            captions.ENABLE if account.enable else captions.DISABLE,
        ),
        chat_id=call.from_user.id,
        photo=open(file_name, "rb"),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("account_detail:"), is_subscribed_user=True
)
def account_detail(call: types.CallbackQuery):
    telegram_user = call.from_user

    account_id = call.data.split(":")[1]

    account = utils.get_account(account_id)

    percent_traffic_usage = (
        round((account.used_traffic / account.data_limit) * 100, 2)
        if account.data_limit > 0
        else "Unlimited"
    )
    expired_at = (
        "Unlimited"
        if not account.expired_at
        else utils.get_jalali_date(account.expired_at.timestamp())
    )

    try:
        bot.edit_message_text(
            message_id=call.message.message_id,
            text=messages.MY_ACCOUNT_MESSAGE.format(
                captions.ENABLE if account.enable else captions.DISABLE,
                account.email,
                utils.get_readable_size(account.used_traffic),
                utils.get_readable_size(account.data_limit),
                percent_traffic_usage,
                expired_at,
                config.SUBSCRIPTION_BASE_URL,
                account.uuid,
            ),
            chat_id=telegram_user.id,
            reply_markup=BotUserKeyboard.my_account(account_id),
            parse_mode="html",
        )
    except ApiTelegramException as error:
        logger.warn(error)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data == "user_info", is_subscribed_user=True
)
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info(f"Telegram user {telegram_user.full_name} Call {call.data}")

    bot.edit_message_text(
        call.data,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=BotUserKeyboard.main_menu(),
    )
