"""
===============================================================================
The Uncharted Route
Central Digital Asset Management (DAM) Service
===============================================================================
Central business logic for the TUR Digital Asset Management system.

Responsibilities
----------------
• Upload media assets
• Create media assets
• Retrieve media assets
• Search and filter media
• Update media metadata
• Manage hierarchical media folders
• Assign assets to multiple folders
• Set primary folders
• Manage media usage
• Activate / deactivate media
• Feature / unfeature media
• Manage download availability
• Delete media
• Manage ExperienceMedia associations
• Validate uploaded media
• Generate browser-accessible media URLs

Architecture
------------
Route → Form → Service → Model
"""

from datetime import datetime
import hashlib
import os
import uuid

from flask import current_app, url_for
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.models import (
    Experience,
    ExperienceMedia,
    MediaAsset,
    MediaAssetFolder,
    MediaFolder,
)
from extensions import db

# =============================================================================
# Constants
# =============================================================================
VALID_MEDIA_USAGES = {
    "general",
    "hero",
    "banner",
    "featured",
    "gallery",
    "thumbnail",
    "category_card",
    "room_gallery",
    "room_hero",
    "logo",
    "icon",
    "map",
    "social",
    "seo",
    "brochure",}

VALID_FOLDER_TYPES = {
    "general",
    "hero",
    "destination",
    "experience",
    "experience_category",
    "stay",
    "stay_room",
    "icon",
    "logo",
    "social",
    "document",}

ALLOWED_MEDIA_TYPES = {
    "image",
    "video",
    "document",
    "audio",
    "icon",
    "map",}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
    "avif",}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov",
    "avi",
    "mkv",}

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "txt",}

ALLOWED_AUDIO_EXTENSIONS = {
    "mp3",
    "wav",
    "ogg",
    "m4a",
    "aac",}

ALLOWED_ICON_EXTENSIONS = {
    "svg",
    "ico",}

ALLOWED_MAP_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
    "svg",
    "pdf",}

ALLOWED_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS
    | ALLOWED_VIDEO_EXTENSIONS
    | ALLOWED_DOCUMENT_EXTENSIONS
    | ALLOWED_AUDIO_EXTENSIONS
    | ALLOWED_ICON_EXTENSIONS
    | ALLOWED_MAP_EXTENSIONS)

# =============================================================================
# Upload / Storage Helpers
# =============================================================================
def _get_upload_folder():
    """
    Return the configured DAM upload directory.
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


def _build_file_url(
    file_path=None,
    filename=None,
):
    """
    Build a browser-accessible URL for a stored media file.
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
# Authorization
# =============================================================================

def can_manage_media(user):
    """
    Determine whether a user may manage the media library.
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

    Route-level administrator protection can be restored later.
    """

    return None


# =============================================================================
# Normalization Helpers
# =============================================================================

def _clean(value):
    """
    Normalize optional text values.
    """

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def normalize_media_type(media_type):
    """
    Normalize and validate a media type.
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
    """

    if not extension:
        return ""

    extension = str(extension).strip().lower()

    if extension.startswith("."):
        extension = extension[1:]

    return extension


def normalize_media_usage(usage):
    """
    Normalize and validate a MediaAsset usage.
    """

    normalized = (
        usage.strip().lower()
        if usage
        else "general"
    )

    if normalized not in VALID_MEDIA_USAGES:
        raise ValueError(
            "Invalid media usage."
        )

    return normalized


# =============================================================================
# Extension Validation
# =============================================================================

def validate_media_extension(
    media_type,
    file_extension,
):
    """
    Validate that a file extension is appropriate
    for its media type.
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


def _detect_media_type(extension):
    """
    Determine media type from file extension.
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
# File Helpers
# =============================================================================

def _generate_storage_filename(extension):
    """
    Generate a unique physical storage filename.
    """

    return (
        f"{uuid.uuid4().hex}."
        f"{normalize_extension(extension)}"
    )


