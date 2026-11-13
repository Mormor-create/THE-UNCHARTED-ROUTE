"""
===============================================================================
The Uncharted Route
Administrative Destination Management
===============================================================================
Administrative management routes for Destinations.
Destinations are parent records for Experiences.
Responsibilities
----------------
• Destination catalogue
• Search and filtering
• Create destinations
• View destination details
• Edit destinations
• Activate destinations
• Deactivate destinations
• Feature destinations
• Unfeature destinations
• View destination statistics
• View experiences belonging to a destination

Deletion
--------
Destinations are intentionally NOT deleted through this administrative module.

A destination may have many Experiences attached to it. Deactivating a
destination preserves its historical relationships while preventing it from
being presented as an active destination on the public website.

Child resources and Experience records are managed through their respective
modules.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app,
)
from app.decorators.admin import admin_required
from app.forms.admin_destination import (
    AdminDestinationCreateForm,
    AdminDestinationEditForm,
    AdminDestinationFilterForm,
    AdminDestinationStatusForm,
)
from app.services.destination_service import (
    activate_destination,
    count_destination_experiences,
    create_destination,
    deactivate_destination,
    get_all_destinations,
    get_destination,
    get_destination_experiences,
    get_destination_image_choices,
    get_destination_statistics,
    search_destinations,
    set_destination_featured,
    update_destination,)
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
destinations_bp = Blueprint(
    "admin_destinations",
    __name__,
    url_prefix="/admin/destinations",)

# =============================================================================
# Helpers
# =============================================================================
def _get_destination_or_redirect(destination_id):
    """
    Retrieve a destination or redirect to the destination catalogue.

    This helper keeps repeated not-found handling consistent across routes.
    """

    destination = get_destination(destination_id)
    if destination is None:
        flash(
            "Destination not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_destinations.index"
            )
        )

    return destination


def _populate_image_choices(form):
    """
    Populate destination image selectors from the central Media Library.

    Featured image:
        Required image selected from active MediaAssets.

    Banner image:
        Optional image selected from active MediaAssets.
    """

    image_choices = get_destination_image_choices()

    form.featured_image_id.choices = [
        (
            0,
            "Select featured image from Media Library",
        ),
        *image_choices,
    ]

    form.banner_image_id.choices = [
        (
            0,
            "No banner image",
        ),
        *image_choices,
    ]


# =============================================================================
# Destination Catalogue
# =============================================================================
@destinations_bp.route("/")
@admin_required
def index():
    """
    Display the administrative destination catalogue.

    Supports:
    • Search
    • Active/inactive filtering
    • Featured filtering
    • Country filtering
    • County filtering
    • Region filtering
    """

    form = AdminDestinationFilterForm(
        formdata=request.args
    )

    query = form.search.data
    active = form.active.data
    featured = form.featured.data
    country = form.country.data
    county = form.county.data
    region = form.region.data

    # -------------------------------------------------------------------------
    # Normalize filter values
    # -------------------------------------------------------------------------

    if active == "":
        active = None
    elif active == "1":
        active = True
    elif active == "0":
        active = False

    if featured == "":
        featured = None
    elif featured == "1":
        featured = True
    elif featured == "0":
        featured = False

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    if query and query.strip():

        destinations = search_destinations(
            query=query,
            active=active,
        )

        # ---------------------------------------------------------------------
        # Additional filters
        # ---------------------------------------------------------------------

        if featured is not None:
            destinations = [
                destination
                for destination in destinations
                if destination.featured == featured
            ]

        if country:
            country_value = country.strip().lower()

            destinations = [
                destination
                for destination in destinations
                if (
                    destination.country
                    and destination.country.strip().lower()
                    == country_value
                )
            ]

        if county:
            county_value = county.strip().lower()

            destinations = [
                destination
                for destination in destinations
                if (
                    destination.county
                    and destination.county.strip().lower()
                    == county_value
                )
            ]

        if region:
            region_value = region.strip().lower()

            destinations = [
                destination
                for destination in destinations
                if (
                    destination.region
                    and destination.region.strip().lower()
                    == region_value
                )
            ]

    # -------------------------------------------------------------------------
    # Standard filtered catalogue
    # -------------------------------------------------------------------------

    else:

        destinations = get_all_destinations(
            active=active,
            featured=featured,
            country=country,
            county=county,
            region=region,
        )

    return render_template(
        "admin/destinations/index.html",
        form=form,
        destinations=destinations,
    )


# =============================================================================
# Create Destination
# =============================================================================
@destinations_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    """Create a destination using the central Media Library."""

    form = AdminDestinationCreateForm()

    # Populate Media Library choices before form validation.
    _populate_image_choices(form)

    if form.validate_on_submit():
        try:
            destination = create_destination(
                name=form.name.data,
                slug=form.slug.data,
                featured_image_id=form.featured_image_id.data,
                country=form.country.data,
                county=form.county.data,
                region=form.region.data,
                short_description=form.short_description.data,
                description=form.description.data,
                banner_image_id=(
                    form.banner_image_id.data
                    or None
                ),
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                featured=form.featured.data,
                show_on_homepage=form.show_on_homepage.data,
                active=form.active.data,
            )

        except ValueError as exc:
            flash(str(exc), "danger")

            _populate_image_choices(form)

            return render_template(
                "admin/destinations/create.html",
                form=form,
            )

        flash("Destination created successfully.", "success")

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,
            )
        )

    return render_template(
        "admin/destinations/create.html",
        form=form,
    )

# =============================================================================
# Destination Detail
# =============================================================================
@destinations_bp.route("/<int:destination_id>")
@admin_required
def detail(destination_id):
    """
    Display a destination management overview.

    Includes:
    • Destination information
    • Statistics
    • Active and inactive experiences
    """

    destination = _get_destination_or_redirect(
        destination_id
    )

    if not hasattr(destination, "id"):
        return destination

    statistics = get_destination_statistics(
        destination
    )

    experiences = get_destination_experiences(
        destination,
        active=None,
    )

    return render_template(
        "admin/destinations/detail.html",
        destination=destination,
        statistics=statistics,
        experiences=experiences,)

# =============================================================================
# Edit Destination
# =============================================================================
@destinations_bp.route("/<int:destination_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(destination_id):
    """Edit a destination's details and visibility settings."""

    destination = _get_destination_or_redirect(destination_id)

    if not hasattr(destination, "id"):
        return destination

    form = AdminDestinationEditForm(obj=destination)

    # Populate Media Library choices before validating the submitted form.
    _populate_image_choices(form)

    if form.validate_on_submit():
        try:
            update_destination(
                destination,
                name=form.name.data,
                slug=form.slug.data,
                country=form.country.data,
                county=form.county.data,
                region=form.region.data,
                short_description=form.short_description.data,
                description=form.description.data,
                featured_image_id=form.featured_image_id.data,
                banner_image_id=form.banner_image_id.data or None,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                featured=form.featured.data,
                show_on_homepage=form.show_on_homepage.data,
                active=form.active.data,
            )

        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

            return render_template(
                "admin/destinations/edit.html",
                form=form,
                destination=destination,
            )

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update destination %s",
                destination.id,
            )
            flash(
                "The destination could not be saved. Please check the application logs.",
                "danger",
            )

            return render_template(
                "admin/destinations/edit.html",
                form=form,
                destination=destination,
            )

        flash("Destination updated successfully.", "success")

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,
            )
        )

    if form.is_submitted():
        for field_name, errors in form.errors.items():
            flash(
                f"{field_name.replace('_', ' ').title()}: {'; '.join(errors)}",
                "danger",
            )

    return render_template(
        "admin/destinations/edit.html",
        form=form,
        destination=destination,
    )

