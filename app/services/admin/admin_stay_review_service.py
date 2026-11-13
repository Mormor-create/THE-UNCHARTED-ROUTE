from __future__ import annotations
from datetime import date
from typing import Optional
from sqlalchemy import func
from extensions import db
from app.models.stay import Stay
from app.models.stay_review import StayReview

def _require_admin(user):
    return None

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_stay_review(
    review_id: int,
) -> Optional[StayReview]:
    if not review_id:
        return None

    return db.session.get(
        StayReview,
        review_id,
    )


def get_stay_reviews(
    stay_id: Optional[int] = None,
    status: Optional[str] = None,
    verified_stay: Optional[bool] = None,
    featured: Optional[bool] = None,
    rating: Optional[int] = None,
):
    query = StayReview.query

    if stay_id:
        query = query.filter(
            StayReview.stay_id == stay_id
        )

    if status:
        query = query.filter(
            StayReview.status == status
        )

    if verified_stay is not None:
        query = query.filter(
            StayReview.verified_stay.is_(verified_stay)
        )

    if featured is not None:
        query = query.filter(
            StayReview.featured.is_(featured)
        )

    if rating is not None:
        query = query.filter(
            StayReview.rating == rating
        )

    return (
        query
        .order_by(
            StayReview.created_at.desc(),
            StayReview.id.desc(),
        )
        .all()
    )


def get_approved_stay_reviews(
    stay_id: int,
    limit: Optional[int] = None,
):
    query = (
        StayReview.query
        .filter(
            StayReview.stay_id == stay_id,
            StayReview.status == "approved",
        )
        .order_by(
            StayReview.created_at.desc(),
            StayReview.id.desc(),
        )
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_featured_stay_reviews(
    stay_id: Optional[int] = None,
):
    query = StayReview.query.filter(
        StayReview.status == "approved",
        StayReview.featured.is_(True),
    )

    if stay_id:
        query = query.filter(
            StayReview.stay_id == stay_id
        )

    return (
        query
        .order_by(
            StayReview.created_at.desc(),
            StayReview.id.desc(),
        )
        .all()
    )


def get_pending_stay_reviews(
    stay_id: Optional[int] = None,
):
    return get_stay_reviews(
        stay_id=stay_id,
        status="pending",
    )


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def get_stay_review_count(
    stay_id: Optional[int] = None,
    status: Optional[str] = None,
):
    query = db.session.query(
        func.count(StayReview.id)
    )

    if stay_id:
        query = query.filter(
            StayReview.stay_id == stay_id
        )

    if status:
        query = query.filter(
            StayReview.status == status
        )

    return query.scalar() or 0


def get_stay_average_rating(
    stay_id: int,
):
    result = (
        db.session.query(
            func.avg(StayReview.rating)
        )
        .filter(
            StayReview.stay_id == stay_id,
            StayReview.status == "approved",
        )
        .scalar()
    )

    if result is None:
        return None

    return round(float(result), 2)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_stay(stay_id: int):
    stay = db.session.get(
        Stay,
        stay_id,
    )

    if stay is None:
        raise ValueError("Stay not found.")

    return stay


def _validate_rating(rating):
    if rating is None:
        raise ValueError(
            "Rating is required."
        )

    if rating < 1 or rating > 5:
        raise ValueError(
            "Rating must be between 1 and 5."
        )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_stay_review(
    acting_admin,
    *,
    stay_id,
    guest_name,
    guest_email=None,
    rating,
    title=None,
    review,
    room_name=None,
    stay_date=None,
    status="pending",
    verified_stay=False,
    featured=False,
    admin_response=None,
):
    _require_admin(acting_admin)

    stay = _validate_stay(stay_id)

    guest_name = (guest_name or "").strip()
    review = (review or "").strip()

    if not guest_name:
        raise ValueError(
            "Guest name is required."
        )

    if not review:
        raise ValueError(
            "Review text is required."
        )

    _validate_rating(rating)

    review_record = StayReview(
        stay_id=stay.id,
        guest_name=guest_name,
        guest_email=guest_email,
        rating=rating,
        title=title,
        review=review,
        room_name=room_name,
        stay_date=stay_date,
        status=status,
        verified_stay=bool(verified_stay),
        featured=bool(featured),
        admin_response=admin_response,
    )

    db.session.add(review_record)
    db.session.commit()

    return review_record


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_stay_review(
    acting_admin,
    *,
    review,
    stay_id,
    guest_name,
    guest_email=None,
    rating,
    title=None,
    review_text,
    room_name=None,
    stay_date=None,
    status="pending",
    verified_stay=False,
    featured=False,
    admin_response=None,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    stay = _validate_stay(stay_id)

    guest_name = (guest_name or "").strip()
    review_text = (review_text or "").strip()

    if not guest_name:
        raise ValueError(
            "Guest name is required."
        )

    if not review_text:
        raise ValueError(
            "Review text is required."
        )

    _validate_rating(rating)

    review.stay_id = stay.id
    review.guest_name = guest_name
    review.guest_email = guest_email
    review.rating = rating
    review.title = title
    review.review = review_text
    review.room_name = room_name
    review.stay_date = stay_date
    review.status = status
    review.verified_stay = bool(verified_stay)
    review.featured = bool(featured)
    review.admin_response = admin_response

    db.session.commit()

    return review


# ---------------------------------------------------------------------------
# Moderation
# ---------------------------------------------------------------------------

def approve_stay_review(
    acting_admin,
    review,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.status = "approved"

    db.session.commit()

    return review


def reject_stay_review(
    acting_admin,
    review,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.status = "rejected"
    review.featured = False

    db.session.commit()

    return review


def hide_stay_review(
    acting_admin,
    review,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.status = "hidden"
    review.featured = False

    db.session.commit()

    return review


def set_stay_review_status(
    acting_admin,
    review,
    status,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.status = status

    if status != "approved":
        review.featured = False

    db.session.commit()

    return review


def set_stay_review_verified(
    acting_admin,
    review,
    verified=True,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.verified_stay = bool(verified)

    db.session.commit()

    return review


def set_stay_review_featured(
    acting_admin,
    review,
    featured=True,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    if featured:
        if review.status != "approved":
            raise ValueError(
                "Only approved reviews can be featured."
            )

    review.featured = bool(featured)

    db.session.commit()

    return review


def add_admin_response(
    acting_admin,
    review,
    response,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    review.admin_response = (
        response.strip()
        if isinstance(response, str)
        else response
    )

    db.session.commit()

    return review


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_stay_review(
    acting_admin,
    review,
):
    _require_admin(acting_admin)

    if review is None:
        raise ValueError(
            "Review not found."
        )

    db.session.delete(review)
    db.session.commit()

    return True