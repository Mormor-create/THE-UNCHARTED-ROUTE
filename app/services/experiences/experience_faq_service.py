"""
===============================================================================
The Uncharted Route
Experience FAQ Service
===============================================================================

Business logic for managing Frequently Asked Questions attached to experiences.

Responsibilities
----------------
• Create FAQs
• Retrieve FAQs
• Update FAQs
• Delete FAQs
• Activate / deactivate FAQs
• Feature / unfeature FAQs
• Reorder FAQs
• Filter FAQs by category
• Retrieve featured FAQs
"""

from extensions import db
from app.models import ExperienceFAQ


# =============================================================================
# Experience FAQ Service
# =============================================================================


class ExperienceFAQService:
    """
    Service layer for Experience FAQ operations.
    """

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_faq(
        experience_id,
        question,
        answer,
        category="General",
        display_order=0,
        featured=False,
        active=True
    ):
        """
        Create a new FAQ for an experiences.
        """

        if not question or not question.strip():
            raise ValueError("FAQ question is required.")

        if not answer or not answer.strip():
            raise ValueError("FAQ answer is required.")

        faq = ExperienceFAQ(
            experience_id=experience_id,
            question=question.strip(),
            answer=answer.strip(),
            category=category or "General",
            display_order=display_order,
            featured=featured,
            active=active
        )

        db.session.add(faq)
        db.session.commit()

        return faq

    # =========================================================================
    # Retrieve
    # =========================================================================

    @staticmethod
    def get_by_id(faq_id):
        """
        Retrieve an FAQ by ID.
        """

        return ExperienceFAQ.query.get(faq_id)

    # -------------------------------------------------------------------------

    @staticmethod
    def get_or_404(faq_id):
        """
        Retrieve an FAQ or raise a 404 error.
        """

        return ExperienceFAQ.query.get_or_404(faq_id)

    # -------------------------------------------------------------------------

    @staticmethod
    def get_for_experience(
        experience_id,
        active_only=True
    ):
        """
        Retrieve FAQs belonging to an experiences.
        """

        query = ExperienceFAQ.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.order_by(
            ExperienceFAQ.display_order.asc(),
            ExperienceFAQ.id.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_featured_for_experience(experience_id):
        """
        Retrieve featured FAQs for an experiences.
        """

        return ExperienceFAQ.query.filter_by(
            experience_id=experience_id,
            featured=True,
            active=True
        ).order_by(
            ExperienceFAQ.display_order.asc()
        ).all()

    # -------------------------------------------------------------------------

    @staticmethod
    def get_by_category(
        experience_id,
        category,
        active_only=True
    ):
        """
        Retrieve FAQs for an experiences by category.
        """

        query = ExperienceFAQ.query.filter_by(
            experience_id=experience_id,
            category=category
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.order_by(
            ExperienceFAQ.display_order.asc(),
            ExperienceFAQ.id.asc()
        ).all()

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_faq(
        faq_id,
        question=None,
        answer=None,
        category=None,
        display_order=None,
        featured=None,
        active=None
    ):
        """
        Update an existing FAQ.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        if question is not None:
            if not question.strip():
                raise ValueError("FAQ question cannot be empty.")

            faq.question = question.strip()

        if answer is not None:
            if not answer.strip():
                raise ValueError("FAQ answer cannot be empty.")

            faq.answer = answer.strip()

        if category is not None:
            faq.category = category.strip() or "General"

        if display_order is not None:
            faq.display_order = display_order

        if featured is not None:
            faq.featured = bool(featured)

        if active is not None:
            faq.active = bool(active)

        db.session.commit()

        return faq

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete_faq(faq_id):
        """
        Permanently delete an FAQ.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        db.session.delete(faq)
        db.session.commit()

        return True

    # =========================================================================
    # Status Management
    # =========================================================================

    @staticmethod
    def activate(faq_id):
        """
        Activate an FAQ.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        faq.active = True

        db.session.commit()

        return faq

    # -------------------------------------------------------------------------

    @staticmethod
    def deactivate(faq_id):
        """
        Deactivate an FAQ without deleting it.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        faq.active = False

        db.session.commit()

        return faq

    # =========================================================================
    # Featured Management
    # =========================================================================

    @staticmethod
    def feature(faq_id):
        """
        Mark an FAQ as featured.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        faq.featured = True

        db.session.commit()

        return faq

    # -------------------------------------------------------------------------

    @staticmethod
    def unfeature(faq_id):
        """
        Remove the featured status from an FAQ.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        faq.featured = False

        db.session.commit()

        return faq

    # =========================================================================
    # Ordering
    # =========================================================================

    @staticmethod
    def reorder(faq_id, display_order):
        """
        Change the display order of an FAQ.
        """

        faq = ExperienceFAQ.query.get(faq_id)

        if not faq:
            raise ValueError("FAQ not found.")

        faq.display_order = display_order

        db.session.commit()

        return faq

    # =========================================================================
    # Bulk Ordering
    # =========================================================================

    @staticmethod
    def reorder_many(order_data):
        """
        Reorder multiple FAQs.

        Expected format:

        [
            {"id": 1, "display_order": 0},
            {"id": 5, "display_order": 1},
            {"id": 3, "display_order": 2}
        ]
        """

        if not order_data:
            return []

        updated = []

        for item in order_data:
            faq_id = item.get("id")
            display_order = item.get("display_order")

            faq = ExperienceFAQ.query.get(faq_id)

            if not faq:
                continue

            faq.display_order = display_order
            updated.append(faq)

        db.session.commit()

        return updated

    # =========================================================================
    # Counting
    # =========================================================================

    @staticmethod
    def count_for_experience(
        experience_id,
        active_only=True
    ):
        """
        Count FAQs belonging to an experiences.
        """

        query = ExperienceFAQ.query.filter_by(
            experience_id=experience_id
        )

        if active_only:
            query = query.filter_by(active=True)

        return query.count()