def _calculate_checksum(file_object):
    """
    Calculate SHA-256 checksum for an uploaded file.
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
# Media Retrieval
# =============================================================================

def get_media_asset(asset_id):
    """
    Retrieve a MediaAsset by ID.
    """

    if not asset_id:
        return None

    return db.session.get(
        MediaAsset,
        asset_id,
    )


def get_active_media_asset(asset_id):
    """
    Retrieve an active MediaAsset.
    """

    asset = get_media_asset(
        asset_id
    )

    if asset is None or not asset.active:
        return None

    return asset


def get_media_assets(
    search=None,
    media_type=None,
    usage=None,
    folder_id=None,
    active_only=False,
    featured_only=False,
):
    """
    Retrieve MediaAssets using DAM filters.
    """

    query = MediaAsset.query

    if active_only:
        query = query.filter(
            MediaAsset.active.is_(True)
        )

    if featured_only:
        query = query.filter(
            MediaAsset.featured.is_(True)
        )

    if media_type:
        query = query.filter(
            MediaAsset.media_type
            == normalize_media_type(media_type)
        )

    if usage:
        query = query.filter(
            MediaAsset.usage
            == normalize_media_usage(usage)
        )

    if folder_id:
        query = (
            query
            .join(
                MediaAssetFolder,
                MediaAssetFolder.media_asset_id
                == MediaAsset.id,
            )
            .filter(
                MediaAssetFolder.folder_id
                == folder_id
            )
        )

    if search:
        search_term = (
            f"%{search.strip()}%"
        )

        query = query.filter(
            or_(
                MediaAsset.filename.ilike(
                    search_term
                ),
                MediaAsset.original_filename.ilike(
                    search_term
                ),
                MediaAsset.title.ilike(
                    search_term
                ),
                MediaAsset.alt_text.ilike(
                    search_term
                ),
                MediaAsset.caption.ilike(
                    search_term
                ),
                MediaAsset.description.ilike(
                    search_term
                ),
                MediaAsset.tags.ilike(
                    search_term
                ),
            )
        )

    return (
        query
        .order_by(
            MediaAsset.created_at.desc(),
            MediaAsset.id.desc(),
        )
        .distinct()
        .all()
    )

def get_cms_media_assets(
    folder_id=None,
    include_descendants=True,
    media_type=None,
    usage=None,
    search=None,
    active_only=True,
):
    """
    Retrieve media assets for CMS selectors using a specific folder.

    Args:
        folder_id: ID of the folder whose media should be retrieved.
        include_descendants: Include media from nested subfolders.
        media_type: Optional media type filter (image, video, etc.).
        usage: Optional usage filter (hero, featured, gallery, etc.).
        search: Optional search term.
        active_only: Only return active assets when True.

    Returns:
        A list of matching MediaAsset records.
    """
    query = MediaAsset.query

    if active_only:
        query = query.filter(MediaAsset.active.is_(True))

    if media_type:
        media_type = normalize_media_type(media_type)
        query = query.filter(MediaAsset.media_type == media_type)

    if usage:
        usage = normalize_media_usage(usage)
        query = query.filter(MediaAsset.usage == usage)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                MediaAsset.title.ilike(search_term),
                MediaAsset.original_filename.ilike(search_term),
                MediaAsset.alt_text.ilike(search_term),
                MediaAsset.caption.ilike(search_term),
                MediaAsset.description.ilike(search_term),
                MediaAsset.tags.ilike(search_term),
            )
        )

    if folder_id is not None:
        folder = get_media_folder(folder_id)

        if folder is None or not folder.active:
            return []

        folder_ids = {folder.id}

        if include_descendants:
            def collect_descendant_ids(parent_folder):
                for child in parent_folder.children.filter(
                    MediaFolder.active.is_(True)
                ).all():
                    folder_ids.add(child.id)
                    collect_descendant_ids(child)

            collect_descendant_ids(folder)

        query = (
            query.join(
                MediaAssetFolder,
                MediaAssetFolder.media_asset_id == MediaAsset.id,
            )
            .filter(MediaAssetFolder.folder_id.in_(folder_ids))
            .distinct()
        )

    return query.order_by(
        MediaAsset.featured.desc(),
        MediaAsset.created_at.desc(),
        MediaAsset.id.desc(),
    ).all()

def search_media_assets(
    query=None,
    media_type=None,
    usage=None,
    folder_id=None,
    active=True,
    featured=None,
    downloadable=None,
):
    """
    Search the media library.
    """

    media_query = MediaAsset.query

    if query:
        search_term = (
            f"%{query.strip()}%"
        )

        media_query = media_query.filter(
            or_(
                MediaAsset.filename.ilike(
                    search_term
                ),
                MediaAsset.original_filename.ilike(
                    search_term
                ),
                MediaAsset.title.ilike(
                    search_term
                ),
                MediaAsset.alt_text.ilike(
                    search_term
                ),
                MediaAsset.caption.ilike(
                    search_term
                ),
                MediaAsset.description.ilike(
                    search_term
                ),
                MediaAsset.tags.ilike(
                    search_term
                ),
            )
        )

    if media_type:
        media_query = media_query.filter(
            MediaAsset.media_type
            == normalize_media_type(media_type)
        )

    if usage:
        media_query = media_query.filter(
            MediaAsset.usage
            == normalize_media_usage(usage)
        )

    if folder_id:
        media_query = (
            media_query
            .join(
                MediaAssetFolder,
                MediaAssetFolder.media_asset_id
                == MediaAsset.id,
            )
            .filter(
                MediaAssetFolder.folder_id
                == folder_id
            )
        )

    if active is not None:
        media_query = media_query.filter(
            MediaAsset.active.is_(active)
        )

    if featured is not None:
        media_query = media_query.filter(
            MediaAsset.featured.is_(featured)
        )

    if downloadable is not None:
        media_query = media_query.filter(
            MediaAsset.downloadable.is_(downloadable)
        )

    return (
        media_query
        .order_by(
            MediaAsset.created_at.desc(),
            MediaAsset.id.desc(),
        )
        .distinct()
        .all()
    )

def get_active_media_assets(
    media_type=None,
):
    return get_media_assets(
        media_type=media_type,
        active_only=True,
    )

def get_featured_media_assets(
    media_type=None,
):
    return get_media_assets(
        media_type=media_type,
        active_only=True,
        featured_only=True,
    )


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
    usage="general",
    folder_ids=None,
    primary_folder_id=None,
    tags=None,
    seo_title=None,
    seo_description=None,
    downloadable=False,
    featured=False,
    active=True,
    width=None,
    height=None,
    duration=None,
):
    """
    Store an uploaded file and create its MediaAsset record.
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

    normalized_usage = normalize_media_usage(
        usage
    )

    checksum = _calculate_checksum(
        file
    )

    existing_checksum = (
        MediaAsset.query
        .filter_by(
            checksum=checksum
        )
        .first()
    )

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
            usage=normalized_usage,
            title=title,
            alt_text=alt_text,
            caption=caption,
            description=description,
            credit=credit,
            width=width,
            height=height,
            duration=duration,
            seo_title=seo_title,
            seo_description=seo_description,
            tags=tags,
            active=active,
            featured=featured,
            downloadable=downloadable,
        )

        if (
            folder_ids is not None
            or primary_folder_id is not None
        ):
            assign_media_folders(
                asset,
                folder_ids=folder_ids,
                primary_folder_id=primary_folder_id,
            )

        return asset

    except Exception:
        db.session.rollback()

        if os.path.exists(storage_path):
            try:
                os.remove(
                    storage_path
                )
            except OSError:
                pass

        raise


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
    usage="general",
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
    tags=None,
    active=True,
    featured=False,
    downloadable=False,
):
    """
    Create a MediaAsset database record.
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

    normalized_usage = normalize_media_usage(
        usage
    )

    existing_filename = (
        MediaAsset.query
        .filter_by(
            filename=filename
        )
        .first()
    )

    if existing_filename:
        raise ValueError(
            "A media asset with this filename already exists."
        )

    if checksum:
        existing_checksum = (
            MediaAsset.query
            .filter_by(
                checksum=checksum
            )
            .first()
        )

        if existing_checksum:
            raise ValueError(
                "A media asset with this file checksum already exists."
            )

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
        usage=normalized_usage,
        width=width,
        height=height,
        duration=duration,
        seo_title=_clean(seo_title),
        seo_description=_clean(seo_description),
        tags=_clean(tags),
        active=bool(active),
        featured=bool(featured),
        downloadable=bool(downloadable),
    )

    db.session.add(
        asset
    )

    db.session.commit()

    return asset

# =============================================================================
# Update Media Asset
# =============================================================================
def update_media_asset(
    acting_admin,
    asset,
    *,
    title=None,
    alt_text=None,
    caption=None,
    description=None,
    credit=None,
    file_url=None,
    seo_title=None,
    seo_description=None,
    tags=None,
    dimensions=None,
    duration=None,
    media_type=None,
    usage=None,
    file_size=None,
    downloadable=None,
    featured=None,
    active=None,
    folder_ids=None,
    primary_folder_id=None,
):
    """
    Update an existing MediaAsset and its DAM folder assignments.
    This is the authoritative media update operation.
    Folder assignments are completely replaced with the submitted
    folder_ids when updating an asset.
    """

    # -------------------------------------------------------------------------
    # Validate asset
    # -------------------------------------------------------------------------

    if asset is None:
        raise ValueError(
            "Media asset not found."
        )

    # -------------------------------------------------------------------------
    # Validate acting administrator
    # -------------------------------------------------------------------------
    if acting_admin is None:
        raise PermissionError("You are not authorized to update media assets.")

    # -------------------------------------------------------------------------
    # Normalize media type
    # -------------------------------------------------------------------------
    if media_type is not None:
        media_type = media_type.strip() or None

    # -------------------------------------------------------------------------
    # Validate usage
    # -------------------------------------------------------------------------
    if usage is not None:
        usage = normalize_media_usage(usage)

    # -------------------------------------------------------------------------
    # Normalize folder IDs
    # -------------------------------------------------------------------------

    if folder_ids is None:
        folder_ids = []

    if not isinstance(
        folder_ids,
        (list, tuple, set),
    ):
        folder_ids = [
            folder_ids
        ]

    normalized_folder_ids = []

    for folder_id in folder_ids:

        if folder_id in (
            None,
            "",
            0,
            "0",
        ):
            continue

        folder_id = int(
            folder_id
        )

        if folder_id not in normalized_folder_ids:
            normalized_folder_ids.append(
                folder_id
            )

    # -------------------------------------------------------------------------
    # Normalize primary folder
    # -------------------------------------------------------------------------

    if primary_folder_id in (
        None,
        "",
        0,
        "0",
    ):
        primary_folder_id = None

    else:
        primary_folder_id = int(
            primary_folder_id
        )

    # -------------------------------------------------------------------------
    # Validate primary folder
    # -------------------------------------------------------------------------

    if (
        primary_folder_id is not None
        and primary_folder_id
        not in normalized_folder_ids
    ):
        raise ValueError(
            "The primary folder must be one of the assigned folders."
        )

    # -------------------------------------------------------------------------
    # Update metadata
    # -------------------------------------------------------------------------

    if title is not None:
        asset.title = title

    if alt_text is not None:
        asset.alt_text = alt_text

    if caption is not None:
        asset.caption = caption

    if description is not None:
        asset.description = description

    if credit is not None:
        asset.credit = credit

    if file_url is not None:
        asset.file_url = file_url

    if seo_title is not None:
        asset.seo_title = seo_title

    if seo_description is not None:
        asset.seo_description = seo_description

    if tags is not None:
        asset.tags = tags

    if duration is not None:
        asset.duration = duration

    if media_type is not None:
        media_type = normalize_media_type(media_type)

    if usage is not None:
        asset.usage = usage

    if file_size is not None:
        asset.file_size = file_size

    if downloadable is not None:
        asset.downloadable = downloadable

    if featured is not None:
        asset.featured = featured

    if active is not None:
        asset.active = active

    # -------------------------------------------------------------------------
    # Update DAM folder assignments
    # -------------------------------------------------------------------------

    assign_media_folders(
        asset,
        normalized_folder_ids,
        primary_folder_id,
        replace_existing=True,
    )

    # -------------------------------------------------------------------------
    # Commit metadata changes
    # -------------------------------------------------------------------------
    # assign_media_folders() already commits the folder assignments.
    # The asset metadata changes are part of the same SQLAlchemy session,
    # so commit here as well to make the update explicit and authoritative.
    # -------------------------------------------------------------------------

    db.session.commit()

    # Refresh the asset from the database.
    db.session.refresh(asset)

    return asset

# =============================================================================
# Status Controls
# =============================================================================
def activate_media_asset(
    acting_admin=None,
    asset=None,
):
    if asset is None:
        asset = acting_admin

    if asset is None:
        raise ValueError(
            "Media asset is required."
        )

    asset.active = True
    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def deactivate_media_asset(
    acting_admin=None,
    asset=None,
):
    if asset is None:
        asset = acting_admin

    if asset is None:
        raise ValueError(
            "Media asset is required."
        )

    asset.active = False
    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def set_media_featured(
    acting_admin=None,
    asset=None,
    featured=True,
):
    if asset is None:
        asset = acting_admin

    if asset is None:
        raise ValueError(
            "Media asset is required."
        )

    asset.featured = bool(
        featured
    )

    asset.updated_at = datetime.utcnow()

    db.session.commit()

    return asset


def set_media_downloadable(
    acting_admin=None,
    asset=None,
    downloadable=True,
):
    if asset is None:
        asset = acting_admin

    if asset is None:
        raise ValueError(
            "Media asset is required."
        )

    asset.downloadable = bool(
        downloadable)
    asset.updated_at = datetime.utcnow()
    db.session.commit()
    return asset

# =============================================================================
# Media Validation
# =============================================================================
def validate_media_asset(asset):
    """
    Validate an existing MediaAsset record.
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

    normalize_media_usage(
        asset.usage)
    return True

