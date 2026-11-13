"""
===============================================================================
The Uncharted Route
Admin Experience Review Routes
===============================================================================

Administrative routes for managing customer reviews attached to experiences.

Supported operations:

- List reviews
- Create reviews
- Edit reviews
- View review details
- Approve reviews
- Reject reviews
- Unpublish reviews
- Feature / unfeature reviews
- Respond to reviews
- Remove admin responses
- Record helpful votes
- Record reports
- Delete reviews
- Filter reviews
- View rating statistics
- View rating distribution
- View pending reviews
- View reported reviews
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import login_required, current_user

from app.forms.admin_experience_reviews import (
    ExperienceReviewCreateForm,
    ExperienceReviewEditForm,
    ExperienceReviewModerationForm,
    ExperienceReviewResponseForm,
    ExperienceReviewFilterForm,
)

from app.models import (
    Experience,
    ExperienceReview,
)

from app.services.experiences.experience_review_service import (
    create_review,
    get_review,
    get_experience_reviews,
    get_public_reviews,
    get_featured_reviews,
    approve_review,
    reject_review,
    unpublish_review,
    feature_review,
    unfeature_review,
    respond_to_review,
    remove_admin_response,
    add_helpful_vote,
    report_review,
    get_rating_statistics,
    get_rating_distribution,
    count_reviews,
    get_pending_reviews,
    get_reported_reviews,
    delete_review,
)


# =============================================================================
# Blueprint
# =============================================================================

admin_experience_reviews = Blueprint(
    "admin_experience_reviews",
    __name__,
    url_prefix="/admin/experiences",
)


# =============================================================================
# Experience Helper
# =============================================================================

def _get_experience_or_404(experience_id):
    """
    Retrieve an experiences or return a 404 response.
    """

    return Experience.query.get_or_404(
        experience_id
    )


# =============================================================================
# Review Helper
# =============================================================================

def _get_review_for_experience_or_redirect(
    experience_id,
    review_id,
):
    """
    Retrieve a review and ensure it belongs to the requested experiences.

    Returns
    -------
    tuple
        (experiences, review)

    Returns
    -------
    None
        When the review does not belong to the experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    review = get_review(
        review_id
    )

    if review is None:
        flash(
            "Review not found.",
            "danger",
        )

        return experience, None

    if review.experience_id != experience.id:
        flash(
            "Review does not belong to this experiences.",
            "danger",
        )

        return experience, None

    return experience, review


