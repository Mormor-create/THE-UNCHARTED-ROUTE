"""
===============================================================================
The Uncharted Route
Testimonial Service
===============================================================================
Business logic for managing curated customer testimonials.
Supports:
    - Experiences, stays, and safari package associations.
    - Media Library profile photos, customer photos, and testimonial videos.
    - Legacy photo paths and external video URLs.
    - Testimonial categories and tags.
    - Moderation, verification, featured and homepage controls.
    - Filtering, statistics, and display ordering.
===============================================================================
"""

from extensions import db
from app.models import Testimonial

class TestimonialService:
    """Service layer for testimonial management."""

    # =========================================================================
    # Internal Helpers
    # =========================================================================
    @staticmethod
    def _normalize_optional_id(value):
        """Normalize empty optional foreign-key values to None."""
        if value in ("", 0, "0"):
            return None
        return value

    @staticmethod
    def _validate_rating(rating):
        """Validate and normalize a testimonial rating from 1 to 5."""
        if rating is None:
            return 5

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            raise ValueError("Rating must be between 1 and 5.")

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")

        return rating

    @staticmethod
    def _validate_sort_order(sort_order):
        """Validate and normalize testimonial display order."""
        try:
            sort_order = int(sort_order or 0)
        except (TypeError, ValueError):
            raise ValueError("Sort order must be a whole number.")

        if not 0 <= sort_order <= 9999:
            raise ValueError("Sort order must be between 0 and 9,999.")

        return sort_order

    # =========================================================================
    # Create
    # =========================================================================
    @staticmethod
    def create_testimonial(
            customer_name,
            testimonial,
            experience_id=None,
            stay_id=None,
            safari_package_option_id=None,
            profile_photo_asset_id=None,
            customer_photo_asset_id=None,
            video_asset_id=None,
            customer_country=None,
            customer_email=None,
            customer_city=None,
            company=None,
            position=None,
            title=None,
            short_testimonial=None,
            rating=5,
            profile_photo=None,
            customer_photo=None,
            video_url=None,
            featured=False,
            homepage=False,
            active=True,
            verified=True,
            sort_order=0,
            source=None,
            categories=None,
            tags=None,
    ):
        """Create a testimonial and optionally assign categories and tags."""

        customer_name = (customer_name or "").strip()
        testimonial = (testimonial or "").strip()

        customer_email = (
            customer_email.strip().lower()
            if isinstance(customer_email, str) and customer_email.strip()
            else None
        )

        if not customer_name:
            raise ValueError("Customer name is required.")

        if not testimonial:
            raise ValueError("Testimonial content is required.")

        rating = TestimonialService._validate_rating(rating)
        sort_order = TestimonialService._validate_sort_order(sort_order)

        record = Testimonial(
            # Listing associations
            experience_id=TestimonialService._normalize_optional_id(
                experience_id
            ),
            stay_id=TestimonialService._normalize_optional_id(stay_id),
            safari_package_option_id=(
                TestimonialService._normalize_optional_id(
                    safari_package_option_id
                )
            ),

            # Media Library associations.
            # Admin workflows can use these; public routes should pass None.
            profile_photo_asset_id=(
                TestimonialService._normalize_optional_id(
                    profile_photo_asset_id
                )
            ),
            customer_photo_asset_id=(
                TestimonialService._normalize_optional_id(
                    customer_photo_asset_id
                )
            ),
            video_asset_id=TestimonialService._normalize_optional_id(
                video_asset_id
            ),

            # Customer information
            customer_name=customer_name,
            customer_email=customer_email,
            customer_country=customer_country,
            customer_city=customer_city,
            company=company,
            position=position,

            # Testimonial content
            title=(title.strip() or None) if isinstance(title, str) else title,
            testimonial=testimonial,
            short_testimonial=(
                short_testimonial.strip() or None
                if isinstance(short_testimonial, str)
                else short_testimonial
            ),
            rating=rating,

            # Legacy media fields retained for compatibility.
            # customer_photo is the actual method parameter.
            profile_photo=profile_photo,
            customer_photo=customer_photo,
            video_url=video_url,

            # Display and moderation
            featured=featured,
            homepage=homepage,
            active=active,
            verified=verified,
            sort_order=sort_order,
            source=source,
        )

        try:
            if categories is not None:
                record.categories = list(categories)

            if tags is not None:
                record.tags = list(tags)

            db.session.add(record)
            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Retrieve
    # =========================================================================
    @staticmethod
    def get_by_id(testimonial_id):
        """Retrieve a testimonial by its primary key."""
        return db.session.get(Testimonial, testimonial_id)

    # =========================================================================
    # Get All
    # =========================================================================
    @staticmethod
    def get_all(
        active_only=False,
        verified_only=False,
        featured_only=False,
        homepage_only=False,
        experience_id=None,
        stay_id=None,
        safari_package_option_id=None,
        category_id=None,
    ):
        """Retrieve testimonials using optional filters."""

        query = Testimonial.query

        if active_only:
            query = query.filter(Testimonial.active.is_(True))

        if verified_only:
            query = query.filter(Testimonial.verified.is_(True))

        if featured_only:
            query = query.filter(Testimonial.featured.is_(True))

        if homepage_only:
            query = query.filter(Testimonial.homepage.is_(True))

        if experience_id is not None:
            query = query.filter(
                Testimonial.experience_id == experience_id
            )

        if stay_id is not None:
            query = query.filter(Testimonial.stay_id == stay_id)

        if safari_package_option_id is not None:
            query = query.filter(
                Testimonial.safari_package_option_id
                == safari_package_option_id
            )

        if category_id is not None:
            query = query.filter(
                Testimonial.categories.any(id=category_id)
            )

        return query.order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        ).all()

    # =========================================================================
    # Featured Testimonials
    # =========================================================================
    @staticmethod
    def get_featured(limit=None):
        """Return active, verified, featured testimonials."""

        query = Testimonial.query.filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
            Testimonial.featured.is_(True),
        ).order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    # =========================================================================
    # Homepage Testimonials
    # =========================================================================
    @staticmethod
    def get_homepage_testimonials(limit=None):
        """Return testimonials selected for homepage display."""

        query = Testimonial.query.filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
            Testimonial.homepage.is_(True),
        ).order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    # =========================================================================
    # Listing-Specific Testimonials
    # =========================================================================
    @staticmethod
    def get_for_experience(experience_id):
        """Return active, verified testimonials for an experience."""

        return Testimonial.query.filter(
            Testimonial.experience_id == experience_id,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        ).order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        ).all()

    @staticmethod
    def get_for_stay(stay_id):
        """Return active, verified testimonials for a stay."""

        return Testimonial.query.filter(
            Testimonial.stay_id == stay_id,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        ).order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        ).all()

    @staticmethod
    def get_for_safari(safari_package_option_id):
        """Return active, verified testimonials for a safari package."""

        return Testimonial.query.filter(
            Testimonial.safari_package_option_id
            == safari_package_option_id,
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        ).order_by(
            Testimonial.sort_order.asc(),
            Testimonial.created_at.desc(),
        ).all()

    # =========================================================================
    # Update
    # =========================================================================
    @staticmethod
    def update_testimonial(testimonial_id, **kwargs):
        """Update a testimonial using an explicit field allowlist."""

        record = TestimonialService.get_by_id(testimonial_id)

        if not record:
            return None

        if "customer_name" in kwargs:
            customer_name = (kwargs["customer_name"] or "").strip()

            if not customer_name:
                raise ValueError("Customer name is required.")

            kwargs["customer_name"] = customer_name

        if "testimonial" in kwargs:
            testimonial = (kwargs["testimonial"] or "").strip()

            if not testimonial:
                raise ValueError("Testimonial content is required.")

            kwargs["testimonial"] = testimonial

        if "rating" in kwargs:
            kwargs["rating"] = TestimonialService._validate_rating(
                kwargs["rating"]
            )

        if "sort_order" in kwargs:
            kwargs["sort_order"] = (
                TestimonialService._validate_sort_order(
                    kwargs["sort_order"]
                )
            )

        allowed_fields = {
            # Listing associations
            "experience_id",
            "stay_id",
            "safari_package_option_id",

            # Media Library associations
            "profile_photo_asset_id",
            "customer_photo_asset_id",
            "video_asset_id",

            # Customer information
            "customer_name",
            "customer_country",
            "customer_city",
            "company",
            "position",

            # Content
            "title",
            "testimonial",
            "short_testimonial",
            "rating",

            # Legacy media
            "profile_photo",
            "customer_photo",
            "video_url",

            # Display and moderation
            "featured",
            "homepage",
            "active",
            "sort_order",
            "verified",
            "source",
        }

        try:
            for field, value in kwargs.items():
                if field in allowed_fields:
                    if field.endswith("_id"):
                        value = (
                            TestimonialService._normalize_optional_id(value)
                        )

                    setattr(record, field, value)

            if "categories" in kwargs:
                record.categories = list(kwargs["categories"] or [])

            if "tags" in kwargs:
                record.tags = list(kwargs["tags"] or [])

            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Delete
    # =========================================================================
    @staticmethod
    def delete_testimonial(testimonial_id):
        """Delete a testimonial."""

        record = TestimonialService.get_by_id(testimonial_id)

        if not record:
            return False

        try:
            db.session.delete(record)
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Verification
    # =========================================================================
    @staticmethod
    def verify(testimonial_id):
        """Mark a testimonial as verified."""
        return TestimonialService._set_flag(
            testimonial_id,
            "verified",
            True,
        )

    @staticmethod
    def unverify(testimonial_id):
        """Remove testimonial verification."""
        return TestimonialService._set_flag(
            testimonial_id,
            "verified",
            False,
        )

    # =========================================================================
    # Featured
    # =========================================================================

    @staticmethod
    def feature(testimonial_id):
        """Mark a testimonial as featured."""
        return TestimonialService._set_flag(
            testimonial_id,
            "featured",
            True,
        )

    @staticmethod
    def unfeature(testimonial_id):
        """Remove featured status."""
        return TestimonialService._set_flag(
            testimonial_id,
            "featured",
            False,
        )

    # =========================================================================
    # Homepage
    # =========================================================================

    @staticmethod
    def add_to_homepage(testimonial_id):
        """Enable homepage display."""
        return TestimonialService._set_flag(
            testimonial_id,
            "homepage",
            True,
        )

    @staticmethod
    def remove_from_homepage(testimonial_id):
        """Disable homepage display."""
        return TestimonialService._set_flag(
            testimonial_id,
            "homepage",
            False,
        )

    # =========================================================================
    # Activation
    # =========================================================================

    @staticmethod
    def activate(testimonial_id):
        """Activate a testimonial."""
        return TestimonialService._set_flag(
            testimonial_id,
            "active",
            True,
        )

    @staticmethod
    def deactivate(testimonial_id):
        """Deactivate a testimonial."""
        return TestimonialService._set_flag(
            testimonial_id,
            "active",
            False,
        )

    @staticmethod
    def _set_flag(testimonial_id, field, value):
        """Update a supported boolean moderation/display flag."""

        allowed_flags = {
            "verified",
            "featured",
            "homepage",
            "active",
        }

        if field not in allowed_flags:
            raise ValueError("Unsupported testimonial flag.")

        record = TestimonialService.get_by_id(testimonial_id)

        if not record:
            return None

        try:
            setattr(record, field, value)
            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Display Order
    # =========================================================================

    @staticmethod
    def update_sort_order(testimonial_id, sort_order):
        """Update a testimonial's display order."""

        record = TestimonialService.get_by_id(testimonial_id)

        if not record:
            return None

        sort_order = TestimonialService._validate_sort_order(sort_order)

        try:
            record.sort_order = sort_order
            db.session.commit()
            return record

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Rating Statistics
    # =========================================================================

    @staticmethod
    def get_rating_statistics():
        """Return rating statistics for active, verified testimonials."""

        records = Testimonial.query.filter(
            Testimonial.active.is_(True),
            Testimonial.verified.is_(True),
        ).all()

        ratings = [
            record.rating
            for record in records
            if record.rating is not None
        ]

        count = len(ratings)

        return {
            "count": count,
            "average": round(sum(ratings) / count, 1) if count else 0,
            "five_star": ratings.count(5),
            "four_star": ratings.count(4),
            "three_star": ratings.count(3),
            "two_star": ratings.count(2),
            "one_star": ratings.count(1),
        }

    # =========================================================================
    # Count
    # =========================================================================

    @staticmethod
    def count(
        active_only=False,
        verified_only=False,
        featured_only=False,
        homepage_only=False,
    ):
        """Return testimonial count using optional filters."""

        query = Testimonial.query

        if active_only:
            query = query.filter(Testimonial.active.is_(True))

        if verified_only:
            query = query.filter(Testimonial.verified.is_(True))

        if featured_only:
            query = query.filter(Testimonial.featured.is_(True))

        if homepage_only:
            query = query.filter(Testimonial.homepage.is_(True))

        return query.count()
