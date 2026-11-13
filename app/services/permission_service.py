"""
===============================================================================
The Uncharted Route
Permission Service
===============================================================================

Centralized authorization and permission management.

The application uses two concepts:

1. Roles
   - customer
   - guide
   - staff
   - admin

2. Permissions
   - Fine-grained actions assigned to roles.

Routes should use permission decorators rather than implementing role checks
directly.

This keeps authorization logic centralized and makes the application easier
to extend as The Uncharted Route grows.
===============================================================================
"""

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


# =============================================================================
# Roles
# =============================================================================
CUSTOMER_ROLE = "customer"
GUIDE_ROLE = "guide"
STAFF_ROLE = "staff"
ADMIN_ROLE = "admin"

ALL_ROLES = {
    CUSTOMER_ROLE,
    GUIDE_ROLE,
    STAFF_ROLE,
    ADMIN_ROLE,
}

# =============================================================================
# Permissions
# =============================================================================

# -----------------------------------------------------------------------------
# Administration
# -----------------------------------------------------------------------------
MANAGE_USERS = "manage_users"
MANAGE_ROLES = "manage_roles"
MANAGE_SETTINGS = "manage_settings"

# -----------------------------------------------------------------------------
# Experiences
# -----------------------------------------------------------------------------
MANAGE_EXPERIENCES = "manage_experiences"

# -----------------------------------------------------------------------------
# Destinations
# -----------------------------------------------------------------------------
MANAGE_DESTINATIONS = "manage_destinations"

# -----------------------------------------------------------------------------
# Safaris
# -----------------------------------------------------------------------------
MANAGE_SAFARIS = "manage_safaris"


# -----------------------------------------------------------------------------
# Bookings
# -----------------------------------------------------------------------------
MANAGE_BOOKINGS = "manage_bookings"
CREATE_BOOKING = "create_booking"
VIEW_OWN_BOOKINGS = "view_own_bookings"
CANCEL_OWN_BOOKING = "cancel_own_booking"

# -----------------------------------------------------------------------------
# Media
# -----------------------------------------------------------------------------

MANAGE_MEDIA = "manage_media"


# -----------------------------------------------------------------------------
# Blog
# -----------------------------------------------------------------------------

MANAGE_BLOG = "manage_blog"


# -----------------------------------------------------------------------------
# Guides / Operations
# -----------------------------------------------------------------------------

VIEW_ASSIGNED_TOURS = "view_assigned_tours"

UPDATE_TOUR_STATUS = "update_tour_status"


# -----------------------------------------------------------------------------
# Reviews
# -----------------------------------------------------------------------------

WRITE_REVIEW = "write_review"


# -----------------------------------------------------------------------------
# Customer Profile
# -----------------------------------------------------------------------------

MANAGE_PROFILE = "manage_profile"

MANAGE_OWN_DOCUMENTS = "manage_own_documents"


# =============================================================================
# Permission Registry
# =============================================================================

ALL_PERMISSIONS = {
    MANAGE_USERS,
    MANAGE_ROLES,
    MANAGE_SETTINGS,

    MANAGE_EXPERIENCES,
    MANAGE_DESTINATIONS,
    MANAGE_SAFARIS,

    MANAGE_BOOKINGS,
    CREATE_BOOKING,
    VIEW_OWN_BOOKINGS,
    CANCEL_OWN_BOOKING,

    MANAGE_MEDIA,

    MANAGE_BLOG,

    VIEW_ASSIGNED_TOURS,
    UPDATE_TOUR_STATUS,

    WRITE_REVIEW,

    MANAGE_PROFILE,
    MANAGE_OWN_DOCUMENTS,
}


# =============================================================================
# Role Permission Matrix
# =============================================================================

