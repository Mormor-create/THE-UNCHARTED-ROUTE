"""
The Uncharted Route — Administrative Experience Forms
Forms for managing the core Experience record.
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,)
from app.services.media_service import (
    get_cms_media_assets,
    get_media_folders,)

EXPERIENCE_FOLDER_NAME = "Experiences"

# =============================================================================
# EXPERIENCE FILTER FORM
# =============================================================================
class AdminExperienceFilterForm(FlaskForm):
    """
    Filtering and search form for the administrative experiences catalogue.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=200),],)

    category_id = SelectField(
        "Category",
        coerce=lambda value: int(value) if value else None,
        validators=[Optional()],)

    destination_id = SelectField(
        "Destination",
        coerce=lambda value: int(value) if value else None,
        validators=[Optional()],)

    difficulty = SelectField(
        "Difficulty",
        choices=[
            ("", "All Difficulties"),
            ("Easy", "Easy"),
            ("Moderate", "Moderate"),
            ("Challenging", "Challenging"),
            ("Extreme", "Extreme"),
        ],validators=[Optional()],)

    active_only = BooleanField(
        "Active only",
        default=False,)

    featured_only = BooleanField(
        "Featured only",
        default=False,)

    submit = SubmitField("Filter Experiences")


# =============================================================================
# EXPERIENCE CREATE FORM
# =============================================================================

