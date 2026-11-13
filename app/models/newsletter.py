"""
===============================================================================
The Uncharted Route
Newsletter Subscriber Model
===============================================================================
Stores newsletter subscribers and their communication preferences.
Supports:
• Double Opt-In
• Subscriber Preferences
• Marketing Segmentation
• Engagement Tracking
• GDPR/Privacy Compliance
"""

from datetime import datetime

from extensions import db
# =============================================================================
# Newsletter Subscriber Model
# =============================================================================
class NewsletterSubscriber(db.Model):
    """
    Newsletter subscriber.
    """
    __tablename__ = "newsletter_subscribers"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Subscriber Information
    # =========================================================================
    email = db.Column(db.String(255),unique=True,nullable=False,index=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    country = db.Column(db.String(100))

    # =========================================================================
    # Subscription
    # =========================================================================
    subscribed = db.Column(db.Boolean,default=True,nullable=False)
    verified = db.Column(db.Boolean,default=False,nullable=False)
    verification_token = db.Column(db.String(255),unique=True)
    unsubscribed_at = db.Column(db.DateTime)
    unsubscribe_reason = db.Column(db.String(255))

    # =========================================================================
    # Marketing Preferences
    # =========================================================================
    receive_promotions = db.Column(db.Boolean,default=True,nullable=False)
    receive_new_experiences = db.Column(db.Boolean,default=True,nullable=False)
    receive_blog_updates = db.Column(db.Boolean,default=True,nullable=False)
    receive_company_news = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Interest Segments
    # =========================================================================
    adventure = db.Column(db.Boolean,default=False,nullable=False)
    wildlife = db.Column(db.Boolean,default=False,nullable=False)
    luxury = db.Column(db.Boolean,default=False,nullable=False)
    coastal = db.Column(db.Boolean,default=False,nullable=False)
    corporate = db.Column(db.Boolean,default=False,nullable=False)
    family = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Engagement
    # =========================================================================
    last_email_sent = db.Column(db.DateTime)
    last_opened = db.Column(db.DateTime)
    last_clicked = db.Column(db.DateTime)
    total_emails_sent = db.Column(db.Integer,default=0,nullable=False)
    total_opens = db.Column(db.Integer,default=0,nullable=False)
    total_clicks = db.Column(db.Integer,default=0,nullable=False)

    # =========================================================================
    # Source
    # =========================================================================
    source = db.Column(db.String(100),default="Website")
    # Website
    # Blog
    # Booking
    # Contact Form
    # Landing Page
    # Manual Import
    # Event
    # QR Code

    # =========================================================================
    # Privacy
    # =========================================================================
    marketing_consent = db.Column(db.Boolean,default=False,nullable=False)
    consent_date = db.Column(db.DateTime)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.email

    @property
    def open_rate(self):
        if self.total_emails_sent == 0:
            return 0

        return round(
            (self.total_opens / self.total_emails_sent) * 100,
            2)

    @property
    def click_rate(self):
        if self.total_emails_sent == 0:
            return 0

        return round(
            (self.total_clicks / self.total_emails_sent) * 100,
            2)

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<NewsletterSubscriber {self.email}>"
        )

from datetime import datetime, timezone
from extensions import db


class Newsletter(db.Model):
    """
    Represents a newsletter subscriber.
    """
    __tablename__ = "newsletters"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Subscriber Information
    # =========================================================================
    email = db.Column(db.String(255),nullable=False,unique=True,index=True,)

    # =========================================================================
    # Subscription Status
    # =========================================================================
    is_subscribed = db.Column(db.Boolean,nullable=False,default=True,)

    # =========================================================================
    # Verification
    # =========================================================================
    is_verified = db.Column(db.Boolean,nullable=False,default=False,)

    # =========================================================================
    # Subscription Source
    # =========================================================================
    source = db.Column(db.String(100),nullable=True,)

    # =========================================================================
    # Timestamps
    # =========================================================================
    subscribed_at = db.Column(db.DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc),)
    updated_at = db.Column(db.DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),)

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<Newsletter "
            f"id={self.id} "
            f"email='{self.email}'>")