ROLE_PERMISSIONS = {

    # =========================================================================
    # Administrator
    # =========================================================================

    ADMIN_ROLE: {
        MANAGE_USERS,
        MANAGE_ROLES,
        MANAGE_SETTINGS,

        MANAGE_EXPERIENCES,
        MANAGE_DESTINATIONS,
        MANAGE_SAFARIS,

        MANAGE_BOOKINGS,

        MANAGE_MEDIA,

        MANAGE_BLOG,

        VIEW_ASSIGNED_TOURS,
        UPDATE_TOUR_STATUS,

        CREATE_BOOKING,
        VIEW_OWN_BOOKINGS,
        CANCEL_OWN_BOOKING,

        WRITE_REVIEW,

        MANAGE_PROFILE,
        MANAGE_OWN_DOCUMENTS,
    },

    # =========================================================================
    # Staff
    # =========================================================================

    STAFF_ROLE: {
        MANAGE_EXPERIENCES,
        MANAGE_DESTINATIONS,
        MANAGE_SAFARIS,
        MANAGE_BOOKINGS,
        MANAGE_BLOG,
        MANAGE_MEDIA,
    },

    # =========================================================================
    # Guide
    # =========================================================================

    GUIDE_ROLE: {
        VIEW_ASSIGNED_TOURS,
        UPDATE_TOUR_STATUS,
    },

    # =========================================================================
    # Customer
    # =========================================================================

    CUSTOMER_ROLE: {
        CREATE_BOOKING,
        VIEW_OWN_BOOKINGS,
        CANCEL_OWN_BOOKING,

        WRITE_REVIEW,

        MANAGE_PROFILE,
        MANAGE_OWN_DOCUMENTS,
    },
}


# =============================================================================
# Role Normalization
# =============================================================================

def normalize_role(role):
    """
    Normalize a role value.

    Parameters
    ----------
    role : str | None
        User role.

    Returns
    -------
    str
        Normalized lowercase role.
    """

    if not role:
        return ""

    return str(role).strip().lower()


# =============================================================================
# Permission Normalization
# =============================================================================

def normalize_permission(permission):
    """
    Normalize a permission value.
    """

    if not permission:
        return ""

    return str(permission).strip().lower()


# =============================================================================
# Role Checks
# =============================================================================

def has_role(user, *roles):
    """
    Determine whether a user has one of the supplied roles.
    """

    if user is None:
        return False

    user_role = normalize_role(
        getattr(user, "role", None)
    )

    allowed_roles = {
        normalize_role(role)
        for role in roles
    }

    return user_role in allowed_roles


def is_customer(user=None):
    """
    Determine whether a user is a customer.
    """

    user = user or current_user

    return has_role(
        user,
        CUSTOMER_ROLE,
    )


def is_guide(user=None):
    """
    Determine whether a user is a guide.
    """

    user = user or current_user

    return has_role(
        user,
        GUIDE_ROLE,
    )


def is_staff(user=None):
    """
    Determine whether a user has staff-level access.

    Administrators are included.
    """

    user = user or current_user

    return has_role(
        user,
        STAFF_ROLE,
        ADMIN_ROLE,
    )


def is_admin(user=None):
    """
    Determine whether a user is an administrator.
    """

    user = user or current_user

    return has_role(
        user,
        ADMIN_ROLE,
    )


# =============================================================================
# Permission Resolution
# =============================================================================

def get_user_permissions(user=None):
    """
    Return all permissions granted to a user.

    Administrators receive every registered permission.
    """

    user = user or current_user

    if user is None:
        return set()

    role = normalize_role(
        getattr(user, "role", None)
    )

    if role == ADMIN_ROLE:
        return set(ALL_PERMISSIONS)

    return set(
        ROLE_PERMISSIONS.get(
            role,
            set(),
        )
    )


def has_permission(user, permission):
    """
    Determine whether a user has a specific permission.

    Parameters
    ----------
    user : User
        User to check.

    permission : str
        Permission to check.

    Returns
    -------
    bool
        True if permission is granted.
    """

    if user is None:
        return False

    normalized_permission = normalize_permission(
        permission
    )

    if normalized_permission not in ALL_PERMISSIONS:
        return False

    return normalized_permission in get_user_permissions(
        user
    )


def has_any_permission(user, *permissions):
    """
    Determine whether a user has at least one of the supplied permissions.
    """

    return any(
        has_permission(
            user,
            permission,
        )
        for permission in permissions
    )


