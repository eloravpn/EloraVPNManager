import random
import string

import humanize as humanize
import pytz

from src import logger
from src.database import GetDB
from src.users.schemas import UserCreate, UserResponse
import src.users.service as user_service
import src.accounts.service as account_service

from persiantools.jdatetime import JalaliDateTime


# from src.users.service import create_user, get_user_by_telegram_chat_id


def add_or_get_user(telegram_user) -> UserResponse:
    try:
        with GetDB() as db:
            username = telegram_user.username if telegram_user.username else telegram_user.id
            db_user = user_service.get_user_by_telegram_chat_id(db=db, telegram_chat_id=telegram_user.id)

            if not db_user:
                logger.info("Create telegram_user for:" + str(telegram_user))

                user = UserCreate(username=username, first_name=telegram_user.first_name,
                                  last_name=telegram_user.last_name, telegram_chat_id=telegram_user.id,
                                  telegram_username=telegram_user.username, password=get_random_string(10),
                                  enable=True)
                db_user = user_service.create_user(db=db, user=user)

            return UserResponse.from_orm(db_user)
    except Exception as err:
        logger.error(err)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_my_accounts(user_id: int):
    with GetDB() as db:
        accounts = account_service.get_my_accounts(db=db, user_id=user_id)

        return accounts


def get_readable_size(size: int):
    return humanize.naturalsize(size, binary=True, format='%.2f')


def get_readable_size_short(size: int):
    return humanize.naturalsize(size, binary=True, gnu=True, format='%.0f')


def get_jalali_date(ms: int):
    return JalaliDateTime.fromtimestamp(ms,
                                        pytz.timezone("Asia/Tehran")).strftime("%Y/%m/%d")
