"""
===============================================================================
The Uncharted Route
Admin Stay Media Forms
===============================================================================
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,)
from app.services.media_service import get_cms_media_assets

MEDIA_USAGE = [
    ("hero", "Hero"),
    ("banner", "Banner"),
    ("thumbnail", "Thumbnail"),
    ("gallery", "Gallery"),
]


class AdminStayMediaForm(FlaskForm):
    """
    Associate a MediaAsset with a Stay.

    Media choices are populated from the Stay's assigned media folder
    by the route layer using:

        form.set_media_choices(stay.media_folder_id)

    Only assets directly inside that folder are included.
    """

    media_asset_id = SelectField(
        "Media Asset",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )

    usage = SelectField(
        "Usage",
        choices=MEDIA_USAGE,
        default="gallery",
        validators=[
            DataRequired(),
        ],
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            InputRequired(
                message="Please provide a display order."
            ),
            NumberRange(
                min=0,
                message="Display order cannot be negative.",
            ),
        ],
    )

    caption = StringField(
        "Caption",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField(
        "Save Media"
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """
        Initialize the form.

        Media choices are intentionally not populated here because the form
        does not know which Stay it belongs to until the route supplies the
        Stay's assigned media folder.
        """

        super().__init__(
            *args,
            **kwargs,
        )

        self.media_asset_id.choices = [
            (
                0,
                "Select media from this Stay's folder",
            )
        ]

    def set_media_choices(
        self,
        folder_id,
    ):
        """
        Load active image and video assets from the exact Stay media folder.

        Descendant folders are deliberately excluded.

        This means:

            Stays/
                Fairmont Mount Kenya Safari Club/
                    property-image.jpg
                    property-gallery.jpg
                    Manor Junior Suites/
                        room-image.jpg

        The Fairmont Stay media selector receives only:

            property-image.jpg
            property-gallery.jpg

        It does not receive assets from Manor Junior Suites.
        """

        placeholder = [
            (
                0,
                "Select media from this Stay's folder",
            )
        ]

        if not folder_id:
            self.media_asset_id.choices = placeholder
            return

        assets = get_cms_media_assets(
            folder_id=folder_id,
            include_descendants=False,
            media_type=None,
            active_only=True,
        )

        assets = [
            asset
            for asset in assets
            if getattr(
                asset,
                "media_type",
                None,
            ) in (
                "image",
                "video",
            )
        ]

        assets.sort(
            key=lambda asset: (
                (
                    getattr(
                        asset,
                        "title",
                        None,
                    )
                    or getattr(
                        asset,
                        "original_filename",
                        None,
                    )
                    or getattr(
                        asset,
                        "filename",
                        None,
                    )
                    or f"Media Asset #{asset.id}"
                ).casefold(),
                asset.id,
            )
        )

        choices = list(
            placeholder
        )

        for asset in assets:
            title = (
                getattr(
                    asset,
                    "title",
                    None,
                )
                or getattr(
                    asset,
                    "original_filename",
                    None,
                )
                or getattr(
                    asset,
                    "filename",
                    None,
                )
                or f"Media Asset #{asset.id}"
            )

            media_type = (
                getattr(
                    asset,
                    "media_type",
                    "media",
                ).title()
            )

            choices.append(
                (
                    asset.id,
                    f"{title} ({media_type})",
                )
            )

        self.media_asset_id.choices = choices

    def validate_media_asset_id(
        self,
        field,
    ):
        """
        Ensure an actual media asset was selected.
        """

        if not field.data or field.data == 0:
            raise ValidationError(
                "Please select a media asset."
            )