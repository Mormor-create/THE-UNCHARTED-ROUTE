"""
===============================================================================
The Uncharted Route — Administrative Media Forms
===============================================================================

WTForms used by the administrative Digital Asset Management interface.

Architecture
------------

Route → Form → Service → Model

The DAM supports:

• Media metadata
• Media upload
• Hierarchical folders
• Multiple folder assignments
• Primary folder assignment
• Media usage classification
• Media filtering
• Media editing
• Folder management
"""

from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    FileField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    URL,
)


# =============================================================================
# Media Type Choices
# =============================================================================

MEDIA_TYPE_CHOICES = [
    ("", "Auto-detect"),
    ("image", "Image"),
    ("video", "Video"),
    ("document", "Document"),
    ("audio", "Audio"),
    ("icon", "Icon"),
    ("map", "Map"),
]


# =============================================================================
# Media Usage Choices
# =============================================================================

MEDIA_USAGE_CHOICES = [
    ("general", "General"),
    ("hero", "Hero"),
    ("banner", "Banner"),
    ("featured", "Featured"),
    ("gallery", "Gallery"),
    ("thumbnail", "Thumbnail"),
    ("category_card", "Category Card"),
    ("room_gallery", "Room Gallery"),
    ("room_hero", "Room Hero"),
    ("logo", "Logo"),
    ("icon", "Icon"),
    ("map", "Map"),
    ("social", "Social"),
    ("seo", "SEO"),
    ("brochure", "Brochure"),
]


# =============================================================================
# Media Upload Form
# =============================================================================

class AdminMediaUploadForm(FlaskForm):

    file = FileField(
        "File",
        validators=[
            DataRequired(
                message="Please select a file to upload."
            )
        ],
    )

    title = StringField(
        "Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    alt_text = StringField(
        "Alt Text",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    caption = TextAreaField(
        "Caption",
        validators=[
            Optional(),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    credit = StringField(
        "Credit",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    media_type = SelectField(
        "Media Type",
        choices=MEDIA_TYPE_CHOICES,
        validators=[
            Optional(),
        ],
        default="",
    )

    usage = SelectField(
        "Media Usage",
        choices=MEDIA_USAGE_CHOICES,
        validators=[
            DataRequired(),
        ],
        default="general",
    )

    folder_ids = SelectMultipleField(
        "Folders",
        choices=[],
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    primary_folder_id = SelectField(
        "Primary Folder",
        choices=[],
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    tags = StringField(
        "Tags",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    seo_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    seo_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
        ],
    )

    downloadable = BooleanField(
        "Allow Download",
        default=False,
    )

    featured = BooleanField(
        "Featured Asset",
        default=False,
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField(
        "Upload Media",
    )


# =============================================================================
# Media Edit Form
# =============================================================================
class AdminMediaEditForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    alt_text = StringField(
        "Alt Text",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    caption = TextAreaField(
        "Caption",
        validators=[
            Optional(),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    credit = StringField(
        "Credit",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    media_type = SelectField(
        "Media Type",
        choices=MEDIA_TYPE_CHOICES[1:],
        validators=[
            DataRequired(),
        ],
    )

    usage = SelectField(
        "Media Usage",
        choices=MEDIA_USAGE_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    folder_ids = SelectMultipleField(
        "Folders",
        choices=[],
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    primary_folder_id = SelectField(
        "Primary Folder",
        choices=[],
        coerce=int,
        validators=[
        Optional(),
        ],
    )

    tags = StringField(
        "Tags",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    seo_title = StringField(
        "SEO Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    seo_description = TextAreaField(
        "SEO Description",
        validators=[
            Optional(),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    featured = BooleanField(
        "Featured",
        default=False,
    )

    downloadable = BooleanField(
        "Allow Download",
        default=False,
    )

    submit = SubmitField(
        "Save Changes",
    )


# =============================================================================
# Media Filter Form
# =============================================================================

class AdminMediaFilterForm(FlaskForm):

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    media_type = SelectField(
        "Media Type",
        choices=MEDIA_TYPE_CHOICES,
        validators=[
            Optional(),
        ],
    )

    usage = SelectField(
        "Usage",
        choices=[
            ("", "All Usage"),
            *MEDIA_USAGE_CHOICES,
        ],
        validators=[
            Optional(),
        ],
    )

    folder_id = SelectField(
        "Folder",
        choices=[],
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    active_only = BooleanField(
        "Active Only",
        default=False,
    )

    featured_only = BooleanField(
        "Featured Only",
        default=False,
    )

    submit = SubmitField(
        "Filter",
    )


# =============================================================================
# Media Folder Form
# =============================================================================

class AdminMediaFolderForm(FlaskForm):

    name = StringField(
        "Folder Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    slug = StringField(
        "Slug",
        validators=[
            Optional(),
            Length(max=180),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    parent_id = SelectField(
        "Parent Folder",
        choices=[],
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    folder_type = SelectField(
        "Folder Type",
        choices=[
            ("general", "General"),
            ("hero", "Hero"),
            ("destination", "Destination"),
            ("experience", "Experience"),
            ("experience_category", "Experience Category"),
            ("stay", "Stay"),
            ("stay_room", "Stay Room"),
            ("icon", "Icon"),
            ("logo", "Logo"),
            ("social", "Social"),
            ("document", "Document"),
        ],
        validators=[
            DataRequired(),
        ],
        default="general",
    )

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            Optional(),
        ],
    )

    active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField(
        "Save Folder",
    )


# =============================================================================
# Status Form
# =============================================================================

class AdminMediaStatusForm(FlaskForm):

    submit = SubmitField(
        "Confirm",
    )


# =============================================================================
# Metadata Form
# =============================================================================

class AdminMediaMetadataForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    alt_text = StringField(
        "Alt Text",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    caption = TextAreaField(
        "Caption",
        validators=[
            Optional(),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
        ],
    )

    credit = StringField(
        "Credit",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    submit = SubmitField(
        "Save Metadata",
    )


__all__ = [
    "MEDIA_TYPE_CHOICES",
    "MEDIA_USAGE_CHOICES",
    "AdminMediaUploadForm",
    "AdminMediaEditForm",
    "AdminMediaFilterForm",
    "AdminMediaFolderForm",
    "AdminMediaStatusForm",
    "AdminMediaMetadataForm",
]