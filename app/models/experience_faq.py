"""
===============================================================================
The Uncharted Route
Experience FAQ Model
===============================================================================

Stores Frequently Asked Questions (FAQs) for an experiences.

Examples

• Is transport included?
• Can children join?
• What happens if it rains?
• Are meals provided?
• Can dietary requirements be accommodated?
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience FAQ Model
# =============================================================================

class ExperienceFAQ(db.Model):
    """
    Represents a Frequently Asked Question for an experiences.
    """

    __tablename__ = "experience_faqs"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------------------------
    # Experience Relationship
    # -------------------------------------------------------------------------

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey("experiences.id"),
        nullable=False
    )

    # -------------------------------------------------------------------------
    # FAQ Content
    # -------------------------------------------------------------------------

    question = db.Column(
        db.String(500),
        nullable=False
    )

    answer = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        default="General",
        nullable=False
    )
    # Examples:
    # Booking
    # Transport
    # Accommodation
    # Meals
    # Wildlife
    # Children
    # Accessibility
    # Weather

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------

    experiences = db.relationship(
        "Experience",
        back_populates="faqs"
    )

    # -------------------------------------------------------------------------
    # Audit Fields
    # -------------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<ExperienceFAQ {self.question}>"
        )