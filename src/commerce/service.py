import datetime
from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import and_, func, or_, String, cast, null
from sqlalchemy.orm import Session

from src import config
from src.accounts.models import Account, AccountUsedTraffic
from src.accounts.schemas import (
    AccountCreate,
    AccountModify,
    AccountUsedTrafficResponse,
)
from src.commerce.models import Transaction, Order, Payment, Service
from src.commerce.schemas import (
    TransactionCreate,
    TransactionModify,
    ServiceCreate,
    OrderCreate,
    OrderModify,
    PaymentCreate,
    PaymentModify,
    PaymentMethod,
    PaymentStatus,
    OrderStatus,
    TransactionType,
)
from src.users.models import User

import src.users.service as user_service

TransactionSortingOptions = Enum(
    "TransactionSortingOptions",
    {
        "created": Account.created_at.asc(),
        "-created": Account.created_at.desc(),
        "modified": Account.modified_at.asc(),
        "-modified": Account.modified_at.desc(),
    },
)

ServiceSortingOptions = Enum(
    "ServiceSortingOptions",
    {
        "created": Service.created_at.asc(),
        "-created": Service.created_at.desc(),
        "modified": Service.modified_at.asc(),
        "-modified": Service.modified_at.desc(),
        "price": Service.price.asc(),
        "-price": Service.price.desc(),
        "duration": Service.duration.asc(),
        "-duration": Service.duration.desc(),
        "data_limit": Service.data_limit.asc(),
        "-data_limit": Service.data_limit.desc(),
    },
)

OrderSortingOptions = Enum(
    "OrderSortingOptions",
    {
        "created": Order.created_at.asc(),
        "-created": Order.created_at.desc(),
        "modified": Order.modified_at.asc(),
        "-modified": Order.modified_at.desc(),
        "total": Order.total.asc(),
        "-total": Order.total.desc(),
        "status": Order.status.asc(),
        "-status": Order.status.desc(),
    },
)

PaymentSortingOptions = Enum(
    "PaymentSortingOptions",
    {
        "created": Payment.created_at.asc(),
        "-created": Payment.created_at.desc(),
        "modified": Payment.modified_at.asc(),
        "-modified": Payment.modified_at.desc(),
        "total": Payment.total.asc(),
        "-total": Payment.total.desc(),
        "status": Payment.status.asc(),
        "-status": Payment.status.desc(),
    },
)


# Transaction CRUDs


def create_transaction(
    db: Session,
    db_user: User,
    transaction: TransactionCreate,
    db_order: Optional[Order] = None,
    db_payment: Optional[Payment] = None,
):
    db_transaction = Transaction(
        user_id=db_user.id,
        order_id=None if db_order is None else db_order.id,
        payment_id=None if db_payment is None else db_payment.id,
        description=transaction.description,
        amount=transaction.amount,
        type=transaction.type,
    )

    balance = db_user.balance if db_user.balance else 0

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    user_service.update_user_balance(
        db=db, db_user=db_user, new_balance=balance + db_transaction.amount
    )

    return db_transaction


# TODO
# def update_transaction(db: Session, db_transaction: Transaction, modify: TransactionModify):
#     db_transaction.description = modify.description
#     db_transaction.amount = modify.amount
#
#     db.commit()
#     db.refresh(db_transaction)
#
#     user_service.update_user_balance(db=db, db_user=db_user, new_balance=balance + db_transaction.amount)
#
#     return db_transaction


def remove_transaction(db: Session, db_user: User, db_transaction: Transaction):
    balance = db_user.balance if db_user.balance else 0

    db.delete(db_transaction)
    db.commit()

    user_service.update_user_balance(
        db=db, db_user=db_user, new_balance=balance - db_transaction.amount
    )

    return db_transaction


def get_transactions(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[TransactionSortingOptions]] = [
        TransactionSortingOptions["-modified"]
    ],
    user_id: int = 0,
    order_id: int = 0,
    payment_id: int = 0,
    type_: TransactionType = None,
    return_with_count: bool = True,
    q: str = None,
) -> Tuple[List[Transaction], int]:
    query = db.query(Transaction)

    if user_id > 0:
        query = query.filter(Transaction.user_id == user_id)

    if order_id > 0:
        query = query.filter(Transaction.order_id == order_id)

    if payment_id > 0:
        query = query.filter(Transaction.payment_id == payment_id)

    if type_:
        query = query.filter(Transaction.type == type_)

    if q:
        query = query.filter(
            or_(
                cast(Transaction.id, String).ilike(f"%{q}%"),
                cast(Transaction.order_id, String).ilike(f"%{q}%"),
                cast(Transaction.payment_id, String).ilike(f"%{q}%"),
                Transaction.description.ilike(f"%{q}%"),
            )
        )

    return _get_query_result(limit, offset, query, return_with_count, sort)


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