# =============================================================================
# Delete Media Asset
# =============================================================================
def delete_media_asset(
    acting_admin=None,
    asset=None,):
    """
    Delete a MediaAsset database record.
    The database cascade removes MediaAssetFolder relationships.
    The physical file is also removed after the database record
    has been successfully deleted.
    """

    if asset is None:
        asset = acting_admin
    if asset is None:
        raise ValueError("Media asset is required.")

    file_path = asset.file_path
    db.session.delete(asset)
    db.session.commit()

    if (
        file_path
        and os.path.isfile(file_path)
    ):
        try:
            os.remove(
                file_path
            )
        except OSError:
            pass

    return True

# =============================================================================
# Media Folder Helpers
# =============================================================================
def get_media_folder(folder_id):
    """
    Retrieve a MediaFolder by ID.
    """
    if not folder_id:
        return None
    return db.session.get(
        MediaFolder,
        folder_id,)

def get_media_folders(
    active_only=True,
    folder_type=None,
):
    """
    Return media folders.
    """

    query = MediaFolder.query

    if active_only is not None:
        query = query.filter(
            MediaFolder.active.is_(active_only)
        )

    if folder_type:
        query = query.filter(
            MediaFolder.folder_type
            == folder_type
        )

    return (
        query
        .order_by(
            MediaFolder.display_order.asc(),
            MediaFolder.name.asc(),
        )
        .all()
    )


