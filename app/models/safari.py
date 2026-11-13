"""
===============================================================================
THE UNCHARTED ROUTE
Safari Models
===============================================================================
Independent safari catalogue and inquiry system.
Models:
    SafariDestination
    SafariProperty
    SafariPropertyMedia
    SafariPackageOption
    SafariItineraryDay
    SafariPackageRate
    SafariInquiry

Integrates with the existing central Digital Asset Management system through
MediaAsset and MediaFolder. Does not depend on the existing Experience, Stay,
Destination, or Booking models.
===============================================================================
"""
from datetime import datetime
from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from extensions import db

# =============================================================================
# Shared timestamp helper
# =============================================================================
def safari_utcnow():
    """Return a UTC timestamp for audit fields."""
    return datetime.utcnow()

# =============================================================================
# 1. SAFARI DESTINATION
# =============================================================================
class SafariDestination(db.Model):
    """A destination available through the independent safari catalogue."""

    __tablename__ = "safari_destinations"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)

    short_description = db.Column(db.String(500))
    introduction = db.Column(db.Text)
    history = db.Column(db.Text)
    landscape_and_wildlife = db.Column(db.Text)
    conservation_story = db.Column(db.Text)
    travel_information = db.Column(db.Text)

    # Reuse the existing central media library.
    media_folder_id = db.Column(
        db.Integer,
        db.ForeignKey("media_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    card_media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )

    hero_media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
    )

    display_order = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=safari_utcnow,
        onupdate=safari_utcnow,
    )

    media_folder = db.relationship("MediaFolder", foreign_keys=[media_folder_id])

    card_media_asset = db.relationship(
        "MediaAsset",
        foreign_keys=[card_media_asset_id],
    )

    hero_media_asset = db.relationship(
        "MediaAsset",
        foreign_keys=[hero_media_asset_id],
    )

    properties = db.relationship(
        "SafariProperty",
        back_populates="destination",
        cascade="all, delete-orphan",
        order_by="SafariProperty.display_order, SafariProperty.name",
    )

    def __repr__(self):
        return f"<SafariDestination {self.slug}>"


# =============================================================================
# 2. SAFARI PROPERTY
# =============================================================================
class SafariProperty(db.Model):
    """
    A lodge, hotel, tented camp, villa, or other safari accommodation.

    This is independent of the existing Stay model.
    """

    __tablename__ = "safari_properties"

    id = db.Column(db.Integer, primary_key=True)

    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)

    property_type = db.Column(
        db.String(40),
        nullable=False,
        default="lodge",
    )

    short_description = db.Column(db.String(500))
    overview = db.Column(db.Text)
    property_story = db.Column(db.Text)
    location_description = db.Column(db.Text)

    accommodation_details = db.Column(db.Text)
    facilities = db.Column(db.Text)
    dining_information = db.Column(db.Text)
    activities = db.Column(db.Text)
    wildlife_experience = db.Column(db.Text)
    transport_information = db.Column(db.Text)

    # Useful operational details. These are descriptive, not live availability.
    check_in_information = db.Column(db.Text)
    check_out_information = db.Column(db.Text)
    child_policy = db.Column(db.Text)
    accessibility_information = db.Column(db.Text)
    booking_conditions = db.Column(db.Text)

    official_website_url = db.Column(db.String(500))
    location_name = db.Column(db.String(200))

    # Optional link to the property's folder in the central DAM.
    media_folder_id = db.Column(
        db.Integer,
        db.ForeignKey("media_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    display_order = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=safari_utcnow,
        onupdate=safari_utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "property_type IN "
            "('lodge', 'hotel', 'tented_camp', 'villa', "
            "'mobile_camp', 'private_conservancy', 'other')",
            name="ck_safari_property_type",
        ),
        Index(
            "ix_safari_property_destination_active",
            "destination_id",
            "active",
        ),
    )

    destination = db.relationship(
        "SafariDestination",
        back_populates="properties",
    )

    media_folder = db.relationship(
        "MediaFolder",
        foreign_keys=[media_folder_id],
    )

    media = db.relationship(
        "SafariPropertyMedia",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="SafariPropertyMedia.display_order",
    )

    package_options = db.relationship(
        "SafariPackageOption",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="SafariPackageOption.display_order",
    )

    inquiries = db.relationship(
        "SafariInquiry",
        back_populates="property",
    )

    @property
    def primary_media(self):
        """Return the explicitly designated primary image, if assigned."""
        return next(
            (item for item in self.media if item.is_primary and item.active),
            None,
        )

    @property
    def gallery_media(self):
        """Return active gallery items in display order."""
        return [
            item for item in self.media
            if item.active and item.usage in ("hero", "gallery", "room", "dining", "activity")
        ]

    def __repr__(self):
        return f"<SafariProperty {self.slug}>"


