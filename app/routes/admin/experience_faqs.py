"""
===============================================================================
The Uncharted Route
Admin Experience FAQ Routes
===============================================================================

Administrative routes for managing Frequently Asked Questions attached to
experiences.

Supported operations:

- List FAQs
- Create FAQs
- Edit FAQs
- Activate FAQs
- Deactivate FAQs
- Feature FAQs
- Unfeature FAQs
- Delete FAQs
- Reorder FAQs
- Bulk reorder FAQs
- Filter by category
- Filter by status
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import login_required

from app.forms.admin_experience_faqs import (
    ExperienceFAQCreateForm,
    ExperienceFAQEditForm,
    FAQ_CATEGORY_CHOICES,
)

from app.models import (
    Experience,
    ExperienceFAQ,
)

from app.services.experiences.experience_faq_service import (
    ExperienceFAQService,
)


# =============================================================================
# Blueprint
# =============================================================================

admin_experience_faqs = Blueprint(
    "admin_experience_faqs",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Experience Helper
# =============================================================================

def _get_experience_or_404(experience_id):
    """
    Retrieve an experiences or return a 404 response.
    """

    return Experience.query.get_or_404(
        experience_id
    )


# =============================================================================
# FAQ Helper
# =============================================================================

def _get_faq_for_experience_or_redirect(
    experience_id,
    faq_id,
):
    """
    Retrieve an FAQ and verify that it belongs to the requested experiences.

    Returns:
        tuple[ExperienceFAQ | None, redirect response | None]
    """

    faq = ExperienceFAQService.get_by_id(
        faq_id
    )

    if faq is None or faq.experience_id != experience_id:
        flash(
            "FAQ not found.",
            "danger",
        )

        return (
            None,
            redirect(
                url_for(
                    "admin_experience_faqs.index",
                    experience_id=experience_id,
                )
            ),
        )

    return faq, None


# =============================================================================
# Index
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs")
#@login_required
def index(experience_id):
    """
    Display FAQs belonging to an experiences.

    Supports optional filtering by:

    - category
    - status
    - featured
    """

    experience = _get_experience_or_404(
        experience_id
    )

    category = request.args.get(
        "category",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    featured = request.args.get(
        "featured",
        "",
    ).strip()

    # -------------------------------------------------------------------------
    # Validate category
    # -------------------------------------------------------------------------

    if category and category not in dict(
        FAQ_CATEGORY_CHOICES
    ):
        flash(
            "Invalid FAQ category.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_faqs.index",
                experience_id=experience.id,
            )
        )

    # -------------------------------------------------------------------------
    # Retrieve FAQs
    # -------------------------------------------------------------------------

    faqs = ExperienceFAQService.get_for_experience(
        experience.id,
        active_only=False,
    )

    # -------------------------------------------------------------------------
    # Category filtering
    # -------------------------------------------------------------------------

    if category:
        faqs = [
            faq
            for faq in faqs
            if faq.category == category
        ]

    # -------------------------------------------------------------------------
    # Status filtering
    # -------------------------------------------------------------------------

    if status == "active":

        faqs = [
            faq
            for faq in faqs
            if faq.active
        ]

    elif status == "inactive":

        faqs = [
            faq
            for faq in faqs
            if not faq.active
        ]

    elif status != "all":

        status = "active"

        faqs = [
            faq
            for faq in faqs
            if faq.active
        ]

    # -------------------------------------------------------------------------
    # Featured filtering
    # -------------------------------------------------------------------------

    if featured == "featured":

        faqs = [
            faq
            for faq in faqs
            if faq.featured
        ]

    elif featured == "not_featured":

        faqs = [
            faq
            for faq in faqs
            if not faq.featured
        ]

    # -------------------------------------------------------------------------
    # Counts
    # -------------------------------------------------------------------------

    total_count = ExperienceFAQService.count_for_experience(
        experience.id,
        active_only=False,
    )

    active_count = ExperienceFAQService.count_for_experience(
        experience.id,
        active_only=True,
    )

    inactive_count = (
        total_count - active_count
    )

    featured_count = len(
        ExperienceFAQ.query.filter_by(
            experience_id=experience.id,
            featured=True,
            active=True,
        ).all()
    )

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------

    return render_template(
        "admin/experiences/experience_faqs/index.html",
        experience=experience,
        faqs=faqs,
        categories=FAQ_CATEGORY_CHOICES,
        selected_category=category,
        selected_status=status,
        selected_featured=featured,
        total_count=total_count,
        active_count=active_count,
        inactive_count=inactive_count,
        featured_count=featured_count,
    )


# =============================================================================
# Create
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/create",methods=["GET", "POST"],)
#@login_required
def create(experience_id):
    """
    Create a new FAQ for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceFAQCreateForm()

    if form.validate_on_submit():

        try:

            faq = ExperienceFAQService.create_faq(
                experience.id,
                question=form.question.data,
                answer=form.answer.data,
                category=form.category.data,
                display_order=form.display_order.data or 0,
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                f'FAQ "{faq.question}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_faqs.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_faqs/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# ============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    faq_id,
):
    """
    Edit an existing FAQ.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    form = ExperienceFAQEditForm(
        obj=faq
    )

    if form.validate_on_submit():

        try:

            ExperienceFAQService.update_faq(
                faq.id,
                question=form.question.data,
                answer=form.answer.data,
                category=form.category.data,
                display_order=form.display_order.data or 0,
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                "FAQ updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_faqs.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_faqs/edit.html",
        experience=experience,
        faq=faq,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/activate",methods=["POST"],)
#@login_required
def activate(
    experience_id,
    faq_id,
):
    """
    Activate an FAQ.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    try:

        ExperienceFAQService.activate(
            faq.id
        )

        flash(
            f'FAQ "{faq.question}" has been activated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/deactivate",methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    faq_id,
):
    """
    Deactivate an FAQ without deleting it.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    try:

        ExperienceFAQService.deactivate(
            faq.id
        )

        flash(
            f'FAQ "{faq.question}" has been deactivated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Feature
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/feature",methods=["POST"],)
#@login_required
def feature(
    experience_id,
    faq_id,
):
    """
    Mark an FAQ as featured.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    try:

        ExperienceFAQService.feature(
            faq.id
        )

        flash(
            f'FAQ "{faq.question}" is now featured.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Unfeature
# =============================================================================

@admin_experience_faqs.route(
    "/<int:experience_id>/faqs/<int:faq_id>/unfeature",
    methods=["POST"],
)
@login_required
def unfeature(
    experience_id,
    faq_id,
):
    """
    Remove the featured status from an FAQ.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    try:

        ExperienceFAQService.unfeature(
            faq.id
        )

        flash(
            f'FAQ "{faq.question}" is no longer featured.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/delete",methods=["POST"],)
#@login_required
def delete(
    experience_id,
    faq_id,
):
    """
    Permanently delete an FAQ.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    question = faq.question

    try:

        ExperienceFAQService.delete_faq(
            faq.id
        )

        flash(
            f'FAQ "{question}" was deleted.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Reorder Single FAQ
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/<int:faq_id>/reorder",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    faq_id,
):
    """
    Change the display order of a single FAQ.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq, error_response = (
        _get_faq_for_experience_or_redirect(
            experience.id,
            faq_id,
        )
    )

    if error_response:
        return error_response

    try:

        display_order = int(
            request.form.get(
                "display_order",
                0,
            )
        )

        if display_order < 0:
            raise ValueError(
                "Display order cannot be negative."
            )

        ExperienceFAQService.reorder(
            faq.id,
            display_order,
        )

        flash(
            "FAQ order updated successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Bulk Reorder
# =============================================================================
@admin_experience_faqs.route("/<int:experience_id>/faqs/reorder",methods=["POST"],)
#@login_required
def reorder_bulk(experience_id):
    """
    Reorder multiple FAQs.

    Expected form input:

        faq_ids[]

    containing FAQ IDs in their desired order.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    faq_ids = request.form.getlist(
        "faq_ids[]"
    )

    if not faq_ids:
        faq_ids = request.form.getlist(
            "faq_ids"
        )

    try:

        ordered_faq_ids = [
            int(faq_id)
            for faq_id in faq_ids
        ]

        order_data = [
            {
                "id": faq_id,
                "display_order": position,
            }
            for position, faq_id in enumerate(
                ordered_faq_ids
            )
        ]

        # ---------------------------------------------------------------------
        # Security check
        # ---------------------------------------------------------------------

        valid_faq_ids = {
            faq.id
            for faq in ExperienceFAQService.get_for_experience(
                experience.id,
                active_only=False,
            )
        }

        invalid_ids = (
            set(ordered_faq_ids)
            - valid_faq_ids
        )

        if invalid_ids:
            raise ValueError(
                "One or more FAQs do not belong to this experiences."
            )

        ExperienceFAQService.reorder_many(
            order_data
        )

        flash(
            "FAQs reordered successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_faqs.index",
            experience_id=experience.id,
        )
    )