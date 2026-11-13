"""
===============================================================================
The Uncharted Route
Blog Forms
===============================================================================

Forms used by the Blog CMS.

Includes:

    • Blog category creation and editing
    • Blog category filtering
    • Blog category sorting
    • Blog category deletion
    • Blog post creation and editing
    • Blog post filtering
    • Publishing
    • Scheduling
    • Status management
    • Archiving
    • Restoring
    • Featured / pinned controls
    • Bulk management
    • SEO
    • Marketing CTA
    • Duplication
    • Statistics filtering
"""

from datetime import datetime

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    URL,
    ValidationError,)

# =============================================================================
# Choices
# =============================================================================
BLOG_STATUS_CHOICES = [
    ("", "All Statuses"),
    ("Draft", "Draft"),
    ("Review", "Review"),
    ("Scheduled", "Scheduled"),
    ("Published", "Published"),
    ("Archived", "Archived"),]

BLOG_STATUS_CREATE_CHOICES = [
    ("Draft", "Draft"),
    ("Review", "Review"),
    ("Scheduled", "Scheduled"),
    ("Published", "Published"),]

BLOG_SORT_CHOICES = [
    ("newest", "Newest First"),
    ("oldest", "Oldest First"),
    ("title_asc", "Title A–Z"),
    ("title_desc", "Title Z–A"),
    ("views_desc", "Most Viewed"),
    ("likes_desc", "Most Liked"),
    ("shares_desc", "Most Shared"),
    ("published_desc", "Recently Published"),
    ("updated_desc", "Recently Updated"),]

BLOG_BULK_ACTION_CHOICES = [
    ("", "Choose Action"),
    ("publish", "Publish Selected"),
    ("unpublish", "Move to Draft"),
    ("review", "Send for Review"),
    ("archive", "Archive Selected"),
    ("restore", "Restore Selected"),
    ("feature", "Feature Selected"),
    ("unfeature", "Remove from Featured"),
    ("pin", "Pin Selected"),
    ("unpin", "Unpin Selected"),
    ("delete", "Delete Selected"),]

CATEGORY_SORT_CHOICES = [
    ("sort_order", "Custom Order"),
    ("name_asc", "Name A–Z"),
    ("name_desc", "Name Z–A"),
    ("newest", "Newest First"),
    ("oldest", "Oldest First"),
    ("posts_desc", "Most Posts"),]

from app.services.media_service import (
    get_cms_media_assets,
    get_media_folders,
)

BLOG_POSTS_FOLDER_NAME = "Blog Posts"
BLOG_CATEGORIES_FOLDER_NAME = "Blog Categories"


def _media_choices_for_folder(folder_name, placeholder_text):
    """
    Return (choices, assets) for active images in an exact Media Library
    folder and its descendants. Never fall back to unrelated folders.
    """
    placeholder = [("", placeholder_text)]
    folders = get_media_folders(active_only=True) or []

    target = (folder_name or "").strip().casefold()
    folder = next(
        (
            item for item in folders
            if (getattr(item, "name", "") or "").strip().casefold() == target
        ),
        None,
    )

    if folder is None:
        current_app.logger.warning(
            "Blog Media CMS folder '%s' was not found among active folders. "
            "Available active folders: %s",
            folder_name,
            [
                getattr(item, "name", None)
                for item in folders
            ],
        )
        return placeholder, []

    try:
        assets = get_cms_media_assets(
            folder_id=folder.id,
            include_descendants=True,
            media_type="image",
            active_only=True,
        ) or []
    except Exception:
        current_app.logger.exception(
            "Could not load image assets from Media CMS folder '%s'.",
            folder_name,
        )
        return placeholder, []

    assets = [
        asset for asset in assets
        if getattr(asset, "id", None) is not None
    ]
    assets.sort(
        key=lambda asset: (
            str(
                getattr(asset, "title", None)
                or getattr(asset, "original_filename", None)
                or getattr(asset, "filename", None)
                or f"Media Asset #{asset.id}"
            ).casefold(),
            str(asset.id),
        )
    )

    choices = list(placeholder)
    for asset in assets:
        title = (
            getattr(asset, "title", None)
            or getattr(asset, "original_filename", None)
            or getattr(asset, "filename", None)
            or f"Media Asset #{asset.id}"
        )
        filename = (
            getattr(asset, "original_filename", None)
            or getattr(asset, "filename", None)
        )
        label = str(title)
        if filename and str(filename) != label:
            label = f"{label} — {filename}"
        choices.append((str(asset.id), label))

    current_app.logger.info(
        "Blog Media CMS folder '%s' (id=%s): loaded %s active image asset(s).",
        folder_name,
        folder.id,
        len(assets),
    )
    if not assets:
        current_app.logger.warning(
            "Blog Media CMS folder '%s' exists but returned no active image assets.",
            folder_name,
        )

    return choices, assets

