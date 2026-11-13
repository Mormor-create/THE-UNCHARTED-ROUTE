"""
===============================================================================
The Uncharted Route
Admin Experience Exclusion Forms
===============================================================================

WTForms used by the administration interface for managing
experiences exclusions.

Supported operations:

- Create exclusions
- Edit exclusions
- Configure icons
- Configure display ordering
- Activate / deactivate exclusions
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    IntegerField,
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
# Create Exclusion Form
# =============================================================================

class ExperienceExclusionCreateForm(FlaskForm):
    """
    Form used to create a new experiences exclusion.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Exclusion Title",
        validators=[
            DataRequired(
                message="Exclusion title is required."
            ),
            Length(
                min=2,
                max=255,
                message="Title must be between 2 and 255 characters.",
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    icon = StringField(
        "Icon",
        default="x-circle",
        validators=[
            Optional(),
            Length(
                max=100,
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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
        "Create Exclusion"
    )


# =============================================================================
# Edit Exclusion Form
# =============================================================================

class ExperienceExclusionEditForm(FlaskForm):
    """
    Form used to edit an existing experiences exclusion.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Exclusion Title",
        validators=[
            DataRequired(
                message="Exclusion title is required."
            ),
            Length(
                min=2,
                max=255,
                message="Title must be between 2 and 255 characters.",
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    icon = StringField(
        "Icon",
        validators=[
            Optional(),
            Length(
                max=100,
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

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