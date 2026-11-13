"""
===============================================================================
The Uncharted Route
Experience Safety Rule Model
===============================================================================

Stores safety guidelines for an experiences.

Examples

• Stay inside the safari vehicle.
• Wear comfortable walking shoes.
• Follow your guide's instructions.
• Carry sufficient drinking water.
• Do not feed wildlife.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Experience Safety Rule Model
# =============================================================================

class ExperienceSafetyRule(db.Model):
    """
    Represents one safety rule for an experiences.
    """

    __tablename__ = "experience_safety_rules"

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
    # Safety Information
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
    # Wildlife
    # Health
    # Hiking
    # Water Safety
    # Transport
    # Weather
    # Emergency

    priority = db.Column(
        db.String(20),
        default="Medium",
        nullable=False
    )
    # Low
    # Medium
    # High
    # Critical

    icon = db.Column(
        db.String(100),
        default="shield-check"
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
        back_populates="safety_rules"
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
            f"<ExperienceSafetyRule {self.title}>"
        )