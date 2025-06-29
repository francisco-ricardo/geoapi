"""
Logging configuration for the GeoSpatial Links API.

This module provides a structured logging setup with support for:
- Console logging with readable formatting for development
- JSON formatting for production (cloud-friendly)
- Correlation IDs for request tracing
- Log level configuration via environment variables
- Integration with observability platforms

Usage:
    from app.core.logging import logger
    
    logger.info("Processing request", extra={"request_id": request_id})
    
    try:
        # Some operation
        logger.debug("Operation details", extra={"operation_data": data})
    except Exception as e:
        logger.exception("Operation failed", extra={"error_code": 500})
"""

import logging
import sys
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union

from functools import lru_cache

# Try to import settings, but handle case where it's not available yet
try:
    from app.core.config import get_settings
    settings = get_settings()
except (ImportError, ModuleNotFoundError):
    settings = None

# Log levels
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Define custom log format for structured logging
class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    
    This formatter is particularly useful for cloud environments and 
    observability platforms that consume structured logs.
    """
    
    def __init__(self, **kwargs):
        self.json_default = kwargs.pop("json_default", str)
        self.json_encoder = kwargs.pop("json_encoder", json.JSONEncoder)
        self.json_indent = kwargs.pop("json_indent", None)
        self.json_separators = kwargs.pop("json_separators", None)
        self.reserved_keys = kwargs.pop("reserved_keys", None) or []
        self.timestamp_field = kwargs.pop("timestamp_field", "timestamp")
        super().__init__(**kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_dict = {}
        
        # Add timestamp
        log_dict[self.timestamp_field] = datetime.utcnow().isoformat() + "Z"
        
        # Standard log record attributes
        log_dict["level"] = record.levelname
        log_dict["message"] = record.getMessage()
        log_dict["logger"] = record.name
        
        # Add location info
        log_dict["location"] = {
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Include exception info if present
        if record.exc_info:
            exc_type = record.exc_info[0]
            exc_value = record.exc_info[1]
            if exc_type and exc_value:
                log_dict["exception"] = {
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "traceback": self.formatException(record.exc_info),
                }
        
        # Include any extra attributes passed via extra parameter
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and key not in self.reserved_keys:
                log_dict[key] = value
        
        return json.dumps(log_dict, 
                          default=self.json_default,
                          cls=self.json_encoder,
                          indent=self.json_indent,
                          separators=self.json_separators)


class ConsoleFormatter(logging.Formatter):
    """
    Formatter for console output with color support.
    
    Designed for readability during development.
    """
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[31;1m' # Bold Red
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color for console output."""
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{log_message}{self.RESET}"


class ContextLogger(logging.Logger):
    """
    Logger that supports context and correlation IDs.
    
    Enhances tracking of requests through the system for observability.
    """
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self._context = {}
    
    def with_correlation_id(self, correlation_id: Optional[str] = None) -> "ContextLogger":
        """
        Create a logger instance with a correlation ID.
        
        Args:
            correlation_id: Optional correlation ID. If not provided, a new UUID will be generated.
            
        Returns:
            Logger instance with correlation ID context
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        return self.with_context({"correlation_id": correlation_id})
    
    def with_context(self, context: Dict[str, Any]) -> "ContextLogger":
        """
        Create a logger instance with additional context.
        
        Args:
            context: Dictionary of context values to include in all log records
            
        Returns:
            Logger instance with added context
        """
        logger_copy = self.__class__(self.name, self.level)
        for handler in self.handlers:
            logger_copy.addHandler(handler)
        
        logger_copy._context = {**self._context, **context}
        return logger_copy
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        """Override _log to include context in all log records."""
        if extra is None:
            extra = {}
        
        if self._context:
            extra.update(self._context)
            
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1, **kwargs)


# Register custom logger class
logging.setLoggerClass(ContextLogger)


def ensure_log_directory(log_file_path: str) -> None:
    """
    Ensure the directory for a log file exists.
    
    Args:
        log_file_path: Path to the log file
    """
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            # Fall back to a directory we know exists
            print(f"Warning: Could not create log directory {log_dir}: {e}")


@lru_cache(maxsize=1)
def get_logger(name: str = "geoapi", log_level: str = "INFO") -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL_MAP.get(log_level, logging.INFO))
    logger.propagate = False
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    
    # Use color formatting for console in development
    if len(logger.handlers) == 0:
        console_handler.setFormatter(ConsoleFormatter(console_format))
        logger.addHandler(console_handler)
    
    # File handler (optional)
    if settings and settings.log_to_file and settings.log_file_path:
        try:
            # Ensure directory exists
            ensure_log_directory(settings.log_file_path)
            
            # Create file handler
            file_handler = logging.FileHandler(settings.log_file_path)
            file_handler.setLevel(LOG_LEVEL_MAP.get(log_level, logging.INFO))
            
            # Use JSON formatter for file logs
            if settings.log_format == "json":
                file_handler.setFormatter(JsonFormatter())
            else:
                file_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
                file_handler.setFormatter(logging.Formatter(file_format))
            
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # Log to console if file logging fails
            console_handler.setFormatter(ConsoleFormatter(
                "%(asctime)s [ERROR] Logging setup - %(message)s"
            ))
            logger.addHandler(console_handler)
            logger.error(f"Failed to set up file logging: {str(e)}")
    
    return logger


# Create default logger instance
logger = get_logger()
