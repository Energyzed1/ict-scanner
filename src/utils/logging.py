"""
Logging configuration utility
"""

import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger

def setup_logging(config: Dict[str, Any]) -> None:
    """
    Configure logging with loguru
    
    Args:
        config: Logging configuration
    """
    # Remove default handler
    logger.remove()
    
    # Get configuration
    log_level = config.get("level", "INFO").upper()
    log_file = config.get("file", "logs/scanner.log")
    max_size = config.get("max_size_mb", 100) * 1024 * 1024  # Convert to bytes
    backup_count = config.get("backup_count", 5)
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        log_file,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        level=log_level,
        rotation=f"{max_size} bytes",
        retention=backup_count,
        compression="zip"
    )
    
    logger.info(f"Logging configured with level {log_level}")
    
def get_logger(name: str):
    """
    Get a logger instance with the given name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name) 