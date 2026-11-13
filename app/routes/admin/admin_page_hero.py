"""
The Uncharted Route
Admin Page Hero CMS Routes
"""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from app.decorators.admin import admin_required
from app.forms.page_hero import PageHeroForm
from app.services.page_hero_service import PageHeroService

admin_page_hero = Blueprint(
    "admin_page_hero",
    __name__,
    url_prefix="/admin/page-heroes",)

@admin_page_hero.route("/")
@admin_required
def index():
    search = request.args.get("search", "", type=str).strip()
    active_filter = request.args.get("active", "", type=str).strip()

    active = None
    if active_filter == "1":
        active = True
    elif active_filter == "0":
        active = False

    heroes = PageHeroService.get_all(
        search=search,
        active=active,
    )

    return render_template(
        "admin/page_heroes/index.html",
        heroes=heroes,
        search=search,
        active_filter=active_filter,
    )

@admin_page_hero.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    form = PageHeroForm()
    form.set_media_choices()

    if form.validate_on_submit():
        try:
            hero = PageHeroService.create(form)
            flash("Page hero created successfully.", "success")

            return redirect(
                url_for("admin_page_hero.detail", hero_id=hero.id)
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/page_heroes/create.html",
        form=form,)

@admin_page_hero.route("/<int:hero_id>")
@admin_required
def detail(hero_id):
    hero = PageHeroService.get_by_id(hero_id)

    if hero is None:
        flash("Page hero not found.", "danger")
        return redirect(url_for("admin_page_hero.index"))

    return render_template(
        "admin/page_heroes/detail.html",
        hero=hero,)

@admin_page_hero.route("/<int:hero_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(hero_id):
    hero = PageHeroService.get_by_id(hero_id)

    if hero is None:
        flash("Page hero not found.", "danger")
        return redirect(url_for("admin_page_hero.index"))

    form = PageHeroForm(obj=hero)
    form.set_media_choices()

    if form.validate_on_submit():
        try:
            PageHeroService.update(hero, form)
            flash("Page hero updated successfully.", "success")

            return redirect(
                url_for("admin_page_hero.detail", hero_id=hero.id)
            )

        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/page_heroes/edit.html",
        form=form,
        hero=hero,)

@admin_page_hero.route("/<int:hero_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_active(hero_id):
    hero = PageHeroService.get_by_id(hero_id)

    if hero is None:
        flash("Page hero not found.", "danger")
        return redirect(url_for("admin_page_hero.index"))

    try:
        PageHeroService.toggle_active(hero)
        status = "activated" if hero.active else "deactivated"
        flash(f"Page hero {status} successfully.", "success")

    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(
        request.referrer or url_for("admin_page_hero.index"))

@admin_page_hero.route("/<int:hero_id>/delete", methods=["POST"])
@admin_required
def delete(hero_id):
    hero = PageHeroService.get_by_id(hero_id)
    if hero is None:
        flash("Page hero not found.", "danger")
        return redirect(url_for("admin_page_hero.index"))

    try:
        PageHeroService.delete(hero)
        flash("Page hero deleted successfully.", "success")

    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin_page_hero.index"))

__all__ = ["admin_page_hero"]
