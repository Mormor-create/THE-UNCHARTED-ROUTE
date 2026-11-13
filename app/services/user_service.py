"""
===============================================================================
The Uncharted Route
User Service
===============================================================================
Provides business logic for application users.
Responsibilities

• Create users
• Retrieve users
• Find users by ID, username, or email
• Update user profiles
• Change passwords
• Verify user accounts
• Activate / deactivate accounts
• Manage user roles
• Record login activity
• Check account status
• Prevent duplicate usernames and emails

Authentication and session management remain the responsibility of
auth_service.py.
"""

from datetime import datetime
from sqlalchemy import or_
from extensions import db
from app.models import User
# =============================================================================
# User Creation
# =============================================================================
def create_user(
    first_name,
    last_name,
    username,
    email,
    password,
    role="customer",
    phone=None,
    profile_image=None,
    bio=None,
    is_verified=False,):
    """
    Create and persist a new user.
    Raises:
        ValueError:
            If the username or email already exists.
    """
    username = username.strip()
    email = email.strip().lower()
    if user_exists_by_username(username):
        raise ValueError("A user with this username already exists.")

    if user_exists_by_email(email):
        raise ValueError("A user with this email already exists.")

    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        username=username,
        email=email,
        role=role.strip().lower(),
        phone=phone,
        profile_image=profile_image,
        bio=bio,
        is_verified=is_verified,
        is_active=True,)

    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

# =============================================================================
# User Retrieval
# =============================================================================
def get_user_by_id(user_id):
    """
    Retrieve a user by primary key.
    """
    return db.session.get(User, user_id)

def get_user_by_username(username):
    """
    Retrieve a user by username.
    """

    if not username:
        return None
    return User.query.filter(
        db.func.lower(User.username) == username.strip().lower()
    ).first()

def get_user_by_email(email):
    """
    Retrieve a user by email address.
    """
    if not email:
        return None
    return User.query.filter(
        db.func.lower(User.email) == email.strip().lower()).first()

def get_user_by_login(identifier):
    """
    Retrieve a user using either username or email.
    Useful for login flows that allow users to enter either value.
    """
    if not identifier:
        return None

    identifier = identifier.strip().lower()
    return User.query.filter(
        or_(
            db.func.lower(User.username) == identifier,
            db.func.lower(User.email) == identifier,
        )).first()

# =============================================================================
# Existence Checks
# =============================================================================
def user_exists_by_username(username):
    """
    Determine whether a username is already registered.
    """
    return get_user_by_username(username) is not None

def user_exists_by_email(email):
    """
    Determine whether an email address is already registered.
    """
    return get_user_by_email(email) is not None

def user_exists(
    username=None,
    email=None,
    exclude_user_id=None,
):
    """
    Determine whether a username or email is already in use.

    An existing user can be excluded, which is useful when updating
    an existing account.
    """

    query = User.query
    conditions = []
    if username:
        conditions.append(
            db.func.lower(User.username) == username.strip().lower())

    if email:
        conditions.append(
            db.func.lower(User.email) == email.strip().lower())

    if not conditions:
        return False

    query = query.filter(or_(*conditions))
    if exclude_user_id is not None:
        query = query.filter(
            User.id != exclude_user_id
        )

    return query.first() is not None


