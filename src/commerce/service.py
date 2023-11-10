import datetime
from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import or_, String, cast, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.users.service as user_service
from src import messages
from src.accounts.models import Account
from src.commerce.exc import (
    MaxOpenOrderError,
    MaxPendingOrderError,
    NoEnoughBalanceError,
    PaymentPaidStatusError,
    OrderNotEditableError,
    OrderStatusConflictError,
)
from src.commerce.models import Transaction, Order, Payment, Service
from src.commerce.schemas import (
    TransactionCreate,
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
from src.hosts.models import HostZone
from src.messages import PAYMENT_METHODS
from src.notification.schemas import NotificationType, NotificationCreate
from src.notification.service import create_notification
from src.users.models import User

TransactionSortingOptions = Enum(
    "TransactionSortingOptions",
    {
        "created": Transaction.created_at.asc(),
        "-created": Transaction.created_at.desc(),
        "modified": Transaction.modified_at.asc(),
        "-modified": Transaction.modified_at.desc(),
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
        "name": Service.name.asc(),
        "-name": Service.name.desc(),
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

    db_user = user_service.update_user_balance(
        db=db, db_user=db_user, new_balance=balance + db_transaction.amount
    )

    if db_transaction.amount > 0:
        _send_notification(
            db=db,
            db_user=db_user,
            type_=NotificationType.transaction,
            message=messages.TRANSACTION_DEPOSIT_NOTIFICATION.format(
                amount=transaction.amount_readable, description=transaction.description
            )
            + messages.USER_BALANCE.format(balance=db_user.balance_readable),
        )
    else:
        _send_notification(
            db=db,
            db_user=db_user,
            type_=NotificationType.transaction,
            message=messages.TRANSACTION_WITHDRAW_NOTIFICATION.format(
                amount=transaction.amount_readable, description=transaction.description
            )
            + messages.USER_BALANCE.format(balance=db_user.balance_readable),
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


def get_transactions_sum(
    db: Session,
    user_id: int = 0,
    type_: TransactionType = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
) -> int:
    query = db.query(
        func.sum(Transaction.amount).label("sum"),
    )

    if user_id > 0:
        query = query.filter(Transaction.user_id == user_id)

    if type_:
        query = query.filter(Transaction.type == type_)

    if user_id > 0:
        query = query.filter(Transaction.user_id == user_id)

    if end_date:
        query = query.filter(
            and_(
                Transaction.created_at <= end_date,
            )
        )

    if start_date:
        query = query.filter(
            and_(
                Transaction.created_at >= start_date,
            )
        )

    result = query.one()

    if result:
        return result[0]
    else:
        return 0


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


# Service CRUDs
def create_service(db: Session, service: ServiceCreate, db_host_zone: HostZone = None):
    db_service = Service(
        host_zone_id=1 if db_host_zone is None else db_host_zone.id,
        name=service.name,
        duration=service.duration,
        data_limit=service.data_limit,
        ip_limit=service.ip_limit,
        price=service.price,
        discount=service.discount,
        enable=service.enable,
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


def update_service(db: Session, db_service: Service, modify: ServiceCreate):
    db_service.host_zone_id = modify.host_zone_id
    db_service.name = modify.name
    db_service.duration = modify.duration
    db_service.data_limit = modify.data_limit
    db_service.ip_limit = modify.ip_limit
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
    sort: Optional[List[ServiceSortingOptions]] = [ServiceSortingOptions["name"]],
    return_with_count: bool = True,
    enable: int = -1,
    q: str = None,
) -> Tuple[List[Service], int]:
    query = db.query(Service)

    if enable >= 0:
        query = query.filter(Service.enable == (True if enable > 0 else False))

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
    if db_service:
        db_order = Order(
            user_id=db_user.id,
            account_id=None if db_account is None else db_account.id,
            service_id=db_service.id,
            host_zone_id=db_service.host_zone_id,
            status=order.status,
            duration=db_service.duration,
            data_limit=db_service.data_limit,
            ip_limit=db_service.ip_limit,
            total=db_service.price,
            total_discount_amount=db_service.discount,
        )
    else:
        db_order = Order(
            user_id=db_user.id,
            account_id=None if db_account is None else db_account.id,
            service_id=None,
            status=order.status,
            duration=order.duration,
            data_limit=order.data_limit,
            ip_limit=order.ip_limit,
            total=order.total,
            total_discount_amount=order.total_discount_amount,
        )

    _validate_order(db=db, db_user=db_user, db_order=db_order)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    _process_order(db=db, db_user=db_user, db_order=db_order, db_service=db_service)

    return db_order


def update_order(db: Session, db_order: Order, modify: OrderModify):
    db_user = user_service.get_user(db, db_order.user_id)
    db_service = get_service(db, db_order.service_id)

    _validate_order(db=db, db_user=db_user, db_order=db_order, modify=modify)

    db_order.status = modify.status
    db_order.account_id = modify.account_id
    db_order.duration = modify.duration
    db_order.data_limit = modify.data_limit
    db_order.ip_limit = modify.ip_limit
    db_order.total = modify.total
    db_order.total_discount_amount = modify.total_discount_amount

    db.commit()
    db.refresh(db_order)

    _process_order(db=db, db_user=db_user, db_order=db_order, db_service=db_service)

    return db_order


def update_order_status(
    db: Session,
    db_order: Order,
    status: OrderStatus,
    db_account: Optional[Account] = None,
):
    order_modify = OrderModify(
        user_id=db_order.user_id,
        account_id=db_order.account_id if db_account is None else db_account.id,
        service_id=db_order.service_id,
        duration=db_order.duration,
        data_limit=db_order.data_limit,
        total=db_order.total,
        total_discount_amount=db_order.total_discount_amount,
        status=status,
    )

    return update_order(db=db, db_order=db_order, modify=order_modify)


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
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
) -> Tuple[List[Order], int]:
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

    if end_date:
        query = query.filter(
            and_(
                Order.created_at <= end_date,
            )
        )

    if start_date:
        query = query.filter(
            and_(
                Order.created_at >= start_date,
            )
        )
    return _get_query_result(limit, offset, query, return_with_count, sort)


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def _process_order(db: Session, db_order: Order, db_user: User, db_service: Service):
    sub_total = db_order.total - db_order.total_discount_amount

    order_title = ""
    if db_service:
        order_title = db_service.name

    if db_order.status == OrderStatus.paid:
        transaction = TransactionCreate(
            user_id=db_user.id,
            description=messages.ORDER_PAID_DESCRIPTION.format(id=db_order.id),
            amount=-sub_total,
            type=TransactionType.order,
        )

        create_transaction(
            db, db_order=db_order, db_user=db_user, transaction=transaction
        )

        _send_notification(
            db=db,
            db_user=db_user,
            type_=NotificationType.order,
            message=messages.ORDER_PAID_NOTIFICATION.format(
                title=order_title, id=db_order.id
            ),
        )

    if db_order.status == OrderStatus.completed:
        _send_notification(
            db=db,
            db_user=db_user,
            type_=NotificationType.order,
            message=messages.ORDER_COMPLETE_NOTIFICATION.format(
                title=order_title, id=db_order.id
            ),
        )


def _validate_order(
    db: Session, db_user: User, db_order: Order, modify: Optional[OrderModify] = None
):
    if db_order.status in [OrderStatus.completed] or (
        modify
        and modify.status == OrderStatus.completed
        and db_order.status != OrderStatus.paid
    ):
        raise OrderStatusConflictError

    if db_order.status in [OrderStatus.completed, OrderStatus.canceled]:
        raise OrderNotEditableError

    if db_order.status in [OrderStatus.paid] and (
        modify and modify.status not in [OrderStatus.completed]
    ):
        raise OrderStatusConflictError

    if db_order.status in [OrderStatus.open, OrderStatus.pending]:
        open_orders, count_open = get_orders(
            db=db, user_id=db_user.id, status=OrderStatus.open
        )
        pending_orders, count_pending = get_orders(
            db=db, user_id=db_user.id, status=OrderStatus.pending
        )
        if (count_open > 0 and modify is None) or (
            modify and modify.status is OrderStatus.open and count_open > 0
        ):
            raise MaxOpenOrderError(count_open)

        if (count_pending > 0 and modify is None) or (
            modify and modify.status is OrderStatus.pending and count_pending > 0
        ):
            raise MaxPendingOrderError(count_pending)

    if (db_order.status == OrderStatus.paid and modify is None) or (
        modify and modify.status == OrderStatus.paid
    ):
        total = db_order.total - db_order.total_discount_amount

        if db_user.balance is None or db_user.balance < total:
            raise NoEnoughBalanceError(total=total)


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

    if db_payment.status == PaymentStatus.paid:
        try:
            process_payment(db=db, db_payment=db_payment, db_user=db_user)
        except Exception:
            db_payment.status = PaymentStatus.pending
            db.commit()
            db.refresh(db_payment)
            raise IntegrityError

    return db_payment


def update_payment(db: Session, db_payment: Payment, modify: PaymentModify):
    db_user = user_service.get_user(db=db, user_id=db_payment.user_id)

    _validate_payment(db_payment=db_payment)

    db_payment.status = modify.status
    db_payment.total = modify.total

    if db_payment.status == PaymentStatus.paid:
        try:
            process_payment(db=db, db_payment=db_payment, db_user=db_user)
        except Exception:
            db.rollback()
            raise IntegrityError
    else:
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
) -> Tuple[List[Payment], int]:
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


def process_payment(db: Session, db_payment: Payment, db_user: User):
    if db_payment.status == PaymentStatus.paid:
        transaction = TransactionCreate(
            user_id=db_user.id,
            description=messages.PAYMENT_PAID_DESCRIPTION.format(
                method=PAYMENT_METHODS[db_payment.method.value], id=db_payment.id
            ),
            amount=db_payment.total,
            type=TransactionType.payment,
        )

        create_transaction(
            db, db_payment=db_payment, db_user=db_user, transaction=transaction
        )


def _validate_payment(db_payment: Payment, payment: Optional[PaymentModify] = None):
    if db_payment.status == PaymentStatus.paid:
        raise PaymentPaidStatusError


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


def _send_notification(
    db, db_user: User, message: str, type_: NotificationType, level: int = 0
):
    create_notification(
        db=db,
        db_user=db_user,
        notification=NotificationCreate(
            approve=True,
            message=message,
            level=level,
            type=type_,
        ),
    )
