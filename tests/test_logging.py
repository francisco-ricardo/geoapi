"""
Tests for the logging system.
"""
import json
import logging
import os
import pytest
from unittest.mock import patch, MagicMock

from app.core.logging import (
    JsonFormatter, 
    ConsoleFormatter, 
    ContextLogger, 
    get_logger, 
    logger
)


class TestJsonFormatter:
    """Tests for JsonFormatter class."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record as JSON."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON
        log_dict = json.loads(formatted)
        
        # Check required fields
        assert log_dict["level"] == "INFO"
        assert log_dict["message"] == "Test message"
        assert log_dict["logger"] == "test_logger"
        assert "timestamp" in log_dict
        
        # Check location info
        assert "location" in log_dict
        assert log_dict["location"]["module"] == "test_file"
        assert log_dict["location"]["line"] == 10
    
    def test_format_with_exception(self):
        """Test formatting a log record with exception info."""
        formatter = JsonFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            import sys
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test_file.py",
                lineno=20,
                msg="Error occurred",
                args=(),
                exc_info=exc_info  # Pass the actual exc_info tuple
            )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON
        log_dict = json.loads(formatted)
        
        # Check exception info
        assert "exception" in log_dict
        assert log_dict["exception"]["type"] == "ValueError"
        assert log_dict["exception"]["message"] == "Test exception"
        assert "traceback" in log_dict["exception"]
    
    def test_format_with_extra_fields(self):
        """Test formatting a log record with extra fields."""
        formatter = JsonFormatter()
        
        # Create a record with extra fields
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=30,
            msg="Request processed",
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.request_id = "abc-123"
        record.user_id = 42
        record.performance = {"duration_ms": 150}
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON
        log_dict = json.loads(formatted)
        
        # Check extra fields
        assert log_dict["request_id"] == "abc-123"
        assert log_dict["user_id"] == 42
        assert log_dict["performance"] == {"duration_ms": 150}


class TestContextLogger:
    """Tests for ContextLogger class."""
    
    def test_with_correlation_id(self):
        """Test creating a logger with correlation ID."""
        # Create a logger
        logger = ContextLogger("test_logger")
        
        # Add a correlation ID
        correlation_id = "test-correlation-id"
        logger_with_id = logger.with_correlation_id(correlation_id)
        
        # Check that the context contains the correlation ID
        assert logger_with_id._context["correlation_id"] == correlation_id
        
        # Check that it's a different logger instance
        assert logger_with_id is not logger
    
    def test_with_context(self):
        """Test creating a logger with custom context."""
        # Create a logger
        logger = ContextLogger("test_logger")
        
        # Add context
        context = {"user_id": 123, "request_path": "/api/test"}
        logger_with_context = logger.with_context(context)
        
        # Check that the context contains the added fields
        assert logger_with_context._context["user_id"] == 123
        assert logger_with_context._context["request_path"] == "/api/test"
    
    def test_log_includes_context(self):
        """Test that log messages include context."""
        # Create a logger
        logger = ContextLogger("test_logger")
        logger.setLevel(logging.INFO)
        
        # Create a real handler with a custom formatter to capture records
        import io
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(message)s %(request_id)s'))
        logger.addHandler(handler)
        
        # Add context and log a message
        logger_with_context = logger.with_context({"request_id": "req-123"})
        logger_with_context.info("Test message")
        
        # Check that the output includes the context
        log_output = output.getvalue()
        assert "Test message" in log_output
        assert "req-123" in log_output


class TestGetLogger:
    """Tests for get_logger function."""
    
    def test_get_logger_caching(self):
        """Test that get_logger caches logger instances."""
        # Get logger twice with the same name
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        
        # They should be the same instance
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Test that get_logger returns different loggers for different names."""
        # Get loggers with different names
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        
        # They should be different instances
        assert logger1 is not logger2
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
    
    def test_get_logger_level(self):
        """Test that get_logger sets the correct log level."""
        # Get logger with custom level
        logger = get_logger("test_logger", log_level="ERROR")
        
        # Check level
        assert logger.level == logging.ERROR
        
        # Check handlers
        assert len(logger.handlers) > 0
        
        # The logger should not propagate
        assert not logger.propagate
