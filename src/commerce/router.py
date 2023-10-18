import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.accounts.service as account_service
import src.commerce.service as commerce_service
import src.users.service as user_service
from src.admins.schemas import Admin
from src.commerce.exc import MaxPendingOrderError
from src.commerce.models import Order, Payment
from src.commerce.schemas import (
    OrderResponse,
    OrderCreate,
    OrderModify,
    OrdersResponse,
    OrderStatus,
    ServicesResponse,
    ServiceResponse,
    ServiceCreate,
    ServiceModify,
    PaymentResponse,
    PaymentCreate,
    PaymentModify,
    PaymentsResponse,
    PaymentStatus,
    PaymentMethod,
    TransactionResponse,
    TransactionCreate,
    TransactionModify,
    TransactionsResponse,
    TransactionType,
)
from src.database import get_db
from src.exc import EloraApplicationError

order_router = APIRouter()
service_router = APIRouter()
payment_router = APIRouter()
transaction_router = APIRouter()

logger = logging.getLogger("uvicorn.error")

# Order Routes


@order_router.post("/orders/", tags=["Order"], response_model=OrderResponse)
def add_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, order.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_service = None
    db_account = None

    if order.account_id > 0:
        db_account = account_service.get_account(db=db, account_id=order.account_id)

        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

    if order.service_id > 0:
        db_service = commerce_service.get_service(db=db, service_id=order.service_id)

        if not db_service:
            raise HTTPException(status_code=404, detail="Service not found")

    try:
        db_order = commerce_service.create_order(
            db=db,
            db_user=db_user,
            db_service=db_service if db_service else None,
            db_account=db_account if db_account else None,
            order=order,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Order already exists")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())

    return db_order


@order_router.put("/orders/{order_id}", tags=["Order"], response_model=OrderResponse)
def modify_order(
    order_id: int,
    order: OrderModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_order = commerce_service.get_order(db, order_id=order_id)

    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        db_order = commerce_service.update_order(db=db, db_order=db_order, modify=order)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Order already exists")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())

    return db_order


@order_router.get("/orders/{order_id}", tags=["Order"], response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_order = commerce_service.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    return db_order


@order_router.delete("/orders/{order_id}", tags=["Order"])
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_order = commerce_service.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    commerce_service.remove_order(db=db, db_order=db_order)
    return {}


@order_router.get("/orders/", tags=["Order"], response_model=OrdersResponse)
def get_orders(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    status: OrderStatus = None,
    account_id: int = 0,
    user_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(commerce_service.OrderSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    orders, count = commerce_service.get_orders(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        status=status,
        account_id=account_id,
        user_id=user_id,
        q=q,
    )

    return {"orders": orders, "total": count}


# Service Routes


@service_router.post("/services/", tags=["Service"], response_model=ServiceResponse)
def add_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    try:
        db_service = commerce_service.create_service(
            db=db,
            service=service,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Service already exists")

    return db_service


@service_router.put(
    "/services/{service_id}", tags=["Service"], response_model=ServiceResponse
)
def modify_service(
    service_id: int,
    service: ServiceModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_service = commerce_service.get_service(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    return commerce_service.update_service(db=db, db_service=db_service, modify=service)


@service_router.get(
    "/services/{service_id}", tags=["Service"], response_model=ServiceResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_service = commerce_service.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    return db_service


@service_router.delete("/services/{service_id}", tags=["Service"])
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_service = commerce_service.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    commerce_service.remove_service(db=db, db_service=db_service)
    return {}


@service_router.get("/services/", tags=["Service"], response_model=ServicesResponse)
def get_services(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(commerce_service.ServiceSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    services, count = commerce_service.get_services(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        q=q,
    )

    return {"services": services, "total": count}


# Payment Routes


@payment_router.post("/payments/", tags=["Payment"], response_model=PaymentResponse)
def add_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, payment.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_order: Order = None

    if payment.order_id > 0:
        db_order = commerce_service.get_order(db=db, order_id=payment.order_id)

        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

    try:
        db_payment = commerce_service.create_payment(
            db=db,
            db_user=db_user,
            db_order=db_order if db_order else None,
            payment=payment,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Payment already exists")

    return db_payment


@payment_router.put(
    "/payments/{payment_id}", tags=["Payment"], response_model=PaymentResponse
)
def modify_payment(
    payment_id: int,
    payment: PaymentModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_payment = commerce_service.get_payment(db, payment_id=payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    try:
        db_payment = commerce_service.update_payment(
            db=db, db_payment=db_payment, modify=payment
        )
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Error on update payment")

    return db_payment


@payment_router.get(
    "/payments/{payment_id}", tags=["Payment"], response_model=PaymentResponse
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_payment = commerce_service.get_payment(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return db_payment


@payment_router.delete("/payments/{payment_id}", tags=["Payment"])
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_payment = commerce_service.get_payment(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    commerce_service.remove_payment(db=db, db_payment=db_payment)
    return {}


@payment_router.get("/payments/", tags=["Payment"], response_model=PaymentsResponse)
def get_payments(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    status: PaymentStatus = None,
    method: PaymentMethod = None,
    user_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(commerce_service.PaymentSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    payments, count = commerce_service.get_payments(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        status=status,
        method=method,
        user_id=user_id,
        q=q,
    )

    return {"payments": payments, "total": count}


# Transaction Routes


@transaction_router.post(
    "/transactions/", tags=["Transaction"], response_model=TransactionResponse
)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, transaction.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_order: Order = None
    db_payment: Payment = None

    if transaction.order_id > 0:
        db_order = commerce_service.get_order(db=db, order_id=transaction.order_id)

        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

    if transaction.payment_id > 0:
        db_payment = commerce_service.get_payment(db, payment_id=transaction.payment_id)

        if not db_payment:
            raise HTTPException(status_code=404, detail="Payment not found")

    try:
        db_transaction = commerce_service.create_transaction(
            db=db,
            db_user=db_user,
            db_order=db_order if db_order else None,
            db_payment=db_payment if db_payment else None,
            transaction=transaction,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Transaction already exists")

    return db_transaction


# TODO
# @transaction_router.put(
#     "/transactions/{transaction_id}",
#     tags=["Transaction"],
#     response_model=TransactionResponse,
# )
# def modify_transaction(
#     transaction_id: int,
#     transaction: TransactionModify,
#     db: Session = Depends(get_db),
#     admin: Admin = Depends(Admin.get_current),
# ):
#     db_transaction = commerce_service.get_transaction(db, transaction_id=transaction_id)
#     if not db_transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")
#
#     return commerce_service.update_transaction(
#         db=db, db_transaction=db_transaction, modify=transaction
#     )


@transaction_router.get(
    "/transactions/{transaction_id}",
    tags=["Transaction"],
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_transaction = commerce_service.get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return db_transaction


@transaction_router.delete("/transactions/{transaction_id}", tags=["Transaction"])
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_transaction = commerce_service.get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db_user = user_service.get_user(db, db_transaction.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    commerce_service.remove_transaction(
        db=db, db_user=db_user, db_transaction=db_transaction
    )
    return {}


@transaction_router.get(
    "/transactions/", tags=["Transaction"], response_model=TransactionsResponse
)
def get_transactions(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    type_: TransactionType = None,
    user_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(commerce_service.TransactionSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    transactions, count = commerce_service.get_transactions(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        type_=type_,
        user_id=user_id,
        q=q,
    )

    return {"transactions": transactions, "total": count}
