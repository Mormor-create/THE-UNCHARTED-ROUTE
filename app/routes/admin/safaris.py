from flask import (
    Blueprint, current_app,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app,)
from sqlalchemy import desc
from app.decorators.admin import admin_required
from app.services.permission_service import (
    MANAGE_SAFARIS,
    permission_required,)
from extensions import db
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPropertyMedia,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
    SafariInquiry,)
from app.forms.safari import (
    SafariDestinationForm,
    SafariPropertyForm,
    SafariPropertyMediaForm,
    SafariPackageOptionForm,
    SafariItineraryDayForm,
    SafariPackageRateForm,)
from app.models.page_hero import PageHero
from app.services.safari.admin_service import (
    list_destinations,
    get_destination,
    save_destination,
    set_destination_active,
    list_properties,
    get_property,
    save_property,
    set_property_active,
    list_property_media,
    save_property_media,
    delete_property_media,
    list_package_options,
    get_package_option,
    save_package_option,
    set_package_option_active,
    list_itinerary_days,
    save_itinerary_day,
    delete_itinerary_day,
    list_rates,
    save_rate,
    set_rate_active,)
from app.services.media_service import (
    get_cms_media_assets,
    get_media_folders,)

admin_safari_bp = Blueprint(
    "admin_safaris",
    __name__,
    url_prefix="/admin/safaris",)

# ============================================================
# SHARED HELPERS
# ============================================================
def _get_or_404(getter, record_id):
    """Retrieve a safari record or return a 404 response."""
    record = getter(record_id)

    if record is None:
        abort(404)
    return record

# ============================================================
# SHARED MEDIA HELPERS
# ============================================================
def _coerce_optional_int(value):
    """Allow blank optional integer dropdowns without raising ValueError."""
    if value is None or value == "":
        return None
    return int(value)

def _get_folder_parent_id(folder):
    """
    Resolve a media folder's parent ID across the supported
    folder model representations.
    """
    parent_id = getattr(folder, "parent_id", None)

    if parent_id is not None:
        return parent_id

    parent = getattr(folder, "parent", None)

    if parent is not None:
        return getattr(parent, "id", None)

    return None


def _get_folder_slug(folder):
    """Return a normalized media folder slug."""
    return (
        getattr(folder, "slug", None)
        or getattr(folder, "name", None)
        or ""
    ).strip().casefold()


def _get_folder_name(folder):
    """Return a readable media folder name."""
    return (
        getattr(folder, "name", None)
        or getattr(folder, "title", None)
        or f"Folder #{getattr(folder, 'id', '')}"
    )


def _build_media_folder_paths(folders):
    """
    Build readable hierarchical paths for Media Library folders.

    Example:
        Safaris
        Safaris / Maasai Mara
        Safaris / Maasai Mara / Hero
    """
    folder_by_id = {
        folder.id: folder
        for folder in folders
        if getattr(folder, "id", None) is not None
    }

    path_cache = {}

    def build_path(folder, seen=None):
        folder_id = getattr(folder, "id", None)

        if folder_id in path_cache:
            return path_cache[folder_id]

        seen = set(seen or set())

        # Protect against malformed circular folder relationships.
        if folder_id in seen:
            return _get_folder_name(folder)

        seen.add(folder_id)

        parent_id = _get_folder_parent_id(folder)

        if parent_id and parent_id in folder_by_id:
            parent = folder_by_id[parent_id]
            path = (
                f"{build_path(parent, seen)}"
                f" / {_get_folder_name(folder)}"
            )
        else:
            path = _get_folder_name(folder)

        path_cache[folder_id] = path
        return path

    return {
        folder.id: build_path(folder)
        for folder in folders
        if getattr(folder, "id", None) is not None}

def _get_safaris_root_folder(folders):
    """
    Locate the top-level Safaris Media Library folder.

    The lookup deliberately checks the folder's slug/name and
    requires it to be a root folder so an unrelated nested folder
    named 'Safaris' cannot become the catalogue root.
    """
    for folder in folders:
        parent_id = _get_folder_parent_id(folder)

        if parent_id is not None:
            continue

        if _get_folder_slug(folder) == "safaris":
            return folder

    return None


def _get_descendant_folder_ids(folders, root_folder_id):
    """
    Return the selected folder and all of its descendants.
    """
    children = {}

    for folder in folders:
        parent_id = _get_folder_parent_id(folder)

        if parent_id is not None:
            children.setdefault(parent_id, []).append(folder.id)

    allowed_ids = {root_folder_id}
    pending = [root_folder_id]

    while pending:
        parent_id = pending.pop()

        for child_id in children.get(parent_id, []):
            if child_id not in allowed_ids:
                allowed_ids.add(child_id)
                pending.append(child_id)

    return allowed_ids

