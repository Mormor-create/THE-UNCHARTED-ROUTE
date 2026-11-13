"""
===============================================================================
The Uncharted Route
Stay Model
===============================================================================

Represents accommodation properties offered through The Uncharted Route.

Examples:

- Hotels
- Lodges
- Resorts
- Villas
- Safari Camps
- Tented Camps
- Boutique Properties
- Guesthouses
- Eco-Lodges

A Stay belongs to a Destination and can contain multiple StayRoom records.

The Stay represents the property itself. Individual rooms, rates, availability,
media, amenities, reviews, and policies are managed through related models.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Stay Model
# =============================================================================

class Stay(db.Model):
    """
    Represents an accommodation property.
    """

    __tablename__ = "stays"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # =========================================================================
    # Identity
    # =========================================================================

    stay_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    property_name = db.Column(
        db.String(200),
        nullable=False,
        index=True,
    )

    slug = db.Column(
        db.String(220),
        unique=True,
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Property Classification
    # =========================================================================

    accommodation_type = db.Column(
        db.String(50),
        nullable=False,
        default="Hotel",
    )

    # Hotel
    # Lodge
    # Resort
    # Villa
    # Boutique Hotel
    # Safari Camp
    # Tented Camp
    # Guesthouse
    # Apartment
    # Cottage
    # Eco-Lodge
    # Private Residence
    # Other

    # =========================================================================
    # Descriptions
    # =========================================================================

    short_description = db.Column(
        db.String(350),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    # =========================================================================
    # Location
    # =========================================================================

    location = db.Column(
        db.String(255),
        nullable=False,
    )

    address = db.Column(
        db.String(500),
    )

    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destinations.id"),
        nullable=False,
        index=True,
    )

    latitude = db.Column(
        db.Float,
    )

    longitude = db.Column(
        db.Float,
    )

    # =========================================================================
    # Capacity
    # =========================================================================

    maximum_guests = db.Column(
        db.Integer,
    )

    maximum_adults = db.Column(
        db.Integer,
    )

    maximum_children = db.Column(
        db.Integer,
    )

    total_rooms = db.Column(
        db.Integer,
    )

    minimum_nights = db.Column(
        db.Integer,
        default=1,
    )

    # =========================================================================
    # Check-in / Check-out
    # =========================================================================

    check_in_time = db.Column(
        db.String(20),
    )

    check_out_time = db.Column(
        db.String(20),
    )

    # =========================================================================
    # Property Contact Information
    # =========================================================================

    contact_phone = db.Column(
        db.String(50),
    )

    contact_email = db.Column(
        db.String(255),
    )

    website_url = db.Column(
        db.String(500),
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = db.Column(
        db.String(160),
    )

    meta_description = db.Column(
        db.String(320),
    )

    # =========================================================================
    # Homepage / Catalogue
    # =========================================================================

    featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    show_on_homepage = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    display_order = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    cancellation_policy_id = db.Column(
        db.Integer,
        db.ForeignKey("cancellation_policies.id"),
        nullable=True,
    )

    # =========================================================================
    # Media Library
    # =========================================================================
    #
    # This stores the Media Library folder assigned to the property itself.
    #
    # Example:
    #
    #     Stays
    #       └── Fairmont Mount Kenya Safari Club
    #
    # Property media is managed from this folder.
    #
    # This is intentionally a folder ID rather than a MediaAsset ID because
    # one Stay can have many media assets.
    #
    # =========================================================================

    media_folder_id = db.Column(
        db.Integer,
        db.ForeignKey("media_folders.id"),
        nullable=True,
        index=True,
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    destination = db.relationship(
        "Destination",
        back_populates="stays",
    )

    cancellation_policy = db.relationship(
        "CancellationPolicy",
        back_populates="stays",
    )

    media_folder = db.relationship(
        "MediaFolder",
        foreign_keys=[media_folder_id],
    )

    rooms = db.relationship(
        "StayRoom",
        back_populates="stay",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayRoom.display_order",
    )

    # =========================================================================
    # Bookings
    # =========================================================================
    bookings = db.relationship(
        "StayBooking",
        back_populates="stay",
        lazy="dynamic",)

    testimonials = db.relationship(
        "Testimonial",
        back_populates="stay",
        foreign_keys="Testimonial.stay_id",)

    media = db.relationship(
        "StayMedia",
        back_populates="stay",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayMedia.display_order",)

    amenities = db.relationship(
        "StayAmenity",
        back_populates="stay",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayAmenity.display_order",)

    reviews = db.relationship(
        "StayReview",
        back_populates="stay",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="StayReview.created_at.desc()",)

    # =========================================================================
    # Audit Fields
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # =========================================================================
    # Helper Properties
    # =========================================================================

    @property
    def room_count(self):
        return self.rooms.count()

    @property
    def media_count(self):
        return self.media.count()

    @property
    def amenity_count(self):
        return self.amenities.count()

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def hero_media(self):
        return self.media.filter_by(
            usage="hero",
            active=True,
        ).first()

    @property
    def banner_media(self):
        return self.media.filter_by(
            usage="banner",
            active=True,
        ).first()

    @property
    def thumbnail_media(self):
        return self.media.filter_by(
            usage="thumbnail",
            active=True,
        ).first()

    @property
    def gallery_media(self):
        return (
            self.media
            .filter_by(
                usage="gallery",
                active=True,
            )
            .order_by(
                "StayMedia.display_order"
            )
            .all()
        )

    @property
    def average_rating(self):
        reviews = (
            self.reviews
            .filter_by(status="approved")
            .all()
        )

        if not reviews:
            return 0

        return round(
            sum(
                review.rating
                for review in reviews
            ) / len(reviews),
            1,
        )

    @property
    def active_rooms(self):
        return self.rooms.filter_by(
            active=True
        ).all()

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<Stay "
            f"{self.stay_code} - {self.property_name}>"
        )