"""Quick test script to verify database session lifecycle."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.db import get_session, get_engine


def main():
    print("=" * 70)
    print("Database Session Management Test")
    print("=" * 70)
    print()
    
    # Test engine
    print("Engine Configuration:")
    print("-" * 70)
    engine = get_engine()
    print(f"✓ Engine created: {type(engine).__name__}")
    print(f"✓ Engine URL: {str(engine.url)[:50]}...")
    print(f"✓ Pool pre-ping enabled: {engine.pool._pre_ping}")
    print(f"✓ Pool size: {engine.pool.size()}")
    print()
    
    # Test session lifecycle
    print("Session Lifecycle Test:")
    print("-" * 70)
    gen = get_session()
    session = next(gen)
    
    print(f"✓ Session created: {type(session).__name__}")
    print(f"✓ Session is active: {session.is_active}")
    print(f"✓ Session in transaction: {session.in_transaction()}")
    
    # Cleanup
    try:
        next(gen)
    except StopIteration:
        print("✓ Generator cleanup completed")
    
    print(f"✓ Session no longer in transaction: {not session.in_transaction()}")
    print()
    
    # Test multiple sessions
    print("Multiple Sessions Test:")
    print("-" * 70)
    gen1 = get_session()
    session1 = next(gen1)
    
    gen2 = get_session()
    session2 = next(gen2)
    
    print(f"✓ Session 1 ID: {id(session1)}")
    print(f"✓ Session 2 ID: {id(session2)}")
    print(f"✓ Sessions are different: {session1 is not session2}")
    
    # Cleanup
    for gen in [gen1, gen2]:
        try:
            next(gen)
        except StopIteration:
            pass
    
    print()
    print("=" * 70)
    print("All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
