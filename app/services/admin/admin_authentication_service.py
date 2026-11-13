"""
===============================================================================
The Uncharted Route
Administrative Authentication Service
===============================================================================

Business logic for administrator authentication and administration-created
internal accounts.

Responsibilities
----------------
• Authenticate administrator users
• Verify administrator account status
• Record successful administrator logins
• Determine administrative eligibility
• Create staff accounts
• Create guide accounts
• Generate administrator password-reset tokens
• Verify administrator password-reset tokens
• Reset administrator passwords

Security Model
--------------
The application uses one User model and one Flask-Login authentication system.

Public registration:
    customer

Administrative account creation:
    administrator → staff
    administrator → guide

Administrator accounts are NOT created through the administrative user
creation form.

Routes should handle HTTP concerns only.
Forms should handle input validation.
Models should handle persistence and model behavior.
This service handles administrative business logic.
===============================================================================
"""

from datetime import datetime
from app.models import User
from app.services.auth_service import (
    authenticate_user,
    generate_password_reset_token,
    record_login,
    reset_password,
    verify_password_reset_token,)
from extensions import db

# =============================================================================
# Administrator Authentication
# =============================================================================
def authenticate_admin(identity, password):
    """
    Authenticate a user and verify administrator access.
    Parameters
    ----------
    identity : str
        Username or email address.
    password : str
        Plain-text password supplied during login
    Returns
    -------
    User | None
        The authenticated administrator when credentials and access are valid.

        Returns None when:
        • identity is missing
        • password is missing
        • the user does not exist
        • the password is incorrect
        • the account is inactive
        • the user is not an administrator
    """

    if not identity or not password:
        return None

    user = authenticate_user(
        identity=identity,
        password=password,
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not user.is_admin:
        return None

    return user


# =============================================================================
# Successful Administrator Login
# =============================================================================
def complete_admin_login(user):
    """
    Complete the business logic associated with a successful admin login.

    Records the administrator's latest successful login.

    Parameters
    ----------
    user : User
        Authenticated administrator.

    Returns
    -------
    User | None
        Updated administrator user.
    """

    if user is None:
        return None

    if not user.is_admin:
        return None

    if not user.is_active:
        return None

    return record_login(user)


# =============================================================================
# Administrator Eligibility
# =============================================================================
def can_access_admin(user):
    """
    Determine whether a user is eligible to access the admin system.

    Parameters
    ----------
    user : User
        User being evaluated.

    Returns
    -------
    bool
        True when the user is an active administrator.
    """

    if user is None:
        return False

    return bool(
        user.is_active
        and user.is_admin)

# =============================================================================
# Internal User Creation
# =============================================================================
def create_internal_user(
    acting_admin,
    first_name,
    last_name,
    username,
    email,
    password,
    role,
):
    """
    Create a staff or guide account on behalf of an administrator.

    Security
    --------
    Only an active administrator may call this operation.

    Allowed roles
    -------------
    • staff
    • guide

    The role ``admin`` is deliberately rejected.

    Parameters
    ----------
    acting_admin : User
        Administrator performing the operation.

    first_name : str
        New user's first name.

    last_name : str
        New user's last name.

    username : str
        New user's username.

    email : str
        New user's email address.

    password : str
        Initial password.

    role : str
        Internal account role.

    Returns
    -------
    User
        Newly created staff or guide.

    Raises
    ------
    PermissionError
        When the acting user is not an active administrator.

    ValueError
        When the requested role is not allowed.
    """

    if not can_access_admin(acting_admin):
        raise PermissionError(
            "Only an active administrator may create internal users."
        )

    normalized_role = (
        role.strip().lower()
        if role
        else ""
    )

    if normalized_role not in {
        "staff",
        "guide",
    }:
        raise ValueError(
            "Only staff and guide accounts may be created "
            "through administrative registration."
        )

    if not password:
        raise ValueError(
            "A password is required."
        )

    # -------------------------------------------------------------------------
    # Normalize supplied account information.
    # -------------------------------------------------------------------------

    normalized_username = (
        username.strip()
        if username
        else ""
    )

    normalized_email = (
        email.strip().lower()
        if email
        else ""
    )

    # -------------------------------------------------------------------------
    # Protect against duplicate accounts at the service layer as well.
    #
    # The form already performs validation, but service-level checks prevent
    # other callers from bypassing those form validations.
    # -------------------------------------------------------------------------

    existing_username = User.query.filter(
        User.username.ilike(normalized_username)
    ).first()

    if existing_username is not None:
        raise ValueError(
            "That username is already in use."
        )

    existing_email = User.query.filter(
        User.email.ilike(normalized_email)
    ).first()

    if existing_email is not None:
        raise ValueError(
            "That email address is already registered."
        )

    # -------------------------------------------------------------------------
    # Create the internal user.
    # -------------------------------------------------------------------------
    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        username=normalized_username,
        email=normalized_email,
        role=normalized_role,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

# =============================================================================
# Administrator Password Reset Token
# =============================================================================
def generate_admin_password_reset_token(user):
    """
    Generate a password-reset token for an administrator.

    Only administrator accounts may receive administrative reset tokens.

    Parameters
    ----------
    user : User
        Administrator requesting a password reset.

    Returns
    -------
    str | None
        Signed reset token, or None when the user is not eligible.
    """

    if not can_access_admin(user):
        return None
    return generate_password_reset_token(user)

# =============================================================================
# Verify Administrator Reset Token
# =============================================================================
def verify_admin_password_reset_token(token):
    """
    Verify a password-reset token and ensure it belongs to an administrator.

    Parameters
    ----------
    token : str
        Signed password-reset token.

    Returns
    -------
    User | None
        Active administrator associated with the token.

        Returns None when:
        • the token is invalid
        • the token has expired
        • the user does not exist
        • the user is inactive
        • the user is not an administrator
    """

    if not token:
        return None

    user = verify_password_reset_token(
        token
    )

    if not can_access_admin(user):
        return None

    return user


# =============================================================================
# Reset Administrator Password
# =============================================================================
def reset_admin_password(user, password):
    """
    Reset an administrator's password.

    Parameters
    ----------
    user : User
        Administrator whose password is being changed.

    password : str
        New plain-text password.

    Returns
    -------
    User | None
        Updated administrator.
    """

    if not can_access_admin(user):
        return None
    return reset_password(
        user=user,
        password=password,)
# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "authenticate_admin",
    "complete_admin_login",
    "can_access_admin",
    "create_internal_user",
    "generate_admin_password_reset_token",
    "verify_admin_password_reset_token",
    "reset_admin_password",]