import datetime
import random

import qrcode as qrcode
from telebot import types, custom_filters
from telebot.apihelper import ApiTelegramException
from telebot.custom_filters import IsReplyFilter
from telebot.types import ForceReply

from src import logger, config
from src.commerce.exc import (
    MaxOpenOrderError,
    MaxPendingOrderError,
    NoEnoughBalanceError,
)
from src.telegram import bot, utils
from src.telegram.user import captions, messages
from src.telegram.user.keyboard import BotUserKeyboard
from src.users.models import User

change_account_name_message_ids = {}


class IsSubscribedUser(custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = "is_subscribed_user"

    @staticmethod
    def check(message: types.Message):
        try:
            telegram_user = message.from_user

            referral_user = None

            if isinstance(message, types.Message) and message.text:
                referral_user = IsSubscribedUser.get_referral_user(
                    message_text=message.text
                )

            user = utils.add_or_get_user(
                telegram_user=telegram_user, referral_user=referral_user
            )

            if not config.TELEGRAM_CHANNEL or not user.force_join_channel:
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

    @staticmethod
    def get_referral_user(message_text) -> User:
        user = None
        try:
            if message_text.startswith("/start"):
                split_message_text = message_text.split(" ")
                if len(split_message_text) == 2:
                    referral_code = message_text.split(" ")[1]
                    logger.info(f"Referral code: {referral_code}")
                    user = utils.get_user(user_id=int(referral_code))
        except Exception as error:
            logger.error(error)
        return user


bot.add_custom_filter(IsSubscribedUser())
bot.add_custom_filter(IsReplyFilter())


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


@bot.message_handler(regexp=captions.MY_PROFILE, is_subscribed_user=True)
def my_profile(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.reply_to(
        message,
        messages.MY_PROFILE.format(
            user_id=user.id,
            bot_user_name=config.BOT_USER_NAME,
            full_name=user.full_name,
            balance=user.balance_readable if user.balance_readable else 0,
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
            referral_count=utils.get_user_referral_count(telegram_user=telegram_user),
            bonus=config.REFERRAL_BONUS_AMOUNT,
        ),
        parse_mode="html",
    )


@bot.message_handler(regexp=captions.SUPPORT, is_subscribed_user=True)
def support(message):
    bot.reply_to(
        message,
        text=messages.WELCOME_MESSAGE.format(config.TELEGRAM_ADMIN_USER_NAME),
        parse_mode="markdown",
    )


@bot.message_handler(regexp=captions.PAYMENT, is_subscribed_user=True)
def payment(message):
    bot.reply_to(
        message,
        text=messages.PAYMENT_MESSAGE.format(
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
            card_number=config.CARD_NUMBER,
            card_owner=config.CARD_OWNER,
        ),
        parse_mode="html",
        disable_web_page_preview=True,
    )


@bot.message_handler(regexp=captions.MY_SERVICES, is_subscribed_user=True)
def my_services(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = sorted(user.accounts, key=lambda x: x.modified_at, reverse=True)

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

    if (
        utils.allow_to_get_new_test_service(user_id=user.id)
        and config.TEST_SERVICE_ID > 0
    ):

        try:
            utils.place_paid_order(
                chat_id=user.telegram_chat_id,
                account_id=0,
                service_id=config.TEST_SERVICE_ID,
            )

            bot.reply_to(
                message,
                messages.GET_TEST_SERVICE_SUCCESS.format(
                    admin_id=config.TELEGRAM_ADMIN_USER_NAME
                ),
                parse_mode="html",
                disable_web_page_preview=True,
            )

            utils.send_message_to_admin(
                messages.GET_TEST_SERVICE_ADMIN_ALERT.format(
                    chat_id=telegram_user.id, full_name=telegram_user.full_name
                ),
                disable_notification=True,
            )

        except Exception as error:
            logger.error(error)
            utils.send_message_to_admin(
                messages.GET_TEST_SERVICE_ERROR_ADMIN_ALERT.format(
                    chat_id=telegram_user.id, full_name=telegram_user.full_name
                ),
                disable_notification=False,
            )

    else:
        bot.reply_to(
            message,
            messages.GET_TEST_SERVICE_NOT_ALLOWED.format(
                day=config.TEST_ACCOUNT_LIMIT_INTERVAL_DAYS,
                admin_id=config.TELEGRAM_ADMIN_USER_NAME,
            ),
            parse_mode="html",
            disable_web_page_preview=True,
        )


@bot.message_handler(regexp=captions.BUY_NEW_SERVICE, is_subscribed_user=True)
def buy_service(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    available_services = utils.get_available_service()

    if not available_services:
        bot.reply_to(message, messages.BUY_NEW_SERVICE_HELP)
    else:
        bot.reply_to(
            message,
            messages.BUY_NEW_SERVICE_HELP,
            reply_markup=BotUserKeyboard.available_services(
                available_services=available_services
            ),
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
    func=lambda call: call.data.startswith("recharge_service_1:"),
    is_subscribed_user=True,
)
def recharge_service_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    account_id = call.data.split(":")[1]

    available_services = utils.get_available_service()

    if not available_services:
        bot.send_message(
            text=messages.BUY_NEW_SERVICE_HELP, chat_id=call.message.chat.id
        )
    bot.reply_to(
        message=call.message,
        text=messages.RECHARGE_SERVICE_HELP,
        # chat_id=call.message.chat.id,
        reply_markup=BotUserKeyboard.available_services(
            available_services=available_services, account_id=account_id
        ),
        parse_mode="html",
        disable_web_page_preview=True,
    )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_1:"),
    is_subscribed_user=True,
)
def buy_service_step_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    service_id = call.data.split(":")[1]

    account_id = call.data.split(":")[2]

    service = utils.get_service(service_id=int(service_id))

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_CONFIRMATION.format(
            service.name, service.price_readable
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_1(
            service_id=service_id, account_id=account_id
        ),
        parse_mode="html",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_2:"),
    is_subscribed_user=True,
)
def buy_service_step_2(call: types.CallbackQuery):
    telegram_user = call.from_user

    service_id = call.data.split(":")[1]
    account_id = call.data.split(":")[2]

    service = utils.get_service(service_id=int(service_id))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    try:
        order = utils.place_paid_order(
            chat_id=telegram_user.id,
            account_id=int(account_id),
            service_id=int(service_id),
        )

        if int(account_id) > 0:
            bot.edit_message_text(
                text=messages.RECHARGE_SERVICE_FINAL.format(
                    order.id, config.TELEGRAM_ADMIN_USER_NAME
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
        else:
            bot.edit_message_text(
                text=messages.BUY_NEW_SERVICE_FINAL.format(
                    order.id, config.TELEGRAM_ADMIN_USER_NAME
                ),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
    except MaxOpenOrderError as error:
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_MAX_OPEN_ORDERS.format(
                total="1", admin_id=config.TELEGRAM_ADMIN_USER_NAME
            ),
            parse_mode="html",
        )
    except MaxPendingOrderError as error:
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_MAX_OPEN_ORDERS.format(
                total="1", admin_id=config.TELEGRAM_ADMIN_USER_NAME
            ),
            parse_mode="html",
        )
    except NoEnoughBalanceError as error:
        balance = user.balance_readable if user.balance_readable else 0
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_NO_ENOUGH_BALANCE.format(
                balance=balance, admin_id=config.TELEGRAM_ADMIN_USER_NAME
            ),
            parse_mode="html",
        )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(is_reply=True)
def get_account_name(message: types.Message):
    key = f"{message.reply_to_message.message_id}:{message.chat.id}"
    if key in change_account_name_message_ids:
        db_account = utils.update_account_user_title(
            account_id=change_account_name_message_ids[key], title=message.text
        )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("change_account_name:"),
    is_subscribed_user=True,
)
def change_account_name(call: types.CallbackQuery):
    account_id = call.data.split(":")[1]
    message = bot.send_message(
        call.from_user.id, "Enter No.", reply_markup=ForceReply()
    )
    change_account_name_message_ids[f"{message.message_id}:{message.chat.id}"] = (
        account_id
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
                account.service_title,
                account.user_title,
                expired_at,
                utils.get_readable_size(account.used_traffic),
                utils.get_readable_size(account.data_limit),
                percent_traffic_usage,
                config.SUBSCRIPTION_BASE_URL,
                account.uuid,
            ),
            chat_id=telegram_user.id,
            reply_markup=BotUserKeyboard.my_account(account),
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
