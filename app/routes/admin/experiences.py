"""
===============================================================================
The Uncharted Route
Administrative Experience Management
===============================================================================
Core administrative CRUD routes for Experiences.

Child resources such as pricing, itineraries, inclusions, exclusions, wildlife,
photography, FAQs, schedules, reviews, tags, Signature Moments, etc. are
managed through their respective modules.

This module is responsible only for the core Experience record and its
catalogue relationships.
===============================================================================
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,)
from app.decorators.admin import admin_required
from app.forms.admin_experience import (
    AdminExperienceCreateForm,
    AdminExperienceEditForm,
    AdminExperienceFilterForm,
    AdminExperienceStatusForm,)
from app.models import (
    Accessibility,
    CancellationPolicy,
    ConservationStory,
    Destination,
    ExperienceCategory,
    ExperienceMedia,)
from app.models.experience_tag import ExperienceTag
from app.models.signature_moment import SignatureMoment
from app.services.experiences.experience_service import (
    activate_experience,
    create_experience,
    deactivate_experience,
    delete_experience,
    feature_experience,
    get_all_experiences,
    get_experience_by_id,
    get_experiences_by_category,
    get_experiences_by_destination,
    get_experience_statistics,
    search_experiences,
    unfeature_experience,
    update_experience,)
from app.services.media_service import (
    get_media_assets,
    get_media_folders,)
from app.services.experiences.primary_image_service import (
    set_primary_experience_image,
    get_primary_experience_image_url,
    get_primary_experience_image_urls,)
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
experiences_bp = Blueprint(
    "admin_experiences",
    __name__,
    url_prefix="/admin/experiences",
)

# =============================================================================
# Form Choice Helpers
# =============================================================================

def _populate_filter_form_choices(form):
    """
    Populate database-backed choices used by the Experience filter form.

    The filter form contains optional Category and Destination SelectFields.
    These choices must exist before WTForms processes the submitted values.
    """

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    categories = (
        ExperienceCategory.query
        .order_by(ExperienceCategory.name.asc())
        .all()
    )

    form.category_id.choices = [
        ("", "All Categories")
    ] + [
        (category.id, category.name)
        for category in categories
    ]

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------

    destinations = (
        Destination.query
        .order_by(Destination.name.asc())
        .all()
    )

    form.destination_id.choices = [
        ("", "All Destinations")
    ] + [
        (destination.id, destination.name)
        for destination in destinations
    ]

    return form


# =============================================================================
# Experience Media Library
# =============================================================================

EXPERIENCE_MEDIA_FOLDER_NAME = "Experiences"


def _get_experience_media_assets():
    """
    Retrieve active images from the Experiences folder
    and its active descendants.
    """

    folders = get_media_folders(active_only=True)

    root_folder = next(
        (
            folder
            for folder in folders
            if (
                folder.name
                and folder.name.strip().casefold()
                == EXPERIENCE_MEDIA_FOLDER_NAME.casefold()
            )
        ),
        None,
    )

    if root_folder is None:
        return []

    # Group folders by their parent ID.
    folders_by_parent = {}

    for folder in folders:
        folders_by_parent.setdefault(
            folder.parent_id,
            [],
        ).append(folder)

    # Collect the root folder and all descendants.
    folder_ids = set()
    pending = [root_folder]

    while pending:
        folder = pending.pop()

        if folder.id in folder_ids:
            continue

        folder_ids.add(folder.id)

        pending.extend(
            folders_by_parent.get(folder.id, [])
        )

    # Fetch images using the existing media service.
    assets_by_id = {}

    for folder_id in folder_ids:
        assets = get_media_assets(
            folder_id=folder_id,
            media_type="image",
            active_only=True,
        )

        for asset in assets:
            assets_by_id[asset.id] = asset

    return sorted(
        assets_by_id.values(),
        key=lambda asset: (
            (
                getattr(asset, "title", None)
                or getattr(asset, "original_filename", None)
                or getattr(asset, "filename", None)
                or ""
            ).casefold(),
            asset.id,
        ),
    )


def _media_label(asset):
    """Build a readable label for a Media Library image."""

    label = (
        getattr(asset, "title", None)
        or getattr(asset, "original_filename", None)
        or getattr(asset, "filename", None)
        or f"Image #{asset.id}"
    )

    return str(label)


def _populate_experience_media_choices(form, experience=None):
    """
    Populate the featured and banner image selectors.

    Existing image paths are preserved as legacy choices when an older
    Experience image is not represented by an eligible Media Library asset.
    """

    assets = _get_experience_media_assets()

    image_choices = [
        (str(asset.id), _media_label(asset))
        for asset in assets
    ]

    featured_choices = [
        ("", "— Select a featured image —"),
        *image_choices,
    ]

    banner_choices = [
        ("", "— No banner image —"),
        *image_choices,
    ]

    # Preserve existing values on edit when they are older static paths
    # or URLs that are not represented in the current Media Library list.
    if experience is not None:
        existing_featured = (
            getattr(experience, "featured_image", None) or ""
        )

        existing_banner = (
            getattr(experience, "banner_image", None) or ""
        )

        available_ids = {
            str(asset.id)
            for asset in assets
        }

        if (
            existing_featured
            and existing_featured not in available_ids
        ):
            featured_choices.append(
                (
                    existing_featured,
                    "Current featured image (legacy path)",
                )
            )

        if (
            existing_banner
            and existing_banner not in available_ids
        ):
            banner_choices.append(
                (
                    existing_banner,
                    "Current banner image (legacy path)",
                )
            )

    form.featured_image.choices = featured_choices
    form.banner_image.choices = banner_choices

    return assets


def _resolve_experience_image(value, assets, current_value=None):
    """
    Convert a selected MediaAsset ID into a renderable image path.

    A current legacy path is retained only when it exactly matches the
    existing database value. Newly submitted arbitrary paths are rejected.
    """

    value = (value or "").strip()

    if not value:
        return None

    # Preserve the existing image path on edit if it is a legacy value.
    if current_value and value == current_value:
        if not value.isdigit():
            return value

    asset_by_id = {
        str(asset.id): asset
        for asset in assets
    }

    asset = asset_by_id.get(value)

    if asset is None:
        raise ValueError(
            "Please select an image from the active Experiences "
            "Media Library folder."
        )

    file_path = (
        getattr(asset, "file_path", None) or ""
    ).strip()

    file_url = (
        getattr(asset, "file_url", None) or ""
    ).strip()

    # Prefer the stored file path because the existing public templates
    # use url_for('static', filename=...).
    if file_path:
        # Convert "static/uploads/example.jpg" to "uploads/example.jpg".
        if file_path.startswith("static/"):
            file_path = file_path[len("static/"):]

        return file_path

    # Support assets whose canonical location is an external URL.
    if file_url.startswith(("https://", "http://")):
        return file_url

    raise ValueError(
        f"The selected image '{_media_label(asset)}' has no usable "
        "file path or URL. Please check its Media Library record."
    )


def _populate_experience_form_choices(form):
    """
    Populate all database-backed SelectField choices used by the
    Experience create and edit forms.

    Choices are loaded directly from the database so that WTForms can
    correctly validate submitted foreign-key values.
    """

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    categories = (
        ExperienceCategory.query
        .order_by(ExperienceCategory.name.asc())
        .all()
    )

    form.category_id.choices = [
        (category.id, category.name)
        for category in categories
    ]

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------

    destinations = (
        Destination.query
        .order_by(Destination.name.asc())
        .all()
    )

    form.destination_id.choices = [
        (destination.id, destination.name)
        for destination in destinations
    ]

    # -------------------------------------------------------------------------
    # Conservation Stories
    # -------------------------------------------------------------------------

    conservation_stories = (
        ConservationStory.query
        .order_by(ConservationStory.id.desc())
        .all()
    )

    form.conservation_story_id.choices = [
        ("", "No Conservation Story")
    ] + [
        (
            story.id,
            getattr(
                story,
                "title",
                f"Conservation Story #{story.id}",
            ),
        )
        for story in conservation_stories
    ]

    # -------------------------------------------------------------------------
    # Cancellation Policies
    # -------------------------------------------------------------------------

    cancellation_policies = (
        CancellationPolicy.query
        .order_by(CancellationPolicy.id.desc())
        .all()
    )

    form.cancellation_policy_id.choices = [
        ("", "— Select a cancellation policy —")
    ] + [
        (
            policy.id,
            getattr(
                policy,
                "name",
                getattr(
                    policy,
                    "title",
                    f"Cancellation Policy #{policy.id}",
                ),
            ),
        )
        for policy in cancellation_policies
    ]

    # -------------------------------------------------------------------------
    # Accessibility Profiles
    # -------------------------------------------------------------------------

    accessibility_profiles = (
        Accessibility.query
        .order_by(Accessibility.id.desc())
        .all()
    )

    form.accessibility_profile_id.choices = [
        ("", "No Accessibility Profile")
    ] + [
        (
            profile.id,
            getattr(
                profile,
                "name",
                getattr(
                    profile,
                    "title",
                    f"Accessibility Profile #{profile.id}",
                ),
            ),
        )
        for profile in accessibility_profiles
    ]

    return form


# =============================================================================
# Experience Tag Helpers
# =============================================================================

def _populate_experience_tag_choices(form, experience=None):
    """
    Populate the Experience tag selector.

    Active tags are available for new assignments.

    Inactive tags already assigned to an Experience remain available
    when editing so existing assignments are not lost unintentionally.
    """

    active_tags = (
        ExperienceTag.query
        .filter_by(active=True)
        .order_by(
            ExperienceTag.sort_order.asc(),
            ExperienceTag.name.asc(),
        )
        .all()
    )

    available_tags = {
        tag.id: tag
        for tag in active_tags
    }

    if experience is not None:
        existing_tags = experience.tags.all()

        for tag in existing_tags:
            available_tags[tag.id] = tag

    tags = sorted(
        available_tags.values(),
        key=lambda tag: (
            tag.sort_order,
            (tag.name or "").casefold(),
        ),
    )

    form.set_tag_choices(tags)

    return tags


def _sync_experience_tags(
    experience,
    selected_tag_ids,
    allowed_tags,
):
    """
    Synchronize an Experience's dynamic tags relationship.

    Only tags supplied through the populated form choices can be assigned.
    """

    selected_ids = {
        int(tag_id)
        for tag_id in (selected_tag_ids or [])
    }

    allowed_tag_map = {
        tag.id: tag
        for tag in allowed_tags
    }

    invalid_ids = selected_ids - set(allowed_tag_map)

    if invalid_ids:
        raise ValueError(
            "One or more selected Experience Tags are unavailable. "
            "Please refresh the form and try again."
        )

    existing_tags = experience.tags.all()

    existing_tag_map = {
        tag.id: tag
        for tag in existing_tags
    }

    # Remove tags that are no longer selected.
    for tag_id, tag in existing_tag_map.items():
        if tag_id not in selected_ids:
            experience.tags.remove(tag)

    # Add newly selected tags.
    for tag_id in selected_ids:
        if tag_id not in existing_tag_map:
            experience.tags.append(
                allowed_tag_map[tag_id]
            )


# =============================================================================
# Signature Moment Helpers
# =============================================================================

def _populate_signature_moment_choices(form, experience=None):
    """
    Populate the Signature Moments selector.

    Active Signature Moments are available for new assignments.

    Inactive Signature Moments already assigned to an Experience remain
    available when editing so existing assignments are not lost.

    Signature Moments are independent catalogue records. This helper
    only supplies choices for the Experience association.
    """

    active_moments = (
        SignatureMoment.query
        .filter_by(active=True)
        .order_by(
            SignatureMoment.display_order.asc(),
            SignatureMoment.title.asc(),
        )
        .all()
    )

    available_moments = {
        moment.id: moment
        for moment in active_moments
    }

    if experience is not None:
        existing_moments = experience.signature_moments.all()

        for moment in existing_moments:
            available_moments[moment.id] = moment

    moments = sorted(
        available_moments.values(),
        key=lambda moment: (
            moment.display_order,
            (moment.title or "").casefold(),
        ),
    )

    form.set_signature_moment_choices(moments)

    return moments


def _sync_experience_signature_moments(
    experience,
    selected_moment_ids,
    allowed_moments,
):
    """
    Synchronize an Experience's Signature Moments relationship.

    This function only adds or removes many-to-many associations.

    It NEVER deletes Signature Moment catalogue records.
    """

    selected_ids = {
        int(moment_id)
        for moment_id in (selected_moment_ids or [])
    }

    allowed_moment_map = {
        moment.id: moment
        for moment in allowed_moments
    }

    invalid_ids = selected_ids - set(allowed_moment_map)

    if invalid_ids:
        raise ValueError(
            "One or more selected Signature Moments are unavailable. "
            "Please refresh the form and try again."
        )

    existing_moments = experience.signature_moments.all()

    existing_moment_map = {
        moment.id: moment
        for moment in existing_moments
    }

    # Remove only associations that were deselected.
    for moment_id, moment in existing_moment_map.items():
        if moment_id not in selected_ids:
            experience.signature_moments.remove(moment)

    # Add newly selected associations.
    for moment_id in selected_ids:
        if moment_id not in existing_moment_map:
            experience.signature_moments.append(
                allowed_moment_map[moment_id]
            )


# =============================================================================
# Experience Catalogue
# =============================================================================

@experiences_bp.route("/")
@admin_required
def index():
    """Display the administrative Experience catalogue."""

    form = AdminExperienceFilterForm(formdata=request.args)

    # Populate database-backed SelectFields before reading their values.
    _populate_filter_form_choices(form)

    search = form.search.data
    category_id = form.category_id.data
    destination_id = form.destination_id.data
    difficulty = form.difficulty.data
    active_only = form.active_only.data
    featured_only = form.featured_only.data

    # Retrieve the base collection.
    if search:
        experiences = search_experiences(
            search,
            active_only=active_only,
        )

    elif category_id:
        experiences = get_experiences_by_category(category_id)

    elif destination_id:
        experiences = get_experiences_by_destination(destination_id)

    else:
        experiences = get_all_experiences()

    # Apply the remaining filters.
    if difficulty:
        experiences = [
            experience
            for experience in experiences
            if experience.difficulty == difficulty
        ]

    if active_only:
        experiences = [
            experience
            for experience in experiences
            if experience.active
        ]

    if featured_only:
        experiences = [
            experience
            for experience in experiences
            if experience.featured
        ]

    image_urls = get_primary_experience_image_urls(experiences)

    return render_template(
        "admin/experiences/experience/index.html",
        form=form,
        experiences=experiences,
        image_urls=image_urls,
    )


# =============================================================================
# Create Experience
# =============================================================================

@experiences_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create():
    """Create a new Experience using the central Media Library."""

    form = AdminExperienceCreateForm()

    # Populate all database-backed fields before validation.
    _populate_experience_form_choices(form)

    tag_choices = _populate_experience_tag_choices(form)

    moment_choices = _populate_signature_moment_choices(form)

    # Use the same folder-aware selector pattern as Page Hero CMS.
    form.set_media_choices()

    # Build previews from the assets permitted by the populated choices.
    # The form's values are MediaAsset IDs, not filesystem paths.
    from app.models.media_asset import MediaAsset

    allowed_asset_ids = {
        int(value)
        for value, _label in form.featured_image.choices
        if value
    }

    media_assets = (
        MediaAsset.query.filter(
            MediaAsset.id.in_(allowed_asset_ids),
            MediaAsset.active.is_(True),
            MediaAsset.media_type == "image",
        ).all()
        if allowed_asset_ids
        else []
    )

    image_preview_map = {
        str(asset.id): asset.browser_url
        for asset in media_assets
        if asset.browser_url
    }

    if form.validate_on_submit():
        try:
            # Resolve selected asset IDs to the legacy image values expected
            # by the existing Experience service.
            featured_image_path = _resolve_experience_image(
                form.featured_image.data,
                media_assets,
            )

            banner_image_path = _resolve_experience_image(
                form.banner_image.data,
                media_assets,
            )

            experience = create_experience(
                # Identity
                experience_code=form.experience_code.data,
                title=form.title.data,
                slug=form.slug.data,

                # Content
                short_description=form.short_description.data,
                description=form.description.data,

                # Pricing
                price_from=form.price_from.data,
                currency=form.currency.data,

                # Images
                featured_image=featured_image_path,
                banner_image=banner_image_path,

                # Relationships
                category_id=form.category_id.data,
                destination_id=form.destination_id.data,
                conservation_story_id=form.conservation_story_id.data,
                cancellation_policy_id=form.cancellation_policy_id.data,
                accessibility_profile_id=form.accessibility_profile_id.data,

                # Logistics
                duration=form.duration.data,
                meeting_point=form.meeting_point.data,
                location=form.location.data,

                # Group information
                minimum_people=form.minimum_people.data,
                maximum_people=form.maximum_people.data,
                minimum_age=form.minimum_age.data,

                # Difficulty
                difficulty=form.difficulty.data,

                # SEO
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,

                # Publication
                featured=form.featured.data,
                show_on_homepage=form.show_on_homepage.data,
                active=form.active.data,
                display_order=form.display_order.data,
            )

            # Associate the selected Experience Tags.
            _sync_experience_tags(
                experience,
                form.tag_ids.data,
                tag_choices,
            )

            # Associate the selected Signature Moments.
            _sync_experience_signature_moments(
                experience,
                form.moment_ids.data,
                moment_choices,
            )

            # Associate the chosen Media Library asset with the experience.
            set_primary_experience_image(
                experience,
                form.featured_image.data,
            )

            db.session.commit()

            flash(
                "Experience created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experiences.detail",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to create experience or assign its primary image."
            )

            flash(
                "The experience could not be created. "
                "Please check the application logs.",
                "danger",
            )

    return render_template(
        "admin/experiences/experience/create.html",
        form=form,
        image_preview_map=image_preview_map,
    )


# =============================================================================
# Experience Detail
# =============================================================================
@experiences_bp.route("/<int:experience_id>")
@admin_required
def detail(experience_id):
    """Display an Experience and its management overview."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    statistics = get_experience_statistics(experience)
    primary_image_url = get_primary_experience_image_url(experience)

    return render_template(
        "admin/experiences/experience/detail.html",
        experience=experience,
        statistics=statistics,
        primary_image_url=primary_image_url,)

