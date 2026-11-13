"""
===============================================================================
The Uncharted Route
Experience Requirement Model
===============================================================================

Stores participation requirements for an experiences.

Examples

• Minimum Age: 12 Years
• Valid Passport Required
• Moderate Fitness Level
• Closed Shoes Required
• Swimming Ability Recommended
• Maximum Weight Limit
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Requirement Model
# =============================================================================

class ExperienceRequirement(db.Model):
    """
    Represents one participation requirement for an experiences.
    """

    __tablename__ = "experience_requirements"

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
    # Requirement Information
    # -------------------------------------------------------------------------

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    category = db.Column(
        db.String(100),
        default="General",
        nullable=False
    )
    # Examples:
    # Age
    # Fitness
    # Documentation
    # Clothing
    # Health
    # Equipment
    # Legal

    mandatory = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    icon = db.Column(
        db.String(100),
        default="clipboard-check"
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    display_order = db.Column(
        db.Integer,
        default=0,
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
        back_populates="requirements"
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
            f"<ExperienceRequirement {self.title}>"
        )