def _populate_safari_destination_media_choices(form):
    """
    Populate Safari Destination DAM selectors.

    The folder selector is limited to the Safaris Media Library tree.

    The card and hero asset selectors are scoped to the EXACT
    folder currently selected. Descendant folders are not included.

    Example:

        Safaris
            ├── Hero
            ├── Card
            ├── Gallery

        Selecting "Safaris"
        -> only assets directly inside Safaris.

        Selecting "Safaris / Maasai Mara"
        -> only assets directly inside Maasai Mara.

        Selecting "Safaris / Maasai Mara / Angama Mara"
        -> only assets directly inside Angama Mara.
    """

    for field_name in (
        "media_folder_id",
        "card_media_asset_id",
        "hero_media_asset_id",
    ):
        field = getattr(form, field_name, None)

        if field is not None:
            field.coerce = _coerce_optional_int

    folder_field = getattr(form, "media_folder_id", None)

    if folder_field is None:
        return []

    # ------------------------------------------------------------------
    # Load all active Media Library folders.
    # ------------------------------------------------------------------
    try:
        folders = get_media_folders(active_only=True) or []

    except Exception:
        current_app.logger.exception(
            "Could not load Media Library folders for Safari destinations."
        )

        folder_field.choices = [
            ("", "Safari Media Library unavailable")
        ]

        for field_name in (
            "card_media_asset_id",
            "hero_media_asset_id",
        ):
            field = getattr(form, field_name, None)

            if field is not None:
                field.choices = [
                    ("", "No Safari media assets available")
                ]

        return []

    # ------------------------------------------------------------------
    # Find the root Safaris folder.
    # ------------------------------------------------------------------
    safaris_root = _get_safaris_root_folder(folders)

    if safaris_root is None:
        current_app.logger.warning(
            "Safari destination media selector could not find "
            "the root Media Library folder named 'Safaris'."
        )

        folder_field.choices = [
            ("", "Safaris Media folder not configured")
        ]

        for field_name in (
            "card_media_asset_id",
            "hero_media_asset_id",
        ):
            field = getattr(form, field_name, None)

            if field is not None:
                field.choices = [
                    ("", "No Safari media assets available")
                ]

        return []

    # ------------------------------------------------------------------
    # Restrict the folder selector itself to:
    #
    # Safaris
    # Safaris / Maasai Mara
    # Safaris / Maasai Mara / Angama Mara
    # ...
    # ------------------------------------------------------------------
    safari_folder_ids = _get_descendant_folder_ids(
        folders,
        safaris_root.id,
    )

    safari_folders = [
        folder
        for folder in folders
        if folder.id in safari_folder_ids
    ]

    folder_paths = _build_media_folder_paths(
        safari_folders
    )

    safari_folders.sort(
        key=lambda folder: folder_paths.get(
            folder.id,
            _get_folder_name(folder),
        ).casefold()
    )

    folder_field.choices = [
        (
            "",
            "Select a Safari media folder",
        )
    ] + [
        (
            str(folder.id),
            folder_paths.get(
                folder.id,
                _get_folder_name(folder),
            ),
        )
        for folder in safari_folders
    ]

    # ------------------------------------------------------------------
    # Determine the selected folder.
    # ------------------------------------------------------------------
    selected_folder_id = folder_field.data

    if selected_folder_id is None:
        selected_folder_id = request.form.get(
            "media_folder_id",
            type=int,
        )

    # ------------------------------------------------------------------
    # IMPORTANT:
    #
    # If no specific folder has been selected yet, use the root
    # Safaris folder.
    #
    # If a folder has been selected, use ONLY that exact folder.
    #
    # No descendants.
    # ------------------------------------------------------------------
    if selected_folder_id not in safari_folder_ids:
        selected_folder_id = safaris_root.id

    # Keep the selected folder visible to WTForms.
    if not form.is_submitted() and folder_field.data is None:
        folder_field.data = selected_folder_id

    # ------------------------------------------------------------------
    # Load assets ONLY from the exact selected folder.
    # ------------------------------------------------------------------
    try:
        assets = get_cms_media_assets(
            folder_id=selected_folder_id,
            include_descendants=False,
            active_only=True,
        ) or []

    except Exception:
        assets = []

        current_app.logger.exception(
            "Could not load Safari Media Library assets "
            "for folder ID %s.",
            selected_folder_id,
        )

        flash(
            "Safari Media Library assets could not be loaded. "
            "Check the selected Safari media folder.",
            "warning",
        )

    # ------------------------------------------------------------------
    # Build readable asset choices.
    #
    # Because we are now querying one exact folder, every asset here
    # belongs directly to the selected folder.
    # ------------------------------------------------------------------
    selected_folder_path = folder_paths.get(
        selected_folder_id,
        "Safaris",
    )

    asset_choices = [
        (
            "",
            "Select a Safari media asset",
        )
    ]

    for asset in assets:
        asset_name = (
            getattr(asset, "title", None)
            or getattr(asset, "original_filename", None)
            or getattr(asset, "filename", None)
            or f"Media asset #{asset.id}"
        )

        asset_choices.append(
            (
                str(asset.id),
                f"{selected_folder_path} / {asset_name}",
            )
        )

    # ------------------------------------------------------------------
    # Apply the exact-folder asset choices to both fields.
    # ------------------------------------------------------------------
    for field_name in (
        "card_media_asset_id",
        "hero_media_asset_id",
    ):
        field = getattr(form, field_name, None)

        if field is not None:
            field.choices = asset_choices

    return assets

def _populate_media_choices(
    form,
    folder_id=None,
    restrict_to_folder=False,
):
    """
    Populate generic Media Library selectors.

    This helper remains available for property/media forms.
    Safari Destination forms use the dedicated
    _populate_safari_destination_media_choices() helper so
    their DAM is never accidentally populated from the global
    Media Library.
    """

    for field_name in (
        "media_folder_id",
        "card_media_asset_id",
        "hero_media_asset_id",
        "media_asset_id",
    ):
        field = getattr(form, field_name, None)

        if field is not None:
            field.coerce = _coerce_optional_int

    folder_field = getattr(form, "media_folder_id", None)

    if folder_field is not None:
        try:
            folders = get_media_folders(active_only=True)

            folder_field.choices = [
                ("", "No folder selected")
            ] + [
                (
                    str(folder.id),
                    getattr(
                        folder,
                        "name",
                        f"Folder #{folder.id}",
                    ),
                )
                for folder in folders
            ]

        except Exception:
            folder_field.choices = [
                ("", "No folder selected")
            ]

            current_app.logger.exception(
                "Could not load Media Library folders for Safari forms."
            )

    try:
        if restrict_to_folder and folder_id is not None:
            assets = get_cms_media_assets(
                folder_id=folder_id,
                include_descendants=True,
                active_only=True,
            ) or []
        else:
            assets = get_cms_media_assets(
                folder_id=None,
                include_descendants=True,
                active_only=True,
            ) or []

    except Exception:
        assets = []

        current_app.logger.exception(
            "Could not load Media Library assets for Safari forms."
        )

        flash(
            "Media Library assets could not be loaded. "
            "Check the media library configuration.",
            "warning",
        )

    asset_choices = [
        (
            "",
            "Select an existing media asset",
        )
    ]

    for asset in assets:
        label = (
            getattr(asset, "title", None)
            or getattr(asset, "original_filename", None)
            or getattr(asset, "filename", None)
            or f"Media asset #{asset.id}"
        )

        asset_choices.append(
            (
                str(asset.id),
                label,
            )
        )

    for field_name in (
        "card_media_asset_id",
        "hero_media_asset_id",
        "media_asset_id",
    ):
        field = getattr(form, field_name, None)

        if field is not None:
            field.choices = asset_choices

    return assets

def _populate_property_choices(form):
    field = getattr(form, "property_id", None)

    if field is not None:
        properties = list_properties(include_inactive=True)
        field.choices = [
            ("", "Select a safari property")
        ] + [
            (str(prop.id), prop.name)
            for prop in properties
        ]

def _populate_package_choices(form, property_obj=None):
    field = getattr(form, "package_option_id", None)

    if field is not None:
        options = (
            list_package_options(
                property_obj.id,
                include_inactive=True,
            )
            if property_obj
            else []
        )

        field.choices = [
            ("", "Select a package option")
        ] + [
            (
                str(option.id),
                f"{option.name} — "
                f"{option.duration_days} days / "
                f"{option.duration_nights} nights",
            )
            for option in options
        ]

