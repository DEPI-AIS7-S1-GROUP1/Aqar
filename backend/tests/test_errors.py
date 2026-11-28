"""Tests for centralized API error handling."""

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.errors import (
    ErrorResponse,
    _get_request_id,
    generic_exception_handler,
    http_exception_handler,
    register_exception_handlers,
    validation_exception_handler,
)


class SampleRequest(BaseModel):
    """Sample model for validation testing."""
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)


def test_error_response_model_structure():
    """Verify ErrorResponse has correct structure."""
    response = ErrorResponse(
        error={
            "code": "not_found",
            "message": "Resource not found",
            "request_id": "test-123",
        }
    )
    
    data = response.model_dump()
    assert "error" in data
    assert data["error"]["code"] == "not_found"
    assert data["error"]["message"] == "Resource not found"
    assert data["error"]["request_id"] == "test-123"


def test_get_request_id_from_state():
    """Verify request ID is extracted from request.state."""
    app = FastAPI()
    with TestClient(app) as client:
        @app.get("/test")
        def test_endpoint(request: Request):
            request.state.request_id = "state-123"
            return {"request_id": _get_request_id(request)}
        
        response = client.get("/test")
        assert response.json()["request_id"] == "state-123"


def test_get_request_id_from_header():
    """Verify request ID is extracted from header when state unavailable."""
    app = FastAPI()
    with TestClient(app) as client:
        @app.get("/test")
        def test_endpoint(request: Request):
            return {"request_id": _get_request_id(request)}
        
        response = client.get("/test", headers={"X-Request-ID": "header-456"})
        assert response.json()["request_id"] == "header-456"


def test_get_request_id_generates_uuid_fallback():
    """Verify UUID is generated when no request ID available."""
    app = FastAPI()
    with TestClient(app) as client:
        @app.get("/test")
        def test_endpoint(request: Request):
            return {"request_id": _get_request_id(request)}
        
        response = client.get("/test")
        request_id = response.json()["request_id"]
        
        # Should be a valid UUID format
        assert len(request_id) > 0
        assert "-" in request_id


def test_http_exception_handler_404():
    """Verify HTTP 404 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/items/{item_id}")
        def get_item(item_id: str):
            raise HTTPException(status_code=404, detail="Item not found")
        
        response = client.get("/items/123")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Item not found"
        assert "request_id" in data["error"]


def test_http_exception_handler_400():
    """Verify HTTP 400 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/test")
        def test_endpoint():
            raise HTTPException(status_code=400, detail="Invalid request")
        
        response = client.get("/test")
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["error"]["code"] == "bad_request"
        assert data["error"]["message"] == "Invalid request"


def test_http_exception_handler_401():
    """Verify HTTP 401 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/protected")
        def protected_endpoint():
            raise HTTPException(status_code=401, detail="Authentication required")
        
        response = client.get("/protected")
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["error"]["code"] == "unauthorized"
        assert data["error"]["message"] == "Authentication required"


def test_http_exception_handler_403():
    """Verify HTTP 403 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/admin")
        def admin_endpoint():
            raise HTTPException(status_code=403, detail="Access denied")
        
        response = client.get("/admin")
        
        assert response.status_code == 403
        data = response.json()
        
        assert data["error"]["code"] == "forbidden"
        assert data["error"]["message"] == "Access denied"


def test_http_exception_handler_409():
    """Verify HTTP 409 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.post("/users")
        def create_user():
            raise HTTPException(status_code=409, detail="User already exists")
        
        response = client.post("/users")
        
        assert response.status_code == 409
        data = response.json()
        
        assert data["error"]["code"] == "conflict"
        assert data["error"]["message"] == "User already exists"


def test_http_exception_handler_429():
    """Verify HTTP 429 exception produces correct error envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/rate-limited")
        def rate_limited_endpoint():
            raise HTTPException(status_code=429, detail="Too many requests")
        
        response = client.get("/rate-limited")
        
        assert response.status_code == 429
        data = response.json()
        
        assert data["error"]["code"] == "too_many_requests"
        assert data["error"]["message"] == "Too many requests"


