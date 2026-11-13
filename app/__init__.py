"""
===============================================================================
The Uncharted Route
Application Factory
===============================================================================
Creates and configures the Flask application.
Responsibilities:
    • Create the Flask application
    • Load configuration
    • Initialize Flask extensions
    • Register models
    • Register public blueprints
    • Register administrative blueprints
    • Register context processors
    • Register error handlers
    • Register CLI commands
    • Configure application directories

The application factory is intentionally kept here.
IMPORTANT:
Do NOT import run.py or wsgi.py from this module.
Dependency direction:

    app/__init__.py
          ↓
      create_app()
          ↓
      run.py / wsgi.py
"""

import os
from flask import Flask, request, render_template
from config import config
from extensions import (
    csrf,
    db,
    login_manager,
    mail,
    migrate,)

# =============================================================================
# Application Factory
# =============================================================================
def create_app(config_name=None):
    """
    Create and configure the Flask application.
    Parameters
    ----------
    config_name : str, optional
        Configuration environment.

        Supported values:

            development
            testing
            production

        If omitted, FLASK_ENV is used.

    Returns
    -------
    Flask
        Configured Flask application.
    """

    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    # =========================================================================
    # Configuration
    # =========================================================================
    if config_name is None:
        config_name = os.getenv(
            "FLASK_ENV",
            "development",)
    selected_config = config.get(
        config_name,
        config["default"],)
    app.config.from_object(
        selected_config)

    # =========================================================================
    # Instance Directory
    # =========================================================================
    os.makedirs(
        app.instance_path,
        exist_ok=True,)

    # =========================================================================
    # Upload Directories
    # =========================================================================
    upload_directories = [
        app.config["UPLOAD_FOLDER"],
        app.config["EXPERIENCE_IMAGE_FOLDER"],
        app.config["DESTINATION_IMAGE_FOLDER"],
        app.config["BLOG_IMAGE_FOLDER"],
        app.config["GALLERY_FOLDER"],
        app.config["USER_IMAGE_FOLDER"],
    ]

    for directory in upload_directories:
        os.makedirs(
            directory,
            exist_ok=True,)

    # =========================================================================
    # Initialize Extensions
    # =========================================================================
    db.init_app(app)
    migrate.init_app(
        app,
        db,
    )
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # =========================================================================
    # Import Models
    # =========================================================================
    #
    # Import the complete models package so that all SQLAlchemy models are
    # registered before the application begins handling requests or database
    # operations.
    #
    from app import models  # noqa: F401

    # =========================================================================
    # Flask-Login User Loader
    # =========================================================================
    from app.models import User
    @app.context_processor
    def inject_site_settings():
        from app.services.settings_service import SettingsService

        return {
            "site_settings": SettingsService.get_settings()
        }

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user from the database for Flask-Login.
        """

        try:
            user_id = int(user_id)

        except (
            TypeError,
            ValueError,
        ):
            return None

        return db.session.get(
            User,
            user_id,
        )

    from app.models import SiteSetting
    @app.before_request
    def enforce_maintenance_mode():
        endpoint = request.endpoint

        # Allow static files and requests Flask has not resolved.
        if endpoint is None or endpoint == "static":
            return None

        # Allow the login page so an administrator can sign in.
        if endpoint == "login" or endpoint.endswith(".login"):
            return None

        # Let existing admin routes run their own authentication
        # and permission checks. This does NOT grant admin access.
        if endpoint.startswith(("admin_", "admin.")):
            return None

        # Read the existing settings record without creating one
        # during every request.
        settings = SiteSetting.query.first()

        if settings is None or not settings.maintenance_mode:
            return None

        # All other public requests are paused.
        return render_template(
            "maintenance.html",
            settings=settings,
        ), 503

    from app.services.contact_mailbox_sync_service import (
        ContactMailboxSyncService,
    )

    @app.cli.command("sync-contact-mailbox")
    def sync_contact_mailbox_command():
        """Import incoming contact replies from the configured mailbox."""
        try:
            result = ContactMailboxSyncService.sync_inbox()
            print(
                "Mailbox synchronization complete: "
                f"{result['imported']} imported, "
                f"{result['skipped']} skipped, "
                f"{result['unmatched']} unmatched."
            )
        except Exception as exc:
            print(f"Mailbox synchronization failed: {exc}")
            raise SystemExit(1)

    # =========================================================================
    # Register Blueprints
    # =========================================================================
    register_blueprints(app)

    # =========================================================================
    # Context Processors
    # =========================================================================
    register_context_processors(app)

    # =========================================================================
    # Error Handlers
    # =========================================================================
    register_error_handlers(app)

    # =========================================================================
    # CLI Commands
    # =========================================================================

    register_cli_commands(app)
    return app

# =============================================================================
# Blueprint Registration
# =============================================================================
def register_blueprints(app):
    """
    Register all application blueprints.

    Public website routes are registered first.

    Administrative routes are then registered individually so every admin
    module remains independently accessible while sharing the /admin URL
    namespace defined by its own blueprint.
    """

    # =========================================================================
    # PUBLIC WEBSITE
    # =========================================================================

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # -------------------------------------------------------------------------
    # Main Website
    # -------------------------------------------------------------------------
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.admin.promotions import admin_promotions
    from app.routes.promotions import promotions_bp
    app.register_blueprint(admin_promotions)
    app.register_blueprint(promotions_bp)

    # -------------------------------------------------------------------------
    # Safari
    # -------------------------------------------------------------------------
    from app.routes.admin.safaris import admin_safari_bp
    app.register_blueprint(admin_safari_bp)

    from app.routes.public.safaris import safari_public_bp
    app.register_blueprint(safari_public_bp)

    # -------------------------------------------------------------------------
    # Experiences
    # -------------------------------------------------------------------------
    from app.routes.experiences import experiences_bp
    app.register_blueprint(experiences_bp)

    from app.routes.experience_inquiries import experience_inquiries_bp
    app.register_blueprint(experience_inquiries_bp)

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------
    from app.routes.destinations import destinations_bp
    app.register_blueprint(destinations_bp)

    from app.routes.destination_journeys import (destination_journeys_bp,)
    app.register_blueprint(destination_journeys_bp)

    # -------------------------------------------------------------------------
    # Bookings
    # -------------------------------------------------------------------------
    from app.routes.bookings import bookings_bp
    app.register_blueprint(bookings_bp)

    from app.routes.admin.experience_bookings import experience_bookings_bp
    app.register_blueprint(experience_bookings_bp)

    from app.routes.admin.safari_bookings import safari_bookings_bp
    app.register_blueprint(safari_bookings_bp)

    from app.routes.admin.stay_bookings import stay_bookings_bp
    app.register_blueprint(stay_bookings_bp)

    from app.routes.admin.destination_bookings import destination_bookings_bp
    app.register_blueprint(destination_bookings_bp)

    from app.routes.admin.booking_addons import booking_addons_bp
    app.register_blueprint(booking_addons_bp)

    from app.routes.admin.addon_catalogue import addon_catalogue_bp
    app.register_blueprint(addon_catalogue_bp)

    from app.routes.admin.booking_travellers import booking_travellers_bp
    app.register_blueprint(booking_travellers_bp)

    from app.routes.admin.booking_documents import booking_documents_bp
    app.register_blueprint(booking_documents_bp)

    from app.routes.admin.booking_notes import booking_notes_bp
    app.register_blueprint(booking_notes_bp)

    from app.routes.admin.booking_payments import booking_payments_bp
    app.register_blueprint(booking_payments_bp)

    from app.routes.admin.central_bookings import central_bookings_bp
    app.register_blueprint(central_bookings_bp)

    # -------------------------------------------------------------------------
    # Blog
    # -------------------------------------------------------------------------
    from app.routes.blog import blog_bp
    app.register_blueprint(blog_bp)

    from app.routes.admin.admin_legal_help import admin_legal_help_bp
    app.register_blueprint(admin_legal_help_bp)

    # -------------------------------------------------------------------------
    # Contacts
    # -------------------------------------------------------------------------
    from app.routes.contacts import contacts_bp
    app.register_blueprint(contacts_bp)

    # -------------------------------------------------------------------------
    # Service Enquiries
    # -------------------------------------------------------------------------
    from app.routes.admin.service_inquiries import service_inquiries_bp
    app.register_blueprint(service_inquiries_bp)

    # -------------------------------------------------------------------------
    # Newsletter
    # -------------------------------------------------------------------------
    from app.routes.newsletter import newsletter_bp
    app.register_blueprint(newsletter_bp)

    from app.routes.public_newsletter import public_newsletter_bp
    app.register_blueprint(public_newsletter_bp)

    # =========================================================================
    # ADMINISTRATION
    # =========================================================================
    #
    # The admin package defines the main admin blueprint and the individual
    # administrative modules live inside app/routes/admin/.
    #
    # We import the package-level admin_bp rather than importing
    # app.routes.admin.admin directly. This keeps the package registration
    # structure consistent with app/routes/admin/__init__.py.
    #

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # =========================================================================
    # ADMINISTRATION - CORE MODULES
    # =========================================================================
    from app.routes.admin.admin_page_hero import admin_page_hero
    app.register_blueprint(admin_page_hero)
    # -------------------------------------------------------------------------
    # Blog
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_blog import admin_blog_bp
    app.register_blueprint(admin_blog_bp)

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_destination import (destinations_bp as admin_destinations_bp)
    app.register_blueprint(admin_destinations_bp)

    # -------------------------------------------------------------------------
    # Guide
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_guide import admin_guide_bp
    app.register_blueprint(admin_guide_bp)
    from app.routes.guide_portal import guide_portal_bp
    app.register_blueprint(guide_portal_bp)

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_settings import admin_settings
    app.register_blueprint(admin_settings)

    # -------------------------------------------------------------------------
    # Staff
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_staff import staff_bp
    app.register_blueprint(staff_bp)

    # -------------------------------------------------------------------------
    # Testimonials
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_testimonial import admin_testimonial_bp
    app.register_blueprint(admin_testimonial_bp)

    # -------------------------------------------------------------------------
    # Users
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_user import admin_user_bp
    app.register_blueprint(admin_user_bp)

    # =========================================================================
    # ADMINISTRATION - EXPERIENCE MANAGEMENT
    # =========================================================================
    from app.routes.admin.admin_conservation_story import (conservation_story_bp,)
    app.register_blueprint(conservation_story_bp)
    from app.routes.admin.admin_cancellation_policies import (admin_cancellation_policies)
    app.register_blueprint(admin_cancellation_policies)
    from app.routes.admin.admin_accessibility import admin_accessibility_bp
    app.register_blueprint(admin_accessibility_bp)

    # -------------------------------------------------------------------------
    # Experience Signature Moments
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_signature_moment import (admin_signature_moments_bp,)
    app.register_blueprint(admin_signature_moments_bp)

    # -------------------------------------------------------------------------
    # Experiences
    # -------------------------------------------------------------------------
    from app.routes.admin.experiences import (experiences_bp as admin_experiences_bp)
    app.register_blueprint(admin_experiences_bp)

    # -------------------------------------------------------------------------
    # Experience Add-ons
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_addons import  experience_addons_bp
    app.register_blueprint(experience_addons_bp)

    # -------------------------------------------------------------------------
    # Experience Categories
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_categories import (experience_categories_bp)
    app.register_blueprint(experience_categories_bp)

    # -------------------------------------------------------------------------
    # Experience Exclusions
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_exclusions import (experience_exclusions_bp)
    app.register_blueprint(experience_exclusions_bp)

    # -------------------------------------------------------------------------
    # Experience FAQs
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_faqs import (admin_experience_faqs)
    app.register_blueprint(admin_experience_faqs)

    # -------------------------------------------------------------------------
    # Experience Highlights
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_highlights import (admin_experience_highlights)
    app.register_blueprint(admin_experience_highlights)

    # -------------------------------------------------------------------------
    # Experience Inclusions
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_inclusions import (experience_inclusions_bp)
    app.register_blueprint(experience_inclusions_bp)

    # -------------------------------------------------------------------------
    # Experience Itinerary
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_itinerary import (experience_itinerary_admin)
    app.register_blueprint(experience_itinerary_admin)

    # -------------------------------------------------------------------------
    # Experience Packing Items
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_packing_items import (experience_packing_items_bp)
    app.register_blueprint(experience_packing_items_bp)

    # -------------------------------------------------------------------------
    # Experience Media
    # -------------------------------------------------------------------------
    from app.routes.admin.admin_experience_media import experience_media_bp
    app.register_blueprint(experience_media_bp)

    # -------------------------------------------------------------------------
    # Experience Photography
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_photography import (admin_experience_photography)
    app.register_blueprint(admin_experience_photography)

    # -------------------------------------------------------------------------
    # Experience Pricing
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_pricing import (experience_pricing_bp)
    app.register_blueprint(experience_pricing_bp)

    # -------------------------------------------------------------------------
    # Experience Requirements
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_requirements import (admin_experience_requirements)
    app.register_blueprint(admin_experience_requirements)

    # -------------------------------------------------------------------------
    # Experience Reviews
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_reviews import (admin_experience_reviews)
    app.register_blueprint(admin_experience_reviews)

    # -------------------------------------------------------------------------
    # Experience Safety Rules
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_safety_rules import (admin_experience_safety_rules)
    app.register_blueprint(admin_experience_safety_rules)

    # -------------------------------------------------------------------------
    # Experience Tags
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_tags import (admin_experience_tags_bp)
    app.register_blueprint(admin_experience_tags_bp)

    # -------------------------------------------------------------------------
    # Experience Wildlife
    # -------------------------------------------------------------------------
    from app.routes.admin.experience_wildlife import (experience_wildlife_bp)
    app.register_blueprint(experience_wildlife_bp)

    # =========================================================================
    # ADMINISTRATION - MEDIA & HOMEPAGE
    # =========================================================================
    # -------------------------------------------------------------------------
    # Homepage
    # -------------------------------------------------------------------------
    from app.routes.admin.homepage import homepage_bp
    app.register_blueprint(homepage_bp)

    # -------------------------------------------------------------------------
    # Media
    # -------------------------------------------------------------------------
    from app.routes.admin.media import media_bp
    app.register_blueprint(media_bp)
    from app.routes.admin.photography_spots import photography_spots_bp
    app.register_blueprint(photography_spots_bp)
    from app.routes.admin.wildlife_species import (wildlife_species_bp,)
    app.register_blueprint(wildlife_species_bp)

    # -------------------------------------------------------------------------
    # Stays
    # -------------------------------------------------------------------------
    from app.routes.stays import stays_bp
    app.register_blueprint(stays_bp)

    from app.routes.admin.admin_stay import stay_bp
    app.register_blueprint(stay_bp)

    from app.routes.admin.admin_stay_amenity import stay_amenity_bp
    app.register_blueprint(stay_amenity_bp)

    from app.routes.admin.admin_stay_room import stay_room_bp
    app.register_blueprint(stay_room_bp)

    from app.routes.admin.admin_stay_media import stay_media_bp
    app.register_blueprint(stay_media_bp)

    from app.routes.admin.admin_stay_review import stay_review_bp
    app.register_blueprint(stay_review_bp)

    from app.routes.admin.admin_stay_room_amenity import stay_room_amenity_bp
    app.register_blueprint(stay_room_amenity_bp)

    from app.routes.admin.admin_stay_room_media import stay_room_media_bp
    app.register_blueprint(stay_room_media_bp)

    from app.routes.stay_inquiries import stay_inquiries_bp
    app.register_blueprint(stay_inquiries_bp)

    from app.routes.public_stay_bookings import public_stay_bookings_bp
    app.register_blueprint(public_stay_bookings_bp)

    from app.routes.admin.bookings import bookings_bp
    app.register_blueprint(bookings_bp)

    from app.routes.public_experience_bookings import experience_bookings_bp
    app.register_blueprint(experience_bookings_bp)

# =============================================================================
# Context Processors
# =============================================================================
def register_context_processors(app):
    """
    Register variables available to all templates.
    """
    @app.context_processor
    def inject_globals():
        return {
            "company_name": app.config["COMPANY_NAME"],
            "company_phone": app.config["COMPANY_PHONE"],
            "company_email": app.config["COMPANY_EMAIL"],
            "company_address": app.config["COMPANY_ADDRESS"],
        }

# =============================================================================
# Error Handlers
# =============================================================================
def register_error_handlers(app):
    """
    Register application-wide error handlers.
    """

    @app.errorhandler(404)
    def page_not_found(error):

        return (
            "404 Page Not Found",
            404,
        )

    @app.errorhandler(403)
    def forbidden(error):

        return (
            "403 Forbidden",
            403,
        )

    @app.errorhandler(500)
    def server_error(error):

        return (
            "500 Internal Server Error",
            500,
        )

# =============================================================================
# CLI Commands
# =============================================================================
def register_cli_commands(app):
    """
    Register custom Flask CLI commands.
    """
    pass