# =============================================================================
# 3. SAFARI PROPERTY MEDIA
# =============================================================================
class SafariPropertyMedia(db.Model):
    """
    Associates an accommodation with an existing MediaAsset.
    One uploaded asset can be reused across the website. This model stores
    the property's particular use, caption, and display order for that asset.
    """
    __tablename__ = "safari_property_media"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey("media_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    usage = db.Column(
        db.String(30),
        nullable=False,
        default="gallery",
    )

    caption = db.Column(db.String(300))
    alt_text = db.Column(db.String(300))

    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "usage IN ('hero', 'gallery', 'room', 'dining', 'activity')",
            name="ck_safari_property_media_usage",
        ),
        UniqueConstraint(
            "property_id",
            "media_asset_id",
            "usage",
            name="uq_safari_property_media_usage",
        ),
        Index(
            "ix_safari_property_media_order",
            "property_id",
            "display_order",
        ),
    )

    property = db.relationship(
        "SafariProperty",
        back_populates="media",
    )

    media_asset = db.relationship(
        "MediaAsset",
        foreign_keys=[media_asset_id],
    )

    def __repr__(self):
        return (
            f"<SafariPropertyMedia property={self.property_id} "
            f"asset={self.media_asset_id}>"
        )


# =============================================================================
# 4. SAFARI PACKAGE OPTION
# =============================================================================
class SafariPackageOption(db.Model):
    """
    A selectable duration offered at a particular property.

    Example:
        3 days / 2 nights
        5 days / 4 nights
        7 days / 6 nights
        10 days / 9 nights

    Each duration owns its own itinerary and can have multiple rates.
    """

    __tablename__ = "safari_package_options"

    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False)

    summary = db.Column(db.String(500))
    description = db.Column(db.Text)

    duration_days = db.Column(db.Integer, nullable=False)
    duration_nights = db.Column(db.Integer, nullable=False)

    # Defaults for the public price display; actual rates live in SafariPackageRate.
    display_currency = db.Column(
        db.String(3),
        nullable=False,
        default="KES",
    )

    inclusions = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    transport_details = db.Column(db.Text)
    meals_information = db.Column(db.Text)
    important_information = db.Column(db.Text)

    display_order = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=safari_utcnow,
        onupdate=safari_utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "property_id",
            "slug",
            name="uq_safari_package_property_slug",
        ),
        CheckConstraint(
            "duration_days >= 3 AND duration_days <= 10",
            name="ck_safari_package_duration_days",
        ),
        CheckConstraint(
            "duration_nights >= 2 AND duration_nights < duration_days",
            name="ck_safari_package_duration_nights",
        ),
        Index(
            "ix_safari_package_property_active",
            "property_id",
            "active",
        ),
    )

    property = db.relationship(
        "SafariProperty",
        back_populates="package_options",
    )

    itinerary_days = db.relationship(
        "SafariItineraryDay",
        back_populates="package_option",
        cascade="all, delete-orphan",
        order_by="SafariItineraryDay.day_number",
    )

    rates = db.relationship(
        "SafariPackageRate",
        back_populates="package_option",
        cascade="all, delete-orphan",
        order_by="SafariPackageRate.amount",
    )

    inquiries = db.relationship(
        "SafariInquiry",
        back_populates="package_option",
    )

    testimonials = db.relationship(
        "Testimonial",
        back_populates="safari_package_option",
        foreign_keys="Testimonial.safari_package_option_id",
    )

    def __repr__(self):
        return (
            f"<SafariPackageOption {self.slug} "
            f"{self.duration_days}d/{self.duration_nights}n>"
        )


