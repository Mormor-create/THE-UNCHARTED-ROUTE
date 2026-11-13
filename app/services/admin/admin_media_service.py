"""
The Uncharted Route — Administrative Media Service

Business logic for the Central Digital Asset Management (DAM) system.

Responsibilities
----------------
• Retrieve media assets
• Filter and search media assets
• Create media assets
• Update media metadata
• Activate / deactivate assets
• Feature / unfeature assets
• Control download availability
• Delete media assets
• Validate media assets
• Store uploaded files
• Generate browser-accessible media URLs

Architecture
------------
Route → Form → Service → Model

The MediaAsset model remains the single source of truth for uploaded
digital assets throughout the application.

Other systems such as:

• Homepage
• Experiences
• Destinations
• Blog
• Testimonials

reference MediaAsset records rather than duplicating file information.
"""

from datetime import datetime
import hashlib
import os
import uuid

from flask import current_app, url_for
from werkzeug.utils import secure_filename

from app.models import MediaAsset
from extensions import db


# =============================================================================
# Constants
# =============================================================================

ALLOWED_MEDIA_TYPES = {
    "image",
    "video",
    "document",
    "audio",
    "icon",
    "map",
}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
    "avif",
}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov",
    "avi",
    "mkv",
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "txt",
}

ALLOWED_AUDIO_EXTENSIONS = {
    "mp3",
    "wav",
    "ogg",
    "m4a",
    "aac",
}

ALLOWED_ICON_EXTENSIONS = {
    "svg",
    "ico",
}

ALLOWED_MAP_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "svg",
    "pdf",
}

ALLOWED_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS
    | ALLOWED_VIDEO_EXTENSIONS
    | ALLOWED_DOCUMENT_EXTENSIONS
    | ALLOWED_AUDIO_EXTENSIONS
    | ALLOWED_ICON_EXTENSIONS
    | ALLOWED_MAP_EXTENSIONS
)


# =============================================================================
# Upload Configuration
# =============================================================================

def _get_upload_folder():
    """
    Return the configured DAM upload directory.

    The directory is created automatically when it does not exist.
    """

    folder = current_app.config.get("UPLOAD_FOLDER")

    if not folder:
        raise ValueError(
            "The application upload folder is not configured."
        )

    folder = os.path.abspath(folder)

    os.makedirs(
        folder,
        exist_ok=True,
    )

    return folder


def _get_static_folder():
    """
    Return Flask's static directory as an absolute path.
    """

    static_folder = current_app.static_folder

    if not static_folder:
        return None

    return os.path.abspath(static_folder)


def _build_file_url(file_path=None, filename=None):
    """
    Build a browser-accessible URL for a stored media file.

    DAM uploads normally live outside Flask's static directory, so they
    must be served through the dedicated media-serving route.

    Parameters
    ----------
    file_path : str | None
        Physical filesystem path to the stored file.

    filename : str | None
        Stored MediaAsset filename.

    Returns
    -------
    str | None
        Browser-accessible URL when a filename can be determined.
    """

    storage_filename = None

    if filename:
        storage_filename = os.path.basename(
            str(filename).strip()
        )

    elif file_path:
        storage_filename = os.path.basename(
            os.path.abspath(file_path)
        )

    if not storage_filename:
        return None

    return url_for(
        "admin_media.serve_media",
        filename=storage_filename,
    )


def _get_media_browser_url(asset):
    """
    Resolve the best browser-accessible URL for an existing asset.

    Priority
    --------
    1. Stored file_url
    2. Dedicated DAM media-serving URL generated from filename
    3. Dedicated DAM media-serving URL generated from file_path

    This helper is useful for existing records where file_url may
    still be empty because they were uploaded before browser URLs
    were introduced.
    """

    if asset is None:
        return None

    if asset.file_url:
        return asset.file_url

    if asset.filename:
        return _build_file_url(
            filename=asset.filename
        )

    if asset.file_path:
        return _build_file_url(
            file_path=asset.file_path
        )

    return None


# =============================================================================
# Media Type Detection
# =============================================================================

