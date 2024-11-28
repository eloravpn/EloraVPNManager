import json
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from src.database import Base
from src.inbounds.schemas import (
    InboundSecurity,
    InboundType,
    InboundFingerPrint,
    InboundNetwork,
)


class InboundConfig(Base):
    __tablename__ = "inbound_config"

    id = Column(Integer, primary_key=True, index=True)
    inbound_id = Column(Integer, ForeignKey("inbound.id"), nullable=True)
    inbound = relationship("Inbound", back_populates="inbound_configs")
    remark = Column(String(128), index=True)
    port = Column(Integer, index=True)
    domain = Column(String(128), index=True)
    host = Column(String(128), index=True)
    sni = Column(String(128), index=True)
    address = Column(String(128), index=True)
    path = Column(String(400))
    pbk = Column(String(400))
    sid = Column(String(400))
    spx = Column(String(400))
    enable = Column(Boolean, default=True)
    develop = Column(Boolean, default=False)

    finger_print = Column(
        Enum(InboundFingerPrint),
        unique=False,
        nullable=False,
        default=InboundFingerPrint.default.value,
    )

    security = Column(
        Enum(InboundSecurity),
        unique=False,
        nullable=False,
        default=InboundSecurity.default.value,
    )

    network = Column(
        Enum(InboundNetwork),
        unique=False,
        nullable=False,
        default=InboundNetwork.ws.value,
    )

    alpn = Column(String(400))

    type = Column(Enum(InboundType), nullable=False, default=InboundType.default.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def alpns(self):
        """Deserialize JSON string into a Python list."""
        if self.alpn:
            try:
                return json.loads(self.alpn)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON stored in alpn: {self.alpn}. Error: {str(e)}")
        return None

    @alpns.setter
    def alpns(self, value):
        """Serialize a Python list into a JSON string for alpn."""
        if value is not None:
            # Ensure the list is in a correct format
            if isinstance(value, str):
                # If the value is a string like "{h2,h3}", convert it into a list
                value = [item.strip() for item in value.strip("{}").split(",")]

            try:
                self.alpn = json.dumps(value)  # Store as a valid JSON string
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid value for alpns: {value}. Error: {str(e)}")
        else:
            self.alpn = None  # Set to None if no value is provided