"""
Tests for the exception handlers.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
    register_exception_handlers,
)


class TestExceptionHandlers:
    """Tests for exception handlers."""
    
    @pytest.fixture
    def app(self):
        """Create a FastAPI app with the exception handlers."""
        app = FastAPI()
        register_exception_handlers(app)
        
        class Item(BaseModel):
            name: str = Field(..., min_length=3)
            price: float = Field(..., gt=0)
        
        @app.post("/items/")
        async def create_item(item: Item):
            return item
        
        @app.get("/not-found")
        async def not_found():
            raise StarletteHTTPException(status_code=404, detail="Item not found")
        
        @app.get("/error")
        async def error():
            # This will be caught by the general exception handler
            raise ValueError("Test error")
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a TestClient for the app."""
        # Configure o TestClient para não levantar exceções
        return TestClient(app, raise_server_exceptions=False)
    
    def test_validation_exception_handler(self, client):
        """Test that validation errors are handled correctly."""
        # Make a request with invalid data
        response = client.post("/items/", json={"name": "a", "price": -1})
        
        # Check response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        assert "message" in response.json()
        assert "Validation error" in response.json()["message"]
        
        # Verify that detail contains the validation errors
        detail = response.json()["detail"]
        assert isinstance(detail, list)
        assert len(detail) > 0
        
        # Check for specific validation errors by type instead of message
        error_types = [e.get("type", "") for e in detail]
        assert any("string_too_short" in err_type for err_type in error_types)  # name too short
        assert any("greater_than" in err_type for err_type in error_types)  # price <= 0
    
    def test_http_exception_handler(self, client):
        """Test that HTTP exceptions are handled correctly."""
        # Make a request that will raise a 404
        response = client.get("/not-found")
        
        # Check response
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "message" in response.json()
        assert "Item not found" in response.json()["detail"]
    
    def test_general_exception_handler(self, client):
        """Test that general exceptions are handled correctly."""
        # Make a request that will raise a ValueError
        response = client.get("/error")
        
        # Verificar que o handler retorna um erro 500
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "message" in response.json()
        assert "Internal server error" in response.json()["detail"]
    
    @patch("app.core.exceptions.logger")
    def test_validation_exception_logs(self, mock_logger, client):
        """Test that validation exceptions are logged."""
        # Make a request with invalid data
        client.post("/items/", json={"name": "a", "price": -1})
        
        # Check that the logger was called
        mock_logger.warning.assert_called()
        
        # Get the log message and extras
        args, kwargs = mock_logger.warning.call_args
        assert "Request validation error" in args[0]
        assert "validation_errors" in kwargs["extra"]
    
    @patch("app.core.exceptions.logger")
    def test_http_exception_logs(self, mock_logger, client):
        """Test that HTTP exceptions are logged."""
        # Make a request that will raise a 404
        client.get("/not-found")
        
        # Check that the logger was called
        mock_logger.warning.assert_called()
        
        # Get the log message and extras
        args, kwargs = mock_logger.warning.call_args
        assert "HTTP exception" in args[0]
        assert "status_code" in kwargs["extra"]
        assert kwargs["extra"]["status_code"] == 404
    
    @patch("app.core.exceptions.logger")
    def test_general_exception_logs(self, mock_logger, client):
        """Test that general exceptions are logged."""
        # Make a request that will raise a ValueError
        client.get("/error")
        
        # Check that the logger was called
        mock_logger.exception.assert_called()
        
        # Get the log message and extras
        args, kwargs = mock_logger.exception.call_args
        assert "Unhandled exception" in args[0]
        assert "exception_type" in kwargs["extra"]
        assert kwargs["extra"]["exception_type"] == "ValueError"


def test_register_exception_handlers():
    """Test that register_exception_handlers adds the handlers to the app."""
    # Create a mock app
    app = MagicMock()
    
    # Call the function
    register_exception_handlers(app)
    
    # Check that add_exception_handler was called for each handler
    assert app.add_exception_handler.call_count == 3
    
    # Check that it was called with the right exception types
    app.add_exception_handler.assert_any_call(RequestValidationError, validation_exception_handler)
    app.add_exception_handler.assert_any_call(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler.assert_any_call(Exception, general_exception_handler)
