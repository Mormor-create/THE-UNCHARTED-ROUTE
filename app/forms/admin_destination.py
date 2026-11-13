"""
===============================================================================
The Uncharted Route
Administrative Destination Forms
===============================================================================

Forms for managing Destinations in the administrative dashboard.

Destination records are parent records for Experiences.

Because destinations may have many associated Experiences, this module
intentionally provides no delete form.

Forms
-----
• AdminDestinationFilterForm
• AdminDestinationCreateForm
• AdminDestinationEditForm
• AdminDestinationStatusForm
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
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
# Destination Filter Form
# =============================================================================
class AdminDestinationFilterForm(FlaskForm):
    """
    Filtering and search form for the administrative destination catalogue.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=200),
        ],
    )

    active = SelectField(
        "Status",
        choices=[
            ("", "All Destinations"),
            ("1", "Active"),
            ("0", "Inactive"),
        ],
        validators=[
            Optional(),
        ],
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("1", "Featured"),
            ("0", "Not Featured"),
        ],
        validators=[
            Optional(),
        ],
    )

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    county = StringField(
        "County",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    region = StringField(
        "Region",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    submit = SubmitField(
        "Filter Destinations"
    )


# =============================================================================
# Destination Create Form
# =============================================================================
class AdminDestinationCreateForm(FlaskForm):
    """
    Form for creating a new Destination.
    """

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = StringField(
        "Destination Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=170),
        ],
    )

    country = StringField(
        "Country",
        default="Kenya",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    county = StringField(
        "County",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    region = StringField(
        "Region",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    # =========================================================================
    # Descriptions
    # =========================================================================

    short_description = StringField(
        "Short Description",
        validators=[
            Optional(),
            Length(max=300),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Media Assets
    # =========================================================================

    featured_image_id = SelectField(
        "Featured Image",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    banner_image_id = SelectField(
        "Banner Image",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Location Coordinates
    # =========================================================================

    latitude = DecimalField(
        "Latitude",
        validators=[
            Optional(),
            NumberRange(
                min=-90,
                max=90,
            ),
        ],
        places=7,
        rounding=None,
    )

    longitude = DecimalField(
        "Longitude",
        validators=[
            Optional(),
            NumberRange(
                min=-180,
                max=180,
            ),
        ],
        places=7,
        rounding=None,
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(max=160),
        ],
    )

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(max=300),
        ],
    )

    # =========================================================================
    # Status
    # =========================================================================

    featured = BooleanField(
        "Featured",
        default=False,)
    show_on_homepage = BooleanField(
        "Show on Homepage",
        default=False,)
    active = BooleanField(
        "Active",
        default=True,)

    # =========================================================================
    # Submit
    # =========================================================================
    submit = SubmitField(
        "Create Destination")

# =============================================================================
# Destination Edit Form
# =============================================================================
class AdminDestinationEditForm(
    AdminDestinationCreateForm
):
    """
    Form for editing an existing Destination.
    """

    submit = SubmitField(
        "Save Changes")

# =============================================================================
# Destination Status Form
# =============================================================================

class AdminDestinationStatusForm(FlaskForm):
    """
    CSRF-protected confirmation form for protected destination actions.

    Used by:
    • Activate
    • Deactivate
    • Feature
    • Unfeature

    There is intentionally no delete action.
    """

    submit = SubmitField(
        "Confirm"
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AdminDestinationFilterForm",
    "AdminDestinationCreateForm",
    "AdminDestinationEditForm",
    "AdminDestinationStatusForm",
]