def _coerce_optional_int(value):
    """Allow blank optional integer dropdowns without raising ValueError."""
    if value is None or value == "":
        return None
    return int(value)

def _save_error(message="The record could not be saved."):
    flash(message, "danger")

# ============================================================
# SAFARI DESTINATION INDEX
# ============================================================
@admin_safari_bp.route("/")
@permission_required(MANAGE_SAFARIS)
def index():
    all_destinations = list_destinations(include_inactive=True)

    # Calculate the summary from the full destination catalogue.
    destination_count = len(all_destinations)
    active_destination_count = sum(
        1 for item in all_destinations if item.active
    )
    inactive_destination_count = (
        destination_count - active_destination_count
    )
    featured_destination_count = sum(
        1 for item in all_destinations
        if getattr(item, "featured", False)
    )

    # Search and status filters.
    search = request.args.get("search", "").strip()
    active_filter = request.args.get("status", "all").strip().lower()

    destinations = all_destinations

    if search:
        search_lower = search.casefold()
        destinations = [
            item for item in destinations
            if search_lower in (item.name or "").casefold()
            or search_lower in (item.slug or "").casefold()
            or search_lower in (
                getattr(item, "description", "") or ""
            ).casefold()
        ]

    if active_filter == "active":
        destinations = [
            item for item in destinations if item.active
        ]
    elif active_filter == "inactive":
        destinations = [
            item for item in destinations if not item.active
        ]

    destinations.sort(
        key=lambda item: (
            getattr(item, "display_order", None)
            if getattr(item, "display_order", None) is not None
            else getattr(item, "sort_order", None)
            if getattr(item, "sort_order", None) is not None
            else getattr(item, "order", 0) or 0,
            (item.name or "").casefold(),
        )
    )

    return render_template(
        "admin/safaris/index.html",
        destinations=destinations,
        search=search,
        active_filter=active_filter,
        destination_count=destination_count,
        active_destination_count=active_destination_count,
        inactive_destination_count=inactive_destination_count,
        featured_destination_count=featured_destination_count,
    )

# ============================================================
# DESTINATIONS
# ============================================================
@admin_safari_bp.route("/destinations")
@permission_required(MANAGE_SAFARIS)
def destinations():
    items = list_destinations(include_inactive=True)

    return render_template(
        "admin/safaris/destinations/index.html",
        destinations=items,
    )

@admin_safari_bp.route("/destinations/new", methods=["GET", "POST"])
@permission_required(MANAGE_SAFARIS)
def destination_create():
    """Create a safari destination."""
    form = SafariDestinationForm()

    # Safari destinations must use the dedicated Safaris DAM tree.
    _populate_safari_destination_media_choices(form)
    if form.validate_on_submit():
        try:
            destination = save_destination(form)

            if destination:
                flash(
                    "Safari destination created successfully.",
                    "success",
                )
                return redirect(
                    url_for(
                        "admin_safaris.destination_detail",
                        destination_id=destination.id,
                    )
                )

            _save_error()

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to create safari destination."
            )
            _save_error()

    return render_template(
        "admin/safaris/destinations/form.html",
        form=form,
        destination=None,
        page_title="Create Safari Destination",
    )

@admin_safari_bp.route("/destinations/<int:destination_id>/edit",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def destination_edit(destination_id):
    destination = _get_or_404(
        get_destination,
        destination_id,
    )

    form = SafariDestinationForm(obj=destination)

    # Safari destinations use only the Safaris Media Library tree.
    _populate_safari_destination_media_choices(form)

    if form.validate_on_submit():
        try:
            saved = save_destination(
                form,
                destination,
            )

            if saved:
                flash(
                    "Safari destination updated successfully.",
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_safaris.destination_edit",
                        destination_id=destination.id,
                    )
                )

            _save_error()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to update safari destination."
            )

            _save_error()

    return render_template(
        "admin/safaris/destinations/form.html",
        form=form,
        destination=destination,
        page_title="Edit Safari Destination",)

@admin_safari_bp.route("/destinations/media-assets",methods=["GET"],)
def destination_media_assets():
    """
    Return active media assets belonging ONLY to the
    selected Safari Media Library folder.

    Descendant folders are deliberately excluded.
    """

    folder_id = request.args.get(
        "folder_id",
        type=int,
    )

    if folder_id is None:
        return {
            "success": False,
            "message": "A Safari media folder is required.",
            "assets": [],
        }, 400

    try:
        folders = get_media_folders(
            active_only=True
        ) or []

        safaris_root = _get_safaris_root_folder(
            folders
        )

        if safaris_root is None:
            return {
                "success": False,
                "message": "The Safaris Media Library folder is not configured.",
                "assets": [],
            }, 404

        safari_folder_ids = _get_descendant_folder_ids(
            folders,
            safaris_root.id,
        )

        # Security/data-integrity check:
        # never allow the endpoint to fetch assets from
        # a folder outside the Safaris tree.
        if folder_id not in safari_folder_ids:
            return {
                "success": False,
                "message": "The selected folder is not part of the Safaris Media Library.",
                "assets": [],
            }, 400

        selected_folder = next(
            (
                folder
                for folder in folders
                if folder.id == folder_id
            ),
            None,
        )

        if selected_folder is None:
            return {
                "success": False,
                "message": "The selected Safari media folder could not be found.",
                "assets": [],
            }, 404

        folder_paths = _build_media_folder_paths(
            [
                folder
                for folder in folders
                if folder.id in safari_folder_ids
            ]
        )

        folder_path = folder_paths.get(
            folder_id,
            _get_folder_name(selected_folder),
        )

        # IMPORTANT:
        # Exact folder only. No descendants.
        assets = get_cms_media_assets(
            folder_id=folder_id,
            include_descendants=False,
            active_only=True,
        ) or []

        payload = []

        for asset in assets:
            asset_name = (
                getattr(asset, "title", None)
                or getattr(
                    asset,
                    "original_filename",
                    None,
                )
                or getattr(
                    asset,
                    "filename",
                    None,
                )
                or f"Media asset #{asset.id}"
            )

            payload.append(
                {
                    "id": asset.id,
                    "label": (
                        f"{folder_path} / "
                        f"{asset_name}"
                    ),
                }
            )

        return {
            "success": True,
            "folder_id": folder_id,
            "folder_path": folder_path,
            "assets": payload,
        }

    except Exception:
        current_app.logger.exception(
            "Failed to load Safari destination media assets "
            "for folder ID %s.",
            folder_id,
        )

        return {
            "success": False,
            "message": "Safari media assets could not be loaded.",
            "assets": [],
        }, 500

