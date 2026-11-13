"""
===============================================================================
The Uncharted Route
Admin Experience Packing Item Forms
===============================================================================

WTForms used by the administration interface for managing
experiences packing items.

Supported operations:

- Create packing items
- Edit packing items
- Configure packing categories
- Mark items as recommended
- Mark items as required
- Configure display ordering
- Activate / deactivate packing items
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
    Length,
    NumberRange,
    Optional,
)


# =============================================================================
# Shared Choices
# =============================================================================

PACKING_CATEGORY_CHOICES = [
    ("General", "General"),
    ("Clothing", "Clothing"),
    ("Equipment", "Equipment"),
    ("Electronics", "Electronics"),
    ("Documents", "Documents"),
    ("Health", "Health"),
    ("Personal Items", "Personal Items"),
]


# =============================================================================
# Create Packing Item Form
# =============================================================================

class ExperiencePackingItemCreateForm(FlaskForm):
    """
    Form used to create a new experiences packing item.
    """

    name = StringField(
        "Item Name",
        validators=[
            DataRequired(
                message="Packing item name is required."
            ),
            Length(
                min=2,
                max=255,
                message="Item name must be between 2 and 255 characters.",
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    category = SelectField(
        "Category",
        choices=PACKING_CATEGORY_CHOICES,
        default="General",
        validators=[
            DataRequired(
                message="Please select a category."
            ),
        ],
    )

    icon = StringField(
        "Icon",
        default="backpack",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Icon name cannot exceed 100 characters.",
            ),
        ],
    )

    recommended = BooleanField(
        "Recommended",
        default=True,
    )

    required = BooleanField(
        "Required",
        default=False,
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
        "Create Packing Item"
    )


# =============================================================================
# Edit Packing Item Form
# =============================================================================

class ExperiencePackingItemEditForm(FlaskForm):
    """
    Form used to edit an existing experiences packing item.
    """

    name = StringField(
        "Item Name",
        validators=[
            DataRequired(
                message="Packing item name is required."
            ),
            Length(
                min=2,
                max=255,
                message="Item name must be between 2 and 255 characters.",
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    category = SelectField(
        "Category",
        choices=PACKING_CATEGORY_CHOICES,
        validators=[
            DataRequired(
                message="Please select a category."
            ),
        ],
    )

    icon = StringField(
        "Icon",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Icon name cannot exceed 100 characters.",
            ),
        ],
    )

    recommended = BooleanField(
        "Recommended",
    )

    required = BooleanField(
        "Required",
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