def test_validation_exception_handler():
    """Verify validation errors produce HTTP 422 with correct envelope."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.post("/validate")
        def validate_endpoint(request: SampleRequest):
            return {"valid": True}
        
        # Send invalid data (negative age)
        response = client.post("/validate", json={"name": "Test", "age": -5})
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "validation_error"
        assert "age" in data["error"]["message"].lower()
        assert "request_id" in data["error"]


def test_validation_exception_handler_missing_field():
    """Verify validation errors for missing required fields."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.post("/validate")
        def validate_endpoint(request: SampleRequest):
            return {"valid": True}
        
        # Send incomplete data (missing name)
        response = client.post("/validate", json={"age": 25})
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["error"]["code"] == "validation_error"
        assert "name" in data["error"]["message"].lower()


def test_generic_exception_handler():
    """Verify unhandled exceptions produce HTTP 500 with safe message."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app, raise_server_exceptions=False) as client:
        @app.get("/crash")
        def crash_endpoint():
            raise ValueError("Internal bug with sensitive data")
        
        response = client.get("/crash")
        
        assert response.status_code == 500
        data = response.json()
        
        assert data["error"]["code"] == "internal_error"
        # Should NOT expose internal exception details
        assert "sensitive data" not in data["error"]["message"].lower()
        assert "bug" not in data["error"]["message"].lower()
        # Should have generic safe message
        assert "internal error" in data["error"]["message"].lower()
        assert "request_id" in data["error"]


def test_generic_exception_handler_does_not_expose_stack_trace():
    """Verify stack traces are not exposed to clients."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app, raise_server_exceptions=False) as client:
        @app.get("/error")
        def error_endpoint():
            # Trigger an exception with stack trace
            x = 1 / 0
        
        response = client.get("/error")
        
        assert response.status_code == 500
        data = response.json()
        
        # Ensure no stack trace information in response
        message = data["error"]["message"].lower()
        assert "traceback" not in message
        assert "file" not in message
        assert "line" not in message
        assert "zerodivision" not in message


def test_error_response_has_consistent_structure():
    """Verify all error responses have the same structure."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app, raise_server_exceptions=False) as client:
        # Define endpoints with different error types
        @app.get("/error400")
        def error400():
            raise HTTPException(status_code=400, detail="Bad request")
        
        @app.get("/error404")
        def error404():
            raise HTTPException(status_code=404, detail="Not found")
        
        @app.get("/error500")
        def error500():
            raise RuntimeError("Server error")
        
        # Test all endpoints
        for path in ["/error400", "/error404", "/error500"]:
            response = client.get(path)
            data = response.json()
            
            # All should have same structure
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]
            assert "request_id" in data["error"]
            
            # Should not have extra fields
            assert len(data) == 1  # Only "error" key
            assert len(data["error"]) == 3  # Only code, message, request_id


def test_request_id_consistency():
    """Verify request ID is consistent when set via state."""
    app = FastAPI()
    register_exception_handlers(app)
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = "consistent-123"
        response = await call_next(request)
        return response
    
    with TestClient(app) as client:
        @app.get("/test")
        def test_endpoint():
            raise HTTPException(status_code=404, detail="Not found")
        
        response = client.get("/test")
        data = response.json()
        
        assert data["error"]["request_id"] == "consistent-123"


def test_register_exception_handlers_does_not_break_app():
    """Verify registering handlers doesn't affect normal responses."""
    app = FastAPI()
    register_exception_handlers(app)
    
    with TestClient(app) as client:
        @app.get("/success")
        def success_endpoint():
            return {"status": "ok"}
        
        response = client.get("/success")
        
        assert response.status_code == 200
        data = response.json()
        
        # Normal response should not have error envelope
        assert "error" not in data
        assert data["status"] == "ok"
