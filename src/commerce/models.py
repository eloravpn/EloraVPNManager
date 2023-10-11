from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Boolean,
    BigInteger,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from src.commerce.schemas import (
    PaymentMethod,
    TransactionType,
    PaymentStatus,
    OrderStatus,
)
from src.database import Base


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, index=True)

    # Relations

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="transactions")

    payment_id = Column(Integer, ForeignKey("payment.id"), nullable=True)
    payment = relationship("Payment", back_populates="transactions")

    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    order = relationship("Order", back_populates="transactions")

    description = Column(String(4000), nullable=True)

    amount = Column(BigInteger, default=0)

    type = Column(
        Enum(TransactionType), nullable=False, default=TransactionType.payment
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)

    # Relations

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="payments")

    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    order = relationship("Order", back_populates="payments")

    transactions = relationship("Transaction", back_populates="payment")

    method = Column(
        Enum(PaymentMethod), nullable=False, default=PaymentMethod.money_order
    )

    total = Column(BigInteger, default=0)

    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)

    # Relations

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="orders")

    account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
    account = relationship("Account", back_populates="orders")

    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)
    service = relationship("Service", back_populates="orders")

    payments = relationship("Payment", back_populates="order")

    transactions = relationship("Transaction", back_populates="order")

    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.open)

    duration = Column(Integer, default=1)
    data_limit = Column(BigInteger, nullable=True)

    total = Column(BigInteger, default=0)
    total_discount_amount = Column(BigInteger, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Service(Base):
    __tablename__ = "service"

    # Relations

    orders = relationship("Order", back_populates="service")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=True)

    duration = Column(Integer, default=1)
    data_limit = Column(BigInteger, nullable=True)
    price = Column(BigInteger, default=0)
    discount = Column(Integer, default=0)
    enable = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
