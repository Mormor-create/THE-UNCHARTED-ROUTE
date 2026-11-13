"""
The Uncharted Route
Experience Booking Forms
"""
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import (
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
    Optional,
    ValidationError,)

BOOKING_STATUSES = [
    ("pending", "Pending"),
    ("awaiting_payment", "Awaiting Payment"),
    ("confirmed", "Confirmed"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("refunded", "Refunded"),
]

PAYMENT_STATUSES = [
    ("unpaid", "Unpaid"),
    ("pending", "Pending"),
    ("partially_paid", "Partially Paid"),
    ("paid", "Paid"),
    ("partially_refunded", "Partially Refunded"),
    ("refunded", "Refunded"),
    ("failed", "Failed"),
    ("not_required", "Not Required"),
]

PRICE_BASES = [
    ("per_person", "Per Person"),
    ("per_group", "Per Group"),
    ("per_booking", "Per Booking"),
]


class ExperienceBookingFilterForm(FlaskForm):
    """Filters for the Experience Bookings index."""

    search = StringField(
        "Search",
        validators=[Optional(), Length(max=150)],
    )

    status = SelectField(
        "Booking Status",
        choices=[("", "All Statuses")] + BOOKING_STATUSES,
        validators=[Optional()],
    )

    payment_status = SelectField(
        "Payment Status",
        choices=[("", "All Payment Statuses")] + PAYMENT_STATUSES,
        validators=[Optional()],
    )

    source = SelectField(
        "Booking Source",
        choices=[
            ("", "All Sources"),
            ("website", "Website"),
            ("admin", "Administrator"),
            ("staff_request", "Staff Request"),
            ("phone", "Phone"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )

    assignment = SelectField(
        "Assignment",
        choices=[
            ("", "All Bookings"),
            ("assigned", "Assigned"),
            ("unassigned", "Unassigned"),
        ],
        validators=[Optional()],
    )

    start_date = DateField(
        "From Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    end_date = DateField(
        "To Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    submit = SubmitField("Filter")


class ExperienceBookingForm(FlaskForm):
    """Create or edit a central experience booking."""

    # Customer
    first_name = StringField(
        "First Name",
        validators=[DataRequired(), Length(max=100)],
    )

    last_name = StringField(
        "Last Name",
        validators=[DataRequired(), Length(max=100)],
    )

    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=255)],
    )

    phone = StringField(
        "Phone Number",
        validators=[Optional(), Length(max=50)],
    )

    nationality = StringField(
        "Nationality",
        validators=[Optional(), Length(max=100)],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[Optional(), Length(max=100)],
    )

    # Experience selection. Choices are populated by the route.
    experience_id = SelectField(
        "Experience",
        coerce=int,
        validators=[DataRequired()],
    )

    pricing_id = SelectField(
        "Pricing Option",
        coerce=int,
        validators=[Optional()],
    )

    # Group
    adults = IntegerField(
        "Adults",
        default=1,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    children = IntegerField(
        "Children",
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    seniors = IntegerField(
        "Seniors",
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    students = IntegerField(
        "Students",
        default=0,
        validators=[DataRequired(), NumberRange(min=0)],
    )

    quantity = IntegerField(
        "Quantity",
        default=1,
        validators=[DataRequired(), NumberRange(min=1)],
    )

    # Price snapshot
    price_basis = SelectField(
        "Price Basis",
        choices=PRICE_BASES,
        default="per_person",
        validators=[DataRequired()],
    )

    unit_price = DecimalField(
        "Unit Price",
        places=2,
        default=Decimal("0.00"),
        validators=[DataRequired(), NumberRange(min=0)],
    )

    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES"),
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
        ],
        default="KES",
        validators=[DataRequired()],
    )

    discount_amount = DecimalField(
        "Discount",
        places=2,
        default=Decimal("0.00"),
        validators=[DataRequired(), NumberRange(min=0)],
    )

    tax_amount = DecimalField(
        "Tax",
        places=2,
        default=Decimal("0.00"),
        validators=[DataRequired(), NumberRange(min=0)],
    )

    # Operational details
    pickup_location = StringField(
        "Pickup Location",
        validators=[Optional(), Length(max=255)],
    )

    dropoff_location = StringField(
        "Drop-off Location",
        validators=[Optional(), Length(max=255)],
    )

    experience_date = DateField(
        "Experience Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    start_date = DateField(
        "Start Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    end_date = DateField(
        "End Date",
        format="%Y-%m-%d",
        validators=[Optional()],
    )

    # Shared booking information
    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[Optional(), Length(max=150)],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[Optional(), Length(max=50)],
    )

    emergency_contact_relationship = StringField(
        "Relationship",
        validators=[Optional(), Length(max=100)],
    )

    dietary_requirements = TextAreaField(
        "Dietary Requirements",
        validators=[Optional()],
    )

    medical_information = TextAreaField(
        "Medical Information",
        validators=[Optional()],
    )

    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[Optional()],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[Optional()],
    )

    customer_instructions = TextAreaField(
        "Experience Instructions",
        validators=[Optional()],
    )

    customer_notes = TextAreaField(
        "Customer Notes",
        validators=[Optional()],
    )

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[Optional()],
    )

    status = SelectField(
        "Booking Status",
        choices=BOOKING_STATUSES,
        default="pending",
        validators=[DataRequired()],
    )

    payment_status = SelectField(
        "Payment Status",
        choices=PAYMENT_STATUSES,
        default="unpaid",
        validators=[DataRequired()],
    )

    submit = SubmitField("Save Booking")

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)

        if not valid:
            return False

        if not any([
            self.adults.data or 0,
            self.children.data or 0,
            self.infants.data or 0,
            self.seniors.data or 0,
            self.students.data or 0,
        ]):
            self.adults.errors.append("At least one traveller is required.")
            return False

        if (
            self.start_date.data
            and self.end_date.data
            and self.end_date.data < self.start_date.data
        ):
            self.end_date.errors.append(
                "End date cannot be before the start date."
            )
            return False
        return True

