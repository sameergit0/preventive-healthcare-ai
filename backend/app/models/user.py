from app.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    
    timezone = Column(String(50), default="UTC", nullable=False)
    
    profile = relationship("Profile", back_populates="user", uselist=False)
    health_metrics = relationship("HealthMetric", back_populates="user")