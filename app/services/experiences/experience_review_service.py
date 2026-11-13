"""
===============================================================================
The Uncharted Route
Experience Review Service
===============================================================================

Business logic for managing customer reviews.

Responsibilities
----------------

• Create reviews
• Validate ratings
• Verify booking eligibility
• Retrieve reviews
• Retrieve public reviews
• Retrieve featured reviews
• Approve reviews
• Reject reviews
• Feature / unfeature reviews
• Respond to reviews
• Record helpful votes
• Record review reports
• Calculate rating statistics
• Manage review moderation

The service layer keeps review business logic out of routes,
controllers, and templates.
"""

from datetime import datetime

from extensions import db

from app.models import ExperienceReview, Experience, Booking

# =============================================================================
# Constants
# =============================================================================

MIN_RATING = 1
MAX_RATING = 5

RATING_FIELDS = [
    "overall_rating",
    "guide_rating",
    "transportation_rating",
    "accommodation_rating",
    "value_rating",
    "organization_rating",
]


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_rating(rating, required=False):
    """
    Validate a rating value.

    Returns
    -------
    int
        Validated rating.

    Raises
    ------
    ValueError
        If the rating is invalid.
    """

    if rating is None:

        if required:
            raise ValueError("Rating is required.")

        return None

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        raise ValueError("Rating must be a number.")

    if rating < MIN_RATING or rating > MAX_RATING:
        raise ValueError(
            f"Rating must be between {MIN_RATING} and {MAX_RATING}."
        )

    return rating


def validate_review_data(data):
    """
    Validate review input data.
    """

    if not data:
        raise ValueError("Review data is required.")

    reviewer_name = data.get("reviewer_name")

    if not reviewer_name:
        raise ValueError("Reviewer name is required.")

    review_text = data.get("review")

    if not review_text:
        raise ValueError("Review content is required.")

    overall_rating = validate_rating(
        data.get("overall_rating"),
        required=True
    )

    validated = {
        "reviewer_name": reviewer_name.strip(),
        "reviewer_email": data.get("reviewer_email"),
        "reviewer_country": data.get("reviewer_country"),
        "overall_rating": overall_rating,
        "guide_rating": validate_rating(
            data.get("guide_rating")
        ),
        "transportation_rating": validate_rating(
            data.get("transportation_rating")
        ),
        "accommodation_rating": validate_rating(
            data.get("accommodation_rating")
        ),
        "value_rating": validate_rating(
            data.get("value_rating")
        ),
        "organization_rating": validate_rating(
            data.get("organization_rating")
        ),
        "title": data.get("title"),
        "review": review_text.strip(),
        "pros": data.get("pros"),
        "cons": data.get("cons"),
        "travel_date": data.get("travel_date"),
        "would_recommend": data.get(
            "would_recommend",
            True
        ),
    }

    return validated


# =============================================================================
# Booking Verification
# =============================================================================

def verify_booking_eligibility(booking):
    """
    Determine whether a booking is eligible to leave a review.

    A booking is considered eligible when:

    • It exists
    • It is associated with the experiences
    • It has been completed
    """

    if not booking:
        return False

    return booking.status in [
        "Completed",
        "Reviewed",
    ]


def find_booking(booking_id):
    """
    Retrieve a booking by ID.
    """

    if not booking_id:
        return None

    return db.session.get(
        Booking,
        booking_id
    )


# =============================================================================
# Create Review
# =============================================================================

def create_review(
    experience_id,
    data,
    booking_id=None,
    user_id=None,
):
    """
    Create a customer review.

    Reviews created through a completed booking are automatically
    marked as verified.
    """

    experience = db.session.get(
        Experience,
        experience_id
    )

    if not experience:
        raise ValueError("Experience not found.")

    validated = validate_review_data(data)

    booking = None

    if booking_id:

        booking = find_booking(booking_id)

        if not booking:
            raise ValueError("Booking not found.")

        if booking.experience_id != experience_id:
            raise ValueError(
                "Booking does not belong to this experiences."
            )

        if not verify_booking_eligibility(booking):
            raise ValueError(
                "Only completed booking can submit verified reviews."
            )

        existing_review = ExperienceReview.query.filter_by(
            booking_id=booking.id
        ).first()

        if existing_review:
            raise ValueError(
                "This booking already has a review."
            )

    review = ExperienceReview(
        experience_id=experience_id,
        booking_id=booking_id,
        user_id=user_id,
        verified_booking=bool(booking),
        approved=False,
        rejected=False,
        featured=False,
        **validated
    )

    db.session.add(review)
    db.session.commit()

    return review


# =============================================================================
# Get Review
# =============================================================================

def get_review(review_id):
    """
    Retrieve a review by ID.
    """

    return db.session.get(
        ExperienceReview,
        review_id
    )


# =============================================================================
# Get Experience Reviews
# =============================================================================

def get_experience_reviews(
    experience_id,
    public_only=False,
    featured_only=False,
):
    """
    Retrieve reviews belonging to an experiences.
    """

    query = ExperienceReview.query.filter_by(
        experience_id=experience_id
    )

    if public_only:
        query = query.filter(
            ExperienceReview.approved.is_(True),
            ExperienceReview.rejected.is_(False)
        )

    if featured_only:
        query = query.filter_by(
            featured=True
        )

    return query.order_by(
        ExperienceReview.created_at.desc()
    ).all()


# =============================================================================
# Public Reviews
# =============================================================================

def get_public_reviews(experience_id=None):
    """
    Retrieve reviews visible to customers.
    """

    query = ExperienceReview.query.filter(
        ExperienceReview.approved.is_(True),
        ExperienceReview.rejected.is_(False)
    )

    if experience_id:
        query = query.filter_by(
            experience_id=experience_id
        )

    return query.order_by(
        ExperienceReview.created_at.desc()
    ).all()


