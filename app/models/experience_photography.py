"""
===============================================================================
The Uncharted Route
Experience Photography Model
===============================================================================

Represents a photography location that can be used in one or more experiences.

Examples

• Lion Rock
• Mara River Crossing Point
• Observation Hill
• Hippo Pool
• Rhino Viewpoint
• Sunset Ridge
• Giraffe Feeding Platform

A photography spot may belong to many experiences.

===============================================================================
The Uncharted Route
Experience Photography Model

Connects travel experiences with photography spots.

An experiences may contain multiple photography stops, and a photography
spot may be associated with multiple experiences.
===============================================================================
"""

from extensions import db


class ExperiencePhotography(db.Model):
    """
    Association model connecting an Experience with a PhotographySpot.
    """

    __tablename__ = "experience_photography"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================================
    # Foreign Keys
    # =========================================================================

    experience_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "experiences.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    photography_spot_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "photography_spots.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =========================================================================
    # Photography Stop Information
    # =========================================================================

    stop_order = db.Column(
        db.Integer,
        nullable=False,
        default=0
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

    # =========================================================================
    # Experience-Specific Notes
    # =========================================================================

    notes = db.Column(
        db.Text
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    experiences = db.relationship(
        "Experience",
        back_populates="photography_spots"
    )

    spot = db.relationship(
        "PhotographySpot",
        back_populates="experiences"
    )

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ExperiencePhotography "
            f"experience_id={self.experience_id} "
            f"photography_spot_id={self.photography_spot_id}>"
        )