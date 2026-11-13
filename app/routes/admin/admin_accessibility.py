"""
===============================================================================
The Uncharted Route — Admin Accessibility Profiles CMS
===============================================================================
Administrative management of reusable accessibility profiles.
Routes
------

    /admin/accessibility/
    /admin/accessibility/create
    /admin/accessibility/<id>
    /admin/accessibility/<id>/edit
    /admin/accessibility/<id>/activate
    /admin/accessibility/<id>/deactivate
    /admin/accessibility/<id>/delete
    /admin/accessibility/statistics
Business logic is delegated to:
    AccessibilityService
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
from flask_login import login_required

from app.decorators.admin import admin_required

from app.forms.admin_accessibility import (
    AdminAccessibilityDeleteForm,
    AdminAccessibilityFilterForm,
    AdminAccessibilityForm,
)

from app.services.accessibility_service import (
    AccessibilityService,
)

# =============================================================================
# Blueprint
# =============================================================================
admin_accessibility_bp = Blueprint(
    "admin_accessibility",
    __name__,
    url_prefix="/admin/accessibility",)

# =============================================================================
# Dashboard
# =============================================================================
@admin_accessibility_bp.route("/",methods=["GET"],)
#@login_required
#@admin_required
def index():
    """
    Display the Accessibility Profiles CMS dashboard.

    Supports:

    - Search
    - Status filtering
    - Wheelchair accessibility filtering
    - Child-friendly filtering
    - Fitness-level filtering
    """

    form = AdminAccessibilityFilterForm(
        request.args,
    )

    query_text = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    active = request.args.get(
        "active",
        "",
        type=str,
    )

    wheelchair_accessible = request.args.get(
        "wheelchair_accessible",
        "",
        type=str,
    )

    child_friendly = request.args.get(
        "child_friendly",
        "",
        type=str,
    )

    fitness_level = request.args.get(
        "fitness_level",
        "",
        type=str,
    )

    # -------------------------------------------------------------------------
    # Base Query
    # -------------------------------------------------------------------------

    if query_text:

        profiles = AccessibilityService.search(
            query=query_text,
            active_only=False,
        )

    else:

        profiles = AccessibilityService.get_all(
            active_only=False,
        )

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------

    if active in {"0", "1"}:

        requested_status = (
            active == "1"
        )

        profiles = [
            profile
            for profile in profiles
            if profile.active == requested_status
        ]

    if wheelchair_accessible in {"0", "1"}:

        requested_value = (
            wheelchair_accessible == "1"
        )

        profiles = [
            profile
            for profile in profiles
            if profile.wheelchair_accessible
            == requested_value
        ]

    if child_friendly in {"0", "1"}:

        requested_value = (
            child_friendly == "1"
        )

        profiles = [
            profile
            for profile in profiles
            if profile.child_friendly
            == requested_value
        ]

    if fitness_level:

        profiles = [
            profile
            for profile in profiles
            if (
                profile.minimum_fitness_level
                and profile.minimum_fitness_level.lower()
                == fitness_level.lower()
            )
        ]

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    statistics = AccessibilityService.get_statistics()

    return render_template(
        "admin/accessibility/index.html",
        profiles=profiles,
        form=form,
        statistics=statistics,
    )


# =============================================================================
# Create
# =============================================================================
@admin_accessibility_bp.route("/create",methods=["GET", "POST"],)
#@login_required
#@admin_required
def create():
    """
    Create a new accessibility profile.
    """

    form = AdminAccessibilityForm()

    if form.validate_on_submit():

        try:

            profile = AccessibilityService.create_profile(
                name=form.name.data.strip(),

                slug=(
                    form.slug.data.strip()
                    if form.slug.data
                    else None
                ),

                summary=form.summary.data,

                wheelchair_accessible=(
                    form.wheelchair_accessible.data
                ),

                stroller_friendly=(
                    form.stroller_friendly.data
                ),

                walking_required=(
                    form.walking_required.data
                ),

                hiking_required=(
                    form.hiking_required.data
                ),

                uneven_terrain=(
                    form.uneven_terrain.data
                ),

                stairs_required=(
                    form.stairs_required.data
                ),

                child_friendly=(
                    form.child_friendly.data
                ),

                elderly_friendly=(
                    form.elderly_friendly.data
                ),

                pregnancy_friendly=(
                    form.pregnancy_friendly.data
                ),

                pet_friendly=(
                    form.pet_friendly.data
                ),

                minimum_fitness_level=(
                    form.minimum_fitness_level.data
                ),

                maximum_altitude_meters=(
                    form.maximum_altitude_meters.data
                ),

                accessible_restrooms=(
                    form.accessible_restrooms.data
                ),

                changing_facilities=(
                    form.changing_facilities.data
                ),

                medical_support_available=(
                    form.medical_support_available.data
                ),

                vegetarian_available=(
                    form.vegetarian_available.data
                ),

                vegan_available=(
                    form.vegan_available.data
                ),

                halal_available=(
                    form.halal_available.data
                ),

                kosher_available=(
                    form.kosher_available.data
                ),

                gluten_free_available=(
                    form.gluten_free_available.data
                ),

                allergy_support=(
                    form.allergy_support.data
                ),

                multilingual_guides=(
                    form.multilingual_guides.data
                ),

                sign_language_available=(
                    form.sign_language_available.data
                ),

                braille_materials=(
                    form.braille_materials.data
                ),

                audio_guides=(
                    form.audio_guides.data
                ),

                notes=form.notes.data,

                active=form.active.data,
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/accessibility/create.html",
                form=form,
            )

        flash(
            "Accessibility profile created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_accessibility.detail",
                profile_id=profile.id,
            )
        )

    return render_template(
        "admin/accessibility/create.html",
        form=form,
    )


# =============================================================================
# Detail
# =============================================================================
@admin_accessibility_bp.route("/<int:profile_id>",methods=["GET"],)
#@login_required
#@admin_required
def detail(profile_id):
    """
    Display an accessibility profile.
    """

    profile = AccessibilityService.get_by_id(
        profile_id
    )

    if not profile:
        abort(404)

    usage_count = AccessibilityService.get_usage_count(
        profile_id
    )

    delete_form = AdminAccessibilityDeleteForm()

    return render_template(
        "admin/accessibility/detail.html",
        profile=profile,
        usage_count=usage_count,
        delete_form=delete_form,
    )


# =============================================================================
# Edit
# =============================================================================
@admin_accessibility_bp.route("/<int:profile_id>/edit",methods=["GET", "POST"],)
#@login_required
#@admin_required
def edit(profile_id):
    """
    Edit an accessibility profile.
    """

    profile = AccessibilityService.get_by_id(
        profile_id
    )

    if not profile:
        abort(404)

    form = AdminAccessibilityForm(
        obj=profile,
    )

    if form.validate_on_submit():

        try:

            AccessibilityService.update_profile(
                profile_id=profile.id,

                name=form.name.data.strip(),

                slug=(
                    form.slug.data.strip()
                    if form.slug.data
                    else None
                ),

                summary=form.summary.data,

                wheelchair_accessible=(
                    form.wheelchair_accessible.data
                ),

                stroller_friendly=(
                    form.stroller_friendly.data
                ),

                walking_required=(
                    form.walking_required.data
                ),

                hiking_required=(
                    form.hiking_required.data
                ),

                uneven_terrain=(
                    form.uneven_terrain.data
                ),

                stairs_required=(
                    form.stairs_required.data
                ),

                child_friendly=(
                    form.child_friendly.data
                ),

                elderly_friendly=(
                    form.elderly_friendly.data
                ),

                pregnancy_friendly=(
                    form.pregnancy_friendly.data
                ),

                pet_friendly=(
                    form.pet_friendly.data
                ),

                minimum_fitness_level=(
                    form.minimum_fitness_level.data
                ),

                maximum_altitude_meters=(
                    form.maximum_altitude_meters.data
                ),

                accessible_restrooms=(
                    form.accessible_restrooms.data
                ),

                changing_facilities=(
                    form.changing_facilities.data
                ),

                medical_support_available=(
                    form.medical_support_available.data
                ),

                vegetarian_available=(
                    form.vegetarian_available.data
                ),

                vegan_available=(
                    form.vegan_available.data
                ),

                halal_available=(
                    form.halal_available.data
                ),

                kosher_available=(
                    form.kosher_available.data
                ),

                gluten_free_available=(
                    form.gluten_free_available.data
                ),

                allergy_support=(
                    form.allergy_support.data
                ),

                multilingual_guides=(
                    form.multilingual_guides.data
                ),

                sign_language_available=(
                    form.sign_language_available.data
                ),

                braille_materials=(
                    form.braille_materials.data
                ),

                audio_guides=(
                    form.audio_guides.data
                ),

                notes=form.notes.data,

                active=form.active.data,
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/accessibility/edit.html",
                form=form,
                profile=profile,
            )

        flash(
            "Accessibility profile updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_accessibility.detail",
                profile_id=profile.id,
            )
        )

    return render_template(
        "admin/accessibility/edit.html",
        form=form,
        profile=profile,
    )


# =============================================================================
# Activate
# =============================================================================
@admin_accessibility_bp.route("/<int:profile_id>/activate",methods=["POST"],)
#@login_required
#@admin_required
def activate(profile_id):
    """
    Activate an accessibility profile.
    """

    profile = AccessibilityService.activate(
        profile_id
    )

    if not profile:
        abort(404)

    flash(
        f'"{profile.name}" has been activated.',
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_accessibility.index"
        )
    )


# =============================================================================
# Deactivate
# =============================================================================

@admin_accessibility_bp.route(
    "/<int:profile_id>/deactivate",
    methods=["POST"],
)
#@login_required
#@admin_required
def deactivate(profile_id):
    """
    Deactivate an accessibility profile.

    The profile remains in the database and can be
    reactivated later.
    """

    profile = AccessibilityService.deactivate(
        profile_id
    )

    if not profile:
        abort(404)

    flash(
        f'"{profile.name}" has been deactivated.',
        "success",
    )

    return redirect(
        request.referrer
        or url_for(
            "admin_accessibility.index"
        )
    )


# =============================================================================
# Delete
# =============================================================================
@admin_accessibility_bp.route(
    "/<int:profile_id>/delete",
    methods=["POST"],
)
#@login_required
#@admin_required
def delete(profile_id):
    """
    Delete an accessibility profile.

    Profiles currently assigned to experiences cannot
    be deleted.
    """

    profile = AccessibilityService.get_by_id(
        profile_id
    )

    if not profile:
        abort(404)

    form = AdminAccessibilityDeleteForm()

    if not form.validate_on_submit():

        flash(
            "Invalid deletion request.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_accessibility.detail",
                profile_id=profile.id,
            )
        )

    profile_name = profile.name

    try:

        deleted = AccessibilityService.delete_profile(
            profile_id
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_accessibility.detail",
                profile_id=profile.id,
            )
        )

    if not deleted:
        abort(404)

    flash(
        f'"{profile_name}" has been deleted.',
        "success",
    )

    return redirect(
        url_for(
            "admin_accessibility.index"
        )
    )


# =============================================================================
# Statistics
# =============================================================================

@admin_accessibility_bp.route(
    "/statistics",
    methods=["GET"],
)
#@login_required
#@admin_required
def statistics():
    """
    Display Accessibility Profiles CMS statistics.
    """

    statistics_data = AccessibilityService.get_statistics()

    profiles = AccessibilityService.get_all(
        active_only=False,
    )

    return render_template(
        "admin/accessibility/statistics.html",
        statistics=statistics_data,
        profiles=profiles,
    )