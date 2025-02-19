from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr

from src.accounts.schemas import AccountResponse
from src.hosts.schemas import HostZoneResponse
from src.users.schemas import UserResponse


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
    user_id: Optional[int] = None
    payment_id: Optional[int] = None
    order_id: Optional[int] = None
    payment_account_id: Optional[int] = None
    amount: int
    type: TransactionType = TransactionType.payment

    @property
    def amount_readable(self):
        if self.amount:
            return f"{self.amount:,}"
        else:
            return 0


class TransactionCreate(TransactionBase):
    pass


class TransactionModify(TransactionBase):
    pass


class PaymentBase(BaseModel):
    user_id: Optional[int] = None
    order_id: Optional[int] = None
    payment_account_id: Optional[int] = None
    paid_at: Optional[datetime] = datetime.utcnow()
    verify: Optional[bool] = True
    total: int

    method: PaymentMethod = PaymentMethod.money_order
    status: PaymentStatus = PaymentStatus.pending


class PaymentCreate(PaymentBase):
    pass


class PaymentModify(PaymentBase):
    pass


class PaymentBase(PaymentBase):
    pass


class ServiceBase(BaseModel):
    host_zone_ids: Optional[List[int]] = None
    name: str
    duration: int = 1
    data_limit: int = 0
    ip_limit: Optional[int] = 0
    price: int = 0
    discount: int = 0
    enable: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceModify(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: int
    host_zones: Optional[List[HostZoneResponse]]
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class ServicesResponse(BaseModel):
    services: List[ServiceResponse]
    total: int


class OrderBase(BaseModel):
    user_id: Optional[int] = None
    account_id: Optional[int] = None
    service_id: Optional[int] = None
    duration: Optional[int] = None
    data_limit: Optional[int] = None
    ip_limit: Optional[int] = 0
    total: Optional[int] = None
    total_discount_amount: Optional[int] = None

    status: OrderStatus = OrderStatus.open


class OrderCreate(OrderBase):
    extra_discount: Optional[int] = 0
    is_debt: Optional[bool] = False
    pass


class OrderModify(OrderBase):
    extra_discount: Optional[int] = 0
    is_debt: Optional[bool] = False
    pass


class OrderResponse(OrderBase):
    id: int
    user: Optional[UserResponse]
    account: Optional[AccountResponse]
    service: Optional[ServiceResponse]
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class TransactionResponse(TransactionBase):
    id: int
    user: Optional[UserResponse]
    order: Optional[OrderResponse]
    service: Optional[ServiceResponse]
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class PaymentResponse(PaymentBase):
    id: int
    user: Optional[UserResponse]
    order: Optional[OrderResponse]
    created_at: datetime
    modified_at: datetime

    def dict(cls, *args, **kwargs):
        return super().dict(*args, **kwargs)

    class Config:
        orm_mode = True


class TransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int


class OrdersResponse(BaseModel):
    orders: List[OrderResponse]
    total: int


class PaymentsResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int


class PaymentAccountBase(BaseModel):
    card_number: constr(min_length=16, max_length=16)
    account_number: constr(max_length=128)
    bank_name: Optional[str]
    shaba: Optional[str]
    owner_name: str
    owner_family: str
    enable: bool = True
    min_payment_for_bot: int = 0
    max_daily_transactions: int = 100
    max_daily_amount: int = 1000000000
    min_payment_amount: int = 0
    user_id: Optional[int] = None
    payment_notice: Optional[str] = None


class PaymentAccountCreate(PaymentAccountBase):
    pass


class PaymentAccountModify(PaymentAccountBase):
    pass


class PaymentAccountResponse(PaymentAccountBase):
    id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


class PaymentAccountsResponse(BaseModel):
    payment_accounts: List[PaymentAccountResponse]
    total: int


TransactionResponse.update_forward_refs()
PaymentResponse.update_forward_refs()
OrdersResponse.update_forward_refs()
