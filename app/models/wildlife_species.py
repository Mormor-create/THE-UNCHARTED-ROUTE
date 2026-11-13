"""
===============================================================================
The Uncharted Route
Wildlife Species Model
===============================================================================
Stores wildlife species that may be encountered during experiences.
Examples

• African Lion
• African Elephant
• Black Rhinoceros
• Masai Giraffe
• Cheetah
• Leopard
• Hippopotamus
• Nile Crocodile
• Grevy's Zebra
• Flamingo
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Wildlife Species Model
# =============================================================================

class WildlifeSpecies(db.Model):
    """
    Represents a wildlife species.
    """

    __tablename__ = "wildlife_species"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Identification
    # =========================================================================
    common_name = db.Column(db.String(255),nullable=False,unique=True)
    scientific_name = db.Column(db.String(255))
    family = db.Column(db.String(255))

    # =========================================================================
    # Classification
    # =========================================================================
    animal_class = db.Column(db.String(100),nullable=False)
    # Mammal
    # Bird
    # Reptile
    # Amphibian
    # Fish
    # Insect

    category = db.Column(db.String(100))
    # Big Five
    # Big Cats
    # Herbivore
    # Carnivore
    # Bird of Prey
    # Water Bird
    # Marine Life
    # Primate

    # =========================================================================
    # Conservation
    # =========================================================================
    conservation_status = db.Column(db.String(100))
    # Least Concern
    # Near Threatened
    # Vulnerable
    # Endangered
    # Critically Endangered

    protected = db.Column(db.Boolean,default=False,nullable=False)
    endemic = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Information
    # =========================================================================
    description = db.Column(db.Text)
    interesting_fact = db.Column(db.Text)
    habitat = db.Column(db.String(255))
    diet = db.Column(db.String(255))
    best_viewing_time = db.Column(db.String(255))

    # =========================================================================
    # Photography
    # =========================================================================
    photography_difficulty = db.Column(db.String(50),default="Medium")
    # Easy
    # Medium
    # Difficult

    # =========================================================================
    # Display
    # =========================================================================
    featured = db.Column(db.Boolean,default=False,nullable=False)
    active = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    experiences = db.relationship(
        "ExperienceWildlife",
        back_populates="species",
        cascade="all, delete-orphan",
        lazy="dynamic")

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def experience_count(self):
        return self.experiences.count()

    @property
    def is_big_five(self):
        return self.category == "Big Five"

    @property
    def is_endangered(self):
        return self.conservation_status in [
            "Endangered",
            "Critically Endangered"]

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return f"<WildlifeSpecies {self.common_name}>"