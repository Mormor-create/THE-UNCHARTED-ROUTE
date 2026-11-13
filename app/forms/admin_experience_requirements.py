"""
===============================================================================
The Uncharted Route
Admin Experience Requirement Forms
===============================================================================

Forms used by administrators to create and edit participation requirements
attached to experiences.
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)


# =============================================================================
# Choices
# =============================================================================

REQUIREMENT_CATEGORY_CHOICES = [
    ("General", "General"),
    ("Age", "Age"),
    ("Fitness", "Fitness"),
    ("Documentation", "Documentation"),
    ("Clothing", "Clothing"),
    ("Health", "Health"),
    ("Equipment", "Equipment"),
    ("Legal", "Legal"),
]


# =============================================================================
# Create Form
# =============================================================================

class ExperienceRequirementCreateForm(FlaskForm):
    """
    Form for creating a new experiences participation requirement.
    """

    # -------------------------------------------------------------------------
    # Requirement Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Requirement Title",
        validators=[
            DataRequired(
                message="Requirement title is required."
            ),
            Length(
                max=255,
                message="Requirement title cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. Minimum Age: 12 Years"
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
        render_kw={
            "placeholder": (
                "Provide additional information about this requirement..."
            ),
            "rows": 5,
        },
    )

    category = StringField(
        "Category",
        validators=[
            DataRequired(
                message="Requirement category is required."
            ),
        ],
        default="General",
    )

    # -------------------------------------------------------------------------
    # Requirement Status
    # -------------------------------------------------------------------------

    mandatory = BooleanField(
        "Mandatory Requirement",
        default=True,
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
                message="Icon name cannot exceed 100 characters."
            ),
        ],
        default="clipboard-check",
        render_kw={
            "placeholder": "clipboard-check"
        },
    )

    display_order = IntegerField(
        "Display Order",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            ),
        ],
        default=0,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    submit = SubmitField(
        "Create Requirement"
    )


# =============================================================================
# Edit Form
# =============================================================================

class ExperienceRequirementEditForm(FlaskForm):
    """
    Form for editing an existing experiences participation requirement.
    """

    # -------------------------------------------------------------------------
    # Requirement Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Requirement Title",
        validators=[
            DataRequired(
                message="Requirement title is required."
            ),
            Length(
                max=255,
                message="Requirement title cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. Valid Passport Required"
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
        render_kw={
            "placeholder": (
                "Provide additional information about this requirement..."
            ),
            "rows": 5,
        },
    )

    category = StringField(
        "Category",
        validators=[
            DataRequired(
                message="Requirement category is required."
            ),
        ],
        default="General",
    )

    # -------------------------------------------------------------------------
    # Requirement Status
    # -------------------------------------------------------------------------

    mandatory = BooleanField(
        "Mandatory Requirement",
        default=True,
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
                message="Icon name cannot exceed 100 characters."
            ),
        ],
        default="clipboard-check",
        render_kw={
            "placeholder": "clipboard-check"
        },
    )

    display_order = IntegerField(
        "Display Order",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            ),
        ],
        default=0,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    submit = SubmitField(
        "Update Requirement"
    )