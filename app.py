"""
===============================================================================
The Uncharted Route
Application Launcher
The application factory lives inside app/__init__.py.
This file exists as the simple entry point for local development and
environments that expect a root-level app.py.
"""
from app import create_app

# =============================================================================
# Application Instance
# =============================================================================
app = create_app()

# =============================================================================
# Development Server
# =============================================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=app.config.get("DEBUG", False),)