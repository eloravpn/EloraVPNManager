import random
import string

from src import logger
from src.database import GetDB
from src.users.schemas import UserCreate, UserResponse
from src.users.service import create_user, get_user_by_telegram_chat_id


def add_or_get_user(telegram_user) -> UserResponse:
    try:
        with GetDB() as db:
            username = telegram_user.username if telegram_user.username else telegram_user.id
            db_user = get_user_by_telegram_chat_id(db=db, telegram_chat_id=telegram_user.id)

            if not db_user:
                user = UserCreate(username=username, first_name=telegram_user.first_name,
                                  last_name=telegram_user.last_name, telegram_chat_id=telegram_user.id,
                                  telegram_username=telegram_user.username, password=get_random_string(10),
                                  enable=True)
                db_user = create_user(db=db, user=user)

            return UserResponse.from_orm(db_user)
    except Exception as err:
        logger.error(err)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
