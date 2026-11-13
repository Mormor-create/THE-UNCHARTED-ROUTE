"""
===============================================================================
The Uncharted Route
Promotions and Promotion Inquiries Models
===============================================================================
"""

from datetime import date, datetime
from extensions import db

class Promotion(db.Model):
    """A poster-first promotional offer."""
    __tablename__ = "promotions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    slug = db.Column(
        db.String(220),
        unique=True,
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    poster_media_asset_id = db.Column(
        db.Integer,
        db.ForeignKey("media_assets.id"),
        nullable=False,
        index=True,
    )

    starts_at = db.Column(
        db.Date,
        nullable=True,
    )

    ends_at = db.Column(
        db.Date,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="draft",
        index=True,
    )

    show_on_homepage = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    media_asset = db.relationship(
        "MediaAsset",
        foreign_keys=[poster_media_asset_id],
        lazy="joined",
    )

    # A promotion can have multiple inquiries.
    # Inquiry records are retained if the promotion is deleted.
    inquiries = db.relationship(
        "PromotionInquiry",
        back_populates="promotion",
        lazy="dynamic",
        passive_deletes=True,
    )

    @property
    def poster_url(self):
        if self.media_asset:
            return self.media_asset.browser_url

        return None

    @property
    def poster_alt(self):
        if self.media_asset:
            return (
                self.media_asset.alt_text
                or self.media_asset.title
                or self.title
            )

        return self.title

    @property
    def display_status(self):
        if self.status != "published":
            return "draft"

        today = date.today()

        if self.starts_at and self.starts_at > today:
            return "scheduled"

        if self.ends_at and self.ends_at < today:
            return "expired"

        return "published"

    @property
    def is_currently_available(self):
        if self.status != "published":
            return False

        today = date.today()

        if self.starts_at and self.starts_at > today:
            return False

        if self.ends_at and self.ends_at < today:
            return False

        return True

    def __repr__(self):
        return f"<Promotion {self.title!r}>"


class PromotionInquiry(db.Model):
    """
    Customer inquiry relating to a promotional offer.

    This is an inquiry and lead-management record, not a booking.
    """

    __tablename__ = "promotion_inquiries"

    STATUSES = [
        "new",
        "in_progress",
        "contacted",
        "converted",
        "closed",]

    CONTACT_METHODS = [
        "email",
        "phone",
        "whatsapp",]

    id = db.Column(
        db.Integer,
        primary_key=True,)

    # SET NULL preserves the inquiry if its promotion is deleted.
    promotion_id = db.Column(
        db.Integer,
        db.ForeignKey("promotions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,)

    # Snapshot preserves the promotion name for historical records.
    promotion_title = db.Column(
        db.String(200),
        nullable=False,)

    customer_name = db.Column(
        db.String(150),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        index=True,
    )

    phone = db.Column(
        db.String(40),
        nullable=False,
    )

    country = db.Column(
        db.String(100),
        nullable=True,
    )

    contact_method = db.Column(
        db.String(20),
        nullable=False,
        default="email",
    )

    message = db.Column(
        db.Text,
        nullable=False,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="new",
        index=True,
    )

    admin_notes = db.Column(
        db.Text,
        nullable=True,
    )

    submitted_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    promotion = db.relationship(
        "Promotion",
        back_populates="inquiries",
    )

    @property
    def display_status(self):
        return self.status.replace("_", " ").title()

    @property
    def preferred_contact_method(self):
        return self.contact_method.replace("_", " ").title()

    def __repr__(self):
        return (
            f"<PromotionInquiry "
            f"{self.id}: {self.customer_name!r}>"
        )
