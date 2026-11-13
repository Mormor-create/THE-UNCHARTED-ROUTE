"""
===============================================================================
The Uncharted Route
Authentication Service
===============================================================================

Business logic for authentication-related operations.

Responsibilities
----------------
• Authenticate users
• Create customer accounts
• Update login information
• Generate password-reset tokens
• Verify password-reset tokens
• Reset user passwords

Routes should handle HTTP concerns only.
Forms should handle input validation.
Models should handle persistence and model behavior.
This service handles authentication business logic.
"""

from datetime import datetime
from flask import current_app
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,)
from app.models import User
from extensions import db


# =============================================================================
# Token Configuration
# =============================================================================
PASSWORD_RESET_SALT = (
    "uncharted-route-password-reset"
)
PASSWORD_RESET_MAX_AGE = 3600

# =============================================================================
# User Authentication
# =============================================================================
def authenticate_user(identity, password):
    """
    Authenticate a user using either username or email.

    Parameters
    ----------
    identity : str
        Username or email address.

    password : str
        Plain-text password supplied during login.

    Returns
    -------
    User | None
        The authenticated user when credentials are valid.

        Returns None when:
        • the user does not exist
        • the password is incorrect
    """

    if not identity or not password:
        return None

    identity = identity.strip()

    user = User.query.filter(
        db.or_(
            User.username.ilike(identity),
            User.email.ilike(identity),
        )
    ).first()

    if user is None:
        return None

    if not user.check_password(password):
        return None

    return user

# =============================================================================
# Account Status
# =============================================================================
def is_user_active(user):
    """
    Determine whether a user account is active.

    Returns
    -------
    bool
        True when the account is active.
    """
    if user is None:
        return False
    return bool(user.is_active)

# =============================================================================
# Login Tracking
# =============================================================================
def record_login(user):
    """
    Record the user's latest successful login.

    Parameters
    ----------
    user : User
        Authenticated user.

    Returns
    -------
    User
        Updated user.
    """

    if user is None:
        return None
    user.last_login = datetime.utcnow()
    db.session.commit()
    return user

# =============================================================================
# Password Reset Token Helpers
# =============================================================================
def generate_password_reset_token(user):
    """
    Generate a signed password-reset token.

    Parameters
    ----------
    user : User
        User requesting a password reset.

    Returns
    -------
    str
        Signed password-reset token.
    """

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    return serializer.dumps(
        user.id,
        salt=PASSWORD_RESET_SALT,
    )


def verify_password_reset_token(token):
    """
    Verify a password-reset token.

    Parameters
    ----------
    token : str
        Signed password-reset token.

    Returns
    -------
    User | None
        The corresponding user when the token is valid.

        Returns None when:
        • the token is invalid
        • the token has expired
        • the referenced user does not exist
    """

    if not token:
        return None

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    try:
        user_id = serializer.loads(
            token,
            salt=PASSWORD_RESET_SALT,
            max_age=PASSWORD_RESET_MAX_AGE,
        )

    except (
        BadSignature,
        SignatureExpired,
    ):
        return None

    return db.session.get(
        User,
        user_id,
    )


# =============================================================================
# Password Reset
# =============================================================================

def reset_password(user, password):
    """
    Set a new password for a user.

    Parameters
    ----------
    user : User
        User whose password is being changed.

    password : str
        New plain-text password.

    Returns
    -------
    User
        Updated user.
    """

    if user is None:
        return None

    if not password:
        raise ValueError(
            "A password is required."
        )

    user.set_password(password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return user

# =============================================================================
# User Creation
# =============================================================================
def create_user(
    first_name,
    last_name,
    username,
    email,
    password,
):
    """
    Create a new standard customer account.

    Public registration must never allow the caller to select
    an administrative or staff role.

    Parameters
    ----------
    first_name : str
        User's first name.

    last_name : str
        User's last name.

    username : str
        Unique username.

    email : str
        Unique email address.

    password : str
        Plain-text password.

    Returns
    -------
    User
        Newly created user.
    """

    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        username=username.strip(),
        email=email.strip().lower(),

        # -----------------------------------------------------------------
        # Public registrations are always customers.
        # Privileged roles must be assigned separately by administrators.
        # -----------------------------------------------------------------

        role="customer",

        is_active=True,
        is_verified=False,

        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    user.set_password(password)

    db.session.add(user)

    db.session.commit()

    return user