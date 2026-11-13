"""
===============================================================================
The Uncharted Route
Site Settings Forms
===============================================================================

Forms used by the Site Settings CMS.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,Length,
    Optional,URL,)

# =============================================================================
# Site Settings Form
# =============================================================================
class SiteSettingsForm(FlaskForm):
    """
    Manage global website settings.
    """
    # =========================================================================
    # Website Identity
    # =========================================================================
    site_name = StringField(
        "Site Name",
        validators=[
            DataRequired(
                message="Site name is required."),
            Length(max=150),],)

    tagline = StringField(
        "Tagline",
        validators=[
            Optional(),
            Length(max=255),],
        render_kw={
            "placeholder": "Explore. Experience. Remember."})

    description = TextAreaField(
        "Website Description",
        validators=[
            Optional(),
            Length(max=5000),],
        render_kw={
            "rows": 4,
            "placeholder": "Describe The Uncharted Route..."})

    logo = StringField(
        "Logo",
        validators=[
            Optional(),
            Length(max=255),
        ],
        render_kw={
            "placeholder": "Logo path or media asset"})

    favicon = StringField(
        "Favicon",
        validators=[
            Optional(),
            Length(max=255),],
        render_kw={
            "placeholder": "Favicon path or media asset"})

    # =========================================================================
    # Contact
    # =========================================================================
    email = StringField(
        "Public Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),],)

    phone = StringField(
        "Public Phone",
        validators=[
            Optional(),
            Length(max=100),],)

    whatsapp = StringField(
        "WhatsApp",
        validators=[
            Optional(),
            Length(max=100),],)

    address = TextAreaField(
        "Address",
        validators=[
            Optional(),
            Length(max=1000),
        ],
        render_kw={
            "rows": 3})

    city = StringField(
        "City",
        validators=[
            Optional(),
            Length(max=100),],)

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    # =========================================================================
    # Business
    # =========================================================================

    business_name = StringField(
        "Business Name",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    registration_number = StringField(
        "Registration Number",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    tax_number = StringField(
        "Tax Number",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    business_email = StringField(
        "Business Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
        ],
    )

    business_phone = StringField(
        "Business Phone",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    # =========================================================================
    # Social Media
    # =========================================================================
    facebook_url = StringField(
        "Facebook",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    instagram_url = StringField(
        "Instagram",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    twitter_url = StringField(
        "X / Twitter",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    youtube_url = StringField(
        "YouTube",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    linkedin_url = StringField(
        "LinkedIn",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    tiktok_url = StringField(
        "TikTok",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    # =========================================================================
    # Homepage
    # =========================================================================

    homepage_title = StringField(
        "Homepage Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    homepage_subtitle = StringField(
        "Homepage Subtitle",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    homepage_description = TextAreaField(
        "Homepage Description",
        validators=[
            Optional(),
            Length(max=5000),
        ],
        render_kw={
            "rows": 4
        }
    )

    homepage_hero_image = StringField(
        "Hero Image",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    homepage_hero_video = StringField(
        "Hero Video",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = StringField(
        "Default Meta Title",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    meta_description = TextAreaField(
        "Default Meta Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
        render_kw={
            "rows": 4
        }
    )

    meta_keywords = TextAreaField(
        "Default Meta Keywords",
        validators=[
            Optional(),
            Length(max=2000),
        ],
        render_kw={
            "rows": 3
        }
    )

    canonical_url = StringField(
        "Canonical URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500),],)

    # =========================================================================
    # Analytics
    # =========================================================================
    google_analytics_id = StringField(
        "Google Analytics ID",
        validators=[
            Optional(),
            Length(max=100),
        ],
        render_kw={
            "placeholder": "G-XXXXXXXXXX"})
    google_tag_manager_id = StringField(
        "Google Tag Manager ID",
        validators=[
            Optional(),
            Length(max=100),],
        render_kw={
            "placeholder": "GTM-XXXXXXX"})
    facebook_pixel_id = StringField(
        "Facebook Pixel ID",
        validators=[
            Optional(),
            Length(max=100),],)

    # =========================================================================
    # Booking
    # =========================================================================
    booking_email = StringField(
        "Booking Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),],)
    booking_phone = StringField(
        "Booking Phone",
        validators=[
            Optional(),
            Length(max=100),],)
    booking_enabled = BooleanField("Enable Bookings",default=True)
    online_payment_enabled = BooleanField("Enable Online Payments",default=False)

    # =========================================================================
    # Newsletter
    # =========================================================================
    newsletter_enabled = BooleanField("Enable Newsletter",default=True)
    newsletter_email = StringField(
        "Newsletter Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),],)

    # =========================================================================
    # Website Status
    # =========================================================================
    maintenance_mode = BooleanField("Maintenance Mode",default=False)
    maintenance_message = TextAreaField(
        "Maintenance Message",
        validators=[
            Optional(),
            Length(max=2000),],
        render_kw={
            "rows": 4,
            "placeholder": (
                "We are currently updating the website. "
                "Please check back soon.")})

    # =========================================================================
    # Display
    # =========================================================================
    show_phone = BooleanField("Show Phone",default=True)
    show_email = BooleanField("Show Email",default=True)
    show_social_links = BooleanField("Show Social Links",default=True)
    show_booking_button = BooleanField("Show Booking Button",default=True)

    # =========================================================================
    # Footer
    # =========================================================================
    footer_text = TextAreaField(
        "Footer Text",
        validators=[
            Optional(),
            Length(max=5000),],
        render_kw={
            "rows": 4})

    copyright_text = StringField(
        "Copyright Text",
        validators=[
            Optional(),
            Length(max=500),],
        render_kw={
            "placeholder": "© 2026 The Uncharted Route"})

    # =========================================================================
    # Submit
    # =========================================================================
    submit = SubmitField("Save Settings")