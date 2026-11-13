"""
===============================================================================
The Uncharted Route
Administrative Booking Forms
===============================================================================

WTForms used by the administrative Booking Management module.

Forms
-----
• AdminBookingFilterForm
• AdminBookingCreateForm
• AdminBookingEditForm
• AdminBookingStatusForm
• AdminBookingCancellationForm

The forms handle:
    • Validation
    • Input normalization
    • Administrative filtering
    • Booking creation input
    • Booking editing input
    • Booking lifecycle actions
    • Cancellation requests

Business logic such as:
    • Pricing selection
    • Booking totals
    • Payment calculations

remains inside the Booking Service.
"""

from flask_wtf import FlaskForm

from wtforms import (
    DateField,
    DecimalField,
    EmailField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
)

from app.models import (
    Experience,
    ExperiencePricing,
)

from app.services.bookings.booking_service import (
    BOOKING_STATUSES,
)


# =============================================================================
# Shared Choices
# =============================================================================

def _status_choices(
    include_all=False,
):
    """
    Build booking status choices.

    Parameters
    ----------
    include_all : bool
        Include an empty "All statuses" option for filtering.
    """
    choices = []

    if include_all:
        choices.append(
            (
                "",
                "All statuses",
            )
        )

    choices.extend(
        (
            status,
            status,
        )
        for status in sorted(
            BOOKING_STATUSES
        )
    )

    return choices


def _experience_choices(
    include_all=False,
):
    """
    Build Experience choices for booking forms.

    Only active Experiences are offered for new bookings.
    """
    choices = []

    if include_all:
        choices.append(
            (
                "",
                "All experiences",
            )
        )

    experiences = (
        Experience.query
        .filter(
            Experience.active.is_(True)
        )
        .order_by(
            Experience.title.asc()
        )
        .all()
    )

    choices.extend(
        (
            str(experience.id),
            (
                f"{experience.experience_code} — "
                f"{experience.title}"
            ),
        )
        for experience in experiences
    )

    return choices


def _pricing_choices(
    experience_id=None,
):
    """
    Build pricing choices.

    When an Experience is supplied, pricing options are restricted
    to that Experience.
    """
    query = ExperiencePricing.query

    if experience_id:
        query = query.filter(
            ExperiencePricing.experience_id
            == experience_id
        )

    pricing_options = (
        query
        .order_by(
            ExperiencePricing.id.asc()
        )
        .all()
    )

    choices = [
        (
            "",
            "Automatic pricing selection",
        )
    ]

    for pricing in pricing_options:

        name = getattr(
            pricing,
            "name",
            None,
        )

        level = getattr(
            pricing,
            "experience_level",
            None,
        )

        amount = getattr(
            pricing,
            "price",
            None,
        )

        if amount is None:
            amount = getattr(
                pricing,
                "price_per_person",
                None,
            )

        if name:
            label = name

        elif level:
            label = level

        else:
            label = (
                f"Pricing option #{pricing.id}"
            )

        if amount is not None:

            currency = getattr(
                pricing,
                "currency",
                "KES",
            )

            label = (
                f"{label} — "
                f"{currency} {amount:,.2f}"
            )

        choices.append(
            (
                str(pricing.id),
                label,
            )
        )

    return choices


# =============================================================================
# Booking Filter Form
# =============================================================================