# =============================================================================
# Helper Validators
# =============================================================================
def validate_schedule_datetime(form, field):
    """
    Ensure scheduled publication is in the future.
    """

    if not field.data:
        return

    if field.data <= datetime.now():
        raise ValidationError(
            "Scheduled publication time must be in the future."
        )


def validate_published_datetime(form, field):
    """
    Ensure a manually supplied publication date is not in the future.
    """

    if not field.data:
        return

    if field.data > datetime.now():
        raise ValidationError(
            "Published date cannot be in the future."
        )


from urllib.parse import urlparse
from wtforms.validators import ValidationError

def validate_cta_button_url(form, field):
    """Accept an internal site path or an absolute HTTP(S) URL."""
    value = (field.data or "").strip()

    if not value:
        return

    # Allow internal paths, but not protocol-relative URLs.
    if value.startswith("/") and not value.startswith("//"):
        return

    parsed = urlparse(value)

    if parsed.scheme in ("http", "https") and parsed.netloc:
        return

    raise ValidationError(
        "Enter a valid internal path or an absolute HTTP(S) URL."
    )

def validate_hex_color(form, field):
    """
    Validate category color values.

    Accepted examples:

        #14B8A6
        #ffffff
        #000000
        #fff
    """

    if not field.data:
        return

    value = field.data.strip()

    if not value.startswith("#"):
        raise ValidationError(
            "Color must be a hexadecimal value beginning with #."
        )

    if len(value) not in (4, 7):
        raise ValidationError(
            "Enter a valid hexadecimal color."
        )

    valid_characters = "0123456789abcdefABCDEF"

    if not all(
        character in valid_characters
        for character in value[1:]
    ):
        raise ValidationError(
            "Enter a valid hexadecimal color."
        )

