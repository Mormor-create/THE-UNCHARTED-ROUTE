"""
===============================================================================
The Uncharted Route
Administrator Profile Forms
===============================================================================

Forms for managing the currently authenticated administrator's account.

Responsibilities
----------------
• Edit administrator profile information
• Change administrator password
• Validate email and phone information
• Protect password changes with the current password
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    EqualTo,
    ValidationError,
)

from app.models import User


# =============================================================================
# Administrator Profile Form
# =============================================================================

class AdminProfileForm(FlaskForm):
    """
    Form for editing the authenticated administrator's profile.
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
                message="First name must be between 2 and 100 characters."
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
                message="Last name must be between 2 and 100 characters."
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
                max=100,
                message="Username must be between 3 and 100 characters."
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
                max=255
            ),
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(
                max=50,
                message="Phone number is too long."
            ),
        ],
    )

    bio = TextAreaField(
        "Bio",
        validators=[
            Optional(),
            Length(
                max=2000,
                message="Bio must not exceed 2,000 characters."
            ),
        ],
    )

    submit = SubmitField(
        "Save Profile"
    )

    def validate_username(self, field):
        """
        Ensure the username is unique, excluding the current user.
        """

        if not self.username.data:
            return

        from flask_login import current_user

        existing = User.query.filter(
            User.username == self.username.data.strip(),
            User.id != current_user.id,
        ).first()

        if existing:
            raise ValidationError(
                "That username is already in use."
            )

    def validate_email(self, field):
        """
        Ensure the email address is unique, excluding the current user.
        """

        if not self.email.data:
            return

        from flask_login import current_user

        existing = User.query.filter(
            User.email == self.email.data.strip().lower(),
            User.id != current_user.id,
        ).first()

        if existing:
            raise ValidationError(
                "That email address is already in use."
            )


# =============================================================================
# Administrator Password Form
# =============================================================================

class AdminPasswordForm(FlaskForm):
    """
    Form for changing the authenticated administrator's password.
    """

    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired(
                message="Please enter your current password."
            ),
        ],
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(
                message="Please enter a new password."
            ),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters."
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(
                message="Please confirm your new password."
            ),
            EqualTo(
                "new_password",
                message="The passwords do not match."
            ),
        ],
    )

    submit = SubmitField(
        "Change Password"
    )

    def validate_current_password(self, field):
        """
        Verify the administrator's existing password.
        """

        from flask_login import current_user

        if not current_user.check_password(field.data):
            raise ValidationError(
                "The current password is incorrect."
            )