from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_stay import AdminStayFilterForm, AdminStayForm
from app.services.admin.admin_stay_service import (
    activate_stay,
    create_stay,
    deactivate_stay,
    delete_stay,
    get_stay,
    get_stays,
    set_stay_featured,
    update_stay,)
from app.services.media_service import get_all_media_folders

stay_bp = Blueprint(
    "admin_stay",
    __name__,
    url_prefix="/admin/stays",)

# ---------------------------------------------------------------------------
# Media Folder Helpers
# ---------------------------------------------------------------------------

def _get_stay_media_folder_choices(root_name):
    """
    Build media-folder choices from a specific Stay media-library tree.

    The root folder itself is not selectable. All child folders and their
    descendants are included, preserving the folder hierarchy visually.
    """

    folders = get_all_media_folders(active=True)

    root_folder = next(
        (
            folder
            for folder in folders
            if folder.name.strip().lower() == root_name.strip().lower()
            and folder.parent_id is None
        ),
        None,
    )

    if root_folder is None:
        return []

    children_by_parent = {}

    for folder in folders:
        children_by_parent.setdefault(folder.parent_id, []).append(folder)

    for children in children_by_parent.values():
        children.sort(
            key=lambda folder: (
                folder.display_order,
                folder.name.lower(),
            )
        )

    choices = []

    def append_children(parent_id, depth):
        for folder in children_by_parent.get(parent_id, []):
            choices.append(
                (
                    folder.id,
                    f'{"— " * depth}{folder.name}',
                )
            )
            append_children(folder.id, depth + 1)

    append_children(root_folder.id, 0)

    return choices


def _populate_stay_media_folder_choices(form):
    """
    Restrict Stay media-folder selection to the Stays media-library tree.
    """

    form.media_folder_id.choices = _get_stay_media_folder_choices("Stays")


# ---------------------------------------------------------------------------
# Stay Management
# ---------------------------------------------------------------------------

@stay_bp.route("/")
@admin_required
def index():
    form = AdminStayFilterForm()

    stays = get_stays()

    return render_template(
        "admin/stays/index.html",
        stays=stays,
        form=form,
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@stay_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    form = AdminStayForm()

    _populate_stay_media_folder_choices(form)

    if form.validate_on_submit():
        try:
            stay = create_stay(
                acting_admin=current_user,
                stay_code=form.stay_code.data,
                property_name=form.property_name.data,
                slug=form.slug.data,
                accommodation_type=form.accommodation_type.data,
                short_description=form.short_description.data,
                description=form.description.data,
                location=form.location.data,
                address=form.address.data,
                destination_id=form.destination_id.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                maximum_guests=form.maximum_guests.data,
                maximum_adults=form.maximum_adults.data,
                maximum_children=form.maximum_children.data,
                total_rooms=form.total_rooms.data,
                minimum_nights=form.minimum_nights.data,
                check_in_time=form.check_in_time.data,
                check_out_time=form.check_out_time.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                website_url=form.website_url.data,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                featured=form.featured.data,
                active=form.active.data,
                display_order=form.display_order.data,
                media_folder_id=form.media_folder_id.data,
            )

            flash(
                f'Stay "{stay.property_name}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay.detail",
                    stay_id=stay.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/create.html",
        form=form,
    )


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

@stay_bp.route("/<int:stay_id>")
@admin_required
def detail(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    return render_template(
        "admin/stays/detail.html",
        stay=stay,
    )


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

@stay_bp.route("/<int:stay_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayForm(obj=stay)

    _populate_stay_media_folder_choices(form)

    if form.validate_on_submit():
        try:
            update_stay(
                acting_admin=current_user,
                stay=stay,
                stay_code=form.stay_code.data,
                property_name=form.property_name.data,
                slug=form.slug.data,
                accommodation_type=form.accommodation_type.data,
                short_description=form.short_description.data,
                description=form.description.data,
                location=form.location.data,
                address=form.address.data,
                destination_id=form.destination_id.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                maximum_guests=form.maximum_guests.data,
                maximum_adults=form.maximum_adults.data,
                maximum_children=form.maximum_children.data,
                total_rooms=form.total_rooms.data,
                minimum_nights=form.minimum_nights.data,
                check_in_time=form.check_in_time.data,
                check_out_time=form.check_out_time.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                website_url=form.website_url.data,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                featured=form.featured.data,
                active=form.active.data,
                display_order=form.display_order.data,
                media_folder_id=form.media_folder_id.data,
            )

            flash(
                f'Stay "{stay.property_name}" was updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay.detail",
                    stay_id=stay.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/edit.html",
        form=form,
        stay=stay,
    )


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

@stay_bp.route("/filter", methods=["GET", "POST"])
@admin_required
def filter():
    form = AdminStayFilterForm()

    if form.validate_on_submit():
        stays = get_stays(
            search=form.search.data,
            destination_id=(
                form.destination_id.data
                if form.destination_id.data
                else None
            ),
            accommodation_type=(
                form.accommodation_type.data
                if form.accommodation_type.data
                else None
            ),
            status=(
                form.status.data
                if form.status.data
                else None
            ),
            featured=(
                form.featured.data
                if form.featured.data is not None
                else None
            ),
        )
    else:
        stays = get_stays()

    return render_template(
        "admin/stays/index.html",
        stays=stays,
        form=form,
    )


# ---------------------------------------------------------------------------
# Activation
# ---------------------------------------------------------------------------

@stay_bp.route(
    "/<int:stay_id>/activate",
    methods=["POST"],
)
@admin_required
def activate(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        activate_stay(
            acting_admin=current_user,
            stay=stay,
        )

        flash(
            f'Stay "{stay.property_name}" was activated.',
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay.detail",
            stay_id=stay.id,
        )
    )


# ---------------------------------------------------------------------------
# Deactivation
# ---------------------------------------------------------------------------

@stay_bp.route(
    "/<int:stay_id>/deactivate",
    methods=["POST"],
)
@admin_required
def deactivate(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        deactivate_stay(
            acting_admin=current_user,
            stay=stay,
        )

        flash(
            f'Stay "{stay.property_name}" was deactivated.',
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay.detail",
            stay_id=stay.id,
        )
    )


# ---------------------------------------------------------------------------
# Featured
# ---------------------------------------------------------------------------

@stay_bp.route(
    "/<int:stay_id>/feature",
    methods=["POST"],
)
@admin_required
def feature(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_featured(
            acting_admin=current_user,
            stay=stay,
            featured=True,
        )

        flash(
            f'"{stay.property_name}" is now featured.',
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay.detail",
            stay_id=stay.id,
        )
    )


@stay_bp.route(
    "/<int:stay_id>/unfeature",
    methods=["POST"],
)
@admin_required
def unfeature(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_featured(
            acting_admin=current_user,
            stay=stay,
            featured=False,
        )

        flash(
            f'"{stay.property_name}" is no longer featured.',
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay.detail",
            stay_id=stay.id,
        )
    )


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@stay_bp.route(
    "/<int:stay_id>/delete",
    methods=["POST"],
)
@admin_required
def delete(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    property_name = stay.property_name

    try:
        delete_stay(
            acting_admin=current_user,
            stay=stay,
        )

        flash(
            f'Stay "{property_name}" was deleted.',
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for("admin_stay.index")
    )