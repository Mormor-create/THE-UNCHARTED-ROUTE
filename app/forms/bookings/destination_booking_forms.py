# =============================================================================
# The Uncharted Route
# Destination Journey Booking Forms
# =============================================================================

from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
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
    Optional,)

CURRENCIES = [
    ("KES", "KES — Kenyan Shilling"),
    ("USD", "USD — US Dollar"),
    ("EUR", "EUR — Euro"),
    ("GBP", "GBP — British Pound"),
    ("UGX", "UGX — Ugandan Shilling"),
    ("TZS", "TZS — Tanzanian Shilling"),
    ("ZAR", "ZAR — South African Rand"),
    ("NGN", "NGN — Nigerian Naira"),
    ("GHS", "GHS — Ghanaian Cedi"),
]

PRICING_BASES = [
    ("per_person", "Per person"),
    ("per_group", "Per group"),
    ("per_vehicle", "Per vehicle"),
    ("fixed", "Fixed package price"),
    ("bespoke", "Bespoke agreed price"),
]

BOOKING_STATUSES = [
    ("pending", "Pending"),
    ("awaiting_payment", "Awaiting payment"),
    ("confirmed", "Confirmed"),
    ("in_progress", "In progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("refunded", "Refunded"),
    ("archived", "Archived"),
]

PAYMENT_STATUSES = [
    ("unpaid", "Unpaid"),
    ("pending", "Pending"),
    ("partially_paid", "Partially paid"),
    ("paid", "Paid"),
    ("partially_refunded", "Partially refunded"),
    ("refunded", "Refunded"),
    ("failed", "Failed"),
    ("not_required", "Not required"),
]

BOOKING_SOURCES = [
    ("admin", "Admin"),
    ("staff_request", "Staff request"),
    ("phone", "Phone"),
    ("other", "Other"),
]


class DestinationBookingForm(FlaskForm):
    """Create or update a destination journey booking."""

    # Customer details
    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(max=100)],
    )
    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(max=100)],
    )
    email = StringField(
        "Email address",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    phone = StringField(
        "Phone number",
        validators=[Optional(), Length(max=50)],
    )
    nationality = StringField(
        "Nationality",
        validators=[Optional(), Length(max=100)],
    )
    country_of_residence = StringField(
        "Country of residence",
        validators=[Optional(), Length(max=100)],
    )

    # Journey
    journey_id = SelectField(
        "Destination journey",
        coerce=int,
        validators=[DataRequired()],
    )
    start_date = DateField(
        "Start date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    end_date = DateField(
        "End date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    duration_days = IntegerField(
        "Duration in days",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    duration_nights = IntegerField(
        "Duration in nights",
        validators=[DataRequired(), NumberRange(min=0)],
    )
    travellers_count = IntegerField(
        "Number of travellers",
        default=1,
        validators=[DataRequired(), NumberRange(min=1)],
    )

    rooming_preferences = TextAreaField(
        "Rooming preferences",
        validators=[Optional(), Length(max=5000)],
    )
    transport_preferences = TextAreaField(
        "Transport preferences",
        validators=[Optional(), Length(max=5000)],
    )
    preferred_stops = TextAreaField(
        "Preferred stops",
        description="Enter one stop per line.",
        validators=[Optional(), Length(max=5000)],
    )
    bespoke_requirements = TextAreaField(
        "Bespoke requirements",
        validators=[Optional(), Length(max=10000)],
    )
    bespoke = BooleanField("Bespoke itinerary")

    # Price snapshot
    pricing_basis = SelectField(
        "Pricing basis",
        choices=PRICING_BASES,
        validators=[DataRequired()],
    )
    unit_price = DecimalField(
        "Unit price",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    currency = SelectField(
        "Currency",
        choices=CURRENCIES,
        default="KES",
        validators=[DataRequired()],
    )

    # Central booking
    booking_date = DateField(
        "Booking date",
        format="%Y-%m-%d",
        default=date.today,
        validators=[DataRequired()],
    )
    status = SelectField(
        "Booking status",
        choices=BOOKING_STATUSES,
        default="pending",
        validators=[DataRequired()],
    )
    payment_status = SelectField(
        "Payment status",
        choices=PAYMENT_STATUSES,
        default="unpaid",
        validators=[DataRequired()],
    )
    source = SelectField(
        "Booking source",
        choices=BOOKING_SOURCES,
        default="admin",
        validators=[DataRequired()],
    )
    total_amount = DecimalField(
        "Total booking amount",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    amount_paid = DecimalField(
        "Amount paid",
        places=2,
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    # Customer and internal notes
    dietary_requirements = TextAreaField(
        "Dietary requirements",
        validators=[Optional(), Length(max=5000)],
    )
    medical_information = TextAreaField(
        "Medical information",
        validators=[Optional(), Length(max=5000)],
    )
    accessibility_requirements = TextAreaField(
        "Accessibility requirements",
        validators=[Optional(), Length(max=5000)],
    )
    special_requests = TextAreaField(
        "Special requests",
        validators=[Optional(), Length(max=10000)],
    )
    customer_notes = TextAreaField(
        "Customer notes",
        validators=[Optional(), Length(max=10000)],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional(), Length(max=10000)],
    )

    submit = SubmitField("Save booking")

    def validate_end_date(self, field):
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValueError("End date cannot be before start date.")

    def validate_duration_days(self, field):
        if field.data and field.data < 1:
            raise ValueError("Duration must be at least one day.")

    def validate_duration_nights(self, field):
        if field.data is not None and field.data < 0:
            raise ValueError("Duration in nights cannot be negative.")

    def validate_amount_paid(self, field):
        if (
            field.data is not None
            and self.total_amount.data is not None
            and field.data > self.total_amount.data
        ):
            raise ValueError("Amount paid cannot exceed the total amount.")


class DestinationBookingStatusForm(FlaskForm):
    status = SelectField(
        "Booking status",
        choices=BOOKING_STATUSES,
        validators=[DataRequired()],
    )
    internal_notes = TextAreaField(
        "Internal notes",
        validators=[Optional(), Length(max=10000)],
    )
    submit = SubmitField("Update status")


class DestinationBookingCommunicationForm(FlaskForm):
    subject = StringField(
        "Subject",
        validators=[DataRequired(), Length(max=255)],
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(max=20000)],
    )
    submit = SubmitField("Send email")


class DestinationBookingRequestInformationForm(FlaskForm):
    subject = StringField(
        "Subject",
        validators=[DataRequired(), Length(max=255)],
    )
    message = TextAreaField(
        "Information requested",
        validators=[DataRequired(), Length(max=20000)],
    )
    submit = SubmitField("Request information")