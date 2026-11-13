"""
The Uncharted Route — Administrative Media Library Blueprint

Protected administrative routes for the centralized Digital Asset
Management (DAM) system.

Responsibilities
----------------
• View media library
• Search and filter media
• Upload media assets
• View media asset details
• Edit media metadata
• Activate / deactivate assets
• Feature / unfeature assets
• Control download availability
• Delete media assets
• Serve stored media files to the browser

Architecture
------------
Route → Form → Service → Model

Routes handle HTTP concerns only.

Business logic is delegated to:
    app.services.admin.admin_media_service

Authorization is enforced through:
    app.decorators.admin.admin_required

The MediaAsset model remains the central source of truth for
application media.
"""

import mimetypes
import os
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,)
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_media import (
    AdminMediaEditForm,
    AdminMediaFilterForm,
    AdminMediaFolderForm,
    AdminMediaStatusForm,
    AdminMediaUploadForm,
)
from app.models import MediaFolder, MediaAsset, MediaAssetFolder
from app.services.media_service import (
    assign_media_folders,
    create_media_folder,
    delete_media_folder,
    get_media_folder,
    get_media_folder_choices,
    update_media_folder,
    activate_media_asset,
    deactivate_media_asset,
    delete_media_asset,
    get_media_asset,
    get_media_assets,
    get_media_folders,
    set_media_downloadable,
    set_media_featured,
    update_media_asset,
    upload_media_asset,
)

# =============================================================================
# Form Choice Helpers
# =============================================================================
def _populate_media_folder_choices(form):
    """
    Populate hierarchical DAM folder choices.
    """

    choices = get_media_folder_choices(
        active_only=True,
        include_empty=True,
    )

    if hasattr(form, "folder_ids"):
        form.folder_ids.choices = choices

    if hasattr(form, "primary_folder_id"):
        form.primary_folder_id.choices = choices

    if hasattr(form, "folder_id"):
        form.folder_id.choices = choices

    return form

# =============================================================================
# Blueprint
# =============================================================================
media_bp = Blueprint(
    "admin_media",
    __name__,
    url_prefix="/admin/media",
)


# =============================================================================
# Browser Media Serving
# =============================================================================
@media_bp.route("/file/<path:filename>",)
def serve_media(filename):
    """
    Serve a DAM media file to the browser.

    This route intentionally does not use @admin_required because
    uploaded media is also consumed by the public website.

    The physical file remains in UPLOAD_FOLDER and is never exposed
    directly as a filesystem path.

    Examples
    --------
    /admin/media/file/abc123.jpg
    /admin/media/file/abc123.mp4
    """

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER"
    )

    if not upload_folder:
        return (
            "Media upload folder is not configured.",
            500,
        )

    upload_folder = os.path.abspath(
        upload_folder
    )

    # Only the stored filename should be used.
    # Never allow an arbitrary filesystem path to be passed through.
    safe_filename = os.path.basename(
        filename
    )

    if not safe_filename:
        return (
            "Media file not found.",
            404,
        )

    file_path = os.path.join(
        upload_folder,
        safe_filename,
    )

    if not os.path.isfile(file_path):
        return (
            "Media file not found.",
            404,
        )

    mimetype = mimetypes.guess_type(
        safe_filename
    )[0]

    return send_from_directory(
        upload_folder,
        safe_filename,
        mimetype=mimetype,
        conditional=True,
    )

# =============================================================================
# Media Library
# =============================================================================
@media_bp.route("/")
def index():

    form = AdminMediaFilterForm(
        request.args,
        meta={
            "csrf": False
        },
    )

    _populate_media_folder_choices(form)

    assets = get_media_assets(
        search=form.search.data,
        media_type=form.media_type.data,
        usage=form.usage.data,
        folder_id=form.folder_id.data,
        active_only=form.active_only.data,
        featured_only=form.featured_only.data,
    )

    all_folders = get_media_folders(
        active_only=None
    )

    root_folders = [
        folder
        for folder in all_folders
        if folder.parent_id is None
    ]

    recent_assets = (
        get_media_assets(
            active_only=True
        )
    )[:8]

    return render_template(
        "admin/media/index.html",
        form=form,
        assets=assets,
        folders=root_folders,
        recent_assets=recent_assets,
    )

