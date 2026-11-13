"""
===============================================================================
The Uncharted Route
Administrative Experience Category Routes
===============================================================================

Manage experience categories and populate their media selectors from the
existing hierarchical Media Library.

Architecture:
    Route -> Form -> Service -> Model

Authorization remains temporarily disabled during CMS setup.
"""

import re
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.forms.admin_experience_category import (
    AdminExperienceCategoryCreateForm,
    AdminExperienceCategoryEditForm,
    AdminExperienceCategoryFilterForm,
    AdminExperienceCategoryStatusForm,
    AdminExperienceCategoryFeaturedForm,
    AdminExperienceCategoryOrderForm,)
from app.services.experiences.experience_category_service import (
    create_category,
    get_category,
    get_all_categories,
    get_category_experiences,
    update_category,
    activate_category,
    deactivate_category,
    feature_category,
    unfeature_category,
    reorder_category,
    delete_category,)
from app.services.media_service import get_cms_media_assets

# =============================================================================
# Blueprint
# =============================================================================
experience_categories_bp = Blueprint(
    "admin_experience_categories",
    __name__,
    url_prefix="/admin/experiences/experiences-categories",)

# =============================================================================
# Media Library Helpers
# =============================================================================
MEDIA_ROOT_ID = 3
ICON_USAGES = {"icon"}
FEATURED_USAGES = {"featured", "category_card", "thumbnail"}
BANNER_USAGES = {"banner", "hero"}

def _normalize_name(value):
    """Normalize names for matching folder and category names."""

    value = (value or "").strip().lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def _name_tokens(value):
    """Return meaningful normalized words from a name."""

    return {
        token
        for token in _normalize_name(value).split()
        if token and token != "and"}


def _get_category_media_root():
    """Find the existing Experience Categories media root."""
    from app.models import MediaFolder
    root = MediaFolder.query.get(MEDIA_ROOT_ID)
    if root is not None and _normalize_name(root.name) == "experience categories":
        return root
    return (
        MediaFolder.query
        .filter(MediaFolder.name.ilike("Experience Categories"))
        .first()
    )


def _get_asset_folders(asset):
    """Return folders directly assigned to an asset."""

    assignments = getattr(asset, "folder_assignments", None)

    if assignments is None:
        return []

    try:
        assignments = assignments.all()
    except AttributeError:
        assignments = list(assignments)

    return [
        assignment.folder
        for assignment in assignments
        if getattr(assignment, "folder", None) is not None]

def _get_asset_value(asset):
    """
    Return a browser-accessible value suitable for the existing SelectFields.

    Keep the stored selection format compatible with the existing category
    model, which stores media selections as strings.
    """
    try:
        browser_url = asset.browser_url
    except (RuntimeError, AttributeError):
        browser_url = None

    return (
        browser_url
        or getattr(asset, "file_url", None)
        or getattr(asset, "file_path", None)
        or getattr(asset, "filename", None)
        or ""
    )


def _get_asset_label(asset):
    """Build a readable label for a media selector."""

    return (
        getattr(asset, "title", None)
        or getattr(asset, "original_filename", None)
        or getattr(asset, "filename", None)
        or f"Media asset {asset.id}"
    )


def _get_category_media_assets(category_name=None):
    """
    Retrieve active images from the Experience Categories folder tree.

    Assets assigned directly to the root are treated as shared assets.
    Category-specific assets are identified through their folder names,
    including nested folders such as 'Wildlife & Conservation icon'.
    """

    root_folder = _get_category_media_root()

    if root_folder is None or not root_folder.active:
        return []

    assets = get_cms_media_assets(
        folder_id=root_folder.id,
        include_descendants=True,
        media_type="image",
        active_only=True,
    )

    if not category_name:
        return assets

    category_tokens = _name_tokens(category_name)

    if not category_tokens:
        return assets

    matching_assets = []
    shared_assets = []

    for asset in assets:
        folders = _get_asset_folders(asset)

        is_shared = any(
            folder.id == root_folder.id
            for folder in folders
        )

        matches_category = any(
            category_tokens.issubset(_name_tokens(folder.name))
            for folder in folders
            if folder.id != root_folder.id
        )

        if is_shared or matches_category:
            matching_assets.append(asset)

        if is_shared:
            shared_assets.append(asset)

    # If no category-specific folder exists yet, retain the shared assets.
    # If the category has no assigned media at all, let the selector helper
    # fall back to the full Experience Categories media tree.
    if matching_assets:
        return matching_assets

    return shared_assets or assets