class ExperienceBookingAssignmentForm(FlaskForm):
    """Assign or reassign a booking to a staff member."""

    staff_id = SelectField(
        "Staff Member",
        coerce=int,
        validators=[DataRequired()],)

    role = StringField(
        "Assignment Role",
        default="Booking Manager",
        validators=[DataRequired(), Length(max=100)],
    )

    notes = TextAreaField(
        "Assignment Notes",
        validators=[Optional()],
    )

    submit = SubmitField("Assign Staff")


class ExperienceBookingStatusForm(FlaskForm):
    """Change a booking's lifecycle status."""

    status = SelectField(
        "Status",
        choices=BOOKING_STATUSES,
        validators=[DataRequired()],
    )

    cancellation_reason = TextAreaField(
        "Cancellation Reason",
        validators=[Optional()],
    )

    submit = SubmitField("Update Status")


class ExperienceBookingArchiveForm(FlaskForm):
    """Confirmation form for archiving a booking."""

    reason = TextAreaField(
        "Archive Reason",
        validators=[Optional()],
    )

    submit = SubmitField("Archive Booking")


class ExperienceBookingDeleteForm(FlaskForm):
    """Confirmation form for safe deletion."""

    confirmation = StringField(
        "Type DELETE to confirm",
        validators=[DataRequired()],
    )

    submit = SubmitField("Delete Booking")

    def validate_confirmation(self, field):
        if field.data != "DELETE":
            raise ValidationError(
                "Enter DELETE exactly to confirm."
            )


class ExperienceBookingCommunicationForm(FlaskForm):
    """Email the booking customer."""

    subject = StringField(
        "Subject",
        validators=[DataRequired(), Length(max=255)],
    )

    message = TextAreaField(
        "Message",
        validators=[DataRequired()],)

    submit = SubmitField("Send Email")


class ExperienceBookingInformationForm(FlaskForm):
    """Request missing information from the customer."""
    message = TextAreaField(
        "Information Required",
        validators=[DataRequired()],)

    submit = SubmitField("Request Information")