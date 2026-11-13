"""
===============================================================================
The Uncharted Route
Safari Booking Forms
===============================================================================
"""
from datetime import date
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,)

class SafariBookingForm(FlaskForm):
    """Create or edit a central booking and its safari-specific details."""
    # Customer
    first_name = StringField("First Name", validators=[
        DataRequired(), Length(max=100)
    ])
    last_name = StringField("Last Name", validators=[
        DataRequired(), Length(max=100)
    ])
    email = StringField("Email Address", validators=[
        DataRequired(), Email(), Length(max=255)
    ])
    phone = StringField("Phone Number", validators=[
        Optional(), Length(max=50)
    ])
    nationality = StringField("Nationality", validators=[
        Optional(), Length(max=100)
    ])
    country_of_residence = StringField("Country of Residence", validators=[
        Optional(), Length(max=100)
    ])

    # Package selection
    safari_destination_id = SelectField(
        "Safari Destination", coerce=int, validators=[Optional()]
    )
    property_id = SelectField(
        "Property / Camp / Lodge", coerce=int, validators=[Optional()]
    )
    package_option_id = SelectField(
        "Safari Package", coerce=int, validators=[DataRequired()]
    )
    package_rate_id = SelectField(
        "Package Rate", coerce=int, validators=[Optional()]
    )

    # Travel dates
    start_date = DateField(
        "Arrival / Start Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
    )
    end_date = DateField(
        "Departure / End Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
    )
    duration_days = IntegerField(
        "Duration (Days)", default=1,
        validators=[DataRequired(), NumberRange(min=1)]
    )
    duration_nights = IntegerField(
        "Duration (Nights)", default=0,
        validators=[DataRequired(), NumberRange(min=0)]
    )

    # Occupancy
    rooms_required = IntegerField(
        "Rooms Required", default=1,
        validators=[DataRequired(), NumberRange(min=1)]
    )
    adults = IntegerField(
        "Adults", default=1,
        validators=[DataRequired(), NumberRange(min=0)]
    )
    children = IntegerField(
        "Children", default=0,
        validators=[DataRequired(), NumberRange(min=0)]
    )
    infants = IntegerField(
        "Infants", default=0,
        validators=[DataRequired(), NumberRange(min=0)]
    )
    rooming_preferences = TextAreaField(
        "Rooming Preferences", validators=[Optional(), Length(max=5000)]
    )

    # Rate
    rate_name_snapshot = StringField(
        "Rate Name", validators=[Optional(), Length(max=150)]
    )
    rate_basis = SelectField(
        "Rate Basis",
        choices=[
            ("per_person_sharing", "Per Person Sharing"),
            ("per_person", "Per Person"),
            ("per_room", "Per Room"),
            ("per_vehicle", "Per Vehicle"),
            ("per_group", "Per Group"),
            ("total_package", "Total Package"),
        ],
        validators=[DataRequired()],
    )
    unit_rate = StringField(
        "Unit Rate", default="0.00",
        validators=[DataRequired(), Length(max=30)]
    )
    quantity = IntegerField(
        "Rate Quantity", default=1,
        validators=[DataRequired(), NumberRange(min=1)]
    )
    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),
        ],
        default="USD",
        validators=[DataRequired()],
    )

    # Central booking
    status = SelectField(
        "Booking Status",
        choices=[
            ("pending", "Pending"),
            ("awaiting_payment", "Awaiting Payment"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        validators=[DataRequired()],
    )
    payment_status = SelectField(
        "Payment Status",
        choices=[
            ("unpaid", "Unpaid"),
            ("pending", "Pending"),
            ("partially_paid", "Partially Paid"),
            ("paid", "Paid"),
            ("not_required", "Not Required"),
        ],
        default="unpaid",
        validators=[DataRequired()],
    )
    source = SelectField(
        "Booking Source",
        choices=[
            ("admin", "Admin Created"),
            ("staff_request", "Approved Staff Request"),
            ("phone", "Phone"),
            ("other", "Other"),
        ],
        default="admin",
        validators=[DataRequired()],
    )
    booking_date = DateField(
        "Booking Date", default=date.today,
        validators=[DataRequired()], format="%Y-%m-%d"
    )
    currency_total = StringField(
        "Total Amount", validators=[Optional(), Length(max=30)]
    )
    amount_paid = StringField(
        "Amount Paid", default="0.00",
        validators=[DataRequired(), Length(max=30)]
    )

    # Safari-specific requests
    pickup_location = StringField(
        "Pickup Location", validators=[Optional(), Length(max=255)]
    )
    transfer_requirements = TextAreaField(
        "Transfer Requirements", validators=[Optional(), Length(max=5000)]
    )
    wildlife_interests = TextAreaField(
        "Wildlife Interests", validators=[Optional(), Length(max=5000)]
    )
    special_safari_requirements = TextAreaField(
        "Special Safari Requirements",
        validators=[Optional(), Length(max=5000)]
    )

    dietary_requirements = TextAreaField(
        "Dietary Requirements", validators=[Optional(), Length(max=5000)]
    )
    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[Optional(), Length(max=5000)]
    )
    special_requests = TextAreaField(
        "Other Special Requests", validators=[Optional(), Length(max=5000)]
    )
    customer_notes = TextAreaField(
        "Customer Notes", validators=[Optional(), Length(max=10000)]
    )
    internal_notes = TextAreaField(
        "Internal Notes", validators=[Optional(), Length(max=10000)]
    )

    submit = SubmitField("Save Safari Booking")

    def validate_end_date(self, field):
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError(
                    "The departure date cannot be before the start date."
                )

    def validate_unit_rate(self, field):
        try:
            amount = Decimal(str(field.data).strip())
            if not amount.is_finite() or amount < 0:
                raise ValidationError("Enter a valid non-negative rate.")
        except (ValueError, TypeError, ArithmeticError):
            raise ValidationError("Enter a valid monetary amount.")

    def validate_currency_total(self, field):
        if field.data:
            try:
                amount = Decimal(str(field.data).strip())
                if not amount.is_finite() or amount < 0:
                    raise ValidationError("Enter a valid non-negative total.")
            except (ValueError, TypeError, ArithmeticError):
                raise ValidationError("Enter a valid monetary total.")

    def validate_amount_paid(self, field):
        try:
            amount = Decimal(str(field.data).strip())
            if not amount.is_finite() or amount < 0:
                raise ValidationError("Amount paid cannot be negative.")
        except (ValueError, TypeError, ArithmeticError):
            raise ValidationError("Enter a valid amount paid.")


class SafariBookingStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("awaiting_payment", "Awaiting Payment"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        validators=[DataRequired()],
    )
    internal_notes = TextAreaField(
        "Internal Notes", validators=[Optional(), Length(max=10000)]
    )
    submit = SubmitField("Update Status")


class SafariBookingCommunicationForm(FlaskForm):
    recipient = StringField(
        "Recipient Email", validators=[DataRequired(), Email(), Length(max=255)]
    )
    subject = StringField(
        "Subject", validators=[DataRequired(), Length(max=255)]
    )
    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(max=15000)]
    )
    submit = SubmitField("Send Message")


class SafariBookingRequestInformationForm(FlaskForm):
    message = TextAreaField(
        "Information Requested",
        validators=[DataRequired(), Length(max=10000)],
    )
    submit = SubmitField("Request Information")