def get_all_media_folders(
    active=None,
):
    """
    Retrieve all media folders.

    active=None returns both active and inactive folders.
    """

    query = MediaFolder.query

    if active is not None:
        query = query.filter(
            MediaFolder.active.is_(active)
        )

    return (
        query
        .order_by(
            MediaFolder.display_order.asc(),
            MediaFolder.name.asc(),
        )
        .all()
    )

def _build_folder_tree(folders):
    """
    Return folders in parent-before-child order.
    """

    by_parent = {}

    for folder in folders:
        by_parent.setdefault(
            folder.parent_id,
            [],
        ).append(folder)

    ordered = []

    def walk(
        parent_id,
        depth=0,
    ):
        children = by_parent.get(
            parent_id,
            [],
        )

        for folder in children:
            ordered.append(
                (
                    folder,
                    depth,
                )
            )

            walk(
                folder.id,
                depth + 1,
            )

    walk(None)

    seen = {
        folder.id
        for folder, _ in ordered
    }

    for folder in folders:
        if folder.id not in seen:
            ordered.append(
                (
                    folder,
                    0,
                )
            )
    return ordered

def get_media_folder_by_slug(slug):
    """
    Retrieve a media folder by slug.
    """

    if not slug:
        return None

    normalized_slug = (
        slug.strip().lower()
    )

    if not normalized_slug:
        return None

    return MediaFolder.query.filter_by(
        slug=normalized_slug
    ).first()