def _detect_media_type(extension):
    """
    Determine the DAM media type from a file extension.
    """

    extension = normalize_extension(
        extension
    )

    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return "image"

    if extension in ALLOWED_VIDEO_EXTENSIONS:
        return "video"

    if extension in ALLOWED_DOCUMENT_EXTENSIONS:
        return "document"

    if extension in ALLOWED_AUDIO_EXTENSIONS:
        return "audio"

    if extension in ALLOWED_ICON_EXTENSIONS:
        return "icon"

    if extension in ALLOWED_MAP_EXTENSIONS:
        return "map"

    raise ValueError(
        f"The .{extension} file type is not supported."
    )


# =============================================================================
# Filename / File Helpers
# =============================================================================

def _generate_storage_filename(extension):
    """
    Generate a unique filename for physical storage.
    """

    return (
        f"{uuid.uuid4().hex}."
        f"{normalize_extension(extension)}"
    )


def _calculate_checksum(file_object):
    """
    Calculate a SHA-256 checksum for an uploaded file.
    """

    sha256 = hashlib.sha256()

    file_object.seek(0)

    while True:
        chunk = file_object.read(
            1024 * 1024
        )

        if not chunk:
            break

        sha256.update(chunk)

    file_object.seek(0)

    return sha256.hexdigest()


def _get_file_size(file_object):
    """
    Determine uploaded file size in bytes.
    """

    current_position = file_object.tell()

    file_object.seek(
        0,
        os.SEEK_END,
    )

    size = file_object.tell()

    file_object.seek(
        current_position
    )

    return size


# =============================================================================
# Authorization
# =============================================================================

def can_manage_media(user):
    """
    Determine whether a user may manage the media library.

    Returns
    -------
    bool
        True when the user is an active administrator.
    """

    if user is None:
        return False

    return bool(
        user.is_active
        and user.is_admin
    )


def _require_admin(user):
    """
    Administrative authorization is temporarily disabled during
    CMS setup and testing.

    Route-level administrator protection can be restored later by
    enabling @admin_required on the administrative routes.
    """

    return None


# =============================================================================
# Normalization Helpers
# =============================================================================

def _clean(value):
    """
    Normalize optional text values.

    Empty strings become None.
    """

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def normalize_media_type(media_type):
    """
    Normalize and validate a media type.

    Returns
    -------
    str
        Normalized media type.

    Raises
    ------
    ValueError
        When the media type is invalid.
    """

    normalized = (
        media_type.strip().lower()
        if media_type
        else ""
    )

    if normalized not in ALLOWED_MEDIA_TYPES:
        raise ValueError(
            "Invalid media type."
        )

    return normalized


def normalize_extension(extension):
    """
    Normalize a file extension.

    The leading dot is removed when supplied.
    """

    if not extension:
        return ""

    extension = str(extension).strip().lower()

    if extension.startswith("."):
        extension = extension[1:]

    return extension


# =============================================================================
# Extension Validation
# =============================================================================

def validate_media_extension(
    media_type,
    file_extension,
):
    """
    Validate that a file extension is appropriate for its media type.

    Returns
    -------
    bool
        True when valid.

    Raises
    ------
    ValueError
        When the extension is not permitted.
    """

    media_type = normalize_media_type(
        media_type
    )

    extension = normalize_extension(
        file_extension
    )

    extension_groups = {
        "image": ALLOWED_IMAGE_EXTENSIONS,
        "video": ALLOWED_VIDEO_EXTENSIONS,
        "document": ALLOWED_DOCUMENT_EXTENSIONS,
        "audio": ALLOWED_AUDIO_EXTENSIONS,
        "icon": ALLOWED_ICON_EXTENSIONS,
        "map": ALLOWED_MAP_EXTENSIONS,
    }

    allowed_extensions = extension_groups[
        media_type
    ]

    if extension not in allowed_extensions:
        raise ValueError(
            f"The .{extension} file extension is not valid "
            f"for {media_type} media."
        )

    return True


# =============================================================================
# Media Retrieval
# =============================================================================

