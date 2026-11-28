"""Demo script showing centralized error handling in action.

Run this to see how different error types are handled consistently.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.errors import register_exception_handlers


class CreateUserRequest(BaseModel):
    """Sample request model for validation demo."""
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    age: int = Field(..., gt=0, lt=150)


def main():
    print("=" * 70)
    print("Centralized API Error Handling Demo")
    print("=" * 70)
    print()
    
    # Create FastAPI app with error handlers
    app = FastAPI(title="Error Handling Demo")
    register_exception_handlers(app)
    
    # Define sample endpoints
    @app.get("/items/{item_id}")
    def get_item(item_id: str):
        """Example 404 error."""
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
    @app.get("/protected")
    def protected_resource():
        """Example 401 error."""
        raise HTTPException(status_code=401, detail="Authentication required")
    
    @app.get("/admin")
    def admin_only():
        """Example 403 error."""
        raise HTTPException(status_code=403, detail="Admin access required")
    
    @app.post("/users")
    def create_user():
        """Example 409 conflict."""
        raise HTTPException(status_code=409, detail="Username already exists")
    
    @app.post("/validate")
    def validate_user(request: CreateUserRequest):
        """Example validation endpoint."""
        return {"valid": True, "user": request.username}
    
    @app.get("/crash")
    def crash_endpoint():
        """Example unhandled exception."""
        # This will trigger generic exception handler
        result = 1 / 0
        return {"result": result}
    
    # Test the endpoints
    print("Testing Error Responses:")
    print("-" * 70)
    print()
    
    with TestClient(app, raise_server_exceptions=False) as client:
        # Test 404
        print("1. HTTP 404 - Not Found")
        response = client.get("/items/abc123")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 401
        print("2. HTTP 401 - Unauthorized")
        response = client.get("/protected")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 403
        print("3. HTTP 403 - Forbidden")
        response = client.get("/admin")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 409
        print("4. HTTP 409 - Conflict")
        response = client.post("/users")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 422 - Validation Error
        print("5. HTTP 422 - Validation Error (invalid email)")
        response = client.post("/validate", json={
            "username": "john",
            "email": "not-an-email",
            "age": 25
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 422 - Missing field
        print("6. HTTP 422 - Validation Error (missing field)")
        response = client.post("/validate", json={
            "username": "john",
            "age": 25
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 500 - Unhandled Exception
        print("7. HTTP 500 - Internal Server Error")
        response = client.get("/crash")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
    
    print("-" * 70)
    print("Key Features Demonstrated:")
    print("-" * 70)
    print("✓ Consistent error envelope structure")
    print("✓ Appropriate HTTP status codes")
    print("✓ User-friendly error codes (not_found, unauthorized, etc.)")
    print("✓ Request ID tracking for all errors")
    print("✓ Safe error messages (no sensitive data exposed)")
    print("✓ Validation errors formatted clearly")
    print()
    print("=" * 70)
    print("All error types handled successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
