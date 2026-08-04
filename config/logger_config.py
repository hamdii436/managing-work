"""Logging configuration."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config.settings import get_settings

# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    global _logger

    settings = get_settings()
    log_dir = Path(settings.log_file_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("maps_automation")
    logger.setLevel(getattr(logging, settings.log_level.value))

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.log_max_size,
        backupCount=settings.log_backup_count,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # File handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=settings.log_max_size,
        backupCount=settings.log_backup_count,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level.value))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _logger = logger
    return logger


def get_logger(name: str = "maps_automation") -> logging.Logger:
    """Get logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return logging.getLogger(name)
