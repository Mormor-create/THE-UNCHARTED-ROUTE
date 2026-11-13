"""
===============================================================================
The Uncharted Route
Admin Cancellation Policies Routes
===============================================================================
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash)
from app.forms.admin_cancellation_policy import (
    CancellationPolicyForm,
    CancellationPolicyActionForm)
from app.services.cancellation_policy_service import (
    CancellationPolicyService)

# =============================================================================
# Blueprint
# =============================================================================

admin_cancellation_policies = Blueprint(
    "admin_cancellation_policies",
    __name__,
    url_prefix="/admin/cancellation-policies"
)


# =============================================================================
# Index
# =============================================================================
@admin_cancellation_policies.route("/")
#@login_required
def index():

    policies = CancellationPolicyService.get_all()

    statistics: dict[str, int] = CancellationPolicyService.get_statistics()

    return render_template(
        "admin/cancellation_policies/index.html",
        policies=policies,
        statistics=statistics
    )


# =============================================================================
# Create
# =============================================================================

@admin_cancellation_policies.route("/create", methods=["GET", "POST"])
#@login_required
def create():

    form = CancellationPolicyForm()

    if form.validate_on_submit():

        try:

            policy = CancellationPolicyService.create_policy(
                name=form.name.data,
                slug=form.slug.data or None,
                short_description=form.short_description.data or None,
                full_policy=form.full_policy.data,
                full_refund_days=form.full_refund_days.data,
                partial_refund_days=form.partial_refund_days.data,
                partial_refund_percentage=(
                    form.partial_refund_percentage.data
                ),
                no_refund_days=form.no_refund_days.data,
                date_changes_allowed=form.date_changes_allowed.data,
                name_changes_allowed=form.name_changes_allowed.data,
                transferable_booking=form.transferable_booking.data,
                notes=form.notes.data or None,
                active=form.active.data,
                default_policy=form.default_policy.data
            )

            flash(
                f'Cancellation policy "{policy.name}" was created successfully.',
                "success"
            )

            return redirect(
                url_for(
                    "admin_cancellation_policies.detail",
                    policy_id=policy.id
                )
            )

        except Exception as exc:

            flash(
                f"Unable to create cancellation policy: {exc}",
                "danger"
            )

    return render_template(
        "admin/cancellation_policies/create.html",
        form=form
    )


# =============================================================================
# Detail
# =============================================================================

@admin_cancellation_policies.route("/<int:policy_id>")
#@login_required
def detail(policy_id):

    policy = CancellationPolicyService.get_by_id(policy_id)

    if not policy:

        flash(
            "Cancellation policy not found.",
            "warning"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.index"
            )
        )

    experience_count = policy.experience_count
    stay_count = policy.stay_count

    in_use = (
        experience_count > 0
        or stay_count > 0
    )

    return render_template(
        "admin/cancellation_policies/detail.html",
        policy=policy,
        experience_count=experience_count,
        stay_count=stay_count,
        in_use=in_use
    )


# =============================================================================
# Edit
# =============================================================================

@admin_cancellation_policies.route(
    "/<int:policy_id>/edit",
    methods=["GET", "POST"]
)
#@login_required
def edit(policy_id):

    policy = CancellationPolicyService.get_by_id(policy_id)

    if not policy:

        flash(
            "Cancellation policy not found.",
            "warning"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.index"
            )
        )

    form = CancellationPolicyForm(obj=policy)

    if form.validate_on_submit():

        try:

            updated = CancellationPolicyService.update_policy(
                policy_id,
                name=form.name.data,
                slug=form.slug.data or None,
                short_description=form.short_description.data or None,
                full_policy=form.full_policy.data,
                full_refund_days=form.full_refund_days.data,
                partial_refund_days=form.partial_refund_days.data,
                partial_refund_percentage=(
                    form.partial_refund_percentage.data
                ),
                no_refund_days=form.no_refund_days.data,
                date_changes_allowed=form.date_changes_allowed.data,
                name_changes_allowed=form.name_changes_allowed.data,
                transferable_booking=form.transferable_booking.data,
                notes=form.notes.data or None,
                active=form.active.data
            )

            if not updated:
                raise ValueError(
                    "Cancellation policy could not be updated."
                )

            # Handle default separately so the service can guarantee
            # only one active default policy.
            if form.default_policy.data:

                CancellationPolicyService.set_default(
                    policy_id
                )

            elif policy.default_policy:

                policy.default_policy = False

                from extensions import db

                db.session.commit()

            flash(
                f'Cancellation policy "{updated.name}" was updated successfully.',
                "success"
            )

            return redirect(
                url_for(
                    "admin_cancellation_policies.detail",
                    policy_id=updated.id
                )
            )

        except Exception as exc:

            flash(
                f"Unable to update cancellation policy: {exc}",
                "danger"
            )

    return render_template(
        "admin/cancellation_policies/edit.html",
        form=form,
        policy=policy
    )


# =============================================================================
# Activate
# =============================================================================

@admin_cancellation_policies.route(
    "/<int:policy_id>/activate",
    methods=["POST"]
)
#@login_required
def activate(policy_id):

    form = CancellationPolicyActionForm()

    if not form.validate_on_submit():
        flash(
            "Invalid request.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.detail",
                policy_id=policy_id
            )
        )

    policy = CancellationPolicyService.activate(
        policy_id
    )

    if not policy:

        flash(
            "Cancellation policy not found.",
            "warning"
        )

    else:

        flash(
            f'"{policy.name}" has been activated.',
            "success"
        )

    return redirect(
        url_for(
            "admin_cancellation_policies.detail",
            policy_id=policy_id
        )
    )


# =============================================================================
# Deactivate
# =============================================================================

@admin_cancellation_policies.route(
    "/<int:policy_id>/deactivate",
    methods=["POST"]
)
#@login_required
def deactivate(policy_id):

    form = CancellationPolicyActionForm()

    if not form.validate_on_submit():
        flash(
            "Invalid request.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.detail",
                policy_id=policy_id
            )
        )

    policy = CancellationPolicyService.deactivate(
        policy_id
    )

    if not policy:

        flash(
            "Cancellation policy not found.",
            "warning"
        )

    else:

        flash(
            f'"{policy.name}" has been deactivated.',
            "success"
        )

    return redirect(
        url_for(
            "admin_cancellation_policies.detail",
            policy_id=policy_id
        )
    )


# =============================================================================
# Set Default
# =============================================================================

@admin_cancellation_policies.route(
    "/<int:policy_id>/set-default",
    methods=["POST"]
)
#@login_required
def set_default(policy_id):

    form = CancellationPolicyActionForm()

    if not form.validate_on_submit():
        flash(
            "Invalid request.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.detail",
                policy_id=policy_id
            )
        )

    try:

        policy = CancellationPolicyService.set_default(
            policy_id
        )

        if not policy:

            flash(
                "Cancellation policy not found.",
                "warning"
            )

        else:

            flash(
                f'"{policy.name}" is now the default cancellation policy.',
                "success"
            )

    except ValueError as exc:

        flash(
            str(exc),
            "warning"
        )

    return redirect(
        url_for(
            "admin_cancellation_policies.detail",
            policy_id=policy_id
        )
    )


# =============================================================================
# Delete
# =============================================================================

@admin_cancellation_policies.route(
    "/<int:policy_id>/delete",
    methods=["POST"]
)
#@login_required
def delete(policy_id):

    form = CancellationPolicyActionForm()

    if not form.validate_on_submit():

        flash(
            "Invalid request.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.detail",
                policy_id=policy_id
            )
        )

    try:

        deleted = CancellationPolicyService.delete(
            policy_id
        )

        if not deleted:

            flash(
                "Cancellation policy not found.",
                "warning"
            )

            return redirect(
                url_for(
                    "admin_cancellation_policies.index"
                )
            )

        flash(
            "Cancellation policy deleted successfully.",
            "success"
        )

    except ValueError as exc:

        flash(
            str(exc),
            "warning"
        )

        return redirect(
            url_for(
                "admin_cancellation_policies.detail",
                policy_id=policy_id
            )
        )

    return redirect(
        url_for(
            "admin_cancellation_policies.index"
        )
    )


# =============================================================================
# Statistics
# =============================================================================
@admin_cancellation_policies.route("/statistics")
#@login_required
def statistics():

    statistics_data = (
        CancellationPolicyService.get_statistics()
    )

    policies = CancellationPolicyService.get_all()

    return render_template(
        "admin/cancellation_policies/statistics.html",
        statistics=statistics_data,
        policies=policies
    )