# =============================================================================
# BLOG CATEGORY FORM
# =============================================================================
class BlogCategoryForm(FlaskForm):
    """Create or edit a blog category."""

    # -------------------------------------------------------------------------
    # Basic information
    # -------------------------------------------------------------------------

    name = StringField(
        "Category Name",
        validators=[
            DataRequired(message="Category name is required."),
            Length(
                min=2,
                max=150,
                message="Category name must be between 2 and 150 characters.",
            ),
        ],
        render_kw={"placeholder": "e.g. Safari Tips"},
    )

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(message="Slug is required."),
            Length(
                min=2,
                max=180,
                message="Slug must be between 2 and 180 characters.",
            ),
        ],
        render_kw={"placeholder": "safari-tips"},
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=5000,
                message="Description cannot exceed 5,000 characters.",
            ),
        ],
        render_kw={
            "rows": 5,
            "placeholder": "Describe what readers can expect from this category...",
        },
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    icon = StringField(
        "Icon",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "e.g. bi-binoculars"},
    )

    color = StringField(
        "Color",
        default="#14B8A6",
        validators=[
            Optional(),
            Length(max=20),
            validate_hex_color,
        ],
        render_kw={"placeholder": "#14B8A6"},
    )

    # Keep the existing string field for compatibility with your service.
    banner_image = StringField(
        "Banner Image URL",
        validators=[Optional(), Length(max=1000)],
        render_kw={
            "placeholder": "Existing image URL or path",
        },
    )

    # New selector populated by _populate_blog_category_media_choices().
    # The selected ID must be resolved to an asset before saving if your
    # category model stores a URL/path rather than a media asset foreign key.
    banner_media_asset_id = SelectField(
        "Banner Image from Media Library",
        choices=[("", "Select an image from Blog Categories")],
        coerce=str,
        validators=[Optional()],
    )

    # -------------------------------------------------------------------------
    # SEO
    # -------------------------------------------------------------------------

    meta_title = StringField(
        "Meta Title",
        validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "SEO title"},
    )

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(max=1000),
        ],
        render_kw={
            "rows": 3,
            "placeholder": "SEO description",
        },
    )

    meta_keywords = TextAreaField(
        "Meta Keywords",
        validators=[Optional(), Length(max=2000)],
        render_kw={
            "rows": 2,
            "placeholder": "safari, kenya, wildlife, travel",
        },
    )

    # -------------------------------------------------------------------------
    # Status and display
    # -------------------------------------------------------------------------

    featured = BooleanField("Featured Category", default=False)
    active = BooleanField("Active", default=True)

    sort_order = IntegerField(
        "Sort Order",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=9999,
                message="Sort order must be between 0 and 9,999.",
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------
    submit = SubmitField("Save Category")


    def set_media_choices(self):
        """Load banner images only from Blog Categories and its descendants."""
        choices, assets = _media_choices_for_folder(
            BLOG_CATEGORIES_FOLDER_NAME,
            "— Select an image from Blog Categories —",
        )
        self.banner_media_asset_id.choices = choices
        self._category_media_assets = assets


class BlogCategoryFilterForm(FlaskForm):
    """
    Filter and search blog categories.
    """
    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=150),
        ],
        render_kw={
            "placeholder": "Search categories..."},)

    active = SelectField(
        "Status",
        choices=[
            ("", "All"),
            ("1", "Active"),
            ("0", "Inactive"),
        ],
        default="",
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("1", "Featured"),
            ("0", "Not Featured"),
        ],
        default="",
    )

    sort = SelectField(
        "Sort By",
        choices=CATEGORY_SORT_CHOICES,
        default="sort_order",
    )

    submit = SubmitField(
        "Filter"
    )


class BlogCategorySortForm(FlaskForm):
    """
    Update the display order of a blog category.
    """

    sort_order = IntegerField(
        "Sort Order",
        validators=[
            DataRequired(
                message="Sort order is required."
            ),
            NumberRange(
                min=0,
                max=9999,
                message="Sort order must be between 0 and 9,999.",
            ),
        ],
    )

    submit = SubmitField(
        "Update Order"
    )

class BlogCategoryDeleteForm(FlaskForm):
    """
    Confirm deletion of a blog category.
    """

    confirm = BooleanField(
        "Confirm deletion",
        validators=[
            DataRequired(
                message="Please confirm deletion."
            ),
        ],
    )

    submit = SubmitField(
        "Delete Category"
    )

