"""
===============================================================================
The Uncharted Route
Booking Traveller Forms
===============================================================================
"""
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    Email,)

class BookingTravellerForm(FlaskForm):
    """Create or update a traveller attached to a central booking."""

    booking_id = SelectField(
        "Booking",
        coerce=int,
        validators=[DataRequired(message="Please select a booking.")],
    )

    traveller_reference = StringField(
        "Traveller Reference",
        validators=[Optional(), Length(max=40)],
    )

    traveller_number = IntegerField(
        "Traveller Number",
        validators=[Optional(), NumberRange(min=1)],
    )

    first_name = StringField(
        "First Name",
        validators=[DataRequired(), Length(max=100)],
    )

    middle_name = StringField(
        "Middle Name",
        validators=[Optional(), Length(max=100)],
    )

    last_name = StringField(
        "Last Name",
        validators=[DataRequired(), Length(max=100)],
    )

    date_of_birth = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    traveller_type = SelectField(
        "Traveller Type",
        choices=[
            ("adult", "Adult"),
            ("child", "Child"),
            ("infant", "Infant"),
            ("student", "Student"),
            ("senior", "Senior"),
        ],
        validators=[DataRequired()],
    )

    nationality = StringField(
        "Nationality",
        validators=[Optional(), Length(max=100)],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[Optional(), Length(max=100)],
    )

    email = StringField(
        "Email Address",
        validators=[Optional(), Email(), Length(max=255)],
    )

    phone = StringField(
        "Phone Number",
        validators=[Optional(), Length(max=50)],
    )

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[Optional(), Length(max=200)],
    )

    emergency_contact_relationship = StringField(
        "Relationship to Traveller",
        validators=[Optional(), Length(max=100)],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[Optional(), Length(max=50)],
    )

    emergency_contact_email = StringField(
        "Emergency Contact Email",
        validators=[Optional(), Email(), Length(max=255)],
    )

    dietary_requirements = TextAreaField(
        "Dietary Requirements",
        validators=[Optional()],
    )

    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[Optional()],
    )

    medical_information = TextAreaField(
        "Medical Information",
        validators=[Optional()],
    )

    special_requirements = TextAreaField(
        "Other Special Requirements",
        validators=[Optional()],
    )

    waiver_required = BooleanField("Waiver Required")

    waiver_status = SelectField(
        "Waiver Status",
        choices=[
            ("not_required", "Not Required"),
            ("pending", "Pending"),
            ("signed", "Signed"),
            ("rejected", "Rejected"),
        ],
        validators=[DataRequired()],
    )

    status = SelectField(
        "Record Status",
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        validators=[DataRequired()],
    )

    notes = TextAreaField(
        "Internal Notes",
        validators=[Optional()],
    )

    submit = SubmitField("Save Traveller")