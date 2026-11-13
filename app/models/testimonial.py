"""
===============================================================================
The Uncharted Route
Testimonial Model
===============================================================================
Stores curated customer testimonials displayed throughout the website.
Unlike Experience Reviews, testimonials are curated marketing content that may
appear on the homepage, destination pages, landing pages, and promotional
materials.
Testimonials can optionally be linked to an Experience.
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Testimonial Categories and Tags — Many-to-Many Association Tables
# =============================================================================
testimonial_categories = db.Table(
    "testimonial_category_assignments",
    db.Column(
        "testimonial_id",
        db.Integer,
        db.ForeignKey("testimonials.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("testimonial_categories.id", ondelete="CASCADE"),
        primary_key=True,),)

testimonial_tags = db.Table(
    "testimonial_tag_assignments",
    db.Column(
        "testimonial_id",
        db.Integer,
        db.ForeignKey("testimonials.id", ondelete="CASCADE"),
        primary_key=True,),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("testimonial_tags.id", ondelete="CASCADE"),
        primary_key=True,),)

# =============================================================================
# Testimonial Model
# =============================================================================
class Testimonial(db.Model):
    """
    Featured customer testimonials.
    """
    __tablename__ = "testimonials"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Optional Experience Relationship
    # =========================================================================
    experience_id = db.Column(db.Integer,db.ForeignKey("experiences.id"),index=True)
    # =============================================================================
    # Optional Listing Relationships
    # =============================================================================
    stay_id = db.Column(db.Integer,db.ForeignKey("stays.id", ondelete="SET NULL"),nullable=True,index=True,)
    safari_package_option_id = db.Column(db.Integer,db.ForeignKey("safari_package_options.id", ondelete="SET NULL"),nullable=True,index=True,)

    # =============================================================================
    # Optional Central Media Library Relationships
    # =============================================================================
    profile_photo_asset_id = db.Column(db.Integer,db.ForeignKey("media_assets.id", ondelete="SET NULL"),nullable=True,index=True,)
    customer_photo_asset_id = db.Column(db.Integer,db.ForeignKey("media_assets.id", ondelete="SET NULL"),nullable=True,index=True,)

    # =============================================================================
    # Listing Relationships
    # =============================================================================
    stay = db.relationship("Stay",back_populates="testimonials",foreign_keys=[stay_id],)
    safari_package_option = db.relationship("SafariPackageOption",back_populates="testimonials",foreign_keys=[safari_package_option_id],)
    profile_photo_asset = db.relationship("MediaAsset",foreign_keys=[profile_photo_asset_id],)
    customer_photo_asset = db.relationship("MediaAsset",foreign_keys=[customer_photo_asset_id],)

    # =============================================================================
    # Category and Tag Relationships
    # =============================================================================
    categories = db.relationship("TestimonialCategory",secondary=testimonial_categories,back_populates="testimonials",order_by="TestimonialCategory.display_order",)
    tags = db.relationship("TestimonialTag",secondary=testimonial_tags,back_populates="testimonials",order_by="TestimonialTag.name",)

    # =========================================================================
    # Customer Information
    # =========================================================================
    customer_name = db.Column(db.String(150),nullable=False)
    customer_email = db.Column(db.String(255),nullable=True,index=True,)
    customer_country = db.Column(db.String(100))
    customer_city = db.Column(db.String(100))
    company = db.Column(db.String(150))
    position = db.Column(db.String(150))

    # =========================================================================
    # Testimonial Content
    # =========================================================================
    title = db.Column(db.String(255))
    testimonial = db.Column(db.Text,nullable=False)
    short_testimonial = db.Column(db.String(300))

    # =========================================================================
    # Rating
    # =========================================================================
    rating = db.Column(db.Integer,default=5,nullable=False)

    # =========================================================================
    # Media
    # =========================================================================
    profile_photo = db.Column(db.String(255))
    customer_photo = db.Column(db.String(255))
    video_url = db.Column(db.String(500))
    video_asset_id = db.Column(db.Integer,db.ForeignKey("media_assets.id", ondelete="SET NULL"),nullable=True,index=True,)
    video_asset = db.relationship("MediaAsset",foreign_keys=[video_asset_id],)

    # =========================================================================
    # Display
    # =========================================================================
    featured = db.Column(db.Boolean,default=False,nullable=False)
    homepage = db.Column(db.Boolean,default=False,nullable=False)
    active = db.Column(db.Boolean,default=True,nullable=False)
    sort_order = db.Column(db.Integer,default=0,nullable=False)

    # =========================================================================
    # Verification
    # =========================================================================
    verified = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    experience = db.relationship("Experience",back_populates="testimonials")

    # =========================================================================
    # Source / Marketing
    # =========================================================================
    source = db.Column(db.String(100))
    # Examples:
    # Website
    # Google
    # TripAdvisor
    # Facebook
    # LinkedIn
    # Email

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def stars(self):
        """
        Return the testimonial rating as star characters.
        """
        return "★" * self.rating

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return f"<Testimonial {self.customer_name}>"