"""
===============================================================================
The Uncharted Route
Site Settings Service
===============================================================================
Business logic for managing global website settings.
Handles:
- Retrieving global settings
- Creating default settings
- Updating settings
- Initializing settings
- Resetting display settings
The booking_enabled setting controls whether the public website should offer
booking actions or enquiry-focused alternatives.
===============================================================================
"""

from extensions import db
from app.models import SiteSetting
# =============================================================================
# Site Settings Service
# =============================================================================
class SettingsService:
    """Service layer for managing global website settings."""

    # =========================================================================
    # Default Settings
    # =========================================================================
    DEFAULT_SETTINGS = {
        "site_name": "The Uncharted Route",
        "country": "Kenya",
        "booking_enabled": True,
        "newsletter_enabled": True,
        "maintenance_mode": False,
        "show_phone": True,
        "show_email": True,
        "show_social_links": True,
        "show_booking_button": True,}

    # =========================================================================
    # Allowed Settings Fields
    # =========================================================================
    ALLOWED_FIELDS = {
        "site_name",
        "tagline",
        "description",
        "logo",
        "favicon",

        "email",
        "phone",
        "whatsapp",
        "address",
        "city",
        "country",

        "business_name",
        "registration_number",
        "tax_number",
        "business_email",
        "business_phone",

        "facebook_url",
        "instagram_url",
        "twitter_url",
        "youtube_url",
        "linkedin_url",
        "tiktok_url",

        "homepage_title",
        "homepage_subtitle",
        "homepage_description",
        "homepage_hero_image",
        "homepage_hero_video",

        "meta_title",
        "meta_description",
        "meta_keywords",
        "canonical_url",

        "google_analytics_id",
        "google_tag_manager_id",
        "facebook_pixel_id",

        "booking_email",
        "booking_phone",
        "booking_enabled",
        "online_payment_enabled",

        "newsletter_enabled",
        "newsletter_email",

        "maintenance_mode",
        "maintenance_message",

        "show_phone",
        "show_email",
        "show_social_links",
        "show_booking_button",

        "footer_text",
        "copyright_text",}

    # =========================================================================
    # Get Settings
    # =========================================================================
    @staticmethod
    def get_settings():
        """
        Return the global settings record.

        If no settings record exists, create and persist a default record.
        """
        settings = SiteSetting.query.first()
        if settings is not None:
            return settings
        settings = SiteSetting(**SettingsService.DEFAULT_SETTINGS)

        try:
            db.session.add(settings)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return settings

    # =========================================================================
    # Update Settings
    # =========================================================================
    @staticmethod
    def update_settings(settings, **kwargs):
        """
        Update an existing settings record.

        Only recognized fields that are provided in kwargs are updated.
        The existing booking_enabled setting remains the authoritative
        switch for enabling or disabling booking actions on the public site.
        """
        if settings is None:
            settings = SettingsService.get_settings()

        model_fields = {
            column.name
            for column in SiteSetting.__table__.columns}
        for field, value in kwargs.items():
            if (
                field in SettingsService.ALLOWED_FIELDS
                and field in model_fields):
                setattr(settings, field, value)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return settings

    # =========================================================================
    # Initialize Settings
    # =========================================================================
    @staticmethod
    def initialize():
        """
        Ensure that a global settings record exists.
        Returns the existing record or creates one with default values.
        """
        settings = SiteSetting.query.first()
        if settings is not None:
            return settings
        return SettingsService.get_settings()

    # =========================================================================
    # Booking Availability
    # =========================================================================
    @staticmethod
    def bookings_enabled():
        """
        Return whether booking are enabled on the public website.

        This method centralizes access to the existing booking_enabled
        setting so routes and templates can use the same source of truth.
        """
        settings = SettingsService.get_settings()
        return bool(settings.booking_enabled)

    # =========================================================================
    # Online Payment Availability
    # =========================================================================
    @staticmethod
    def online_payments_enabled():
        """
        Return whether online payments are enabled.

        Booking availability and online payment availability are separate:
        booking may be enabled even when online payments are disabled.
        """
        settings = SettingsService.get_settings()
        return bool(settings.online_payment_enabled)

    # =========================================================================
    # Reset Display Settings
    # =========================================================================
    @staticmethod
    def reset_display_settings(settings):
        """
        Reset display-related settings to their default values.
        """
        if settings is None:
            settings = SettingsService.get_settings()
        settings.show_phone = True
        settings.show_email = True
        settings.show_social_links = True
        settings.show_booking_button = True

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return settings
