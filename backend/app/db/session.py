from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables for database configuration
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine for database connection
# pool_pre_ping=True enables connection health checking
engine = create_engine(url=DATABASE_URL, pool_pre_ping=True)

# Session factory
sessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
