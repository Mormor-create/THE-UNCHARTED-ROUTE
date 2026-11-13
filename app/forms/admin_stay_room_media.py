"""
===============================================================================
The Uncharted Route
Admin Stay Room Media Forms
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

ROOM_MEDIA_USAGE = [
    ("hero", "Hero"),
    ("thumbnail", "Thumbnail"),
    ("gallery", "Gallery"),
]


class AdminStayRoomMediaForm(FlaskForm):
    """
    Associate a MediaAsset with a StayRoom.

    Media choices are populated from the StayRoom's assigned media folder
    by the route layer using:

        form.set_media_choices(room.media_folder_id)

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
        choices=ROOM_MEDIA_USAGE,
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
        "Save Room Media"
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """
        Initialize the form.

        Media choices are intentionally not populated here because the form
        does not know which StayRoom it belongs to until the route supplies
        the room's assigned media folder.
        """

        super().__init__(
            *args,
            **kwargs,
        )

        self.media_asset_id.choices = [
            (
                0,
                "Select media from this room's folder",
            )
        ]

    def set_media_choices(
        self,
        folder_id,
    ):
        """
        Load active image and video assets from the exact room media folder.

        Descendant folders are deliberately excluded.

        This ensures that a room only sees its own media and cannot select
        media belonging to another room.
        """

        placeholder = [
            (
                0,
                "Select media from this room's folder",
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