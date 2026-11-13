"""
===============================================================================
The Uncharted Route
Administrative Stay Booking Forms
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    SubmitField,
    StringField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


# =============================================================================
# Stay Booking Form
# =============================================================================

class AdminStayBookingForm(FlaskForm):
    """
    Create or edit an accommodation component attached to a master Booking.
    """

    stay_id = SelectField(
        "Stay",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a stay."
            ),
        ],
    )

    room_id = SelectField(
        "Room",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a room."
            ),
        ],
    )

    check_in = DateField(
        "Check-in",
        validators=[
            DataRequired(
                message="Please select a check-in date."
            ),
        ],
    )

    check_out = DateField(
        "Check-out",
        validators=[
            DataRequired(
                message="Please select a check-out date."
            ),
        ],
    )

    rooms = IntegerField(
        "Rooms",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(
                min=1,
                message="At least one room is required.",
            ),
        ],
    )

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                message="Adults cannot be negative.",
            ),
        ],
    )

    children = IntegerField(
        "Children",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Children cannot be negative.",
            ),
        ],
    )

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Infants cannot be negative.",
            ),
        ],
    )

    meal_plan = StringField(
        "Meal Plan",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional(),
            Length(max=3000),
        ],
    )

    notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional(),
            Length(max=5000),
        ],
    )

    submit = SubmitField(
        "Save Stay Booking"
    )

    def validate_check_out(self, field):
        """
        Ensure checkout occurs after check-in.
        """

        if (
            field.data
            and self.check_in.data
            and field.data <= self.check_in.data
        ):
            raise ValidationError(
                "Check-out must be after check-in."
            )

    def validate(self, extra_validators=None):
        """
        Run standard validation and ensure at least one guest exists.
        """

        if not super().validate(
            extra_validators=extra_validators
        ):
            return False

        total_guests = (
            (self.adults.data or 0)
            + (self.children.data or 0)
            + (self.infants.data or 0)
        )

        if total_guests < 1:

            self.adults.errors.append(
                "At least one guest is required."
            )

            return False

        return True


# =============================================================================
# Filter Form
# =============================================================================

class AdminStayBookingFilterForm(FlaskForm):
    """
    Stay booking filtering form.
    """

    stay_id = SelectField(
        "Stay",
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    room_id = SelectField(
        "Room",
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    check_in_from = DateField(
        "Check-in From",
        validators=[
            Optional(),
        ],
    )

    check_in_to = DateField(
        "Check-in To",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Filter"
    )


__all__ = [
    "AdminStayBookingForm",
    "AdminStayBookingFilterForm",
]