# =============================================================================
# Media Folder Choices
# =============================================================================
def get_media_folder_choices(
    active_only=True,
    folder_type=None,
    include_empty=True,
):
    """
    Build WTForms-compatible hierarchical folder choices.

    Integer fields use 0 for the empty choice instead of "".
    """

    folders = get_all_media_folders(
        active=True
        if active_only
        else None
    )

    if folder_type:
        normalized_type = (
            folder_type.strip().lower()
        )

        folders = [
            folder
            for folder in folders
            if folder.folder_type
            == normalized_type
        ]

    children = {}

    for folder in folders:
        children.setdefault(
            folder.parent_id,
            [],
        ).append(folder)

    for child_list in children.values():
        child_list.sort(
            key=lambda item: (
                item.display_order,
                item.name.lower(),
            )
        )

    choices = []

    if include_empty:
        choices.append(
            (
                (0, "No parent — Root folder")
            )
        )

    def add_folder(
        folder,
        depth=0,
    ):
        label = (
            "— " * depth
            + folder.name
        )

        choices.append(
            (
                folder.id,
                label,
            )
        )

        for child in children.get(
            folder.id,
            [],):
            add_folder(
                child,
                depth + 1,)

    for root in children.get(
        None,
        [],):
        add_folder(root)
    return choices

