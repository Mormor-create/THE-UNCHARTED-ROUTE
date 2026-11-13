"""
===============================================================================
THE UNCHARTED ROUTE
Admin Testimonial Routes
===============================================================================
Administrative routes for managing curated customer testimonials.
Handles:
- Testimonial listing, filtering, searching and pagination
- Creating, viewing and editing testimonials
- Experience, Stay and Safari Package associations
- Media Library photo and video selectors
- Featured and homepage status
- Verification and activation/deactivation
- Display ordering and deletion
- Testimonial statistics
===============================================================================
"""

from datetime import datetime
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from app.decorators.admin import admin_required
from app.forms.testimonial import (
    TestimonialForm,
    TestimonialFilterForm,
    TestimonialSortForm,
    TestimonialFeatureForm,
    TestimonialHomepageForm,
    TestimonialVerificationForm,
    TestimonialStatusForm,
    TestimonialDeleteForm,)
from app.models import Experience, Testimonial
from app.services.testimonial_service import TestimonialService
from app.services.media_service import (
    get_cms_media_assets,
    get_media_folder_by_slug,)
# =============================================================================
# Optional Model Imports
# =============================================================================
try:
    from app.models import Stay
except ImportError:
    from app.models.stay import Stay

try:
    from app.models import SafariPackageOption
except ImportError:
    from app.models.safari import SafariPackageOption


# =============================================================================
# Blueprint
# =============================================================================

admin_testimonial_bp = Blueprint(
    "admin_testimonial",
    __name__,
    url_prefix="/admin/testimonials",
)


# =============================================================================
# Shared Listing Helpers
# =============================================================================

def _is_available(record):
    """Return whether a listing or media record is active."""
    if record is None:
        return False

    for attribute in ("active", "is_active"):
        value = getattr(record, attribute, None)

        if value is False:
            return False

    return True


def _active_experiences():
    """Return active experiences ordered by title."""
    records = Experience.query.order_by(Experience.title.asc()).all()

    return [
        record
        for record in records
        if _is_available(record)
    ]


def _active_stays():
    """Return active stays in a predictable alphabetical order."""
    records = [
        record
        for record in Stay.query.all()
        if _is_available(record)
    ]

    def stay_label(record):
        return (
            getattr(record, "name", None)
            or getattr(record, "title", None)
            or getattr(record, "property_name", None)
            or getattr(record, "stay_name", None)
            or getattr(record, "slug", None)
            or f"Stay #{record.id}"
        )

    return sorted(
        records,
        key=lambda record: stay_label(record).lower(),
    )


def _safari_package_label(package):
    """Build a readable label for a safari package option."""
    package_name = (
        getattr(package, "name", None)
        or getattr(package, "title", None)
        or getattr(package, "package_name", None)
        or getattr(package, "option_name", None)
        or f"Safari Package #{package.id}"
    )

    property_record = (
        getattr(package, "property", None)
        or getattr(package, "safari_property", None)
    )

    destination = (
        getattr(package, "destination", None)
        or getattr(property_record, "destination", None)
    )

    property_name = (
        getattr(property_record, "name", None)
        or getattr(property_record, "title", None)
        or getattr(property_record, "property_name", None)
    )

    destination_name = (
        getattr(destination, "name", None)
        or getattr(destination, "title", None)
    )

    details = [
        value
        for value in (property_name, destination_name)
        if value
    ]

    if details:
        return f"{package_name} — {' · '.join(details)}"

    return package_name


def _active_safari_packages():
    """
    Return active safari packages whose associated property and destination
    are also active when those relationships exist.
    """
    available = []

    for package in SafariPackageOption.query.all():
        if not _is_available(package):
            continue

        property_record = (
            getattr(package, "property", None)
            or getattr(package, "safari_property", None)
        )

        destination = (
            getattr(package, "destination", None)
            or getattr(property_record, "destination", None)
        )

        if (
            property_record is not None
            and not _is_available(property_record)
        ):
            continue

        if (
            destination is not None
            and not _is_available(destination)
        ):
            continue

        available.append(package)

    return sorted(
        available,
        key=lambda package: _safari_package_label(package).lower(),
    )


