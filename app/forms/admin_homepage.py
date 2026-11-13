"""
===============================================================================
The Uncharted Route — Administrative Homepage Forms
===============================================================================

WTForms used by the administrative homepage CMS.

Responsibilities
----------------
• Edit homepage-level configuration
• Edit homepage SEO metadata
• Control homepage publishing state
• Create and edit homepage sections
• Control section visibility
• Control section ordering
• Configure section content and calls to action
• Select an optional MediaAsset for a section
• Enforce Hero-specific content requirements
• Validate internal and external CTA URLs

Security Model
--------------
These forms are intended exclusively for the protected administrative
interface.

Authorization must be enforced by the route/decorator/service layer.

The forms do not perform administrative authorization themselves.

Homepage content remains connected to its respective systems rather than
duplicating Experience, Destination, BlogPost, or other records.

===============================================================================
"""

from urllib.parse import urlparse

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
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.models import MediaAsset, MediaFolder
from app.services.media_service import get_cms_media_assets

# =============================================================================
# CTA URL Validation
# =============================================================================

def _validate_cta_url(form, field):
    """
    Validate homepage CTA URLs.

    Supported URL formats
    ---------------------
    Internal:
        /experiences
        /destinations
        /contact
        /experiences?category=wildlife
        /experiences#featured

    External:
        https://example.com
        http://example.com/path
    """

    value = (
        field.data.strip()
        if isinstance(field.data, str)
        else ""
    )

    if not value:
        return

    # -------------------------------------------------------------------------
    # Internal application URL
    # -------------------------------------------------------------------------

    if value.startswith("/"):

        if value.startswith("//"):
            raise ValidationError(
                "Please enter a valid internal path or an HTTP/HTTPS URL."
            )

        return

    # -------------------------------------------------------------------------
    # Absolute HTTP/HTTPS URL
    # -------------------------------------------------------------------------

    parsed = urlparse(value)

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        raise ValidationError(
            "CTA URL must be an internal path such as /experiences "
            "or an HTTP/HTTPS URL."
        )

    if not parsed.netloc:
        raise ValidationError(
            "Please enter a valid HTTP/HTTPS URL."
        )

    if " " in value:
        raise ValidationError(
            "CTA URL cannot contain spaces."
        )


# =============================================================================
# Homepage Form
# =============================================================================

class AdminHomepageForm(FlaskForm):
    """
    Form used by an administrator to configure the main homepage.
    """

    # =========================================================================
    # Homepage Metadata
    # =========================================================================

    title = StringField(
        "Homepage Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Homepage title cannot exceed 255 characters.",
            ),
        ],
    )

    description = TextAreaField(
        "Homepage Description",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="SEO title cannot exceed 255 characters.",
            ),
        ],
    )

    meta_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
            Length(
                max=500,
                message="SEO description cannot exceed 500 characters.",
            ),
        ],
    )

    # =========================================================================
    # Publishing
    # =========================================================================

    is_published = BooleanField(
        "Publish Homepage",
        default=True,
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Homepage",
    )


