"""
===============================================================================
The Uncharted Route
Admin Experience Tag Forms
===============================================================================

WTForms used by the administrative experiences tag management interface.

Responsibilities
----------------

• Create experiences tags
• Edit experiences tags
• Validate tag names and slugs
• Manage display settings
• Manage featured status
• Manage SEO metadata
• Manage activation status
• Manage display ordering
===============================================================================
"""

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    IntegerField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
    Regexp,
)


# =============================================================================
# Shared Constants
# =============================================================================

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


# =============================================================================
# Experience Tag Form
# =============================================================================

class ExperienceTagForm(FlaskForm):
    """
    Form used to create and edit experiences tags.

    The same form is intentionally used for both creation and editing so
    validation remains consistent throughout the admin interface.
    """

    # =========================================================================
    # Basic Information
    # =========================================================================

    name = StringField(
        "Tag Name",
        validators=[
            DataRequired(
                message="Tag name is required."
            ),
            Length(
                min=2,
                max=100,
                message="Tag name must be between 2 and 100 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. Wildlife",
        },
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(
                message="Tag slug is required."
            ),
            Length(
                min=2,
                max=120,
                message="Tag slug must be between 2 and 120 characters."
            ),
            Regexp(
                SLUG_PATTERN,
                message=(
                    "Slug may only contain lowercase letters, numbers, "
                    "and hyphens."
                ),
            ),
        ],
        render_kw={
            "placeholder": "e.g. wildlife",
        },
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=5000,
                message="Description cannot exceed 5000 characters."
            ),
        ],
        render_kw={
            "placeholder": (
                "Describe what this tag represents and how it is used."
            ),
            "rows": 4,
        },
    )

    # =========================================================================
    # Display Settings
    # =========================================================================

    color = StringField(
        "Display Color",
        validators=[
            Optional(),
            Length(
                max=20,
                message="Color value cannot exceed 20 characters."
            ),
        ],
        render_kw={
            "placeholder": "#10B981",
        },
    )

    icon = StringField(
        "Icon",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Icon value cannot exceed 100 characters."
            ),
        ],
        render_kw={
            "placeholder": "e.g. fa-solid fa-paw",
        },
    )

    featured = BooleanField(
        "Featured Tag",
        default=False,
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Meta title cannot exceed 255 characters."
            ),
        ],
        render_kw={
            "placeholder": "SEO page title",
        },
    )

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(
                max=500,
                message="Meta description cannot exceed 500 characters."
            ),
        ],
        render_kw={
            "placeholder": "SEO description for this tag.",
            "rows": 3,
        },
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = BooleanField(
        "Active",
        default=True,
    )

    sort_order = IntegerField(
        "Sort Order",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Sort order cannot be negative."
            ),
        ],
        default=0,
        render_kw={
            "placeholder": "0",
        },
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Tag"
    )