def update_user(
    user,
    first_name=None,
    last_name=None,
    username=None,
    email=None,
    phone=None,
    bio=None,
    profile_image=None,
    password=None,
    is_active=None,
    is_verified=None,
):
    """
    Update a user's account/profile information.

    Only values explicitly supplied are updated.

    Password:
        If password is None or blank, the existing password is preserved.

    Account status:
        is_active and is_verified are only changed when explicitly supplied.

    Raises:
        ValueError:
            If the user is invalid or the new username/email belongs
            to another user.
    """

    if not user:
        raise ValueError("A valid user is required.")

    # ---------------------------------------------------------------
    # Username
    # ---------------------------------------------------------------
    if username is not None:
        username = username.strip()

        if not username:
            raise ValueError("Username is required.")

        if user_exists(
            username=username,
            exclude_user_id=user.id,
        ):
            raise ValueError(
                "A user with this username already exists.")

        user.username = username

    # ---------------------------------------------------------------
    # Email
    # ---------------------------------------------------------------
    if email is not None:
        email = email.strip().lower()

        if not email:
            raise ValueError("Email is required.")

        if user_exists(
            email=email,
            exclude_user_id=user.id,):
            raise ValueError("A user with this email already exists.")
        user.email = email

    # ---------------------------------------------------------------
    # Personal information
    # ---------------------------------------------------------------
    if first_name is not None:
        first_name = first_name.strip()

        if not first_name:
            raise ValueError("First name is required.")
        user.first_name = first_name

    if last_name is not None:
        last_name = last_name.strip()

        if not last_name:
            raise ValueError("Last name is required.")
        user.last_name = last_name

    if phone is not None:
        user.phone = phone.strip() if phone else None

    if bio is not None:
        user.bio = bio

    if profile_image is not None:
        user.profile_image = profile_image

    # ---------------------------------------------------------------
    # Password
    # ---------------------------------------------------------------
    if password is not None:
        password = password.strip()

        if password:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long.")
            user.set_password(password)

    # ---------------------------------------------------------------
    # Account status
    # ---------------------------------------------------------------
    if is_active is not None:
        user.is_active = bool(is_active)

    if is_verified is not None:
        user.is_verified = bool(is_verified)

    # ---------------------------------------------------------------
    # Persist
    # ---------------------------------------------------------------
    db.session.commit()
    return user
# =============================================================================
# Password Management
# =============================================================================

def set_user_password(user, password):
    """
    Set a new password for a user.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    user.set_password(password)

    db.session.commit()

    return user


def check_user_password(user, password):
    """
    Verify a user's password.
    """

    if not user or not password:
        return False

    return user.check_password(password)


def change_password(
    user,
    current_password,
    new_password,
):
    """
    Change a user's password after verifying the current password.

    Raises:
        ValueError:
            If the current password is incorrect or the new password
            is invalid.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    if not user.check_password(current_password):
        raise ValueError(
            "Current password is incorrect."
        )

    if not new_password:
        raise ValueError(
            "New password cannot be empty."
        )

    user.set_password(new_password)
    db.session.commit()
    return user

# =============================================================================
# Account Status
# =============================================================================
def activate_user(user):
    """
    Activate a user account.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    user.is_active = True

    db.session.commit()

    return user


def deactivate_user(user):
    """
    Deactivate a user account.

    The user remains in the database but can no longer be treated
    as an active account.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    user.is_active = False

    db.session.commit()

    return user


def verify_user(user):
    """
    Mark a user account as verified.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    user.is_verified = True

    db.session.commit()

    return user


def unverify_user(user):
    """
    Remove a user's verification status.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    user.is_verified = False

    db.session.commit()

    return user


# =============================================================================
# Login Activity
# =============================================================================

