"""Demo script to demonstrate the centralized settings configuration.

Run this script to see how settings load from environment variables.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import Settings, settings, get_settings


def main():
    print("=" * 70)
    print("AqarAI Backend - Centralized Settings Configuration Demo")
    print("=" * 70)
    print()
    
    # Show current settings
    print("Current Settings:")
    print("-" * 70)
    print(f"Database URL: {settings.DATABASE_URL[:30]}...")
    print(f"Redis URL: {settings.REDIS_URL}")
    print(f"JWT Secret set: {'Yes' if settings.JWT_SECRET else 'No (Warning!)'}")
    print(f"CORS Origins: {settings.cors_origins_list}")
    print()
    
    # Show feature flags
    print("Feature Flags:")
    print("-" * 70)
    print(f"  USE_REAL_LISTINGS: {settings.USE_REAL_LISTINGS}")
    print(f"  USE_REAL_FINANCE: {settings.USE_REAL_FINANCE}")
    print(f"  USE_REAL_RAG: {settings.USE_REAL_RAG}")
    print(f"  USE_REAL_CONVERSATIONS: {settings.USE_REAL_CONVERSATIONS}")
    print(f"  USE_REAL_LEADS: {settings.USE_REAL_LEADS}")
    print(f"  USE_REAL_AGENT: {settings.USE_REAL_AGENT}")
    print()
    
    # Show safe repr (secrets masked)
    print("Safe Representation (secrets masked):")
    print("-" * 70)
    print(repr(settings))
    print()
    
    # Demonstrate environment override
    print("Environment Override Demo:")
    print("-" * 70)
    print("Set environment variable: USE_REAL_LISTINGS=true")
    print("Then reload settings to see the change take effect.")
    print()
    
    # Show the convenience function
    print("Using get_settings() function:")
    print("-" * 70)
    settings_via_func = get_settings()
    print(f"Same instance: {settings_via_func is settings}")
    print()
    
    print("=" * 70)
    print("Configuration loaded successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
