
"""
===============================================================================
The Uncharted Route
Experience Category Model
===============================================================================

Represents the major categories of experiences offered by
The Uncharted Route.

Examples:

- Wildlife & Conservation
- Coastal Experiences
- Adventure
- Luxury
- Family & Group
- Corporate
- Culture & Heritage
- Wellness

Each category contains multiple experiences.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Experience Category Model
# =============================================================================

class ExperienceCategory(db.Model):
    """
    Represents an experiences category.
    """

    __tablename__ = "experience_categories"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------
    id = db.Column(db.Integer,primary_key=True)

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------
    name = db.Column(db.String(150),nullable=False,unique=True,index=True)
    slug = db.Column(db.String(170),nullable=False,unique=True,index=True)
    icon = db.Column(db.String(100))
    color = db.Column(db.String(20),default="#0F766E")

    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    short_description = db.Column(db.String(300))
    description = db.Column(db.Text)

    # -------------------------------------------------------------------------
    # Images
    # -------------------------------------------------------------------------
    featured_image = db.Column(db.String(255))
    banner_image = db.Column(db.String(255))

    # -------------------------------------------------------------------------
    # Homepage Display
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
    # Relationships
    # -------------------------------------------------------------------------

    experiences = db.relationship(
        "Experience",
        back_populates="category",
        lazy="dynamic",
        cascade="all, delete-orphan"
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
    # Helper Properties
    # -------------------------------------------------------------------------

    @property
    def experience_count(self):
        """
        Return the number of experiences
        in this category.
        """
        return self.experiences.count()

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<ExperienceCategory {self.name}>"
        )