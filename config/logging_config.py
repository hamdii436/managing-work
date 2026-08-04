"""Logging configuration and setup."""

import json
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from config.settings import get_settings
from core.enums import LogLevel


def _get_format_string(is_json: bool = False) -> str:
    """Get log format string."""
    if is_json:
        return '%(message)s'
    return '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def _create_json_formatter() -> logging.Formatter:
    """Create JSON formatter for structured logging."""
    
    class JSONFormatter(logging.Formatter):
        """Custom JSON formatter."""
        
        def format(self, record: logging.LogRecord) -> str:
            """Format record as JSON."""
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            return json.dumps(log_data)
    
    return JSONFormatter()


def setup_logging() -> None:
    """Setup logging configuration based on settings."""
    settings = get_settings()
    
    # Get logging configuration
    log_level = settings.log_level
    log_file_path = Path(settings.log_file_path)
    log_file_path.mkdir(parents=True, exist_ok=True)
    
    is_json = settings.log_format == 'json'
    format_string = _get_format_string(is_json)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.value)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    if is_json:
        formatter = _create_json_formatter()
    else:
        formatter = logging.Formatter(format_string)
    
    # Console handler
    if settings.log_console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level.value)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_file_path / 'application.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=settings.log_max_size,
        backupCount=settings.log_backup_count,
        encoding='utf-8',
    )
    file_handler.setLevel(log_level.value)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file handler
    error_log_file = log_file_path / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=settings.log_max_size,
        backupCount=settings.log_backup_count,
        encoding='utf-8',
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    root_logger.info(f"Logging initialized - Level: {log_level.value}, Format: {settings.log_format}")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module."""
    return logging.getLogger(name)


def set_log_level(level: LogLevel) -> None:
    """Change log level at runtime."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level.value)
    for handler in root_logger.handlers:
        handler.setLevel(level.value)
    logging.getLogger(__name__).info(f"Log level changed to {level.value}")


def get_log_level() -> LogLevel:
    """Get current log level."""
    root_logger = logging.getLogger()
    return LogLevel(root_logger.level)


def get_log_file_path() -> Path:
    """Get path to log file."""
    settings = get_settings()
    return Path(settings.log_file_path) / 'application.log'


def get_error_log_file_path() -> Path:
    """Get path to error log file."""
    settings = get_settings()
    return Path(settings.log_file_path) / 'errors.log'


def clear_logs() -> None:
    """Clear log files."""
    log_dir = Path(get_settings().log_file_path)
    for log_file in log_dir.glob('*.log*'):
        try:
            log_file.unlink()
        except Exception as e:
            logging.error(f"Could not delete log file {log_file}: {e}")


# Setup logging on module import
setup_logging()
