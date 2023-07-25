import sqlite3
from datetime import datetime

from sqlalchemy.exc import IntegrityError

import src.users.service
from src import config
from src.accounts.schemas import AccountCreate
from src.database import GetDB
from src.telegram import utils
from src.users.schemas import UserCreate


def get_inbound_settings(inbound_id):
    conn = sqlite3.connect(config.XUI_DB_PATH)
    cursor = conn.execute(
        f"select id,settings from inbounds where id = '{inbound_id}'")

    for c in cursor:
        settings = c[1]

    return settings


def get_all_client_infos(inbound_id: int, limit: int = 20, offset: int = 0, enabled: bool = True,
                         order_by: str = 'id'):
    conn = sqlite3.connect(config.XUI_DB_PATH)
    sql = f"select email,up,down,total,expiry_time from client_traffics "
    sql += f"where enable = {enabled} and inbound_id ={inbound_id} "
    sql += f"order by {order_by} DESC "
    sql += f"limit {limit} offset {offset}"

    cursor = conn.execute(sql)
    client_info_list = []
    for c in cursor:
        expire_time = 0
        if c[4] != 0:
            expire_time = c[4]
        client_info_list.append({'email': c[0], 'up': c[1], 'down': c[2], 'total': c[3],
                                 'expiry_time': expire_time})
    conn.close()
    return client_info_list


def get_old_users():
    conn = sqlite3.connect(config.OLD_BOT_DB_PATH)
    sql = f"select id,chat_id,username,first_name,last_name,date_added from user "
    return conn.execute(sql)


def get_user_chat_id(email: str):
    conn = sqlite3.connect(config.OLD_BOT_DB_PATH)
    sql = f"select chat_id from user inner join account a on user.id = a.user_id where a.email = '{email}'"
    return conn.execute(sql).fetchone()[0]


def get_account_uuid(email: str):
    conn = sqlite3.connect(config.OLD_BOT_DB_PATH)
    sql = f"select uuid from account where email = '{email}'"
    return conn.execute(sql).fetchone()[0]


if __name__ == "__main__":
    client_list = get_all_client_infos(1, 500, 0, True)

    # for c in get_old_users():
    #     with GetDB() as db:
    #         user_model = UserCreate(password=utils.get_random_string(10))
    #         user_model.username = str(c[1]) if not c[2] else c[2].lower()
    #         user_model.telegram_chat_id = c[1]
    #         user_model.telegram_username = c[2]
    #         user_model.first_name = c[3] if c[3] else ""
    #         user_model.last_name = c[4] if c[4] else ""
    #         print(user_model)
    #
    #
    #         try:
    #             src.users.service.create_user(db, user_model)
    #         except IntegrityError as error:
    #             print("Duplicated ...")

    for index, client in enumerate(client_list):
        expire_time = None
        if client['expiry_time'] > 0:
            expire_time = datetime.fromtimestamp(client['expiry_time'] / 1000)
        print("X-UI {} - {}, {}".format(index, client['email'], expire_time))
        chat_id = get_user_chat_id(email=client['email'])
        uuid = get_account_uuid(email=client['email'])
        print(f"Telegram ChatID: {chat_id}")
        if chat_id:
            with GetDB() as db:
                user = src.users.service.get_user_by_telegram_chat_id(db=db, telegram_chat_id=chat_id)
                if user:
                    print(f"New User ID: {user.id}")
                    account_model = AccountCreate(user_id=user.id, uuid=uuid, data_limit=client["total"],
                                                  email=client['email'],
                                                  enable=True,
                                                  expired_at=expire_time)
                    print(f"Final account model is : {account_model}")
                    try:
                        src.accounts.service.create_account(db=db, db_user=user, account=account_model)
                    except IntegrityError as error:
                        print("Duplicated ...")

                else:
                    print("Error: User does not found!")

    # settings = get_inbound_settings(1)
    # print(settings)
    # for index, client in enumerate(client_list):
    #     print("{} - {}".format(index, client['email']))
    #     settings = settings.replace(client["email"], "1_1_" + client["email"])
    #
    # print(settings)
