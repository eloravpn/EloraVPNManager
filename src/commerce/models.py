import math
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
    Table,
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

    payment_account_id = Column(
        Integer, ForeignKey("payment_account.id"), nullable=True
    )
    payment_account = relationship("PaymentAccount", back_populates="transactions")

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

    payment_account_id = Column(
        Integer, ForeignKey("payment_account.id"), nullable=True
    )
    payment_account = relationship("PaymentAccount", back_populates="payments")

    transactions = relationship("Transaction", back_populates="payment")

    method = Column(
        Enum(PaymentMethod), nullable=False, default=PaymentMethod.money_order
    )

    total = Column(BigInteger, default=0)

    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    verify = Column(Boolean, default=True, nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)

    # Relations

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="orders")

    host_zone_id = Column(
        Integer, ForeignKey("host_zone.id"), nullable=False, server_default=str(1)
    )
    host_zone = relationship("HostZone", back_populates="orders")

    account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
    account = relationship("Account", back_populates="orders")

    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)
    service = relationship("Service", back_populates="orders")

    payments = relationship("Payment", back_populates="order")

    transactions = relationship("Transaction", back_populates="order")

    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.open)

    ip_limit = Column(Integer, default=0)
    duration = Column(Integer, default=1)
    data_limit = Column(BigInteger, nullable=True)

    total = Column(BigInteger, default=0)
    total_discount_amount = Column(BigInteger, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


service_host_zone = Table(
    "service_host_zone",
    Base.metadata,
    Column("service_id", ForeignKey("service.id"), primary_key=True),
    Column("host_zone_id", ForeignKey("host_zone.id"), primary_key=True),
)


class Service(Base):
    __tablename__ = "service"

    # Relations

    orders = relationship("Order", back_populates="service")

    host_zones = relationship(
        "HostZone", secondary=service_host_zone, back_populates="services"
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=True)

    duration = Column(Integer, default=1)
    data_limit = Column(BigInteger, nullable=True)
    ip_limit = Column(Integer, default=0)
    price = Column(BigInteger, default=0)
    discount = Column(Integer, default=0)
    enable = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def price_readable(self):
        if self.price and self.discount:
            return f"<del>{self.price :,}</del> {self.price - self.discount :,}"
        elif self.price:
            return f"{self.price :,}"
        else:
            return 0

    @property
    def price_readable_plain(self):
        if self.price and self.discount:
            return f"{self.price - self.discount :,}"
        elif self.price:
            return f"{self.price :,}"
        else:
            return 0

    @property
    def discount_percent(self):
        if self.price and self.discount:
            percent = math.ceil((self.discount / self.price) * 100)
            return percent
        else:
            return 0


class PaymentAccount(Base):
    __tablename__ = "payment_account"
    id = Column(Integer, primary_key=True, index=True)

    # Relations
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="payment_accounts")

    # Account info
    card_number = Column(String(16), unique=True, index=True)
    account_number = Column(String(128), unique=True, index=True)
    bank_name = Column(String(128), unique=True, index=True)
    shaba = Column(String(128), unique=True, index=True)
    owner_name = Column(String(128))
    payment_notice = Column(String(300))
    owner_family = Column(String(128))

    # Settings
    enable = Column(Boolean, default=True)
    min_payment_for_bot = Column(BigInteger, default=0)
    min_payment_amount = Column(BigInteger, default=0)
    max_daily_transactions = Column(Integer, default=100)
    max_daily_amount = Column(BigInteger, default=1000000000)  # 1B default limit

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = relationship("Payment", back_populates="payment_account")
    transactions = relationship("Transaction", back_populates="payment_account")
