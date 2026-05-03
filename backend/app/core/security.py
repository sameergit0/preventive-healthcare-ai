from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
import jwt
from app.api.deps import get_db
import os
from dotenv import load_dotenv

# Load environment variables for security configuration
load_dotenv()

# Security Configuration
H_ALGORITHM = os.getenv("H_ALGORITHM")
AK_SECRET_KEY = os.getenv("AK_SECRET_KEY")
AK_ALGORITHM = os.getenv("AK_ALGORITHM")
AK_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AK_ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password hashing context using the algorithm defined in .env (e.g., bcrypt)
pwd_context = CryptContext(schemes=[H_ALGORITHM], deprecated='auto')

# HTTP Bearer scheme for token-based authentication
security = HTTPBearer()

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password for secure storage in the database.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Generate a new JWT access token with an expiration timestamp.
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=AK_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode and return the JWT
    encoded_jwt = jwt.encode(to_encode, AK_SECRET_KEY, algorithm=AK_ALGORITHM)    
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to retrieve and validate the current user from a Bearer token.
    
    - Decodes the JWT token.
    - Extracts the user ID (uid).
    - Verifies the user exists in the database.
    
    Raises:
        HTTP_401_UNAUTHORIZED: If the token is invalid, expired, or user not found.
    """
    try:
        # Decode the token
        payload = jwt.decode(credentials.credentials, AK_SECRET_KEY, algorithms=[AK_ALGORITHM])
        user_id = int(payload.get("uid"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token payload: missing user ID."
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials: token may be expired or tampered."
        )
        
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication failed: user no longer exists."
        )

    return user