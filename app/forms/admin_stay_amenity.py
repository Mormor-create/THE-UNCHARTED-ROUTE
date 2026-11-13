"""
===============================================================================
The Uncharted Route
Admin Stay Amenity Forms
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
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

AMENITY_CATEGORIES = [
    ("General", "General"),
    ("Dining", "Dining"),
    ("Wellness", "Wellness"),
    ("Recreation", "Recreation"),
    ("Connectivity", "Connectivity"),
    ("Transport", "Transport"),
    ("Family", "Family"),
    ("Business", "Business"),
    ("Accessibility", "Accessibility"),
    ("Outdoor", "Outdoor"),
    ("Other", "Other"),
]


# =============================================================================
# Stay Amenity Form
# =============================================================================

class AdminStayAmenityForm(FlaskForm):
    """
    Create/edit a property-level Stay amenity.
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
        choices=AMENITY_CATEGORIES,
        default="General",
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
        "Save Amenity"
    )