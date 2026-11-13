"""
===============================================================================
The Uncharted Route
Admin Stay Room Forms
===============================================================================
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,)

# =============================================================================
# Choices
# =============================================================================
ROOM_TYPES = [
    ("Standard Room", "Standard Room"),
    ("Deluxe Room", "Deluxe Room"),
    ("Superior Room", "Superior Room"),
    ("Executive Room", "Executive Room"),
    ("Family Room", "Family Room"),
    ("Family Suite", "Family Suite"),
    ("Junior Suite", "Junior Suite"),
    ("Suite", "Suite"),
    ("Luxury Suite", "Luxury Suite"),
    ("Villa", "Villa"),
    ("Private Villa", "Private Villa"),
    ("Cottage", "Cottage"),
    ("Tent", "Tent"),
    ("Tented Suite", "Tented Suite"),
    ("Presidential Suite", "Presidential Suite"),
    ("Other", "Other"),
]

MEAL_PLANS = [
    ("Room Only", "Room Only"),
    ("Bed & Breakfast", "Bed & Breakfast"),
    ("Half Board", "Half Board"),
    ("Full Board", "Full Board"),
    ("All Inclusive", "All Inclusive"),
    ("Custom", "Custom"),
]


AVAILABILITY_STATUSES = [
    ("Available", "Available"),
    ("Limited", "Limited"),
    ("Sold Out", "Sold Out"),
    ("Closed", "Closed"),
    ("On Request", "On Request"),
]


# =============================================================================
# Stay Room Form
# =============================================================================

class AdminStayRoomForm(FlaskForm):
    """
    Create/edit an accommodation room type.

    The Room Media Folder field is populated by the route because the route
    knows which DAM hierarchy should be presented.
    """

    # =========================================================================
    # Identity
    # =========================================================================

    room_code = StringField(
        "Room Code",
        validators=[
            DataRequired(),
            Length(max=40),
        ],
    )

    name = StringField(
        "Room Name",
        validators=[
            DataRequired(),
            Length(max=200),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=220),
        ],
    )

    room_type = SelectField(
        "Room Type",
        choices=ROOM_TYPES,
        validators=[
            DataRequired(),
        ],
    )

    # =========================================================================
    # Media Library
    # =========================================================================
    media_folder_id = SelectField(
        "Room Media Folder",
        coerce=lambda value: int(value) if value not in (
            None,
            "",
        ) else None,
        validators=[
            DataRequired(
                message="Please select the Room media folder."
            ),
        ],
        choices=[
            ("", "Select Room Media Folder"),
        ],
    )

    # =========================================================================
    # Description
    # =========================================================================
    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(max=350),],)

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),],)

    # =========================================================================
    # Occupancy
    # =========================================================================
    maximum_guests = IntegerField(
        "Maximum Guests",
        default=2,
        validators=[
            InputRequired(),
            NumberRange(
                min=1,
                message="Maximum guests must be at least 1.",),],)

    maximum_adults = IntegerField(
        "Maximum Adults",
        default=2,
        validators=[
            Optional(),
            NumberRange(
                min=1,
                message="Maximum adults must be at least 1.",
            ),
        ],
    )

    maximum_children = IntegerField(
        "Maximum Children",
        default=2,
        validators=[
            InputRequired(
                message="Please specify the maximum number of children."
            ),
            NumberRange(
                min=0,
                message="Maximum children cannot be negative.",
            ),
        ],
    )

    minimum_guests = IntegerField(
        "Minimum Guests",
        default=1,
        validators=[
            InputRequired(),
            NumberRange(
                min=1,
                message="Minimum guests must be at least 1.",
            ),
        ],
    )

    # =========================================================================
    # Inventory
    # =========================================================================

    total_units = IntegerField(
        "Total Units",
        default=1,
        validators=[
            InputRequired(),
            NumberRange(min=1),
        ],
    )

    # =========================================================================
    # Pricing
    # =========================================================================

    nightly_rate = DecimalField(
        "Nightly Rate",
        validators=[
            InputRequired(),
            NumberRange(min=0),
        ],
        places=2,
    )

    currency = SelectField(
        "Currency",
        choices=[
            ("KES", "KES — Kenyan Shilling"),
            ("USD", "USD — US Dollar"),
            ("EUR", "EUR — Euro"),
            ("GBP", "GBP — British Pound"),
            ("ZAR", "ZAR — South African Rand"),
            ("TZS", "TZS — Tanzanian Shilling"),
            ("UGX", "UGX — Ugandan Shilling"),
        ],
        default="KES",
        validators=[
            DataRequired(),
        ],
    )

    meal_plan = SelectField(
        "Meal Plan",
        choices=MEAL_PLANS,
        default="Bed & Breakfast",
        validators=[
            DataRequired(),
        ],
    )

    # =========================================================================
    # Room Features
    # =========================================================================

    bed_configuration = StringField(
        "Bed Configuration",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    floor = StringField(
        "Floor",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    size_description = StringField(
        "Room Size",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    # =========================================================================
    # Availability
    # =========================================================================

    availability_status = SelectField(
        "Availability Status",
        choices=AVAILABILITY_STATUSES,
        default="Available",
        validators=[
            DataRequired(),
        ],
    )

    # =========================================================================
    # Catalogue
    # =========================================================================

    featured = BooleanField(
        "Featured Room",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            InputRequired(
                message="Please provide a display order."
            ),
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Room"
    )

    # =========================================================================
    # Cross-field Validation
    # =========================================================================

    def validate(self, extra_validators=None):
        if not super().validate(
            extra_validators=extra_validators
        ):
            return False

        if (
            self.maximum_adults.data is not None
            and self.maximum_guests.data is not None
            and self.maximum_adults.data > self.maximum_guests.data
        ):
            self.maximum_adults.errors.append(
                "Maximum adults cannot exceed maximum guests."
            )
            return False

        if (
            self.maximum_children.data is not None
            and self.maximum_guests.data is not None
            and self.maximum_children.data > self.maximum_guests.data
        ):
            self.maximum_children.errors.append(
                "Maximum children cannot exceed maximum guests."
            )
            return False

        if (
            self.minimum_guests.data is not None
            and self.maximum_guests.data is not None
            and self.minimum_guests.data > self.maximum_guests.data
        ):
            self.minimum_guests.errors.append(
                "Minimum guests cannot exceed maximum guests."
            )
            return False

        return True
