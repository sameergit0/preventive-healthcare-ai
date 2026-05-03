from app.schemas import UserCreate, UserLogin, MessageResponse, TokenResponse, UserResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db
from app.models import User
from app.core import hash_password, verify_password, create_access_token, get_current_user
from app.utils import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/signup", 
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse, 
    summary="Register New User",
    description="Creates a new user account with a unique email and secure password. Requires a valid IANA timezone."
)
def signup(
    user: UserCreate, 
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Handle new user registration.
    
    1. Validates that the email is not already in use.
    2. Hashes the password using a secure algorithm.
    3. Saves the user record to the database.
    """
    
    # Check for existing user
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Signup conflict: Email {user.email} is already registered.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="This email address is already associated with an account."
        )

    # Hash password and create user instance
    hashed_password = hash_password(plain_password=user.password)
    new_user = User(
        **user.model_dump(exclude={"password"}),
        hash_password=hashed_password
    )
        
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registration successful: {new_user.email} (ID: {new_user.id})")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create user {user.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred while creating your account. Please try again later."
        )
    
    return MessageResponse(message="Account created successfully! You can now log in.")  

@router.post(
    "/login", 
    status_code=status.HTTP_200_OK, 
    response_model=TokenResponse, 
    summary="User Login",
    description="Authenticates a user with email and password, returning a JWT access token if successful."
)
def login(
    user: UserLogin, 
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and issue a secure access token.
    
    1. Verifies the user exists in the database.
    2. Validates the provided password against the stored hash.
    3. Generates a JWT token containing the user's email and ID.
    """
    
    # Locate user by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user:
        logger.warning(f"Login failed: User not found for email {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="The email or password you entered is incorrect."
        )
        
    # Verify security credentials
    if not verify_password(plain_password=user.password, hashed_password=existing_user.hash_password):
        logger.warning(f"Login failed: Invalid password provided for user {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="The email or password you entered is incorrect."
        )
    
    # Create secure JWT access token
    access_token = create_access_token(
        data={"sub": existing_user.email, "uid": existing_user.id}
    )
    
    logger.info(f"User login successful: {existing_user.email} (ID: {existing_user.id})")
    
    return TokenResponse(
        message="Login successful! Welcome back.",
        access_token=access_token,
        token_type="bearer"
    )  

@router.get(
    "/me", 
    status_code=status.HTTP_200_OK, 
    response_model=UserResponse,
    summary="Get Current User",
    description="Returns the profile details of the currently authenticated user based on the provided access token."
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Retrieve the current user's account information.
    
    This endpoint requires a valid JWT access token in the Authorization header.
    It returns core user details like ID, email, and timezone.
    """
    
    logger.debug(f"Authorized profile access: {current_user.email} (ID: {current_user.id})")
    
    return current_user