# =============================================================================
# Featured Reviews
# =============================================================================

def get_featured_reviews(experience_id=None):
    """
    Retrieve featured public reviews.
    """

    query = ExperienceReview.query.filter(
        ExperienceReview.featured.is_(True),
        ExperienceReview.approved.is_(True),
        ExperienceReview.rejected.is_(False)
    )

    if experience_id:
        query = query.filter_by(
            experience_id=experience_id
        )

    return query.order_by(
        ExperienceReview.created_at.desc()
    ).all()


# =============================================================================
# Moderation
# =============================================================================

def approve_review(review_id):
    """
    Approve a review for public display.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.approved = True
    review.rejected = False
    review.rejection_reason = None

    db.session.commit()

    return review


def reject_review(
    review_id,
    reason=None,
):
    """
    Reject a review.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.rejected = True
    review.approved = False
    review.featured = False
    review.rejection_reason = reason

    db.session.commit()

    return review


def unpublish_review(review_id):
    """
    Remove a review from public display without deleting it.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.approved = False
    review.featured = False

    db.session.commit()

    return review


# =============================================================================
# Featured Reviews
# =============================================================================

def feature_review(review_id):
    """
    Mark an approved review as featured.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    if not review.is_public:
        raise ValueError(
            "Only public reviews can be featured."
        )

    review.featured = True

    db.session.commit()

    return review


def unfeature_review(review_id):
    """
    Remove a review from featured status.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.featured = False

    db.session.commit()

    return review


# =============================================================================
# Admin Response
# =============================================================================

def respond_to_review(
    review_id,
    response,
    responded_by,
):
    """
    Add or update an administrative response.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    if not response:
        raise ValueError(
            "Admin response cannot be empty."
        )

    if not responded_by:
        raise ValueError(
            "Responder information is required."
        )

    review.admin_response = response.strip()
    review.admin_responded_by = responded_by
    review.admin_responded_at = datetime.utcnow()

    db.session.commit()

    return review


def remove_admin_response(review_id):
    """
    Remove an administrative response.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.admin_response = None
    review.admin_responded_by = None
    review.admin_responded_at = None

    db.session.commit()

    return review


# =============================================================================
# Helpful Votes
# =============================================================================

def add_helpful_vote(review_id):
    """
    Increment the helpful vote counter.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.helpful_votes += 1

    db.session.commit()

    return review


# =============================================================================
# Review Reports
# =============================================================================

def report_review(review_id):
    """
    Increment the report counter for a review.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    review.report_count += 1

    db.session.commit()

    return review


# =============================================================================
# Rating Statistics
# =============================================================================

def get_rating_statistics(experience_id):
    """
    Calculate rating statistics for an experiences.

    Only public reviews are included.
    """

    reviews = get_public_reviews(
        experience_id=experience_id
    )

    if not reviews:
        return {
            "review_count": 0,
            "average_rating": 0,
            "guide_rating": 0,
            "transportation_rating": 0,
            "accommodation_rating": 0,
            "value_rating": 0,
            "organization_rating": 0,
        }

    def average(field):
        values = [
            getattr(review, field)
            for review in reviews
            if getattr(review, field) is not None
        ]

        if not values:
            return 0

        return round(
            sum(values) / len(values),
            1
        )

    return {
        "review_count": len(reviews),
        "average_rating": average("overall_rating"),
        "guide_rating": average("guide_rating"),
        "transportation_rating": average(
            "transportation_rating"
        ),
        "accommodation_rating": average(
            "accommodation_rating"
        ),
        "value_rating": average("value_rating"),
        "organization_rating": average(
            "organization_rating"
        ),
    }


# =============================================================================
# Rating Distribution
# =============================================================================

def get_rating_distribution(experience_id):
    """
    Return the distribution of overall ratings.

    Example:

    {
        5: 12,
        4: 8,
        3: 2,
        2: 0,
        1: 1
    }
    """

    reviews = get_public_reviews(
        experience_id=experience_id
    )

    distribution = {
        5: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 0,
    }

    for review in reviews:

        rating = review.overall_rating

        if rating in distribution:
            distribution[rating] += 1

    return distribution


# =============================================================================
# Review Counts
# =============================================================================

def count_reviews(
    experience_id=None,
    public_only=False,
):
    """
    Count reviews.

    Can count all reviews or only public reviews.
    """

    if public_only:

        query = ExperienceReview.query.filter(
            ExperienceReview.approved.is_(True),
            ExperienceReview.rejected.is_(False)
        )

    else:

        query = ExperienceReview.query

    if experience_id:

        query = query.filter_by(
            experience_id=experience_id
        )

    return query.count()


# =============================================================================
# Pending Moderation
# =============================================================================

def get_pending_reviews():
    """
    Return reviews awaiting moderation.
    """

    return ExperienceReview.query.filter(
        ExperienceReview.approved.is_(False),
        ExperienceReview.rejected.is_(False)
    ).order_by(
        ExperienceReview.created_at.asc()
    ).all()


# =============================================================================
# Reported Reviews
# =============================================================================

def get_reported_reviews():
    """
    Return reviews that have been reported.
    """

    return ExperienceReview.query.filter(
        ExperienceReview.report_count > 0
    ).order_by(
        ExperienceReview.report_count.desc()
    ).all()


# =============================================================================
# Delete Review
# =============================================================================

def delete_review(review_id):
    """
    Permanently delete a review.

    Intended primarily for administrative use.
    """

    review = get_review(review_id)

    if not review:
        raise ValueError("Review not found.")

    db.session.delete(review)
    db.session.commit()

    return True