# ============================================================
# SAFARI DESTINATION DETAIL WORKSPACE
# ============================================================
@admin_safari_bp.route("/destinations/<int:destination_id>")
def destination_detail(destination_id):
    destination = _get_or_404(get_destination, destination_id)

    # Only show properties belonging to this destination.
    properties = list_properties(
        destination_id=destination.id,
        include_inactive=True,
    )

    property_ids = [prop.id for prop in properties]

    # Gather package options and their nested operational records.
    packages_by_property = {}
    property_media_by_property = {}
    itinerary_count = 0
    rate_count = 0
    package_count = 0
    media_count = 0

    for prop in properties:
        media_items = list_property_media(
            prop.id,
            include_inactive=True,
        )
        property_media_by_property[prop.id] = media_items
        media_count += len(media_items)

        package_options = list_package_options(
            prop.id,
            include_inactive=True,
        )
        packages_by_property[prop.id] = package_options
        package_count += len(package_options)

        for option in package_options:
            itinerary_count += len(list_itinerary_days(option.id))
            rate_count += len(
                list_rates(option.id, include_inactive=True)
            )

    # Count enquiries connected to this destination.
    inquiry_count = SafariInquiry.query.filter_by(
        destination_id=destination.id
    ).count()

    new_inquiry_count = SafariInquiry.query.filter_by(
        destination_id=destination.id,
        status="new",
    ).count()

    # Connect this destination to the existing Page Heroes CMS.
    hero_page_key = f"safari_destination_{destination.slug}"
    page_hero = PageHero.query.filter_by(
        page_key=hero_page_key
    ).first()

    # Use the configured Page Hero image first, then fall back
    # to the destination's existing DAM hero/card media.
    hero_image_url = None

    if page_hero and page_hero.active:
        hero_image_url = (
                page_hero.desktop_image_url
                or page_hero.mobile_image_url
        )

    if not hero_image_url:
        hero_asset = getattr(
            destination, "hero_media_asset", None
        )
        if hero_asset is None:
            hero_asset = getattr(destination, "hero_asset", None)

        card_asset = getattr(
            destination, "card_media_asset", None
        )
        if hero_asset is None:
            hero_asset = card_asset

        hero_image_url = (
            getattr(hero_asset, "browser_url", None)
            if hero_asset else None
        )

    return render_template(
        "admin/safaris/destinations/destination_detail.html",
        destination=destination,
        page_hero=page_hero,
        hero_page_key=hero_page_key,
        properties=properties,
        packages_by_property=packages_by_property,
        property_media_by_property=property_media_by_property,
        property_count=len(properties),
        package_count=package_count,
        media_count=media_count,
        itinerary_count=itinerary_count,
        rate_count=rate_count,
        inquiry_count=inquiry_count,
        new_inquiry_count=new_inquiry_count,
        hero_image_url=hero_image_url,
    )

@admin_safari_bp.route("/destinations/<int:destination_id>/toggle",methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def destination_toggle(destination_id):
    destination = _get_or_404(get_destination, destination_id)

    try:
        set_destination_active(destination, not destination.active)
        db.session.commit()

        flash(
            f"{destination.name} has been "
            f"{'activated' if destination.active else 'deactivated'}.",
            "success",
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to toggle safari destination status."
        )
        flash("Unable to update destination status.", "danger")

    return redirect(url_for("admin_safaris.index"))

# ============================================================
# PROPERTIES
# ============================================================
def _populate_safari_property_media_choices(form):
    """
    Populate the Safari property media-folder selector.

    Property forms use the Safari Media Library tree only.
    The property gallery itself can later resolve descendant
    assets from the selected property folder.
    """

    folder_field = getattr(
        form,
        "media_folder_id",
        None,
    )

    if folder_field is None:
        return

    folder_field.coerce = _coerce_optional_int

    try:
        folders = get_media_folders(
            active_only=True,
        ) or []

        safari_root = _get_safaris_root_folder(
            folders
        )

        if safari_root is None:
            folder_field.choices = [
                (
                    "",
                    "No folder selected",
                )
            ]

            current_app.logger.warning(
                "Safari Media Library root folder could not be found."
            )

            return

        safari_folder_ids = _get_descendant_folder_ids(
            folders,
            safari_root.id,
        )

        safari_folders = [
            folder
            for folder in folders
            if folder.id in safari_folder_ids
        ]

        folder_paths = _build_media_folder_paths(
            safari_folders
        )

        safari_folders.sort(
            key=lambda folder: (
                folder_paths.get(
                    folder.id,
                    getattr(
                        folder,
                        "name",
                        "",
                    ),
                ).casefold()
            )
        )

        folder_field.choices = [
            (
                "",
                "No folder selected",
            )
        ]

        for folder in safari_folders:
            folder_field.choices.append(
                (
                    str(folder.id),
                    folder_paths.get(
                        folder.id,
                        getattr(
                            folder,
                            "name",
                            f"Folder #{folder.id}",
                        ),
                    ),
                )
            )

    except Exception:
        folder_field.choices = [
            (
                "",
                "No folder selected",)]

        current_app.logger.exception(
            "Could not load Safari Media Library folders "
            "for the Safari property form.")

@admin_safari_bp.route("/properties")
@permission_required(MANAGE_SAFARIS)
def properties():
    destination_id = request.args.get("destination_id", type=int)

    items = list_properties(
        destination_id=destination_id,
        include_inactive=True,
    )

    return render_template(
        "admin/safaris/properties/index.html",
        properties=items,
        destinations=list_destinations(include_inactive=True),
        selected_destination_id=destination_id,
    )

@admin_safari_bp.route("/properties/new",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def property_create():
    """
    Create a Safari property inside a specific Safari destination.

    The destination is intentionally contextual. This route does NOT
    load all Safari destinations into the property form.
    """

    destination_id = request.args.get(
        "destination_id",
        type=int,
    )

    # On POST, preserve the destination from the submitted form.
    if request.method == "POST":
        submitted_destination_id = request.form.get(
            "destination_id",
            type=int,
        )

        if submitted_destination_id is not None:
            destination_id = submitted_destination_id

    # A property must belong to a specific Safari destination.
    if destination_id is None:
        flash(
            "A Safari destination must be selected before creating a property.",
            "warning",
        )
        return redirect(
            url_for("admin_safaris.properties")
        )

    destination = _get_or_404(
        get_destination,
        destination_id,
    )

    form = SafariPropertyForm()

    # --------------------------------------------------------
    # Destination context
    # --------------------------------------------------------
    #
    # Do NOT populate every Safari destination here.
    # The property belongs to the destination that opened this
    # form, so only that destination is available.
    #
    destination_field = getattr(
        form,
        "destination_id",
        None,
    )

    if destination_field is not None:
        destination_field.coerce = _coerce_optional_int
        destination_field.choices = [
            (
                str(destination.id),
                destination.name,
            )
        ]

        if not form.is_submitted():
            destination_field.data = destination.id

    # --------------------------------------------------------
    # Safari Media Library
    # --------------------------------------------------------
    _populate_safari_property_media_choices(form)

    if form.validate_on_submit():

        # Security/data-integrity check:
        # never allow the submitted destination to differ
        # from the destination that owns this form.
        submitted_destination_id = form.destination_id.data

        if submitted_destination_id != destination.id:
            flash(
                "The property destination could not be changed from "
                "the selected Safari destination.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_safaris.property_create",
                    destination_id=destination.id,
                )
            )

        try:
            prop = save_property(form)

            if prop:
                flash(
                    "Safari property created successfully.",
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_safaris.property_detail",
                        property_id=prop.id,
                    )
                )

            _save_error()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to create safari property."
            )

            _save_error()

    return render_template(
        "admin/safaris/properties/form.html",
        form=form,
        property=None,
        destination=destination,
        page_title=f"Add Property · {destination.name}",
    )


