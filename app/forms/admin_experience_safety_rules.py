"""
===============================================================================
The Uncharted Route
Admin Experience Safety Rule Forms
===============================================================================

WTForms used by the administration interface for managing
experiences safety rules.

Supported operations:

- Create safety rules
- Edit safety rules
- Configure safety categories
- Configure safety priorities
- Configure icons
- Configure display ordering
- Activate / deactivate safety rules
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

SAFETY_CATEGORY_CHOICES = [
    ("Wildlife", "Wildlife"),
    ("Health", "Health"),
    ("Hiking", "Hiking"),
    ("Water Safety", "Water Safety"),
    ("Transport", "Transport"),
    ("Weather", "Weather"),
    ("Emergency", "Emergency"),
    ("General", "General"),
]


SAFETY_PRIORITY_CHOICES = [
    ("Low", "Low"),
    ("Medium", "Medium"),
    ("High", "High"),
    ("Critical", "Critical"),
]


# =============================================================================
# Create Safety Rule Form
# =============================================================================

class ExperienceSafetyRuleCreateForm(FlaskForm):
    """
    Form used to create a new experiences safety rule.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Safety Rule Title",
        validators=[
            DataRequired(
                message="Safety rule title is required."
            ),
            Length(
                min=2,
                max=255,
                message=(
                    "Safety rule title must be between "
                    "2 and 255 characters."
                ),
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    # -------------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------------

    category = SelectField(
        "Category",
        choices=SAFETY_CATEGORY_CHOICES,
        default="General",
        validators=[
            DataRequired(
                message="Safety category is required."
            ),
        ],
    )

    priority = SelectField(
        "Priority",
        choices=SAFETY_PRIORITY_CHOICES,
        default="Medium",
        validators=[
            DataRequired(
                message="Safety priority is required."
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    icon = StringField(
        "Icon",
        default="shield-check",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Icon name cannot exceed 100 characters.",
            ),
        ],
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

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    active = BooleanField(
        "Active",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    submit = SubmitField(
        "Create Safety Rule"
    )


# =============================================================================
# Edit Safety Rule Form
# =============================================================================

class ExperienceSafetyRuleEditForm(FlaskForm):
    """
    Form used to edit an existing experiences safety rule.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Safety Rule Title",
        validators=[
            DataRequired(
                message="Safety rule title is required."
            ),
            Length(
                min=2,
                max=255,
                message=(
                    "Safety rule title must be between "
                    "2 and 255 characters."
                ),
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    # -------------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------------

    category = SelectField(
        "Category",
        choices=SAFETY_CATEGORY_CHOICES,
        validators=[
            DataRequired(
                message="Safety category is required."
            ),
        ],
    )

    priority = SelectField(
        "Priority",
        choices=SAFETY_PRIORITY_CHOICES,
        validators=[
            DataRequired(
                message="Safety priority is required."
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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

    display_order = IntegerField(
        "Display Order",
        validators=[
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    active = BooleanField(
        "Active",
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    submit = SubmitField(
        "Save Changes"
    )