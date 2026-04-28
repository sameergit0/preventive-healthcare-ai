from app.db import Base
from sqlalchemy import Column, Integer, JSON, Float, ForeignKey, DateTime, func, Date, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    steps = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    water_intake = Column(Float, nullable=True)
    food_log = Column(MutableList.as_mutable(JSON), default=[], nullable=False)
    
    log_date = Column(Date, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="health_metrics")
    
    __table_args__ = (
        Index("idx_user_log_date", "user_id", "log_date"),
        UniqueConstraint("user_id", "log_date", name="uq_user_daily_log")
    )