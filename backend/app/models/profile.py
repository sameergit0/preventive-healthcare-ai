from app.db import Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    full_name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Enum('M', 'F', name='gender_enum'), nullable=True) 

    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)

    goal = Column(
        Enum(
            'Weight Loss', 
            'Weight Gain', 
            'Muscle Building', 
            'Maintain Fitness', 
            'Improve Sleep', 
            'Reduce Stress',
            name='health_goal_enum'
        ), 
        nullable=True
    )
    profile_image = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="profile")
    
    __table_args__ = (
        CheckConstraint('age > 0 AND age < 120', name='check_age_range'),
        CheckConstraint('weight > 20 AND weight < 300', name='check_weight_range'),
        CheckConstraint('height > 50 AND height < 250', name='check_height_range'),
        CheckConstraint('waist_cm > 30 AND waist_cm < 200', name='check_waist_cm_range')
    )