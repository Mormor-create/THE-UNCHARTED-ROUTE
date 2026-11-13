"""
===============================================================================
The Uncharted Route
Admin Stay Room Amenity Forms
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
)


# =============================================================================
# Choices
# =============================================================================

ROOM_AMENITY_CATEGORIES = [
    ("Room", "Room"),
    ("Bathroom", "Bathroom"),
    ("Technology", "Technology"),
    ("Comfort", "Comfort"),
    ("Dining", "Dining"),
    ("Outdoor", "Outdoor"),
    ("Accessibility", "Accessibility"),
    ("Other", "Other"),
]


# =============================================================================
# Stay Room Amenity Form
# =============================================================================

class AdminStayRoomAmenityForm(FlaskForm):
    """
    Create/edit a room-level amenity.
    """

    name = StringField(
        "Amenity Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    description = StringField(
        "Description",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    category = SelectField(
        "Category",
        choices=ROOM_AMENITY_CATEGORIES,
        default="Room",
        validators=[
            DataRequired(),
        ],
    )

    icon = StringField(
        "Icon",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    featured = BooleanField(
        "Featured",
        default=False,
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
                message="Display order cannot be negative."
            ),
        ],
    )

    submit = SubmitField(
        "Save Room Amenity"
    )