# =============================================================================
# 5. SAFARI ITINERARY DAY
# =============================================================================
class SafariItineraryDay(db.Model):
    """One scheduled day within a specific duration option."""

    __tablename__ = "safari_itinerary_days"

    id = db.Column(db.Integer, primary_key=True)

    package_option_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_package_options.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="1",
        index=True,
    )

    morning_activities = db.Column(db.Text)
    afternoon_activities = db.Column(db.Text)
    evening_activities = db.Column(db.Text)

    meals_included = db.Column(db.String(200))
    overnight_location = db.Column(db.String(200))
    transport_details = db.Column(db.Text)
    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=safari_utcnow,
        onupdate=safari_utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "package_option_id",
            "day_number",
            name="uq_safari_itinerary_option_day",
        ),
        CheckConstraint(
            "day_number >= 1",
            name="ck_safari_itinerary_day_number",
        ),
    )

    package_option = db.relationship(
        "SafariPackageOption",
        back_populates="itinerary_days",
    )

    def __repr__(self):
        return (
            f"<SafariItineraryDay option={self.package_option_id} "
            f"day={self.day_number}>"
        )

# =============================================================================
# 6. SAFARI PACKAGE RATE
# =============================================================================

class SafariPackageRate(db.Model):
    """
    A price rule for a particular duration.

    Supports per-person pricing as the preferred default, while also allowing
    per-room, per-night, group, vehicle, and exclusive-use pricing.

    Age bands and occupancy rules are configurable per rate. We do not impose
    one universal child-age threshold across all accommodation providers.
    """

    __tablename__ = "safari_package_rates"

    id = db.Column(db.Integer, primary_key=True)

    package_option_id = db.Column(
        db.Integer,
        db.ForeignKey("safari_package_options.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(180), nullable=False)

    pricing_basis = db.Column(
        db.String(40),
        nullable=False,
        default="per_person_sharing",
    )

    guest_category = db.Column(
        db.String(20),
        nullable=False,
        default="adult",
    )

    min_guest_age = db.Column(db.Integer)
    max_guest_age = db.Column(db.Integer)

    occupancy_type = db.Column(
        db.String(20),
        nullable=False,
        default="sharing",
    )

    min_guests = db.Column(db.Integer, nullable=False, default=1)
    max_guests = db.Column(db.Integer)

    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")

    # Applicable where the supplier provides season-specific rates.
    season_name = db.Column(db.String(100))
    valid_from = db.Column(db.Date)
    valid_to = db.Column(db.Date)

    board_basis = db.Column(db.String(60))
    supplier_rate_reference = db.Column(db.String(150))
    rate_notes = db.Column(db.Text)

    # A rate is not necessarily a live booking or availability confirmation.
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime, nullable=False, default=safari_utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=safari_utcnow,
        onupdate=safari_utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "pricing_basis IN "
            "('per_person', 'per_person_sharing', 'per_person_single', "
            "'per_room_per_night', 'per_room_per_stay', "
            "'per_group', 'per_vehicle', 'exclusive_use')",
            name="ck_safari_rate_pricing_basis",
        ),
        CheckConstraint(
            "guest_category IN ('all', 'adult', 'child', 'infant')",
            name="ck_safari_rate_guest_category",
        ),
        CheckConstraint(
            "occupancy_type IN "
            "('any', 'sharing', 'single', 'double', 'triple', 'family')",
            name="ck_safari_rate_occupancy_type",
        ),
        CheckConstraint(
            "amount >= 0",
            name="ck_safari_rate_amount",
        ),
        CheckConstraint(
            "min_guests >= 1",
            name="ck_safari_rate_min_guests",
        ),
        CheckConstraint(
            "max_guests IS NULL OR max_guests >= min_guests",
            name="ck_safari_rate_max_guests",
        ),
        CheckConstraint(
            "min_guest_age IS NULL OR min_guest_age >= 0",
            name="ck_safari_rate_min_age",
        ),
        CheckConstraint(
            "max_guest_age IS NULL OR max_guest_age >= 0",
            name="ck_safari_rate_max_age",
        ),
        CheckConstraint(
            "min_guest_age IS NULL OR max_guest_age IS NULL "
            "OR max_guest_age >= min_guest_age",
            name="ck_safari_rate_age_range",
        ),
        CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_to >= valid_from",
            name="ck_safari_rate_validity",
        ),
        Index(
            "ix_safari_rate_option_active_currency",
            "package_option_id",
            "active",
            "currency",
        ),
    )

    package_option = db.relationship(
        "SafariPackageOption",
        back_populates="rates",
    )

    def __repr__(self):
        return (
            f"<SafariPackageRate option={self.package_option_id} "
            f"basis={self.pricing_basis} amount={self.amount} {self.currency}>"
        )


