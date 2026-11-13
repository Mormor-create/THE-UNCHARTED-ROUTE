"""
===============================================================================
The Uncharted Route
Administrative Destination Booking Forms
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    ValidationError,
)


# =============================================================================
# Destination Booking Form
# =============================================================================

class AdminDestinationBookingForm(FlaskForm):
    """
    Create or edit a destination journey booking component.
    """

    journey_id = SelectField(
        "Destination Journey",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a destination journey."
            ),
        ],
    )

    start_date = DateField(
        "Start Date",
        validators=[
            DataRequired(
                message="Please select a journey start date."
            ),
        ],
    )

    end_date = DateField(
        "End Date",
        validators=[
            Optional(),
        ],
    )

    pickup_location = StringField(
        "Pickup Location",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    dropoff_location = StringField(
        "Drop-off Location",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional(),
            Length(max=3000),
        ],
    )

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional(),
            Length(max=5000),
        ],
    )

    submit = SubmitField(
        "Save Destination Booking"
    )

    def validate_end_date(self, field):
        """
        Ensure the end date does not precede the start date.
        """

        if (
            field.data
            and self.start_date.data
            and field.data < self.start_date.data
        ):
            raise ValidationError(
                "The end date cannot be before the start date."
            )


# =============================================================================
# Filter Form
# =============================================================================

class AdminDestinationBookingFilterForm(FlaskForm):
    """
    Destination booking filtering form.
    """

    journey_id = SelectField(
        "Journey",
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    start_date_from = DateField(
        "Start Date From",
        validators=[
            Optional(),
        ],
    )

    start_date_to = DateField(
        "Start Date To",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Filter"
    )


__all__ = [
    "AdminDestinationBookingForm",
    "AdminDestinationBookingFilterForm",
]