def _get_media_choices(assets, placeholder, preferred_usages=None,
                       category_name=None, field_name=None,
                       current_value=None):
    """
    Build SelectField choices from media assets.

    Prefer assets whose usage or folder matches the requested field.
    Fall back to the available category assets if no specialized assets
    exist yet, so the selector remains usable during CMS setup.
    """

    assets = list(assets or [])
    preferred_usages = preferred_usages or set()

    def usage_of(asset):
        return (getattr(asset, "usage", None) or "").strip().lower()

    def folder_matches_field(asset):
        folders = _get_asset_folders(asset)
        names = [_normalize_name(folder.name) for folder in folders]

        if field_name == "icon":
            return any(
                name.endswith(" icon") or name == "icon"
                for name in names
            )

        if field_name == "featured_image":
            return any(
                "featured" in name or "category card" in name
                for name in names
            )

        if field_name == "banner_image":
            return any(
                "banner" in name or "hero" in name
                for name in names
            )

        return False

    specialized = [
        asset for asset in assets
        if usage_of(asset) in preferred_usages
        or folder_matches_field(asset)
    ]

    # A category-specific icon folder is the strongest match for icons.
    # For other fields, media usage metadata helps distinguish assets.
    selected_assets = specialized or assets

    choices = [("", placeholder)]
    seen_values = {""}

    for asset in selected_assets:
        value = _get_asset_value(asset)

        if not value or value in seen_values:
            continue

        label = _get_asset_label(asset)
        usage = usage_of(asset)

        if usage:
            label = f"{label} ({usage.replace('_', ' ').title()})"

        choices.append((value, label))
        seen_values.add(value)

    # Preserve an existing saved selection even if the asset has since been
    # moved out of this category's folder or no longer matches its usage.
    if current_value and current_value not in seen_values:
        choices.append((current_value, f"Current selection — {current_value}"))

    return choices


def _populate_category_form_choices(form, category_name=None, category=None):
    """
    Populate all three media SelectFields before validation.

    This is essential because WTForms validates submitted SelectField values
    against their available choices.
    """

    assets = _get_category_media_assets(category_name)

    if not assets:
        # The media root may be empty. Leave the placeholder available and
        # preserve any existing values on an edit form.
        assets = []

    fields = (
        ("icon", "Select an icon image", ICON_USAGES),
        ("featured_image", "Select a featured image", FEATURED_USAGES),
        ("banner_image", "Select a banner image", BANNER_USAGES),
    )

    for field_name, placeholder, preferred_usages in fields:
        field = getattr(form, field_name)

        current_value = (
            getattr(category, field_name, None)
            if category is not None
            else None
        )

        # Prefer the submitted value on POST, otherwise retain the model value.
        submitted_value = field.data
        if submitted_value:
            current_value = submitted_value
        elif current_value:
            field.data = current_value

        field.choices = _get_media_choices(
            assets=assets,
            placeholder=placeholder,
            preferred_usages=preferred_usages,
            category_name=category_name,
            field_name=field_name,
            current_value=current_value,
        )


def _category_form_context(form, category=None):
    """Populate selectors and return the shared create/edit template context."""

    category_name = (
        category.name
        if category is not None
        else (form.name.data or None)
    )

    _populate_category_form_choices(
        form,
        category_name=category_name,
        category=category,
    )

    return {
        "form": form,
        "category": category,
        # Backward compatibility with templates or partials using this key.
        "category_media_assets": _get_category_media_assets(category_name),
        "category_icon_assets": _get_category_media_assets(category_name),
        "category_featured_image_assets": _get_category_media_assets(category_name),
        "category_banner_image_assets": _get_category_media_assets(category_name),
    }


# =============================================================================
# Category Library
# =============================================================================
@experience_categories_bp.route("/")
@login_required
def index():
    """Display and filter the category library."""

    form = AdminExperienceCategoryFilterForm(request.args)

    categories = get_all_categories(active_only=False)

    search = (form.search.data or "").strip().lower()
    status = form.status.data
    featured = form.featured.data

    if search:
        categories = [
            category for category in categories
            if (
                search in category.name.lower()
                or (
                    category.short_description
                    and search in category.short_description.lower()
                )
                or (
                    category.description
                    and search in category.description.lower()
                )
            )
        ]

    if status == "active":
        categories = [category for category in categories if category.active]
    elif status == "inactive":
        categories = [category for category in categories if not category.active]

    if featured == "featured":
        categories = [category for category in categories if category.featured]
    elif featured == "not_featured":
        categories = [category for category in categories if not category.featured]

    return render_template(
        "admin/experiences/experience_categories/index.html",
        form=form,
        categories=categories,
    )


