"""Smoke tests to verify basic backend functionality."""

import sys
from pathlib import Path


def test_python_version():
    """Verify Python version is 3.11 or higher."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"


def test_backend_app_import():
    """Verify backend.app package can be imported."""
    # Add backend directory to path to allow absolute imports
    backend_path = Path(__file__).parent.parent
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    # Import the app package
    import app
    assert app is not None
    assert hasattr(app, '__name__')


def test_required_dependencies():
    """Verify critical dependencies are installed."""
    required_modules = ['pydantic', 'fastapi', 'uvicorn', 'pytest', 'ruff']
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            assert False, f"Required module '{module_name}' not available: {e}"
