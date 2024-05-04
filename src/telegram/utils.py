import datetime
import random
import string
from typing import List

import humanize as humanize
import pytz
from persiantools.jdatetime import JalaliDateTime
from telebot import types
from telebot.apihelper import ApiTelegramException

import src.accounts.service as account_service
import src.commerce.service as commerce_service
import src.users.service as user_service
from src import logger, config
from src.accounts.models import Account
from src.accounts.schemas import (
    AccountCreate,
    AccountResponse,
    AccountUsedTrafficReportResponse,
)
from src.commerce.models import Service, Order
from src.commerce.schemas import OrderCreate, OrderStatus, TransactionType
from src.config import TELEGRAM_ADMIN_ID
from src.database import GetDB
from src.hosts.service import get_host_zone
from src.notification.models import Notification
from src.telegram import bot
from src.users.models import User
from src.users.schemas import UserCreate, UserResponse


# from src.users.service import create_user, get_user_by_telegram_chat_id


def send_message_to_admin(
    message: str, parse_mode="html", keyboard=None, disable_notification: bot = False
):
    if bot and TELEGRAM_ADMIN_ID:
        try:
            bot.send_message(
                TELEGRAM_ADMIN_ID,
                text=message,
                parse_mode=parse_mode,
                reply_markup=keyboard,
                disable_notification=disable_notification,
            )
        except ApiTelegramException as e:
            logger.error(e)


def send_message_to_user(
    message: str,
    parse_mode="html",
    keyboard=None,
    disable_notification: bot = False,
    chat_id=int,
):
    if bot and TELEGRAM_ADMIN_ID:
        try:
            bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
                reply_markup=keyboard,
                disable_notification=disable_notification,
            )
        except ApiTelegramException as e:
            logger.error(e)


def send_approval_message(account: Account, db_notification: Notification):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(
            text="Approve",
            callback_data=f"approve_notification:{db_notification.id}",
        ),
        types.InlineKeyboardButton(
            text="Decline!",
            callback_data=f"decline_notification:{db_notification.id}",
        ),
    )
    send_message_to_admin(
        message=f"Send notification to {account.user.full_name}/ <code>{account.email}</code> \n"
        + db_notification.message,
        keyboard=keyboard,
    )


def send_approval_message_to_admin_by_user(
    db_user: User, db_notification: Notification
):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(
            text="Approve",
            callback_data=f"approve_notification:{db_notification.id}",
        ),
        types.InlineKeyboardButton(
            text="Decline!",
            callback_data=f"decline_notification:{db_notification.id}",
        ),
    )
    send_message_to_admin(
        message=f"Send notification to {db_user.full_name}/ <code>{db_user.telegram_chat_id}</code> \n"
        + db_notification.message,
        keyboard=keyboard,
    )


def get_available_service():
    try:
        with GetDB() as db:
            return commerce_service.get_services(
                db=db,
                limit=20,
                return_with_count=False,
                enable=1,
                sort=[commerce_service.ServiceSortingOptions["name"]],
            )
    except Exception as err:
        logger.error(err)
        return None


def get_service(service_id: int) -> Service:
    try:
        with GetDB() as db:
            return commerce_service.get_service(db=db, service_id=service_id)
    except Exception as err:
        logger.error(err)
        return None


def place_paid_order(chat_id: int, account_id: int, service_id: int) -> Order:
    with GetDB() as db:
        db_account = None

        db_user = user_service.get_user_by_telegram_chat_id(
            db=db, telegram_chat_id=chat_id
        )

        db_service = commerce_service.get_service(db=db, service_id=service_id)

        if account_id > 0:
            db_account = account_service.get_account(db, account_id=account_id)

        order = OrderCreate(user_id=db_user.id, status=OrderStatus.paid)

        return commerce_service.create_order(
            db=db,
            db_user=db_user,
            db_account=db_account,
            db_service=db_service,
            order=order,
        )


def get_user_referral_count(telegram_user) -> UserResponse:
    try:
        with GetDB() as db:
            db_user = user_service.get_user_by_telegram_chat_id(
                db=db, telegram_chat_id=telegram_user.id
            )
            return user_service.get_user_referral_count(db=db, user_id=db_user.id)
    except Exception as error:
        logger.error(error)

    return 0