def get_media_asset(media_asset_id):
    """
    Retrieve a media asset by primary key.

    Returns
    -------
    MediaAsset | None
    """

    if not media_asset_id:
        return None

    return db.session.get(
        MediaAsset,
        media_asset_id,
    )


def get_media_assets(
    media_type=None,
    folder=None,
    active_only=False,
    featured_only=False,
    search=None,
):
    """
    Retrieve media assets using optional filters.

    Results are ordered with newest assets first.
    """

    query = MediaAsset.query

    if media_type:
        normalized_type = normalize_media_type(
            media_type
        )

        query = query.filter(
            MediaAsset.media_type == normalized_type
        )

    if folder:
        query = query.filter(
            MediaAsset.folder == folder.strip()
        )

    if active_only:
        query = query.filter(
            MediaAsset.active.is_(True)
        )

    if featured_only:
        query = query.filter(
            MediaAsset.featured.is_(True)
        )

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            db.or_(
                MediaAsset.title.ilike(search_term),
                MediaAsset.filename.ilike(search_term),
                MediaAsset.original_filename.ilike(search_term),
                MediaAsset.alt_text.ilike(search_term),
                MediaAsset.caption.ilike(search_term),
                MediaAsset.description.ilike(search_term),
                MediaAsset.tags.ilike(search_term),
            )
        )

    return query.order_by(
        MediaAsset.created_at.desc(),
        MediaAsset.id.desc(),
    ).all()


def get_active_media_assets(
    media_type=None,
):
    """
    Return active media assets.

    Useful when populating media selectors throughout
    the administrative CMS.
    """

    return get_media_assets(
        media_type=media_type,
        active_only=True,
    )


def get_featured_media_assets(
    media_type=None,
):
    """
    Return featured media assets.
    """

    return get_media_assets(
        media_type=media_type,
        active_only=True,
        featured_only=True,
    )


def get_media_folders():
    """
    Return all distinct DAM folders.

    Returns
    -------
    list[str]
        Alphabetically ordered folder names.
    """

    rows = (
        db.session.query(
            MediaAsset.folder
        )
        .filter(
            MediaAsset.folder.isnot(None)
        )
        .distinct()
        .order_by(
            MediaAsset.folder.asc()
        )
        .all()
    )

    return [
        row[0]
        for row in rows
        if row[0]
    ]


# =============================================================================
# Media Upload
# =============================================================================
def upload_media_asset(
    acting_admin,
    file,
    title=None,
    alt_text=None,
    caption=None,
    description=None,
    credit=None,
    media_type=None,
    folder="General",
    tags=None,
    seo_title=None,
    seo_description=None,
    downloadable=False,
    featured=False,
    active=True,
):
    """
    Store an uploaded file and create its MediaAsset record.

    Media type is automatically detected from the file extension
    when it is not supplied.

    Physical file storage and database registration are handled
    together so that the MediaAsset record represents an actual
    uploaded file.

    Returns
    -------
    MediaAsset
        Newly created media asset.
    """

    _require_admin(
        acting_admin
    )

    if file is None:
        raise ValueError(
            "Please select a file to upload."
        )

    original_filename = secure_filename(
        file.filename or ""
    )

    if not original_filename:
        raise ValueError(
            "The uploaded file has no valid filename."
        )

    if "." not in original_filename:
        raise ValueError(
            "The uploaded file must have an extension."
        )

    extension = normalize_extension(
        original_filename.rsplit(
            ".",
            1,
        )[1]
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"The .{extension} file type is not supported."
        )

    detected_media_type = _detect_media_type(
        extension
    )

    if media_type:
        normalized_media_type = normalize_media_type(
            media_type
        )

        validate_media_extension(
            normalized_media_type,
            extension,
        )
    else:
        normalized_media_type = detected_media_type

    checksum = _calculate_checksum(
        file
    )

    existing_checksum = MediaAsset.query.filter_by(
        checksum=checksum
    ).first()

    if existing_checksum:
        raise ValueError(
            "This file already exists in the media library."
        )

    upload_folder = _get_upload_folder()

    storage_filename = _generate_storage_filename(
        extension
    )

    storage_path = os.path.join(
        upload_folder,
        storage_filename,
    )

    file_size = _get_file_size(
        file
    )

    file.seek(0)

    try:
        file.save(
            storage_path
        )

        # IMPORTANT:
        # The uploaded file normally lives outside Flask's static
        # directory. Therefore its browser URL must use the dedicated
        # DAM serving endpoint rather than Flask's static route.
        file_url = _build_file_url(
            filename=storage_filename
        )

        asset = create_media_asset(
            acting_admin=acting_admin,
            filename=storage_filename,
            original_filename=original_filename,
            file_path=storage_path,
            file_url=file_url,
            mime_type=(
                file.mimetype
                or "application/octet-stream"
            ),
            file_extension=extension,
            file_size=file_size,
            checksum=checksum,
            media_type=normalized_media_type,
            title=title,
            alt_text=alt_text,
            caption=caption,
            description=description,
            credit=credit,
            seo_title=seo_title,
            seo_description=seo_description,
            folder=folder,
            tags=tags,
            active=active,
            featured=featured,
            downloadable=downloadable,
        )

    except Exception:
        if os.path.exists(storage_path):
            try:
                os.remove(
                    storage_path
                )
            except OSError:
                pass

        raise

    return asset