# =============================================================================
# Blog Post Forms
# =============================================================================
class BlogPostForm(FlaskForm):
    """
    Create or edit a blog post.
    """

    def set_media_choices(self):
        """Load featured/social images only from Blog Posts and descendants."""
        choices, assets = _media_choices_for_folder(
            BLOG_POSTS_FOLDER_NAME,
            "— Select an image from Blog Posts —",
        )
        self.featured_media_asset_id.choices = list(choices)
        self.social_media_asset_id.choices = list(choices)
        self._post_media_assets = assets

    # -------------------------------------------------------------------------
    # Category
    # -------------------------------------------------------------------------
    category_id = SelectField(
        "Category",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(
                message="Please select a blog category."),],)

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------
    title = StringField(
        "Title",
        validators=[
            DataRequired(
                message="Blog post title is required."
            ),
            Length(
                min=3,
                max=255,
                message=(
                    "Title must be between "
                    "3 and 255 characters."
                ),),],
        render_kw={
            "placeholder": "Enter the blog post title..."},)

    slug = StringField(
        "Slug",
        validators=[
            DataRequired(
                message="Slug is required."
            ),
            Length(
                min=2,
                max=300,
                message=(
                    "Slug must be between "
                    "2 and 300 characters."
                ),
            ),
        ],
        render_kw={
            "placeholder": "your-blog-post-slug"
        },
    )

    subtitle = StringField(
        "Subtitle",
        validators=[
            Optional(),
            Length(
                max=500,
                message="Subtitle cannot exceed 500 characters.",
            ),
        ],
        render_kw={
            "placeholder": "Optional supporting headline..."
        },
    )

    excerpt = TextAreaField(
        "Excerpt",
        validators=[
            Optional(),
            Length(
                max=5000,
                message="Excerpt cannot exceed 5,000 characters.",
            ),
        ],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Short summary used in blog cards, "
                "previews and SEO..."
            ),
        },
    )

    content = TextAreaField(
        "Content",
        validators=[
            DataRequired(
                message="Blog post content is required."
            ),
        ],
        render_kw={
            "rows": 20,
            "placeholder": "Write your blog article here...",
            "class": (
                "blog-content-editor form-control "
                "w-full rounded-xl border border-gray-300 "
                "px-4 py-3 focus:border-green-700 "
                "focus:ring-2 focus:ring-green-700/20"
            ),
            "data-editor": "rich-text",
            "aria-label": "Blog post content",
        },
    )

    # -------------------------------------------------------------------------
    # Author
    # -------------------------------------------------------------------------

    author = StringField(
        "Author",
        validators=[
            DataRequired(
                message="Author name is required."
            ),
            Length(
                min=2,
                max=150,
                message=(
                    "Author name must be between "
                    "2 and 150 characters."
                ),
            ),
        ],
        render_kw={
            "placeholder": "Author name"
        },
    )

    author_title = StringField(
        "Author Title",
        validators=[
            Optional(),
            Length(max=150),
        ],
        render_kw={
            "placeholder": (
                "e.g. Travel Writer & Safari Specialist"
            ),
        },
    )

    author_photo = StringField(
        "Author Photo",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Author photo path or media asset"
        },
    )

    # Legacy URL/path fields retained for existing templates and records.
    # New images should be selected from the Media Library below.
    featured_image = StringField(
        "Featured Image URL (optional fallback)",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Select an image below, or enter an existing URL/path"},
    )

    featured_image_alt = StringField(
        "Featured Image Alt Text",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Describe the featured image"},
    )

    cover_video = StringField(
        "Cover Video URL",
        validators=[Optional(), Length(max=1000)],
        render_kw={"placeholder": "Optional video URL"},
    )

    # -------------------------------------------------------------------------
    # Media Library selectors
    # -------------------------------------------------------------------------
    featured_media_asset_id = SelectField(
        "Featured Image from Media Library",
        choices=[("", "Select an image from Blog Posts")],
        coerce=str,
        validators=[Optional()],
    )

    social_media_asset_id = SelectField(
        "Social Image from Media Library",
        choices=[("", "Use featured image or select a social image")],
        coerce=str,
        validators=[Optional()],
    )

    gallery = TextAreaField(
        "Gallery",
        validators=[
            Optional(),
        ],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Optional gallery data. "
                "Service layer may convert this to JSON."
            ),
        },
    )

    # -------------------------------------------------------------------------
    # Reading Information
    # -------------------------------------------------------------------------

    reading_time = IntegerField(
        "Reading Time (minutes)",
        default=5,
        validators=[
            Optional(),
            NumberRange(
                min=1,
                max=999,
                message=(
                    "Reading time must be between "
                    "1 and 999 minutes."
                ),
            ),
        ],
    )

    word_count = IntegerField(
        "Word Count",
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=1000000,
                message="Word count must be a valid positive number.",
            ),
        ],
    )

    # -------------------------------------------------------------------------
    # Publishing
    # -------------------------------------------------------------------------

    status = SelectField(
        "Status",
        choices=BLOG_STATUS_CREATE_CHOICES,
        default="Draft",
        validators=[
            DataRequired(
                message="Please select a post status."
            ),
        ],
    )

    published_at = DateTimeLocalField(
        "Published At",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_published_datetime,
        ],
    )

    scheduled_for = DateTimeLocalField(
        "Schedule For",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_schedule_datetime,
        ],
    )

    featured = BooleanField(
        "Featured Post",
        default=False,
    )

    pinned = BooleanField(
        "Pin to Top",
        default=False,
    )

    allow_comments = BooleanField(
        "Allow Comments",
        default=True,
    )

    # -------------------------------------------------------------------------
    # Related Content
    # -------------------------------------------------------------------------

    related_experience_id = SelectField(
        "Related Experience",
        coerce=int,
        choices=[(0, "None")],
        validators=[
            Optional(),
        ],
    )

    related_destination_id = SelectField(
        "Related Destination",
        coerce=int,
        choices=[(0, "None")],
        validators=[
            Optional(),
        ],
    )

    # -------------------------------------------------------------------------
    # Marketing CTA
    # -------------------------------------------------------------------------

    cta_title = StringField(
        "CTA Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Ready for your next adventure?"
        },
    )

    cta_text = TextAreaField(
        "CTA Text",
        validators=[
            Optional(),
            Length(max=5000),
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Supporting call-to-action text..."
        },
    )

    cta_button_text = StringField(
        "CTA Button Text",
        validators=[
            Optional(),
            Length(max=100),
        ],
        render_kw={
            "placeholder": "Explore Experiences"},)

    cta_button_url = StringField(
        "CTA Button URL",
        validators=[
            Optional(),
            Length(max=500),
            validate_cta_button_url,
        ],
        render_kw={
            "placeholder": "/experiences/nairobi-national-park-experience"},)

    # -------------------------------------------------------------------------
    # SEO
    # -------------------------------------------------------------------------
    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "SEO title"},)

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(max=1000),
        ],
        render_kw={
            "rows": 3,
            "placeholder": "SEO description"},)

    meta_keywords = TextAreaField(
        "Meta Keywords",
        validators=[
            Optional(),
            Length(max=2000),
        ],
        render_kw={
            "rows": 2,
            "placeholder": "kenya, safari, travel, wildlife"},)

    canonical_url = StringField(
        "Canonical URL",
        validators=[
            Optional(),
            Length(max=500),
            URL(
                message="Please enter a valid canonical URL."
            ),
        ],
        render_kw={
            "placeholder": "https://..."
        },
    )

    social_title = StringField(
        "Social Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Title used when shared socially"
        },
    )

    social_description = TextAreaField(
        "Social Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Description used when shared socially"
        },
    )

    social_image = StringField(
        "Social Image",
        validators=[
            Optional(),
            Length(max=1000),
        ],
        render_kw={
            "placeholder": "Social image path or media asset"
        },
    )

    # -------------------------------------------------------------------------
    # Submit
    # -------------------------------------------------------------------------

    submit = SubmitField(
        "Save Blog Post"
    )