# =============================================================================
# Index
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews"
)
#@login_required
def index(experience_id):
    """
    Display reviews belonging to an experiences.

    Supports filtering by:

    - reviewer
    - rating
    - verification
    - moderation status
    - featured status
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceReviewFilterForm(
        request.args
    )

    reviews = get_experience_reviews(
        experience.id,
        public_only=False,
        featured_only=False,
    )

    # =========================================================================
    # Filters
    # =========================================================================

    reviewer_name = request.args.get(
        "reviewer_name",
        "",
    ).strip()

    rating = request.args.get(
        "rating",
        "",
    ).strip()

    verified = request.args.get(
        "verified",
        "",
    ).strip()

    moderation = request.args.get(
        "moderation",
        "",
    ).strip()

    featured = request.args.get(
        "featured",
        "",
    ).strip()

    # -------------------------------------------------------------------------
    # Reviewer Filter
    # -------------------------------------------------------------------------

    if reviewer_name:

        search_term = reviewer_name.lower()

        reviews = [
            review
            for review in reviews
            if search_term
            in review.reviewer_name.lower()
        ]

    # -------------------------------------------------------------------------
    # Rating Filter
    # -------------------------------------------------------------------------

    if rating:

        try:
            rating_value = int(rating)

            reviews = [
                review
                for review in reviews
                if review.overall_rating == rating_value
            ]

        except (TypeError, ValueError):

            flash(
                "Invalid rating filter.",
                "danger",
            )

            return redirect(
                url_for(
                    "admin_experience_reviews.index",
                    experience_id=experience.id,
                )
            )

    # -------------------------------------------------------------------------
    # Verification Filter
    # -------------------------------------------------------------------------

    if verified == "verified":

        reviews = [
            review
            for review in reviews
            if review.verified_booking
        ]

    elif verified == "unverified":

        reviews = [
            review
            for review in reviews
            if not review.verified_booking
        ]

    # -------------------------------------------------------------------------
    # Moderation Filter
    # -------------------------------------------------------------------------

    if moderation == "pending":

        reviews = [
            review
            for review in reviews
            if not review.approved
            and not review.rejected
        ]

    elif moderation == "approved":

        reviews = [
            review
            for review in reviews
            if review.approved
            and not review.rejected
        ]

    elif moderation == "rejected":

        reviews = [
            review
            for review in reviews
            if review.rejected
        ]

    # -------------------------------------------------------------------------
    # Featured Filter
    # -------------------------------------------------------------------------

    if featured == "featured":

        reviews = [
            review
            for review in reviews
            if review.featured
        ]

    elif featured == "not_featured":

        reviews = [
            review
            for review in reviews
            if not review.featured
        ]

    # =========================================================================
    # Statistics
    # =========================================================================

    total_count = count_reviews(
        experience_id=experience.id,
        public_only=False,
    )

    public_count = count_reviews(
        experience_id=experience.id,
        public_only=True,
    )

    pending_count = len([
        review
        for review in get_experience_reviews(
            experience.id,
            public_only=False,
        )
        if not review.approved
        and not review.rejected
    ])

    rejected_count = len([
        review
        for review in get_experience_reviews(
            experience.id,
            public_only=False,
        )
        if review.rejected
    ])

    featured_count = len([
        review
        for review in get_experience_reviews(
            experience.id,
            public_only=False,
        )
        if review.featured
        and review.approved
        and not review.rejected
    ])

    statistics = get_rating_statistics(
        experience.id
    )

    distribution = get_rating_distribution(
        experience.id
    )

    return render_template(
        "admin/experiences/experience_reviews/index.html",
        experience=experience,
        reviews=reviews,
        form=form,
        total_count=total_count,
        public_count=public_count,
        pending_count=pending_count,
        rejected_count=rejected_count,
        featured_count=featured_count,
        statistics=statistics,
        distribution=distribution,
        selected_reviewer=reviewer_name,
        selected_rating=rating,
        selected_verified=verified,
        selected_moderation=moderation,
        selected_featured=featured,
    )


# =============================================================================
# Create
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/create",
    methods=["GET", "POST"],
)
#@login_required
def create(experience_id):
    """
    Create a review for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    form = ExperienceReviewCreateForm()

    if form.validate_on_submit():

        data = {
            "reviewer_name": form.reviewer_name.data,
            "reviewer_email": form.reviewer_email.data,
            "reviewer_country": form.reviewer_country.data,
            "overall_rating": form.overall_rating.data,
            "guide_rating": (
                form.guide_rating.data
                if form.guide_rating.data != 0
                else None
            ),
            "transportation_rating": (
                form.transportation_rating.data
                if form.transportation_rating.data != 0
                else None
            ),
            "accommodation_rating": (
                form.accommodation_rating.data
                if form.accommodation_rating.data != 0
                else None
            ),
            "value_rating": (
                form.value_rating.data
                if form.value_rating.data != 0
                else None
            ),
            "organization_rating": (
                form.organization_rating.data
                if form.organization_rating.data != 0
                else None
            ),
            "title": form.title.data,
            "review": form.review.data,
            "pros": form.pros.data,
            "cons": form.cons.data,
            "travel_date": form.travel_date.data,
            "would_recommend": form.would_recommend.data,
        }

        try:

            review = create_review(
                experience.id,
                data,
            )

            # Administrative creation can explicitly set
            # verification and moderation fields after creation.

            review.verified_booking = (
                form.verified_booking.data
            )

            review.featured = (
                form.featured.data
            )

            review.approved = (
                form.approved.data
            )

            review.rejected = (
                form.rejected.data
            )

            review.rejection_reason = (
                form.rejection_reason.data
            )

            from extensions import db

            db.session.commit()

            flash(
                "Review created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_reviews.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_reviews/create.html",
        experience=experience,
        form=form,
    )


