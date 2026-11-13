"""
===============================================================================
The Uncharted Route — Administrative Homepage Blueprint
===============================================================================

Protected administrative routes for managing the public homepage CMS.

Responsibilities
----------------
• View homepage CMS dashboard
• View homepage configuration
• Edit homepage configuration
• View hero content
• View homepage media
• View homepage sections
• Create homepage sections
• Edit homepage sections
• Delete homepage sections
• Toggle section visibility
• Publish / unpublish homepage

Architecture
------------
Routes handle HTTP concerns only.

    Route → Form → Service → Model

Forms handle input validation.

Business logic is delegated to:
    app.services.admin_homepage_service

Authorization is enforced through:
    app.decorators.admin.admin_required

The homepage does not duplicate Experience, Destination, BlogPost,
Booking, Testimonial, or MediaAsset data.

Those systems remain responsible for their own records.

Homepage structure:

    Homepage
        │
        └── HomepageSection
                │
                └── MediaAsset
===============================================================================
"""
from flask import (
    Blueprint, request,
    flash,
    redirect,
    render_template,
    url_for, jsonify,
)
from flask_login import current_user
from app.decorators.admin import admin_required
from app.forms.admin_homepage import (
    AdminHomepageForm,
    AdminHomepageSectionForm,
)
from app.models import MediaFolder
from app.services.admin.admin_homepage_service import (
    get_current_homepage,
    get_homepage_section,
    get_homepage_sections,
    update_homepage,
    create_homepage_section,
    update_homepage_section,
    delete_homepage_section,
    set_homepage_section_visibility,
    publish_homepage,
    unpublish_homepage,)
from app.services.media_service import get_cms_media_assets

# =============================================================================
# Blueprint
# =============================================================================
homepage_bp = Blueprint(
    "admin_homepage",
    __name__,
    url_prefix="/admin/homepage",
)

# =============================================================================
# Homepage CMS Dashboard
# =============================================================================
@homepage_bp.route("/")
#@admin_required
def index():
    """
    Display the homepage CMS dashboard.

    Provides a central overview of:

    • Homepage publishing status
    • Homepage metadata
    • Hero section
    • Homepage sections
    • Homepage media
    """

    homepage = get_current_homepage()

    sections = get_homepage_sections(
        homepage=homepage,
    )

    return render_template(
        "admin/homepage/index.html",
        homepage=homepage,
        sections=sections,
    )


# =============================================================================
# Homepage Settings
# =============================================================================
@homepage_bp.route("/edit",methods=["GET", "POST"],)
#@admin_required
def edit():
    """
    Edit homepage-level configuration.

    Controls:

    • Homepage title
    • Homepage description
    • SEO title
    • SEO description
    • Publishing state
    """

    homepage = get_current_homepage()

    form = AdminHomepageForm(
        obj=homepage,
    )

    if form.validate_on_submit():

        try:

            update_homepage(
                acting_admin=current_user,
                homepage=homepage,
                title=form.title.data,
                description=form.description.data,
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,
                is_published=form.is_published.data,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_homepage.index",
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_homepage.edit",
                )
            )

        flash(
            "Homepage settings have been updated.",
            "success",
        )

        return redirect(
            url_for(
                "admin_homepage.index",
            )
        )

    return render_template(
        "admin/homepage/edit.html",
        form=form,
        homepage=homepage,
    )


# =============================================================================
# Hero Management
# =============================================================================
@homepage_bp.route("/hero")
#@admin_required
def hero():
    """
    Display the homepage hero management screen.

    The hero is represented by a HomepageSection whose:

        section_type == "hero"

    No separate hero database model is required.
    """

    homepage = get_current_homepage()

    sections = get_homepage_sections(
        homepage=homepage,
    )

    hero_section = next(
        (
            section
            for section in sections
            if section.is_hero
        ),
        None,
    )

    return render_template(
        "admin/homepage/hero.html",
        homepage=homepage,
        hero=hero_section,
    )


