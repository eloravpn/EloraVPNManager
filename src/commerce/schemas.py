from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TransactionType(str, Enum):
    payment = "PAYMENT"
    order = "ORDER"
    bonus = "BONUS"


class PaymentMethod(str, Enum):
    money_order = "MONEY_ORDER"
    online = "ONLINE"
    cryptocurrencies = "CRYPTOCURRENCIES"


class PaymentStatus(str, Enum):
    pending = "PENDING"
    canceled = "CANCELED"
    paid = "PAID"


class OrderStatus(str, Enum):
    open = "OPEN"
    pending = "PENDING"
    canceled = "CANCELED"
    paid = "PAID"
    completed = "COMPLETED"


class TransactionBase(BaseModel):
    description: str
    user_id: int
    payment_id: Optional[int] = None
    order_id: Optional[int] = None
    amount: int
    type: TransactionType = TransactionType.payment


class TransactionCreate(TransactionBase):
    pass


class TransactionModify(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class TransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int


class PaymentBase(BaseModel):
    user_id: int
    order_id: Optional[int] = None
    total: int

    method: PaymentMethod = PaymentMethod.money_order
    status: PaymentStatus = PaymentStatus.pending


class PaymentCreate(PaymentBase):
    pass


class PaymentModify(PaymentBase):
    pass


class PaymentBase(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class PaymentsResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int


class OrderBase(BaseModel):
    user_id: int
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    duration: int = 1
    data_limit: int = 0
    total: int = 0
    total_discount_amount: int = 0

    status: OrderStatus = OrderStatus.open


class OrderCreate(OrderBase):
    pass


class OrderModify(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class OrdersResponse(BaseModel):
    orders: List[OrderResponse]
    total: int


class ServiceBase(BaseModel):
    name: str
    duration: int = 1
    data_limit: int = 0
    price: int = 0
    discount: int = 0
    enable: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceModify(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class ServicesResponse(BaseModel):
    services: List[ServiceResponse]
    total: int
