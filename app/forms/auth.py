"""
===============================================================================
The Uncharted Route
Authentication Forms
===============================================================================

WTForms used by the authentication system.

Supports:

- Login
- Registration
- Forgot password
- Password reset
"""

from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
)

# =============================================================================
# Login Form
# =============================================================================
class LoginForm(FlaskForm):
    """
    Authentication form for existing users.
    """

    identity = StringField(
        "Username or Email",
        validators=[
            DataRequired(
                message="Please enter your username or email."
            )
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(
                message="Please enter your password."
            )
        ],
    )

    submit = SubmitField(
        "Sign In"
    )


# =============================================================================
# Registration Form
# =============================================================================
class RegistrationForm(FlaskForm):
    """
    Form for creating a new user account.
    """
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=100,),],)
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=100,
            ),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=80,
            ),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=255,
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                max=128,
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField("Create Account")

# =============================================================================
# Forgot Password Form
# =============================================================================
class ForgotPasswordForm(FlaskForm):
    """
    Form used to request a password reset.
    """
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=255,
            ),
        ],
    )
    submit = SubmitField("Send Reset Link")

# =============================================================================
# Reset Password Form
# =============================================================================
class ResetPasswordForm(FlaskForm):
    """
    Form used to set a new password.
    """
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                max=128,
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField(
        "Reset Password"
    )


__all__ = [
    "LoginForm",
    "RegistrationForm",
    "ForgotPasswordForm",
    "ResetPasswordForm",
]