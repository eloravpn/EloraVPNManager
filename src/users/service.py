from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import cast, String, or_
from sqlalchemy.orm import Session

from src.accounts.models import Account
from src.inbounds.models import Inbound
from src.users.models import User
from src.users.schemas import UserCreate, UserModify

UserSortingOptions = Enum('UserSortingOptions', {
    'created': User.created_at.asc(),
    '-created': User.created_at.desc(),
    'modified': User.modified_at.asc(),
    '-modified': User.modified_at.desc(),
    'first_name': User.first_name.asc(),
    '-first_name': User.first_name.desc(),
    'last_name': User.last_name.asc(),
    '-last_name': User.last_name.desc(),
    'telegram_username': User.last_name.asc(),
    '-telegram_username': User.last_name.desc(),
})


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


def get_users(db: Session,
              offset: Optional[int] = None,
              limit: Optional[int] = None,
              sort: Optional[List[UserSortingOptions]] = None,
              q: str = None,
              return_with_count: bool = True) -> Tuple[List[User], int]:
    query = db.query(User)

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    if q:
        query = query.join(Account, User.id == Account.user_id)
        query = query.filter(or_(User.first_name.ilike(f"%{q}%"),
                                 User.last_name.ilike(f"%{q}%"),
                                 User.username.ilike(f"%{q}%"),
                                 User.telegram_username.ilike(f"%{q}%"),
                                 cast(User.telegram_chat_id, String).ilike(f"%{q}%")
                                 ))

    count = query.count()

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

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