@admin_safari_bp.route("/properties/<int:property_id>/edit",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def property_edit(property_id):
    """
    Edit an existing Safari property.

    The property's existing destination is the only destination
    context available to the form. It is not replaced with a
    global destination selector.
    """

    prop = _get_or_404(
        get_property,
        property_id,
    )

    destination = getattr(
        prop,
        "destination",
        None,
    )

    # Fall back to the foreign-key relationship if necessary.
    if destination is None and getattr(prop, "destination_id", None):
        destination = _get_or_404(
            get_destination,
            prop.destination_id,
        )

    if destination is None:
        flash(
            "This Safari property is not connected to a valid destination.",
            "danger",
        )
        return redirect(
            url_for("admin_safaris.properties")
        )

    form = SafariPropertyForm(obj=prop)

    # --------------------------------------------------------
    # Destination context
    # --------------------------------------------------------
    #
    # Only the property's current destination is supplied.
    # There is deliberately no list_destinations() call here.
    #
    destination_field = getattr(
        form,
        "destination_id",
        None,
    )

    if destination_field is not None:
        destination_field.coerce = _coerce_optional_int
        destination_field.choices = [
            (
                str(destination.id),
                destination.name,
            )
        ]

        if not form.is_submitted():
            destination_field.data = destination.id

    # --------------------------------------------------------
    # Safari Media Library
    # --------------------------------------------------------
    _populate_safari_property_media_choices(form)

    if form.validate_on_submit():

        submitted_destination_id = form.destination_id.data

        # A property's destination is fixed by its current
        # catalogue relationship. Do not allow an edit form
        # to silently move it to another destination.
        if submitted_destination_id != destination.id:
            flash(
                "The property's Safari destination cannot be changed "
                "from the property editor.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_safaris.property_edit",
                    property_id=prop.id,
                )
            )

        try:
            saved = save_property(
                form,
                prop,
            )

            if saved:
                flash(
                    "Safari property updated successfully.",
                    "success",
                )

                return redirect(
                    url_for(
                        "admin_safaris.property_detail",
                        property_id=prop.id,
                    )
                )

            _save_error()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to update safari property."
            )

            _save_error()

    return render_template(
        "admin/safaris/properties/form.html",
        form=form,
        property=prop,
        destination=destination,
        page_title=f"Edit Property · {destination.name}",
    )

# ============================================================
# SAFARI PROPERTY DETAIL WORKSPACE
# ============================================================
@admin_safari_bp.route("/properties/<int:property_id>")
@permission_required(MANAGE_SAFARIS)
def property_detail(property_id):
    """Central management workspace for a safari property."""

    prop = _get_or_404(get_property, property_id)

    # Load all packages and media, including inactive records,
    # so administrators can manage the complete property catalogue.
    media_items = list_property_media(
        prop.id,
        include_inactive=True,
    )

    package_options = list_package_options(
        prop.id,
        include_inactive=True,
    )

    packages_by_property = {prop.id: package_options}
    itinerary_days_by_package = {}
    rates_by_package = {}

    itinerary_count = 0
    rate_count = 0

    for option in package_options:
        days = list_itinerary_days(option.id)
        rates = list_rates(
            option.id,
            include_inactive=True,
        )

        itinerary_days_by_package[option.id] = days
        rates_by_package[option.id] = rates

        itinerary_count += len(days)
        rate_count += len(rates)

    # Choose a suitable gallery image for the workspace header.
    # Prefer an active primary image, then an active hero image,
    # then the first active image with a usable DAM URL.
    active_media = [
        item for item in media_items
        if getattr(item, "active", True)
        and getattr(item, "media_asset", None)
    ]

    hero_media = next(
        (
            item for item in active_media
            if getattr(item, "is_primary", False)
        ),
        None,
    )

    if hero_media is None:
        hero_media = next(
            (
                item for item in active_media
                if getattr(item, "usage", "") == "hero"
            ),
            None,
        )

    if hero_media is None and active_media:
        hero_media = active_media[0]

    hero_image_url = None
    if hero_media and hero_media.media_asset:
        hero_image_url = (
            getattr(hero_media.media_asset, "browser_url", None)
            or getattr(hero_media.media_asset, "file_url", None)
            or getattr(hero_media.media_asset, "file_path", None)
        )

    # Enquiries associated with this property.
    inquiry_count = SafariInquiry.query.filter_by(
        property_id=prop.id
    ).count()

    new_inquiry_count = SafariInquiry.query.filter_by(
        property_id=prop.id,
        status="new",
    ).count()

    return render_template(
        "admin/safaris/properties/detail.html",
        property=prop,
        properties=[prop],
        media_items=media_items,
        hero_image_url=hero_image_url,
        packages_by_property=packages_by_property,
        property_media_by_property={prop.id: media_items},
        itinerary_days_by_package=itinerary_days_by_package,
        rates_by_package=rates_by_package,
        property_count=1,
        package_count=len(package_options),
        media_count=len(media_items),
        itinerary_count=itinerary_count,
        rate_count=rate_count,
        inquiry_count=inquiry_count,
        new_inquiry_count=new_inquiry_count,
    )

