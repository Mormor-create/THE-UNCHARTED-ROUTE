"""
===============================================================================
The Uncharted Route
Accessibility Model
===============================================================================
Reusable accessibility profiles that describe how accessible an experiences is.
Accessibility information is intentionally separated from Experience so that
multiple experiences with identical accessibility characteristics can reuse
the same profile.

Examples
• Fully Accessible
• Family Friendly
• Luxury Accessible
• Moderate Hiking Required
• High Adventure
"""

from datetime import datetime

from extensions import db

# =============================================================================
# Accessibility Model
# =============================================================================
class Accessibility(db.Model):
    """
    Reusable accessibility profile.
    """
    __tablename__ = "accessibility_profiles"
    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = db.Column(db.String(120),nullable=False,unique=True)
    slug = db.Column(db.String(150),unique=True,index=True)
    summary = db.Column(db.Text)

    # =========================================================================
    # Mobility
    # =========================================================================
    wheelchair_accessible = db.Column(db.Boolean,default=False,nullable=False)
    stroller_friendly = db.Column(db.Boolean,default=False,nullable=False)
    walking_required = db.Column(db.Boolean,default=True,nullable=False)
    hiking_required = db.Column(db.Boolean,default=False,nullable=False)
    uneven_terrain = db.Column(db.Boolean,default=False,nullable=False)
    stairs_required = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Guest Suitability
    # =========================================================================
    child_friendly = db.Column(db.Boolean,default=True,nullable=False)
    elderly_friendly = db.Column(db.Boolean,default=True,nullable=False)
    pregnancy_friendly = db.Column(db.Boolean,default=True,nullable=False)
    pet_friendly = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Physical Requirements
    # =========================================================================
    minimum_fitness_level = db.Column(db.String(50),default="Very Low")
    # Very Low
    # Moderate
    # Active
    # Challenging
    # Extreme

    maximum_altitude_meters = db.Column(db.Integer)

    # =========================================================================
    # Facilities
    # =========================================================================
    accessible_restrooms = db.Column(db.Boolean,default=False,nullable=False)
    changing_facilities = db.Column(db.Boolean,default=False,nullable=False)
    medical_support_available = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Dietary Support
    # =========================================================================
    vegetarian_available = db.Column(db.Boolean,default=False )
    vegan_available = db.Column(db.Boolean,default=False)
    halal_available = db.Column(db.Boolean,default=False)
    kosher_available = db.Column(db.Boolean,default=False)
    gluten_free_available = db.Column(db.Boolean,default=False)
    allergy_support = db.Column(db.Boolean,default=False)

    # =========================================================================
    # Communication
    # =========================================================================
    multilingual_guides = db.Column(db.Boolean,default=True)
    sign_language_available = db.Column(db.Boolean,default=False)
    braille_materials = db.Column(db.Boolean,default=False)
    audio_guides = db.Column(db.Boolean,default=False)

    # =========================================================================
    # Additional Information
    # =========================================================================
    notes = db.Column(db.Text)

    # =========================================================================
    # Status
    # =========================================================================
    active = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    experiences = db.relationship("Experience",back_populates="accessibility_profile",lazy="dynamic")

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def family_friendly(self):
        return (
            self.child_friendly
            and self.elderly_friendly)

    @property
    def fully_accessible(self):
        return (
            self.wheelchair_accessible
            and self.accessible_restrooms)

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return f"<Accessibility {self.name}>"