def _populate_listing_choices(form, include_all=False):
    """Populate the Experience, Stay and Safari Package selectors."""
    experiences = (
        Experience.query.order_by(Experience.title.asc()).all()
        if include_all
        else _active_experiences()
    )

    stays = (
        Stay.query.all()
        if include_all
        else _active_stays()
    )

    safari_packages = (
        SafariPackageOption.query.all()
        if include_all
        else _active_safari_packages()
    )

    form.set_listing_choices(
        experiences=experiences,
        stays=stays,
        safari_packages=safari_packages,
    )

    if include_all:
        for field_name, label in (
            ("experience_id", "All Experiences"),
            ("stay_id", "All Stays"),
            ("safari_package_option_id", "All Safari Packages"),
        ):
            field = getattr(form, field_name, None)

            if field is not None and field.choices:
                field.choices[0] = (0, label)


# =============================================================================
# Testimonials Media Library Helpers
# =============================================================================

def _get_testimonial_media_assets(media_type):
    """
    Return active assets of the requested type from the Testimonials folder
    and all its active descendants.

    Deliberately does not fall back to the entire Media Library if the
    Testimonials folder is missing or inactive.
    """
    folder = get_media_folder_by_slug("testimonials")

    if folder is None or not _is_available(folder):
        return []

    return get_cms_media_assets(
        folder_id=folder.id,
        include_descendants=True,
        media_type=media_type,
        active_only=True,)

def _populate_testimonial_media_choices(form):
    """
    Populate each selector with assets from the Testimonials folder only.

    Both photo fields receive images. The video field receives videos.
    """
    profile_assets = _get_testimonial_media_assets("image")
    customer_assets = _get_testimonial_media_assets("image")
    video_assets = _get_testimonial_media_assets("video")

    form.set_media_choices(
        profile_assets=profile_assets,
        customer_assets=customer_assets,
        video_assets=video_assets,)

def _populate_form_choices(form, include_all=False):
    """Populate all listing and Testimonials-folder media selectors."""
    _populate_listing_choices(form, include_all=include_all)
    _populate_testimonial_media_choices(form)


def _selected_id(value):
    """Convert empty selector values and the zero option to None."""
    if value in (None, "", 0, "0"):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _form_listing_ids(form):
    """Return selected listing IDs without mixing listing types."""
    return {
        "experience_id": _selected_id(form.experience_id.data),
        "stay_id": _selected_id(form.stay_id.data),
        "safari_package_option_id": _selected_id(
            form.safari_package_option_id.data
        ),
    }


def _form_media_ids(form):
    """Return selected photo and video Media Library IDs."""
    return {
        "profile_photo_asset_id": _selected_id(
            form.profile_photo_asset_id.data
        ),
        "customer_photo_asset_id": _selected_id(
            form.customer_photo_asset_id.data
        ),
        "video_asset_id": _selected_id(
            form.video_asset_id.data
        ),
    }


def _validate_listing_selection(listing_ids):
    """
    Ensure a testimonial is associated with at most one listing type
    and that the selected listing exists and is available.
    """
    selected = [
        (field_name, record_id)
        for field_name, record_id in listing_ids.items()
        if record_id is not None
    ]

    if len(selected) > 1:
        return False

    if not selected:
        return True

    field_name, record_id = selected[0]

    model_map = {
        "experience_id": Experience,
        "stay_id": Stay,
        "safari_package_option_id": SafariPackageOption,
    }

    record = model_map[field_name].query.get(record_id)

    if record is None:
        return False

    if field_name == "safari_package_option_id":
        return any(
            package.id == record_id
            for package in _active_safari_packages()
        )

    return _is_available(record)


def _validate_media_selection(media_ids):
    """
    Validate every selected asset against its required media type and
    the Testimonials folder hierarchy.
    """
    image_ids = {
        asset.id
        for asset in _get_testimonial_media_assets("image")
    }

    video_ids = {
        asset.id
        for asset in _get_testimonial_media_assets("video")
    }

    profile_photo_id = media_ids.get("profile_photo_asset_id")
    customer_photo_id = media_ids.get("customer_photo_asset_id")
    video_asset_id = media_ids.get("video_asset_id")

    if (
        profile_photo_id is not None
        and profile_photo_id not in image_ids
    ):
        return False

    if (
        customer_photo_id is not None
        and customer_photo_id not in image_ids
    ):
        return False

    if (
        video_asset_id is not None
        and video_asset_id not in video_ids
    ):
        return False

    return True


