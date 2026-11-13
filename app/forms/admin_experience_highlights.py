"""
===============================================================================
The Uncharted Route
Admin Experience Highlight Forms
===============================================================================

WTForms used by administrators to create and edit highlights belonging to
experiences.

Supported operations
--------------------

• Create experiences highlights
• Edit experiences highlights
• Select highlight type
• Set display order
• Mark highlights as featured
• Activate / deactivate highlights
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
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
# Highlight Type Choices
# =============================================================================

HIGHLIGHT_TYPE_CHOICES = [
    ("General", "General"),
    ("Wildlife", "Wildlife"),
    ("Scenic", "Scenic"),
    ("Luxury", "Luxury"),
    ("Food", "Food"),
    ("Adventure", "Adventure"),
    ("Photography", "Photography"),
    ("Family", "Family"),
    ("Cultural", "Cultural"),
]


# =============================================================================
# Shared Fields
# =============================================================================

class ExperienceHighlightBaseForm(FlaskForm):
    """
    Shared fields used by experiences highlight create and edit forms.
    """

    # -------------------------------------------------------------------------
    # Highlight Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Highlight Title",
        validators=[
            DataRequired(
                message="Highlight title is required."
            ),
            Length(
                max=255,
                message="Highlight title cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. Sunrise Game Drive",
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
        render_kw={
            "placeholder": (
                "Describe what makes this highlight special..."
            ),
            "rows": 5,
        },
    )

    # -------------------------------------------------------------------------
    # Icon
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
        default="sparkles",
        render_kw={
            "placeholder": "e.g. sparkles, car, camera",
        },
    )

    # -------------------------------------------------------------------------
    # Highlight Type
    # -------------------------------------------------------------------------

    highlight_type = SelectField(
        "Highlight Type",
        choices=HIGHLIGHT_TYPE_CHOICES,
        validators=[
            DataRequired(
                message="Please select a highlight type."
            ),
        ],
        default="General",
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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

    featured = BooleanField(
        "Featured Highlight",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )


# =============================================================================
# Create Form
# =============================================================================

class ExperienceHighlightCreateForm(
    ExperienceHighlightBaseForm
):
    """
    Form used to create a new experiences highlight.
    """

    submit = SubmitField(
        "Create Highlight"
    )


# =============================================================================
# Edit Form
# =============================================================================

class ExperienceHighlightEditForm(
    ExperienceHighlightBaseForm
):
    """
    Form used to edit an existing experiences highlight.
    """

    submit = SubmitField(
        "Save Changes"
    )