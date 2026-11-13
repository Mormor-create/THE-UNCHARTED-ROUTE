"""
===============================================================================
The Uncharted Route
Administrative Conservation Story Routes
===============================================================================
CMS management for reusable conservation stories.
Architecture:
Route → Form → Service → Model
Responsibilities:
- View conservation story library
- Search and filter stories
- Create stories
- View story details
- Edit stories
- Activate/deactivate stories
- Feature/unfeature stories
- Change display order
- Delete unused stories
"""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from flask_login import login_required
from app.decorators.admin import admin_required
from app.forms.admin_conservation_story import (
    AdminConservationStoryCreateForm,
    AdminConservationStoryEditForm,
    AdminConservationStoryFilterForm,
    AdminConservationStoryFeaturedForm,
    AdminConservationStoryOrderForm,
    AdminConservationStoryStatusForm,)
from app.services.experiences.conservation_story_service import (
    ConservationStoryService,)

# =============================================================================
# Blueprint
# =============================================================================
conservation_story_bp = Blueprint(
    "admin_conservation_stories",
    __name__,
    url_prefix="/admin/experiences/conservation-stories",)

# =============================================================================
# Library
# =============================================================================
@conservation_story_bp.route("/")
@admin_required
@login_required
def index():
    """
    Display the conservation story library.
    """
    form = AdminConservationStoryFilterForm(
        request.args,)
    stories = ConservationStoryService.get_all(
        active_only=False,
        featured_only=False,)
    search = (
        form.search.data.strip().lower()
        if form.search.data
        else "")

    conservation_type = (
        form.conservation_type.data
        if form.conservation_type.data
        else "")

    status = (
        form.status.data
        if form.status.data
        else "")

    featured = (
        form.featured.data
        if form.featured.data
        else "")

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    if search:
        stories = [
            story
            for story in stories
            if (
                search in story.title.lower()
                or (
                    story.short_description
                    and search
                    in story.short_description.lower())
                or (
                    story.focus_species
                    and search
                    in story.focus_species.lower())
                or (
                    story.organization_name
                    and search
                    in story.organization_name.lower()))]

    # -------------------------------------------------------------------------
    # Conservation Type
    # -------------------------------------------------------------------------
    if conservation_type:
        stories = [
            story
            for story in stories
            if story.conservation_type
            == conservation_type]

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------
    if status == "active":
        stories = [
            story
            for story in stories
            if story.active]

    elif status == "inactive":
        stories = [
            story
            for story in stories
            if not story.active]

    # -------------------------------------------------------------------------
    # Featured
    # -------------------------------------------------------------------------
    if featured == "featured":
        stories = [
            story
            for story in stories
            if story.featured]

    elif featured == "not_featured":
        stories = [
            story
            for story in stories
            if not story.featured]

    statistics = (ConservationStoryService.get_statistics())
    return render_template(
        "admin/conservation_stories/index.html",
        form=form,
        stories=stories,
        statistics=statistics,)

# =============================================================================
# Create
# =============================================================================
@conservation_story_bp.route("/create",methods=["GET", "POST"],)
@login_required
def create():
    """
    Create a new conservation story.
    """

    form = AdminConservationStoryCreateForm()
    if form.validate_on_submit():
        story = (
            ConservationStoryService.create_story(
                title=form.title.data.strip(),
                slug=(
                    form.slug.data.strip()
                    if form.slug.data
                    else None
                ),
                conservation_type=(
                    form.conservation_type.data
                ),
                short_description=(
                    form.short_description.data
                ),
                full_story=form.full_story.data,
                focus_species=(
                    form.focus_species.data
                ),
                organization_name=(
                    form.organization_name.data
                ),
                organization_website=(
                    form.organization_website.data
                ),
                why_it_matters=(
                    form.why_it_matters.data
                ),
                visitor_impact=(
                    form.visitor_impact.data
                ),
                how_guests_help=(
                    form.how_guests_help.data
                ),
                interesting_fact=(
                    form.interesting_fact.data
                ),
                featured=form.featured.data,
                active=form.active.data,
                display_order=form.display_order.data,
                hero_media_id=(
                    form.hero_media_id.data or None),))

        flash("Conservation story created successfully.","success",)
        return redirect(
            url_for(
                "admin_conservation_stories.detail",
                story_id=story.id,))

    return render_template(
        "admin/conservation_stories/create.html",
        form=form,)

# =============================================================================
# Detail
# =============================================================================
@conservation_story_bp.route("/<int:story_id>",)
@admin_required
@login_required
def detail(story_id):
    """
    Display complete conservation story details.
    """

    story = (
        ConservationStoryService.get_by_id(
            story_id
        )
    )

    if story is None:
        flash(
            "Conservation story not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_conservation_stories.index"
            )
        )

    experience_count = (
        ConservationStoryService
        .get_experience_count(story_id)
    )

    in_use = (
        ConservationStoryService
        .is_in_use(story_id)
    )

    return render_template(
        "admin/conservation_stories/detail.html",
        story=story,
        experience_count=experience_count,
        in_use=in_use,
    )