# =============================================================================
# Activate Destination
# =============================================================================
@destinations_bp.route("/<int:destination_id>/activate",methods=["POST"],)
@admin_required
def activate(destination_id):
    """
    Activate a Destination.
    """

    destination = _get_destination_or_redirect(
        destination_id
    )

    if not hasattr(destination, "id"):
        return destination

    form = AdminDestinationStatusForm()

    if not form.validate_on_submit():

        flash(
            "Invalid destination status request.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,
            )
        )

    activate_destination(
        destination
    )

    flash(
        "Destination activated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_destinations.detail",
            destination_id=destination.id,))

# =============================================================================
# Deactivate Destination
# =============================================================================
@destinations_bp.route("/<int:destination_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate(destination_id):
    """
    Deactivate a Destination.

    Deactivation preserves the destination and all of its Experience
    relationships.
    """

    destination = _get_destination_or_redirect(
        destination_id
    )

    if not hasattr(destination, "id"):
        return destination

    form = AdminDestinationStatusForm()

    if not form.validate_on_submit():

        flash(
            "Invalid destination status request.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,
            )
        )

    deactivate_destination(
        destination
    )

    flash(
        "Destination deactivated successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_destinations.detail",
            destination_id=destination.id,
        )
    )

# =============================================================================
# Feature Destination
# =============================================================================
@destinations_bp.route("/<int:destination_id>/feature",methods=["POST"],)
@admin_required
def feature(destination_id):
    """
    Mark a Destination as featured.
    """

    destination = _get_destination_or_redirect(
        destination_id
    )

    if not hasattr(destination, "id"):
        return destination

    form = AdminDestinationStatusForm()

    if not form.validate_on_submit():

        flash(
            "Invalid destination feature request.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,
            )
        )

    set_destination_featured(
        destination,
        featured=True,
    )

    flash(
        "Destination featured successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_destinations.detail",
            destination_id=destination.id,
        )
    )


