"""
===============================================================================
The Uncharted Route
Stay Inquiry Form
===============================================================================
"""

from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


class StayInquiryForm(FlaskForm):
    """Collect accommodation inquiry details."""

    # -------------------------------------------------------------------------
    # Guest details
    # -------------------------------------------------------------------------

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    country = StringField(
        "Country of Residence",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    # -------------------------------------------------------------------------
    # Requested stay
    # -------------------------------------------------------------------------

    check_in = DateField(
        "Check-in Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(),
        ],
    )

    check_out = DateField(
        "Check-out Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(),
        ],
    )

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            InputRequired(),
            NumberRange(min=1, max=100),
        ],
    )

    children = IntegerField(
        "Children",
        default=0,
        validators=[
            InputRequired(),
            NumberRange(min=0, max=100),
        ],
    )

    # -------------------------------------------------------------------------
    # Room context
    # -------------------------------------------------------------------------
    #
    # This is populated automatically when the visitor arrives from a
    # specific room page.
    #
    # It remains optional because the customer may submit a general stay
    # inquiry without selecting a particular room.
    # -------------------------------------------------------------------------

    room_id = HiddenField(
        validators=[
            Optional(),
        ],
    )

    # -------------------------------------------------------------------------
    # Currency
    # -------------------------------------------------------------------------

    preferred_currency = SelectField(
        "Preferred Currency",
        choices=[
            ("KES", "Kenyan Shilling (KES)"),
            ("USD", "US Dollar (USD)"),
            ("EUR", "Euro (EUR)"),
            ("GBP", "British Pound (GBP)"),
        ],
        default="KES",
        validators=[
            DataRequired(),
        ],
    )

    # -------------------------------------------------------------------------
    # Additional information
    # -------------------------------------------------------------------------

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional(),
            Length(max=5000),
        ],
    )

    submit = SubmitField(
        "Send Stay Inquiry"
    )

    # -------------------------------------------------------------------------
    # Date validation
    # -------------------------------------------------------------------------

    def validate_check_in(self, field):
        """Prevent guests from selecting a past check-in date."""

        if field.data and field.data < date.today():
            raise ValidationError(
                "Check-in date cannot be in the past."
            )

    def validate_check_out(self, field):
        """Ensure check-out occurs after check-in."""

        if field.data and self.check_in.data:

            if field.data <= self.check_in.data:
                raise ValidationError(
                    "Check-out must be after check-in."
                )