# Service CRUDs
def create_service(db: Session, service: ServiceCreate):
    db_service = Service(
        name=service.name,
        duration=service.duration,
        data_limit=service.data_limit,
        price=service.price,
        discount=service.discount,
        enable=service.enable,
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


def update_service(db: Session, db_service: Service, modify: ServiceCreate):
    db_service.name = modify.name
    db_service.duration = modify.duration
    db_service.data_limit = modify.data_limit
    db_service.price = modify.price
    db_service.discount = modify.discount
    db_service.enable = modify.enable

    db.commit()
    db.refresh(db_service)

    return db_service


def remove_service(db: Session, db_service: Service):
    db.delete(db_service)
    db.commit()

    return db_service


def get_services(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[ServiceSortingOptions]] = [ServiceSortingOptions["-modified"]],
    return_with_count: bool = True,
    q: str = None,
) -> Tuple[List[Transaction], int]:
    query = db.query(Service)

    if q:
        query = query.filter(
            or_(
                cast(Service.id, String).ilike(f"%{q}%"),
                Service.name.ilike(f"%{q}%"),
            )
        )

    return _get_query_result(limit, offset, query, return_with_count, sort)


def get_service(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()


# Order CRUDs


def create_order(
    db: Session,
    db_user: User,
    order: OrderCreate,
    db_account: Optional[Account] = None,
    db_service: Optional[Service] = None,
):
    db_order = Order(
        user_id=db_user.id,
        account_id=None if db_account is None else db_account.id,
        service_id=None if db_service is None else db_service.id,
        status=order.status,
        duration=order.duration,
        data_limit=order.data_limit,
        total=order.total,
        total_discount_amount=order.total_discount_amount,
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


def update_order(db: Session, db_order: Order, modify: OrderModify):
    db_order.status = modify.status
    db_order.duration = modify.duration
    db_order.data_limit = modify.data_limit
    db_order.total = modify.total
    db_order.total_discount_amount = modify.total_discount_amount

    db.commit()
    db.refresh(db_order)

    return db_order


def remove_order(db: Session, db_order: Order):
    db.delete(db_order)
    db.commit()

    return db_order


def get_orders(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[OrderSortingOptions]] = [OrderSortingOptions["-modified"]],
    return_with_count: bool = True,
    user_id: int = 0,
    account_id: int = 0,
    status: OrderStatus = None,
    q: str = None,
) -> Tuple[List[Transaction], int]:
    query = db.query(Order)

    if user_id > 0:
        query = query.filter(Order.user_id == user_id)

    if account_id > 0:
        query = query.filter(Order.account_id == account_id)

    if status:
        query = query.filter(Order.status == status)

    if q:
        query = query.filter(
            or_(
                cast(Order.id, String).ilike(f"%{q}%"),
            )
        )
    return _get_query_result(limit, offset, query, return_with_count, sort)


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


# Payment CRUDs


def create_payment(
    db: Session,
    db_user: User,
    payment: PaymentCreate,
    db_order: Optional[Order] = None,
):
    db_payment = Payment(
        user_id=db_user.id,
        order_id=None if db_order is None else db_order.id,
        status=payment.status,
        method=payment.method,
        total=payment.total,
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


def update_payment(db: Session, db_payment: Payment, modify: PaymentModify):
    db_payment.status = modify.status
    db_payment.total = modify.total

    db.commit()
    db.refresh(db_payment)

    return db_payment


def remove_payment(db: Session, db_payment: Payment):
    db.delete(db_payment)
    db.commit()

    return db_payment


def get_payments(
    db: Session,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[PaymentSortingOptions]] = [PaymentSortingOptions["-modified"]],
    return_with_count: bool = True,
    order_id: int = 0,
    user_id: int = 0,
    method: PaymentMethod = None,
    status: PaymentStatus = None,
    q: str = None,
) -> Tuple[List[Transaction], int]:
    query = db.query(Payment)

    if user_id > 0:
        query = query.filter(Payment.user_id == user_id)

    if order_id > 0:
        query = query.filter(Payment.order_id == order_id)

    if method:
        query = query.filter(Payment.method == method)

    if status:
        query = query.filter(Payment.status == status)

    if q:
        query = query.filter(
            or_(
                cast(Payment.id, String).ilike(f"%{q}%"),
            )
        )
    return _get_query_result(limit, offset, query, return_with_count, sort)


def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def _get_query_result(limit, offset, query, return_with_count, sort):
    if sort:
        query = query.order_by(*(opt.value for opt in sort))
    count = query.count()
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    if return_with_count:
        return query.all(), count
    else:
        return query.all()