# =============================================================================
# Create Category
# =============================================================================
@experience_categories_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new experience category."""

    form = AdminExperienceCategoryCreateForm()

    # Populate choices before validate_on_submit(), including on POST.
    _populate_category_form_choices(
        form,
        category_name=form.name.data or None,
    )

    if form.validate_on_submit():
        try:
            category = create_category(
                name=form.name.data,
                short_description=form.short_description.data,
                description=form.description.data,
                icon=form.icon.data,
                color=form.color.data,
                featured_image=form.featured_image.data,
                banner_image=form.banner_image.data,
                display_order=form.display_order.data,
                featured=form.featured.data,
                active=form.active.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "admin/experiences/experience_categories/create.html",
                **_category_form_context(form),
            )

        flash("Experience category created successfully.", "success")
        return redirect(
            url_for(
                "admin_experience_categories.detail",
                category_id=category.id,
            )
        )

    return render_template(
        "admin/experiences/experience_categories/create.html",
        **_category_form_context(form),
    )


# =============================================================================
# Category Detail
# =============================================================================
@experience_categories_bp.route("/<int:category_id>")
@login_required
def detail(category_id):
    """Display category details and its associated experiences."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    experiences = get_category_experiences(
        category_id,
        active_only=False,
    )

    return render_template(
        "admin/experiences/experience_categories/detail.html",
        category=category,
        experiences=experiences,
    )


# =============================================================================
# Edit Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit(category_id):
    """Edit an existing experience category."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryEditForm(obj=category)

    # Use the existing category folder while preserving its saved selections.
    _populate_category_form_choices(
        form,
        category_name=category.name,
        category=category,
    )

    if form.validate_on_submit():
        try:
            update_category(
                category_id,
                name=form.name.data,
                short_description=form.short_description.data,
                description=form.description.data,
                icon=form.icon.data,
                color=form.color.data,
                featured_image=form.featured_image.data,
                banner_image=form.banner_image.data,
                display_order=form.display_order.data,
                featured=form.featured.data,
                active=form.active.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template(
                "admin/experiences/experience_categories/edit.html",
                **_category_form_context(form, category),
            )

        flash("Experience category updated successfully.", "success")
        return redirect(
            url_for(
                "admin_experience_categories.detail",
                category_id=category.id,
            )
        )

    return render_template(
        "admin/experiences/experience_categories/edit.html",
        **_category_form_context(form, category),
    )

# =============================================================================
# Activate Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/activate", methods=["POST"])
@login_required
def activate(category_id):
    """Activate an experience category."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryStatusForm()

    if form.validate_on_submit():
        activate_category(category_id)
        flash("Experience category activated.", "success")

    return redirect(
        url_for(
            "admin_experience_categories.detail",
            category_id=category.id,
        )
    )


# =============================================================================
# Deactivate Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/deactivate", methods=["POST"])
@login_required
def deactivate(category_id):
    """Deactivate an experience category."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryStatusForm()

    if form.validate_on_submit():
        deactivate_category(category_id)
        flash("Experience category deactivated.", "success")

    return redirect(
        url_for(
            "admin_experience_categories.detail",
            category_id=category.id,))

# =============================================================================
# Feature Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/feature", methods=["POST"])
@login_required
def feature(category_id):
    """Mark a category as featured."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryFeaturedForm()

    if form.validate_on_submit():
        feature_category(category_id)
        flash("Experience category featured.", "success")

    return redirect(
        url_for(
            "admin_experience_categories.detail",
            category_id=category.id,
        )
    )


# =============================================================================
# Unfeature Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/unfeature", methods=["POST"])
@login_required
def unfeature(category_id):
    """Remove a category from featured categories."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryFeaturedForm()

    if form.validate_on_submit():
        unfeature_category(category_id)
        flash("Experience category unfeatured.", "success")

    return redirect(
        url_for(
            "admin_experience_categories.detail",
            category_id=category.id,))

# =============================================================================
# Reorder Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/order", methods=["POST"])
@login_required
def order(category_id):
    """Update the display order of a category."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryOrderForm()

    if form.validate_on_submit():
        reorder_category(category_id, form.display_order.data)
        flash("Category display order updated.", "success")

    return redirect(url_for("admin_experience_categories.index"))

# =============================================================================
# Delete Category
# =============================================================================
@experience_categories_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id):
    """Delete an experience category and its associated records."""

    category = get_category(category_id)

    if category is None:
        flash("Experience category not found.", "danger")
        return redirect(url_for("admin_experience_categories.index"))

    form = AdminExperienceCategoryStatusForm()

    if form.validate_on_submit():
        delete_category(category_id)
        flash("Experience category deleted successfully.", "success")
        return redirect(url_for("admin_experience_categories.index"))

    return redirect(
        url_for("admin_experience_categories.detail",category_id=category.id,))

# =============================================================================
# Public API
# =============================================================================
__all__ = ["experience_categories_bp"]