# =============================================================================
# Edit
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/edit",
    methods=["GET", "POST"],
)
#@login_required
def edit(
    experience_id,
    review_id,
):
    """
    Edit an existing review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceReviewEditForm(
        obj=review
    )

    if form.validate_on_submit():

        # Convert "Not provided" values back to None.

        from app.services.experiences.experience_review_service import (
            validate_review_data,
        )

        data = {
            "reviewer_name": form.reviewer_name.data,
            "reviewer_email": form.reviewer_email.data,
            "reviewer_country": form.reviewer_country.data,
            "overall_rating": form.overall_rating.data,
            "guide_rating": (
                form.guide_rating.data
                if form.guide_rating.data != 0
                else None
            ),
            "transportation_rating": (
                form.transportation_rating.data
                if form.transportation_rating.data != 0
                else None
            ),
            "accommodation_rating": (
                form.accommodation_rating.data
                if form.accommodation_rating.data != 0
                else None
            ),
            "value_rating": (
                form.value_rating.data
                if form.value_rating.data != 0
                else None
            ),
            "organization_rating": (
                form.organization_rating.data
                if form.organization_rating.data != 0
                else None
            ),
            "title": form.title.data,
            "review": form.review.data,
            "pros": form.pros.data,
            "cons": form.cons.data,
            "travel_date": form.travel_date.data,
            "would_recommend": form.would_recommend.data,
        }

        try:

            validated = validate_review_data(
                data
            )

            review.reviewer_name = (
                validated["reviewer_name"]
            )

            review.reviewer_email = (
                validated["reviewer_email"]
            )

            review.reviewer_country = (
                validated["reviewer_country"]
            )

            review.overall_rating = (
                validated["overall_rating"]
            )

            review.guide_rating = (
                validated["guide_rating"]
            )

            review.transportation_rating = (
                validated["transportation_rating"]
            )

            review.accommodation_rating = (
                validated["accommodation_rating"]
            )

            review.value_rating = (
                validated["value_rating"]
            )

            review.organization_rating = (
                validated["organization_rating"]
            )

            review.title = validated["title"]
            review.review = validated["review"]
            review.pros = validated["pros"]
            review.cons = validated["cons"]
            review.travel_date = validated["travel_date"]
            review.would_recommend = (
                validated["would_recommend"]
            )

            review.verified_booking = (
                form.verified_booking.data
            )

            review.featured = (
                form.featured.data
            )

            review.approved = (
                form.approved.data
            )

            review.rejected = (
                form.rejected.data
            )

            review.rejection_reason = (
                form.rejection_reason.data
            )

            review.admin_response = (
                form.admin_response.data
            )

            review.admin_responded_by = (
                form.admin_responded_by.data
            )

            from datetime import datetime
            from extensions import db

            if review.admin_response:

                review.admin_responded_at = (
                    datetime.utcnow()
                )

            else:

                review.admin_responded_at = None
                review.admin_responded_by = None

            if review.rejected:

                review.approved = False

            if review.approved:

                review.rejected = False
                review.rejection_reason = None

            db.session.commit()

            flash(
                "Review updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_reviews.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_reviews/edit.html",
        experience=experience,
        review=review,
        form=form,
    )


# =============================================================================
# Approve
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/approve",methods=["POST"],)
#@login_required
def approve(
    experience_id,
    review_id,
):
    """
    Approve a review for public display.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        approve_review(
            review.id
        )

        flash(
            "Review approved successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Reject
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/reject",
    methods=["POST"],)
#@login_required
def reject(
    experience_id,
    review_id,
):
    """
    Reject a review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    reason = request.form.get(
        "rejection_reason",
        "",
    ).strip()

    try:

        reject_review(
            review.id,
            reason=reason or None,
        )

        flash(
            "Review rejected successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Moderation
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/moderate",
    methods=["GET", "POST"],
)
#@login_required
def moderate(
    experience_id,
    review_id,
):
    """
    Open the moderation form for a review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceReviewModerationForm(
        obj=review
    )

    if form.validate_on_submit():

        try:

            if form.rejected.data:

                reject_review(
                    review.id,
                    reason=form.rejection_reason.data,
                )

            elif form.approved.data:

                approve_review(
                    review.id
                )

            else:

                unpublish_review(
                    review.id
                )

            flash(
                "Review moderation status updated.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_reviews.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_reviews/edit.html",
        experience=experience,
        review=review,
        form=form,
        moderation_only=True,
    )


