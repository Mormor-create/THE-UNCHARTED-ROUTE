"""
===============================================================================
The Uncharted Route
Admin Stay Forms
===============================================================================

Forms used by the administration interface to create, edit, filter, and
manage accommodation properties.
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
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    URL,
    ValidationError,)
from app.models.destination import Destination

# =============================================================================
# Choices
# =============================================================================
ACCOMMODATION_TYPES = [
    ("Hotel", "Hotel"),
    ("Lodge", "Lodge"),
    ("Resort", "Resort"),
    ("Villa", "Villa"),
    ("Boutique Hotel", "Boutique Hotel"),
    ("Safari Camp", "Safari Camp"),
    ("Tented Camp", "Tented Camp"),
    ("Guesthouse", "Guesthouse"),
    ("Apartment", "Apartment"),
    ("Cottage", "Cottage"),
    ("Eco-Lodge", "Eco-Lodge"),
    ("Private Residence", "Private Residence"),
    ("Other", "Other"),
]


# =============================================================================
# Stay Form
# =============================================================================

class AdminStayForm(FlaskForm):
    """
    Create/edit a Stay.
    """

    # =========================================================================
    # Identity
    # =========================================================================

    stay_code = StringField(
        "Stay Code",
        validators=[
            DataRequired(),
            Length(max=30),
        ],
    )

    property_name = StringField(
        "Property Name",
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

    accommodation_type = SelectField(
        "Accommodation Type",
        choices=ACCOMMODATION_TYPES,
        validators=[
            DataRequired(),
        ],
    )

    # =========================================================================
    # Description
    # =========================================================================

    short_description = StringField(
        "Short Description",
        validators=[
            DataRequired(),
            Length(max=350),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
        ],
    )

    # =========================================================================
    # Location
    # =========================================================================

    location = StringField(
        "Location",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    address = StringField(
        "Address",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    destination_id = SelectField(
        "Destination",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )

    latitude = DecimalField(
        "Latitude",
        validators=[
            Optional(),
        ],
        places=8,
        rounding=None,
    )

    longitude = DecimalField(
        "Longitude",
        validators=[
            Optional(),
        ],
        places=8,
        rounding=None,
    )

    # =========================================================================
    # Media Library
    # =========================================================================

    media_folder_id = SelectField(
        "Stay Media Folder",
        coerce=lambda value: int(value) if value not in (
            None,
            "",
        ) else None,
        validators=[
            DataRequired(
                message="Please select the Stay media folder."
            ),
        ],
        choices=[
            ("", "Select Stay Media Folder"),
        ],
    )

    # =========================================================================
    # Capacity
    # =========================================================================

    maximum_guests = IntegerField(
        "Maximum Guests",
        validators=[
            Optional(),
            NumberRange(min=1),
        ],
    )

    maximum_adults = IntegerField(
        "Maximum Adults",
        validators=[
            Optional(),
            NumberRange(min=1),
        ],
    )

    maximum_children = IntegerField(
        "Maximum Children",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
    )

    total_rooms = IntegerField(
        "Total Rooms / Units",
        validators=[
            Optional(),
            NumberRange(min=1),
        ],
    )

    minimum_nights = IntegerField(
        "Minimum Nights",
        default=1,
        validators=[
            InputRequired(),
            NumberRange(min=1),
        ],
    )

    # =========================================================================
    # Check-in / Check-out
    # =========================================================================

    check_in_time = StringField(
        "Check-in Time",
        validators=[
            Optional(),
            Length(max=20),
        ],
        description="Example: 14:00",
    )

    check_out_time = StringField(
        "Check-out Time",
        validators=[
            Optional(),
            Length(max=20),
        ],
        description="Example: 10:00",
    )

    # =========================================================================
    # Contact
    # =========================================================================

    contact_phone = StringField(
        "Contact Phone",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    contact_email = StringField(
        "Contact Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
        ],
    )

    website_url = StringField(
        "Website",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(max=160),
        ],
    )

    meta_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
            Length(max=320),
        ],
    )

    # =========================================================================
    # Catalogue
    # =========================================================================

    featured = BooleanField(
        "Featured Stay",
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
        "Save Stay"
    )

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        destinations = (
            Destination.query
            .filter_by(active=True)
            .order_by(Destination.name.asc())
            .all()
        )

        self.destination_id.choices = [
            (0, "Select Destination")
        ] + [
            (
                destination.id,
                destination.name,
            )
            for destination in destinations
        ]

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_destination_id(self, field):
        if not field.data or field.data == 0:
            raise ValidationError(
                "Please select a destination."
            )


# =============================================================================
# Stay Filter Form
# =============================================================================

class AdminStayFilterForm(FlaskForm):
    """
    Filtering form for the Stay administration index.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=200),
        ],
    )

    destination_id = SelectField(
        "Destination",
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    accommodation_type = SelectField(
        "Accommodation Type",
        choices=[
            ("", "All Accommodation Types"),
            *ACCOMMODATION_TYPES,
        ],
        validators=[
            Optional(),
        ],
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "All Statuses"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        validators=[
            Optional(),
        ],
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("yes", "Featured"),
            ("no", "Not Featured"),
        ],
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Filter"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        destinations = (
            Destination.query
            .order_by(Destination.name.asc())
            .all()
        )

        self.destination_id.choices = [
            (0, "All Destinations")
        ] + [
            (
                destination.id,
                destination.name,
            )
            for destination in destinations
        ]