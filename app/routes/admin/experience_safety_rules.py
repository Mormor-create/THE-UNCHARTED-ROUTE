"""
===============================================================================
The Uncharted Route
Admin Experience Safety Rule Routes
===============================================================================

Administrative routes for managing safety rules attached to experiences.

Supported operations:

- List safety rules
- Create safety rules
- Edit safety rules
- View safety rule details
- Activate safety rules
- Deactivate safety rules
- Toggle safety rule status
- Delete safety rules
- Reorder safety rules
- Filter by category
- Filter by priority
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    login_required,
)

from app.forms.admin_experience_safety_rules import (
    ExperienceSafetyRuleCreateForm,
    ExperienceSafetyRuleEditForm,
    SAFETY_CATEGORY_CHOICES,
    SAFETY_PRIORITY_CHOICES,
)

from app.models import (
    Experience,
    ExperienceSafetyRule,
)

from app.services.experiences.experience_safety_rule_service import (
    create_safety_rule,
    delete_safety_rule,
    get_experience_safety_rules,
    get_rules_by_category,
    get_rules_by_priority,
    get_safety_rule,
    update_safety_rule,
    activate_safety_rule,
    deactivate_safety_rule,
    toggle_safety_rule,
    reorder_safety_rule,
    reorder_safety_rules,
    count_safety_rules,
)

# =============================================================================
# Blueprint
# =============================================================================

admin_experience_safety_rules = Blueprint(
    "admin_experience_safety_rules",
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

    experience = Experience.query.get_or_404(
        experience_id
    )

    return experience


# =============================================================================
# Index
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules"
)
#@login_required
def index(experience_id):
    """
    Display all safety rules belonging to an experiences.

    Supports optional filtering by:

    - category
    - priority
    - status
    """

    experience = _get_experience_or_404(
        experience_id
    )

    category = request.args.get(
        "category",
        "",
    ).strip()

    priority = request.args.get(
        "priority",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    # -------------------------------------------------------------------------
    # Filter by category
    # -------------------------------------------------------------------------

    if category:

        if category not in dict(
            SAFETY_CATEGORY_CHOICES
        ):
            flash(
                "Invalid safety category.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_experience_safety_rules.index",
                    experience_id=experience.id,
                )
            )

        rules = get_rules_by_category(
            experience.id,
            category,
            active_only=(status != "all"),
        )

    # -------------------------------------------------------------------------
    # Filter by priority
    # -------------------------------------------------------------------------

    elif priority:

        if priority not in dict(
            SAFETY_PRIORITY_CHOICES
        ):
            flash(
                "Invalid safety priority.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_experience_safety_rules.index",
                    experience_id=experience.id,
                )
            )

        rules = get_rules_by_priority(
            experience.id,
            priority,
            active_only=(status != "all"),
        )

    # -------------------------------------------------------------------------
    # Default retrieval
    # -------------------------------------------------------------------------

    else:

        rules = get_experience_safety_rules(
            experience.id,
            active_only=(status != "all"),
        )

    # -------------------------------------------------------------------------
    # Status filtering
    # -------------------------------------------------------------------------

    if status == "inactive":
        rules = [
            rule
            for rule in rules
            if not rule.active
        ]

    elif status == "active":
        rules = [
            rule
            for rule in rules
            if rule.active
        ]

    # -------------------------------------------------------------------------
    # Counts
    # -------------------------------------------------------------------------

    total_count = count_safety_rules(
        experience.id,
        active_only=False,
    )

    active_count = count_safety_rules(
        experience.id,
        active_only=True,
    )

    inactive_count = (
        total_count - active_count
    )

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------

    return render_template(
        "admin/experiences/experience_safety_rules/index.html",
        experience=experience,
        rules=rules,
        categories=SAFETY_CATEGORY_CHOICES,
        priorities=SAFETY_PRIORITY_CHOICES,
        selected_category=category,
        selected_priority=priority,
        selected_status=status,
        total_count=total_count,
        active_count=active_count,
        inactive_count=inactive_count,
    )


# =============================================================================
# Create
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules/create",
    methods=["GET", "POST"],
)
#@login_required
def create(experience_id):
    """
    Create a new safety rule for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceSafetyRuleCreateForm()

    if form.validate_on_submit():

        data = {
            "title": form.title.data,
            "description": form.description.data,
            "category": form.category.data,
            "priority": form.priority.data,
            "icon": form.icon.data,
            "display_order": form.display_order.data,
            "active": form.active.data,
        }

        try:

            rule = create_safety_rule(
                experience.id,
                data,
            )

            flash(
                f'Safety rule "{rule.title}" was created successfully.',
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_safety_rules.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_safety_rules/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@admin_experience_safety_rules.route("/<int:experience_id>/safety-rules/<int:rule_id>/edit",methods=["GET", "POST"],)
#@login_required
def edit(
    experience_id,
    rule_id,
):
    """
    Edit an existing safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceSafetyRuleEditForm(
        obj=rule
    )

    if form.validate_on_submit():

        data = {
            "title": form.title.data,
            "description": form.description.data,
            "category": form.category.data,
            "priority": form.priority.data,
            "icon": form.icon.data,
            "display_order": form.display_order.data,
            "active": form.active.data,
        }

        try:

            update_safety_rule(
                rule.id,
                data,
            )

            flash(
                "Safety rule updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_safety_rules.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_safety_rules/edit.html",
        experience=experience,
        rule=rule,
        form=form,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules/<int:rule_id>/activate",
    methods=["POST"],
)
#@login_required
def activate(
    experience_id,
    rule_id,
):
    """
    Activate a safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    try:

        activate_safety_rule(
            rule.id
        )

        flash(
            f'Safety rule "{rule.title}" has been activated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules/<int:rule_id>/deactivate",
    methods=["POST"],)
#@login_required
def deactivate(
    experience_id,
    rule_id,
):
    """
    Deactivate a safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    try:

        deactivate_safety_rule(
            rule.id
        )

        flash(
            f'Safety rule "{rule.title}" has been deactivated.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Toggle
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules/<int:rule_id>/toggle",
    methods=["POST"],)
#@login_required
def toggle(
    experience_id,
    rule_id,
):
    """
    Toggle the active state of a safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    try:

        toggle_safety_rule(
            rule.id
        )

        state = (
            "activated"
            if rule.active
            else "deactivated"
        )

        flash(
            f'Safety rule "{rule.title}" has been {state}.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_experience_safety_rules.route(
    "/<int:experience_id>/safety-rules/<int:rule_id>/delete",
    methods=["POST"],)
#@login_required
def delete(
    experience_id,
    rule_id,
):
    """
    Permanently delete a safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    rule_title = rule.title

    try:

        delete_safety_rule(
            rule.id
        )

        flash(
            f'Safety rule "{rule_title}" was deleted.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )

# =============================================================================
# Reorder Single Rule
# =============================================================================
@admin_experience_safety_rules.route("/<int:experience_id>/safety-rules/<int:rule_id>/reorder",methods=["POST"],)
#@login_required
def reorder(
    experience_id,
    rule_id,
):
    """
    Change the display order of a single safety rule.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule = get_safety_rule(
        rule_id
    )

    if rule is None or rule.experience_id != experience.id:

        flash(
            "Safety rule not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_experience_safety_rules.index",
                experience_id=experience.id,
            )
        )

    try:

        display_order = int(
            request.form.get(
                "display_order",
                0,
            )
        )

        reorder_safety_rule(
            rule.id,
            display_order,
        )

        flash(
            "Safety rule order updated successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )

# =============================================================================
# Bulk Reorder
# =============================================================================
@admin_experience_safety_rules.route("/<int:experience_id>/safety-rules/reorder",methods=["POST"],)
#@login_required
def reorder_bulk(experience_id):
    """
    Reorder multiple safety rules.

    Expected form input:

        rule_ids[]

    containing rule IDs in their desired order.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    rule_ids = request.form.getlist(
        "rule_ids[]"
    )

    if not rule_ids:
        rule_ids = request.form.getlist(
            "rule_ids"
        )

    try:

        ordered_rule_ids = [
            int(rule_id)
            for rule_id in rule_ids
        ]

        reorder_safety_rules(
            experience.id,
            ordered_rule_ids,
        )

        flash(
            "Safety rules reordered successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_safety_rules.index",
            experience_id=experience.id,
        )
    )