class AdminExperienceCreateForm(FlaskForm):
    """
    Form for creating a new Experience.
    """

    # =========================================================================
    # Identity
    # =========================================================================

    experience_code = StringField(
        "Experience Code",
        validators=[
            DataRequired(),
            Length(max=30),
        ],
    )

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(max=200),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=220),
        ],
    )

    # =========================================================================
    # Descriptions
    # =========================================================================
    short_description = StringField(
        "Short Description",
        validators=[
            DataRequired(),
            Length(max=350),],)

    description = TextAreaField(
        "Description",
        validators=[DataRequired()],)

    # =========================================================================
    # Logistics
    # =========================================================================
    duration = StringField(
        "Duration",
        validators=[
            Optional(),
            Length(max=100),],)

    meeting_point = StringField(
        "Meeting Point",
        validators=[
            Optional(),
            Length(max=255),],)

    location = StringField(
        "Location",
        validators=[
            Optional(),
            Length(max=255),],)

    # =========================================================================
    # Pricing
    # =========================================================================
    price_from = DecimalField(
        "Starting Price",
        validators=[
            DataRequired(),
            NumberRange(min=0),],places=2,)

    currency = StringField(
        "Currency",
        default="KES",
        validators=[
            DataRequired(),
            Length(max=10),],)

    # =========================================================================
    # Group Information
    # =========================================================================
    minimum_people = IntegerField(
        "Minimum People",
        default=1,
        validators=[
            Optional(),
            NumberRange(min=1),],)

    maximum_people = IntegerField(
        "Maximum People",
        validators=[
            Optional(),
            NumberRange(min=1),],)

    minimum_age = IntegerField(
        "Minimum Age",
        validators=[
            Optional(),
            NumberRange(min=0),],)

    # =========================================================================
    # Difficulty
    # =========================================================================
    difficulty = SelectField(
        "Difficulty",
        choices=[
            ("Easy", "Easy"),
            ("Moderate", "Moderate"),
            ("Challenging", "Challenging"),
            ("Extreme", "Extreme"),
        ],
        default="Easy",
        validators=[DataRequired()],)

    # =========================================================================
    # Images — Media Library Asset IDs
    # =========================================================================
    featured_image = SelectField(
        "Featured Image",
        choices=[("", "— Select a featured image —")],
        coerce=str,
        validators=[
            DataRequired(
                message="Please select a featured image."
            ),
            Length(max=255),
        ],
    )

    banner_image = SelectField(
        "Banner Image",
        choices=[("", "— Use no separate banner image —")],
        coerce=str,
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    def set_media_choices(self):
        """
        Load active images from the Experiences folder and its descendants.

        Both image fields store MediaAsset IDs as strings, matching the
        existing Page Hero CMS selector pattern.
        """

        placeholder = [
            ("", "— Select an image from Experiences —")
        ]

        folders = get_media_folders(active_only=True)

        experiences_folder = next(
            (
                folder
                for folder in folders
                if (
                    (getattr(folder, "name", "") or "")
                    .strip()
                    .casefold()
                    == EXPERIENCE_FOLDER_NAME.casefold()
                )
            ),
            None,
        )

        # Fail closed: do not expose assets from unrelated folders.
        if experiences_folder is None:
            self.featured_image.choices = placeholder
            self.banner_image.choices = [
                ("", "— Use no separate banner image —")
            ]
            return

        media_assets = get_cms_media_assets(
            folder_id=experiences_folder.id,
            include_descendants=True,
            media_type="image",
            active_only=True,
        )

        sorted_assets = sorted(
            media_assets,
            key=lambda media: (
                (
                    getattr(media, "title", None)
                    or getattr(media, "original_filename", None)
                    or getattr(media, "filename", None)
                    or f"Media Asset #{media.id}"
                ).casefold(),
                media.id,
            ),
        )

        featured_choices = list(placeholder)

        banner_choices = [
            ("", "— Use no separate banner image —")
        ]

        for media in sorted_assets:
            title = (
                getattr(media, "title", None)
                or getattr(media, "original_filename", None)
                or getattr(media, "filename", None)
                or f"Media Asset #{media.id}"
            )

            filename = (
                getattr(media, "original_filename", None)
                or getattr(media, "filename", None)
            )

            label = title

            if filename and filename != title:
                label = f"{title} — {filename}"

            choice = (str(media.id), label)

            featured_choices.append(choice)
            banner_choices.append(choice)

        self.featured_image.choices = featured_choices
        self.banner_image.choices = banner_choices

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
            Length(max=320),
        ],
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired()],
    )

    destination_id = SelectField(
        "Destination",
        coerce=int,
        validators=[DataRequired()],
    )

    conservation_story_id = SelectField(
        "Conservation Story",
        coerce=lambda value: int(value) if value else None,
        validators=[Optional()],
    )

    cancellation_policy_id = SelectField(
        "Cancellation Policy",
        choices=[],
        coerce=lambda value: int(value) if value else None,
        validators=[
            DataRequired(
                message="Please select a cancellation policy."
            ),
        ],
    )

    accessibility_profile_id = SelectField(
        "Accessibility Profile",
        coerce=lambda value: int(value) if value else None,
        validators=[Optional()],
    )

    # =========================================================================
    # EXPERIENCE TAGS
    # =========================================================================

    tag_ids = SelectMultipleField(
        "Experience Tags",
        coerce=int,
        choices=[],
        validators=[Optional()],
    )

    def set_tag_choices(self, tags):
        """
        Populate the tag selector.

        The route supplies active tags and, when editing, any inactive
        tags already assigned to the experience.
        """

        sorted_tags = sorted(
            tags,
            key=lambda tag: (
                tag.sort_order,
                (tag.name or "").casefold(),
            ),
        )

        self.tag_ids.choices = [
            (tag.id, tag.name)
            for tag in sorted_tags
        ]

    # =========================================================================
    # SIGNATURE MOMENTS
    # =========================================================================

    moment_ids = SelectMultipleField(
        "Signature Moments",
        coerce=int,
        choices=[],
        validators=[Optional()],
    )

    def set_signature_moment_choices(self, moments):
        """
        Populate the Signature Moments selector.

        The route supplies active Signature Moments and, when editing,
        any inactive moments already assigned to the experience.

        Signature Moments remain independent catalogue records.
        This selector only manages their association with an Experience.
        """

        sorted_moments = sorted(
            moments,
            key=lambda moment: (
                moment.display_order,
                (moment.title or "").casefold(),
            ),
        )

        self.moment_ids.choices = [
            (moment.id, moment.title)
            for moment in sorted_moments
        ]

    # =========================================================================
    # PUBLISHING
    # =========================================================================

    featured = BooleanField(
        "Featured",
        default=False,
    )

    show_on_homepage = BooleanField(
        "Show on Homepage",
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
            Optional(),
            NumberRange(min=0),
        ],
    )

    def validate(self, extra_validators=None):
        """Validate standard fields and homepage visibility rules."""

        is_valid = super().validate(
            extra_validators=extra_validators)

        if self.show_on_homepage.data and not self.featured.data:
            self.show_on_homepage.errors.append(
                "An experience must be marked as Featured before "
                "it can be shown on the homepage.")
            return False

        return is_valid

    # =========================================================================
    # SUBMIT
    # =========================================================================
    submit = SubmitField("Create Experience")

# =============================================================================
# EXPERIENCE EDIT FORM
# =============================================================================
class AdminExperienceEditForm(AdminExperienceCreateForm):
    """
    Form for editing an existing Experience.
    """
    submit = SubmitField("Save Changes")


# =============================================================================
# EXPERIENCE STATUS FORM
# =============================================================================
class AdminExperienceStatusForm(FlaskForm):
    """
    Form used for protected status-changing actions.
    """
    submit = SubmitField("Confirm")

# =============================================================================
# PUBLIC API
# =============================================================================
__all__ = [
    "AdminExperienceFilterForm",
    "AdminExperienceCreateForm",
    "AdminExperienceEditForm",
    "AdminExperienceStatusForm",]