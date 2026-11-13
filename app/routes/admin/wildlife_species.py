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
from sqlalchemy import or_
from extensions import db
from app.forms.wildlife_species import (
    WildlifeSpeciesForm,
)
from app.models import WildlifeSpecies
from app.services.wildlife_species_service import (
    WildlifeSpeciesService,
)

wildlife_species_bp = Blueprint(
    "admin_wildlife_species",
    __name__,
    url_prefix="/admin/wildlife-species",
)

@wildlife_species_bp.route("/")
#@login_required
def index():
    search = request.args.get("q", "").strip()
    animal_class = request.args.get("animal_class", "").strip()
    category = request.args.get("category", "").strip()
    conservation_status = request.args.get(
        "conservation_status", ""
    ).strip()
    status = request.args.get("status", "all").strip()
    featured = request.args.get("featured", "").strip()

    query = WildlifeSpecies.query

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                WildlifeSpecies.common_name.ilike(term),
                WildlifeSpecies.scientific_name.ilike(term),
                WildlifeSpecies.family.ilike(term),
                WildlifeSpecies.description.ilike(term),
            )
        )

    if animal_class:
        query = query.filter_by(animal_class=animal_class)

    if category:
        query = query.filter_by(category=category)

    if conservation_status:
        query = query.filter_by(
            conservation_status=conservation_status
        )

    if status == "active":
        query = query.filter_by(active=True)
    elif status == "inactive":
        query = query.filter_by(active=False)

    if featured == "yes":
        query = query.filter_by(featured=True)
    elif featured == "no":
        query = query.filter_by(featured=False)

    species_list = query.order_by(
        WildlifeSpecies.common_name.asc()
    ).all()

    statistics = WildlifeSpeciesService.get_statistics()

    return render_template(
        "admin/experiences/wildlife_species/index.html",
        species_list=species_list,
        statistics=statistics,
        search=search,
        selected_class=animal_class,
        selected_category=category,
        selected_conservation_status=conservation_status,
        selected_status=status,
        selected_featured=featured,
    )


@wildlife_species_bp.route("/create", methods=["GET", "POST"])
#@login_required
def create():
    form = WildlifeSpeciesForm()

    if form.validate_on_submit():
        try:
            WildlifeSpeciesService.create_species(
                common_name=form.common_name.data.strip(),
                scientific_name=form.scientific_name.data,
                family=form.family.data,
                animal_class=form.animal_class.data,
                category=form.category.data or None,
                conservation_status=(
                    form.conservation_status.data or None
                ),
                protected=form.protected.data,
                endemic=form.endemic.data,
                description=form.description.data,
                interesting_fact=form.interesting_fact.data,
                habitat=form.habitat.data,
                diet=form.diet.data,
                best_viewing_time=form.best_viewing_time.data,
                photography_difficulty=(
                    form.photography_difficulty.data
                ),
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                "Wildlife species created successfully.",
                "success",
            )
            return redirect(
                url_for("admin_wildlife_species.index")
            )

        except ValueError as exc:
            flash(str(exc), "error")
        except Exception:
            db.session.rollback()
            flash(
                "The wildlife species could not be created.",
                "error",
            )

    return render_template(
        "admin/experiences/wildlife_species/form.html",
        form=form,
        page_title="Add Wildlife Species",
        species=None,
    )


@wildlife_species_bp.route(
    "/<int:species_id>/edit",
    methods=["GET", "POST"],
)
#@login_required
def edit(species_id):
    species = WildlifeSpeciesService.get_by_id(species_id)

    if species is None:
        abort(404)

    form = WildlifeSpeciesForm(obj=species)

    if form.validate_on_submit():
        try:
            WildlifeSpeciesService.update_species(
                species_id,
                common_name=form.common_name.data.strip(),
                scientific_name=form.scientific_name.data,
                family=form.family.data,
                animal_class=form.animal_class.data,
                category=form.category.data or None,
                conservation_status=(
                    form.conservation_status.data or None
                ),
                protected=form.protected.data,
                endemic=form.endemic.data,
                description=form.description.data,
                interesting_fact=form.interesting_fact.data,
                habitat=form.habitat.data,
                diet=form.diet.data,
                best_viewing_time=form.best_viewing_time.data,
                photography_difficulty=(
                    form.photography_difficulty.data
                ),
                featured=form.featured.data,
                active=form.active.data,
            )

            flash(
                "Wildlife species updated successfully.",
                "success",
            )
            return redirect(
                url_for("admin_wildlife_species.index")
            )

        except ValueError as exc:
            flash(str(exc), "error")
        except Exception:
            db.session.rollback()
            flash(
                "The wildlife species could not be updated.",
                "error",
            )

    return render_template(
        "admin/experiences/wildlife_species/form.html",
        form=form,
        page_title="Edit Wildlife Species",
        species=species,
    )


@wildlife_species_bp.route(
    "/<int:species_id>/toggle-status",
    methods=["POST"],
)
#@login_required
def toggle_status(species_id):
    species = WildlifeSpeciesService.get_by_id(species_id)

    if species is None:
        abort(404)

    try:
        if species.active:
            WildlifeSpeciesService.deactivate(species_id)
            flash("Wildlife species deactivated.", "success")
        else:
            WildlifeSpeciesService.activate(species_id)
            flash("Wildlife species activated.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to update species status.", "error")

    return redirect(url_for("admin_wildlife_species.index"))


@wildlife_species_bp.route("/<int:species_id>/toggle-featured",methods=["POST"],)
#@login_required
def toggle_featured(species_id):
    species = WildlifeSpeciesService.get_by_id(species_id)

    if species is None:
        abort(404)

    try:
        if species.featured:
            WildlifeSpeciesService.unfeature(species_id)
            flash("Species removed from featured items.", "success")
        else:
            WildlifeSpeciesService.feature(species_id)
            flash("Species marked as featured.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to update featured status.", "error")

    return redirect(url_for("admin_wildlife_species.index"))


@wildlife_species_bp.route(
    "/<int:species_id>/delete",
    methods=["POST"],
)
#@login_required
def delete(species_id):
    species = WildlifeSpeciesService.get_by_id(species_id)

    if species is None:
        abort(404)

    # Preserve species that are already linked to experiences.
    if species.experiences.count() > 0:
        flash(
            "This species is linked to experiences. "
            "Deactivate it instead of deleting it.",
            "error",
        )
        return redirect(url_for("admin_wildlife_species.index"))

    try:
        WildlifeSpeciesService.delete(species_id)
        flash("Wildlife species deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to delete this wildlife species.", "error")

    return redirect(url_for("admin_wildlife_species.index"))