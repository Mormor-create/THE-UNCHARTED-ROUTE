"""
===============================================================================
The Uncharted Route
Site Settings Model
===============================================================================
Stores global website configuration managed through the admin CMS.
Includes:
• Website identity
• Contact information
• Social media
• Business information
• Homepage configuration
• SEO defaults
• Analytics
• Booking configuration
• Newsletter configuration
• Display preferences
• Website status
"""
from datetime import datetime
from extensions import db
# =============================================================================
# Site Settings Model
# =============================================================================
class SiteSetting(db.Model):
    """
    Global website settings.
    The application is designed around a single settings record.
    """
    __tablename__ = "site_settings"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Website Identity
    # =========================================================================
    site_name = db.Column(db.String(150),nullable=False,default="The Uncharted Route")
    tagline = db.Column(db.String(255))
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))
    favicon = db.Column(db.String(255))

    # =========================================================================
    # Contact Information
    # =========================================================================
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))
    whatsapp = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100),default="Kenya")

    # =========================================================================
    # Business Information
    # =========================================================================
    business_name = db.Column(db.String(255))
    registration_number = db.Column(db.String(150))
    tax_number = db.Column(db.String(150))
    business_email = db.Column(db.String(255))
    business_phone = db.Column(db.String(100))

    # =========================================================================
    # Social Media
    # =========================================================================
    facebook_url = db.Column(db.String(500))
    instagram_url = db.Column(db.String(500))
    twitter_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    tiktok_url = db.Column(db.String(500))

    # =========================================================================
    # Homepage
    # =========================================================================
    homepage_title = db.Column(db.String(255))
    homepage_subtitle = db.Column(db.String(500))
    homepage_description = db.Column(db.Text)
    homepage_hero_image = db.Column(db.String(255))
    homepage_hero_video = db.Column(db.String(500))

    # =========================================================================
    # SEO Defaults
    # =========================================================================
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)
    canonical_url = db.Column(db.String(500))

    # =========================================================================
    # Analytics
    # =========================================================================
    google_analytics_id = db.Column(db.String(100))
    google_tag_manager_id = db.Column(db.String(100))
    facebook_pixel_id = db.Column(db.String(100))

    # =========================================================================
    # Booking Configuration
    # =========================================================================
    booking_email = db.Column(db.String(255))
    booking_phone = db.Column(db.String(100))
    booking_enabled = db.Column(db.Boolean,default=True,nullable=False)
    online_payment_enabled = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Newsletter
    # =========================================================================
    newsletter_enabled = db.Column(db.Boolean,default=True,nullable=False)
    newsletter_email = db.Column(db.String(255))

    # =========================================================================
    # Website Status
    # =========================================================================
    maintenance_mode = db.Column(db.Boolean,default=False,nullable=False)
    maintenance_message = db.Column(db.Text)

    # =========================================================================
    # Display
    # =========================================================================
    show_phone = db.Column(db.Boolean,default=True,nullable=False)
    show_email = db.Column(db.Boolean,default=True,nullable=False)
    show_social_links = db.Column(db.Boolean,default=True,nullable=False)
    show_booking_button = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Footer
    # =========================================================================
    footer_text = db.Column(db.Text)
    copyright_text = db.Column(db.String(500))

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow, onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (f"<SiteSetting {self.site_name}>")