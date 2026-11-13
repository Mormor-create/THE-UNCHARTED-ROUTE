"""
===============================================================================
The Uncharted Route
Application Configuration
===============================================================================
Centralized configuration for all application environments.
Supported environments:
    • Development
    • Testing
    • Production
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# =============================================================================
# Base Directory
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(
    parents=True,
    exist_ok=True,)

# =============================================================================
# Environment
# =============================================================================
#
# Always load the project's .env explicitly.
#
# IMPORTANT:
# override=True ensures that a stale DATABASE_URL already present in the
# Python process cannot override the project's actual .env value.
#

ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(
        ENV_FILE,
        override=True,)

# =============================================================================
# Database URL Helper
# =============================================================================
def get_database_url():
    """
    Return the database URL used by the application.

    SQLite URLs are normalized so that:

        sqlite:///instance/file.db

    does not accidentally become:

        instance/instance/file.db

    The preferred local database is always:

        instance/uncharted_route.db
    """

    database_url = os.getenv("DATABASE_URL")

    # -------------------------------------------------------------------------
    # No DATABASE_URL supplied
    # -------------------------------------------------------------------------
    if not database_url:
        return f"sqlite:///{(INSTANCE_DIR / 'uncharted_route.db').as_posix()}"

    database_url = database_url.strip()

    # -------------------------------------------------------------------------
    # Normalize the project's local SQLite database
    # -------------------------------------------------------------------------
    #
    # We deliberately treat these relative forms as referring to the
    # project's instance directory.
    #

    relative_sqlite_urls = {
        "sqlite:///instance/uncharted_route.db",
        "sqlite:///instance\\uncharted_route.db",
    }

    if database_url in relative_sqlite_urls:
        return f"sqlite:///{(INSTANCE_DIR / 'uncharted_route.db').as_posix()}"

    # -------------------------------------------------------------------------
    # Normalize the old accidental Fashion database reference.
    #
    # This prevents an old environment variable from silently redirecting
    # the application to fashion.db.
    #

    if database_url in {
        "sqlite:///instance/fashion.db",
        "sqlite:///instance\\fashion.db",
    }:
        return f"sqlite:///{(INSTANCE_DIR / 'uncharted_route.db').as_posix()}"

    return database_url


# =============================================================================
# Base Configuration
# =============================================================================
class Config:
    """
    Base configuration shared by all environments.
    """

    # -------------------------------------------------------------------------
    # General
    # -------------------------------------------------------------------------
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production",)
    APP_NAME = "The Uncharted Route"

    APP_URL = os.getenv(
        "APP_URL",
        "http://127.0.0.1:5001",
    )

    DEBUG = False
    TESTING = False

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    DATABASE_PATH = INSTANCE_DIR / "uncharted_route.db"
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,}

    # -------------------------------------------------------------------------
    # Uploads
    # -------------------------------------------------------------------------
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    EXPERIENCE_IMAGE_FOLDER = (
        UPLOAD_FOLDER / "experiences"
    )
    DESTINATION_IMAGE_FOLDER = (
        UPLOAD_FOLDER / "destinations"
    )
    BLOG_IMAGE_FOLDER = (
        UPLOAD_FOLDER / "blog"
    )
    GALLERY_FOLDER = (
        UPLOAD_FOLDER / "gallery"
    )
    USER_IMAGE_FOLDER = (
        UPLOAD_FOLDER / "users"
    )

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    EXPERIENCES_PER_PAGE = 12
    BLOG_POSTS_PER_PAGE = 9
    DESTINATIONS_PER_PAGE = 12
    REVIEWS_PER_PAGE = 10

    # -------------------------------------------------------------------------
    # Booking
    # -------------------------------------------------------------------------
    DEFAULT_CURRENCY = "KES"
    BOOKING_REFERENCE_PREFIX = "TUR"

    # -------------------------------------------------------------------------
    # Security
    # -------------------------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True

    # -------------------------------------------------------------------------
    # Mail
    # -------------------------------------------------------------------------
    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "",)

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            587,
        )
    )

    MAIL_USE_TLS = os.getenv(
        "MAIL_USE_TLS",
        "true",
    ).lower() == "true"

    MAIL_USE_SSL = os.getenv(
        "MAIL_USE_SSL",
        "false",
    ).lower() == "true"

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",)

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",)

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "The Uncharted Route <noreply@unchartedroute.com>",)

    # -------------------------------------------------------------------------
    # Admin
    # -------------------------------------------------------------------------
    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@unchartedroute.com",)

    # -------------------------------------------------------------------------
    # Company Information
    # -------------------------------------------------------------------------
    COMPANY_NAME = "The Uncharted Route"
    COMPANY_PHONE = "+254 700 000 000"
    COMPANY_EMAIL = "info@unchartedroute.com"
    COMPANY_ADDRESS = "Nairobi, Kenya"

    # -------------------------------------------------------------------------
    # Social Media
    # -------------------------------------------------------------------------
    FACEBOOK_URL = os.getenv(
        "FACEBOOK_URL",
        "",)

    INSTAGRAM_URL = os.getenv(
        "INSTAGRAM_URL",
        "",)

    LINKEDIN_URL = os.getenv(
        "LINKEDIN_URL",
        "",)

    YOUTUBE_URL = os.getenv(
        "YOUTUBE_URL","",)

    X_URL = os.getenv(
        "X_URL",
        "",)

    # -------------------------------------------------------------------------
    # Maps
    # -------------------------------------------------------------------------
    GOOGLE_MAPS_API_KEY = os.getenv(
        "GOOGLE_MAPS_API_KEY",
        "",)

    # -------------------------------------------------------------------------
    # SEO
    # -------------------------------------------------------------------------
    DEFAULT_META_DESCRIPTION = (
        "Luxury safaris, wildlife adventures, coastal escapes, "
        "corporate travel and unforgettable experiences across Kenya.")
    DEFAULT_META_IMAGE = "images/seo/default.jpg"

    # -------------------------------------------------------------------------
    # Cache
    # -------------------------------------------------------------------------
    CACHE_TIMEOUT = 300

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",)

    # -------------------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------------------
    ENABLE_REVIEWS = os.getenv(
        "ENABLE_REVIEWS",
        "true",
    ).lower() == "true"

    ENABLE_NEWSLETTER = os.getenv(
        "ENABLE_NEWSLETTER",
        "true",
    ).lower() == "true"

    ENABLE_BLOG = os.getenv(
        "ENABLE_BLOG",
        "true",
    ).lower() == "true"

    ENABLE_ONLINE_PAYMENTS = os.getenv(
        "ENABLE_ONLINE_PAYMENTS",
        "false",
    ).lower() == "true"

    ENABLE_WISHLISTS = os.getenv(
        "ENABLE_WISHLISTS",
        "false",
    ).lower() == "true"


# =============================================================================
# Development
# =============================================================================
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

# =============================================================================
# Testing
# =============================================================================
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# =============================================================================
# Production
# =============================================================================
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# =============================================================================
# Configuration Mapping
# =============================================================================
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,}