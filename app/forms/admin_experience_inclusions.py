"""
===============================================================================
The Uncharted Route
Admin Experience Inclusion Forms
===============================================================================

WTForms used by the administration interface for managing
experiences inclusions.

Supported operations:

- Create inclusions
- Edit inclusions
- Configure icons
- Configure display ordering
- Activate/deactivate inclusions
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
# Create Inclusion Form
# =============================================================================


class ExperienceInclusionCreateForm(FlaskForm):
    """
    Form used to create a new experiences inclusion.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Inclusion Title",
        validators=[
            DataRequired(
                message="Inclusion title is required."
            ),
            Length(
                min=2,
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

    icon = StringField(
        "Icon",
        default="check-circle",
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
        "Create Inclusion"
    )


# =============================================================================
# Edit Inclusion Form
# =============================================================================


class ExperienceInclusionEditForm(FlaskForm):
    """
    Form used to edit an existing experiences inclusion.
    """

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------

    title = StringField(
        "Inclusion Title",
        validators=[
            DataRequired(
                message="Inclusion title is required."
            ),
            Length(
                min=2,
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