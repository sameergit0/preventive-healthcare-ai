from app.schemas import UserCreate, UserLogin, MessageResponse, TokenResponse, UserResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db
from app.models import User
from app.core import hash_password, verify_password, create_access_token, get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/signup", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MessageResponse, 
    summary="Register a new user"
)
def signup(
    user: UserCreate, 
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Register a new user with email, password, and timezone.
    
    - **email**: Must be a valid email format
    - **password**: Between 8-64 characters
    - **timezone**: Valid IANA timezone (e.g., Asia/Kolkata)
    """
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email already registered"
        )
        
    try:
        hashed_password = hash_password(plain_password=user.password)
        new_user = User(
            email=user.email.lower(),  
            hash_password=hashed_password, 
            timezone=user.timezone
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user created successfully: {new_user.email} (ID: {new_user.id}, Timezone: {new_user.timezone})")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during signup for {user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during user creation"
        )
    
    return MessageResponse(message="User created successfully")  

@router.post(
    "/login", 
    status_code=status.HTTP_200_OK, 
    response_model=TokenResponse, 
    summary="Authenticate user"
)
def login(
    user: UserLogin, 
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return access token.
    
    - **email**: Registered email address
    - **password**: User's password
    """
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if not existing_user:
        logger.warning(f"Login failed - User not found: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
        
    if not verify_password(plain_password=user.password, hashed_password=existing_user.hash_password):
        logger.warning(f"Login failed - Invalid password for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(
        data={"sub": existing_user.email, "uid": existing_user.id}
    )
    
    logger.info(f"User logged in successfully: {existing_user.email} (ID: {existing_user.id})")
    
    return TokenResponse(
        message="User logged in successfully",
        access_token=access_token,
        token_type="bearer"
    )  

@router.get(
    "/me", 
    status_code=status.HTTP_200_OK, 
    response_model=UserResponse,
    summary="Get current user details"
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get details of the currently authenticated user.
    
    Returns user information including ID, email, and timezone.
    """
    
    logger.debug(f"User profile accessed: {current_user.email} (ID: {current_user.id})")
    
    return current_user