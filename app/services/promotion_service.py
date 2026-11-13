"""
===============================================================================
The Uncharted Route
Promotion Service
===============================================================================
Business logic for managing poster-first promotions and promotion inquiries.
Responsibilities:
- Promotions Media Library integration.
- Promotion poster validation.
- Promotion slug generation.
- Public promotion retrieval.
- Promotion creation, updating and deletion.
- Customer promotion inquiry submission.
- Promotion inquiry retrieval, filtering and management.
Promotions use an inquiry-based process. They do not create bookings.

===============================================================================
"""
import re
from sqlalchemy import or_
from app.models.promotion import (
    Promotion,
    PromotionInquiry,)
from app.services.media_service import (
    get_cms_media_assets,
    get_media_folder_by_slug,
)

from extensions import db


class PromotionService:
    """Business logic for promotions and promotion inquiries."""

    PROMOTIONS_FOLDER_SLUG = "promotions"

    INQUIRY_STATUSES = [
        "new",
        "in_progress",
        "contacted",
        "converted",
        "closed",
    ]

    CONTACT_METHODS = [
        "email",
        "phone",
        "whatsapp",
    ]

    # =========================================================================
    # Promotions Media Folder
    # =========================================================================

    @classmethod
    def get_promotions_folder(cls):
        """
        Retrieve the root Promotions folder.

        The folder must exist and be active.
        """

        folder = get_media_folder_by_slug(
            cls.PROMOTIONS_FOLDER_SLUG
        )

        if folder is None or not folder.active:
            return None

        return folder

    @classmethod
    def get_promotion_posters(cls):
        """
        Retrieve active image assets from the Promotions folder
        and all active descendant folders.
        """

        folder = cls.get_promotions_folder()

        if folder is None:
            return []

        return get_cms_media_assets(
            folder_id=folder.id,
            include_descendants=True,
            media_type="image",
            active_only=True,
        )

    @classmethod
    def get_poster_choices(cls):
        """Build WTForms choices from eligible promotion posters."""

        choices = []

        for asset in cls.get_promotion_posters():
            label = (
                asset.title
                or asset.original_filename
                or asset.filename
                or f"Media asset #{asset.id}"
            )

            choices.append(
                (asset.id, label)
            )

        return choices

    @classmethod
    def get_poster_preview_map(cls):
        """Build poster preview URLs for eligible promotion images."""

        return {
            str(asset.id): asset.browser_url
            for asset in cls.get_promotion_posters()
            if asset.browser_url
        }

    @classmethod
    def validate_poster(cls, media_asset_id):
        """
        Validate that a poster is an active image assigned to
        the Promotions folder or one of its active descendants.

        This is the server-side validation check.
        """

        if not media_asset_id:
            return None

        try:
            media_asset_id = int(media_asset_id)
        except (TypeError, ValueError):
            return None

        for asset in cls.get_promotion_posters():
            if asset.id == media_asset_id:
                return asset

        return None

    # =========================================================================
    # Slug Helpers
    # =========================================================================

    @staticmethod
    def slugify(value):
        """Convert a promotion title into a URL-friendly slug."""

        value = (value or "").strip().lower()
        value = re.sub(r"[^\w\s-]", "", value)
        value = re.sub(r"[\s\\_-]+", "-", value)

        return value.strip("-") or "offer"

    @classmethod
    def generate_unique_slug(cls, title, promotion_id=None):
        """Generate a unique promotion slug."""

        base_slug = cls.slugify(title)
        candidate = base_slug
        counter = 2

        while True:
            query = Promotion.query.filter_by(
                slug=candidate
            )

            if promotion_id is not None:
                query = query.filter(
                    Promotion.id != promotion_id
                )

            if query.first() is None:
                return candidate

            candidate = f"{base_slug}-{counter}"
            counter += 1

    # =========================================================================
    # Public Promotions
    # =========================================================================

    @staticmethod
    def get_public_query():
        """Return published promotions within their validity dates."""

        from datetime import date

        today = date.today()

        return Promotion.query.filter(
            Promotion.status == "published",
            or_(
                Promotion.starts_at.is_(None),
                Promotion.starts_at <= today,
            ),
            or_(
                Promotion.ends_at.is_(None),
                Promotion.ends_at >= today,
            ),
        )

    @classmethod
    def get_public_promotions(cls):
        """Retrieve all currently available public promotions."""

        return (
            cls.get_public_query()
            .order_by(
                Promotion.created_at.desc(),
                Promotion.id.desc(),
            )
            .all()
        )

    @classmethod
    def get_public_promotion_by_slug(cls, slug):
        """Retrieve one currently available promotion by slug."""

        if not slug:
            return None

        return cls.get_public_query().filter_by(
            slug=slug
        ).first()

    # =========================================================================
    # Create Promotion
    # =========================================================================

    @classmethod
    def create_promotion(cls, form):
        """Create a new poster-first promotion."""

        poster = cls.validate_poster(
            form.poster_media_asset_id.data
        )

        if poster is None:
            raise ValueError(
                "The selected poster is unavailable or is not assigned "
                "to the Promotions folder. Choose an active image from "
                "the Promotions folder in the Media Library."
            )

        title = (form.title.data or "").strip()

        if not title:
            raise ValueError(
                "A promotion title is required."
            )

        promotion = Promotion(
            title=title,
            slug=cls.generate_unique_slug(title),
            description=(
                (form.description.data or "").strip() or None
            ),
            poster_media_asset_id=poster.id,
            starts_at=form.starts_at.data,
            ends_at=form.ends_at.data,
            status=form.status.data,
            show_on_homepage=bool(
                form.show_on_homepage.data
            ),
        )

        try:
            db.session.add(promotion)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return promotion

    # =========================================================================
    # Update Promotion
    # =========================================================================

    @classmethod
    def update_promotion(cls, promotion, form):
        """Update an existing promotion."""

        poster = cls.validate_poster(
            form.poster_media_asset_id.data
        )

        if poster is None:
            raise ValueError(
                "The selected poster is unavailable or is not assigned "
                "to the Promotions folder. Choose an active image from "
                "the Promotions folder in the Media Library."
            )

        title = (form.title.data or "").strip()

        if not title:
            raise ValueError(
                "A promotion title is required."
            )

        promotion.title = title

        promotion.slug = cls.generate_unique_slug(
            title,
            promotion_id=promotion.id,
        )

        promotion.description = (
            (form.description.data or "").strip() or None
        )

        promotion.poster_media_asset_id = poster.id
        promotion.starts_at = form.starts_at.data
        promotion.ends_at = form.ends_at.data
        promotion.status = form.status.data

        promotion.show_on_homepage = bool(
            form.show_on_homepage.data
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return promotion

    # =========================================================================
    # Delete Promotion
    # =========================================================================

    @staticmethod
    def delete_promotion(promotion):
        """
        Delete a promotion.

        The Media Library poster is not deleted.
        Associated inquiries are retained through the SET NULL
        foreign key relationship.
        """

        try:
            db.session.delete(promotion)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Promotion Inquiry Validation
    # =========================================================================

    @staticmethod
    def validate_inquiry_status(status):
        """Validate an inquiry status."""

        return status in PromotionService.INQUIRY_STATUSES

    @staticmethod
    def validate_contact_method(contact_method):
        """Validate a preferred customer contact method."""

        return contact_method in PromotionService.CONTACT_METHODS

    # =========================================================================
    # Create Promotion Inquiry
    # =========================================================================

    @classmethod
    def create_promotion_inquiry(cls, promotion, form):
        """
        Create a customer inquiry for a currently available promotion.

        Promotion association and title are taken from the server-side
        promotion object, never from visitor-submitted values.

        This method does not create a booking.
        """

        if promotion is None:
            raise ValueError(
                "The requested promotion could not be found."
            )

        if not promotion.is_currently_available:
            raise ValueError(
                "This promotion is currently unavailable for inquiries."
            )

        customer_name = (
            form.customer_name.data or ""
        ).strip()

        email = (
            form.email.data or ""
        ).strip().lower()

        phone = (
            form.phone.data or ""
        ).strip()

        country = (
            form.country.data or ""
        ).strip() or None

        contact_method = (
            form.contact_method.data or "email"
        ).strip().lower()

        message = (
            form.message.data or ""
        ).strip()

        if not customer_name:
            raise ValueError(
                "Customer name is required."
            )

        if not email:
            raise ValueError(
                "Customer email address is required."
            )

        if not phone:
            raise ValueError(
                "Customer phone number is required."
            )

        if not message:
            raise ValueError(
                "An inquiry message is required."
            )

        if not cls.validate_contact_method(contact_method):
            raise ValueError(
                "Please select a valid contact method."
            )

        inquiry = PromotionInquiry(
            promotion_id=promotion.id,
            promotion_title=promotion.title,
            customer_name=customer_name,
            email=email,
            phone=phone,
            country=country,
            contact_method=contact_method,
            message=message,
            status="new",
        )

        try:
            db.session.add(inquiry)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return inquiry

    # =========================================================================
    # Retrieve Promotion Inquiries
    # =========================================================================

    @staticmethod
    def get_inquiries_query(
        status=None,
        promotion_id=None,
        search=None,
    ):
        """
        Build a filtered promotion inquiries query.

        Supported filters:
        - Inquiry status.
        - Promotion ID.
        - Customer name.
        - Customer email.
        - Customer phone number.
        """

        query = PromotionInquiry.query

        if status:
            query = query.filter(
                PromotionInquiry.status == status
            )

        if promotion_id:
            query = query.filter(
                PromotionInquiry.promotion_id == promotion_id
            )

        if search:
            search_term = f"%{search.strip()}%"

            query = query.filter(
                or_(
                    PromotionInquiry.customer_name.ilike(
                        search_term
                    ),
                    PromotionInquiry.email.ilike(
                        search_term
                    ),
                    PromotionInquiry.phone.ilike(
                        search_term
                    ),
                    PromotionInquiry.promotion_title.ilike(
                        search_term
                    ),
                )
            )

        return query

    @classmethod
    def get_inquiries(
        cls,
        status=None,
        promotion_id=None,
        search=None,
        page=None,
        per_page=20,
    ):
        """
        Retrieve promotion inquiries.

        If page is supplied, return a Flask-SQLAlchemy pagination object.
        Otherwise, return a list.
        """

        query = cls.get_inquiries_query(
            status=status,
            promotion_id=promotion_id,
            search=search,
        )

        query = query.order_by(
            PromotionInquiry.submitted_at.desc(),
            PromotionInquiry.id.desc(),
        )

        if page is not None:
            return query.paginate(
                page=page,
                per_page=per_page,
                error_out=False,
            )

        return query.all()

    @staticmethod
    def get_inquiry_by_id(inquiry_id):
        """Retrieve an individual promotion inquiry."""

        if not inquiry_id:
            return None

        return db.session.get(
            PromotionInquiry,
            inquiry_id,
        )

    # =========================================================================
    # Update Promotion Inquiry
    # =========================================================================

    @classmethod
    def update_promotion_inquiry(
        cls,
        inquiry,
        status,
        admin_notes=None,
    ):
        """
        Update inquiry follow-up status and internal notes.

        This operation does not modify the original customer submission.
        """

        if inquiry is None:
            raise ValueError(
                "The promotion inquiry could not be found."
            )

        if not cls.validate_inquiry_status(status):
            raise ValueError(
                "Please select a valid inquiry status."
            )

        inquiry.status = status

        inquiry.admin_notes = (
            (admin_notes or "").strip() or None
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return inquiry

    # =========================================================================
    # Promotion Inquiry Statistics
    # =========================================================================

    @staticmethod
    def get_inquiry_counts():
        """Retrieve inquiry counts grouped by status."""

        counts = {
            status: 0
            for status in PromotionService.INQUIRY_STATUSES
        }

        results = (
            db.session.query(
                PromotionInquiry.status,
                db.func.count(PromotionInquiry.id),
            )
            .group_by(
                PromotionInquiry.status
            )
            .all()
        )

        for status, count in results:
            if status in counts:
                counts[status] = count

        counts["total"] = sum(counts.values())

        return counts
