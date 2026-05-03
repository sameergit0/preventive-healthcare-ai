from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from app.db import Base

class Lifestyle(Base):
    __tablename__ = "lifestyles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    tobacco_type= Column(
        Enum("never", "daily", "weekly", "occasionally", "former", name="tobacco_type_enum"), 
        nullable=True
    )
    passive_smoke = Column(Boolean, nullable=True)
    
    alcohol_freq = Column(
        Enum("never","rarely", "sometimes", "often", "daily", name="alcohol_freq_enum"), 
        nullable=True
    )
    alcohol_binge = Column(Boolean, nullable=True)
    
    stress_level = Column(Integer, nullable=True)
    work_life_balance = Column(Integer, nullable=True)
    screen_time_hours = Column(Float, nullable=True)

    user = relationship("User", back_populates="lifestyle")

    __table_args__ = (
        CheckConstraint("stress_level BETWEEN 1 AND 5", name="check_stress"),
        CheckConstraint("work_life_balance BETWEEN 1 AND 5", name="check_work_life"),
        CheckConstraint("screen_time_hours >= 0 AND screen_time_hours <= 24", name="check_screen"),
    )