# =============================================================================
# Edit Experience
# =============================================================================
@experiences_bp.route("/<int:experience_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(experience_id):
    """Edit an Experience and synchronize its selected primary image."""

    from app.models.media_asset import MediaAsset

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceEditForm(obj=experience)

    # Populate all database-backed SelectFields before validation.
    _populate_experience_form_choices(form)

    tag_choices = _populate_experience_tag_choices(
        form,
        experience=experience,
    )

    moment_choices = _populate_signature_moment_choices(
        form,
        experience=experience,
    )

    # Populate the image choices from the Experiences folder tree.
    form.set_media_choices()

    # Only assets offered by the folder-scoped selector are eligible here.
    allowed_asset_ids = {
        int(value)
        for value, _label in form.featured_image.choices
        if value
    }

    media_assets = (
        MediaAsset.query.filter(
            MediaAsset.id.in_(allowed_asset_ids),
            MediaAsset.active.is_(True),
            MediaAsset.media_type == "image",
        ).all()
        if allowed_asset_ids
        else []
    )

    media_image_urls = {
        str(asset.id): asset.browser_url
        for asset in media_assets
        if asset.browser_url
    }

    # Find the existing primary Media Library association.
    current_primary_media = None

    for usage in ("hero", "cover", "thumbnail"):
        current_primary_media = (
            experience.media
            .filter(
                ExperienceMedia.active.is_(True),
                ExperienceMedia.usage == usage,
            )
            .order_by(ExperienceMedia.id.asc())
            .first()
        )

        if (
            current_primary_media is not None
            and current_primary_media.media_asset is not None
        ):
            break

        current_primary_media = None

    current_image_url = None

    if current_primary_media is not None:
        current_asset = current_primary_media.media_asset

        if current_asset is not None:
            current_image_url = current_asset.browser_url

            # Select the existing asset ID on the initial GET request.
            if request.method == "GET":
                current_asset_id = str(current_asset.id)

                if current_asset.id in allowed_asset_ids:
                    form.featured_image.data = current_asset_id

    # Preserve a usable preview for legacy records without an association.
    if not current_image_url and experience.featured_image:
        legacy_image = experience.featured_image

        if legacy_image.startswith(("https://", "http://", "/")):
            current_image_url = legacy_image

        elif not (
            len(legacy_image) > 2
            and legacy_image[1:3] == ":\\"
        ):
            current_image_url = url_for(
                "static",
                filename=legacy_image.replace("\\", "/"),
            )

    # Preselect the Experience's existing tags and Signature Moments
    # on the initial page load.
    if request.method == "GET":
        form.tag_ids.data = [
            tag.id
            for tag in experience.tags.all()
        ]

        form.moment_ids.data = [
            moment.id
            for moment in experience.signature_moments.all()
        ]

    if form.validate_on_submit():
        try:
            featured_image_path = _resolve_experience_image(
                form.featured_image.data,
                media_assets,
                current_value=experience.featured_image,
            )

            banner_image_path = _resolve_experience_image(
                form.banner_image.data,
                media_assets,
                current_value=experience.banner_image,
            )

            update_experience(
                experience,

                # Identity
                experience_code=form.experience_code.data,
                title=form.title.data,
                slug=form.slug.data,

                # Content
                short_description=form.short_description.data,
                description=form.description.data,

                # Logistics
                duration=form.duration.data,
                meeting_point=form.meeting_point.data,
                location=form.location.data,

                # Pricing and group information
                price_from=form.price_from.data,
                currency=form.currency.data,
                minimum_people=form.minimum_people.data,
                maximum_people=form.maximum_people.data,
                minimum_age=form.minimum_age.data,
                difficulty=form.difficulty.data,

                # Images
                featured_image=featured_image_path,
                banner_image=banner_image_path,

                # SEO
                meta_title=form.meta_title.data,
                meta_description=form.meta_description.data,

                # Publication
                featured=form.featured.data,
                show_on_homepage=form.show_on_homepage.data,
                active=form.active.data,
                display_order=form.display_order.data,

                # Relationships
                category_id=form.category_id.data,
                destination_id=form.destination_id.data,
                conservation_story_id=form.conservation_story_id.data,
                cancellation_policy_id=form.cancellation_policy_id.data,
                accessibility_profile_id=form.accessibility_profile_id.data,
            )

            # Synchronize the selected Experience Tags.
            _sync_experience_tags(
                experience,
                form.tag_ids.data,
                tag_choices,
            )

            # Synchronize the selected Signature Moments.
            # This changes associations only; catalogue records remain intact.
            _sync_experience_signature_moments(
                experience,
                form.moment_ids.data,
                moment_choices,
            )

            # Synchronize the primary Media Library association
            # BEFORE committing the transaction.
            set_primary_experience_image(
                experience,
                form.featured_image.data,
            )

            db.session.commit()
            flash(
                "Experience updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experiences.detail",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Failed to update experience %s.",
                experience_id,
            )

            flash(
                "The experience could not be updated. "
                "Please check the application logs.",
                "danger",
            )

    return render_template(
        "admin/experiences/experience/edit.html",
        form=form,
        experience=experience,
        current_image_url=current_image_url,
        media_image_urls=media_image_urls,
    )


# =============================================================================
# Activate
# =============================================================================

@experiences_bp.route(
    "/<int:experience_id>/activate",
    methods=["POST"],
)
@admin_required
def activate(experience_id):
    """Activate an Experience."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceStatusForm()

    if form.validate_on_submit():
        activate_experience(experience)

        flash(
            "Experience activated.",
            "success",
        )

    return redirect(
        url_for(
            "admin_experiences.detail",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Deactivate
# =============================================================================

@experiences_bp.route(
    "/<int:experience_id>/deactivate",
    methods=["POST"],
)
@admin_required
def deactivate(experience_id):
    """Deactivate an Experience."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceStatusForm()

    if form.validate_on_submit():
        deactivate_experience(experience)

        flash(
            "Experience deactivated.",
            "success",
        )

    return redirect(
        url_for(
            "admin_experiences.detail",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Feature
# =============================================================================

@experiences_bp.route(
    "/<int:experience_id>/feature",
    methods=["POST"],
)
@admin_required
def feature(experience_id):
    """Mark an Experience as featured."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceStatusForm()

    if form.validate_on_submit():
        feature_experience(experience)

        flash(
            "Experience featured successfully.",
            "success",
        )

    return redirect(
        url_for(
            "admin_experiences.detail",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Unfeature
# =============================================================================

@experiences_bp.route(
    "/<int:experience_id>/unfeature",
    methods=["POST"],
)
@admin_required
def unfeature(experience_id):
    """Remove an Experience from featured sections."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash("Experience not found.", "danger")

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceStatusForm()

    if form.validate_on_submit():
        unfeature_experience(experience)

        flash(
            "Experience removed from featured.",
            "success",
        )

    return redirect(
        url_for(
            "admin_experiences.detail",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================

@experiences_bp.route(
    "/<int:experience_id>/delete",
    methods=["POST"],
)
@admin_required
def delete(experience_id):
    """Delete an Experience."""

    experience = get_experience_by_id(experience_id)

    if experience is None:
        flash(
            "Experience not found.",
            "danger",
        )

        return redirect(
            url_for("admin_experiences.index")
        )

    form = AdminExperienceStatusForm()

    if form.validate_on_submit():
        delete_experience(experience)

        flash(
            "Experience deleted successfully.",
            "success",
        )

        return redirect(
            url_for("admin_experiences.index")
        )

    return redirect(
        url_for(
            "admin_experiences.detail",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "experiences_bp",]