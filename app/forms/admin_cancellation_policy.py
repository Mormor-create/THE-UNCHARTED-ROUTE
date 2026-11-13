"""
===============================================================================
The Uncharted Route
Admin Cancellation Policy Forms
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange, InputRequired
)


# =============================================================================
# Base Cancellation Policy Form
# =============================================================================

class CancellationPolicyForm(FlaskForm):
    """
    Shared create/edit form for cancellation policies.
    """

    # =========================================================================
    # Basic Information
    # =========================================================================

    name = StringField(
        "Policy Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    slug = StringField(
        "Slug",
        validators=[
            Optional(),
            Length(max=120)
        ]
    )

    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    full_policy = TextAreaField(
        "Full Policy",
        validators=[
            DataRequired()
        ]
    )

    # =========================================================================
    # Refund Rules
    # =========================================================================

    full_refund_days = IntegerField(
        "Full Refund Days",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=365)
        ]
    )

    partial_refund_days = IntegerField(
        "Partial Refund Days",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=365)
        ]
    )

    partial_refund_percentage = IntegerField(
        "Partial Refund Percentage",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=100)
        ]
    )

    no_refund_days = IntegerField(
        "No Refund Days",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=365)
        ]
    )

    # =========================================================================
    # Booking Changes
    # =========================================================================

    date_changes_allowed = BooleanField(
        "Date Changes Allowed",
        default=True
    )

    name_changes_allowed = BooleanField(
        "Name Changes Allowed",
        default=True
    )

    transferable_booking = BooleanField(
        "Transferable Booking",
        default=False
    )

    # =========================================================================
    # Additional Information
    # =========================================================================

    notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional()
        ]
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = BooleanField(
        "Active",
        default=True
    )

    default_policy = BooleanField(
        "Default Policy",
        default=False
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Cancellation Policy"
    )


# =============================================================================
# Action Form
# =============================================================================

class CancellationPolicyActionForm(FlaskForm):
    """
    Used for POST actions such as activate, deactivate,
    set default and delete.
    """

    submit = SubmitField(
        "Confirm"
    )