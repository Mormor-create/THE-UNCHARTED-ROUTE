"""
===============================================================================
The Uncharted Route
Admin Experience Add-on Forms
===============================================================================

WTForms used by the administration interface for managing
experiences add-ons.

Supported operations:

- Create add-ons
- Edit add-ons
- Configure pricing
- Configure booking behaviour
- Configure online availability
- Configure display ordering
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)


# =============================================================================
# Shared Choices
# =============================================================================

PRICING_TYPE_CHOICES = [
    ("Per Person", "Per Person"),
    ("Per Booking", "Per Booking"),
    ("Per Vehicle", "Per Vehicle"),
    ("Per Group", "Per Group"),
]


# =============================================================================
# Create Add-on Form
# =============================================================================

class ExperienceAddonCreateForm(FlaskForm):
    """
    Form used to create a new experiences add-on.
    """

    name = StringField(
        "Add-on Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=255,
            ),
        ],
    )

    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(
                max=255,
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    price = DecimalField(
        "Price",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                message="Price cannot be negative.",
            ),
        ],
        places=2,
    )

    currency = StringField(
        "Currency",
        default="KES",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=10,
            ),
        ],
    )

    pricing_type = SelectField(
        "Pricing Type",
        choices=PRICING_TYPE_CHOICES,
        default="Per Person",
        validators=[
            DataRequired(),
        ],
    )

    optional = BooleanField(
        "Optional Add-on",
        default=True,
    )

    available_online = BooleanField(
        "Available Online",
        default=True,
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField(
        "Create Add-on"
    )


# =============================================================================
# Edit Add-on Form
# =============================================================================

class ExperienceAddonEditForm(FlaskForm):
    """
    Form used to edit an existing experiences add-on.
    """

    name = StringField(
        "Add-on Name",
        validators=[
            DataRequired(),
            Length(
                min=2,
                max=255,
            ),
        ],
    )

    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(
                max=255,
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    price = DecimalField(
        "Price",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                message="Price cannot be negative.",
            ),
        ],
        places=2,
    )

    currency = StringField(
        "Currency",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=10,
            ),
        ],
    )

    pricing_type = SelectField(
        "Pricing Type",
        choices=PRICING_TYPE_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    optional = BooleanField(
        "Optional Add-on",
    )

    available_online = BooleanField(
        "Available Online",
    )

    display_order = IntegerField(
        "Display Order",
        validators=[
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
    )

    active = BooleanField(
        "Active",
    )

    submit = SubmitField(
        "Save Changes"
    )