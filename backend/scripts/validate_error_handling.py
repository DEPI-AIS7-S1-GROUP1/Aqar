"""Validation script for centralized error handling implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.errors import ErrorResponse, register_exception_handlers


class TestRequest(BaseModel):
    value: int = Field(..., gt=0)


def main():
    print("=" * 70)
    print("Error Handling Validation")
    print("=" * 70)
    print()
    
    app = FastAPI()
    register_exception_handlers(app)
    
    @app.get("/test400")
    def test400():
        raise HTTPException(status_code=400, detail="Bad request test")
    
    @app.get("/test401")
    def test401():
        raise HTTPException(status_code=401, detail="Unauthorized test")
    
    @app.get("/test403")
    def test403():
        raise HTTPException(status_code=403, detail="Forbidden test")
    
    @app.get("/test404")
    def test404():
        raise HTTPException(status_code=404, detail="Not found test")
    
    @app.get("/test409")
    def test409():
        raise HTTPException(status_code=409, detail="Conflict test")
    
    @app.post("/test422")
    def test422(request: TestRequest):
        return {"ok": True}
    
    @app.get("/test429")
    def test429():
        raise HTTPException(status_code=429, detail="Rate limit test")
    
    @app.get("/test500")
    def test500():
        raise ValueError("Unexpected error")
    
    @app.get("/success")
    def success():
        return {"status": "ok"}
    
    with TestClient(app, raise_server_exceptions=False) as client:
        tests = [
            ("HTTP 400", "/test400", 400, "bad_request"),
            ("HTTP 401", "/test401", 401, "unauthorized"),
            ("HTTP 403", "/test403", 403, "forbidden"),
            ("HTTP 404", "/test404", 404, "not_found"),
            ("HTTP 409", "/test409", 409, "conflict"),
            ("HTTP 429", "/test429", 429, "too_many_requests"),
            ("HTTP 500", "/test500", 500, "internal_error"),
        ]
        
        print("Testing Error Responses:")
        print("-" * 70)
        
        all_passed = True
        for name, path, expected_status, expected_code in tests:
            response = client.get(path)
            data = response.json()
            
            # Validate response structure
            checks = {
                "Status code": response.status_code == expected_status,
                "Has 'error' key": "error" in data,
                "Has 'code' field": "code" in data.get("error", {}),
                "Has 'message' field": "message" in data.get("error", {}),
                "Has 'request_id' field": "request_id" in data.get("error", {}),
                "Correct error code": data.get("error", {}).get("code") == expected_code,
                "Only 3 error fields": len(data.get("error", {})) == 3,
                "Only 1 root key": len(data) == 1,
            }
            
            passed = all(checks.values())
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} {name}: {expected_code}")
            
            if not passed:
                all_passed = False
                for check_name, result in checks.items():
                    if not result:
                        print(f"      ✗ {check_name}")
        
        print()
        print("Testing Validation Error (422):")
        print("-" * 70)
        response = client.post("/test422", json={"value": -5})
        data = response.json()
        
        validation_checks = {
            "Status 422": response.status_code == 422,
            "Error code 'validation_error'": data.get("error", {}).get("code") == "validation_error",
            "Has error message": bool(data.get("error", {}).get("message")),
            "Has request_id": bool(data.get("error", {}).get("request_id")),
        }
        
        validation_passed = all(validation_checks.values())
        status = "✓ PASS" if validation_passed else "✗ FAIL"
        print(f"{status} HTTP 422: validation_error")
        
        if not validation_passed:
            all_passed = False
            for check_name, result in validation_checks.items():
                if not result:
                    print(f"      ✗ {check_name}")
        
        print()
        print("Testing Normal Response (should not be affected):")
        print("-" * 70)
        response = client.get("/success")
        data = response.json()
        
        normal_checks = {
            "Status 200": response.status_code == 200,
            "No 'error' key": "error" not in data,
            "Normal response": data.get("status") == "ok",
        }
        
        normal_passed = all(normal_checks.values())
        status = "✓ PASS" if normal_passed else "✗ FAIL"
        print(f"{status} Normal endpoint not affected")
        
        if not normal_passed:
            all_passed = False
        
        print()
        print("=" * 70)
        if all_passed:
            print("✓ All validations passed!")
        else:
            print("✗ Some validations failed")
        print("=" * 70)
        
        return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
