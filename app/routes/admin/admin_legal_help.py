"""
===============================================================================
The Uncharted Route
Admin - Legal & Help
===============================================================================
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,)
from app.forms.admin_legal_help import (
    LegalHelpItemForm,
    LegalHelpPageForm,
    LegalHelpSectionForm,)
from app.services.admin.admin_legal_help_service import LegalHelpService

admin_legal_help_bp = Blueprint(
    "admin_legal_help",
    __name__,
    url_prefix="/admin/legal-help",)

# =============================================================================
# PAGE LIST
# =============================================================================

@admin_legal_help_bp.route("/")
def index():
    pages = LegalHelpService.get_pages()

    return render_template(
        "admin/legal_help/index.html",
        pages=pages,
    )


# =============================================================================
# CREATE PAGE
# =============================================================================

@admin_legal_help_bp.route("/new", methods=["GET", "POST"])
def create():
    form = LegalHelpPageForm()

    if form.validate_on_submit():
        page = LegalHelpService.create_page(
            form.data
        )

        flash(
            "Legal & Help page created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=page.id,
            )
        )

    return render_template(
        "admin/legal_help/page_form.html",
        form=form,
        page=None,
        heading="Create Legal & Help Page",
    )


# =============================================================================
# PAGE DETAIL
# =============================================================================

@admin_legal_help_bp.route("/<int:page_id>")
def detail(page_id):
    page = LegalHelpService.get_page(page_id)

    if not page:
        flash(
            "Legal & Help page not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    return render_template(
        "admin/legal_help/detail.html",
        page=page,
    )


# =============================================================================
# EDIT PAGE
# =============================================================================

@admin_legal_help_bp.route(
    "/<int:page_id>/edit",
    methods=["GET", "POST"],
)
def edit(page_id):
    page = LegalHelpService.get_page(page_id)

    if not page:
        flash(
            "Legal & Help page not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    form = LegalHelpPageForm(obj=page)

    if form.validate_on_submit():
        LegalHelpService.update_page(
            page,
            form.data,
        )

        flash(
            "Legal & Help page updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=page.id,
            )
        )

    return render_template(
        "admin/legal_help/page_form.html",
        form=form,
        page=page,
        heading="Edit Legal & Help Page",
    )


# =============================================================================
# DELETE PAGE
# =============================================================================

@admin_legal_help_bp.route(
    "/<int:page_id>/delete",
    methods=["POST"],
)
def delete(page_id):
    page = LegalHelpService.get_page(page_id)

    if not page:
        flash(
            "Legal & Help page not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    LegalHelpService.delete_page(page)

    flash(
        "Legal & Help page deleted successfully.",
        "success",
    )

    return redirect(
        url_for("admin_legal_help.index")
    )


# =============================================================================
# CREATE SECTION
# =============================================================================

@admin_legal_help_bp.route(
    "/<int:page_id>/sections/new",
    methods=["GET", "POST"],
)
def create_section(page_id):
    page = LegalHelpService.get_page(page_id)

    if not page:
        flash(
            "Legal & Help page not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    form = LegalHelpSectionForm()

    if form.validate_on_submit():
        LegalHelpService.create_section(
            page,
            form.data,
        )

        flash(
            "Section created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=page.id,
            )
        )

    return render_template(
        "admin/legal_help/section_form.html",
        form=form,
        page=page,
        section=None,
        heading="Create Section",
    )


# =============================================================================
# EDIT SECTION
# =============================================================================

@admin_legal_help_bp.route(
    "/sections/<int:section_id>/edit",
    methods=["GET", "POST"],
)
def edit_section(section_id):
    section = LegalHelpService.get_section(section_id)

    if not section:
        flash(
            "Section not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    form = LegalHelpSectionForm(obj=section)

    if form.validate_on_submit():
        LegalHelpService.update_section(
            section,
            form.data,
        )

        flash(
            "Section updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=section.page_id,
            )
        )

    return render_template(
        "admin/legal_help/section_form.html",
        form=form,
        page=section.page,
        section=section,
        heading="Edit Section",
    )


# =============================================================================
# DELETE SECTION
# =============================================================================

@admin_legal_help_bp.route(
    "/sections/<int:section_id>/delete",
    methods=["POST"],
)
def delete_section(section_id):
    section = LegalHelpService.get_section(section_id)

    if not section:
        flash(
            "Section not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    page_id = section.page_id

    LegalHelpService.delete_section(section)

    flash(
        "Section deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_legal_help.detail",
            page_id=page_id,
        )
    )


# =============================================================================
# CREATE ITEM
# =============================================================================

@admin_legal_help_bp.route(
    "/sections/<int:section_id>/items/new",
    methods=["GET", "POST"],
)
def create_item(section_id):
    section = LegalHelpService.get_section(section_id)

    if not section:
        flash(
            "Section not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    form = LegalHelpItemForm()

    if form.validate_on_submit():
        LegalHelpService.create_item(
            section,
            form.data,
        )

        flash(
            "Content item created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=section.page_id,
            )
        )

    return render_template(
        "admin/legal_help/item_form.html",
        form=form,
        section=section,
        item=None,
        heading="Create Content Item",
    )


# =============================================================================
# EDIT ITEM
# =============================================================================

@admin_legal_help_bp.route(
    "/items/<int:item_id>/edit",
    methods=["GET", "POST"],
)
def edit_item(item_id):
    item = LegalHelpService.get_item(item_id)

    if not item:
        flash(
            "Content item not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    form = LegalHelpItemForm(obj=item)

    if form.validate_on_submit():
        LegalHelpService.update_item(
            item,
            form.data,
        )

        flash(
            "Content item updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "admin_legal_help.detail",
                page_id=item.section.page_id,
            )
        )

    return render_template(
        "admin/legal_help/item_form.html",
        form=form,
        section=item.section,
        item=item,
        heading="Edit Content Item",
    )


# =============================================================================
# DELETE ITEM
# =============================================================================

@admin_legal_help_bp.route(
    "/items/<int:item_id>/delete",
    methods=["POST"],
)
def delete_item(item_id):
    item = LegalHelpService.get_item(item_id)

    if not item:
        flash(
            "Content item not found.",
            "error",
        )
        return redirect(
            url_for("admin_legal_help.index")
        )

    page_id = item.section.page_id

    LegalHelpService.delete_item(item)

    flash(
        "Content item deleted successfully.",
        "success",
    )

    return redirect(
        url_for(
            "admin_legal_help.detail",
            page_id=page_id,
        )
    )