# =============================================================================
# Upload Media
# =============================================================================
@media_bp.route(
    "/upload",
    methods=["GET", "POST"],
)
def upload():

    form = AdminMediaUploadForm()

    _populate_media_folder_choices(
        form
    )

    if form.validate_on_submit():

        try:

            selected_media_type = (
                form.media_type.data.strip()
                if form.media_type.data
                else None
            )

            asset = upload_media_asset(
                acting_admin=current_user,
                file=form.file.data,
                title=form.title.data,
                alt_text=form.alt_text.data,
                caption=form.caption.data,
                description=form.description.data,
                credit=form.credit.data,
                media_type=selected_media_type,
                usage=form.usage.data,
                folder_ids=form.folder_ids.data,
                primary_folder_id=form.primary_folder_id.data,
                tags=form.tags.data,
                seo_title=form.seo_title.data,
                seo_description=form.seo_description.data,
                downloadable=form.downloadable.data,
                featured=form.featured.data,
                active=form.active.data,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_media.index"
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/media/upload.html",
                form=form,
            )

        except OSError:

            flash(
                "The file could not be stored. Please try again.",
                "danger",
            )

            return render_template(
                "admin/media/upload.html",
                form=form,
            )

        flash(
            "Media asset uploaded successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_media.detail",
                asset_id=asset.id,
            )
        )

    return render_template(
        "admin/media/upload.html",
        form=form,
    )

