"""
===============================================================================
The Uncharted Route
Administrative Conservation Story Forms
===============================================================================
Forms for managing reusable conservation stories.
Responsibilities:
- Filter conservation stories
- Create conservation stories
- Edit conservation stories
- Manage status
- Manage featured status
- Manage display order
- Select hero media from the central Media Library
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
    URL,
    ValidationError,
)

from app.models import ConservationStory, MediaAsset

# =============================================================================
# Choices
# =============================================================================
CONSERVATION_TYPES = [
    ("Wildlife", "Wildlife"),
    ("Marine", "Marine"),
    ("Forest", "Forest"),
    ("Community", "Community"),
    ("Climate", "Climate"),
    ("Research", "Research"),
    ("Education", "Education"),
]


STATUS_CHOICES = [
    ("", "All Statuses"),
    ("active", "Active"),
    ("inactive", "Inactive"),
]


FEATURED_CHOICES = [
    ("", "All"),
    ("featured", "Featured"),
    ("not_featured", "Not Featured"),
]


# =============================================================================
# Media Helpers
# =============================================================================
def get_media_choices():
    """
    Return active image/video assets from the central Media Library.
    """

    assets = (
        MediaAsset.query
        .filter(
            MediaAsset.active.is_(True),
            MediaAsset.media_type.in_(["image", "video"]),
        )
        .order_by(
            MediaAsset.title.asc(),
            MediaAsset.original_filename.asc(),
        )
        .all()
    )

    choices = [
        (0, "— No Hero Media —")
    ]

    for asset in assets:
        label = (
            asset.title
            or asset.original_filename
            or asset.filename
            or f"Media Asset #{asset.id}"
        )

        media_label = asset.media_type.title() if asset.media_type else "Media"

        choices.append(
            (
                asset.id,
                f"{label} ({media_label})",
            )
        )

    return choices


# =============================================================================
# Slug Validation
# =============================================================================

def validate_unique_slug(form, field):
    """
    Ensure the conservation story slug is unique.
    """

    slug = field.data.strip() if field.data else ""

    if not slug:
        return

    query = ConservationStory.query.filter(
        ConservationStory.slug == slug
    )

    current_story_id = getattr(form, "_current_story_id", None)

    if current_story_id:
        query = query.filter(
            ConservationStory.id != current_story_id
        )

    if query.first() is not None:
        raise ValidationError(
            "A conservation story with this slug already exists."
        )


# =============================================================================
# Filter Form
# =============================================================================

class AdminConservationStoryFilterForm(FlaskForm):
    """
    Filter the conservation story library.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    conservation_type = SelectField(
        "Conservation Type",
        choices=[
            ("", "All Types"),
            *CONSERVATION_TYPES,
        ],
        validators=[
            Optional(),
        ],
    )

    status = SelectField(
        "Status",
        choices=STATUS_CHOICES,
        validators=[
            Optional(),
        ],
    )

    featured = SelectField(
        "Featured",
        choices=FEATURED_CHOICES,
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField("Filter")


# =============================================================================
# Base Story Form
# =============================================================================

class AdminConservationStoryForm(FlaskForm):
    """
    Shared fields for creating and editing conservation stories.
    """

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            Optional(),
            Length(max=255),
            validate_unique_slug,
        ],
    )

    conservation_type = SelectField(
        "Conservation Type",
        choices=CONSERVATION_TYPES,
        validators=[
            DataRequired(),
        ],
    )

    short_description = TextAreaField(
        "Short Description",
        validators=[
            Optional(),
        ],
    )

    full_story = TextAreaField(
        "Full Story",
        validators=[
            Optional(),
        ],
    )

    focus_species = StringField(
        "Focus Species",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    organization_name = StringField(
        "Organization Name",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    organization_website = StringField(
        "Organization Website",
        validators=[
            Optional(),
            Length(max=255),
            URL(),
        ],
    )

    why_it_matters = TextAreaField(
        "Why It Matters",
        validators=[
            Optional(),
        ],
    )

    visitor_impact = TextAreaField(
        "Visitor Impact",
        validators=[
            Optional(),
        ],
    )

    how_guests_help = TextAreaField(
        "How Guests Help",
        validators=[
            Optional(),
        ],
    )

    interesting_fact = TextAreaField(
        "Interesting Fact",
        validators=[
            Optional(),
        ],
    )

    hero_media_id = SelectField(
        "Hero Media",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    featured = BooleanField(
        "Featured",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ],
    )

    submit = SubmitField(
        "Save Conservation Story"
    )

    def __init__(self, *args, **kwargs):
        current_story = kwargs.pop(
            "current_story",
            None,
        )

        super().__init__(*args, **kwargs)

        self._current_story_id = (
            current_story.id
            if current_story
            else None
        )

        self.hero_media_id.choices = get_media_choices()


# =============================================================================
# Create Form
# =============================================================================

class AdminConservationStoryCreateForm(
    AdminConservationStoryForm
):
    """
    Create a conservation story.
    """
    pass


# =============================================================================
# Edit Form
# =============================================================================

class AdminConservationStoryEditForm(
    AdminConservationStoryForm
):
    """
    Edit an existing conservation story.
    """
    pass


# =============================================================================
# Status Form
# =============================================================================

class AdminConservationStoryStatusForm(
    FlaskForm
):
    """
    Used for activate/deactivate/delete actions.
    """

    submit = SubmitField(
        "Confirm"
    )


# =============================================================================
# Featured Form
# =============================================================================

class AdminConservationStoryFeaturedForm(
    FlaskForm
):
    """
    Used for feature/unfeature actions.
    """

    submit = SubmitField(
        "Confirm"
    )


# =============================================================================
# Order Form
# =============================================================================

class AdminConservationStoryOrderForm(
    FlaskForm
):
    """
    Update display order.
    """

    display_order = IntegerField(
        "Display Order",
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ],
    )

    submit = SubmitField(
        "Save Order"
    )


__all__ = [
    "AdminConservationStoryFilterForm",
    "AdminConservationStoryCreateForm",
    "AdminConservationStoryEditForm",
    "AdminConservationStoryStatusForm",
    "AdminConservationStoryFeaturedForm",
    "AdminConservationStoryOrderForm",
]