def _get_testimonial_or_404(testimonial_id):
    """Load a testimonial or raise a 404 response."""
    testimonial = TestimonialService.get_by_id(testimonial_id)

    if testimonial is None:
        abort(404)
    return testimonial

def _redirect_to_detail(testimonial_id):
    """Redirect to the testimonial details page."""
    return redirect(
        url_for(
            "admin_testimonial.detail",
            testimonial_id=testimonial_id,
        )
    )


def _validate_action_form(form, message):
    """Validate a POST action form and report invalid submissions."""
    if form.validate_on_submit():
        return True

    flash(message, "danger")
    return False


def _render_create_form(form):
    """Render the create template while retaining populated choices."""
    return render_template(
        "admin/testimonials/create.html",
        form=form,
    )


def _render_edit_form(form, testimonial):
    """Render the edit template while retaining populated choices."""
    return render_template(
        "admin/testimonials/edit.html",
        form=form,
        testimonial=testimonial,
    )


# =============================================================================
# Index — Listing, Filtering, Sorting, Pagination and Statistics
# =============================================================================
@admin_testimonial_bp.route("/")
@admin_required
def index():
    """Display the testimonial management dashboard."""
    form = TestimonialFilterForm(request.args)
    _populate_listing_choices(form, include_all=True)

    query = list(TestimonialService.get_all() or [])

    # Search
    search = request.args.get("search", "", type=str).strip().lower()

    if search:
        searchable_fields = (
            "customer_name",
            "customer_country",
            "customer_city",
            "company",
            "position",
            "title",
            "testimonial",
            "short_testimonial",
            "source",
        )

        query = [
            item
            for item in query
            if any(
                search in str(getattr(item, field, "") or "").lower()
                for field in searchable_fields
            )
        ]

    # Listing filters
    experience_id = request.args.get("experience_id", 0, type=int)
    stay_id = request.args.get("stay_id", 0, type=int)
    safari_package_option_id = request.args.get(
        "safari_package_option_id",
        0,
        type=int,
    )

    if experience_id:
        query = [
            item for item in query
            if item.experience_id == experience_id
        ]

    if stay_id:
        query = [
            item for item in query
            if getattr(item, "stay_id", None) == stay_id
        ]

    if safari_package_option_id:
        query = [
            item for item in query
            if getattr(item, "safari_package_option_id", None)
            == safari_package_option_id
        ]

    # Rating and source
    rating = request.args.get("rating", 0, type=int)

    if rating:
        query = [
            item for item in query
            if item.rating == rating
        ]

    source = request.args.get("source", "", type=str).strip()

    if source:
        query = [
            item for item in query
            if item.source == source
        ]

    # Boolean filters
    true_values = {"1", "true", "yes"}
    false_values = {"0", "false", "no"}

    for parameter, attribute in (
        ("featured", "featured"),
        ("homepage", "homepage"),
        ("active", "active"),
        ("verified", "verified"),
    ):
        value = request.args.get(
            parameter,
            "",
            type=str,
        ).lower()

        if value in true_values:
            query = [
                item for item in query
                if bool(getattr(item, attribute, False))
            ]
        elif value in false_values:
            query = [
                item for item in query
                if not bool(getattr(item, attribute, False))
            ]

    # Sorting
    sort = request.args.get("sort", "sort_order", type=str)

    def created_key(item):
        value = getattr(item, "created_at", None)

        if value is None:
            return datetime.min

        # Use a timestamp to avoid aware/naive datetime comparison errors.
        try:
            return value.timestamp()
        except (AttributeError, OSError, ValueError):
            return 0

    if sort == "newest":
        query.sort(key=created_key, reverse=True)

    elif sort == "oldest":
        query.sort(key=created_key)

    elif sort == "name_asc":
        query.sort(
            key=lambda item: (
                getattr(item, "customer_name", "") or ""
            ).lower()
        )

    elif sort == "name_desc":
        query.sort(
            key=lambda item: (
                getattr(item, "customer_name", "") or ""
            ).lower(),
            reverse=True,
        )

    elif sort == "rating_desc":
        query.sort(
            key=lambda item: getattr(item, "rating", 0) or 0,
            reverse=True,
        )

    elif sort == "rating_asc":
        query.sort(
            key=lambda item: getattr(item, "rating", 0) or 0
        )

    else:
        query.sort(
            key=lambda item: (
                getattr(item, "sort_order", 0) or 0,
                created_key(item),
            )
        )

    # Pagination
    page = max(1, request.args.get("page", 1, type=int))
    per_page = request.args.get("per_page", 20, type=int)

    if per_page not in {10, 20, 50, 100}:
        per_page = 20

    total = len(query)
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, pages)

    start = (page - 1) * per_page
    testimonials = query[start:start + per_page]

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_prev": page > 1,
        "has_next": page < pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < pages else None,
    }

    # Statistics
    all_testimonials = list(TestimonialService.get_all() or [])

    active_count = sum(
        bool(item.active)
        for item in all_testimonials
    )
    verified_count = sum(
        bool(item.verified)
        for item in all_testimonials
    )
    featured_count = sum(
        bool(item.featured)
        for item in all_testimonials
    )
    homepage_count = sum(
        bool(item.homepage)
        for item in all_testimonials
    )

    statistics = {
        "total": len(all_testimonials),
        "active": active_count,
        "inactive": len(all_testimonials) - active_count,
        "verified": verified_count,
        "unverified": len(all_testimonials) - verified_count,
        "featured": featured_count,
        "homepage": homepage_count,
        "rating": TestimonialService.get_rating_statistics(),
    }

    return render_template(
        "admin/testimonials/index.html",
        testimonials=testimonials,
        pagination=pagination,
        form=form,
        statistics=statistics,)

