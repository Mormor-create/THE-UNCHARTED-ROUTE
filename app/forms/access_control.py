"""
===============================================================================
The Uncharted Route
Access Control Forms
===============================================================================

Forms for managing system users and administrative access.

Responsibilities
----------------
• Search users
• Filter users by role
• Filter users by account status
• Filter users by verification status
• Change user roles
• Activate/deactivate user accounts
• Verify/unverify accounts
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    BooleanField,
    SubmitField,
    HiddenField,
)
from wtforms.validators import (
    Optional,
    Length,
    DataRequired,
)


# =============================================================================
# Role Choices
# =============================================================================

ACCESS_ROLE_CHOICES = [
    ("", "All Roles"),
    ("admin", "Administrator"),
    ("staff", "Staff"),
    ("guide", "Guide"),
    ("customer", "Customer"),
]


MANAGEMENT_ROLE_CHOICES = [
    ("admin", "Administrator"),
    ("staff", "Staff"),
    ("guide", "Guide"),
    ("customer", "Customer"),
]


# =============================================================================
# Access Control Filter Form
# =============================================================================

class AccessControlFilterForm(FlaskForm):
    """
    Filter and search system users.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(
                max=255
            ),
        ],
    )

    role = SelectField(
        "Role",
        choices=ACCESS_ROLE_CHOICES,
        validators=[
            Optional()
        ],
    )

    active = SelectField(
        "Account Status",
        choices=[
            ("", "All Statuses"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        validators=[
            Optional()
        ],
    )

    verified = SelectField(
        "Verification",
        choices=[
            ("", "All"),
            ("verified", "Verified"),
            ("unverified", "Unverified"),
        ],
        validators=[
            Optional()
        ],
    )

    submit = SubmitField(
        "Filter Users"
    )


# =============================================================================
# User Role Form
# =============================================================================

class UserRoleForm(FlaskForm):
    """
    Change the role assigned to a user.
    """

    role = SelectField(
        "Role",
        choices=MANAGEMENT_ROLE_CHOICES,
        validators=[
            DataRequired(
                message="Please select a role."
            ),
        ],
    )

    submit = SubmitField(
        "Update Role"
    )


# =============================================================================
# User Status Form
# =============================================================================

class UserStatusForm(FlaskForm):
    """
    Activate or deactivate a user account.
    """

    active = BooleanField(
        "Account Active"
    )

    submit = SubmitField(
        "Save Status"
    )


# =============================================================================
# User Verification Form
# =============================================================================

class UserVerificationForm(FlaskForm):
    """
    Verify or unverify a user account.
    """

    verified = BooleanField(
        "Account Verified"
    )

    submit = SubmitField(
        "Save Verification"
    )


# =============================================================================
# User Access Action Form
# =============================================================================

class UserAccessActionForm(FlaskForm):
    """
    Generic action form used by access-control actions.
    """

    action = HiddenField(
        "Action",
        validators=[
            DataRequired()
        ],
    )

    submit = SubmitField(
        "Apply"
    )