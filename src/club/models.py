from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from src.database import Base


class ClubProfile(Base):
    __tablename__ = "club_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True, unique=True)
    user = relationship("User", back_populates="club_profile")

    total_score = Column(Integer, default=0)
    total_subset = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)


class ClubScore(Base):
    __tablename__ = "club_score"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="club_scores")

    unique_id = Column(String(128), nullable=False, index=True)
    campaign_key = Column(String(128), nullable=False, index=True)
    score = Column(Integer, default=0)
    description = Column(String(4000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        Index("campaign_key_unique_id_idx", unique_id, campaign_key, unique=True),
    )
