"""
Tests for the logging middleware.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient

from app.middleware.logging_middleware import LoggingMiddleware, setup_logging_middleware
from app.core.logging import ContextLogger


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""
    
    @pytest.fixture
    def app(self):
        """Create a FastAPI app with the logging middleware."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "This is a test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a TestClient for the app."""
        return TestClient(app)
    
    def test_middleware_adds_correlation_id(self, client):
        """Test that the middleware adds a correlation ID to responses."""
        response = client.get("/test")
        
        # Check that the response has a correlation ID header
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] != ""
    
    def test_middleware_uses_provided_correlation_id(self, client):
        """Test that the middleware uses a provided correlation ID."""
        correlation_id = "test-correlation-id"
        response = client.get("/test", headers={"X-Correlation-ID": correlation_id})
        
        # Check that the response has the same correlation ID
        assert response.headers["X-Correlation-ID"] == correlation_id
    
    @patch("app.middleware.logging_middleware.get_logger")
    def test_middleware_logs_request_start(self, mock_get_logger, client):
        """Test that the middleware logs the start of a request."""
        # Create a mock logger
        mock_logger = MagicMock(spec=ContextLogger)
        mock_context_logger = MagicMock(spec=ContextLogger)
        
        # Configure the mock to return our mock_context_logger when with_correlation_id is called
        mock_logger.with_correlation_id.return_value = mock_context_logger
        
        # Configure get_logger to return our mock logger
        mock_get_logger.return_value = mock_logger
        
        # Make a request
        client.get("/test")
        
        # Check that the logger was created and with_correlation_id was called
        mock_get_logger.assert_called()
        mock_logger.with_correlation_id.assert_called()
        
        # Check that info was called on the context logger
        mock_context_logger.info.assert_called()
        
        # Check that at least one call contains "Request started"
        request_started_called = False
        for call in mock_context_logger.info.call_args_list:
            args, kwargs = call
            if args and "Request started" in args[0]:
                request_started_called = True
                assert "GET" in args[0]
                break
        assert request_started_called, "Expected 'Request started' log message not found"
    
    @patch("app.middleware.logging_middleware.get_logger")
    def test_middleware_logs_request_completion(self, mock_get_logger, client):
        """Test that the middleware logs the completion of a request."""
        # Create a mock logger
        mock_logger = MagicMock(spec=ContextLogger)
        mock_context_logger = MagicMock(spec=ContextLogger)
        
        # Configure the mock to return our mock_context_logger when with_correlation_id is called
        mock_logger.with_correlation_id.return_value = mock_context_logger
        
        # Configure get_logger to return our mock logger
        mock_get_logger.return_value = mock_logger
        
        # Make a request
        client.get("/test")
        
        # Check that the logger was created and with_correlation_id was called
        mock_get_logger.assert_called()
        mock_logger.with_correlation_id.assert_called()
        
        # Check that info was called on the context logger
        mock_context_logger.info.assert_called()
        
        # Check that at least one call contains "Request completed"
        request_completed_called = False
        for call in mock_context_logger.info.call_args_list:
            args, kwargs = call
            if args and "Request completed" in args[0]:
                request_completed_called = True
                assert "GET" in args[0]
                assert "200" in args[0]
                break
        assert request_completed_called, "Expected 'Request completed' log message not found"
    
    @patch("app.middleware.logging_middleware.get_logger")
    def test_middleware_logs_request_failure(self, mock_get_logger, client):
        """Test that the middleware logs failed requests."""
        # Create a mock logger
        mock_logger = MagicMock(spec=ContextLogger)
        mock_context_logger = MagicMock(spec=ContextLogger)
        
        # Configure the mock to return our mock_context_logger when with_correlation_id is called
        mock_logger.with_correlation_id.return_value = mock_context_logger
        
        # Configure get_logger to return our mock logger
        mock_get_logger.return_value = mock_logger
        
        # Make a request that will fail
        with pytest.raises(ValueError):
            client.get("/error")
        
        # Check that the logger was created and with_correlation_id was called
        mock_get_logger.assert_called()
        mock_logger.with_correlation_id.assert_called()
        
        # Check that exception was called on the context logger
        mock_context_logger.exception.assert_called()
        
        # Check that the call contains "Request failed"
        request_failed_called = False
        for call in mock_context_logger.exception.call_args_list:
            args, kwargs = call
            if args and "Request failed" in args[0]:
                request_failed_called = True
                assert "GET" in args[0]
                break
        assert request_failed_called, "Expected 'Request failed' log message not found"


class TestSetupLoggingMiddleware:
    """Tests for setup_logging_middleware function."""
    
    def test_setup_logging_middleware(self):
        """Test that setup_logging_middleware adds the middleware to the app."""
        # Create a mock app
        app = MagicMock()
        
        # Call the function
        setup_logging_middleware(app)
        
        # Check that add_middleware was called with LoggingMiddleware
        app.add_middleware.assert_called_once_with(LoggingMiddleware)
