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

load_dotenv()

H_ALGORITHM = os.getenv("H_ALGORITHM")
AK_SECRET_KEY = os.getenv("AK_SECRET_KEY")
AK_ALGORITHM = os.getenv("AK_ALGORITHM")
AK_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AK_ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=[H_ALGORITHM], deprecated='auto')

security = HTTPBearer()

def hash_password(plain_password: str):
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=AK_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, AK_SECRET_KEY, algorithm=AK_ALGORITHM)    
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
): 
    try:
        payload = jwt.decode(credentials.credentials, AK_SECRET_KEY, algorithms=[AK_ALGORITHM])
        user_id = int(payload.get("uid"))
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    return user