# =============================================================================
# Media Asset Detail
# =============================================================================
@media_bp.route("/<int:asset_id>",)
#@admin_required
def detail(asset_id):
    """
    Display complete details for a media asset.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    return render_template(
        "admin/media/detail.html",
        asset=asset,
    )

# =============================================================================
# Edit Media Asset
# =============================================================================
@media_bp.route("/<int:asset_id>/edit", methods=["GET", "POST"])
def edit(asset_id):
    """
    Edit media asset metadata and DAM folder assignments.

    The media service handles metadata updates and folder assignments.
    The uploaded file URL is managed by the DAM and is not editable here.
    """
    asset = get_media_asset(asset_id)

    if asset is None:
        flash("Media asset not found.", "danger")
        return redirect(url_for("admin_media.index"))

    form = AdminMediaEditForm(obj=asset)

    # Populate hierarchical DAM folder choices.
    _populate_media_folder_choices(form)

    # -------------------------------------------------------------------------
    # GET — populate current folder assignments
    # -------------------------------------------------------------------------
    if request.method == "GET":
        form.folder_ids.data = [
            assignment.folder_id
            for assignment in asset.folder_assignments.all()
        ]

        primary_folder = asset.primary_folder
        form.primary_folder_id.data = (
            primary_folder.id if primary_folder else 0
        )

    # -------------------------------------------------------------------------
    # POST — validate and update
    # -------------------------------------------------------------------------
    if form.validate_on_submit():
        try:
            selected_folder_ids = list(form.folder_ids.data or [])
            primary_folder_id = form.primary_folder_id.data

            # Normalize the primary folder selection.
            if primary_folder_id in (None, "", 0, "0"):
                primary_folder_id = None
            else:
                primary_folder_id = int(primary_folder_id)

            # Ensure the primary folder is included among assigned folders.
            if (
                primary_folder_id is not None
                and primary_folder_id not in selected_folder_ids
            ):
                selected_folder_ids.append(primary_folder_id)

            update_media_asset(
                acting_admin=current_user,
                asset=asset,
                title=form.title.data,
                alt_text=form.alt_text.data,
                caption=form.caption.data,
                description=form.description.data,
                credit=form.credit.data,
                media_type=form.media_type.data,
                usage=form.usage.data,
                seo_title=form.seo_title.data,
                seo_description=form.seo_description.data,
                tags=form.tags.data,
                active=form.active.data,
                featured=form.featured.data,
                downloadable=form.downloadable.data,
                folder_ids=selected_folder_ids,
                primary_folder_id=primary_folder_id,
            )

        except (PermissionError, ValueError) as exc:
            flash(str(exc), "danger")
            return render_template(
                "admin/media/edit.html",
                form=form,
                asset=asset,
            )

        flash("Media asset updated successfully.", "success")
        return redirect(
            url_for("admin_media.detail", asset_id=asset.id)
        )

    return render_template(
        "admin/media/edit.html",
        form=form,
        asset=asset,
    )

# =============================================================================
# Activate Media Asset
# =============================================================================
@media_bp.route(
    "/<int:asset_id>/activate",
    methods=["POST"],
)
#@admin_required
def activate(asset_id):
    """
    Activate a media asset.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            activate_media_asset(
                acting_admin=current_user,
                asset=asset,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset activated successfully.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Deactivate Media Asset
# =============================================================================

@media_bp.route(
    "/<int:asset_id>/deactivate",
    methods=["POST"],
)
#@admin_required
def deactivate(asset_id):
    """
    Deactivate a media asset without deleting it.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            deactivate_media_asset(
                acting_admin=current_user,
                asset=asset,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset has been deactivated.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Feature Media Asset
# =============================================================================
@media_bp.route(
    "/<int:asset_id>/feature",
    methods=["POST"],
)
#@admin_required
def feature(asset_id):
    """
    Mark a media asset as featured.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            set_media_featured(
                acting_admin=current_user,
                asset=asset,
                featured=True,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset has been featured.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Unfeature Media Asset
# =============================================================================

@media_bp.route(
    "/<int:asset_id>/unfeature",
    methods=["POST"],
)
#@admin_required
def unfeature(asset_id):
    """
    Remove the featured status from a media asset.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            set_media_featured(
                acting_admin=current_user,
                asset=asset,
                featured=False,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset has been unfeatured.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Enable Downloads
# =============================================================================
@media_bp.route("/<int:asset_id>/downloadable",methods=["POST"],)
#@admin_required
def downloadable(asset_id):
    """
    Mark a media asset as downloadable.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            set_media_downloadable(
                acting_admin=current_user,
                asset=asset,
                downloadable=True,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset is now downloadable.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Disable Downloads
# =============================================================================
@media_bp.route("/<int:asset_id>/non-downloadable",methods=["POST"],)
#@admin_required
def non_downloadable(asset_id):
    """
    Disable public download availability for a media asset.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            set_media_downloadable(
                acting_admin=current_user,
                asset=asset,
                downloadable=False,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

        else:

            flash(
                "Media asset is no longer downloadable.",
                "success",
            )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )


# =============================================================================
# Delete Media Asset
# =============================================================================
@media_bp.route("/<int:asset_id>/delete",methods=["POST"],)
#@admin_required
def delete(asset_id):
    """
    Delete a media asset.

    The service is responsible for deleting the MediaAsset record.
    Physical file deletion belongs to the storage layer.
    """

    asset = get_media_asset(
        asset_id,
    )

    if asset is None:

        flash(
            "Media asset not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    form = AdminMediaStatusForm()

    if form.validate_on_submit():

        try:

            delete_media_asset(
                acting_admin=current_user,
                asset=asset,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_media.detail",
                    asset_id=asset.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_media.detail",
                    asset_id=asset.id,
                )
            )

        flash(
            "Media asset deleted successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_media.index",
            )
        )

    return redirect(
        url_for(
            "admin_media.detail",
            asset_id=asset.id,
        )
    )

# =============================================================================
# Media Gallery
# =============================================================================
@media_bp.route("/gallery", methods=["GET"])
def gallery():
    """
    Visual/search browser for the TUR media library.

    Gallery is a browsing and discovery interface.
    Folder hierarchy remains the primary organizational system.
    """

    form = AdminMediaFilterForm(
        request.args,
        meta={
            "csrf": False
        },
    )

    _populate_media_folder_choices(form)

    assets = get_media_assets(
        search=form.search.data,
        media_type=form.media_type.data,
        usage=form.usage.data,
        folder_id=form.folder_id.data,
        active_only=form.active_only.data,
        featured_only=form.featured_only.data,
    )

    return render_template(
        "admin/media/gallery.html",
        form=form,
        assets=assets,
    )

@media_bp.route("/folders/", methods=["GET"])
def folders():

    all_folders = get_media_folders(
        active_only=None
    )

    folder_list = [
        folder for folder in all_folders
        if folder.parent_id is None
    ]

    return render_template(
        "admin/media/folders/index.html",
        folders=folder_list,
    )

@media_bp.route(
    "/folders/create",
    methods=["GET", "POST"],
)
def create_folder():

    form = AdminMediaFolderForm()

    form.parent_id.choices = (
        get_media_folder_choices(
            active_only=True,
            include_empty=True,
        )
    )

    if request.method == "GET":

        parent_id = request.args.get(
            "parent_id",
            type=int,
        )

        if parent_id:
            form.parent_id.data = parent_id

    if form.validate_on_submit():

        try:

            folder = create_media_folder(
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data,
                parent_id=form.parent_id.data,
                folder_type=form.folder_type.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/media/folders/create.html",
                form=form,
            )

        flash(
            "Media folder created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_media.folders"
            )
        )

    return render_template(
        "admin/media/folders/create.html",
        form=form,
    )

@media_bp.route("/folders/<int:folder_id>/edit",methods=["GET", "POST"],)
def edit_folder(folder_id):

    folder = get_media_folder(
        folder_id
    )

    if folder is None:
        flash(
            "Media folder not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.folders"))

    form = AdminMediaFolderForm(
        obj=folder
    )

    form.parent_id.choices = (
        get_media_folder_choices(
            active_only=True,
            include_empty=True,
        )
    )

    if request.method == "GET":

        form.parent_id.data = (
            folder.parent_id
            or 0
        )

    if form.validate_on_submit():

        try:

            update_media_folder(
                folder,
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data,
                parent_id=form.parent_id.data,
                folder_type=form.folder_type.data,
                display_order=form.display_order.data,
                active=form.active.data,
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/media/folders/edit.html",
                form=form,
                folder=folder,
            )

        flash(
            "Media folder updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_media.folders"
            )
        )

    return render_template(
        "admin/media/folders/edit.html",
        form=form,
        folder=folder,
    )

@media_bp.route(
    "/folders/<int:folder_id>/delete",
    methods=["POST"],
)
def delete_folder(folder_id):

    folder = get_media_folder(
        folder_id
    )

    if folder is None:

        flash(
            "Media folder not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.folders"
            )
        )

    form = AdminMediaStatusForm()

    if not form.validate_on_submit():

        flash(
            "Invalid delete request.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_media.folders"
            )
        )

    try:

        delete_media_folder(
            folder
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",)

        return redirect(
            url_for(
                "admin_media.folders"))

    flash(
        "Media folder deleted successfully.",
        "success",)

    return redirect(
        url_for(
            "admin_media.folders"))


# =============================================================================
# Media Folder Detail
# =============================================================================
@media_bp.route("/folders/<int:folder_id>/",methods=["GET"],)
def folder_detail(folder_id):

    folder = get_media_folder(folder_id)

    if folder is None:
        flash(
            "Media folder not found.",
            "danger",
        )

        return redirect(
            url_for("admin_media.folders")
        )

    child_folders = (
        folder.children
        .order_by(
            MediaFolder.display_order.asc(),
            MediaFolder.name.asc(),
        )
        .all()
    )

    assets = (
        MediaAsset.query
        .join(
            MediaAssetFolder,
            MediaAssetFolder.media_asset_id == MediaAsset.id,
        )
        .filter(
            MediaAssetFolder.folder_id == folder.id,
        )
        .order_by(
            MediaAsset.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin/media/folders/detail.html",
        folder=folder,
        child_folders=child_folders,
        assets=assets,
    )

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "media_bp",
]