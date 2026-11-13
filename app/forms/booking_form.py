"""
===============================================================================
The Uncharted Route
Public Experience Booking Form
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    NumberRange,
    Optional,
    ValidationError,)

class BookingForm(FlaskForm):
    """
    Public booking form for Experience booking.
    Pricing, capacity, availability, and final totals are handled by the
    Booking Service.
    """
    # =========================================================================
    # Experience Selection
    # =========================================================================
    experience_id = SelectField(
        "Experience",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select an experience."
            )
        ],
    )

    pricing_id = SelectField(
        "Pricing",
        coerce=int,
        validators=[
            Optional()
        ],
        default=0,
    )

    experience_level = SelectField(
        "Experience Level",
        choices=[
            ("", "Select experience level"),
            ("Explorer", "Explorer"),
            ("Signature", "Signature"),
            ("Luxury", "Luxury"),
            ("Bespoke", "Bespoke"),
        ],
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Lead Traveller
    # =========================================================================

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(
                message="First name is required."
            )
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(
                message="Last name is required."
            )
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
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional()
        ],
    )

    nationality = StringField(
        "Nationality",
        validators=[
            Optional()
        ],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Traveller Counts
    # =========================================================================

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            NumberRange(
                min=0,
                message="Adult count cannot be negative."
            )
        ],
    )

    children = IntegerField(
        "Children",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Child count cannot be negative."
            )
        ],
    )

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Infant count cannot be negative."
            )
        ],
    )

    seniors = IntegerField(
        "Seniors",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Senior count cannot be negative."
            )
        ],
    )

    students = IntegerField(
        "Students",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Student count cannot be negative."
            )
        ],
    )

    # =========================================================================
    # Emergency Contact
    # =========================================================================

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional()
        ],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional()
        ],
    )

    emergency_contact_relationship = StringField(
        "Relationship",
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Requirements
    # =========================================================================

    dietary_requirements = TextAreaField(
        "Dietary Requirements",
        validators=[
            Optional()
        ],
    )

    medical_information = TextAreaField(
        "Medical Information",
        validators=[
            Optional()
        ],
    )

    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[
            Optional()
        ],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional()
        ],
    )

    customer_notes = TextAreaField(
        "Additional Notes",
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Add-ons
    # =========================================================================

    addon_ids = SelectMultipleField(
        "Add-ons",
        coerce=int,
        validators=[
            Optional()
        ],
    )

    # =========================================================================
    # Terms
    # =========================================================================
    agree_to_terms = BooleanField(
        "I agree to the booking terms and conditions.",
        validators=[
            DataRequired(
                message="You must agree to the booking terms."
            )
    ],)
    submit = SubmitField(
        "Continue Booking"
    )

    # =========================================================================
    # Validation
    # =========================================================================
    def validate(self, extra_validators=None):
        """
        Run normal WTForms validation and ensure the booking contains
        at least one traveller.
        """

        if not super().validate(
            extra_validators=extra_validators
        ):
            return False

        adults = self.adults.data or 0
        children = self.children.data or 0
        infants = self.infants.data or 0
        seniors = self.seniors.data or 0
        students = self.students.data or 0

        total = (
            adults
            + children
            + infants
            + seniors
            + students)
        if total < 1:
            raise_validation = ValidationError(
                "At least one traveller is required.")
            self.adults.errors.append(
                str(raise_validation))
            return False
        return True