"""
===============================================================================
The Uncharted Route
Stay Booking Forms
===============================================================================
"""
from datetime import date
from decimal import Decimal, InvalidOperation
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

class StayBookingForm(FlaskForm):
    """Create or edit a central Booking with accommodation-specific details."""

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

    # Accommodation
    stay_id = SelectField(
        "Accommodation", coerce=int, validators=[DataRequired()]
    )
    room_id = SelectField(
        "Room Type", coerce=int, validators=[Optional()]
    )
    meal_plan = SelectField(
        "Meal Plan",
        choices=[
            ("", "Select a meal plan"),
            ("room_only", "Room Only"),
            ("bed_breakfast", "Bed & Breakfast"),
            ("half_board", "Half Board"),
            ("full_board", "Full Board"),
            ("all_inclusive", "All Inclusive"),
            ("other", "Other / Custom"),
        ],
        validators=[Optional()],
    )
    meal_plan_snapshot = StringField(
        "Meal Plan Description", validators=[Optional(), Length(max=150)]
    )

    # Reservation dates
    check_in = DateField(
        "Check-in Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    check_out = DateField(
        "Check-out Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    nights = IntegerField(
        "Nights", default=1,
        validators=[DataRequired(), NumberRange(min=1)]
    )
    rooms_count = IntegerField(
        "Rooms Required", default=1,
        validators=[DataRequired(), NumberRange(min=1)]
    )

    # Occupancy
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

    # Pricing
    rate_name_snapshot = StringField(
        "Rate Name", validators=[Optional(), Length(max=150)]
    )
    rate_basis = SelectField(
        "Rate Basis",
        choices=[
            ("per_room_per_night", "Per Room Per Night"),
            ("per_person_per_night", "Per Person Per Night"),
            ("per_person", "Per Person"),
            ("per_room", "Per Room"),
            ("per_stay", "Per Stay"),
        ],
        default="per_room_per_night",
        validators=[DataRequired()],
    )
    nightly_rate = StringField(
        "Rate Amount", default="0.00",
        validators=[DataRequired(), Length(max=30)]
    )
    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),
        ],
        default="KES",
        validators=[DataRequired()],
    )
    currency_total = StringField(
        "Booking Total", validators=[Optional(), Length(max=30)]
    )
    amount_paid = StringField(
        "Amount Paid", default="0.00",
        validators=[DataRequired(), Length(max=30)]
    )

    # Arrival and departure
    arrival_time = StringField(
        "Expected Arrival Time", validators=[Optional(), Length(max=30)]
    )
    departure_time = StringField(
        "Expected Departure Time", validators=[Optional(), Length(max=30)]
    )
    availability_reference = StringField(
        "Availability Reference", validators=[Optional(), Length(max=100)]
    )

    # Central booking
    booking_date = DateField(
        "Booking Date", format="%Y-%m-%d",
        default=date.today, validators=[DataRequired()]
    )
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

    # Requirements and notes
    special_requests = TextAreaField(
        "Guest Special Requests", validators=[Optional(), Length(max=10000)]
    )
    accessibility_requirements = TextAreaField(
        "Accessibility Requirements", validators=[Optional(), Length(max=10000)]
    )
    dietary_requirements = TextAreaField(
        "Dietary Requirements", validators=[Optional(), Length(max=5000)]
    )
    customer_notes = TextAreaField(
        "Customer Notes", validators=[Optional(), Length(max=10000)]
    )
    internal_notes = TextAreaField(
        "Internal Notes", validators=[Optional(), Length(max=10000)]
    )

    submit = SubmitField("Save Stay Booking")

    def validate_check_out(self, field):
        if self.check_in.data and field.data:
            if field.data <= self.check_in.data:
                raise ValidationError(
                    "Check-out must be after the check-in date."
                )

    def validate_nights(self, field):
        if self.check_in.data and self.check_out.data:
            if self.check_out.data > self.check_in.data:
                expected = (self.check_out.data - self.check_in.data).days
                if field.data != expected:
                    raise ValidationError(
                        f"The selected dates represent {expected} night(s)."
                    )

    def _validate_money(self, value, label, allow_empty=False):
        if allow_empty and value in (None, ""):
            return
        try:
            amount = Decimal(str(value).strip())
            if not amount.is_finite() or amount < 0:
                raise ValidationError(f"{label} must be a valid non-negative amount.")
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"{label} must be a valid monetary amount.")

    def validate_nightly_rate(self, field):
        self._validate_money(field.data, "Rate")

    def validate_currency_total(self, field):
        self._validate_money(field.data, "Booking total", allow_empty=True)

    def validate_amount_paid(self, field):
        self._validate_money(field.data, "Amount paid")


class StayBookingStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("awaiting_payment", "Awaiting Payment"),
            ("confirmed", "Confirmed"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),],
        validators=[DataRequired()],)
    internal_notes = TextAreaField(
        "Internal Note", validators=[Optional(), Length(max=10000)])
    submit = SubmitField("Update Status")

class StayBookingCommunicationForm(FlaskForm):
    recipient = StringField(
        "Recipient Email", validators=[DataRequired(), Email(), Length(max=255)])
    subject = StringField(
        "Subject", validators=[DataRequired(), Length(max=255)])
    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(max=15000)] )
    submit = SubmitField("Send Message")


class StayBookingRequestInformationForm(FlaskForm):
    message = TextAreaField(
        "Information Requested", validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField("Request Information")