def has_all_permissions(user, *permissions):
    """
    Determine whether a user has all supplied permissions.
    """

    return all(
        has_permission(
            user,
            permission,
        )
        for permission in permissions
    )


# =============================================================================
# Permission Decorator
# =============================================================================

def permission_required(permission):
    """
    Require the authenticated user to have a specific permission.

    Example
    -------
    @permission_required(MANAGE_EXPERIENCES)
    def manage_experiences():
        ...
    """

    normalized_permission = normalize_permission(
        permission
    )

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapped(*args, **kwargs):

            if not has_permission(
                current_user,
                normalized_permission,
            ):
                abort(403)

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


# =============================================================================
# Multiple Permission Decorators
# =============================================================================

def any_permission_required(*permissions):
    """
    Require at least one of the supplied permissions.
    """

    normalized_permissions = {
        normalize_permission(permission)
        for permission in permissions
    }

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapped(*args, **kwargs):

            if not any(
                has_permission(
                    current_user,
                    permission,
                )
                for permission in normalized_permissions
            ):
                abort(403)

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


def all_permissions_required(*permissions):
    """
    Require all supplied permissions.
    """

    normalized_permissions = {
        normalize_permission(permission)
        for permission in permissions
    }

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapped(*args, **kwargs):

            if not all(
                has_permission(
                    current_user,
                    permission,
                )
                for permission in normalized_permissions
            ):
                abort(403)

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


# =============================================================================
# Role Decorators
# =============================================================================

def roles_required(*roles):
    """
    Require one of the supplied roles.

    Authentication is required before the role is checked.
    """

    normalized_roles = {
        normalize_role(role)
        for role in roles
    }

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapped(*args, **kwargs):

            user_role = normalize_role(
                getattr(
                    current_user,
                    "role",
                    None,
                )
            )

            if user_role not in normalized_roles:
                abort(403)

            return function(
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


def admin_required(function):
    """
    Require administrator privileges.
    """

    return roles_required(
        ADMIN_ROLE,
    )(function)


def staff_required(function):
    """
    Require staff-level privileges.

    Administrators are included.
    """

    return roles_required(
        ADMIN_ROLE,
        STAFF_ROLE,
    )(function)


def guide_required(function):
    """
    Require guide privileges.

    Administrators are also accepted.
    """

    return roles_required(
        ADMIN_ROLE,
        GUIDE_ROLE,
    )(function)


def staff_or_guide_required(function):
    """
    Require staff, guide, or administrator access.
    """

    return roles_required(
        ADMIN_ROLE,
        STAFF_ROLE,
        GUIDE_ROLE,
    )(function)


def customer_required(function):
    """
    Require a customer account.
    """

    return roles_required(
        CUSTOMER_ROLE,
    )(function)


# =============================================================================
# Convenience Permission Decorators
# =============================================================================

manage_users_required = permission_required(
    MANAGE_USERS
)

manage_roles_required = permission_required(
    MANAGE_ROLES
)

manage_settings_required = permission_required(
    MANAGE_SETTINGS
)

manage_experiences_required = permission_required(
    MANAGE_EXPERIENCES
)

manage_destinations_required = permission_required(
    MANAGE_DESTINATIONS
)

manage_safaris_required = permission_required(
    MANAGE_SAFARIS
)

manage_bookings_required = permission_required(
    MANAGE_BOOKINGS
)

manage_media_required = permission_required(
    MANAGE_MEDIA
)

manage_blog_required = permission_required(
    MANAGE_BLOG
)

view_assigned_tours_required = permission_required(
    VIEW_ASSIGNED_TOURS
)

update_tour_status_required = permission_required(
    UPDATE_TOUR_STATUS
)

create_booking_required = permission_required(
    CREATE_BOOKING
)

view_own_bookings_required = permission_required(
    VIEW_OWN_BOOKINGS
)

cancel_own_booking_required = permission_required(
    CANCEL_OWN_BOOKING
)

write_review_required = permission_required(
    WRITE_REVIEW
)

manage_profile_required = permission_required(
    MANAGE_PROFILE
)

manage_own_documents_required = permission_required(
    MANAGE_OWN_DOCUMENTS
)