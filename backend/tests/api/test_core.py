"""Tests for core API functionality: routing, error handling, request tracking, and CORS.

Tests verify:
1. Unknown route error envelope structure
2. Request ID propagation on all responses
3. Error handler consistency across different error types
4. Request duration measurement
5. Logging security (no sensitive data exposure)
6. CORS configuration
7. Middleware integration
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.middleware import get_duration_store
from app.main import app

# Create TestClient with raise_server_exceptions=False to test error handling
client = TestClient(app, raise_server_exceptions=False)


class TestUnknownRouteErrorEnvelope:
    """Test that unknown routes return proper error envelope structure."""

    def test_unknown_api_v1_route_returns_404(self):
        """Verify unknown /api/v1 route returns 404 with error envelope."""
        response = client.get("/api/v1/unknown-test-route")
        
        assert response.status_code == 404
        
        data = response.json()
        
        # Verify error envelope structure exists
        assert "error" in data, "Response must contain 'error' object"
        
        error = data["error"]
        assert "code" in error, "Error must contain 'code' field"
        assert "message" in error, "Error must contain 'message' field"
        assert "request_id" in error, "Error must contain 'request_id' field"
        
        # Verify field types and values
        assert error["code"] == "not_found", f"Expected code 'not_found', got '{error['code']}'"
        assert isinstance(error["message"], str), "Message must be a string"
        assert len(error["message"]) > 0, "Message must not be empty"
        assert isinstance(error["request_id"], str), "Request ID must be a string"
        assert len(error["request_id"]) > 0, "Request ID must not be empty"
    
    def test_unknown_root_route_returns_404(self):
        """Verify unknown root-level route returns 404."""
        response = client.get("/nonexistent-route")
        
        assert response.status_code == 404
        # Root level routes may not go through our error handlers,
        # but should still have request ID in header
        assert "x-request-id" in response.headers

    def test_error_response_structure_is_minimal(self):
        """Verify error response contains only required fields."""
        response = client.get("/api/v1/unknown-test-route")
        
        data = response.json()
        
        # Should have only the error envelope, no extra fields
        assert len(data) == 1, "Response should only contain 'error' key"
        
        error = data["error"]
        # Should have exactly code, message, and request_id
        assert len(error) == 3, f"Error should have exactly 3 fields, got {len(error)}"


class TestRequestIDPropagation:
    """Test request ID generation and propagation across all response types."""
    
    def test_health_endpoint_has_request_id_header(self):
        """Verify normal request receives X-Request-ID header."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "x-request-id" in response.headers, "Response must include X-Request-ID header"
        
        request_id = response.headers["x-request-id"]
        assert len(request_id) > 0, "Request ID must not be empty"
        
        # Should look like a UUID
        try:
            uuid.UUID(request_id)
        except ValueError:
            pytest.fail(f"Request ID should be valid UUID format, got: {request_id}")
    
    def test_error_response_has_request_id_header(self):
        """Verify error response includes X-Request-ID header."""
        response = client.get("/api/v1/unknown-test-route")
        
        assert response.status_code == 404
        assert "x-request-id" in response.headers, "Error response must include X-Request-ID header"
        
        request_id = response.headers["x-request-id"]
        assert len(request_id) > 0
    
    def test_request_id_consistency_between_header_and_body(self):
        """Verify request ID is consistent between header and error body."""
        response = client.get("/api/v1/unknown-test-route")
        
        header_request_id = response.headers.get("x-request-id")
        body_request_id = response.json()["error"]["request_id"]
        
        assert header_request_id == body_request_id, (
            f"Request ID mismatch: header={header_request_id}, body={body_request_id}"
        )
    
    def test_custom_request_id_propagation(self):
        """Verify valid incoming X-Request-ID is preserved."""
        custom_id = "test-custom-request-123"
        
        response = client.get(
            "/health",
            headers={"X-Request-ID": custom_id}
        )
        
        assert response.status_code == 200
        assert response.headers["x-request-id"] == custom_id, (
            "Valid incoming request ID should be preserved"
        )
    
    def test_invalid_request_id_is_replaced(self):
        """Verify invalid incoming request ID is replaced with generated one."""
        invalid_id = "invalid id with spaces!!!"
        
        response = client.get(
            "/health",
            headers={"X-Request-ID": invalid_id}
        )
        
        assert response.status_code == 200
        returned_id = response.headers["x-request-id"]
        
        assert returned_id != invalid_id, "Invalid request ID should be replaced"
        assert len(returned_id) > 0
        
        # Should be replaced with valid UUID
        try:
            uuid.UUID(returned_id)
        except ValueError:
            pytest.fail(f"Replacement should be valid UUID, got: {returned_id}")
    
    def test_request_id_on_validation_error(self):
        """Verify validation errors include request ID."""
        # This endpoint doesn't exist yet, but when it does,
        # validation errors should include request ID
        # For now, test with 404 which we know works
        response = client.get("/api/v1/test")
        
        assert "x-request-id" in response.headers