# =============================================================================
# 7. SAFARI INQUIRY
# =============================================================================
class SafariInquiry(db.Model):
    """
    A public inquiry about a specific safari property and, optionally,
    a selected duration and rate.
    This is intentionally separate from the existing Booking model.
    """
    __tablename__ = "safari_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40),unique=True,nullable=False,index=True,)
    destination_id = db.Column(db.Integer,db.ForeignKey("safari_destinations.id", ondelete="RESTRICT"),nullable=False,index=True,)
    property_id = db.Column(db.Integer,db.ForeignKey("safari_properties.id", ondelete="RESTRICT"),nullable=False,index=True,)
    package_option_id = db.Column(db.Integer,db.ForeignKey("safari_package_options.id", ondelete="SET NULL"),nullable=True,index=True,)
    rate_id = db.Column(db.Integer,db.ForeignKey("safari_package_rates.id", ondelete="SET NULL"),nullable=True,)

    # Contact information
    full_name = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(254), nullable=False, index=True)
    phone = db.Column(db.String(40))

    # Requested trip details
    preferred_start_date = db.Column(db.Date)
    preferred_end_date = db.Column(db.Date)
    adults = db.Column(db.Integer, nullable=False, default=2)
    children = db.Column(db.Integer, nullable=False, default=0)
    infants = db.Column(db.Integer, nullable=False, default=0)
    children_ages = db.Column(db.String(200))
    preferred_currency = db.Column(db.String(3), nullable=False, default="KES")
    special_requests = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    status = db.Column(db.String(30),nullable=False,default="new",index=True,)
    source = db.Column(db.String(80), default="website")
    created_at = db.Column(db.DateTime, nullable=False, default=safari_utcnow)
    updated_at = db.Column(db.DateTime,nullable=False,default=safari_utcnow,onupdate=safari_utcnow,)
    is_archived = db.Column(db.Boolean,nullable=False,default=False,server_default=db.false(),index=True,)

    __table_args__ = (
        CheckConstraint(
            "adults >= 1",
            name="ck_safari_inquiry_adults",
        ),
        CheckConstraint(
            "children >= 0",
            name="ck_safari_inquiry_children",
        ),
        CheckConstraint(
            "infants >= 0",
            name="ck_safari_inquiry_infants",
        ),
        CheckConstraint(
            "status IN "
            "('new', 'contacted', 'quoting', 'quoted', "
            "'confirmed', 'declined', 'closed')",
            name="ck_safari_inquiry_status",
        ),
        CheckConstraint(
            "preferred_end_date IS NULL OR preferred_start_date IS NULL "
            "OR preferred_end_date >= preferred_start_date",
            name="ck_safari_inquiry_dates",
        ),
        Index(
            "ix_safari_inquiry_status_created",
            "status",
            "created_at",
        ),
    )

    destination = db.relationship("SafariDestination")
    property = db.relationship("SafariProperty",back_populates="inquiries",)
    package_option = db.relationship("SafariPackageOption",back_populates="inquiries",)
    rate = db.relationship("SafariPackageRate",foreign_keys=[rate_id],)

    def __repr__(self):
        return f"<SafariInquiry {self.reference} status={self.status}>"