# =============================================================================
# Create
# =============================================================================
@admin_testimonial_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    """Create a testimonial with listing and Media Library associations."""
    form = TestimonialForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        listing_ids = _form_listing_ids(form)
        media_ids = _form_media_ids(form)

        if not _validate_listing_selection(listing_ids):
            flash(
                "Select no more than one valid, active experience, stay "
                "or safari package.",
                "danger",
            )
            return _render_create_form(form)

        if not _validate_media_selection(media_ids):
            flash(
                "A selected media item is unavailable, is outside the "
                "Testimonials folder, or has the wrong media type. "
                "Please choose an available item from the correct selector.",
                "danger",
            )
            return _render_create_form(form)

        testimonial = TestimonialService.create_testimonial(
            customer_name=(form.customer_name.data or "").strip(),
            testimonial=(form.testimonial.data or "").strip(),
            **listing_ids,
            **media_ids,
            customer_country=form.customer_country.data,
            customer_city=form.customer_city.data,
            company=form.company.data,
            position=form.position.data,
            title=form.title.data,
            short_testimonial=form.short_testimonial.data,
            rating=form.rating.data,
            video_url=form.video_url.data,
            featured=form.featured.data,
            homepage=form.homepage.data,
            active=form.active.data,
            verified=form.verified.data,
            sort_order=form.sort_order.data,
            source=form.source.data,
        )

        if not testimonial:
            flash(
                "The testimonial could not be created. Please review the "
                "submitted information and try again.",
                "danger",
            )
            return _render_create_form(form)

        flash("Testimonial created successfully.", "success")

        return redirect(
            url_for(
                "admin_testimonial.detail",
                testimonial_id=testimonial.id,
            )
        )

    return _render_create_form(form)


# =============================================================================
# Detail
# =============================================================================

