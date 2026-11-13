
"""
===============================================================================
The Uncharted Route
Shared Add-on Catalogue Admin Routes
===============================================================================
"""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.decorators.admin import admin_required
from extensions import db
from app.forms.bookings.addon_catalogue_forms import AddonCatalogueForm
from app.models.addon_catalogue import AddonCatalogue
from app.services.bookings.addon_catalogue_service import (
    AddonCatalogueService,)

addon_catalogue_bp = Blueprint(
    "admin_addon_catalogue",
    __name__,
    url_prefix="/admin/addon-catalogue",)

def _load_form(form, addon=None):
    if addon is not None and request.method == "GET":
        form.process(obj=addon)
        form.applicable_services.data = addon.applicable_services or []
    return AddonCatalogueService.populate_form_choices(form)


def _commit_changes(message):
    try:
        db.session.commit()
        flash(message, "success")
        return True
    except (IntegrityError, SQLAlchemyError):
        db.session.rollback()
        flash(
            "The changes could not be saved. Check for duplicate codes or slugs.",
            "danger",
        )
        return False


@addon_catalogue_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():
    page = request.args.get("page", 1, type=int)
    active_filter = request.args.get("active", "active")
    active = (
        True if active_filter == "active"
        else False if active_filter == "inactive"
        else None)

    pagination = AddonCatalogueService.list_addons(
        search=request.args.get("q", ""),
        category=request.args.get("category", ""),
        service_type=request.args.get("service_type", ""),
        active=active,
        page=page,)

    return render_template(
        "admin/bookings/addon_catalogue/index.html",
        pagination=pagination,
        addons=pagination.items,
        search=request.args.get("q", ""),
        selected_category=request.args.get("category", ""),
        selected_service=request.args.get("service_type", ""),
        active_filter=active_filter,
        categories=AddonCatalogue.CATEGORIES,
        service_types=AddonCatalogue.SERVICE_TYPES,)

@addon_catalogue_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = _load_form(AddonCatalogueForm())

    if form.validate_on_submit():
        try:
            AddonCatalogueService.create_addon(form.data)
            if _commit_changes("Add-on created successfully."):
                return redirect(url_for("admin_addon_catalogue.index"))
        except (ValueError, TypeError) as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Unable to create the add-on. Please try again.", "danger")

    return render_template(
        "admin/bookings/addon_catalogue/create.html", form=form)

@addon_catalogue_bp.route("/<int:addon_id>")
@login_required
@admin_required
def detail(addon_id):
    addon = AddonCatalogueService.get_addon(addon_id)
    if addon is None:
        abort(404)

    return render_template(
        "admin/bookings/addon_catalogue/detail.html", addon=addon
    )


@addon_catalogue_bp.route("/<int:addon_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(addon_id):
    addon = AddonCatalogueService.get_addon(addon_id)
    if addon is None:
        abort(404)

    form = _load_form(AddonCatalogueForm(), addon)

    if form.validate_on_submit():
        try:
            AddonCatalogueService.update_addon(addon, form.data)
            if _commit_changes("Add-on updated successfully."):
                return redirect(
                    url_for("admin_addon_catalogue.detail", addon_id=addon.id)
                )
        except (ValueError, TypeError) as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Unable to update the add-on. Please try again.", "danger")

    return render_template(
        "admin/bookings/addon_catalogue/edit.html",
        form=form,
        addon=addon,)

@addon_catalogue_bp.route("/<int:addon_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle(addon_id):
    addon = AddonCatalogueService.get_addon(addon_id)
    if addon is None:
        abort(404)

    AddonCatalogueService.set_active(addon, not addon.active)

    if _commit_changes(
        "Add-on activated." if addon.active else "Add-on deactivated."
    ):
        return redirect(
            request.referrer or url_for("admin_addon_catalogue.index")
        )

    return redirect(url_for("admin_addon_catalogue.detail", addon_id=addon.id))