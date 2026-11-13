
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from app.decorators.admin import admin_required
from app.forms.admin_signature_moment import (
    AdminSignatureMomentForm,
)
from app.models import Experience
from app.services.signature_moment_service import (
    SignatureMomentService,
)


# =============================================================================
# BLUEPRINT
# =============================================================================

admin_signature_moments_bp = Blueprint(
    "admin_signature_moments",
    __name__,
    url_prefix="/admin/experiences/signature-moments",
)


# =============================================================================
# HELPERS
# =============================================================================

def _get_moment_or_404(moment_id):
    """
    Retrieve a Signature Moment or return HTTP 404.
    """

    moment = SignatureMomentService.get_by_id(moment_id)

    if moment is None:
        abort(404)

    return moment


def _form_data(form):
    """
    Return validated form data in the format expected by the service.

    Signature Moments are independent catalogue records.
    Experience assignments are managed separately through the
    many-to-many Experience relationship.
    """

    return {
        "title": form.title.data.strip(),
        "short_description": form.short_description.data,
        "full_description": form.full_description.data,
        "moment_type": form.moment_type.data,
        "expected_time": form.expected_time.data,
        "estimated_duration": form.estimated_duration.data,
        "best_season": form.best_season.data,
        "photography_recommended": form.photography_recommended.data,
        "emotional_impact": form.emotional_impact.data,
        "featured": form.featured.data,
        "display_order": form.display_order.data,
        "active": form.active.data,
        "hero_media_id": form.hero_media_id.data or None,
    }


def _redirect_back():
    """
    Return to the referring page or the Signature Moments listing.
    """

    return redirect(
        request.referrer
        or url_for("admin_signature_moments.index")
    )


def _filter_moments_by_experience(moments, experience_id):
    """
    Filter Signature Moments by their many-to-many Experience assignments.

    This only filters the catalogue listing. It never modifies or
    deletes any Signature Moment or relationship.
    """

    if not experience_id:
        return moments

    return [
        moment
        for moment in moments
        if moment.experiences.filter(
            Experience.id == experience_id
        ).count() > 0
    ]


# =============================================================================
# SIGNATURE MOMENTS LISTING
# =============================================================================

@admin_signature_moments_bp.route("/", methods=["GET"])
@login_required
@admin_required
def index():

    moments = SignatureMomentService.get_all(
        active_only=False,
        featured_only=False,
    )

    search = request.args.get("search", "").strip().lower()
    experience_id = request.args.get("experience_id", type=int)
    moment_type = request.args.get("moment_type", "").strip()
    status = request.args.get("status", "").strip()
    featured = request.args.get("featured", "").strip()

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    if search:
        moments = [
            moment
            for moment in moments
            if search in (moment.title or "").lower()
            or search in (moment.short_description or "").lower()
            or search in (moment.full_description or "").lower()
        ]

    # -------------------------------------------------------------------------
    # Experience Filter
    # -------------------------------------------------------------------------

    moments = _filter_moments_by_experience(
        moments,
        experience_id,
    )

    # -------------------------------------------------------------------------
    # Moment Type Filter
    # -------------------------------------------------------------------------

    if moment_type:
        moments = [
            moment
            for moment in moments
            if moment.moment_type == moment_type
        ]

    # -------------------------------------------------------------------------
    # Status Filter
    # -------------------------------------------------------------------------

    if status == "active":
        moments = [
            moment
            for moment in moments
            if moment.active
        ]

    elif status == "inactive":
        moments = [
            moment
            for moment in moments
            if not moment.active
        ]

    # -------------------------------------------------------------------------
    # Featured Filter
    # -------------------------------------------------------------------------

    if featured == "yes":
        moments = [
            moment
            for moment in moments
            if moment.featured
        ]

    elif featured == "no":
        moments = [
            moment
            for moment in moments
            if not moment.featured
        ]

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    statistics = SignatureMomentService.get_statistics()

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------

    return render_template(
        "admin/signature_moments/index.html",
        moments=moments,
        statistics=statistics,
        experiences=(
            Experience.query
            .order_by(Experience.title.asc())
            .all()
        ),
        filters={
            "search": request.args.get("search", ""),
            "experience_id": experience_id,
            "moment_type": moment_type,
            "status": status,
            "featured": featured,
        },
    )