# =============================================================================
# Blog Post Filter Form
# =============================================================================
class BlogPostFilterForm(FlaskForm):
    """
    Filter and search blog posts.
    """

    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": (
                "Search posts by title, author or content..."
            ),
        },
    )

    category_id = SelectField(
        "Category",
        coerce=int,
        choices=[(0, "All Categories")],
        default=0,
        validators=[
            Optional(),
        ],
    )

    status = SelectField(
        "Status",
        choices=BLOG_STATUS_CHOICES,
        default="",
    )

    author = StringField(
        "Author",
        validators=[
            Optional(),
            Length(max=150),
        ],
        render_kw={
            "placeholder": "Author"
        },
    )

    featured = SelectField(
        "Featured",
        choices=[
            ("", "All"),
            ("1", "Featured"),
            ("0", "Not Featured"),
        ],
        default="",
    )

    pinned = SelectField(
        "Pinned",
        choices=[
            ("", "All"),
            ("1", "Pinned"),
            ("0", "Not Pinned"),
        ],
        default="",
    )

    allow_comments = SelectField(
        "Comments",
        choices=[
            ("", "All"),
            ("1", "Allowed"),
            ("0", "Disabled"),
        ],
        default="",
    )

    search_indexed = SelectField(
        "Search Indexed",
        choices=[
            ("", "All"),
            ("1", "Indexed"),
            ("0", "Not Indexed"),
        ],
        default="",
    )

    newsletter_sent = SelectField(
        "Newsletter",
        choices=[
            ("", "All"),
            ("1", "Sent"),
            ("0", "Not Sent"),
        ],
        default="",
    )
    sort = SelectField(
        "Sort By",
        choices=BLOG_SORT_CHOICES,
        default="newest",
    )
    submit = SubmitField(
        "Filter"
    )