# =============================================================================
# Homepage Media
# =============================================================================
@homepage_bp.route("/media")
#@admin_required
def media():
    """
    Display media currently assigned to homepage sections.

    Homepage media continues to use the central MediaAsset system.
    """

    homepage = get_current_homepage()

    sections = get_homepage_sections(
        homepage=homepage,
    )

    media_sections = [
        section
        for section in sections
        if section.media_asset is not None
    ]

    return render_template(
        "admin/homepage/media.html",
        homepage=homepage,
        sections=media_sections,
    )


# =============================================================================
# Homepage Sections
# =============================================================================
@homepage_bp.route("/sections")
#@admin_required
def sections():
    """
    Display all homepage sections.
    """

    homepage = get_current_homepage()

    homepage_sections = get_homepage_sections(
        homepage=homepage,
    )

    return render_template(
        "admin/homepage/sections.html",
        homepage=homepage,
        sections=homepage_sections,
    )


# =============================================================================
# Create Homepage Section
# =============================================================================
@homepage_bp.route("/sections/create",methods=["GET", "POST"],)
#@admin_required
def create_section():
    """
    Create a new homepage section.
    """
    homepage = get_current_homepage()
    form = AdminHomepageSectionForm(
        section_type=(
                request.form.get("section_type")
                or request.args.get("section_type")
                or "hero"
        )
    )
    if form.validate_on_submit():

        media_asset_id = form.media_asset_id.data

        if media_asset_id == 0:
            media_asset_id = None

        try:

            create_homepage_section(
                acting_admin=current_user,
                homepage=homepage,
                section_type=form.section_type.data,
                title=form.title.data,
                subtitle=form.subtitle.data,
                content=form.content.data,
                cta_text=form.cta_text.data,
                cta_url=form.cta_url.data,
                media_asset_id=media_asset_id,
                display_order=form.display_order.data,
                is_visible=form.is_visible.data,
            )

        except PermissionError as exc:

            flash(
                str(exc),
                "danger",
            )

            return redirect(
                url_for(
                    "admin_homepage.sections",
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

            return render_template(
                "admin/homepage/section_form.html",
                form=form,
                page_title="Create Homepage Section",
            )

        flash(
            "Homepage section created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    return render_template(
        "admin/homepage/section_form.html",
        form=form,
        page_title="Create Homepage Section",
    )


# =============================================================================
# Edit Homepage Section
# =============================================================================
@homepage_bp.route("/sections/<int:section_id>/edit",methods=["GET", "POST"],)
#@admin_required
def edit_section(section_id):
    """
    Edit an existing homepage section.
    """

    section = get_homepage_section(
        section_id,
    )

    if section is None:

        flash(
            "Homepage section not found.",
            "danger",
        )

        return redirect(
            url_for("admin_homepage.sections",))

    form = AdminHomepageSectionForm(
        obj=section,
        section_type=(
                request.form.get("section_type")
                or section.section_type
        ),
    )
    if form.validate_on_submit():
        try:
            media_asset_id = form.media_asset_id.data

            if media_asset_id == 0:
                media_asset_id = None

            update_homepage_section(
                acting_admin=current_user,
                section=section,
                section_type=form.section_type.data,
                title=form.title.data,
                subtitle=form.subtitle.data,
                content=form.content.data,
                cta_text=form.cta_text.data,
                cta_url=form.cta_url.data,
                media_asset_id=media_asset_id,
                display_order=form.display_order.data,
                is_visible=form.is_visible.data,
            )

        except PermissionError as exc:
            flash(str(exc),"danger",)
            return redirect(url_for(
                    "admin_homepage.sections",))

        except ValueError as exc:
            flash(str(exc),"danger",)

            return render_template(
                "admin/homepage/section_form.html",
                form=form,
                section=section,
                page_title="Edit Homepage Section",)

        flash(
            "Homepage section updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    return render_template(
        "admin/homepage/section_form.html",
        form=form,
        section=section,
        page_title="Edit Homepage Section",
    )

# =============================================================================
# Delete Homepage Section
# =============================================================================
@homepage_bp.route("/sections/<int:section_id>/delete",methods=["POST"],)
#@admin_required
def delete_section(section_id):
    """
    Delete a homepage section.

    The associated MediaAsset is not deleted.
    """

    section = get_homepage_section(
        section_id,
    )

    if section is None:

        flash(
            "Homepage section not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    try:

        delete_homepage_section(
            acting_admin=current_user,
            section=section,
        )

    except PermissionError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    flash(
        "Homepage section deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_homepage.sections",
        )
    )


# =============================================================================
# Toggle Section Visibility
# =============================================================================
@homepage_bp.route("/sections/<int:section_id>/toggle",methods=["POST"],)
#@admin_required
def toggle_section(section_id):
    """
    Toggle homepage section visibility.
    """

    section = get_homepage_section(
        section_id,
    )

    if section is None:

        flash(
            "Homepage section not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    new_visibility = not section.is_visible

    try:

        set_homepage_section_visibility(
            acting_admin=current_user,
            section=section,
            is_visible=new_visibility,
        )

    except PermissionError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.sections",
            )
        )

    if new_visibility:

        flash(
            "Homepage section is now visible.",
            "success",
        )

    else:

        flash(
            "Homepage section has been hidden.",
            "success",
        )

    return redirect(
        url_for(
            "admin_homepage.sections",
        ))

# =============================================================================
# Publish Homepage
# =============================================================================
@homepage_bp.route("/publish",methods=["POST"],)
#@admin_required
def publish():
    """
    Publish the homepage.
    """

    homepage = get_current_homepage()

    try:

        publish_homepage(
            acting_admin=current_user,
            homepage=homepage,
        )

    except PermissionError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.index",
            )
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.index",
            )
        )

    flash(
        "Homepage published successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_homepage.index",
        )
    )


