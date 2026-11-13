from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,)
from app.models import (
    MediaAsset,
    MediaAssetFolder,)
from app.services.media_service import get_media_folder_by_slug

# =============================================================================
# MEDIA LIBRARY CONFIGURATION
# =============================================================================
SIGNATURE_MOMENTS_MEDIA_FOLDER_SLUG = "signature-moments"

# =============================================================================
# SIGNATURE MOMENT CHOICES
# =============================================================================
MOMENT_TYPES = [
    ("Experience", "Experience"),
    ("Wildlife", "Wildlife"),
    ("Adventure", "Adventure"),
    ("Luxury", "Luxury"),
    ("Cultural", "Cultural"),
    ("Coastal", "Coastal"),
    ("Photography", "Photography"),
    ("Dining", "Dining"),
    ("Scenic", "Scenic"),
    ("Conservation", "Conservation"),]

EMOTIONAL_IMPACTS = [
    ("Moderate", "Moderate"),
    ("High", "High"),
    ("Exceptional", "Exceptional"),]

# =============================================================================
# ADMIN SIGNATURE MOMENT FORM
# =============================================================================
class AdminSignatureMomentForm(FlaskForm):

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------
    title = StringField(
        "Moment Title",
        validators=[
            DataRequired(),
            Length(max=255),],)

    short_description = TextAreaField(
        "Short Description",
        validators=[Optional()],)

    full_description = TextAreaField(
        "Full Description",
        validators=[Optional()],)

    # -------------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------------
    moment_type = SelectField(
        "Moment Type",
        choices=MOMENT_TYPES,
        validators=[DataRequired()],)

    # -------------------------------------------------------------------------
    # Timing
    # -------------------------------------------------------------------------
    expected_time = StringField(
        "Expected Time",
        validators=[
            Optional(),
            Length(max=100),],)

    estimated_duration = IntegerField(
        "Estimated Duration (minutes)",
        validators=[
            Optional(),
            NumberRange(
                min=1,
                message="Duration must be at least 1 minute.",
            ),
        ],
    )

    best_season = StringField(
        "Best Season",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    # -------------------------------------------------------------------------
    # Photography
    # -------------------------------------------------------------------------

    photography_recommended = BooleanField(
        "Photography Recommended",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Emotional Impact
    # -------------------------------------------------------------------------

    emotional_impact = SelectField(
        "Emotional Impact",
        choices=EMOTIONAL_IMPACTS,
        validators=[DataRequired()],
    )

    # -------------------------------------------------------------------------
    # Hero Media
    # -------------------------------------------------------------------------

    hero_media_id = SelectField(
        "Hero Media",
        coerce=int,
        validators=[Optional()],
    )

    # -------------------------------------------------------------------------
    # Publishing
    # -------------------------------------------------------------------------

    featured = BooleanField(
        "Featured Moment",
        default=True,
    )

    display_order = IntegerField(
        "Display Order",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField("Save Signature Moment")

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_choices()

    # =========================================================================
    # FORM CHOICES
    # =========================================================================

    def set_choices(self):
        """
        Populate Hero Media choices.

        Hero media is restricted to active image assets assigned to the
        dedicated Signature Moments Media Folder.

        The folder is identified by its slug:
            signature-moments

        No fallback to the complete Media Library is permitted.
        """

        # ---------------------------------------------------------------------
        # Default Hero Media Choice
        # ---------------------------------------------------------------------

        self.hero_media_id.choices = [
            (0, "— No Hero Media —"),
        ]

        # ---------------------------------------------------------------------
        # Locate the Dedicated Media Folder
        # ---------------------------------------------------------------------

        folder = get_media_folder_by_slug(
            SIGNATURE_MOMENTS_MEDIA_FOLDER_SLUG
        )

        # The folder may not have been created yet.
        # In that case, retain only the default empty choice.
        if folder is None or not folder.active:
            return

        # ---------------------------------------------------------------------
        # Retrieve Images Assigned to This Folder Only
        # ---------------------------------------------------------------------

        media_assets = (
            MediaAsset.query
            .join(
                MediaAssetFolder,
                MediaAssetFolder.media_asset_id == MediaAsset.id,
            )
            .filter(
                MediaAssetFolder.folder_id == folder.id,
                MediaAsset.active.is_(True),
                MediaAsset.media_type == "image",
            )
            .order_by(
                MediaAsset.title.asc(),
                MediaAsset.original_filename.asc(),
            )
            .all()
        )

        # ---------------------------------------------------------------------
        # Build Hero Media Choices
        # ---------------------------------------------------------------------

        self.hero_media_id.choices.extend(
            [
                (
                    asset.id,
                    (
                        asset.title
                        or asset.original_filename
                        or f"Media #{asset.id}"
                    ),
                )for asset in media_assets])

# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    "AdminSignatureMomentForm",
    "MOMENT_TYPES",
    "EMOTIONAL_IMPACTS",
    "SIGNATURE_MOMENTS_MEDIA_FOLDER_SLUG",]