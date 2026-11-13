"""
===============================================================================
The Uncharted Route
Experience Pricing Model
===============================================================================
Stores pricing tiers for each experience.
One experience can have multiple pricing options.
Examples
Explorer
Signature
Luxury
Bespoke
as well as different group sizes.
"""
from datetime import datetime
from extensions import db
# =============================================================================
# Experience Pricing Model
# =============================================================================
class ExperiencePricing(db.Model):
    """
    Pricing options for an experiences.
    """
    __tablename__ = "experience_pricing"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------
    id = db.Column(db.Integer,primary_key=True)

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------
    experience_id = db.Column(db.Integer,db.ForeignKey("experiences.id"),nullable=False)

    # -------------------------------------------------------------------------
    # Pricing Tier
    # -------------------------------------------------------------------------
    experience_level = db.Column(db.String(50),nullable=False)
    # Explorer
    # Signature
    # Luxury
    # Bespoke

    # -------------------------------------------------------------------------
    # Group Size
    # -------------------------------------------------------------------------
    minimum_people = db.Column(db.Integer,default=1,nullable=False)
    maximum_people = db.Column(db.Integer)

    # -------------------------------------------------------------------------
    # Price
    # -------------------------------------------------------------------------
    price = db.Column(db.Float,nullable=False)
    currency = db.Column(db.String(10),default="KES",nullable=False)

    # -------------------------------------------------------------------------
    # Optional Notes
    # -------------------------------------------------------------------------
    notes = db.Column(db.String(255))

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    display_order = db.Column(db.Integer,default=0)
    active = db.Column(db.Boolean,default=True,nullable=False)

    # -------------------------------------------------------------------------
    # Relationship
    # -------------------------------------------------------------------------
    experiences = db.relationship("Experience",back_populates="pricing")
    bookings = db.relationship("ExperienceBooking",back_populates="pricing",lazy="dynamic",)

    # -------------------------------------------------------------------------
    # Audit Fields
    # -------------------------------------------------------------------------
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # -------------------------------------------------------------------------
    # Helper Properties
    # -------------------------------------------------------------------------
    @property
    def formatted_price(self):
        return f"{self.currency} {self.price:,.0f}"

    @property
    def group_label(self):
        """
        Returns:
        1 Person
        2–3 People
        4+ People
        """

        if self.maximum_people is None:
            return f"{self.minimum_people}+ People"
        if self.minimum_people == self.maximum_people:
            return f"{self.minimum_people} Person"
        return f"{self.minimum_people}–{self.maximum_people} People"

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------
    def __repr__(self):
        return (
            f"<ExperiencePricing "
            f"{self.experience_level} "
            f"{self.formatted_price}>")