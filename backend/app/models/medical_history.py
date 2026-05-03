from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    diabetes = Column(Boolean, nullable=True)
    bp = Column(Boolean, nullable=True)
    high_cholesterol = Column(Boolean, nullable=True)
    heart_disease = Column(Boolean, nullable=True)
    asthma = Column(Boolean, nullable=True)

    user = relationship("User", back_populates="medical_history")