# =============================================================================
# Homepage Section Form
# =============================================================================
class AdminHomepageSectionForm(FlaskForm):
    """
    Form used by an administrator to create or edit a homepage section.

    Section media rules
    -------------------
    Hero:
        • Media is required.

    Featured Experiences — Section Heading:
        • No media.
        • This record represents only the section heading.

    Featured Experience — Card:
        • Media is optional.

    Destinations — Section Heading:
        • No media.
        • This record represents only the section heading.

    Destination — Card:
        • Media is optional.

    Other section types:
        • Media is optional.

    CTA:
        • CTA text and CTA URL must be supplied together.
    """

    # =========================================================================
    # Section Identity
    # =========================================================================

    section_type = SelectField(
        "Section Type",
        choices=[
            ("hero", "Hero"),
            (
                "featured_experiences",
                "Featured Experiences — Section Heading",
            ),
            (
                "featured_experience_card",
                "Featured Experience — Card",
            ),
            (
                "destinations",
                "Destinations — Section Heading",
            ),
            (
                "destination_card",
                "Destination — Card",
            ),
            (
                "why_travel",
                "Why Travel With Us",
            ),
            (
                "journal",
                "Featured Journal",
            ),
            (
                "media",
                "Homepage Media",
            ),
            (
                "promotional",
                "Promotional Section",
            ),
        ],
        validators=[
            DataRequired(
                message="Please select a section type.",
            ),
        ],
    )

    title = StringField(
        "Section Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Section title cannot exceed 255 characters.",
            ),
        ],
    )

    subtitle = StringField(
        "Section Subtitle",
        validators=[
            Optional(),
            Length(
                max=500,
                message="Section subtitle cannot exceed 500 characters.",
            ),
        ],
    )

    # =========================================================================
    # Section Content
    # =========================================================================

    content = TextAreaField(
        "Section Content",
        validators=[
            Optional(),
        ],
    )

    # =========================================================================
    # Call To Action
    # =========================================================================

    cta_text = StringField(
        "CTA Text",
        validators=[
            Optional(),
            Length(
                max=100,
                message="CTA text cannot exceed 100 characters.",
            ),
        ],
    )

    cta_url = StringField(
        "CTA URL",
        validators=[
            Optional(),
            Length(
                max=500,
                message="CTA URL cannot exceed 500 characters.",
            ),
            _validate_cta_url,
        ],
    )

    # =========================================================================
    # Media Asset
    # =========================================================================

    media_asset_id = SelectField(
        "Media Asset",
        coerce=int,
        validators=[
            Optional(),
        ],
        default=0,
    )

    # =========================================================================
    # Display Configuration
    # =========================================================================

    display_order = IntegerField(
        "Display Order",
        validators=[
            InputRequired(
                message="Please provide a display order.",
            ),
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
        default=0,
    )

    is_visible = BooleanField(
        "Visible on Homepage",
        default=True,
    )

    # =========================================================================
    # Submit
    # =========================================================================

    submit = SubmitField(
        "Save Section",
    )

    # =========================================================================
    # Initialization
    # =========================================================================
    def __init__(self, *args, **kwargs):
        """
        Initialize the form and populate media choices from the
        folder appropriate to the selected homepage section type.
        """
        super().__init__(*args, **kwargs)

        # Determine the section type from submitted form data,
        # or from the existing section when editing.
        section_type = self.section_type.data

        if not section_type:
            section_type = getattr(
                getattr(self, "obj", None),
                "section_type",
                None,
            )

        folder_name_by_type = {
            "hero": "Hero",
            "featured_experiences": "Featured Experiences",
            "featured_experience_card": "Featured Experiences",
            "destinations": "Destinations",
            "destination_card": "Destinations",
        }

        folder_name = folder_name_by_type.get(section_type)

        assets = []

        if folder_name:
            folder = (
                MediaFolder.query
                .filter_by(
                    name=folder_name,
                    parent_id=(
                        MediaFolder.query
                        .filter_by(
                            slug="homepage",
                            active=True,
                        )
                        .with_entities(MediaFolder.id)
                        .scalar_subquery()
                    ),
                    active=True,
                )
                .first()
            )

            if folder:
                assets = get_cms_media_assets(
                    folder_id=folder.id,
                    include_descendants=False,
                    active_only=True,
                )

                # Homepage hero and cards use image assets.
                # Hero videos remain supported.
                if section_type == "hero":
                    assets = [
                        asset for asset in assets
                        if asset.media_type in {"image", "video"}
                    ]
                else:
                    assets = [
                        asset for asset in assets
                        if asset.media_type == "image"
                    ]

        self.media_asset_id.choices = [
            (0, "No Media Asset"),
        ]

        self.media_asset_id.choices.extend([
            (
                asset.id,
                asset.title
                or asset.original_filename
                or asset.filename,
            )
            for asset in assets
        ])



    # =========================================================================
    # Cross-Field Validation
    # =========================================================================

    def validate(self, extra_validators=None):
        """
        Perform form-level validation that depends on multiple fields.

        Rules
        -----
        1. Hero sections require a title.
        2. Hero sections require an active media asset.
        3. Heading-only sections cannot use media.
        4. CTA text and CTA URL must be supplied together.
        """

        is_valid = super().validate(
            extra_validators=extra_validators,
        )

        # ---------------------------------------------------------------------
        # Normalize values
        # ---------------------------------------------------------------------

        section_type = (
            self.section_type.data.strip()
            if isinstance(self.section_type.data, str)
            else self.section_type.data
        )

        title = (
            self.title.data.strip()
            if isinstance(self.title.data, str)
            else ""
        )

        cta_text = (
            self.cta_text.data.strip()
            if isinstance(self.cta_text.data, str)
            else ""
        )

        cta_url = (
            self.cta_url.data.strip()
            if isinstance(self.cta_url.data, str)
            else ""
        )

        media_asset_id = self.media_asset_id.data

        # ---------------------------------------------------------------------
        # Hero validation
        # ---------------------------------------------------------------------

        if section_type == "hero":

            if not title:
                self.title.errors.append(
                    "A Hero title is required."
                )
                is_valid = False

            if not media_asset_id:
                self.media_asset_id.errors.append(
                    "A Hero image or video is required."
                )
                is_valid = False

        # ---------------------------------------------------------------------
        # Heading-only section validation
        # ---------------------------------------------------------------------

        heading_only_types = {
            "featured_experiences",
            "destinations",
        }

        if section_type in heading_only_types:

            if media_asset_id:
                self.media_asset_id.errors.append(
                    "This section is a heading only and cannot have media."
                )
                is_valid = False

        # ---------------------------------------------------------------------
        # CTA pairing validation
        # ---------------------------------------------------------------------

        has_cta_text = bool(cta_text)
        has_cta_url = bool(cta_url)

        if has_cta_text and not has_cta_url:

            self.cta_url.errors.append(
                "Please provide a CTA URL when CTA text is supplied."
            )

            is_valid = False
        elif has_cta_url and not has_cta_text:

            self.cta_text.errors.append(
                "Please provide CTA text when a CTA URL is supplied."
            )
            is_valid = False
        return is_valid

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "AdminHomepageForm",
    "AdminHomepageSectionForm",
]