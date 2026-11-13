"""
===============================================================================
The Uncharted Route
Admin Access Control
===============================================================================

Decorators used to protect administrator-only routes.

Responsibilities
----------------
• Require an authenticated user
• Require administrator-level access
• Provide a consistent access-control boundary for the admin blueprint

Authentication itself is handled by Flask-Login.

Authorization is handled here using the User model's existing role helpers.

The admin system deliberately does not create a second authentication system.
"""

"""
The Uncharted Route
Administrator Access Control
"""

from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def admin_required(view_function):
    """
    Allow only active administrator accounts to access a route.
    """
    @wraps(view_function)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not current_user.is_active:
            abort(403)

        if not current_user.is_admin:
            abort(403)

        return view_function(*args, **kwargs)
    return wrapped_view

__all__ = [
    "admin_required",
]