# =============================================================================
# Media Creation
# =============================================================================

def create_media_asset(
    acting_admin,
    filename,
    original_filename,
    file_path,
    mime_type,
    file_extension,
    file_size=None,
    checksum=None,
    media_type="image",
    file_url=None,
    title=None,
    alt_text=None,
    caption=None,
    description=None,
    credit=None,
    width=None,
    height=None,
    duration=None,
    seo_title=None,
    seo_description=None,
    folder="General",
    tags=None,
    active=True,
    featured=False,
    downloadable=False,
):
    """
    Create a MediaAsset record.

    File storage itself should be handled by the upload layer.
    This service stores the resulting file metadata.
    """

    _require_admin(
        acting_admin
    )

    if not filename:
        raise ValueError(
            "A filename is required."
        )

    if not original_filename:
        raise ValueError(
            "The original filename is required."
        )

    if not file_path:
        raise ValueError(
            "A file path is required."
        )

    if not mime_type:
        raise ValueError(
            "A MIME type is required."
        )

    if not file_extension:
        raise ValueError(
            "A file extension is required."
        )

    normalized_media_type = normalize_media_type(
        media_type
    )

    normalized_extension = normalize_extension(
        file_extension
    )

    validate_media_extension(
        normalized_media_type,
        normalized_extension,
    )

    existing_filename = MediaAsset.query.filter_by(
        filename=filename
    ).first()

    if existing_filename:
        raise ValueError(
            "A media asset with this filename already exists."
        )

    if checksum:
        existing_checksum = MediaAsset.query.filter_by(
            checksum=checksum
        ).first()

        if existing_checksum:
            raise ValueError(
                "A media asset with this file checksum already exists."
            )

    # If no URL was supplied, always generate the dedicated DAM URL.
    resolved_file_url = (
        _clean(file_url)
        or _build_file_url(
            filename=filename
        )
        or _build_file_url(
            file_path=file_path
        )
    )

    asset = MediaAsset(
        filename=filename.strip(),
        original_filename=original_filename.strip(),
        title=_clean(title),
        alt_text=_clean(alt_text),
        caption=_clean(caption),
        description=_clean(description),
        credit=_clean(credit),
        file_path=file_path.strip(),
        file_url=resolved_file_url,
        mime_type=mime_type.strip(),
        file_extension=normalized_extension,
        file_size=file_size,
        checksum=_clean(checksum),
        media_type=normalized_media_type,
        width=width,
        height=height,
        duration=duration,
        seo_title=_clean(seo_title),
        seo_description=_clean(seo_description),
        folder=_clean(folder) or "General",
        tags=_clean(tags),
        active=bool(active),
        featured=bool(featured),
        downloadable=bool(downloadable),
    )

    db.session.add(asset)
    db.session.commit()

    return asset


