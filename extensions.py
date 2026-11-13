"""
===============================================================================
The Uncharted Route
Extensions
===============================================================================

This module initializes all Flask extensions used throughout the application.

Keeping extensions in one location avoids circular imports and makes the
application factory much cleaner.
"""

import logging

from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


# =============================================================================
# Database
# =============================================================================

db = SQLAlchemy()


# =============================================================================
# Database Migrations
# =============================================================================

migrate = Migrate()


# =============================================================================
# Authentication
# =============================================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Please log in to continue."
)

login_manager.login_message_category = "warning"


# =============================================================================
# Email
# =============================================================================

mail = Mail()


# =============================================================================
# CSRF Protection
# =============================================================================

csrf = CSRFProtect()


# =============================================================================
# Logging
# =============================================================================

logger = logging.getLogger(
    "uncharted_route"
)
