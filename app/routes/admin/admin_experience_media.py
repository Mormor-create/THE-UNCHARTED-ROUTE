"""
The Uncharted Route
Administrative Experience Media Routes
"""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    url_for,)
from flask_wtf import FlaskForm
from app.decorators.admin import admin_required
from app.forms.admin_experience_media import AdminExperienceMediaForm
from app.models import MediaAsset
from app.services.experiences.experience_media_service import (
    create_experience_media,
    delete_experience_media,
    get_experience_for_media,
    get_experience_media,
    get_experience_media_folder,
    get_experience_media_items,
    get_selectable_media_assets,
    set_experience_media_active,
    update_experience_media,)

experience_media_bp = Blueprint(
    "admin_experience_media",
    __name__,
    url_prefix="/admin/experiences/<int:experience_id>/media",)

# ---------------------------------------------------------------------
# Form choices
# ---------------------------------------------------------------------
def _populate_asset_choices(
    form,
    experience,
    current_asset=None,
):
    """
    Populate choices from this Experience's folder and descendants.

    When editing, preserve the current asset in the selector even if it
    is inactive or no longer inside the Experience folder.
    """
    media_folder = get_experience_media_folder(experience)

    assets = get_selectable_media_assets(experience.id)
    selectable_asset_count = len(assets)

    if (
        current_asset is not None
        and all(asset.id != current_asset.id for asset in assets)
    ):
        assets.append(current_asset)

    assets.sort(
        key=lambda asset: (
            (asset.title or asset.original_filename or "").lower(),
            asset.id,
        )
    )

    form.media_asset_id.choices = [
        (
            asset.id,
            (
                f"{asset.title or asset.original_filename}"
                f" — {asset.media_type}"
                f"{' (Inactive)' if not asset.active else ''}"
                f" (#{asset.id})"
            ),
        )
        for asset in assets
    ]

    return {
        "media_folder": media_folder,
        "media_folder_available": media_folder is not None,
        "selectable_asset_count": selectable_asset_count,
    }


# ---------------------------------------------------------------------
# Record lookup
# ---------------------------------------------------------------------

def _get_experience_or_404(experience_id):
    experience = get_experience_for_media(experience_id)

    if experience is None:
        abort(404)

    return experience


def _get_assignment_or_404(experience_id, media_id):
    assignment = get_experience_media(
        experience_id=experience_id,
        media_id=media_id,
    )

    if assignment is None:
        abort(404)

    return assignment


# ---------------------------------------------------------------------
# List assignments
# ---------------------------------------------------------------------

@experience_media_bp.route("/")
@admin_required
def index(experience_id):
    experience = _get_experience_or_404(experience_id)

    assignments = get_experience_media_items(experience_id)

    return render_template(
        "admin/experiences/media/index.html",
        experience=experience,
        assignments=assignments,
    )


# ---------------------------------------------------------------------
# Create assignment
# ---------------------------------------------------------------------

@experience_media_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create(experience_id):
    experience = _get_experience_or_404(experience_id)

    form = AdminExperienceMediaForm()

    folder_context = _populate_asset_choices(
        form=form,
        experience=experience,
    )

    if not folder_context["media_folder_available"]:
        flash(
            "This Experience does not yet have a folder inside "
            "Experience Media Gallery. No Media Library assets can "
            "be selected until its folder is created or associated.",
            "warning",
        )

    elif not folder_context["selectable_asset_count"]:
        flash(
            "There are no active assets in this Experience's media "
            "folder or its subfolders.",
            "warning",
        )

    if form.validate_on_submit():
        try:
            assignment = create_experience_media(
                experience_id=experience.id,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                title=form.title.data,
                caption=form.caption.data,
                photographer=form.photographer.data,
                featured=form.featured.data,
                active=form.active.data,
            )

        except ValueError as exc:
            flash(str(exc), "danger")

        else:
            flash(
                "Media assigned to the experience successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_media.detail",
                    experience_id=experience.id,
                    media_id=assignment.id,
                )
            )

    return render_template(
        "admin/experiences/media/create.html",
        experience=experience,
        form=form,
        **folder_context,
    )