# =============================================================================
# Publishing Forms
# =============================================================================
class BlogPostPublishForm(FlaskForm):
    """
    Publish a blog post immediately.
    """

    published_at = DateTimeLocalField(
        "Publication Date",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_published_datetime,
        ],
    )

    submit = SubmitField(
        "Publish Now"
    )


class BlogPostScheduleForm(FlaskForm):
    """
    Schedule a blog post for future publication.
    """

    scheduled_for = DateTimeLocalField(
        "Schedule For",
        format="%Y-%m-%dT%H:%M",
        validators=[
            DataRequired(
                message=(
                    "Please select a publication "
                    "date and time."
                ),
            ),
            validate_schedule_datetime,
        ],
    )

    submit = SubmitField(
        "Schedule Post"
    )


class BlogPostStatusForm(FlaskForm):
    """
    Change the status of a blog post.
    """

    status = SelectField(
        "Status",
        choices=[
            ("Draft", "Draft"),
            ("Review", "Review"),
            ("Scheduled", "Scheduled"),
            ("Published", "Published"),
            ("Archived", "Archived"),
        ],
        validators=[
            DataRequired(
                message="Please select a status."
            ),
        ],
    )

    submit = SubmitField(
        "Update Status"
    )


class BlogPostFeatureForm(FlaskForm):
    """
    Toggle featured status.
    """

    action = HiddenField(
        validators=[
            Optional()
        ]
    )

    submit = SubmitField(
        "Update Featured Status"
    )


class BlogPostPinForm(FlaskForm):
    """
    Toggle pinned status.
    """

    action = HiddenField(
        validators=[
            Optional()
        ]
    )

    submit = SubmitField(
        "Update Pin Status"
    )


class BlogPostRestoreForm(FlaskForm):
    """
    Restore an archived blog post.
    """

    action = HiddenField(
        default="restore"
    )

    submit = SubmitField(
        "Restore Post"
    )


class BlogPostDeleteForm(FlaskForm):
    """
    Confirm deletion of a blog post.
    """

    confirm = BooleanField(
        "Confirm deletion",
        validators=[
            DataRequired(
                message="Please confirm deletion."
            ),
        ],
    )

    submit = SubmitField(
        "Delete Blog Post"
    )


# =============================================================================
# Editorial Workflow Forms
# =============================================================================

class BlogReviewForm(FlaskForm):
    """
    Submit a blog post for editorial review.
    """

    submit = SubmitField(
        "Send for Review"
    )


class BlogUnpublishForm(FlaskForm):
    """
    Move a published blog post back to draft status.
    """

    submit = SubmitField(
        "Move to Draft"
    )


class BlogPostArchiveForm(FlaskForm):
    """
    Archive a blog post.
    """

    action = HiddenField(
        default="archive"
    )

    submit = SubmitField(
        "Archive Post"
    )

