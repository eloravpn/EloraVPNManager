from datetime import datetime

from sqlalchemy import Column, String, DateTime

from src.database import Base


class ConfigSetting(Base):
    """Database model for storing configuration values"""

    __tablename__ = "config_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=True)
    value_type = Column(String)  # Store the type of value for proper casting
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ConfigSetting {self.key}={self.value} ({self.value_type})>"
