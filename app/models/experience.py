"""
===============================================================================
The Uncharted Route
Experience Model
===============================================================================
Represents every experience offered by The Uncharted Route.
Examples
--------
- WNA-001 Nairobi National Park
- WNA-002 Giraffe Centre
- COE-WEL-001 Beach Wellness Escape
- ADV-001 Mount Kenya Trek
- LUX-001 Luxury Maasai Mara Safari
This is the core model powering the website.
"""
from datetime import datetime
from app.models.experience_media import ExperienceMedia
from extensions import db
# =============================================================================
# Experience Model
# =============================================================================
class Experience(db.Model):
    """
    Represents a travel experience.
    """
    __tablename__ = "experiences"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Identity
    # =========================================================================
    experience_code = db.Column(db.String(30),unique=True,nullable=False,index=True)
    title = db.Column(db.String(200),nullable=False,index=True)
    slug = db.Column(db.String(220),unique=True,nullable=False,index=True)

    # =========================================================================
    # Descriptions
    # =========================================================================
    short_description = db.Column(db.String(350),nullable=False)
    description = db.Column(db.Text,nullable=False)

    # =========================================================================
    # Logistics
    # =========================================================================
    duration = db.Column(db.String(100))
    meeting_point = db.Column(db.String(255))
    location = db.Column(db.String(255))

    # =========================================================================
    # Pricing
    # =========================================================================
    price_from = db.Column(db.Float,nullable=False)
    currency = db.Column(db.String(10),default="KES",nullable=False)

    # =========================================================================
    # Group Information
    # =========================================================================
    minimum_people = db.Column(db.Integer,default=1)
    maximum_people = db.Column(db.Integer)
    minimum_age = db.Column(db.Integer)

    # =========================================================================
    # Difficulty
    # =========================================================================
    difficulty = db.Column(db.String(30),default="Easy")

    # =========================================================================
    # Images
    # =========================================================================
    featured_image = db.Column(db.String(255),nullable=False)
    banner_image = db.Column(db.String(255))

    # =========================================================================
    # SEO
    # =========================================================================
    meta_title = db.Column(db.String(160))
    meta_description = db.Column(db.String(320))

    # =========================================================================
    # Homepage
    # =========================================================================
    featured = db.Column(db.Boolean,default=False,nullable=False)
    show_on_homepage = db.Column(db.Boolean,default=False,nullable=False,index=True,)
    active = db.Column(db.Boolean, default=True, nullable=False)

    # -------------------------------------------------------------------------
    # Destination Activation State
    # -------------------------------------------------------------------------
    # Stores the Experience's individual active state when its parent
    # Destination is deactivated.
    #
    # This allows a Destination to act as a master switch without destroying
    # intentionally inactive Experience states.
    destination_deactivation_previous_active = db.Column(
        db.Boolean,
        nullable=True,
    )
    display_order = db.Column(db.Integer,default=0)

    # =========================================================================
    # Foreign Keys
    # =========================================================================
    category_id = db.Column(db.Integer,db.ForeignKey("experience_categories.id"),nullable=False)
    destination_id = db.Column(db.Integer,db.ForeignKey("destinations.id"),nullable=False)
    conservation_story_id = db.Column(db.Integer,db.ForeignKey("conservation_stories.id"))
    cancellation_policy_id = db.Column(db.Integer,db.ForeignKey("cancellation_policies.id"))
    accessibility_profile_id = db.Column(db.Integer,db.ForeignKey("accessibility_profiles.id"))

    # =========================================================================
    # Relationships
    # =========================================================================
    category = db.relationship("ExperienceCategory",back_populates="experiences")
    destination = db.relationship("Destination",back_populates="experiences")
    bookings = db.relationship("ExperienceBooking",back_populates="experience",lazy="dynamic",)

    # IMPORTANT:
    # ExperienceMedia.experience uses back_populates="media".
    # Therefore, this side MUST use back_populates="experience".
    media = db.relationship("ExperienceMedia",back_populates="experience",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceMedia.display_order")
    testimonials = db.relationship("Testimonial",back_populates="experience",cascade="all, delete-orphan",lazy="dynamic")
    pricing = db.relationship("ExperiencePricing",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic")
    itinerary = db.relationship("ExperienceItinerary",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceItinerary.display_order")
    inclusions = db.relationship("ExperienceInclusion",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceInclusion.display_order")
    exclusions = db.relationship("ExperienceExclusion",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceExclusion.display_order")
    highlights = db.relationship("ExperienceHighlight",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceHighlight.display_order")
    addons = db.relationship("ExperienceAddon",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceAddon.display_order")
    packing_items = db.relationship("ExperiencePackingItem",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperiencePackingItem.display_order")
    safety_rules = db.relationship("ExperienceSafetyRule",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceSafetyRule.display_order")
    requirements = db.relationship("ExperienceRequirement",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceRequirement.display_order")
    faqs = db.relationship("ExperienceFAQ",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceFAQ.display_order")
    wildlife = db.relationship("ExperienceWildlife",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceWildlife.display_order")
    photography_spots = db.relationship("ExperiencePhotography",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperiencePhotography.stop_order")
    conservation_story = db.relationship("ConservationStory",back_populates="experiences")
    cancellation_policy = db.relationship("CancellationPolicy",back_populates="experiences")
    accessibility_profile = db.relationship("Accessibility",back_populates="experiences")
    signature_moments = db.relationship(
        "SignatureMoment",
        secondary="signature_moment_experiences",
        back_populates="experiences",
        lazy="dynamic",
        order_by="SignatureMoment.display_order",)
    tags = db.relationship("ExperienceTag",secondary="experience_tags",back_populates="experiences",lazy="dynamic")
    reviews = db.relationship("ExperienceReview",back_populates="experiences",cascade="all, delete-orphan",lazy="dynamic",order_by="ExperienceReview.created_at.desc()")

    # =========================================================================
    # Audit Fields
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def booking_count(self):
        return self.bookings.count()

    @property
    def media_count(self):
        return self.media.count()

    @property
    def testimonial_count(self):
        return self.testimonials.count()

    @property
    def formatted_price(self):
        return f"{self.currency} {self.price_from:,.0f}"

    @property
    def pricing_count(self):
        return self.pricing.count()

    @property
    def itinerary_count(self):
        return self.itinerary.count()

    @property
    def inclusion_count(self):
        return self.inclusions.count()

    @property
    def exclusion_count(self):
        return self.exclusions.count()

    @property
    def highlight_count(self):
        return self.highlights.count()

    @property
    def addon_count(self):
        return self.addons.count()

    @property
    def packing_item_count(self):
        return self.packing_items.count()

    @property
    def safety_rule_count(self):
        return self.safety_rules.count()

    @property
    def requirement_count(self):
        return self.requirements.count()

    @property
    def faq_count(self):
        return self.faqs.count()

    @property
    def hero_media(self):
        return self.media.filter_by(
            usage="hero",
            active=True
        ).first()

    @property
    def gallery_media(self):
        """
        Return active gallery image assets assigned to this experience.

        The ExperienceMedia record controls the assignment, while
        MediaAsset provides the actual image URL and metadata.
        """
        gallery_assignments = (
            self.media
            .filter_by(
                usage="gallery",
                active=True,
            )
            .order_by(
                ExperienceMedia.display_order.asc(),
                ExperienceMedia.id.asc(),
            )
            .all()
        )

        gallery_assets = []

        for assignment in gallery_assignments:
            asset = assignment.media_asset

            if (
                    asset is not None
                    and asset.active
                    and asset.media_type == "image"
                    and asset.browser_url
            ):
                gallery_assets.append(asset)

        return gallery_assets
    
    @property
    def primary_image_url(self):
        """Return only an image explicitly associated with this experience."""
        primary_media_items = (
            self.media
            .filter(
                ExperienceMedia.active.is_(True),
                ExperienceMedia.usage.in_(
                    ("hero", "cover", "thumbnail")),)
            .order_by(
                db.case(
                    (ExperienceMedia.usage == "hero", 0),
                    (ExperienceMedia.usage == "cover", 1),
                    (ExperienceMedia.usage == "thumbnail", 2),
                    else_=3,),
                ExperienceMedia.display_order.asc(),
                ExperienceMedia.id.asc(),).all())

        for item in primary_media_items:
            asset = item.media_asset

            if (
                    asset is not None
                    and asset.active
                    and asset.media_type == "image"
                    and asset.browser_url):
                return asset.browser_url
        # Never reuse a legacy image path when no valid association exists.
        return None

    @property
    def thumbnail_media(self):
        return self.media.filter_by(
            usage="thumbnail",
            active=True).first()

    @property
    def wildlife_count(self):
        return self.wildlife.count()

    @property
    def photography_count(self):
        return self.photography_spots.count()

    @property
    def featured_photography_spots(self):
        return (
            self.photography_spots
            .filter_by(
                featured=True,
                active=True
            ).order_by("ExperiencePhotography.stop_order").all())

    # =========================================================================
    # String Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<Experience "
            f"{self.experience_code} - {self.title}>")