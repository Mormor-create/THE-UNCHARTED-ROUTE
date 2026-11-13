"""
===============================================================================
The Uncharted Route
Media Asset Model
===============================================================================
Centralized Digital Asset Management (DAM) system.
Every uploaded file in the application is stored here.
Supported Assets
----------------
• Images
• Videos
• Documents
• PDFs
• Icons
• SVG Files
• Logos
• Audio
• Maps
• Brochures

Organization
------------
Media assets can belong to multiple hierarchical MediaFolder records.

Examples:

    Destinations
        └── Nairobi

    Destinations
        └── Amboseli

    Experiences
        └── Wildlife & Conservation

    Stays
        └── JW Marriott
            └── Rooms

An asset may belong to multiple folders without being uploaded multiple times.

Important
---------
MediaAsset is the central source of truth for uploaded media.

Public-facing templates should use:

    asset.browser_url

rather than assuming that a DAM file lives inside Flask's static folder.
"""

from datetime import datetime
from flask import url_for
from extensions import db

class MediaAsset(db.Model):
    """
    Central Digital Asset Management model.
    """

    __tablename__ = "media_assets"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Basic Information
    # =========================================================================
    filename = db.Column(db.String(255),nullable=False,unique=True,)
    original_filename = db.Column(db.String(255),nullable=False,)
    title = db.Column(db.String(255),)
    alt_text = db.Column(db.String(255),)
    caption = db.Column(db.Text,)
    description = db.Column(db.Text,)
    credit = db.Column(db.String(255),)

    # =========================================================================
    # File Information
    # =========================================================================
    file_path = db.Column(db.String(500),nullable=False,)
    file_url = db.Column(db.String(500),)
    mime_type = db.Column(db.String(100),nullable=False,)
    file_extension = db.Column(db.String(20),nullable=False,)
    file_size = db.Column(db.BigInteger,)
    checksum = db.Column(db.String(64),unique=True,)

    # =========================================================================
    # Media Classification
    # =========================================================================
    media_type = db.Column(db.String(50),nullable=False,default="image",index=True,)
    # Supported values:
    #
    # image
    # video
    # document
    # audio
    # icon
    # map
    # logo
    # brochure

    # =========================================================================
    # Intended Usage
    # =========================================================================
    usage = db.Column(db.String(50),nullable=False,default="general",index=True,)

    # Examples:
    #
    # general
    # hero
    # banner
    # featured
    # gallery
    # thumbnail
    # category_card
    # room_gallery
    # room_hero
    # logo
    # icon
    # map
    # social
    # seo
    # brochure

    # =========================================================================
    # Image / Media Metadata
    # =========================================================================
    width = db.Column(db.Integer,)
    height = db.Column(db.Integer,)
    duration = db.Column(db.Integer,)

    # Duration in seconds for video/audio assets.

    # =========================================================================
    # SEO
    # =========================================================================
    seo_title = db.Column(db.String(255),)
    seo_description = db.Column(db.Text,)

    # =========================================================================
    # Legacy Organization Field
    # =========================================================================
    #
    # IMPORTANT:
    # Keep this temporarily so existing assets/data do not break.
    #
    # The hierarchical MediaFolder system is now the proper organization
    # system.
    #
    # This field can be removed later after legacy data has been migrated.
    #

    folder = db.Column(
        db.String(100),
        default="General",
    )

    # =========================================================================
    # Search / Discovery
    # =========================================================================
    tags = db.Column(db.String(500),)

    # Example:
    #
    # wildlife, elephant, safari, Amboseli, Kenya

    # =========================================================================
    # Status
    # =========================================================================
    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    downloadable = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    # =========================================================================
    # Audit
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # =========================================================================
    # Media Folder Relationships
    # =========================================================================

    folder_assignments = db.relationship(
        "MediaAssetFolder",
        back_populates="media_asset",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # =========================================================================
    # Existing Media Relationships
    # =========================================================================

    experience_media = db.relationship(
        "ExperienceMedia",
        back_populates="media_asset",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    stay_media = db.relationship(
        "StayMedia",
        back_populates="media_asset",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    stay_room_media = db.relationship(
        "StayRoomMedia",
        back_populates="media_asset",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # =========================================================================
    # Media Type Properties
    # =========================================================================

    @property
    def is_image(self):
        """
        Return True when this asset is an image.
        """

        return self.media_type == "image"

    @property
    def is_video(self):
        """
        Return True when this asset is a video.
        """

        return self.media_type == "video"

    @property
    def is_document(self):
        """
        Return True when this asset is a document.
        """

        return self.media_type == "document"

    @property
    def is_audio(self):
        """
        Return True when this asset is audio.
        """

        return self.media_type == "audio"

    @property
    def is_icon(self):
        """
        Return True when this asset is an icon.
        """

        return self.media_type == "icon"

    @property
    def is_map(self):
        """
        Return True when this asset is a map.
        """

        return self.media_type == "map"

    @property
    def is_logo(self):
        """
        Return True when this asset is a logo.
        """

        return self.media_type == "logo"

    @property
    def is_brochure(self):
        """
        Return True when this asset is a brochure.
        """

        return self.media_type == "brochure"

    # =========================================================================
    # Browser URL
    # =========================================================================

    @property
    def browser_url(self):
        """
        Return the browser-accessible URL for this DAM asset.

        Priority:

        1. Explicit file_url stored on the asset.
        2. Central DAM serving route using the stored filename.
        3. Central DAM serving route using the stored file path.

        This prevents public templates from incorrectly assuming that
        uploaded DAM files are located inside Flask's static directory.
        """

        if self.file_url:
            return self.file_url

        if self.filename:
            try:
                return url_for(
                    "admin_media.serve_media",
                    filename=self.filename,
                )
            except RuntimeError:
                return None

        if self.file_path:
            try:
                return url_for(
                    "admin_media.serve_media",
                    filename=self.file_path,
                )
            except RuntimeError:
                return None

        return None

    # =========================================================================
    # Human-readable File Size
    # =========================================================================

    @property
    def formatted_size(self):
        """
        Return a human-readable file size.
        """

        if not self.file_size:
            return "Unknown"

        size = self.file_size

        for unit in (
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ):
            if size < 1024:
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} PB"

    # =========================================================================
    # Folder Information
    # =========================================================================

    @property
    def folder_names(self):
        """
        Return the names of all folders assigned to this asset.
        """

        return [
            assignment.folder.name
            for assignment in self.folder_assignments.all()
            if assignment.folder is not None
        ]

    @property
    def folder_paths(self):
        """
        Return complete hierarchical paths for all assigned folders.

        Example:

            [
                "Destinations / Nairobi",
                "Heroes / Destinations",
            ]
        """

        return [
            assignment.folder.full_path
            for assignment in self.folder_assignments.all()
            if assignment.folder is not None
        ]

    @property
    def primary_folder(self):
        """
        Return the primary assigned folder, if one exists.
        """

        assignment = (
            self.folder_assignments
            .filter_by(
                is_primary=True,
            )
            .first()
        )

        return (
            assignment.folder
            if assignment
            else None
        )

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<MediaAsset {self.filename}>"
        )