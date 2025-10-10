"""
Logger Configuration
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from config.settings import Settings


def setup_logger(
    name: str = __name__,
    log_file: str = None,
    level: str = None
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        log_file: Log file path (uses default if None)
        level: Log level (uses Settings.LOG_LEVEL if None)
    
    Returns:
        logging.Logger: Configured logger
    """
    # Get log level
    level = level or Settings.LOG_LEVEL
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter if not Settings.DEBUG else detailed_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = Settings.LOGS_DIR / 'app.log'
    
    # Ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """Get or create logger with default settings"""
    return setup_logger(name)


# Setup root logger
root_logger = setup_logger('attendance_system')