# =============================================================================
# SEO Form
# =============================================================================
class BlogPostSEOForm(FlaskForm):
    """
    Manage SEO and social metadata for a blog post.
    """
    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Meta title cannot exceed 255 characters.",
            ),
        ],
        render_kw={
            "placeholder": "SEO title"
        },)

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(
                max=1000,
                message=(
                    "Meta description cannot exceed "
                    "1,000 characters."
                ),
            ),
        ],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Write a concise search-engine description..."
            ),
        },
    )

    meta_keywords = TextAreaField(
        "Meta Keywords",
        validators=[
            Optional(),
            Length(
                max=2000,
                message="Meta keywords cannot exceed 2,000 characters.",
            ),
        ],
        render_kw={
            "rows": 3,
            "placeholder": (
                "kenya safari, kenya travel, "
                "nairobi safari, wildlife"
            ),
        },
    )

    canonical_url = StringField(
        "Canonical URL",
        validators=[
            Optional(),
            Length(max=500),
            URL(
                message="Please enter a valid canonical URL."
            ),
        ],
        render_kw={
            "placeholder": "https://..."
        },
    )

    social_title = StringField(
        "Social Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": (
                "Title displayed when shared socially"
            ),
        },
    )

    social_description = TextAreaField(
        "Social Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
        render_kw={
            "rows": 4,
            "placeholder": (
                "Description displayed when shared "
                "on social platforms..."
            ),
        },
    )

    social_image = StringField(
        "Social Image",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": (
                "Social image path or media asset"
            ),
        },
    )

    social_media_asset_id = SelectField(
        "Social Image from Media Library",
        choices=[("", "— Select an image from Blog Posts —")],
        coerce=str,
        validators=[Optional()],
    )

    def set_media_choices(self):
        """Load social images only from Blog Posts and its descendants."""
        choices, assets = _media_choices_for_folder(
            BLOG_POSTS_FOLDER_NAME,
            "— Select an image from Blog Posts —",
        )
        self.social_media_asset_id.choices = choices
        self._post_media_assets = assets

    submit = SubmitField(
        "Save SEO Settings"
    )


# =============================================================================
# CTA Form
# =============================================================================
class BlogPostCTAForm(FlaskForm):
    """
    Manage the marketing call-to-action for a blog post.
    """

    cta_title = StringField(
        "CTA Title",
        validators=[
            Optional(),
            Length(
                max=255,
                message="CTA title cannot exceed 255 characters.",
            ),
        ],
        render_kw={
            "placeholder": "Ready for your next adventure?"
        },
    )

    cta_text = TextAreaField(
        "CTA Text",
        validators=[
            Optional(),
            Length(
                max=5000,
                message="CTA text cannot exceed 5,000 characters.",
            ),
        ],
        render_kw={
            "rows": 5,
            "placeholder": (
                "Encourage readers to explore "
                "your experiences..."
            ),
        },
    )

    cta_button_text = StringField(
        "CTA Button Text",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Button text cannot exceed 100 characters.",
            ),
        ],
        render_kw={
            "placeholder": "Explore Experiences"
        },
    )

    cta_button_url = StringField(
        "CTA Button URL",
        validators=[
            Optional(),
            Length(max=500),
            URL(
                message="Please enter a valid URL."
            ),
        ],
        render_kw={
            "placeholder": "https://..."},)
    submit = SubmitField("Save CTA")


# =============================================================================
# Bulk Action Form
# =============================================================================
class BlogBulkActionForm(FlaskForm):
    """
    Perform an action on multiple blog posts.
    """

    selected_ids = HiddenField(
        validators=[
            DataRequired(
                message="Please select at least one blog post."
            ),
        ],
    )

    action = SelectField(
        "Bulk Action",
        choices=BLOG_BULK_ACTION_CHOICES,
        validators=[
            DataRequired(
                message="Please select a bulk action."
            ),
        ],
    )

    confirm = BooleanField(
        "I confirm this bulk action",
        default=False,
    )

    submit = SubmitField(
        "Apply Action"
    )


# =============================================================================
# Duplicate Form
# =============================================================================
class BlogDuplicateForm(FlaskForm):
    """
    Create a draft copy of an existing blog post.
    """

    title = StringField(
        "New Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Leave blank to append 'Copy'"
        },
    )

    submit = SubmitField(
        "Duplicate Post"
    )


# =============================================================================
# Statistics / Reporting Filter
# =============================================================================
class BlogStatisticsFilterForm(FlaskForm):
    """
    Filter blog statistics.
    """

    category_id = SelectField(
        "Category",
        coerce=int,
        choices=[(0, "All Categories")],
        default=0,
        validators=[
            Optional(),
        ],
    )

    status = SelectField(
        "Status",
        choices=BLOG_STATUS_CHOICES,
        default="",
    )

    author = StringField(
        "Author",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    sort = SelectField(
        "Sort By",
        choices=[
            ("views", "Views"),
            ("likes", "Likes"),
            ("shares", "Shares"),
            ("engagement", "Engagement"),
            ("recent", "Recently Published"),
        ],
        default="views",
    )

    submit = SubmitField(
        "Apply"
    )
