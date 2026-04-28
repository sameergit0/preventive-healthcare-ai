from app.db import Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(1), nullable=False) 
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    profile_image = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="profile")
    
    __table_args__ = (
        CheckConstraint('age > 0', name='check_age_positive'),
        CheckConstraint('weight > 0', name='check_weight_positive'),
        CheckConstraint('height > 0', name='check_height_positive'),
        CheckConstraint("gender IN ('M', 'F')", name='check_gender_valid'),
    )