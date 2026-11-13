"""
===============================================================================
The Uncharted Route
Services Package
===============================================================================

Central service layer for The Uncharted Route.

Services contain application business logic and coordinate interactions
between models, routes, external providers, and other application components.

The services package is intentionally kept separate from:

    models/
        Database models and relationships.

    routes/
        HTTP request and response handling.

    templates/
        Presentation layer.

Services should generally:
    - Validate business rules
    - Query and manipulate models
    - Coordinate multiple models
    - Handle reusable application logic
    - Communicate with external providers
    - Keep route functions lightweight

IMPORTANT
---------
This __init__.py intentionally does not eagerly import every service.

Many services depend on models or other services. Eager imports here can
create circular-import problems during application startup.

Import services explicitly where required, for example:

    from app.services.booking_service import booking_service

or:

    from app.services.notification_service import notification_service

===============================================================================
"""
from app.services.blog import blog_category_service, blog_service
from app.services.bookings import booking_service, booking_addon_service, booking_document_service, \
    booking_note_service, booking_payment_service, booking_traveller_service, addon_catalogue_service
from app.services.experiences import conservation_story_service, experience_service, experience_addon_service, \
    experience_category_service, experience_exclusion_service, experience_faq_service, experience_highlight_service, \
    experience_inclusion_service, experience_itinerary_service, experience_media_service, \
    experience_packing_item_service, experience_photography_service, experience_pricing_service, \
    experience_requirement_service, experience_review_service, experience_safety_rule_service, experience_tag_service, \
     experience_wildlife_service

# =============================================================================
# Service Modules
# =============================================================================
__all__ = [

    # -------------------------------------------------------------------------
    # Authentication & Users
    # -------------------------------------------------------------------------
    "auth_service",
    "permission_service",
    "user_service",

    # -------------------------------------------------------------------------
    # Blog & Content
    # -------------------------------------------------------------------------
    "blog_category_service",
    "blog_service",

    # -------------------------------------------------------------------------
    # Bookings
    # -------------------------------------------------------------------------
    "booking_service",
    "booking_addon_service",
    "booking_document_service",
    "booking_note_service",
    "booking_payment_service",
    "booking_traveller_service",
    "addon_catalogue_service",

    # -------------------------------------------------------------------------
    # Cancellation & Policies
    # -------------------------------------------------------------------------
    "cancellation_policy_service",

    # -------------------------------------------------------------------------
    # Conservation
    # -------------------------------------------------------------------------
    "conservation_story_service",

    # -------------------------------------------------------------------------
    # Customer Communication
    # -------------------------------------------------------------------------
    "contact_service",
    "email_service",
    "notification_service",

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------
    "destination_service",

    # -------------------------------------------------------------------------
    # Experiences
    # -------------------------------------------------------------------------
    "experience_service",
    "experience_addon_service",
    "experience_category_service",
    "experience_exclusion_service",
    "experience_faq_service",
    "experience_highlight_service",
    "experience_inclusion_service",
    "experience_itinerary_service",
    "experience_media_service",
    "experience_packing_item_service",
    "experience_photography_service",
    "experience_pricing_service",
    "experience_requirement_service",
    "experience_review_service",
    "experience_safety_rule_service",
    "experience_tag_service",
    "experience_wildlife_service",

    # -------------------------------------------------------------------------
    # File & Media
    # -------------------------------------------------------------------------
    "file_storage_service",
    "media_service",

    # -------------------------------------------------------------------------
    # Newsletter & Marketing
    # -------------------------------------------------------------------------
    "newsletter_service",

    # -------------------------------------------------------------------------
    # Payments
    # -------------------------------------------------------------------------
    "payment_gateway_service",

    # -------------------------------------------------------------------------
    # Photography
    # -------------------------------------------------------------------------
    "photography_spot_service",

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------
    "pricing_service",

    # -------------------------------------------------------------------------
    # Search & SEO
    # -------------------------------------------------------------------------
    "search_service",
    "seo_service",

    # -------------------------------------------------------------------------
    # Signature Moments
    # -------------------------------------------------------------------------
    "signature_moment_service",

    # -------------------------------------------------------------------------
    # Testimonials
    # -------------------------------------------------------------------------
    "testimonial_service",

    # -------------------------------------------------------------------------
    # Wildlife
    # -------------------------------------------------------------------------
    "wildlife_species_service",
]
