"""
The Uncharted Route
Experience Media Forms
"""

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
    InputRequired,
    Length,
    NumberRange,
    Optional,)

EXPERIENCE_MEDIA_USAGES = [
    ("hero", "Hero Image"),
    ("cover", "Cover Image"),
    ("gallery", "Gallery"),
    ("thumbnail", "Thumbnail"),
    ("banner", "Desktop Banner"),
    ("mobile_banner", "Mobile Banner"),
    ("seo", "SEO Image"),
    ("social", "Social Media"),
    ("brochure", "Brochure"),
    ("video", "Video"),
]


class AdminExperienceMediaForm(FlaskForm):
    """Assign a central MediaAsset to an Experience."""

    media_asset_id = SelectField(
        "Media Asset",
        coerce=int,
        choices=[],
        validators=[InputRequired(message="Please select a media asset.")],
    )

    usage = SelectField(
        "Media Usage",
        choices=EXPERIENCE_MEDIA_USAGES,
        validators=[DataRequired()],
        default="gallery",)

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            InputRequired(),
            NumberRange(min=0, message="Display order cannot be negative."),],)

    title = StringField(
        "Display Title",
        validators=[Optional(), Length(max=255)],)

    caption = TextAreaField(
        "Caption",
        validators=[Optional()],)

    photographer = StringField(
        "Photographer / Credit",
        validators=[Optional(), Length(max=255)],)

    featured = BooleanField("Feature this assignment")
    active = BooleanField(
        "Active",
        default=True,)

    submit = SubmitField("Save Media Assignment")