def add_or_get_user(telegram_user, referral_user: User = None) -> UserResponse:
    try:
        with GetDB() as db:
            username = (
                telegram_user.username if telegram_user.username else telegram_user.id
            )
            db_user = user_service.get_user_by_telegram_chat_id(
                db=db, telegram_chat_id=telegram_user.id
            )

            if referral_user:
                logger.info(f"Referral User is 👤 {referral_user.full_name}")

            if not db_user:
                logger.info("Create telegram user for:" + str(telegram_user))

                user = UserCreate(
                    username=username,
                    referral_user_id=referral_user.id if referral_user else None,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    telegram_chat_id=telegram_user.id,
                    telegram_username=telegram_user.username,
                    password=get_random_string(10),
                    enable=True,
                )
                db_user = user_service.create_user(db=db, user=user)
            else:
                db_user = user_service.update_user_info(
                    db=db,
                    db_user=db_user,
                    username=db_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    telegram_username=telegram_user.username,
                )

                logger.info(
                    f"Telegram user info updated for 👤 {db_user.full_name} ({db_user.telegram_username}/{db_user.telegram_chat_id})"
                )

            return UserResponse.from_orm(db_user)
    except Exception as err:
        logger.error(err)


def get_all_account_usage(delta: int):
    result = 0

    with GetDB() as db:
        data_usage = account_service.get_all_accounts_used_traffic(db=db, delta=delta)
        if data_usage.download is not None:
            result += data_usage.download

        if data_usage.upload is not None:
            result += data_usage.upload

    return result


def get_all_account_usage_report(delta: int) -> List[AccountUsedTrafficReportResponse]:
    with GetDB() as db:
        return account_service.get_account_used_traffic_report(
            db=db, start_date=_get_date(delta)
        )


def get_accounts(enable: bool, test_account: bool):
    with GetDB() as db:
        return account_service.get_accounts(
            db=db, filter_enable=True, enable=enable, test_account=test_account
        )


def get_orders(
    delta: int,
    status: OrderStatus = None,
):
    with GetDB() as db:
        return commerce_service.get_orders(
            db=db, start_date=_get_date(delta=delta), status=status
        )


def get_transaction_sum(
    delta: int = 0,
    type_: TransactionType = None,
) -> int:
    with GetDB() as db:
        return commerce_service.get_transactions_sum(
            db=db, start_date=_get_date(delta=delta) if delta > 0 else None, type_=type_
        )


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def get_my_accounts(user_id: int):
    with GetDB() as db:
        accounts = account_service.get_my_accounts(db=db, user_id=user_id)

        return accounts


def get_account(account_id: int):
    with GetDB() as db:
        account = account_service.get_account(db=db, account_id=account_id)

        return account


def get_user(user_id=0) -> User:
    with GetDB() as db:
        account = user_service.get_user(db=db, user_id=user_id)

        return account


def allow_to_get_new_test_service(user_id: int) -> bool:
    with GetDB() as db:
        db_user = user_service.get_user(db=db, user_id=user_id)
        orders, count = commerce_service.get_orders(
            db=db,
            start_date=_get_date(config.TEST_ACCOUNT_LIMIT_INTERVAL_DAYS),
            user_id=db_user.id,
            service_id=config.TEST_SERVICE_ID,
        )

        if count > 0:
            return False
        else:
            return True


def get_readable_size(size: int):
    return humanize.naturalsize(size, binary=True, format="%.2f")


def get_readable_size_short(size: int):
    return humanize.naturalsize(size, binary=True, gnu=True, format="%.0f")


def get_jalali_date(ms: int):
    return JalaliDateTime.fromtimestamp(ms, pytz.timezone("Asia/Tehran")).strftime(
        "%Y/%m/%d"
    )


def get_price_readable(price):
    if price:
        return f"{price :,}"
    else:
        return 0


def _get_date(delta: int, before: bool = True):
    today = datetime.datetime.utcnow()

    if before:
        return today - datetime.timedelta(days=delta)
    else:
        return today + datetime.timedelta(days=delta)
