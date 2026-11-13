"""
===============================================================================
The Uncharted Route
Public Stay Booking Form
===============================================================================
"""
from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    NumberRange,
    Optional,)

class PublicStayBookingForm(FlaskForm):
    """Public booking request form for a specific accommodation."""
    # -------------------------------------------------------------------------
    # Accommodation
    # -------------------------------------------------------------------------
    room_id = SelectField(
        "Room",
        coerce=int,
        validators=[
            DataRequired(message="Please select a room."),],)

    rooms = IntegerField(
        "Number of Rooms",
        default=1,
        validators=[
            InputRequired(
                message="Please select the number of rooms."),
            NumberRange(
                min=1,
                message="Select at least one room.",
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Stay Dates
    # -------------------------------------------------------------------------

    check_in = DateField(
        "Check-in",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Please choose your check-in date."
            ),
        ],
    )

    check_out = DateField(
        "Check-out",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Please choose your check-out date."
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Guest Occupancy
    # InputRequired allows zero while rejecting an empty submission.
    # -------------------------------------------------------------------------

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            InputRequired(
                message="Please enter the number of adults."
            ),
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
            InputRequired(
                message="Please enter the number of children (enter 0 if none)."
            ),
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
            InputRequired(
                message="Please enter the number of infants (enter 0 if none)."
            ),
            NumberRange(
                min=0,
                message="Infants cannot be negative.",
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Guest Information
    # -------------------------------------------------------------------------

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(
                message="Please enter your first name."
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(
                message="Please enter your last name."
            ),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="Please enter your email address."
            ),
            Email(
                message="Please enter a valid email address."
            ),
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[Optional()],
    )

    nationality = StringField(
        "Nationality",
        validators=[Optional()],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[Optional()],
    )

    # -------------------------------------------------------------------------
    # Stay Preferences
    # -------------------------------------------------------------------------

    meal_plan = SelectField(
        "Meal Plan",
        choices=[
            ("", "Use the room's standard meal plan"),
            ("Room Only", "Room Only"),
            ("Bed & Breakfast", "Bed & Breakfast"),
            ("Half Board", "Half Board"),
            ("Full Board", "Full Board"),
            ("All Inclusive", "All Inclusive"),
        ],
        validators=[Optional()],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[Optional()],
    )

    customer_notes = TextAreaField(
        "Additional Notes",
        validators=[Optional()],
    )

    # -------------------------------------------------------------------------
    # Terms and Conditions
    # -------------------------------------------------------------------------

    agree_to_terms = BooleanField(
        "I agree to the booking terms and conditions.",
        validators=[
            DataRequired(
                message="You must agree to the booking terms to continue."
            ),
        ],
    )

    submit = SubmitField("Request This Stay")

    # -------------------------------------------------------------------------
    # Custom Validation
    # -------------------------------------------------------------------------

    def validate(self, extra_validators=None):
        """Validate guest numbers and booking dates."""

        if not super().validate(
            extra_validators=extra_validators
        ):
            return False

        adults = self.adults.data
        children = self.children.data
        infants = self.infants.data

        adults = adults if adults is not None else 0
        children = children if children is not None else 0
        infants = infants if infants is not None else 0

        # At least one guest must be included.
        if adults + children + infants < 1:
            self.adults.errors.append(
                "At least one guest is required."
            )
            return False

        # Check-in cannot be in the past.
        if self.check_in.data and self.check_out.data:

            if self.check_in.data < date.today():
                self.check_in.errors.append(
                    "Check-in cannot be in the past."
                )
                return False

            # Check-out must be after check-in.
            if self.check_out.data <= self.check_in.data:
                self.check_out.errors.append(
                    "Check-out must be after check-in."
                )
                return False

        return True