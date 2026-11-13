"""
===============================================================================
The Uncharted Route
Admin Promotion Routes
===============================================================================

Admin routes for:
- Managing promotional offers.
- Creating and editing promotional posters.
- Deleting promotions.
- Viewing customer promotion inquiries.
- Managing inquiry follow-ups.

Promotion inquiries are independent of the booking system.

===============================================================================
"""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.decorators.admin import admin_required

from app.forms.promotion_forms import (
    PromotionForm,
    PromotionInquiryUpdateForm,
)

from app.models.promotion import (
    Promotion,
    PromotionInquiry,
)

from app.services.promotion_service import PromotionService

from extensions import db


# =============================================================================
# Blueprint
# =============================================================================

admin_promotions = Blueprint(
    "admin_promotions",
    __name__,
    url_prefix="/admin/promotions",)

# =============================================================================
# Helpers
# =============================================================================
def _prepare_promotion_form(form):
    """
    Populate the poster dropdown using images from the Promotions
    folder in the CMS Media Library.
    """
    form.poster_media_asset_id.choices = [
        (0, "Choose a poster from the Media Library"),
        *PromotionService.get_poster_choices(),]

def _get_poster_preview_map():
    """Return poster preview URLs for the promotion form."""
    return PromotionService.get_poster_preview_map()

# =============================================================================
# Promotion Listing
# =============================================================================
@admin_promotions.route("/")
@admin_required
def index():
    """Display all promotions in the admin area."""

    promotions = (
        Promotion.query
        .order_by(
            Promotion.created_at.desc(),
            Promotion.id.desc(),
        ).all())

    inquiry_counts = PromotionService.get_inquiry_counts()

    return render_template(
        "admin/promotions/index.html",
        promotions=promotions,
        inquiry_counts=inquiry_counts,)

# =============================================================================
# Create Promotion
# =============================================================================
@admin_promotions.route("/create",methods=["GET", "POST"],)
@admin_required
def create():
    """Create a new promotion."""

    form = PromotionForm()
    _prepare_promotion_form(form)
    if form.validate_on_submit():
        try:
            promotion = PromotionService.create_promotion(form)

            flash(
                "Promotion created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_promotions.edit",
                    promotion_id=promotion.id,
                )
            )

        except ValueError as exc:
            db.session.rollback()

            flash(
                str(exc),"danger",)

        except Exception:
            db.session.rollback()

            flash(
                "The promotion could not be saved. Please try again.",
                "danger",)

    return render_template(
        "admin/promotions/form.html",
        form=form,
        promotion=None,
        poster_preview_map=_get_poster_preview_map(),
        page_title="Create Promotion",)

# =============================================================================
# Edit Promotion
# =============================================================================
@admin_promotions.route("/<int:promotion_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(promotion_id):
    """Edit an existing promotion."""

    promotion = db.session.get(
        Promotion,
        promotion_id,)

    if promotion is None:
        abort(404)

    form = PromotionForm(obj=promotion)
    _prepare_promotion_form(form)
    if form.validate_on_submit():
        try:
            PromotionService.update_promotion(
                promotion,
                form,
            )

            flash(
                "Promotion updated successfully.",
                "success",
            )

            return redirect(
                url_for("admin_promotions.index")
            )

        except ValueError as exc:
            db.session.rollback()

            flash(
                str(exc),
                "danger",
            )

        except Exception:
            db.session.rollback()

            flash(
                "The promotion could not be updated. Please try again.",
                "danger",
            )

    return render_template(
        "admin/promotions/form.html",
        form=form,
        promotion=promotion,
        poster_preview_map=_get_poster_preview_map(),
        page_title="Edit Promotion",
    )


# =============================================================================
# Delete Promotion
# =============================================================================
@admin_promotions.route("/<int:promotion_id>/delete",methods=["POST"],)
@admin_required
def delete(promotion_id):
    """
    Delete a promotion while keeping its poster in the Media Library.
    Associated promotion inquiries are retained through the SET NULL
    foreign key relationship.
    """

    promotion = db.session.get(
        Promotion,
        promotion_id,)
    if promotion is None:
        abort(404)

    try:
        PromotionService.delete_promotion(promotion)

        flash(
            "Promotion deleted successfully. Existing inquiries have been retained.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "The promotion could not be deleted. Please try again.",
            "danger",
        )

    return redirect(
        url_for("admin_promotions.index")
    )

# =============================================================================
# Promotion Inquiries Listing
# =============================================================================
@admin_promotions.route("/inquiries", methods=["GET"])
@admin_required
def inquiries():
    """
    Display and filter customer inquiries relating to promotions.
    """

    status = request.args.get("status", "").strip() or None
    promotion_id = request.args.get("promotion_id", type=int)
    search = request.args.get("search", "").strip() or None
    page = request.args.get("page", 1, type=int)

    if status and not PromotionService.validate_inquiry_status(status):
        status = None

    pagination = PromotionService.get_inquiries(
        status=status,
        promotion_id=promotion_id,
        search=search,
        page=page,
        per_page=20,
    )

    promotions = (
        Promotion.query
        .order_by(Promotion.title.asc())
        .all()
    )

    inquiry_counts = PromotionService.get_inquiry_counts()

    # Template expects (value, label) pairs.
    inquiry_statuses = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    return render_template(
        "admin/promotions/inquiries/index.html",
        inquiries=pagination.items,
        pagination=pagination,
        promotions=promotions,
        inquiry_counts=inquiry_counts,
        selected_status=status,
        selected_promotion_id=promotion_id,
        search=search or "",
        inquiry_statuses=inquiry_statuses,
    )

# =============================================================================
# Promotion Inquiry Details
# =============================================================================

@admin_promotions.route(
    "/inquiries/<int:inquiry_id>",
    methods=["GET", "POST"],
)
@admin_required
def inquiry_detail(inquiry_id):
    """
    View a customer promotion inquiry and manage its follow-up.
    """

    inquiry = PromotionService.get_inquiry_by_id(
        inquiry_id
    )

    if inquiry is None:
        abort(404)

    form = PromotionInquiryUpdateForm(
        obj=inquiry
    )

    if form.validate_on_submit():
        try:
            PromotionService.update_promotion_inquiry(
                inquiry=inquiry,
                status=form.status.data,
                admin_notes=form.admin_notes.data,
            )

            flash(
                "Promotion inquiry updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_promotions.inquiry_detail",
                    inquiry_id=inquiry.id,
                )
            )

        except ValueError as exc:
            db.session.rollback()

            flash(
                str(exc),
                "danger",
            )

        except Exception:
            db.session.rollback()

            flash(
                "The inquiry could not be updated. Please try again.",
                "danger",
            )

    return render_template(
        "admin/promotions/inquiries/detail.html",
        inquiry=inquiry,
        form=form,)

# =============================================================================
# Promotion Inquiry Status Filters
# =============================================================================
@admin_promotions.route("/inquiries/status/<string:status>",methods=["GET"],)
@admin_required
def inquiries_by_status(status):
    """Redirect to the inquiry listing with a status filter."""

    if not PromotionService.validate_inquiry_status(status):
        abort(404)

    return redirect(
        url_for(
            "admin_promotions.inquiries",
            status=status,))