# =============================================================================
# Edit
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/edit",methods=["GET", "POST"],)
@admin_required
@login_required
def edit(story_id):
    """
    Edit an existing conservation story.
    """

    story = (
        ConservationStoryService.get_by_id(
            story_id
        )
    )

    if story is None:
        flash(
            "Conservation story not found.",
            "danger",
        )

        return redirect(
            url_for(
                "admin_conservation_stories.index"
            )
        )

    form = AdminConservationStoryEditForm(
        obj=story,
        current_story=story,
    )

    if form.validate_on_submit():

        ConservationStoryService.update_story(
            story_id,
            title=form.title.data.strip(),
            slug=(
                form.slug.data.strip()
                if form.slug.data
                else None
            ),
            conservation_type=(
                form.conservation_type.data
            ),
            short_description=(
                form.short_description.data
            ),
            full_story=form.full_story.data,
            focus_species=(
                form.focus_species.data
            ),
            organization_name=(
                form.organization_name.data
            ),
            organization_website=(
                form.organization_website.data
            ),
            why_it_matters=(
                form.why_it_matters.data
            ),
            visitor_impact=(
                form.visitor_impact.data
            ),
            how_guests_help=(
                form.how_guests_help.data
            ),
            interesting_fact=(
                form.interesting_fact.data
            ),
            featured=form.featured.data,
            active=form.active.data,
            display_order=form.display_order.data,
            hero_media_id=(
                form.hero_media_id.data or None
            ),
        )

        flash("Conservation story updated successfully.","success",)
        return redirect(
            url_for(
                "admin_conservation_stories.detail",story_id=story.id,))

    return render_template(
        "admin/conservation_stories/edit.html",
        form=form,story=story,)

# =============================================================================
# Activate
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/activate",methods=["POST"],)
@admin_required
@login_required
def activate(story_id):

    story = (
        ConservationStoryService.get_by_id(story_id))

    if story is None:
        flash("Conservation story not found.","danger",)
        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryStatusForm()
    if form.validate_on_submit():
        ConservationStoryService.activate(story_id)
        flash("Conservation story activated.","success",)

    return redirect(
        url_for("admin_conservation_stories.detail",story_id=story.id,))

# =============================================================================
# Deactivate
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/deactivate",methods=["POST"],)
@admin_required
@login_required
def deactivate(story_id):

    story = (
        ConservationStoryService.get_by_id(story_id))

    if story is None:
        flash("Conservation story not found.","danger",)
        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryStatusForm()
    if form.validate_on_submit():
        ConservationStoryService.deactivate(story_id)
        flash("Conservation story deactivated.","success",)

    return redirect(
        url_for("admin_conservation_stories.detail",story_id=story.id,))

# =============================================================================
# Feature
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/feature",methods=["POST"],)
@admin_required
@login_required
def feature(story_id):

    story = (
        ConservationStoryService.get_by_id(
            story_id))

    if story is None:
        flash("Conservation story not found.","danger",)

        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryFeaturedForm()
    if form.validate_on_submit():
        ConservationStoryService.feature(story_id)
        flash("Conservation story featured.","success",)

    return redirect(
        url_for(
            "admin_conservation_stories.detail",
            story_id=story.id,))

# =============================================================================
# Unfeature
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/unfeature",methods=["POST"],)
@admin_required
@login_required
def unfeature(story_id):

    story = (
        ConservationStoryService.get_by_id(
            story_id))

    if story is None:
        flash("Conservation story not found.","danger",)

        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryFeaturedForm()
    if form.validate_on_submit():
        ConservationStoryService.unfeature(story_id)

        flash("Conservation story removed from featured.","success",)

    return redirect(
        url_for("admin_conservation_stories.detail",story_id=story.id,))

# =============================================================================
# Display Order
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/order",methods=["POST"],)
@admin_required
@login_required
def order(story_id):
    story = (ConservationStoryService.get_by_id(story_id))
    if story is None:
        flash(
            "Conservation story not found.",
            "danger",)

        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryOrderForm()
    if form.validate_on_submit():
        ConservationStoryService.set_display_order(
            story_id,
            form.display_order.data,)

        flash("Conservation story display order updated.","success",)

    return redirect(
        url_for("admin_conservation_stories.index"))

# =============================================================================
# Delete
# =============================================================================
@conservation_story_bp.route("/<int:story_id>/delete",methods=["POST"],)
@admin_required
@login_required
def delete(story_id):

    story = (
        ConservationStoryService.get_by_id(
            story_id))

    if story is None:
        flash("Conservation story not found.","danger",)
        return redirect(
            url_for("admin_conservation_stories.index"))

    form = AdminConservationStoryStatusForm()
    if form.validate_on_submit():
        try:
            deleted = (ConservationStoryService.delete(story_id))
            if deleted:
                flash("Conservation story deleted successfully.","success",)

                return redirect(
                    url_for("admin_conservation_stories.index"))

        except ValueError as exc:
            flash(
                str(exc),
                "danger",)

    return redirect(
        url_for(
            "admin_conservation_stories.detail",story_id=story.id,))

# =============================================================================
# Public API
# =============================================================================
__all__ = ["conservation_story_bp",]