# =============================================================================
# Media Folder Creation
# =============================================================================
def create_media_folder(
    name,
    slug,
    description=None,
    parent_id=None,
    folder_type="general",
    display_order=0,
    active=True,
):
    """
    Create a MediaFolder.
    """

    name = (
        name.strip()
        if isinstance(name, str)
        else ""
    )

    slug = (
        slug.strip().lower()
        if isinstance(slug, str)
        else ""
    )

    folder_type = (
        folder_type.strip().lower()
        if isinstance(folder_type, str)
        and folder_type.strip()
        else "general"
    )

    if not name:
        raise ValueError(
            "Media folder name is required."
        )

    if not slug:
        raise ValueError(
            "Media folder slug is required."
        )

    if folder_type not in VALID_FOLDER_TYPES:
        raise ValueError(
            "Invalid media folder type."
        )

    existing = MediaFolder.query.filter_by(
        slug=slug
    ).first()

    if existing:
        raise ValueError(
            "A media folder with this slug already exists."
        )

    parent = None

    if parent_id not in (
        None,
        "",
        0,
    ):
        parent = db.session.get(
            MediaFolder,
            int(parent_id),
        )

        if parent is None:
            raise ValueError(
                "The selected parent media folder does not exist."
            )

        if not parent.active:
            raise ValueError(
                "An inactive media folder cannot be used as a parent."
            )

    folder = MediaFolder(
        name=name,
        slug=slug,
        description=(
            description.strip()
            if isinstance(description, str)
            and description.strip()
            else None
        ),
        parent_id=(
            parent.id
            if parent
            else None
        ),
        folder_type=folder_type,
        display_order=(
            display_order
            if display_order is not None
            else 0
        ),
        active=bool(active),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(
        folder)
    db.session.commit()
    return folder

# =============================================================================
# Media Folder Update
# =============================================================================
def update_media_folder(
    folder,
    **fields,):
    """
    Update editable MediaFolder fields.
    """

    if folder is None:
        raise ValueError(
            "Media folder is required."
        )

    if "name" in fields:
        name = fields["name"]

        if (
            not isinstance(name, str)
            or not name.strip()
        ):
            raise ValueError(
                "Media folder name is required."
            )

        folder.name = name.strip()

    if "slug" in fields:
        slug = fields["slug"]

        if (
            not isinstance(slug, str)
            or not slug.strip()
        ):
            raise ValueError(
                "Media folder slug is required."
            )

        slug = slug.strip().lower()

        duplicate = MediaFolder.query.filter(
            MediaFolder.slug == slug,
            MediaFolder.id != folder.id,
        ).first()

        if duplicate:
            raise ValueError(
                "A media folder with this slug already exists."
            )

        folder.slug = slug

    if "description" in fields:
        description = fields["description"]

        folder.description = (
            description.strip()
            if isinstance(description, str)
            and description.strip()
            else None
        )

    if "parent_id" in fields:
        parent_id = fields["parent_id"]

        if parent_id in (
            "",
            None,
            0,
        ):
            folder.parent_id = None

        else:
            parent_id = int(
                parent_id
            )

            if parent_id == folder.id:
                raise ValueError(
                    "A media folder cannot be its own parent."
                )

            parent = db.session.get(
                MediaFolder,
                parent_id,
            )

            if parent is None:
                raise ValueError(
                    "The selected parent media folder does not exist."
                )

            current = parent

            while current is not None:
                if current.id == folder.id:
                    raise ValueError(
                        "A folder cannot be placed inside one of its descendants."
                    )

                if not current.parent_id:
                    break

                current = db.session.get(
                    MediaFolder,
                    current.parent_id,
                )

            folder.parent_id = parent_id

    if "folder_type" in fields:
        folder_type = fields["folder_type"]

        normalized_type = (
            folder_type.strip().lower()
            if isinstance(folder_type, str)
            and folder_type.strip()
            else "general"
        )

        if normalized_type not in VALID_FOLDER_TYPES:
            raise ValueError(
                "Invalid media folder type."
            )

        folder.folder_type = normalized_type

    if "display_order" in fields:
        folder.display_order = (
            fields["display_order"]
            if fields["display_order"] is not None
            else 0
        )

    if "active" in fields:
        folder.active = bool(
            fields["active"]
        )

    folder.updated_at = datetime.utcnow()

    db.session.commit()

    return folder


# =============================================================================
# Media Folder Delete
# =============================================================================

def delete_media_folder(
    folder,
):
    """
    Delete a MediaFolder without deleting MediaAssets.
    """

    if folder is None:
        raise ValueError(
            "Media folder is required."
        )

    children = MediaFolder.query.filter(
        MediaFolder.parent_id
        == folder.id
    ).count()

    if children:
        raise ValueError(
            "This media folder contains child folders. "
            "Move or delete the child folders first."
        )

    db.session.delete(
        folder
    )

    db.session.commit()

    return True

# =============================================================================
# Media Folder Assignment
# =============================================================================
def assign_media_folders(
    media_asset,
    folder_ids,
    primary_folder_id=None,
    replace_existing=True,
):
    """
    Assign one or more MediaFolders to a MediaAsset.
    """

    if isinstance(
        media_asset,
        int,
    ):
        media_asset = db.session.get(
            MediaAsset,
            media_asset,
        )

    if media_asset is None:
        raise ValueError(
            "Media asset does not exist."
        )

    if folder_ids is None:
        folder_ids = []

    if not isinstance(
        folder_ids,
        (list, tuple, set),
    ):
        folder_ids = [
            folder_ids
        ]

    normalized_folder_ids = []

    for folder_id in folder_ids:
        if folder_id in (
            "",
            None,
            0,
        ):
            continue

        folder_id = int(
            folder_id
        )

        if folder_id not in normalized_folder_ids:
            normalized_folder_ids.append(
                folder_id
            )

    for folder_id in normalized_folder_ids:
        folder = db.session.get(
            MediaFolder,
            folder_id,
        )

        if folder is None:
            raise ValueError(
                f"Media folder {folder_id} does not exist."
            )

        if not folder.active:
            raise ValueError(
                f"Media folder '{folder.name}' is inactive."
            )

    if primary_folder_id not in (
        None,
        "",
        0,
    ):
        primary_folder_id = int(
            primary_folder_id
        )

        if (
            primary_folder_id
            not in normalized_folder_ids
        ):
            raise ValueError(
                "The primary folder must be one of the assigned folders."
            )

    else:
        primary_folder_id = (
            normalized_folder_ids[0]
            if normalized_folder_ids
            else None
        )

    if replace_existing:
        MediaAssetFolder.query.filter_by(
            media_asset_id=media_asset.id
        ).delete(
            synchronize_session=False
        )

    else:
        existing_ids = {
            item.folder_id
            for item in (
                MediaAssetFolder.query
                .filter_by(
                    media_asset_id=media_asset.id
                )
                .all()
            )
        }

        normalized_folder_ids = [
            folder_id
            for folder_id in normalized_folder_ids
            if folder_id not in existing_ids
        ]

    assignments = []

    for folder_id in normalized_folder_ids:
        assignment = MediaAssetFolder(
            media_asset_id=media_asset.id,
            folder_id=folder_id,
            is_primary=(
                folder_id
                == primary_folder_id
            ),
            created_at=datetime.utcnow(),
        )

        db.session.add(
            assignment
        )

        assignments.append(
            assignment
        )

    if (
        not replace_existing
        and primary_folder_id is not None
    ):
        MediaAssetFolder.query.filter_by(
            media_asset_id=media_asset.id
        ).update(
            {
                MediaAssetFolder.is_primary: False,
            },
            synchronize_session=False,
        )

        MediaAssetFolder.query.filter_by(
            media_asset_id=media_asset.id,
            folder_id=primary_folder_id,
        ).update(
            {
                MediaAssetFolder.is_primary: True,
            },
            synchronize_session=False,
        )

    db.session.commit()

    return (
        MediaAssetFolder.query
        .filter_by(
            media_asset_id=media_asset.id
        )
        .all()
    )


def get_media_asset_folders(
    media_asset,
):
    """
    Retrieve all folders assigned to a MediaAsset.
    """

    if isinstance(
        media_asset,
        int,
    ):
        media_asset = db.session.get(
            MediaAsset,
            media_asset,
        )

    if media_asset is None:
        return []

    return (
        MediaAssetFolder.query
        .filter_by(
            media_asset_id=media_asset.id
        )
        .join(
            MediaFolder,
            MediaFolder.id
            == MediaAssetFolder.folder_id,
        )
        .order_by(
            MediaAssetFolder.is_primary.desc(),
            MediaFolder.name.asc(),
        )
        .all()
    )


def get_primary_media_folder(
    media_asset,
):
    """
    Retrieve the primary MediaFolder.
    """

    if isinstance(
        media_asset,
        int,
    ):
        media_asset = db.session.get(
            MediaAsset,
            media_asset,
        )

    if media_asset is None:
        return None

    assignment = (
        MediaAssetFolder.query
        .filter_by(
            media_asset_id=media_asset.id,
            is_primary=True,
        )
        .first()
    )

    if assignment is None:
        return None

    return assignment.folder


def remove_media_from_folder(
    media_asset,
    folder_id,
):
    """
    Remove an asset from one folder.
    """

    if isinstance(
        media_asset,
        int,
    ):
        media_asset = db.session.get(
            MediaAsset,
            media_asset,
        )

    if media_asset is None:
        raise ValueError(
            "Media asset does not exist."
        )

    assignment = (
        MediaAssetFolder.query
        .filter_by(
            media_asset_id=media_asset.id,
            folder_id=folder_id,
        )
        .first()
    )

    if assignment is None:
        return False

    db.session.delete(
        assignment
    )

    db.session.commit()

    return True


def get_media_assets_by_folder(
    folder_id,
    active_only=True,
    media_type=None,
):
    """
    Retrieve MediaAssets assigned to a folder.
    """

    query = (
        MediaAsset.query
        .join(
            MediaAssetFolder,
            MediaAssetFolder.media_asset_id
            == MediaAsset.id,
        )
        .filter(
            MediaAssetFolder.folder_id
            == folder_id
        )
    )

    if active_only:
        query = query.filter(
            MediaAsset.active.is_(True)
        )

    if media_type:
        query = query.filter(
            MediaAsset.media_type
            == normalize_media_type(media_type)
        )

    return (
        query
        .order_by(
            MediaAsset.created_at.desc(),
            MediaAsset.id.desc(),
        )
        .distinct()
        .all()
    )


# =============================================================================
# Experience Media
# =============================================================================
def attach_media_to_experience(
    experience,
    media_asset,
    usage="gallery",
    display_order=0,
    featured=False,
    active=True,
    title=None,
    caption=None,
    photographer=None,
):
    if isinstance(
        experience,
        int,
    ):
        experience = db.session.get(
            Experience,
            experience,
        )

    if isinstance(
        media_asset,
        int,
    ):
        media_asset = db.session.get(
            MediaAsset,
            media_asset,
        )

    if experience is None:
        raise ValueError(
            "Experience does not exist."
        )

    if media_asset is None:
        raise ValueError(
            "Media asset does not exist."
        )

    if not media_asset.active:
        raise ValueError(
            "Inactive media assets cannot be attached to experiences."
        )

    existing = (
        ExperienceMedia.query
        .filter_by(
            experience_id=experience.id,
            media_asset_id=media_asset.id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "This media asset is already attached to the experience."
        )

    usage = (
        usage or "gallery"
    ).strip().lower()

    experience_media = ExperienceMedia(
        experience_id=experience.id,
        media_asset_id=media_asset.id,
        usage=usage,
        display_order=display_order,
        featured=featured,
        active=active,
        title=title,
        caption=caption,
        photographer=photographer,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(
        experience_media
    )

    db.session.commit()

    return experience_media


def get_experience_media(
    experience,
    usage=None,
    active=True,
):
    if isinstance(
        experience,
        int,
    ):
        experience = db.session.get(
            Experience,
            experience,
        )

    if experience is None:
        return []

    query = ExperienceMedia.query.filter(
        ExperienceMedia.experience_id
        == experience.id
    )

    if active is not None:
        query = query.filter(
            ExperienceMedia.active
            == active
        )

    if usage:
        query = query.filter(
            ExperienceMedia.usage
            == usage
        )

    return (
        query
        .order_by(
            ExperienceMedia.display_order.asc(),
            ExperienceMedia.created_at.asc(),
        )
        .all()
    )


def get_experience_gallery(
    experience,
):
    return get_experience_media(
        experience,
        usage="gallery",
        active=True,
    )


def get_experience_hero_media(
    experience,
):
    media = get_experience_media(
        experience,
        usage="hero",
        active=True,
    )

    return (
        media[0]
        if media
        else None
    )


def get_experience_cover_media(
    experience,
):
    media = get_experience_media(
        experience,
        usage="cover",
        active=True,
    )

    return (
        media[0]
        if media
        else None
    )


def count_experience_media(
    experience,
    active=True,
):
    if isinstance(
        experience,
        int,
    ):
        experience = db.session.get(
            Experience,
            experience,
        )

    if experience is None:
        return 0

    query = ExperienceMedia.query.filter(
        ExperienceMedia.experience_id
        == experience.id
    )

    if active is not None:
        query = query.filter(
            ExperienceMedia.active
            == active
        )

    return query.count()

def remove_media_from_experience(
    experience_media,
):
    db.session.delete(
        experience_media
    )

    db.session.commit()
    return True

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Constants
    "VALID_MEDIA_USAGES",
    "VALID_FOLDER_TYPES",
    "ALLOWED_MEDIA_TYPES",
    "ALLOWED_IMAGE_EXTENSIONS",
    "ALLOWED_VIDEO_EXTENSIONS",
    "ALLOWED_DOCUMENT_EXTENSIONS",
    "ALLOWED_AUDIO_EXTENSIONS",
    "ALLOWED_ICON_EXTENSIONS",
    "ALLOWED_MAP_EXTENSIONS",
    "ALLOWED_EXTENSIONS",

    # Upload / validation
    "can_manage_media",
    "normalize_media_type",
    "normalize_media_usage",
    "normalize_extension",
    "validate_media_extension",
    "validate_media_asset",
    "upload_media_asset",
    "create_media_asset",

    # Asset retrieval
    "get_media_asset",
    "get_active_media_asset",
    "get_media_assets",
    "get_active_media_assets",
    "get_featured_media_assets",
    "search_media_assets",

    # Asset management
    "update_media_asset",
    "activate_media_asset",
    "deactivate_media_asset",
    "set_media_featured",
    "set_media_downloadable",
    "delete_media_asset",

    # Folders
    "get_media_folder",
    "get_media_folders",
    "get_all_media_folders",
    "get_media_folder_by_slug",
    "get_media_folder_choices",
    "get_cms_media_assets",
    "create_media_folder",
    "update_media_folder",
    "delete_media_folder",
    "assign_media_folders",
    "get_media_asset_folders",
    "get_primary_media_folder",
    "remove_media_from_folder",
    "get_media_assets_by_folder",

    # Experience media
    "attach_media_to_experience",
    "get_experience_media",
    "get_experience_gallery",
    "get_experience_hero_media",
    "get_experience_cover_media",
    "count_experience_media",
    "remove_media_from_experience",
]