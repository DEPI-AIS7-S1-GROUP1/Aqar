"""Example showing how to integrate error handlers into main.py.

This is a reference implementation - NOT to be used directly.
The actual integration should be done in app/main.py.
"""

from fastapi import FastAPI

# This is how error handlers should be registered in main.py:
#
# from app.core.errors import register_exception_handlers
#
# app = FastAPI(title="AqarAI API")
#
# # Register exception handlers
# register_exception_handlers(app)
#
# @app.get("/health")
# def health() -> dict[str, str]:
#     """Liveness check. Does not touch db or redis."""
#     return {"status": "ok"}


def main():
    print("=" * 70)
    print("Error Handler Integration Example")
    print("=" * 70)
    print()
    print("To integrate error handling into main.py:")
    print("-" * 70)
    print()
    print("1. Import the registration function:")
    print("   from app.core.errors import register_exception_handlers")
    print()
    print("2. Register handlers after creating the FastAPI app:")
    print("   app = FastAPI(title='AqarAI API')")
    print("   register_exception_handlers(app)")
    print()
    print("3. All endpoints will now use centralized error handling")
    print()
    print("-" * 70)
    print("Example updated main.py:")
    print("-" * 70)
    print('''
from fastapi import FastAPI
from app.core.errors import register_exception_handlers

app = FastAPI(title="AqarAI API")

# Register centralized exception handlers
register_exception_handlers(app)

@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check. Does not touch db or redis."""
    return {"status": "ok"}
    ''')
    print()
    print("-" * 70)
    print("Error Response Format:")
    print("-" * 70)
    print('''
{
  "error": {
    "code": "not_found",
    "message": "Resource not found",
    "request_id": "abc-123"
  }
}
    ''')
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
