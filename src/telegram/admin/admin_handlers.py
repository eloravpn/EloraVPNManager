import datetime
import logging

import pytz
from telebot import types, custom_filters
from telebot.apihelper import ApiTelegramException

from src import config
from src.accounts.service import get_account
from src.commerce.schemas import OrderStatus, TransactionType
from src.database import GetDB
from src.notification.schemas import NotificationStatus
from src.notification.service import get_notification, update_status
from src.telegram import bot, utils
from src.telegram.admin import messages
from src.telegram.admin.keyboard import BotAdminKeyboard
from src.users.service import get_user


class IsAdminUser(custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = "is_admin"

    @staticmethod
    def check(message: types.Message):
        telegram_user = message.from_user

        if telegram_user.id == config.TELEGRAM_ADMIN_ID:
            return True
        else:
            return False


bot.add_custom_filter(IsAdminUser())


@bot.message_handler(is_admin=True, is_forwarded=True)
def handle_froward_message(message: types.Message):
    telegram_info = ""
    account_details = ""
    telegram_chat_id = 0

    payment_details = ""

    if message.forward_from:
        telegram_chat_id = message.forward_from.id
        telegram_info = messages.USER_INFO.format(
            id=message.forward_from.id,
            full_name=message.forward_from.full_name,
            username=message.forward_from.username,
        )
    elif message.forward_sender_name:
        telegram_info = messages.USER_INFO.format(
            id=message.forward_sender_name,
            full_name=message.forward_sender_name,
            username=message.forward_sender_name,
        )

    if telegram_chat_id > 0:
        user = utils.get_user_by_chat_id(telegram_chat_id=telegram_chat_id)
        if user:
            for account in user.accounts:
                account_details = account_details + messages.ACCOUNT_DETAIL.format(
                    id=account.id,
                    email=account.email,
                    used_traffic_percent=account.used_traffic_percent,
                    data_limit=utils.get_readable_size(account.data_limit),
                    enable="✅" if account.enable else "❌",
                )

            payment_details = utils.get_user_payment_history(user.telegram_chat_id)

    bot.send_message(
        chat_id=message.from_user.id,
        text=telegram_info + account_details + payment_details,
        disable_web_page_preview=True,
        parse_mode="html",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve_notification:")
)
def approve_notification(call: types.CallbackQuery):
    telegram_user = call.from_user

    notification_id = int(call.data.split(":")[1])
    with GetDB() as db:
        db_notification = get_notification(db=db, notification_id=notification_id)

        if db_notification.account_id:
            db_account = get_account(db=db, account_id=db_notification.account_id)
            db_user = get_user(db=db, user_id=db_account.user_id)
        elif db_notification.user_id:
            db_user = get_user(db=db, user_id=db_notification.user_id)

        try:
            bot.send_message(
                text=db_notification.message,
                chat_id=db_user.telegram_chat_id,
                parse_mode="html",
            )

            update_status(
                db=db,
                db_notification=db_notification,
                status=NotificationStatus.sent,
                approve=True,
            )

            bot.edit_message_text(
                text=f"Notification with id <code>{db_notification.id}</code> Approved and Sent to {db_user.full_name}!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
        except Exception as error:
            logging.error(error)
            update_status(
                db=db,
                db_notification=db_notification,
                status=NotificationStatus.failed,
                approve=True,
            )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("decline_notification:")
)
def decline_notification(call: types.CallbackQuery):
    telegram_user = call.from_user

    notification_id = call.data.split(":")[1]
    with GetDB() as db:
        db_notification = get_notification(db=db, notification_id=notification_id)
        db_account = get_account(db=db, account_id=db_notification.account_id)

        update_status(
            db=db,
            db_notification=db_notification,
            status=NotificationStatus.canceled,
            approve=False,
        )

        bot.edit_message_text(
            text=f"Notification with id <code>{db_notification.id}</code> Declined to sent to {db_account.user.full_name}!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="html",
        )


# Handle '/admin'
@bot.message_handler(commands=["admin"], is_admin=True)
def send_welcome(message: types.Message):
    bot.send_message(
        chat_id=message.from_user.id,
        text="Hi admin!",
        disable_web_page_preview=True,
        reply_markup=BotAdminKeyboard.main_menu(),
        parse_mode="markdown",
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "report_account_usage", is_admin=True
)
def report_account_usage(call: types.CallbackQuery):
    last_24h_usage = utils.get_all_account_usage(1)
    last_week_usage = utils.get_all_account_usage(7)
    last_month_usage = utils.get_all_account_usage(30)

    active_accounts = utils.get_accounts(enable=True, test_account=False)

    test_accounts = utils.get_accounts(enable=False, test_account=True)

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=messages.ACCOUNT_USAGE.format(
                total_active_accounts=active_accounts[1],
                total_active_test_accounts=test_accounts[1],
                last_24h_usage=utils.get_readable_size(last_24h_usage),
                last_week_usage=utils.get_readable_size(last_week_usage),
                last_month_usage=utils.get_readable_size(last_month_usage),
            ),
            reply_markup=BotAdminKeyboard.main_menu(),
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    except ApiTelegramException as Error:
        logging.error(Error)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data == "account_usage_detail", is_admin=True
)
def account_usage_detail(call: types.CallbackQuery):
    report = utils.get_all_account_usage_report(1)

    report_message = _get_account_usage_from_report(report)

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=report_message,
            reply_markup=BotAdminKeyboard.main_menu(),
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    except ApiTelegramException as Error:
        logging.error(Error)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data == "report_orders", is_admin=True
)
def report_orders(call: types.CallbackQuery):
    today_paid_orders = utils.get_orders(1, OrderStatus.paid)
    today_completed_orders = utils.get_orders(1, OrderStatus.completed)

    last_week_paid_orders = utils.get_orders(7, OrderStatus.paid)
    last_week_completed_orders = utils.get_orders(7, OrderStatus.completed)

    last_month_paid_orders = utils.get_orders(30, OrderStatus.paid)
    last_month_completed_orders = utils.get_orders(30, OrderStatus.completed)

    last_24h_orders = today_paid_orders[1] + today_completed_orders[1]
    last_week_orders = last_week_paid_orders[1] + last_week_completed_orders[1]
    last_month_orders = last_month_paid_orders[1] + last_month_completed_orders[1]

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=messages.ORDERS_REPORT.format(
                last_24h_orders=last_24h_orders,
                last_week_orders=last_week_orders,
                last_month_orders=last_month_orders,
            ),
            reply_markup=BotAdminKeyboard.main_menu(),
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    except ApiTelegramException as Error:
        logging.error(Error)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data == "report_transaction", is_admin=True
)
def report_transaction(call: types.CallbackQuery):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=messages.TRANSACTIONS_REPORT.format(
                last_24h_payment=utils.get_price_readable(
                    utils.get_transaction_sum(1, TransactionType.payment)
                ),
                last_24h_orders=utils.get_price_readable(
                    utils.get_transaction_sum(1, TransactionType.order)
                ),
                last_24h_bonuses=utils.get_price_readable(
                    utils.get_transaction_sum(1, TransactionType.bonus)
                ),
                last_week_payment=utils.get_price_readable(
                    utils.get_transaction_sum(7, TransactionType.payment)
                ),
                last_week_orders=utils.get_price_readable(
                    utils.get_transaction_sum(7, TransactionType.order)
                ),
                last_week_bonuses=utils.get_price_readable(
                    utils.get_transaction_sum(7, TransactionType.bonus)
                ),
                last_month_payment=utils.get_price_readable(
                    utils.get_transaction_sum(30, TransactionType.payment)
                ),
                last_month_orders=utils.get_price_readable(
                    utils.get_transaction_sum(30, TransactionType.order)
                ),
                last_month_bonuses=utils.get_price_readable(
                    utils.get_transaction_sum(30, TransactionType.bonus)
                ),
                total_payment=utils.get_price_readable(
                    utils.get_transaction_sum(type_=TransactionType.payment)
                ),
                total_orders=utils.get_price_readable(
                    utils.get_transaction_sum(type_=TransactionType.order)
                ),
                total_bonuses=utils.get_price_readable(
                    utils.get_transaction_sum(type_=TransactionType.bonus)
                ),
            ),
            reply_markup=BotAdminKeyboard.main_menu(),
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    except ApiTelegramException as Error:
        logging.error(Error)

    bot.answer_callback_query(callback_query_id=call.id)


def _get_account_usage_from_report(report):
    tz_IR = pytz.timezone("Asia/Tehran")
    now = datetime.datetime.now().astimezone(tz_IR)

    message = """
    *Now*: `{}` \n\n*Date \| Count \| Usage*\n""".format(
        now.strftime("%y\-%m\-%d %H:%M:%S")
    )
    for item in report:
        date = item.date.replace(tzinfo=pytz.utc)

        message += """`{}` \| `{}` \|  `{}` \n""".format(
            date.astimezone(tz_IR).strftime("%m-%d %H:%M"),
            item.count,
            utils.get_readable_size(item.download + item.upload),
        )

    return message