# =============================================================================
# Media Metadata Update
# =============================================================================

def update_media_asset(
    acting_admin,
    asset,
    title=None,
    alt_text=None,
    caption=None,
    description=None,
    credit=None,
    file_url=None,
    seo_title=None,
    seo_description=None,
    folder=None,
    tags=None,
    active=None,
    featured=None,
    downloadable=None,
):
    """
    Update editable metadata for a media asset.

    The physical file itself is not replaced here.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    if title is not None:
        asset.title = _clean(title)

    if alt_text is not None:
        asset.alt_text = _clean(alt_text)

    if caption is not None:
        asset.caption = _clean(caption)

    if description is not None:
        asset.description = _clean(description)

    if credit is not None:
        asset.credit = _clean(credit)

    if file_url is not None:
        asset.file_url = _clean(file_url)

    # If the URL was cleared, rebuild the dedicated DAM URL.
    if not asset.file_url:
        asset.file_url = _get_media_browser_url(
            asset
        )

    if seo_title is not None:
        asset.seo_title = _clean(seo_title)

    if seo_description is not None:
        asset.seo_description = _clean(
            seo_description
        )

    if folder is not None:
        asset.folder = (
            _clean(folder)
            or "General"
        )

    if tags is not None:
        asset.tags = _clean(tags)

    if active is not None:
        asset.active = bool(active)

    if featured is not None:
        asset.featured = bool(featured)

    if downloadable is not None:
        asset.downloadable = bool(
            downloadable
        )

    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


# =============================================================================
# Status Controls
# =============================================================================

def activate_media_asset(
    acting_admin,
    asset,
):
    """
    Activate a media asset.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    asset.active = True
    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def deactivate_media_asset(
    acting_admin,
    asset,
):
    """
    Deactivate a media asset without deleting it.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    asset.active = False
    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def set_media_featured(
    acting_admin,
    asset,
    featured,
):
    """
    Explicitly set whether a media asset is featured.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    asset.featured = bool(
        featured
    )

    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def set_media_downloadable(
    acting_admin,
    asset,
    downloadable,
):
    """
    Explicitly set whether a media asset is downloadable.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    asset.downloadable = bool(
        downloadable
    )

    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


# =============================================================================
# Media Validation
# =============================================================================

def validate_media_asset(asset):
    """
    Validate an existing MediaAsset record.

    Returns
    -------
    bool
        True when the record contains the required
        information for DAM use.
    """

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    if not asset.filename:
        raise ValueError(
            "Media asset filename is required."
        )

    if not asset.original_filename:
        raise ValueError(
            "Original filename is required."
        )

    if not asset.file_path:
        raise ValueError(
            "Media asset file path is required."
        )

    if not asset.mime_type:
        raise ValueError(
            "Media asset MIME type is required."
        )

    if not asset.file_extension:
        raise ValueError(
            "Media asset file extension is required."
        )

    validate_media_extension(
        asset.media_type,
        asset.file_extension,
    )

    return True


# =============================================================================
# Delete Media Asset
# =============================================================================

def delete_media_asset(
    acting_admin,
    asset,
):
    """
    Delete a MediaAsset record.

    This removes the database record.

    Physical file deletion should be handled by the
    storage layer after successful database deletion.
    """

    _require_admin(
        acting_admin
    )

    if asset is None:
        raise ValueError(
            "A valid media asset is required."
        )

    db.session.delete(asset)
    db.session.commit()

    return True


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ALLOWED_MEDIA_TYPES",
    "can_manage_media",
    "get_media_asset",
    "get_media_assets",
    "get_active_media_assets",
    "get_featured_media_assets",
    "get_media_folders",
    "normalize_media_type",
    "validate_media_extension",
    "validate_media_asset",
    "upload_media_asset",
    "create_media_asset",
    "update_media_asset",
    "activate_media_asset",
    "deactivate_media_asset",
    "set_media_featured",
    "set_media_downloadable",
    "delete_media_asset",
]