# =============================================================================
# Unpublish
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/unpublish",
    methods=["POST"],
)
#@login_required
def unpublish(
    experience_id,
    review_id,
):
    """
    Remove a review from public display.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        unpublish_review(
            review.id
        )

        flash(
            "Review unpublished successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Feature
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/feature",
    methods=["POST"],)
#@login_required
def feature(
    experience_id,
    review_id,
):
    """
    Feature an approved public review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        feature_review(
            review.id
        )

        flash(
            "Review featured successfully.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Unfeature
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/unfeature",
    methods=["POST"],
)
#@login_required
def unfeature(
    experience_id,
    review_id,
):
    """
    Remove a review from featured status.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        unfeature_review(
            review.id
        )

        flash(
            "Review removed from featured reviews.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Respond
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/respond",
    methods=["GET", "POST"],
)
#@login_required
def respond(
    experience_id,
    review_id,
):
    """
    Add or update an administrative response.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    form = ExperienceReviewResponseForm(
        obj=review
    )

    if not form.admin_responded_by.data:

        form.admin_responded_by.data = (
            getattr(
                current_user,
                "name",
                None,
            )
            or getattr(
                current_user,
                "username",
                None,
            )
            or ""
        )

    if form.validate_on_submit():

        try:

            respond_to_review(
                review.id,
                form.admin_response.data,
                form.admin_responded_by.data,
            )

            flash(
                "Administrative response saved successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "admin_experience_reviews.index",
                    experience_id=experience.id,
                )
            )

        except ValueError as exc:

            flash(
                str(exc),
                "danger",
            )

    return render_template(
        "admin/experiences/experience_reviews/edit.html",
        experience=experience,
        review=review,
        form=form,
        response_only=True,
    )


# =============================================================================
# Remove Response
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/response/delete",
    methods=["POST"],
)
#@login_required
def remove_response(
    experience_id,
    review_id,
):
    """
    Remove the administrative response from a review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        remove_admin_response(
            review.id
        )

        flash(
            "Administrative response removed.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Helpful Vote
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/helpful",
    methods=["POST"],
)
#@login_required
def helpful(
    experience_id,
    review_id,
):
    """
    Record a helpful vote for a review.

    Included for administrative tooling and testing.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        add_helpful_vote(
            review.id
        )

        flash(
            "Helpful vote recorded.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Report
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/report",
    methods=["POST"],
)
#@login_required
def report(
    experience_id,
    review_id,
):
    """
    Record a report against a review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    try:

        report_review(
            review.id
        )

        flash(
            "Review report recorded.",
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Delete
# =============================================================================

@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/<int:review_id>/delete",
    methods=["POST"],
)
#@login_required
def delete(
    experience_id,
    review_id,
):
    """
    Permanently delete a review.
    """

    experience, review = (
        _get_review_for_experience_or_redirect(
            experience_id,
            review_id,
        )
    )

    if review is None:

        return redirect(
            url_for(
                "admin_experience_reviews.index",
                experience_id=experience.id,
            )
        )

    reviewer_name = review.reviewer_name

    try:

        delete_review(
            review.id
        )

        flash(
            f'Review by "{reviewer_name}" was deleted.',
            "success",
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger",
        )

    return redirect(
        url_for(
            "admin_experience_reviews.index",
            experience_id=experience.id,
        )
    )


# =============================================================================
# Pending Reviews
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/pending")
#@login_required
def pending(experience_id):
    """
    Display reviews awaiting moderation for an experiences.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    reviews = [
        review
        for review in get_pending_reviews()
        if review.experience_id == experience.id
    ]

    return render_template(
        "admin/experience_reviews/index.html",
        experience=experience,
        reviews=reviews,
        pending_only=True,
        total_count=len(reviews),
        public_count=0,
        pending_count=len(reviews),
        rejected_count=0,
        featured_count=0,
        statistics=get_rating_statistics(
            experience.id
        ),
        distribution=get_rating_distribution(
            experience.id
        ),
        selected_reviewer="",
        selected_rating="",
        selected_verified="",
        selected_moderation="pending",
        selected_featured="",
        form=ExperienceReviewFilterForm(
            request.args
        ),
    )


# =============================================================================
# Reported Reviews
# =============================================================================
@admin_experience_reviews.route(
    "/<int:experience_id>/reviews/reported")
#@login_required
def reported(experience_id):
    """
    Display reviews that have received reports.
    """

    experience = _get_experience_or_404(
        experience_id
    )

    reviews = [
        review
        for review in get_reported_reviews()
        if review.experience_id == experience.id
    ]

    return render_template(
        "admin/experience_reviews/index.html",
        experience=experience,
        reviews=reviews,
        reported_only=True,
        total_count=len(reviews),
        public_count=0,
        pending_count=0,
        rejected_count=0,
        featured_count=0,
        statistics=get_rating_statistics(
            experience.id
        ),
        distribution=get_rating_distribution(
            experience.id
        ),
        selected_reviewer="",
        selected_rating="",
        selected_verified="",
        selected_moderation="",
        selected_featured="",
        form=ExperienceReviewFilterForm(
            request.args
        ),
    )