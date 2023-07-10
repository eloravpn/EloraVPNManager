from typing import List, Tuple

from sqlalchemy.orm import Session

from src.accounts.models import Account
from src.accounts.schemas import AccountCreate, AccountModify
from src.users.models import User


def create_account(db: Session, db_user: User, account: AccountCreate):
    db_account = Account(user_id=db_user.id, uuid=account.uuid, email=account.email,
                         data_limit=account.data_limit,
                         expired_at=account.expired_at,
                         enable=account.enable)

    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_account(db: Session, db_account: Account, modify: AccountModify):
    db_account.uuid = modify.uuid
    db_account.email = modify.email
    # db_account.used_traffic = modify.used_traffic
    db_account.data_limit = modify.data_limit
    db_account.expired_at = modify.expired_at

    db_account.enable = modify.enable

    db.commit()
    db.refresh(db_account)

    return db_account


def get_accounts(db: Session, return_with_count: bool = True) -> Tuple[List[Account], int]:
    query = db.query(Account)

    count = query.count()

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def remove_account(db: Session, db_account: Account):
    db.delete(db_account)
    db.commit()
    return db_account


def get_account(db: Session, account_id: int):
    return db.query(Account).filter(Account.id == account_id).first()
