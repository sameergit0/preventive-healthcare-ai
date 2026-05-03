import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables for logging configuration
load_dotenv()

# Directory where log files will be stored
LOG_DIR = os.getenv("LOG_DIR", "logs")

def setup_logging():
    """
    Initialize the global logging configuration for the application.
    - Creates a 'logs' directory if it doesn't exist.
    - Sets up a daily log file (e.g., app_20240502.log).
    - Configures both File and Stream (Console) handlers.
    - Suppresses noisy logs from third-party libraries.
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    # Generate log filename based on the current date
    log_filename = f"{LOG_DIR}/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Suppress verbose logs from noisy third-party libraries
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename), # Save logs to file
            logging.StreamHandler()            # Print logs to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Current log file: {log_filename}")
    
    return logger, log_filename

def get_logger(name: str):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: The __name__ of the calling module.
    """
    return logging.getLogger(name)