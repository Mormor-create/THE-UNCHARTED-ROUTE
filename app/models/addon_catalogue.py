"""
===============================================================================
The Uncharted Route
Shared Add-on Catalogue Model
===============================================================================
Reusable add-ons for experiences, safaris, stays, and destination journeys.
"""
from datetime import datetime
from extensions import db

class AddonCatalogue(db.Model):
    __tablename__ = "addon_catalogue"

    SERVICE_TYPES = (
        "experience",
        "safari",
        "stay",
        "destination_journey",)

    CATEGORIES = (
        "transport",
        "accommodation",
        "activity",
        "equipment",
        "meal",
        "insurance",
        "guide",
        "park_fee",
        "upgrade",
        "other",)

    PRICING_BASES = (
        "per_booking",
        "per_person",
        "per_day",
        "per_night",
        "per_unit",)

    CURRENCIES = (
        "KES", "USD", "EUR", "GBP", "UGX",
        "TZS", "ZAR", "NGN", "GHS",)

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(300))
    description = db.Column(db.Text)

    category = db.Column(
        db.String(40), nullable=False, default="other", index=True
    )

    # JSON list, e.g. ["safari", "stay", "destination_journey"].
    applicable_services = db.Column(db.JSON, nullable=False, default=list)

    pricing_basis = db.Column(
        db.String(30), nullable=False, default="per_booking"
    )
    unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    currency = db.Column(db.String(10), nullable=False, default="KES")

    minimum_quantity = db.Column(db.Integer, nullable=False, default=1)
    maximum_quantity = db.Column(db.Integer)

    # Optional inventory control. Null means no fixed inventory limit.
    available_quantity = db.Column(db.Integer)

    # Optional catalogue availability dates.
    available_from = db.Column(db.Date)
    available_until = db.Column(db.Date)

    is_optional = db.Column(db.Boolean, nullable=False, default=True)
    can_be_booked_independently = db.Column(
        db.Boolean, nullable=False, default=False)
    requires_confirmation = db.Column(
        db.Boolean, nullable=False, default=False)

    image_url = db.Column(db.String(500))
    featured = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)

    # Optional bridge to the existing experience-specific catalogue.
    experience_addon_id = db.Column(
        db.Integer,
        db.ForeignKey("experience_addons.id", ondelete="SET NULL"),
        nullable=True,
        index=True,)

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,)

    # Set up this relationship only if ExperienceAddon does not already
    # define an incompatible relationship/backref for this foreign key.
    experience_addon = db.relationship(
        "ExperienceAddon",
        foreign_keys=[experience_addon_id],)

    def applies_to(self, service_type):
        return service_type in (self.applicable_services or [])

    @property
    def formatted_price(self):
        return f"{self.currency} {self.unit_price:,.2f}"

    @property
    def is_available(self):
        return self.active and (
            self.available_quantity is None or self.available_quantity > 0
        )

    def __repr__(self):
        return f"<AddonCatalogue {self.code}: {self.name}>"
