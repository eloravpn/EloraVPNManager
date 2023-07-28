from typing import List, Tuple

from sqlalchemy.orm import Session

from src.inbounds.models import Inbound
from src.users.models import User
from src.users.schemas import UserCreate, UserModify


def create_user(db: Session, user: UserCreate):
    db_user = User(username=user.username, first_name=user.first_name, last_name=user.last_name,
                   hashed_password=user.hashed_password,
                   description=user.description, telegram_chat_id=user.telegram_chat_id, phone_number=user.phone_number,
                   telegram_username=user.telegram_username, enable=user.enable, banned=user.banned)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: Inbound, modify: UserModify):
    db_user.username = modify.username
    db_user.first_name = modify.first_name
    db_user.last_name = modify.last_name
    db_user.description = modify.description
    db_user.telegram_chat_id = modify.telegram_chat_id
    db_user.telegram_username = modify.telegram_username
    db_user.phone_number = modify.phone_number
    db_user.enable = modify.enable
    db_user.banned = modify.banned

    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(db: Session, return_with_count: bool = True) -> Tuple[List[User], int]:
    query = db.query(User)

    query = query.order_by(User.modified_at.desc())

    count = query.count()

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def remove_user(db: Session, db_user: User):
    db.delete(db_user)
    db.commit()
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_telegram_chat_id(db: Session, telegram_chat_id: int):
    return db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
