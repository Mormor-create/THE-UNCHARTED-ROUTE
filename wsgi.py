"""
===============================================================================
The Uncharted Route
WSGI Entry Point
===============================================================================

Production WSGI entry point.

Compatible with:

    Gunicorn
    Render
    Railway
    Fly.io
    Other WSGI-compatible hosting platforms

The application factory lives in:

    app/__init__.py
"""

from app import create_app


# =============================================================================
# Application Instance
# =============================================================================

app = create_app()