# =============================================================================
# CREATE SIGNATURE MOMENT
# =============================================================================

@admin_signature_moments_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def create():

    form = AdminSignatureMomentForm()

    if form.validate_on_submit():

        data = _form_data(form)

        moment = SignatureMomentService.create_moment(
            **data
        )

        if moment:
            flash(
                "Signature moment created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_signature_moments.detail",
                    moment_id=moment.id,
                )
            )

        flash(
            "The signature moment could not be created.",
            "danger",
        )

    return render_template(
        "admin/signature_moments/create.html",
        form=form,
    )


# =============================================================================
# SIGNATURE MOMENT DETAILS
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>",
    methods=["GET"],
)
@login_required
@admin_required
def detail(moment_id):

    moment = _get_moment_or_404(moment_id)

    return render_template(
        "admin/signature_moments/detail.html",
        moment=moment,
    )


# =============================================================================
# EDIT SIGNATURE MOMENT
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def edit(moment_id):

    moment = _get_moment_or_404(moment_id)

    form = AdminSignatureMomentForm(obj=moment)

    if request.method == "GET":
        form.hero_media_id.data = moment.hero_media_id or 0

    if form.validate_on_submit():

        updated_moment = SignatureMomentService.update_moment(
            moment_id,
            **_form_data(form),
        )

        if updated_moment:
            flash(
                "Signature moment updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_signature_moments.detail",
                    moment_id=moment_id,
                )
            )

        flash(
            "The signature moment could not be updated.",
            "danger",
        )

    return render_template(
        "admin/signature_moments/edit.html",
        form=form,
        moment=moment,
    )


# =============================================================================
# ACTIVATE
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/activate",
    methods=["POST"],
)
@login_required
@admin_required
def activate(moment_id):

    _get_moment_or_404(moment_id)

    SignatureMomentService.activate(moment_id)

    flash(
        "Signature moment activated.",
        "success",
    )

    return _redirect_back()


# =============================================================================
# DEACTIVATE
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/deactivate",
    methods=["POST"],
)
@login_required
@admin_required
def deactivate(moment_id):

    _get_moment_or_404(moment_id)

    SignatureMomentService.deactivate(moment_id)

    flash(
        "Signature moment deactivated.",
        "success",
    )

    return _redirect_back()


# =============================================================================
# FEATURE
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/feature",
    methods=["POST"],
)
@login_required
@admin_required
def feature(moment_id):

    _get_moment_or_404(moment_id)

    SignatureMomentService.feature(moment_id)

    flash(
        "Signature moment featured.",
        "success",
    )

    return _redirect_back()


# =============================================================================
# UNFEATURE
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/unfeature",
    methods=["POST"],
)
@login_required
@admin_required
def unfeature(moment_id):

    _get_moment_or_404(moment_id)

    SignatureMomentService.unfeature(moment_id)

    flash(
        "Signature moment removed from featured items.",
        "success",
    )

    return _redirect_back()


# =============================================================================
# UPDATE DISPLAY ORDER
# =============================================================================

@admin_signature_moments_bp.route(
    "/<int:moment_id>/order",
    methods=["POST"],
)
@login_required
@admin_required
def order(moment_id):

    _get_moment_or_404(moment_id)

    display_order = request.form.get(
        "display_order",
        type=int,
    )

    if display_order is None or display_order < 1:

        flash(
            "Enter a valid display order.",
            "danger",
        )

    else:

        SignatureMomentService.set_display_order(
            moment_id,
            display_order,
        )

        flash(
            "Display order updated.",
            "success",
        )

    return _redirect_back()


# =============================================================================
# DELETE
# =============================================================================
@admin_signature_moments_bp.route("/<int:moment_id>/delete",methods=["POST"],)
@login_required
@admin_required
def delete(moment_id):
    _get_moment_or_404(moment_id)
    if SignatureMomentService.delete(moment_id):
        flash("Signature moment deleted successfully.","success",)

    else:
        flash(
            "The signature moment could not be deleted.",
            "danger",)

    return redirect(
        url_for("admin_signature_moments.index"))

# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    "admin_signature_moments_bp",]