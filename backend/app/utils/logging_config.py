import os
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.getenv("LOG_DIR", "logs")

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    log_filename = f"{LOG_DIR}/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__), log_filename

def get_logger(name: str):
    return logging.getLogger(name)