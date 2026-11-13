"""
===============================================================================
The Uncharted Route
Admin Experience Wildlife Forms
===============================================================================

WTForms used to manage wildlife species associated with experiences.

These forms support:

• Adding wildlife to an experience
• Editing experience-specific wildlife information
• Sighting probability
• Best viewing season
• Best time of day
• Guide notes
• Photography notes
• Featured wildlife
• Display ordering
• Activation / deactivation

Wildlife species themselves are managed separately through the
Wildlife Species administration module.
===============================================================================
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
    NumberRange,
    Optional,
)

from app.models import Experience, WildlifeSpecies


# =============================================================================
# Constants
# =============================================================================

SIGHTING_PROBABILITIES = [
    ("Guaranteed", "Guaranteed"),
    ("Very Common", "Very Common"),
    ("Common", "Common"),
    ("Occasional", "Occasional"),
    ("Rare", "Rare"),
]

BEST_TIMES_OF_DAY = [
    ("Sunrise", "Sunrise"),
    ("Morning", "Morning"),
    ("Afternoon", "Afternoon"),
    ("Sunset", "Sunset"),
    ("Night", "Night"),
]


# =============================================================================
# Experience Wildlife Form
# =============================================================================

class ExperienceWildlifeForm(FlaskForm):
    """
    Form for creating and editing an experience wildlife association.
    """

    # =========================================================================
    # Experience
    # =========================================================================

    experience_id = SelectField(
        "Experience",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select an experience."
            )
        ],
        choices=[],
        description=(
            "Select the experience where this wildlife species "
            "can be encountered."
        ),
    )

    # =========================================================================
    # Wildlife Species
    # =========================================================================

    species_id = SelectField(
        "Wildlife Species",
        coerce=int,
        validators=[
            DataRequired(
                message="Please select a wildlife species."
            )
        ],
        choices=[],
        description=(
            "Select the wildlife species associated with this experience."
        ),
    )

    # =========================================================================
    # Sighting Information
    # =========================================================================

    sighting_probability = SelectField(
        "Sighting Probability",
        choices=SIGHTING_PROBABILITIES,
        default="Common",
        validators=[
            DataRequired(
                message="Please select a sighting probability."
            )
        ],
        description=(
            "Indicate how frequently guests can reasonably expect "
            "to encounter this species."
        ),
    )

    best_season = TextAreaField(
        "Best Viewing Season",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 2,
            "placeholder": (
                "e.g. All Year, Dry Season, July–October"
            ),
        },
        description=(
            "Describe the season or period when this species is "
            "most likely to be encountered."
        ),
    )

    best_time_of_day = SelectField(
        "Best Time of Day",
        choices=[
            ("", "Select time of day"),
            *BEST_TIMES_OF_DAY,
        ],
        validators=[
            Optional()
        ],
        description=(
            "Select the time of day when sightings are generally "
            "most favorable."
        ),
    )

    # =========================================================================
    # Guide Information
    # =========================================================================

    guide_notes = TextAreaField(
        "Guide Notes",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 5,
            "placeholder": (
                "Enter useful guide information, behavior notes, "
                "habitat information, or guest-facing interpretation."
            ),
        },
        description=(
            "Operational or interpretive notes for guides and "
            "experience delivery."
        ),
    )

    photography_notes = TextAreaField(
        "Photography Notes",
        validators=[
            Optional()
        ],
        render_kw={
            "rows": 5,
            "placeholder": (
                "Enter photography opportunities, recommended "
                "viewing positions, lighting conditions, or "
                "photography guidance."
            ),
        },
        description=(
            "Photography-specific information for guests and guides."
        ),
    )

    # =========================================================================
    # Display
    # =========================================================================

    featured = BooleanField(
        "Featured Wildlife",
        default=False,
        description=(
            "Display this species as a featured wildlife highlight "
            "for the experience."
        ),
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            ),
        ],
        description=(
            "Lower numbers appear first."
        ),
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = BooleanField(
        "Active",
        default=True,
        description=(
            "Inactive wildlife associations are retained but "
            "excluded from normal guest-facing displays."
        ),
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Wildlife"
    )

    # =========================================================================
    # Choice Loading
    # =========================================================================

    def load_choices(
        self,
        selected_experience_id=None,
        selected_species_id=None,
    ):
        """
        Load experience and wildlife species choices.

        This method is intentionally separated from form initialization
        so that routes can populate choices consistently for both
        create and edit operations.
        """

        experiences = (
            Experience.query
            .filter_by(active=True)
            .order_by(
                Experience.title.asc()
            )
            .all()
        )

        species = (
            WildlifeSpecies.query
            .filter_by(active=True)
            .order_by(
                WildlifeSpecies.common_name.asc()
            )
            .all()
        )

        self.experience_id.choices = [
            (
                experience.id,
                experience.title,
            )
            for experience in experiences
        ]

        self.species_id.choices = [
            (
                wildlife.id,
                wildlife.common_name,
            )
            for wildlife in species
        ]

        # ---------------------------------------------------------------------
        # Preserve currently selected values when editing.
        # ---------------------------------------------------------------------

        if selected_experience_id is not None:
            self.experience_id.data = selected_experience_id

        if selected_species_id is not None:
            self.species_id.data = selected_species_id