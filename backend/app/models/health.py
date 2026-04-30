from app.db import Base
from sqlalchemy import (
    Column, String, Integer, JSON, Float, ForeignKey, DateTime, func, 
    Date, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    steps = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    water_intake = Column(Float, nullable=True)
    food_log = Column(MutableList.as_mutable(JSON), default=lambda: [], nullable=False)

    sleep_quality = Column(String, nullable=True)

    activity_minutes = Column(Integer, nullable=True)
    sedentary_minutes = Column(Integer, nullable=True)
    
    nutrition_sugar = Column(Float, nullable=True)
    nutrition_fruits = Column(Integer, nullable=True)
    
    log_date = Column(Date, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="health_metrics")
    
    __table_args__ = (
        Index("idx_user_log_date", "user_id", "log_date"),
        UniqueConstraint("user_id", "log_date", name="uq_user_daily_log"),

        CheckConstraint("steps >= 0 AND steps <= 100000", name="check_steps_range"),
        CheckConstraint("sleep_hours >= 0 AND sleep_hours <= 24", name="check_sleep_range"),
        CheckConstraint("water_intake >= 0 AND water_intake <= 10", name="check_water_range"),
        CheckConstraint("activity_minutes >= 0 AND activity_minutes <= 1440", name="check_activity_range"),
        CheckConstraint("sedentary_minutes >= 0 AND sedentary_minutes <= 1440", name="check_sedentary_range"),
        CheckConstraint("nutrition_sugar >= 0 AND nutrition_sugar <= 500", name="check_sugar_range"),
        CheckConstraint("nutrition_fruits >= 0 AND nutrition_fruits <= 20", name="check_fruits_range"),
        CheckConstraint(
            "sleep_quality IN ('poor','average','good','excellent')",
            name="check_sleep_quality"
        )
    )