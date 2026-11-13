"""
===============================================================================
The Uncharted Route
Admin Experience Photography Forms
===============================================================================

Forms used by administrators to manage photography spots associated with
experiences.

Supported operations
--------------------

• Add a photography spot to an experiences
• Edit an experiences photography association
• Set photography stop order
• Feature / unfeature a photography stop
• Activate / deactivate a photography stop
• Add experiences-specific photography notes
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Optional,
)

# =============================================================================
# Choices
# =============================================================================
FEATURED_CHOICES = [
    (True, "Featured"),
    (False, "Not Featured"),]

STATUS_CHOICES = [
    (True, "Active"),
    (False, "Inactive"),]

# =============================================================================
# Base Form
# =============================================================================
class ExperiencePhotographyBaseForm(FlaskForm):
    """
    Shared fields for experiences photography administration.
    """

    stop_order = IntegerField(
        "Stop Order",
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message="Stop order cannot be negative.",
            ),
        ],
        default=0,
        description=(
            "Determines the order in which this photography "
            "spot appears within the experiences."
        ),
    )

    featured = BooleanField(
        "Featured",
        default=False,
        description=(
            "Feature this photography spot on the experiences."
        ),
    )

    active = BooleanField(
        "Active",
        default=True,
        description=(
            "Inactive photography spots remain stored but are "
            "not displayed publicly."
        ),
    )

    notes = TextAreaField(
        "Experience-Specific Notes",
        validators=[
            Optional(),
        ],
        description=(
            "Optional notes describing how this photography spot "
            "is used within this particular experiences."
        ),
    )


# =============================================================================
# Create Form
# =============================================================================

class ExperiencePhotographyCreateForm(
    ExperiencePhotographyBaseForm
):
    """
    Form for adding a photography spot to an experiences.

    The photography_spot_id is supplied by the admin interface after
    selecting an existing PhotographySpot.
    """

    photography_spot_id = SelectField(
        "Photography Spot",
        validators=[
            DataRequired(
                message="Please select a photography spot."
            ),
        ],
        coerce=int,
        choices=[],
    )

    submit = SubmitField(
        "Add Photography Spot"
    )


# =============================================================================
# Edit Form
# =============================================================================
class ExperiencePhotographyEditForm(
    ExperiencePhotographyBaseForm):
    """
    Form for editing an existing experiences photography association.
    """
    submit = SubmitField("Save Changes")

# =============================================================================
# Reorder Form
# =============================================================================
class ExperiencePhotographyReorderForm(FlaskForm):
    """
    Form for changing the order of a single photography stop.
    """
    stop_order = IntegerField(
        "Stop Order",
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message="Stop order cannot be negative.",),],)

    submit = SubmitField("Update Order")

# =============================================================================
# Bulk Reorder Form
# =============================================================================
class ExperiencePhotographyBulkReorderForm(
    FlaskForm):
    """
    Form used when submitting a reordered list of photography
    associations.
    The actual association IDs are submitted by the reorder interface
    as `association_ids[]`.
    """
    submit = SubmitField("Save Order")

# =============================================================================
# Status Form
# =============================================================================
class ExperiencePhotographyStatusForm(
    FlaskForm):
    """
    Form used for activating or deactivating a photography association.
    """
    submit = SubmitField(
        "Update Status")

# =============================================================================
# Featured Form
# =============================================================================
class ExperiencePhotographyFeaturedForm(
    FlaskForm
):
    """
    Form used for featuring or unfeaturing a photography association.
    """
    featured = BooleanField(
        "Featured",
        default=False,)

    submit = SubmitField(
        "Update Featured Status")