class AdminBookingFilterForm(
    FlaskForm
):
    """
    Filter form for the administrative Booking catalogue.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(
                max=255
            ),
        ],
    )

    status = SelectField(
        "Status",
        choices=[],
        validators=[
            Optional(),
        ],
    )

    experience_id = SelectField(
        "Experience",
        choices=[],
        validators=[
            Optional(),
        ],
    )

    booking_date_from = DateField(
        "Booking Date From",
        format="%Y-%m-%d",
        validators=[
            Optional(),
        ],
    )

    booking_date_to = DateField(
        "Booking Date To",
        format="%Y-%m-%d",
        validators=[
            Optional(),
        ],
    )

    experience_date_from = DateField(
        "Experience Date From",
        format="%Y-%m-%d",
        validators=[
            Optional(),
        ],
    )

    experience_date_to = DateField(
        "Experience Date To",
        format="%Y-%m-%d",
        validators=[
            Optional(),
        ],
    )

    payment_status = SelectField(
        "Payment Status",
        choices=[
            (
                "",
                "All payment statuses",
            ),
            (
                "paid",
                "Paid",
            ),
            (
                "outstanding",
                "Outstanding",
            ),
        ],
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Apply Filters"
    )

    reset = SubmitField(
        "Reset"
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.status.choices = (
            _status_choices(
                include_all=True
            )
        )

        self.experience_id.choices = (
            _experience_choices(
                include_all=True
            )
        )


# =============================================================================
# Booking Create Form
# =============================================================================

class AdminBookingCreateForm(
    FlaskForm
):
    """
    Create a new administrative Booking.

    The form collects the information required by create_booking().
    Financial calculations are intentionally not performed here.
    """

    # =========================================================================
    # Experience
    # =========================================================================

    experience_id = SelectField(
        "Experience",
        choices=[],
        validators=[
            DataRequired(
                message="Please select an experience."
            ),
        ],
    )

    pricing_id = SelectField(
        "Pricing",
        choices=[],
        validators=[
            Optional(),
        ],
    )

    experience_level = StringField(
        "Experience Level",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    experience_date = DateField(
        "Experience Date",
        format="%Y-%m-%d",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Guest Information
    # =========================================================================

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                max=100
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(
                max=100
            ),
        ],
    )

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=255
            ),
        ],
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    nationality = StringField(
        "Nationality",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    # =========================================================================
    # Group Size
    # =========================================================================

    adults = IntegerField(
        "Adults",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(
                min=0
            ),
        ],
    )

    children = IntegerField(
        "Children",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0
            ),
        ],
    )

    infants = IntegerField(
        "Infants",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0
            ),
        ],
    )

    seniors = IntegerField(
        "Seniors",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0
            ),
        ],
    )

    students = IntegerField(
        "Students",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0
            ),
        ],
    )

    # =========================================================================
    # Emergency Contact
    # =========================================================================

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(
                max=200
            ),
        ],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    emergency_contact_relationship = StringField(
        "Emergency Contact Relationship",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    # =========================================================================
    # Guest Requirements
    # =========================================================================

    dietary_requirements = TextAreaField(
        "Dietary Requirements",
        validators=[
            Optional(),
        ],
    )

    medical_information = TextAreaField(
        "Medical Information",
        validators=[
            Optional(),
        ],
    )

    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[
            Optional(),
        ],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional(),
        ],
    )

    customer_notes = TextAreaField(
        "Customer Notes",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Financial Adjustments
    # =========================================================================
    #
    # These are adjustments passed to the Booking Service.
    # The form does not calculate the final booking total.
    # =========================================================================

    discount_amount = DecimalField(
        "Discount Amount",
        places=2,
        rounding=None,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0
            ),
        ],
    )

    tax_amount = DecimalField(
        "Tax Amount",
        places=2,
        rounding=None,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0
            ),
        ],
    )

    addon_total = DecimalField(
        "Add-on Total",
        places=2,
        rounding=None,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0
            ),
        ],
    )

    # =========================================================================
    # Status
    # =========================================================================

    status = SelectField(
        "Booking Status",
        choices=[],
        default="Pending",
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField(
        "Create Booking"
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.experience_id.choices = (
            _experience_choices()
        )

        # Pricing is initially populated without an Experience filter.
        #
        # The form can later be enhanced with AJAX/dynamic dependent
        # fields so pricing updates immediately when an Experience
        # is selected.
        self.pricing_id.choices = (
            _pricing_choices()
        )

        self.status.choices = (
            _status_choices()
        )


# =============================================================================
# Booking Edit Form
# =============================================================================

class AdminBookingEditForm(
    FlaskForm
):
    """
    Edit an existing Booking.

    Booking identity, financial snapshots and pricing calculations
    are deliberately not exposed as ordinary editable fields.
    """

    # =========================================================================
    # Guest Information
    # =========================================================================

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                max=100
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(
                max=100
            ),
        ],
    )

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=255
            ),
        ],
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    nationality = StringField(
        "Nationality",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    country_of_residence = StringField(
        "Country of Residence",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    # =========================================================================
    # Emergency Contact
    # =========================================================================

    emergency_contact_name = StringField(
        "Emergency Contact Name",
        validators=[
            Optional(),
            Length(
                max=200
            ),
        ],
    )

    emergency_contact_phone = StringField(
        "Emergency Contact Phone",
        validators=[
            Optional(),
            Length(
                max=50
            ),
        ],
    )

    emergency_contact_relationship = StringField(
        "Emergency Contact Relationship",
        validators=[
            Optional(),
            Length(
                max=100
            ),
        ],
    )

    # =========================================================================
    # Guest Requirements
    # =========================================================================

    dietary_requirements = TextAreaField(
        "Dietary Requirements",
        validators=[
            Optional(),
        ],
    )

    medical_information = TextAreaField(
        "Medical Information",
        validators=[
            Optional(),
        ],
    )

    accessibility_requirements = TextAreaField(
        "Accessibility Requirements",
        validators=[
            Optional(),
        ],
    )

    special_requests = TextAreaField(
        "Special Requests",
        validators=[
            Optional(),
        ],
    )

    customer_notes = TextAreaField(
        "Customer Notes",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Operations
    # =========================================================================

    assigned_consultant = StringField(
        "Assigned Consultant",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    assigned_guide = StringField(
        "Assigned Guide",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    assigned_driver = StringField(
        "Assigned Driver",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    assigned_vehicle = StringField(
        "Assigned Vehicle",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    # =========================================================================
    # Internal Notes
    # =========================================================================

    internal_notes = TextAreaField(
        "Internal Notes",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Save Changes"
    )


# =============================================================================
# Booking Status Form
# =============================================================================

class AdminBookingStatusForm(
    FlaskForm
):
    """
    Generic confirmation form for Booking lifecycle actions.

    Used by:
        • Confirm
        • Start
        • Complete
        • Payment refresh
    """

    submit = SubmitField(
        "Confirm Action"
    )


# =============================================================================
# Booking Cancellation Form
# =============================================================================

class AdminBookingCancellationForm(
    FlaskForm
):
    """
    Booking cancellation form.

    A cancellation reason is required so the operational history
    retains context for why the booking was cancelled.
    """

    reason = TextAreaField(
        "Cancellation Reason",
        validators=[
            DataRequired(
                message=(
                    "Please provide a cancellation reason."
                )
            ),
            Length(
                min=3,
                max=2000,
            ),
        ],
    )

    submit = SubmitField(
        "Cancel Booking"
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AdminBookingFilterForm",
    "AdminBookingCreateForm",
    "AdminBookingEditForm",
    "AdminBookingStatusForm",
    "AdminBookingCancellationForm",
]