"""
===============================================================================
The Uncharted Route
Administrator User Management Forms
===============================================================================

Forms used by administrators to manage individual application users.

Responsibilities
----------------
• Edit user profile information
• Change user roles
• Activate / deactivate accounts
• Verify / unverify accounts
• Reset a user's password

Security-sensitive actions remain protected by the administrator routes.
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    BooleanField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
)


# =============================================================================
# Role Choices
# =============================================================================

USER_ROLE_CHOICES = [
    ("customer", "Customer"),
    ("guide", "Guide"),
    ("staff", "Staff"),
    ("admin", "Administrator"),
]


# =============================================================================
# User Profile Form
# =============================================================================

class AdminUserProfileForm(FlaskForm):
    """
    Edit a user's basic profile information.
    """

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(
                message="First name is required."
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
                message="Last name is required."
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
                message="Username is required."
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
                message="Email address is required."
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

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(
                max=30,
                message="Phone number is too long.",
            ),
        ],
    )

    bio = TextAreaField(
        "Bio",
        validators=[
            Optional(),
            Length(
                max=2000,
                message="Bio must not exceed 2,000 characters.",
            ),
        ],
    )

    submit = SubmitField(
        "Save Profile"
    )


# =============================================================================
# User Role Form
# =============================================================================

class AdminUserRoleForm(FlaskForm):
    """
    Change a user's application role.
    """

    role = SelectField(
        "Role",
        choices=USER_ROLE_CHOICES,
        validators=[
            DataRequired(
                message="Please select a role."
            )
        ],
    )

    submit = SubmitField(
        "Update Role"
    )


# =============================================================================
# User Status Form
# =============================================================================

class AdminUserStatusForm(FlaskForm):
    """
    Activate or deactivate a user account.
    """

    is_active = BooleanField(
        "Account Active"
    )

    submit = SubmitField(
        "Save Status"
    )


# =============================================================================
# User Verification Form
# =============================================================================

class AdminUserVerificationForm(FlaskForm):
    """
    Mark a user account as verified or unverified.
    """

    is_verified = BooleanField(
        "Account Verified"
    )

    submit = SubmitField(
        "Save Verification"
    )


# =============================================================================
# Administrator Password Reset Form
# =============================================================================

class AdminUserPasswordForm(FlaskForm):
    """
    Allow an administrator to assign a new password to a user.

    The user's existing password is intentionally not requested here.
    """

    new_password = PasswordField(
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
                "new_password",
                message="The passwords do not match.",
            ),
        ],
    )

    submit = SubmitField(
        "Reset Password"
    )