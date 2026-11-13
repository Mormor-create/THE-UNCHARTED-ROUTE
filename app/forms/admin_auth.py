"""
===============================================================================
The Uncharted Route
Administrative Authentication Forms
===============================================================================

WTForms used by the administrative authentication system.

Supports
--------
• Administrator login
• Administrator-created staff accounts
• Administrator-created guide accounts
• Administrator password-reset requests
• Administrator password resets

Security Model
--------------
Public registration creates customer accounts only.

Administrative registration is deliberately different:

    Administrator
          │
          ├── Staff account
          └── Guide account

Administrators cannot create another administrator account through this form.

Administrator accounts should be provisioned through controlled internal
processes such as a seed command, deployment procedure, or direct administrative
database operation.

The forms handle input validation only.
Business logic belongs in services.
HTTP concerns belong in routes.
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from app.models import User


# =============================================================================
# Administrator Login Form
# =============================================================================
class AdminLoginForm(FlaskForm):
    """
    Authentication form for administrator accounts.

    Administrators may authenticate using either their username
    or email address.
    """

    identity = StringField(
        "Username or Email",
        validators=[
            DataRequired(
                message="Please enter your username or email."
            ),
            Length(
                max=255,
                message="Username or email is too long.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(
                message="Please enter your password."
            ),
            Length(
                max=128,
                message="Password is too long.",
            ),
        ],
    )

    submit = SubmitField(
        "Sign In",
    )

# =============================================================================
# Administrator User Creation Form
# =============================================================================
class AdminUserCreateForm(FlaskForm):
    """
    Form used by an administrator to create an internal user account.

    Supported account types
    -----------------------
    • Staff
    • Guide

    Administrator accounts are intentionally excluded.

    This form should only be exposed through administrator-protected routes.
    The route/service layer must also enforce administrator authorization.
    """

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(
                message="Please enter the first name."
            ),
            Length(
                min=2,
                max=100,
                message="First name must be between 2 and 100 characters.",
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(
                message="Please enter the last name."
            ),
            Length(
                min=2,
                max=100,
                message="Last name must be between 2 and 100 characters.",
            ),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(
                message="Please enter a username."
            ),
            Length(
                min=3,
                max=80,
                message="Username must be between 3 and 80 characters.",
            ),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="Please enter an email address."
            ),
            Email(
                message="Please enter a valid email address."
            ),
            Length(
                max=255,
                message="Email address is too long.",
            ),
        ],
    )

    role = SelectField(
        "Account Type",
        choices=[
            ("staff", "Staff"),
            ("guide", "Guide"),
        ],
        validators=[
            DataRequired(
                message="Please select an account type."
            ),
        ],
    )

    password = PasswordField(
        "Temporary Password",
        validators=[
            DataRequired(
                message="Please enter a temporary password."
            ),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Temporary Password",
        validators=[
            DataRequired(
                message="Please confirm the temporary password."
            ),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField(
        "Create User",
    )

    # =========================================================================
    # Username Validation
    # =========================================================================
    def validate_username(self, field):
        """
        Ensure the username is not already registered.
        """
        username = field.data.strip()
        existing_user = User.query.filter(
            User.username.ilike(username)
        ).first()
        if existing_user is not None:
            raise ValidationError(
                "That username is already in use."
            )

    # =========================================================================
    # Email Validation
    # =========================================================================
    def validate_email(self, field):
        """
        Ensure the email address is not already registered.
        """

        email = field.data.strip().lower()

        existing_user = User.query.filter(
            User.email.ilike(email)
        ).first()

        if existing_user is not None:
            raise ValidationError(
                "That email address is already registered."
            )


# =============================================================================
# Administrator Forgot Password Form
# =============================================================================
class AdminForgotPasswordForm(FlaskForm):
    """
    Form used by administrators to request a password-reset link.

    The route must never reveal whether a particular email belongs to
    an administrator.
    """
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="Please enter your email address."
            ),
            Email(
                message="Please enter a valid email address."
            ),
            Length(
                max=255,
                message="Email address is too long.",
            ),
        ],
    )

    submit = SubmitField(
        "Send Reset Link",
    )

# =============================================================================
# Administrator Reset Password Form
# =============================================================================

class AdminResetPasswordForm(FlaskForm):
    """
    Form used to set a new administrator password.
    """

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(
                message="Please enter a new password."
            ),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(
                message="Please confirm the new password."
            ),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField(
        "Reset Password",
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AdminLoginForm",
    "AdminUserCreateForm",
    "AdminForgotPasswordForm",
    "AdminResetPasswordForm",
]