@admin_testimonial_bp.route("/<int:testimonial_id>")
@admin_required
def detail(testimonial_id):
    """Display testimonial details and moderation controls."""
    testimonial = _get_testimonial_or_404(testimonial_id)

    return render_template(
        "admin/testimonials/detail.html",
        testimonial=testimonial,
        feature_form=TestimonialFeatureForm(),
        homepage_form=TestimonialHomepageForm(),
        verification_form=TestimonialVerificationForm(),
        status_form=TestimonialStatusForm(),
        sort_form=TestimonialSortForm(
            sort_order=testimonial.sort_order,
        ),
        delete_form=TestimonialDeleteForm(),
    )

# =============================================================================
# Edit
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(testimonial_id):
    """Edit testimonial content, listing associations and media selections."""
    testimonial = _get_testimonial_or_404(testimonial_id)

    form = TestimonialForm(obj=testimonial)
    _populate_form_choices(form)

    if request.method == "GET":
        form.experience_id.data = testimonial.experience_id or 0
        form.stay_id.data = getattr(testimonial, "stay_id", None) or 0
        form.safari_package_option_id.data = (
            getattr(testimonial, "safari_package_option_id", None) or 0
        )

        form.profile_photo_asset_id.data = (
            getattr(testimonial, "profile_photo_asset_id", None) or 0
        )
        form.customer_photo_asset_id.data = (
            getattr(testimonial, "customer_photo_asset_id", None) or 0
        )
        form.video_asset_id.data = (
            getattr(testimonial, "video_asset_id", None) or 0
        )

    if form.validate_on_submit():
        listing_ids = _form_listing_ids(form)
        media_ids = _form_media_ids(form)

        if not _validate_listing_selection(listing_ids):
            flash(
                "Select no more than one valid, active experience, stay "
                "or safari package.",
                "danger",
            )
            return _render_edit_form(form, testimonial)

        if not _validate_media_selection(media_ids):
            flash(
                "A selected media item is unavailable, is outside the "
                "Testimonials folder, or has the wrong media type. "
                "Please choose an available item from the correct selector.",
                "danger",
            )
            return _render_edit_form(form, testimonial)

        updated = TestimonialService.update_testimonial(
            testimonial_id,
            customer_name=(form.customer_name.data or "").strip(),
            testimonial=(form.testimonial.data or "").strip(),
            **listing_ids,
            **media_ids,
            customer_country=form.customer_country.data,
            customer_city=form.customer_city.data,
            company=form.company.data,
            position=form.position.data,
            title=form.title.data,
            short_testimonial=form.short_testimonial.data,
            rating=form.rating.data,
            video_url=form.video_url.data,
            featured=form.featured.data,
            homepage=form.homepage.data,
            active=form.active.data,
            verified=form.verified.data,
            sort_order=form.sort_order.data,
            source=form.source.data,
        )

        if updated:
            flash("Testimonial updated successfully.", "success")
            return _redirect_to_detail(testimonial_id)

        flash(
            "The testimonial could not be updated. Please try again.",
            "danger",
        )

    return _render_edit_form(form, testimonial)

# =============================================================================
# Shared Moderation Action
# =============================================================================
def _run_testimonial_action(
    testimonial_id,
    form_class,
    service_method,
    success_message,
    invalid_message,
    success_category="success",
):
    """Run a validated testimonial moderation action."""
    _get_testimonial_or_404(testimonial_id)

    form = form_class()

    if not _validate_action_form(form, invalid_message):
        return _redirect_to_detail(testimonial_id)

    testimonial = getattr(
        TestimonialService,
        service_method,
    )(testimonial_id)

    if not testimonial:
        abort(404)

    flash(success_message, success_category)
    return _redirect_to_detail(testimonial_id)


# =============================================================================
# Featured Status
# =============================================================================

@admin_testimonial_bp.route(
    "/<int:testimonial_id>/feature",
    methods=["POST"],
)
@admin_required
def feature(testimonial_id):
    """Mark a testimonial as featured."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialFeatureForm,
        "feature",
        "Testimonial marked as featured.",
        "Invalid feature request.",
    )


@admin_testimonial_bp.route("/<int:testimonial_id>/unfeature",methods=["POST"],)
@admin_required
def unfeature(testimonial_id):
    """Remove featured status from a testimonial."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialFeatureForm,
        "unfeature",
        "Testimonial removed from featured testimonials.",
        "Invalid feature request.",)