# =============================================================================
# Unfeature Destination
# =============================================================================
@destinations_bp.route("/<int:destination_id>/unfeature",methods=["POST"],)
@admin_required
def unfeature(destination_id):
    """
    Remove a Destination from featured sections.
    """

    destination = _get_destination_or_redirect( destination_id)
    if not hasattr(destination, "id"):
        return destination
    form = AdminDestinationStatusForm()
    if not form.validate_on_submit():
        flash(
            "Invalid destination feature request.","danger",)

        return redirect(
            url_for(
                "admin_destinations.detail",
                destination_id=destination.id,))

    set_destination_featured(
        destination,
        featured=False,)

    flash("Destination removed from featured sections.","success",)

    return redirect(
        url_for(
            "admin_destinations.detail",
            destination_id=destination.id,))

# =============================================================================
# Destination Statistics
# =============================================================================
@destinations_bp.route("/<int:destination_id>/statistics")
@admin_required
def statistics(destination_id):
    """
    Display detailed statistics for a Destination.
    """

    destination = _get_destination_or_redirect(
        destination_id
    )

    if not hasattr(destination, "id"):
        return destination

    destination_statistics = get_destination_statistics(
        destination
    )

    return render_template(
        "admin/destinations/statistics.html",
        destination=destination,
        statistics=destination_statistics,
    )


# =============================================================================
# Destination Experiences
# =============================================================================
@destinations_bp.route("/<int:destination_id>/experiences")
@admin_required
def experiences(destination_id):
    """
    Display all Experiences belonging to a Destination.
    """
    destination = _get_destination_or_redirect(destination_id)
    if not hasattr(destination, "id"):
        return destination

    destination_experiences = get_destination_experiences(
        destination,
        active=None,)

    return render_template(
        "admin/destinations/experiences.html",
        destination=destination,
        experiences=destination_experiences,)

# =============================================================================
# Destination Experience Count
# =============================================================================
@destinations_bp.route("/<int:destination_id>/experience-count")
@admin_required
def experience_count(destination_id):
    """
    Display the number of Experiences belonging to a Destination.
    """
    destination = _get_destination_or_redirect(destination_id)
    if not hasattr(destination, "id"):
        return destination
    count = count_destination_experiences(
        destination,
        active=None,)
    return render_template(
        "admin/destinations/experience_count.html",
        destination=destination,
        count=count,)

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "destinations_bp",
]