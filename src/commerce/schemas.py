from enum import Enum
from typing import List

from pydantic import BaseModel, root_validator, validator


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
    paid = "PAID"


class OrderStatus(str, Enum):
    open = "OPEN"
    pending = "PENDING"
    paid = "PAID"
    completed = "COMPLETED"


class Transaction(BaseModel):
    description: str
