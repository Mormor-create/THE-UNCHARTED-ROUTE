"""
===============================================================================
The Uncharted Route
Destination Model
===============================================================================
Represents destinations offered by The Uncharted Route.
Examples:
- Nairobi
- Maasai Mara
- Amboseli
- Tsavo
- Diani
- Watamu
- Samburu
- Mount Kenya
Each destination can contain multiple experiences.
"""
from datetime import datetime
from extensions import db

# =============================================================================
# Destination Model
# =============================================================================
class Destination(db.Model):
    """
    Represents a travel destination.
    """
    __tablename__ = "destinations"
    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------
    id = db.Column(db.Integer,primary_key=True)

    # -------------------------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------------------------
    name = db.Column(db.String(150),nullable=False,unique=True,index=True)
    slug = db.Column(db.String(170),nullable=False,unique=True,index=True)
    country = db.Column(db.String(100),nullable=False,default="Kenya")
    county = db.Column(db.String(100))
    region = db.Column(db.String(100))

    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    short_description = db.Column(db.String(300))
    description = db.Column(db.Text)

    # -------------------------------------------------------------------------
    # Images
    # -------------------------------------------------------------------------
    featured_image_id = db.Column(db.Integer,db.ForeignKey("media_assets.id"),nullable=True)
    banner_image_id = db.Column(db.Integer,db.ForeignKey("media_assets.id"),nullable=True)
    featured_image_asset = db.relationship("MediaAsset",foreign_keys=[featured_image_id])
    banner_image_asset = db.relationship("MediaAsset",foreign_keys=[banner_image_id])

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # -------------------------------------------------------------------------
    # SEO
    # -------------------------------------------------------------------------
    meta_title = db.Column(db.String(160))
    meta_description = db.Column(db.String(300))

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------
    featured = db.Column(db.Boolean,default=False,nullable=False)
    show_on_homepage = db.Column(db.Boolean,default=False,nullable=False,index=True,)
    active = db.Column(db.Boolean,default=True,nullable=False)

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------
    experiences = db.relationship("Experience",back_populates="destination",lazy="dynamic",cascade="all, delete-orphan")
    stays = db.relationship("Stay",back_populates="destination",lazy="dynamic",cascade="all, delete-orphan")

    # -------------------------------------------------------------------------
    # Audit Fields
    # -------------------------------------------------------------------------
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # -------------------------------------------------------------------------
    # Helper Properties
    # -------------------------------------------------------------------------

    @property
    def experience_count(self):
        """
        Number of experiences under this destination.
        """
        return self.experiences.count()

    @property
    def stay_count(self):
        return self.stays.count()

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __repr__(self):
        return f"<Destination {self.name}>"