def record_login(user):
    """
    Record the user's most recent login.
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    user.last_login = datetime.utcnow()

    db.session.commit()

    return user


# =============================================================================
# Role Management
# =============================================================================

VALID_ROLES = {
    "customer",
    "guide",
    "staff",
    "admin",
}


def set_user_role(user, role):
    """
    Assign a role to a user.

    Valid roles:

    • customer
    • guide
    • staff
    • admin
    """

    if not user:
        raise ValueError(
            "A valid user is required."
        )

    role = role.strip().lower()

    if role not in VALID_ROLES:
        raise ValueError(
            f"Invalid user role: {role}"
        )

    user.role = role

    db.session.commit()

    return user


def get_users_by_role(role):
    """
    Return all users assigned to a specific role.
    """

    if not role:
        return []

    role = role.strip().lower()

    return User.query.filter(
        db.func.lower(User.role) == role
    ).order_by(
        User.created_at.desc()
    ).all()


# =============================================================================
# User Lists
# =============================================================================

def get_all_users():
    """
    Return all users ordered by creation date.
    """

    return User.query.order_by(
        User.created_at.desc()
    ).all()


def get_active_users():
    """
    Return all active users.
    """

    return User.query.filter_by(
        is_active=True
    ).order_by(
        User.created_at.desc()
    ).all()


def get_verified_users():
    """
    Return all verified users.
    """

    return User.query.filter_by(
        is_verified=True
    ).order_by(
        User.created_at.desc()
    ).all()


# =============================================================================
# User Search
# =============================================================================
def search_users(search_term):
    """
    Search users by:
    • First name
    • Last name
    • Username
    • Email
    """

    if not search_term:
        return []

    search_term = search_term.strip()
    pattern = f"%{search_term}%"
    return User.query.filter(
        or_(
            User.first_name.ilike(pattern),
            User.last_name.ilike(pattern),
            User.username.ilike(pattern),
            User.email.ilike(pattern),
        )
    ).order_by(User.created_at.desc()).all()

# =============================================================================
# Administrator User Management
# =============================================================================
def get_users(
    search=None,
    role=None,
    active=None,
    verified=None,):
    """
    Retrieve users using optional administrator filters.

    Args:
        search:
            Searches first name, last name, username, and email.

        role:
            Filters by customer, guide, staff, or admin.

        active:
            True for active users, False for inactive users.

        verified:
            True for verified users, False for unverified users.

    Returns:
        list[User]: Matching users ordered by newest first.
    """

    query = User.query

    if search:
        search = search.strip()

        if search:
            pattern = f"%{search}%"

            query = query.filter(
                or_(
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )

    if role:
        query = query.filter(
            db.func.lower(User.role) == role.strip().lower()
        )

    if active is not None:
        query = query.filter(
            User.is_active.is_(active)
        )

    if verified is not None:
        query = query.filter(
            User.is_verified.is_(verified)
        )

    return query.order_by(
        User.created_at.desc()
    ).all()


def get_user_statistics():
    """
    Return high-level user statistics for the administrator users page.
    """

    return {
        "total": User.query.count(),

        "active": User.query.filter(
            User.is_active.is_(True)
        ).count(),

        "inactive": User.query.filter(
            User.is_active.is_(False)
        ).count(),

        "verified": User.query.filter(
            User.is_verified.is_(True)
        ).count(),

        "unverified": User.query.filter(
            User.is_verified.is_(False)
        ).count(),

        "admins": User.query.filter(
            db.func.lower(User.role) == "admin"
        ).count(),

        "staff": User.query.filter(
            db.func.lower(User.role) == "staff"
        ).count(),

        "guides": User.query.filter(
            db.func.lower(User.role) == "guide"
        ).count(),

        "customers": User.query.filter(
            db.func.lower(User.role) == "customer").count(),}

def get_recent_users(limit=10):
    """
    Return the most recently created users.
    """

    return User.query.order_by(
        User.created_at.desc()
    ).limit(limit).all()

# =============================================================================
# Account State Helpers
# =============================================================================
def is_active_user(user):
    """
    Determine whether a user account is active.
    """
    return bool(user and user.is_active)

def is_verified_user(user):
    """
    Determine whether a user account is verified.
    """
    return bool(user and user.is_verified)

def can_login(user):
    """
    Determine whether a user is currently allowed to log in.
    An account must be:
    • Present
    • Active
    • Verified
    """
    if not user:
        return False
    return (
        user.is_active
        and user.is_verified)

# =============================================================================
# Delete User
# =============================================================================
def delete_user(user):
    """
    Permanently delete a user.
    This should normally be restricted to administrators because
    deletion is irreversible.
    """
    if not user:
        raise ValueError("A valid user is required.")
    db.session.delete(user)
    db.session.commit()
    return True

# =============================================================================
# Representation Helper
# =============================================================================
def user_summary(user):
    """
    Return a safe, non-sensitive summary of a user.
    Password hashes are intentionally never exposed.
    """
    if not user:
        return None

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "profile_image": user.profile_image,
        "role": user.normalized_role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "last_login": user.last_login,}