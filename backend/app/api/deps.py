from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import sessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session to the API endpoints.
    
    This ensures that:
    1. A new session is created for each request.
    2. The session is automatically closed after the request is finished,
       even if an error occurs.
    """
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()