# =============================================================================
# Unpublish Homepage
# =============================================================================
@homepage_bp.route("/unpublish",methods=["POST"],)
#@admin_required
def unpublish():
    """
    Unpublish the homepage.
    """

    homepage = get_current_homepage()

    try:

        unpublish_homepage(
            acting_admin=current_user,
            homepage=homepage,
        )

    except PermissionError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.index",
            )
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

        return redirect(
            url_for(
                "admin_homepage.index",
            )
        )

    flash(
        "Homepage has been unpublished.",
        "success",
    )

    return redirect(
        url_for(
            "admin_homepage.index",
        ))
# =============================================================================
# Homepage Section Media Selector
# =============================================================================
@homepage_bp.route("/sections/media-assets")
def section_media_assets():
    """Return active media assets from the folder for a homepage section."""

    folder_by_type = {
        "hero": "Hero",
        "featured_experience_card": "Featured Experiences",
        "destination_card": "Destinations",
    }

    section_type = request.args.get("section_type", "").strip()
    folder_name = folder_by_type.get(section_type)

    if not folder_name:
        return jsonify({"assets": []})

    homepage_folder = MediaFolder.query.filter_by(
        slug="homepage",
        active=True,
    ).first()

    if homepage_folder is None:
        return jsonify({"assets": []})

    folder = MediaFolder.query.filter_by(
        parent_id=homepage_folder.id,
        name=folder_name,
        active=True,
    ).first()

    if folder is None:
        return jsonify({"assets": []})

    assets = get_cms_media_assets(
        folder_id=folder.id,
        include_descendants=True,
        active_only=True,
    )

    return jsonify({
        "assets": [
            {
                "id": asset.id,
                "title": (
                    asset.title
                    or asset.original_filename
                    or f"Media #{asset.id}"
                ),
            }
            for asset in assets
            if asset.media_type in {"image", "video"}
        ]
    })

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "homepage_bp",
]