@admin_safari_bp.route("/properties/<int:property_id>/toggle",methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def property_toggle(property_id):
    prop = _get_or_404(get_property, property_id)

    try:
        set_property_active(prop, not prop.active)
        flash("Property status updated.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to update property status.", "danger")

    return redirect(url_for("admin_safaris.properties"))

# ============================================================
# PROPERTY MEDIA / GALLERY
# Supports both the global media library and property-specific views.
# ============================================================
@admin_safari_bp.route("/media",defaults={"property_id": None},methods=["GET"],)
@admin_safari_bp.route("/properties/<int:property_id>/media",methods=["GET"],)
@permission_required(MANAGE_SAFARIS)
def property_media(property_id=None):
    # Load properties for the filter dropdown.
    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    # A property can be supplied through the URL or index filter.
    filter_id = property_id

    if filter_id is None:
        filter_id = request.args.get("property_id", type=int)

    selected_property = None

    if filter_id is not None:
        selected_property = _get_or_404(get_property, filter_id)
        media_items = list_property_media(
            selected_property.id,
            include_inactive=True,
        )
    else:
        media_items = (
            SafariPropertyMedia.query
            .order_by(
                SafariPropertyMedia.display_order.asc(),
                SafariPropertyMedia.id.desc(),
            )
            .all()
        )

    return render_template(
        "admin/safaris/media/index.html",
        property=selected_property,
        selected_property=selected_property,
        properties=properties,
        media_items=media_items,
    )

@admin_safari_bp.route(
    "/media/new",
    defaults={"property_id": None},
    methods=["GET", "POST"],)
@admin_safari_bp.route(
    "/properties/<int:property_id>/media/new",
    methods=["GET", "POST"],)
def property_media_create(property_id=None):
    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    form = SafariPropertyMediaForm()
    selected_property = None

    # Resolve the property from the URL or submitted dropdown.
    selected_id = (
        request.form.get("property_id", type=int)
        if request.method == "POST"
        else property_id
    )

    if selected_id is not None:
        selected_property = _get_or_404(get_property, selected_id)

    # Only show assets belonging to this property's assigned folder.
    media_assets = _populate_media_choices(
        form,
        folder_id=(
            selected_property.media_folder_id
            if selected_property
            else None
        ),
        restrict_to_folder=selected_property is not None,
    )
    if form.validate_on_submit():
        if selected_property is None:
            flash("Please select a property.", "error")
        else:
            try:
                # Verify the selected asset belongs to the property's folder
                # (or one of its descendants).
                asset_id = form.media_asset_id.data

                allowed_assets = get_cms_media_assets(
                    folder_id=selected_property.media_folder_id,
                    include_descendants=True,
                    active_only=True,
                ) or []

                allowed_asset_ids = {
                    asset.id for asset in allowed_assets
                }

                if (
                    selected_property.media_folder_id is None
                    or asset_id not in allowed_asset_ids
                ):
                    flash(
                        "Choose an active media asset from this property's "
                        "assigned Media Library folder.",
                        "error",
                    )
                else:
                    item = save_property_media(
                        selected_property,
                        form,
                    )

                    if item:
                        flash(
                            "Property media added successfully.",
                            "success",
                        )
                        return redirect(
                            url_for(
                                "admin_safaris.property_media",
                                property_id=selected_property.id,
                            )
                        )

                    _save_error()

            except Exception:
                db.session.rollback()
                current_app.logger.exception(
                    "Failed to add safari property media."
                )
                _save_error()

    return render_template(
        "admin/safaris/media/form.html",
        form=form,
        properties=properties,
        property=selected_property,
        selected_property=selected_property,
        media_item=None,
        media_assets=media_assets,
        page_title="Attach Property Media",
    )


@admin_safari_bp.route(
    "/properties/<int:property_id>/media/<int:media_id>/edit",
    methods=["GET", "POST"],
)
def property_media_edit(property_id, media_id):
    prop = _get_or_404(get_property, property_id)

    media_item = SafariPropertyMedia.query.filter_by(
        id=media_id,
        property_id=prop.id,
    ).first_or_404()

    form = SafariPropertyMediaForm(obj=media_item)

    # Populate assets only from this property's assigned media folder.
    media_assets = _populate_media_choices(
        form,
        folder_id=prop.media_folder_id,
        restrict_to_folder=True,
    )

    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    if form.validate_on_submit():
        try:
            asset_id = form.media_asset_id.data

            allowed_assets = []
            if prop.media_folder_id is not None:
                allowed_assets = get_cms_media_assets(
                    folder_id=prop.media_folder_id,
                    include_descendants=True,
                    active_only=True,
                ) or []

            allowed_asset_ids = {
                asset.id for asset in allowed_assets
            }

            if (
                prop.media_folder_id is None
                or asset_id not in allowed_asset_ids
            ):
                flash(
                    "Choose an active media asset from this property's "
                    "assigned Media Library folder.",
                    "error",
                )
            else:
                saved = save_property_media(
                    prop,
                    form,
                    media_item,
                )

                if saved:
                    flash(
                        "Property media updated successfully.",
                        "success",
                    )
                    return redirect(
                        url_for(
                            "admin_safaris.property_media",
                            property_id=prop.id,
                        )
                    )

                _save_error()

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update safari property media."
            )
            _save_error()

    return render_template(
        "admin/safaris/media/form.html",
        form=form,
        properties=properties,
        property=prop,
        selected_property=prop,
        media_item=media_item,
        media_assets=media_assets,
        page_title="Edit Property Media",
    )

