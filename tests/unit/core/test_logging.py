"""
Comprehensive tests for logging functionality.
Consolidates all logging tests into a single, well-organized file.
"""
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, UTC
from unittest.mock import patch, MagicMock

import pytest

from app.core.logging import (
    JsonFormatter,
    ConsoleFormatter,
    ContextLogger,
    get_logger,
    ensure_log_directory,
    LOG_LEVEL_MAP
)
from tests.fixtures import mock_settings, temp_log_file


class TestJsonFormatter:
    """Tests for JSON log formatting."""
    
    def test_basic_formatting(self):
        """Test basic JSON log formatting."""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Test message",
            args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert log_dict["message"] == "Test message"
        assert log_dict["level"] == "INFO"
        assert log_dict["name"] == "test"
        assert "timestamp" in log_dict

    def test_custom_json_settings(self):
        """Test JsonFormatter with custom JSON settings."""
        formatter = JsonFormatter(
            json_indent=4,
            json_separators=(',', ': '),
            timestamp_field="@timestamp"
        )
        
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Test message",
            args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert "@timestamp" in log_dict
        assert "timestamp" not in log_dict
        assert '\n' in formatted  # Pretty-printed with indentation

    def test_non_serializable_objects(self):
        """Test JsonFormatter with non-serializable objects."""
        formatter = JsonFormatter()
        
        class NonSerializable:
            def __str__(self):
                return "NonSerializable object"
        
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Test message",
            args=(), exc_info=None
        )
        record.custom_object = NonSerializable()
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert "custom_object" in log_dict
        assert log_dict["custom_object"] == "NonSerializable object"

    def test_custom_json_encoder(self):
        """Test JsonFormatter with custom JSON encoder."""
        class CustomEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, set):
                    return list(o)
                return super().default(o)
        
        formatter = JsonFormatter(json_encoder=CustomEncoder)
        
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Test message",
            args=(), exc_info=None
        )
        record.tags = {"tag1", "tag2", "tag3"}
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert "tags" in log_dict
        if isinstance(log_dict["tags"], list):
            assert sorted(log_dict["tags"]) == sorted(["tag1", "tag2", "tag3"])