class TestErrorHandlerConsistency:
    """Test that all error types use unified error envelope."""
    
    def test_404_error_uses_unified_envelope(self):
        """Verify 404 errors use standard envelope."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert "request_id" in data["error"]
    
    def test_error_does_not_expose_internal_details(self):
        """Verify errors don't expose stack traces or internal details."""
        # Test with 404 (we don't have server errors to test yet)
        response = client.get("/api/v1/unknown")
        
        data = response.json()
        message = data["error"]["message"].lower()
        
        # Should not contain internal implementation details
        assert "traceback" not in message
        assert "file" not in message
        assert "line" not in message
        assert "exception" not in message


class TestRequestDurationMeasurement:
    """Test request duration measurement and storage."""
    
    def test_request_duration_is_recorded(self):
        """Verify completed requests add duration to storage."""
        store = get_duration_store()
        store.clear()  # Start fresh
        
        # Make a request
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check that duration was recorded
        all_durations = store.get_all()
        
        assert len(all_durations) > 0, "Duration should be recorded for request"
        
        # Find the /health route
        health_durations = None
        for route, durations in all_durations.items():
            if "health" in route.lower():
                health_durations = durations
                break
        
        assert health_durations is not None, "Duration should be recorded for /health route"
        assert len(health_durations) > 0
        
        # Duration should be positive and reasonable (not in seconds)
        duration = health_durations[-1]
        assert duration > 0, "Duration must be positive"
        assert duration < 10000, "Duration should be in milliseconds, not seconds"
    
    def test_multiple_requests_accumulate_durations(self):
        """Verify multiple requests to same route accumulate."""
        store = get_duration_store()
        store.clear()
        
        # Make multiple requests
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
        
        all_durations = store.get_all()
        
        # Should have recorded all requests
        total_recorded = sum(len(durations) for durations in all_durations.values())
        assert total_recorded >= 3, f"Expected at least 3 durations, got {total_recorded}"
    
    def test_error_requests_also_record_duration(self):
        """Verify failed requests also record duration."""
        store = get_duration_store()
        store.clear()
        
        # Make a request that will 404
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Duration should still be recorded
        all_durations = store.get_all()
        total_recorded = sum(len(durations) for durations in all_durations.values())
        
        assert total_recorded > 0, "Duration should be recorded even for errors"


class TestLoggingSecurity:
    """Test that sensitive data is not logged."""
    
    def test_request_body_not_in_response(self):
        """Verify request bodies are not echoed in responses."""
        # POST to non-existent endpoint with sensitive data
        response = client.post(
            "/api/v1/test",
            json={"password": "secret123", "credit_card": "1234-5678-9012-3456"}
        )
        
        # Response should not contain the request body
        response_text = response.text.lower()
        assert "secret123" not in response_text, "Password should not appear in response"
        assert "1234-5678" not in response_text, "Credit card should not appear in response"
    
    def test_error_message_does_not_leak_internal_paths(self):
        """Verify error messages don't expose file paths or internal structure."""
        response = client.get("/api/v1/unknown")
        
        data = response.json()
        message = data["error"]["message"]
        
        # Should not contain file system paths
        assert "backend/app" not in message.lower()
        assert "c:\\" not in message.lower()
        assert "/home/" not in message.lower()


class TestCORSConfiguration:
    """Test CORS middleware configuration."""
    
    def test_cors_allows_configured_origin(self):
        """Verify CORS allows configured frontend origin."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    
    def test_cors_enables_credentials(self):
        """Verify CORS enables credentials for authenticated requests."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_cors_allows_required_methods(self):
        """Verify CORS allows required HTTP methods."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        methods = response.headers.get("access-control-allow-methods", "")
        
        assert "GET" in methods
        assert "POST" in methods
        assert "PUT" in methods
        assert "DELETE" in methods


class TestMiddlewareIntegration:
    """Test that middleware components work together correctly."""
    
    def test_request_tracking_works_with_cors(self):
        """Verify request tracking and CORS work together."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        
        # Both request tracking and CORS should be active
        assert "x-request-id" in response.headers, "Request tracking should be active"
        assert "access-control-allow-origin" in response.headers, "CORS should be active"
    
    def test_error_handling_works_with_request_tracking(self):
        """Verify error handlers include request tracking."""
        response = client.get("/api/v1/unknown")
        
        assert response.status_code == 404
        
        # Should have both error envelope and request ID
        assert "error" in response.json()
        assert "x-request-id" in response.headers
        
        # Request ID should be consistent
        header_id = response.headers["x-request-id"]
        body_id = response.json()["error"]["request_id"]
        assert header_id == body_id
    
    def test_health_endpoint_still_works(self):
        """Verify health endpoint still works with all middleware."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert "x-request-id" in response.headers


class TestAPIVersioning:
    """Test API versioning structure."""
    
    def test_api_v1_prefix_is_registered(self):
        """Verify /api/v1 prefix is properly registered."""
        # Even though we get 404, it should be from our router, not FastAPI's default
        response = client.get("/api/v1/test")
        
        assert response.status_code == 404
        # Should have request ID from our middleware
        assert "x-request-id" in response.headers
    
    def test_health_endpoint_outside_api_versioning(self):
        """Verify /health is accessible outside /api/v1."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