@admin_safari_bp.route("/properties/<int:property_id>/media/<int:media_id>/delete",methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def property_media_delete(property_id, media_id):
    prop = _get_or_404(get_property, property_id)

    media_item = SafariPropertyMedia.query.filter_by(
        id=media_id,
        property_id=prop.id,
    ).first_or_404()

    try:
        delete_property_media(media_item)
        flash("Property media removed.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to remove property media.", "danger")

    return redirect(
        url_for(
            "admin_safaris.property_media",
            property_id=prop.id,))

# ============================================================
# PACKAGE OPTIONS / DURATIONS
# Supports global and property-specific package management.
# ============================================================
@admin_safari_bp.route(
    "/packages",
    defaults={"property_id": None},
    methods=["GET"],
)
@admin_safari_bp.route(
    "/properties/<int:property_id>/packages",
    methods=["GET"],
)
def packages(property_id=None):
    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    # The URL takes precedence; the global page can use a GET filter.
    selected_id = property_id
    if selected_id is None:
        selected_id = request.args.get("property_id", type=int)

    selected_property = (
        _get_or_404(get_property, selected_id)
        if selected_id is not None
        else None
    )

    if selected_property:
        options = list_package_options(
            selected_property.id,
            include_inactive=True,
        )
    else:
        options = (
            SafariPackageOption.query
            .order_by(SafariPackageOption.order.asc(),
                      SafariPackageOption.id.desc())
            .all()
        )

    return render_template(
        "admin/safaris/packages/index.html",
        properties=properties,
        property=selected_property,
        selected_property=selected_property,
        packages=options,
        package_options=options,
    )


@admin_safari_bp.route(
    "/packages/new",
    defaults={"property_id": None},
    methods=["GET", "POST"],
)
@admin_safari_bp.route(
    "/properties/<int:property_id>/packages/new",
    methods=["GET", "POST"],
)
def package_create(property_id=None):
    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    form = SafariPackageOptionForm()

    # Populate the property field before WTForms validates the form.
    property_field = getattr(form, "property_id", None)
    if property_field is not None:
        property_field.choices = [
            ("", "Select a property"),
        ] + [
            (
                str(item.id),
                f"{item.name}"
                + (
                    f" — {item.destination.name}"
                    if item.destination
                    else ""
                ),
            )
            for item in properties
        ]

    selected_id = property_id
    if request.method == "POST":
        selected_id = (
            request.form.get("property_id", type=int)
            or property_id
        )

    selected_property = (
        _get_or_404(get_property, selected_id)
        if selected_id is not None
        else None
    )

    if property_field is not None and selected_property:
        if not form.is_submitted():
            property_field.data = selected_property.id

    if form.validate_on_submit():
        # Resolve the property from the submitted selection.
        submitted_id = request.form.get("property_id", type=int)
        target_id = submitted_id or property_id

        if target_id is None:
            flash("Please select a safari property.", "error")
        else:
            try:
                target_property = _get_or_404(
                    get_property,
                    target_id,
                )

                option = save_package_option(
                    target_property,
                    form,
                )

                if option:
                    flash(
                        "Safari package option created successfully.",
                        "success",
                    )
                    return redirect(
                        url_for(
                            "admin_safaris.packages",
                            property_id=target_property.id,
                            option_id=option.id,
                        )
                    )

                _save_error()

            except Exception:
                db.session.rollback()
                current_app.logger.exception(
                    "Failed to create safari package option."
                )
                _save_error()

    return render_template(
        "admin/safaris/packages/form.html",
        form=form,
        properties=properties,
        property=selected_property,
        selected_property=selected_property,
        package=None,
        option=None,
        page_title="Create Package Option",
    )


@admin_safari_bp.route(
    "/properties/<int:property_id>/packages/"
    "<int:option_id>/edit",
    methods=["GET", "POST"],
)
def package_edit(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    properties = SafariProperty.query.order_by(
        SafariProperty.name.asc()
    ).all()

    form = SafariPackageOptionForm(obj=option)

    property_field = getattr(form, "property_id", None)
    if property_field is not None:
        property_field.choices = [
            ("", "Select a property"),
        ] + [
            (
                str(item.id),
                f"{item.name}"
                + (
                    f" — {item.destination.name}"
                    if item.destination
                    else ""
                ),
            )
            for item in properties
        ]

        if not form.is_submitted():
            property_field.data = prop.id

    selected_property = prop
    if request.method == "POST":
        submitted_id = request.form.get("property_id", type=int)
        if submitted_id is not None:
            selected_property = _get_or_404(
                get_property,
                submitted_id,
            )

    if form.validate_on_submit():
        target_id = (
            request.form.get("property_id", type=int)
            or property_id
        )

        try:
            target_property = _get_or_404(
                get_property,
                target_id,
            )

            saved = save_package_option(
                target_property,
                form,
                option,
            )

            if saved:
                flash(
                    "Package option updated successfully.",
                    "success",
                )
                return redirect(
                    url_for(
                        "admin_safaris.packages",
                        property_id=target_property.id,
                        option_id=option.id,
                    )
                )

            _save_error()

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update safari package option."
            )
            _save_error()

    return render_template(
        "admin/safaris/packages/form.html",
        form=form,
        properties=properties,
        property=selected_property,
        selected_property=selected_property,
        package=option,
        option=option,
        page_title="Edit Package Option",
    )

@admin_safari_bp.route(
    "/properties/<int:property_id>/packages/"
    "<int:option_id>/toggle",
    methods=["POST"],)
def package_toggle(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    try:
        set_package_option_active(
            option,
            not option.active,
        )
        flash("Package status updated successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to update safari package status."
        )
        flash("Unable to update package status.", "error")

    return redirect(
        url_for(
            "admin_safaris.packages",
            property_id=prop.id,
        )
    )

# ============================================================
# ITINERARY DAYS
# ============================================================
@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/itinerary",)
@permission_required(MANAGE_SAFARIS)
def itinerary(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    days = list_itinerary_days(option.id)

    return render_template(
        "admin/safaris/itinerary/index.html",
        property=prop,
        option=option,
        itinerary_days=days,
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/itinerary/new",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def itinerary_create(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    form = SafariItineraryDayForm()
    if hasattr(form, "package_option_id"):
        form.package_option_id.choices = [(option.id, option.name)]
        form.package_option_id.data = option.id

    if form.validate_on_submit():
        try:
            day = save_itinerary_day(option, form)

            if day:
                flash("Itinerary day added.", "success")
                return redirect(
                    url_for(
                        "admin_safaris.itinerary",
                        property_id=prop.id,
                        option_id=option.id,
                    )
                )

            _save_error()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to add safari itinerary day."
            )
            _save_error()

    return render_template(
        "admin/safaris/itinerary/form.html",
        form=form,
        property=prop,
        option=option,
        itinerary_day=None,
        page_title="Add Itinerary Day",
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/itinerary/<int:day_id>/edit",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def itinerary_edit(property_id, option_id, day_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    day = SafariItineraryDay.query.filter_by(
        id=day_id,
        package_option_id=option.id,
    ).first_or_404()

    form = SafariItineraryDayForm(obj=day)
    if hasattr(form, "package_option_id"):
        form.package_option_id.choices = [(option.id, option.name)]
        form.package_option_id.data = option.id

    if form.validate_on_submit():
        try:
            saved = save_itinerary_day(option, form, day)

            if saved:
                flash("Itinerary day updated.", "success")
                return redirect(
                    url_for(
                        "admin_safaris.itinerary",
                        property_id=prop.id,
                        option_id=option.id,
                    )
                )

            _save_error()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update safari itinerary day."
            )
            _save_error()

    return render_template(
        "admin/safaris/itinerary/form.html",
        form=form,
        property=prop,
        option=option,
        itinerary_day=day,
        page_title="Edit Itinerary Day",
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/itinerary/<int:day_id>/delete",methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def itinerary_delete(property_id, option_id, day_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    day = SafariItineraryDay.query.filter_by(
        id=day_id,
        package_option_id=option.id,
    ).first_or_404()

    try:
        delete_itinerary_day(day)
        flash("Itinerary day removed.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to remove itinerary day.", "danger")

    return redirect(
        url_for(
            "admin_safaris.itinerary",
            property_id=prop.id,
            option_id=option.id,
        )
    )


# ============================================================
# TOGGLE ITINERARY DAY STATUS
# ============================================================
@admin_safari_bp.route(
    "/properties/<int:property_id>/packages/<int:option_id>/itinerary/<int:day_id>/toggle",
    methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def itinerary_day_toggle(property_id, option_id, day_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    day = SafariItineraryDay.query.filter_by(
        id=day_id,
        package_option_id=option.id,
    ).first_or_404()

    try:
        day.active = not day.active
        db.session.commit()

        status = "activated" if day.active else "deactivated"
        flash(
            f"Day {day.day_number} has been {status}.",
            "success",
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to toggle safari itinerary day status."
        )
        flash(
            "Unable to update the itinerary day status.",
            "danger",
        )

    return redirect(
        url_for(
            "admin_safaris.itinerary",
            property_id=prop.id,
            option_id=option.id,
        )
    )

# ============================================================
# PACKAGE RATES
# ============================================================
@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/rates",)
@permission_required(MANAGE_SAFARIS)
def rates(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    return render_template(
        "admin/safaris/rates/index.html",
        property=prop,
        option=option,
        rates=list_rates(option.id, include_inactive=True),
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/rates/new",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def rate_create(property_id, option_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    form = SafariPackageRateForm()

    if form.validate_on_submit():
        try:
            rate = save_rate(option, form)

            if rate:
                flash("Package rate created successfully.", "success")
                return redirect(
                    url_for(
                        "admin_safaris.rates",
                        property_id=prop.id,
                        option_id=option.id,
                    )
                )

            _save_error()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to create safari package rate."
            )
            _save_error()

    return render_template(
        "admin/safaris/rates/form.html",
        form=form,
        property=prop,
        option=option,
        rate=None,
        page_title="Create Package Rate",
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/<int:option_id>/rates/<int:rate_id>/edit",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def rate_edit(property_id, option_id, rate_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    rate = SafariPackageRate.query.filter_by(
        id=rate_id,
        package_option_id=option.id,
    ).first_or_404()

    form = SafariPackageRateForm(obj=rate)

    if form.validate_on_submit():
        try:
            saved = save_rate(option, form, rate)

            if saved:
                flash("Package rate updated successfully.", "success")
                return redirect(
                    url_for(
                        "admin_safaris.rates",
                        property_id=prop.id,
                        option_id=option.id,
                    )
                )

            _save_error()
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update safari package rate."
            )
            _save_error()

    return render_template(
        "admin/safaris/rates/form.html",
        form=form,
        property=prop,
        option=option,
        rate=rate,
        page_title="Edit Package Rate",
    )

@admin_safari_bp.route("/properties/<int:property_id>/packages/""<int:option_id>/rates/<int:rate_id>/toggle",methods=["POST"],)
@permission_required(MANAGE_SAFARIS)
def rate_toggle(property_id, option_id, rate_id):
    prop = _get_or_404(get_property, property_id)
    option = _get_or_404(get_package_option, option_id)

    if option.property_id != prop.id:
        abort(404)

    rate = SafariPackageRate.query.filter_by(
        id=rate_id,
        package_option_id=option.id,
    ).first_or_404()

    try:
        new_status = not rate.active
        set_rate_active(rate, new_status)

        flash(
            "Rate activated successfully."
            if new_status
            else "Rate deactivated successfully.",
            "success",
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to toggle safari rate status."
        )
        flash("Unable to update rate status. Please try again.", "danger")

    return redirect(
        url_for(
            "admin_safaris.rates",
            property_id=prop.id,
            option_id=option.id,
        )
    )

# ============================================================
# SAFARI INQUIRIES
# ============================================================
@admin_safari_bp.route("/inquiries")
def inquiries():
    status = request.args.get("status", "").strip()
    destination_id = request.args.get("destination_id", type=int)

    query = SafariInquiry.query

    if status:
        query = query.filter_by(status=status)

    if destination_id:
        query = query.filter_by(destination_id=destination_id)

    items = query.order_by(
        desc(SafariInquiry.created_at)
    ).all()

    return render_template(
        "admin/safaris/inquiries/index.html",
        inquiries=items,
        selected_status=status,
        selected_destination_id=destination_id,
    )

@admin_safari_bp.route("/inquiries/<int:inquiry_id>",methods=["GET", "POST"],)
@permission_required(MANAGE_SAFARIS)
def inquiry_detail(inquiry_id):
    inquiry = SafariInquiry.query.get_or_404(inquiry_id)

    allowed_statuses = {
        "new",
        "contacted",
        "quoting",
        "quoted",
        "confirmed",
        "declined",
        "closed",
    }

    if request.method == "POST":
        new_status = request.form.get("status", "").strip()
        internal_notes = request.form.get("internal_notes", "").strip()

        if new_status not in allowed_statuses:
            flash("Please select a valid inquiry status.", "danger")
        else:
            try:
                inquiry.status = new_status
                inquiry.internal_notes = internal_notes or None
                db.session.commit()
                flash("Safari inquiry updated.", "success")
                return redirect(
                    url_for(
                        "admin_safaris.inquiry_detail",
                        inquiry_id=inquiry.id,
                    )
                )
            except Exception:
                db.session.rollback()
                current_app.logger.exception(
                    "Failed to update safari inquiry."
                )
                flash("Unable to update safari inquiry.", "danger")

    return render_template(
        "admin/safaris/inquiries/detail.html",
        inquiry=inquiry,
        allowed_statuses=sorted(allowed_statuses),)