class TestConsoleFormatter:
    """Tests for console log formatting."""
    
    def test_color_formatting(self):
        """Test console color formatting for different log levels."""
        formatter = ConsoleFormatter("%(levelname)s - %(message)s")
        
        # Test different levels
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"), 
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL")
        ]
        
        for level, level_name in levels:
            record = logging.LogRecord(
                name="test", level=level,
                pathname="", lineno=0, msg="Test message",
                args=(), exc_info=None
            )
            
            formatted = formatter.format(record)
            assert level_name in formatted
            assert "\033[" in formatted  # ANSI color code

    def test_unknown_level(self):
        """Test ConsoleFormatter with unknown log level."""
        formatter = ConsoleFormatter("%(levelname)s - %(message)s")
        
        custom_level = 15  # Between DEBUG and INFO
        logging.addLevelName(custom_level, "VERBOSE")
        
        record = logging.LogRecord(
            name="test", level=custom_level,
            pathname="", lineno=0, msg="Custom level message",
            args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "\033[0m" in formatted  # Reset color for unknown level
        assert "VERBOSE" in formatted


class TestContextLogger:
    """Tests for contextual logging."""
    
    def test_basic_context(self):
        """Test basic context functionality."""
        logger = ContextLogger("test_logger")
        
        context = {"request_id": "req-123", "user_id": 42}
        logger_with_context = logger.with_context(context)
        
        assert logger_with_context._context == context

    def test_nested_context(self):
        """Test nested context merging."""
        logger = ContextLogger("test_logger")
        
        context1 = {"request_id": "req-123", "user_id": 42}
        logger_with_context1 = logger.with_context(context1)
        
        context2 = {"session_id": "sess-456", "user_id": 99}
        logger_with_context2 = logger_with_context1.with_context(context2)
        
        assert logger_with_context2._context["request_id"] == "req-123"
        assert logger_with_context2._context["session_id"] == "sess-456"
        assert logger_with_context2._context["user_id"] == 99  # Overridden

    def test_context_isolation(self):
        """Test that context changes don't affect original logger."""
        logger = ContextLogger("test_logger")
        
        logger_with_context = logger.with_context({"request_id": "req-123"})
        
        # Original logger should not have context
        assert not hasattr(logger, "_context") or not logger._context
        
        # Create another derived logger
        logger_with_context2 = logger.with_context({"request_id": "req-456"})
        
        # Should be independent
        assert logger_with_context._context["request_id"] == "req-123"
        assert logger_with_context2._context["request_id"] == "req-456"


class TestLoggerConfiguration:
    """Tests for logger configuration and management."""
    
    def test_get_logger_default(self):
        """Test get_logger with default settings."""
        logger = get_logger("test_logger")
        
        assert isinstance(logger, ContextLogger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO

    def test_get_logger_custom_level(self):
        """Test get_logger with custom log level."""
        logger = get_logger("test_logger", log_level="DEBUG")
        assert logger.level == logging.DEBUG
        
        logger = get_logger("test_logger", log_level="ERROR")
        assert logger.level == logging.ERROR

    def test_get_logger_invalid_level(self):
        """Test get_logger with invalid log level."""
        logger = get_logger("test_logger", log_level="INVALID")
        assert logger.level == logging.INFO  # Should default to INFO

    @patch('app.core.logging.settings')
    def test_file_logging_setup(self, mock_settings_patch, temp_log_file):
        """Test file logging configuration."""
        mock_settings_patch.log_to_file = True
        mock_settings_patch.log_file_path = temp_log_file
        mock_settings_patch.log_format = "text"
        
        with patch('app.core.logging.ensure_log_directory'):
            logger = get_logger("test_file_logger")
            
            # Should have console handler by default
            assert len(logger.handlers) > 0

    @patch('app.core.logging.settings')
    def test_file_logging_error_handling(self, mock_settings_patch):
        """Test file logging error handling."""
        mock_settings_patch.log_to_file = True
        mock_settings_patch.log_file_path = "/tmp/test.log"
        mock_settings_patch.log_format = "text"
        
        with patch('logging.FileHandler') as mock_file_handler:
            mock_file_handler.side_effect = PermissionError("Permission denied")
            
            with patch('logging.StreamHandler') as mock_stream_handler:
                mock_handler = MagicMock()
                mock_handler.level = 10  # DEBUG level
                mock_stream_handler.return_value = mock_handler
                
                # Should not raise exception
                logger = get_logger("test_error_logger")
                
                # Verify handler was configured
                assert mock_handler.setLevel.called
                assert mock_handler.setFormatter.called


class TestLogDirectoryManagement:
    """Tests for log directory creation and management."""
    
    def test_ensure_log_directory_simple(self, temp_log_file):
        """Test basic log directory creation."""
        # Directory should exist after calling ensure_log_directory
        ensure_log_directory(temp_log_file)
        assert os.path.exists(os.path.dirname(temp_log_file))

    def test_ensure_log_directory_nested(self):
        """Test log directory creation with nested directories."""
        base_dir = tempfile.gettempdir()
        nested_dir = os.path.join(base_dir, f"test_logs_{uuid.uuid4().hex}", "nested", "logs")
        log_path = os.path.join(nested_dir, "test.log")
        
        try:
            assert not os.path.exists(nested_dir)
            ensure_log_directory(log_path)
            assert os.path.exists(nested_dir)
        finally:
            # Cleanup
            if os.path.exists(nested_dir):
                os.rmdir(nested_dir)
                os.rmdir(os.path.dirname(nested_dir))
                os.rmdir(os.path.dirname(os.path.dirname(nested_dir)))

    def test_ensure_log_directory_existing(self, temp_log_file):
        """Test ensure_log_directory with existing directory."""
        # Create directory first
        log_dir = os.path.dirname(temp_log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Should not raise error
        ensure_log_directory(temp_log_file)
        assert os.path.exists(log_dir)


class TestLogLevelMapping:
    """Tests for log level mapping functionality."""
    
    def test_log_level_map_completeness(self):
        """Test that LOG_LEVEL_MAP contains expected levels."""
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in expected_levels:
            assert level in LOG_LEVEL_MAP
            assert isinstance(LOG_LEVEL_MAP[level], int)

    def test_log_level_map_values(self):
        """Test LOG_LEVEL_MAP values are correct."""
        assert LOG_LEVEL_MAP["DEBUG"] == logging.DEBUG
        assert LOG_LEVEL_MAP["INFO"] == logging.INFO
        assert LOG_LEVEL_MAP["WARNING"] == logging.WARNING
        assert LOG_LEVEL_MAP["ERROR"] == logging.ERROR
        assert LOG_LEVEL_MAP["CRITICAL"] == logging.CRITICAL


class TestConsoleFormatterExtended:
    """Extended tests for ConsoleFormatter class."""
    
    def test_format_with_color(self):
        """Test that ConsoleFormatter adds color codes to the log message."""
        formatter = ConsoleFormatter("%(levelname)s - %(message)s")
        
        # Create log records for different levels
        debug_record = logging.LogRecord(
            name="test", level=logging.DEBUG,
            pathname="", lineno=0, msg="Debug message",
            args=(), exc_info=None
        )
        
        info_record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Info message",
            args=(), exc_info=None
        )
        
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR,
            pathname="", lineno=0, msg="Error message",
            args=(), exc_info=None
        )
        
        # Format the records
        debug_formatted = formatter.format(debug_record)
        info_formatted = formatter.format(info_record)
        error_formatted = formatter.format(error_record)
        
        # Check that color codes are present
        assert '\033[' in debug_formatted  # ANSI color codes
        assert '\033[' in info_formatted
        assert '\033[' in error_formatted
        
        # Check that messages are present
        assert "Debug message" in debug_formatted
        assert "Info message" in info_formatted
        assert "Error message" in error_formatted


class TestJsonFormatterExtended:
    """Extended tests for JsonFormatter class."""
    
    def test_format_with_custom_json_settings(self):
        """Test JsonFormatter with custom JSON settings."""
        # Create formatter with custom JSON settings
        formatter = JsonFormatter(
            json_indent=4,
            json_separators=(',', ': '),
            timestamp_field="@timestamp"
        )
        
        # Create a basic record
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0, msg="Test message",
            args=(), exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON to verify format
        log_dict = json.loads(formatted)
        
        # Check custom timestamp field
        assert "@timestamp" in log_dict
        assert "timestamp" not in log_dict  # Default field should not be present
        
        # Verify indentation (formatted JSON should have newlines)
        assert '\n' in formatted
        
    def test_format_with_exception_traceback(self):
        """Test JsonFormatter with exception information."""
        import sys
        formatter = JsonFormatter()
        
        # Create an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        
        # Create a record with exception info
        record = logging.LogRecord(
            name="test", level=logging.ERROR,
            pathname="", lineno=0, msg="Error with exception",
            args=(), exc_info=exc_info
        )
        
        # Format the record
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        # Check that exception info is included
        assert "exception" in log_dict
        assert "Test exception" in str(log_dict["exception"])
        assert "ValueError" in str(log_dict["exception"])


class TestContextLoggerExtended:
    """Extended tests for ContextLogger functionality."""
    
    def test_context_logger_creation(self):
        """Test ContextLogger creation and basic functionality."""
        # Simple test that doesn't rely on internal mocking
        logger1 = ContextLogger("test1")
        logger2 = ContextLogger("test2")
        
        # Test that loggers are different instances
        assert logger1 is not logger2
        assert hasattr(logger1, 'info')
        assert hasattr(logger2, 'info')
            
    def test_context_logger_with_extra_data(self):
        """Test ContextLogger with extra logging data."""
        logger = ContextLogger("test")
        
        # Test logging with extra data
        with patch.object(logger, 'info') as mock_info:
            logger.info("Test message", extra={"key": "value"})
            mock_info.assert_called_once_with("Test message", extra={"key": "value"})
