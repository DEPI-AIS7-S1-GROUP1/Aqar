"""Demo showing how to use database sessions in FastAPI endpoints.

This demonstrates the typical usage pattern with Depends(get_session).
"""

import sys
from pathlib import Path

# Add parent to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_session

# Create a simple FastAPI app
app = FastAPI(title="Database Session Demo")


@app.get("/health")
def health_check():
    """Simple health check without database."""
    return {"status": "healthy"}


@app.get("/db-test")
def test_database_connection(db: Session = Depends(get_session)):
    """Test endpoint that uses a database session.
    
    This demonstrates:
    1. How to inject the session using Depends(get_session)
    2. The session is automatically created for the request
    3. The session is automatically closed after the request
    """
    try:
        # Execute a simple query
        result = db.execute(text("SELECT 1 as num, 'Database connected!' as message"))
        row = result.fetchone()
        return {
            "connected": True,
            "num": row[0],
            "message": row[1],
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }


@app.get("/db-info")
def database_info(db: Session = Depends(get_session)):
    """Get database version and connection info.
    
    Shows how the session can be used for real queries.
    """
    try:
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        
        return {
            "connected": True,
            "version": version[:100],  # Truncate for display
            "session_active": db.is_active,
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Import after path is set
    from app.core.db import get_session
    
    print("=" * 70)
    print("FastAPI Database Session Demo")
    print("=" * 70)
    print()
    print("This demo shows how to use get_session() in FastAPI endpoints.")
    print()
    print("Example endpoint definition:")
    print("-" * 70)
    print("""
@app.get("/items")
def get_items(db: Session = Depends(get_session)):
    # Use db session here
    return db.query(Item).all()
    """)
    print("-" * 70)
    print()
    print("The session is automatically:")
    print("  1. Created when the endpoint is called")
    print("  2. Injected as the 'db' parameter")
    print("  3. Closed after the response is sent")
    print()
    print("To run this demo app:")
    print("  uvicorn scripts.demo_db_fastapi:app --reload")
    print()
    print("Then visit:")
    print("  http://localhost:8000/health")
    print("  http://localhost:8000/db-test")
    print("  http://localhost:8000/db-info")
    print("  http://localhost:8000/docs  (Swagger UI)")
    print()
    print("=" * 70)
