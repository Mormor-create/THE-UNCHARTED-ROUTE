from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.decorators.admin import admin_required
from app.forms.admin_stay_review import AdminStayReviewForm
from app.services.admin.admin_stay_review_service import (
    add_admin_response,
    approve_stay_review,
    create_stay_review,
    delete_stay_review,
    get_stay_review,
    get_stay_reviews,
    hide_stay_review,
    reject_stay_review,
    set_stay_review_featured,
    set_stay_review_status,
    set_stay_review_verified,
    update_stay_review,
)
from app.services.admin.admin_stay_service import get_stay


stay_review_bp = Blueprint(
    "admin_stay_review",
    __name__,
    url_prefix="/admin/stays",
)


# ============================================================================
# Review Index
# ============================================================================

@stay_review_bp.route("/<int:stay_id>/reviews/")
#@admin_required
def index(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    reviews = get_stay_reviews(
        stay_id=stay.id,
    )

    return render_template(
        "admin/stays/reviews/index.html",
        stay=stay,
        reviews=reviews,
    )


# ============================================================================
# Create
# ============================================================================

@stay_review_bp.route(
    "/<int:stay_id>/reviews/create",
    methods=["GET", "POST"],
)
#@admin_required
def create(stay_id):
    stay = get_stay(stay_id)

    if stay is None:
        flash("Stay not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayReviewForm()

    if form.validate_on_submit():
        try:
            review = create_stay_review(
                acting_admin=current_user,
                stay_id=stay.id,
                guest_name=form.guest_name.data,
                guest_email=form.guest_email.data,
                rating=form.rating.data,
                title=form.title.data,
                review=form.review.data,
                room_name=form.room_name.data,
                stay_date=form.stay_date.data,
                status=form.status.data,
                verified_stay=form.verified_stay.data,
                featured=form.featured.data,
                admin_response=form.admin_response.data,
            )

            flash(
                "Stay review was created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_review.detail",
                    review_id=review.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/reviews/create.html",
        form=form,
        stay=stay,
    )


# ============================================================================
# Detail
# ============================================================================

@stay_review_bp.route("/reviews/<int:review_id>")
#@admin_required
def detail(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    return render_template(
        "admin/stays/reviews/detail.html",
        review=review,
        stay=review.stay,
    )


# ============================================================================
# Edit
# ============================================================================

@stay_review_bp.route(
    "/reviews/<int:review_id>/edit",
    methods=["GET", "POST"],
)
#@admin_required
def edit(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    form = AdminStayReviewForm(obj=review)

    if form.validate_on_submit():
        try:
            update_stay_review(
                acting_admin=current_user,
                review=review,
                stay_id=review.stay_id,
                guest_name=form.guest_name.data,
                guest_email=form.guest_email.data,
                rating=form.rating.data,
                title=form.title.data,
                review_text=form.review.data,
                room_name=form.room_name.data,
                stay_date=form.stay_date.data,
                status=form.status.data,
                verified_stay=form.verified_stay.data,
                featured=form.featured.data,
                admin_response=form.admin_response.data,
            )

            flash(
                "Stay review was updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_stay_review.detail",
                    review_id=review.id,
                )
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/stays/reviews/edit.html",
        form=form,
        review=review,
        stay=review.stay,
    )


# ============================================================================
# Moderation
# ============================================================================

@stay_review_bp.route(
    "/reviews/<int:review_id>/approve",
    methods=["POST"],
)
#@admin_required
def approve(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        approve_stay_review(
            acting_admin=current_user,
            review=review,
        )

        flash("Review was approved.", "success")

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/reject",
    methods=["POST"],
)
#@admin_required
def reject(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        reject_stay_review(
            acting_admin=current_user,
            review=review,
        )

        flash("Review was rejected.", "success")

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/hide",
    methods=["POST"],
)
#@admin_required
def hide(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        hide_stay_review(
            acting_admin=current_user,
            review=review,
        )

        flash("Review was hidden.", "success")

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/status",
    methods=["POST"],
)
#@admin_required
def status(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    new_status = request.form.get("status")

    if not new_status:
        flash(
            "Review status is required.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_stay_review.detail",
                review_id=review.id,
            )
        )

    try:
        set_stay_review_status(
            acting_admin=current_user,
            review=review,
            status=new_status,
        )

        flash(
            "Review status was updated.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


# ============================================================================
# Verification / Featured
# ============================================================================

@stay_review_bp.route(
    "/reviews/<int:review_id>/verify",
    methods=["POST"],
)
#@admin_required
def verify(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_review_verified(
            acting_admin=current_user,
            review=review,
            verified=True,
        )

        flash(
            "Review was marked as verified.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/unverify",
    methods=["POST"],
)
#@admin_required
def unverify(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_review_verified(
            acting_admin=current_user,
            review=review,
            verified=False,
        )

        flash(
            "Review verification was removed.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/feature",
    methods=["POST"],
)
#@admin_required
def feature(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_review_featured(
            acting_admin=current_user,
            review=review,
            featured=True,
        )

        flash(
            "Review was featured.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


@stay_review_bp.route(
    "/reviews/<int:review_id>/unfeature",
    methods=["POST"],
)
#@admin_required
def unfeature(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    try:
        set_stay_review_featured(
            acting_admin=current_user,
            review=review,
            featured=False,
        )

        flash(
            "Review was unfeatured.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


# ============================================================================
# Admin Response
# ============================================================================

@stay_review_bp.route(
    "/reviews/<int:review_id>/response",
    methods=["POST"],
)
#@admin_required
def response(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    response_text = request.form.get(
        "admin_response",
        "",
    ).strip()

    if not response_text:
        flash(
            "Admin response cannot be empty.",
            "danger",
        )
        return redirect(
            url_for(
                "admin_stay_review.detail",
                review_id=review.id,
            )
        )

    try:
        add_admin_response(
            acting_admin=current_user,
            review=review,
            response=response_text,
        )

        flash(
            "Admin response was saved.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.detail",
            review_id=review.id,
        )
    )


# ============================================================================
# Delete
# ============================================================================

@stay_review_bp.route(
    "/reviews/<int:review_id>/delete",
    methods=["POST"],
)
#@admin_required
def delete(review_id):
    review = get_stay_review(review_id)

    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("admin_stay.index"))

    stay_id = review.stay_id

    try:
        delete_stay_review(
            acting_admin=current_user,
            review=review,
        )

        flash(
            "Review was deleted.",
            "success",
        )

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        url_for(
            "admin_stay_review.index",
            stay_id=stay_id,
        )
    )