# =============================================================================
# Homepage Display
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/homepage",
methods=["POST"],)
@admin_required
def add_to_homepage(testimonial_id):
    """Add a testimonial to homepage display."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialHomepageForm,
        "add_to_homepage",
        "Testimonial added to homepage.",
        "Invalid homepage request.",)

@admin_testimonial_bp.route(
    "/<int:testimonial_id>/remove-homepage",
    methods=["POST"],)
@admin_required
def remove_from_homepage(testimonial_id):
    """Remove a testimonial from homepage display."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialHomepageForm,
        "remove_from_homepage",
        "Testimonial removed from homepage.",
        "Invalid homepage request.",)

# =============================================================================
# Verification
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/verify",methods=["POST"],)
@admin_required
def verify(testimonial_id):
    """Verify a testimonial."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialVerificationForm,
        "verify",
        "Testimonial verified successfully.",
        "Invalid verification request.",
    )


@admin_testimonial_bp.route(
    "/<int:testimonial_id>/unverify",
    methods=["POST"],
)
@admin_required
def unverify(testimonial_id):
    """Remove testimonial verification."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialVerificationForm,
        "unverify",
        "Testimonial marked as unverified.",
        "Invalid verification request.",
        success_category="warning",)

# =============================================================================
# Activation / Deactivation
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/activate",methods=["POST"],)
@admin_required
def activate(testimonial_id):
    """Activate a testimonial."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialStatusForm,
        "activate",
        "Testimonial activated successfully.",
        "Invalid status request.",)

@admin_testimonial_bp.route("/<int:testimonial_id>/deactivate",methods=["POST"],)
@admin_required
def deactivate(testimonial_id):
    """Deactivate a testimonial."""
    return _run_testimonial_action(
        testimonial_id,
        TestimonialStatusForm,
        "deactivate",
        "Testimonial deactivated successfully.",
        "Invalid status request.",
        success_category="warning",)

@admin_testimonial_bp.route("/<int:testimonial_id>/status",methods=["POST"],)
@admin_required
def status(testimonial_id):
    """Update testimonial activation status through the status form."""
    _get_testimonial_or_404(testimonial_id)
    form = TestimonialStatusForm()
    if not _validate_action_form(form, "Invalid status request."):
        return _redirect_to_detail(testimonial_id)

    if form.active.data:
        testimonial = TestimonialService.activate(testimonial_id)
        message = "Testimonial activated successfully."
        category = "success"
    else:
        testimonial = TestimonialService.deactivate(testimonial_id)
        message = "Testimonial deactivated successfully."
        category = "warning"

    if not testimonial:
        abort(404)

    flash(message, category)
    return _redirect_to_detail(testimonial_id)

# =============================================================================
# Display Ordering
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/sort",methods=["POST"],)
@admin_required
def sort(testimonial_id):
    """Update testimonial display order."""
    _get_testimonial_or_404(testimonial_id)

    form = TestimonialSortForm()

    if not _validate_action_form(form, "Invalid display order."):
        return _redirect_to_detail(testimonial_id)

    updated = TestimonialService.update_sort_order(
        testimonial_id,
        form.sort_order.data,
    )

    if updated is False:
        flash("The display order could not be updated.", "danger")
    else:
        flash("Testimonial display order updated.", "success")

    return _redirect_to_detail(testimonial_id)

# =============================================================================
# Delete
# =============================================================================
@admin_testimonial_bp.route("/<int:testimonial_id>/delete",methods=["POST"],)
@admin_required
def delete(testimonial_id):
    """Permanently delete a testimonial after confirmation."""
    _get_testimonial_or_404(testimonial_id)

    form = TestimonialDeleteForm()

    if not _validate_action_form(
        form,
        "Please confirm that you want to delete this testimonial.",
    ):
        return _redirect_to_detail(testimonial_id)

    deleted = TestimonialService.delete_testimonial(testimonial_id)

    if not deleted:
        abort(404)

    flash("Testimonial deleted permanently.", "success")
    return redirect(url_for("admin_testimonial.index"))