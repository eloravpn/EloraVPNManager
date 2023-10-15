import random
import string

import humanize as humanize
import pytz
from persiantools.jdatetime import JalaliDateTime
from telebot.apihelper import ApiTelegramException

import src.accounts.service as account_service
import src.commerce.service as commerce_service
import src.users.service as user_service
from src import logger, config
from src.accounts.schemas import AccountCreate, AccountResponse
from src.commerce.models import Service, Order
from src.commerce.schemas import OrderCreate, OrderStatus
from src.config import TELEGRAM_ADMIN_ID
from src.database import GetDB
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
                message,
                parse_mode=parse_mode,
                reply_markup=keyboard,
                disable_notification=disable_notification,
            )
        except ApiTelegramException as e:
            logger.error(e)


def get_available_service():
    try:
        with GetDB() as db:
            return commerce_service.get_services(
                db=db, limit=20, return_with_count=False, enable=1
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


def add_or_get_user(telegram_user) -> UserResponse:
    try:
        with GetDB() as db:
            username = (
                telegram_user.username if telegram_user.username else telegram_user.id
            )
            db_user = user_service.get_user_by_telegram_chat_id(
                db=db, telegram_chat_id=telegram_user.id
            )

            if not db_user:
                logger.info("Create telegram user for:" + str(telegram_user))

                user = UserCreate(
                    username=username,
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


def add_test_account(user_id: int):
    with GetDB() as db:
        db_user = user_service.get_user(db=db, user_id=user_id)

        account = AccountCreate(
            user_id=db_user.id,
            data_limit=config.TEST_ACCOUNT_DATA_LIMIT,
            email=config.TEST_ACCOUNT_EMAIL_PREFIX + get_random_string(8),
            enable=True,
        )
        db_account = account_service.create_account(
            db=db, db_user=db_user, account=account
        )
        logger.warn(f"A new test account has been created {account}")
        return AccountResponse.from_orm(db_account)


def get_last_test_account(user_id: int) -> AccountResponse:
    with GetDB() as db:
        db_user = user_service.get_user(db=db, user_id=user_id)
        account = account_service.get_user_last_test_account(db=db, db_user=db_user)

        if account:
            return AccountResponse.from_orm(account)
        else:
            return None


def get_readable_size(size: int):
    return humanize.naturalsize(size, binary=True, format="%.2f")


def get_readable_size_short(size: int):
    return humanize.naturalsize(size, binary=True, gnu=True, format="%.0f")


def get_jalali_date(ms: int):
    return JalaliDateTime.fromtimestamp(ms, pytz.timezone("Asia/Tehran")).strftime(
        "%Y/%m/%d"
    )