# ---------------------------------------------------------------------
# Assignment detail
# ---------------------------------------------------------------------

@experience_media_bp.route("/<int:media_id>")
@admin_required
def detail(experience_id, media_id):
    experience = _get_experience_or_404(experience_id)
    assignment = _get_assignment_or_404(experience_id, media_id)

    return render_template(
        "admin/experiences/media/detail.html",
        experience=experience,
        assignment=assignment,
        status_form=FlaskForm(),
    )


# ---------------------------------------------------------------------
# Edit assignment
# ---------------------------------------------------------------------

@experience_media_bp.route(
    "/<int:media_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(experience_id, media_id):
    experience = _get_experience_or_404(experience_id)
    assignment = _get_assignment_or_404(experience_id, media_id)

    form = AdminExperienceMediaForm(obj=assignment)

    # Preserve the current asset in the selector, even if it has
    # become inactive or is no longer inside this Experience's folder.
    current_asset = MediaAsset.query.get(
        assignment.media_asset_id
    )

    folder_context = _populate_asset_choices(
        form=form,
        experience=experience,
        current_asset=current_asset,
    )

    if form.validate_on_submit():
        try:
            update_experience_media(
                assignment=assignment,
                media_asset_id=form.media_asset_id.data,
                usage=form.usage.data,
                display_order=form.display_order.data,
                title=form.title.data,
                caption=form.caption.data,
                photographer=form.photographer.data,
                featured=form.featured.data,
                active=form.active.data,
            )

        except ValueError as exc:
            flash(str(exc), "danger")

        else:
            flash(
                "Experience media assignment updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_media.detail",
                    experience_id=experience.id,
                    media_id=assignment.id,
                )
            )

    return render_template(
        "admin/experiences/media/edit.html",
        experience=experience,
        assignment=assignment,
        form=form,
        **folder_context,
    )


# ---------------------------------------------------------------------
# Activate assignment
# ---------------------------------------------------------------------

@experience_media_bp.route(
    "/<int:media_id>/activate",
    methods=["POST"],
)
@admin_required
def activate(experience_id, media_id):
    _get_experience_or_404(experience_id)
    assignment = _get_assignment_or_404(experience_id, media_id)

    form = FlaskForm()

    if form.validate_on_submit():
        try:
            set_experience_media_active(assignment, True)

        except ValueError as exc:
            flash(str(exc), "danger")

        else:
            flash("Media assignment activated.", "success")

    return redirect(
        url_for(
            "admin_experience_media.detail",
            experience_id=experience_id,
            media_id=media_id,
        )
    )


# ---------------------------------------------------------------------
# Deactivate assignment
# ---------------------------------------------------------------------

@experience_media_bp.route(
    "/<int:media_id>/deactivate",
    methods=["POST"],
)
@admin_required
def deactivate(experience_id, media_id):
    _get_experience_or_404(experience_id)
    assignment = _get_assignment_or_404(experience_id, media_id)

    form = FlaskForm()

    if form.validate_on_submit():
        try:
            set_experience_media_active(assignment, False)

        except ValueError as exc:
            flash(str(exc), "danger")

        else:
            flash("Media assignment deactivated.", "success")

    return redirect(
        url_for(
            "admin_experience_media.detail",
            experience_id=experience_id,
            media_id=media_id,
        )
    )


# ---------------------------------------------------------------------
# Delete assignment only — never delete the central asset
# ---------------------------------------------------------------------

@experience_media_bp.route(
    "/<int:media_id>/delete",
    methods=["POST"],
)
@admin_required
def delete(experience_id, media_id):
    _get_experience_or_404(experience_id)
    assignment = _get_assignment_or_404(experience_id, media_id)

    form = FlaskForm()

    if form.validate_on_submit():
        try:
            delete_experience_media(assignment)

        except ValueError as exc:
            flash(str(exc), "danger")

        else:
            flash(
                "Media assignment removed. The central media asset "
                "has not been deleted.",
                "success",
            )

    return redirect(
        url_for(
            "admin_experience_media.index",
            experience_id=experience_id,
        )
    )