
"""
The Uncharted Route
Admin Page Hero Forms
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,)
from wtforms.validators import DataRequired, Length, Optional
from app.services.media_service import (
    get_cms_media_assets,
    get_media_folders,)

PAGE_HERO_FOLDER_NAME = "Page Heroes"

class PageHeroForm(FlaskForm):
    """Create and edit reusable page hero content."""
    page_key = StringField(
        "Page Key",validators=[DataRequired(), Length(max=100)],render_kw={"placeholder": "e.g. experiences"},)
    page_name = StringField("Page Name",validators=[DataRequired(), Length(max=150)],
        render_kw={"placeholder": "e.g. Experiences"},)
    eyebrow = StringField(
        "Eyebrow",validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Explore Kenya"},)
    heading = StringField("Heading",validators=[DataRequired(), Length(max=255)],
        render_kw={"placeholder": "Experiences Worth Remembering"},)
    subheading = TextAreaField(
        "Subheading",
        validators=[Optional()],
        render_kw={
            "rows": 4,
            "placeholder": "A short supporting statement for the page hero.",},)

    # Store MediaAsset IDs, while limiting choices to the Page Heroes folder tree.
    desktop_media_id = SelectField("Desktop Hero Image",coerce=lambda value: int(value) if value else None,validators=[Optional()],)
    mobile_media_id = SelectField("Mobile Hero Image",coerce=lambda value: int(value) if value else None,validators=[Optional()],)
    overlay_style = SelectField(
        "Overlay Style",
        choices=[
            ("dark", "Dark"),
            ("light", "Light"),
            ("none", "No Overlay"),
        ],
        validators=[DataRequired()],
        default="dark",
    )
    image_position = SelectField(
        "Image Position",
        choices=[
            ("center", "Center"),
            ("center top", "Center Top"),
            ("center bottom", "Center Bottom"),
            ("left center", "Left Center"),
            ("right center", "Right Center"),
        ],
        validators=[DataRequired()],
        default="center",
    )

    primary_cta_text = StringField(
        "Primary Button Text",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Explore Experiences"},
    )

    primary_cta_url = StringField(
        "Primary Button URL",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "/experiences"},
    )

    secondary_cta_text = StringField(
        "Secondary Button Text",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Plan Your Journey"},
    )
    secondary_cta_url = StringField(
        "Secondary Button URL",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "/contact"},)
    active = BooleanField("Active", default=True)
    display_order = IntegerField("Display Order",validators=[Optional()],default=0,)
    notes = TextAreaField(
        "Internal Notes",
        validators=[Optional()],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Internal CMS notes. These are not displayed publicly."),},)

    submit = SubmitField("Save Page Hero")
    def set_media_choices(self):
        """
        Load active images from the Page Heroes folder and its descendants.

        The existing Media Library service handles folder membership and
        descendant retrieval. Images from unrelated CMS folders are excluded.
        """

        placeholder = [
            ("", "— Select an image from Page Heroes —")
        ]

        # Resolve the folder by its actual name instead of assuming its ID.
        folders = get_media_folders(active_only=True)

        page_heroes_folder = next(
            (
                folder
                for folder in folders
                if (getattr(folder, "name", "") or "").strip().casefold()
                == PAGE_HERO_FOLDER_NAME.casefold()
            ),
            None,
        )

        if page_heroes_folder is None:
            # Fail closed: never fall back to the entire Media Library.
            self.desktop_media_id.choices = placeholder
            self.mobile_media_id.choices = placeholder
            return

        media_assets = get_cms_media_assets(
            folder_id=page_heroes_folder.id,
            include_descendants=True,
            media_type="image",
            active_only=True,
        )

        choices = list(placeholder)

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

            choices.append((str(media.id), label))

        self.desktop_media_id.choices = choices
        self.mobile_media_id.choices = choices

    def populate_from_model(self, hero):
        """Populate the form from an existing PageHero record."""
        self.page_key.data = hero.page_key
        self.page_name.data = hero.page_name
        self.eyebrow.data = hero.eyebrow
        self.heading.data = hero.heading
        self.subheading.data = hero.subheading
        self.desktop_media_id.data = hero.desktop_media_id
        self.mobile_media_id.data = hero.mobile_media_id
        self.overlay_style.data = hero.overlay_style
        self.image_position.data = hero.image_position
        self.primary_cta_text.data = hero.primary_cta_text
        self.primary_cta_url.data = hero.primary_cta_url
        self.secondary_cta_text.data = hero.secondary_cta_text
        self.secondary_cta_url.data = hero.secondary_cta_url
        self.active.data = hero.active
        self.display_order.data = hero.display_order
        self.notes.data = hero.notes
