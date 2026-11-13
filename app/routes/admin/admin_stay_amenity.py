from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from app.decorators.admin import admin_required
from app.forms.admin_stay_amenity import AdminStayAmenityForm
from app.services.admin.admin_stay_amenity_service import (
    activate_stay_amenity,
    create_stay_amenity,
    deactivate_stay_amenity,
    delete_stay_amenity,
    get_stay_amenity,
    get_stay_amenities,
    set_stay_amenity_featured,
    update_stay_amenity,)
from app.services.admin.admin_stay_service import get_stay

stay_amenity_bp = Blueprint(
    "admin_stay_amenity",
    __name__,
    url_prefix="/admin/stays")

# ============================================================
# STAY AMENITIES
# ============================================================
@stay_amenity_bp.route("/<int:stay_id>/amenities/")
@admin_required
def index(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    amenities = get_stay_amenities(
        stay_id=stay.id,)

    return render_template(
        "admin/stays/amenities/index.html",
        stay=stay,
        amenities=amenities,)

@stay_amenity_bp.route("/<int:stay_id>/amenities/create",methods=["GET", "POST"],)
@admin_required
def create(stay_id):
    stay = get_stay(stay_id)
    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))
    form = AdminStayAmenityForm()
    if form.validate_on_submit():
        try:
            amenity = create_stay_amenity(
                acting_admin=current_user,
                stay_id=stay.id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data,
                active=form.active.data,
                featured=form.featured.data,
                display_order=form.display_order.data,)

            flash(
                f'Amenity "{amenity.name}" was created successfully.',
                "success",)

            return redirect(
                url_for(
                    "admin_stay_amenity.index",
                    stay_id=stay.id,))

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/amenities/create.html",
        form=form,
        stay=stay,)

@stay_amenity_bp.route("/amenities/<int:amenity_id>")
@admin_required
def detail(amenity_id):
    amenity = get_stay_amenity(amenity_id)
    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    return render_template(
        "admin/stays/amenities/detail.html",
        amenity=amenity,
        stay=amenity.stay,)

@stay_amenity_bp.route("/amenities/<int:amenity_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(amenity_id):
    amenity = get_stay_amenity(amenity_id)

    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayAmenityForm(obj=amenity)

    if form.validate_on_submit():
        try:
            update_stay_amenity(
                acting_admin=current_user,
                amenity=amenity,
                stay_id=amenity.stay_id,
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                icon=form.icon.data,
                active=form.active.data,
                featured=form.featured.data,
                display_order=form.display_order.data,
            )

            flash(
                f'Amenity "{amenity.name}" was updated successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_amenity.detail",
                    amenity_id=amenity.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/amenities/edit.html",
        form=form,
        amenity=amenity,
        stay=amenity.stay,)

# ============================================================
# STATUS
# ============================================================
@stay_amenity_bp.route("/amenities/<int:amenity_id>/activate",methods=["POST"],)
@admin_required
def activate(amenity_id):
    amenity = get_stay_amenity(amenity_id)

    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        activate_stay_amenity(
            acting_admin=current_user,
            amenity=amenity,)

        flash("Amenity was activated.","success",)

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_amenity.detail",
            amenity_id=amenity.id,))

@stay_amenity_bp.route("/amenities/<int:amenity_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate(amenity_id):
    amenity = get_stay_amenity(amenity_id)
    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        deactivate_stay_amenity(
            acting_admin=current_user,
            amenity=amenity,)

        flash("Amenity was deactivated.","success",)

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_amenity.detail",
            amenity_id=amenity.id,))

# ============================================================
# FEATURED
# ============================================================
@stay_amenity_bp.route(
    "/amenities/<int:amenity_id>/feature",
    methods=["POST"],)
@admin_required
def feature(amenity_id):
    amenity = get_stay_amenity(amenity_id)

    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_amenity_featured(
            acting_admin=current_user,
            amenity=amenity,
            featured=True,)

        flash("Amenity was featured.","success",)
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_amenity.detail",
            amenity_id=amenity.id,))

@stay_amenity_bp.route("/amenities/<int:amenity_id>/unfeature",methods=["POST"])
@admin_required
def unfeature(amenity_id):
    amenity = get_stay_amenity(amenity_id)
    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_amenity_featured(
            acting_admin=current_user,
            amenity=amenity,
            featured=False,)

        flash("Amenity was unfeatured.","success",)

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_amenity.detail",
            amenity_id=amenity.id,))

# ============================================================
# DELETE
# ============================================================
@stay_amenity_bp.route("/amenities/<int:amenity_id>/delete",methods=["POST"],)
@admin_required
def delete(amenity_id):
    amenity = get_stay_amenity(amenity_id)
    if amenity is None:
        flash("Amenity not found.", "danger")
        return redirect(url_for("admin_stay.index"))
    stay_id = amenity.stay_id

    try:
        delete_stay_amenity(
            acting_admin=current_user,
            amenity=amenity,)

        flash("Amenity was deleted.","success",)

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_amenity.index",
            stay_id=stay_id,))