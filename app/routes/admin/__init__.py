"""
===============================================================================
The Uncharted Route
Admin Routes Package
===============================================================================
Central registration point for all administrative routes.
The admin blueprint is defined here and individual admin route modules are
imported after the blueprint has been created.
All administrative routes therefore share:
    /admin
Individual modules contain the route logic for their respective management
areas and attach their routes to `admin_bp`.
"""

from flask import Blueprint
# =============================================================================
# Admin Blueprint
# =============================================================================
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",)

# =============================================================================
# Admin Route Modules
# =============================================================================
#
# IMPORTANT:
#
# admin_bp MUST be created before these modules are imported.
#
# Individual modules use:
#
#     from . import admin_bp
#
# and therefore attach their routes directly to this blueprint.
#
# Do not import modules that do not physically exist in this package.
# =============================================================================


# -----------------------------------------------------------------------------
# Main Administration / Dashboard
# -----------------------------------------------------------------------------
from . import admin
from . import  service_inquiries
from . import wildlife_species
from . import promotions
from . import admin_page_hero
from . import admin_settings
from . import admin_guide

# -----------------------------------------------------------------------------
# Blog
# -----------------------------------------------------------------------------
from . import admin_blog

# -----------------------------------------------------------------------------
# Bookings
# -----------------------------------------------------------------------------
from . import bookings
from . import stay_bookings
from . import destination_bookings
from . import safari_bookings
from . import experience_bookings
from . import booking_addons
from . import booking_notes
from . import booking_payments
from . import booking_documents
from . import booking_travellers
from . import addon_catalogue

# -----------------------------------------------------------------------------
# Destinations
# -----------------------------------------------------------------------------
from . import admin_destination

# -----------------------------------------------------------------------------
# Guide
# -----------------------------------------------------------------------------
from . import admin_guide

# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------
from . import admin_settings

# -----------------------------------------------------------------------------
# Staff
# -----------------------------------------------------------------------------
from . import admin_staff

# -----------------------------------------------------------------------------
# Testimonials
# -----------------------------------------------------------------------------
from . import admin_testimonial

# -----------------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------------
from . import admin_user

# =============================================================================
# Experience Management
# =============================================================================
from . import admin_conservation_story
from . import admin_cancellation_policies
from . import admin_accessibility

# -----------------------------------------------------------------------------
# Experiences
# -----------------------------------------------------------------------------
from . import experiences

# -----------------------------------------------------------------------------
# Experience Add-ons
# -----------------------------------------------------------------------------
from . import experience_addons

# -----------------------------------------------------------------------------
# Experience Categories
# -----------------------------------------------------------------------------
from . import experience_categories

# -----------------------------------------------------------------------------
# Experience Exclusions
# -----------------------------------------------------------------------------
from . import experience_exclusions

# -----------------------------------------------------------------------------
# Experience FAQs
# -----------------------------------------------------------------------------
from . import experience_faqs

# -----------------------------------------------------------------------------
# Experience Highlights
# -----------------------------------------------------------------------------
from . import experience_highlights

# -----------------------------------------------------------------------------
# Experience Inclusions
# -----------------------------------------------------------------------------
from . import experience_inclusions

# -----------------------------------------------------------------------------
# Experience Itinerary
# -----------------------------------------------------------------------------
from . import experience_itinerary

# -----------------------------------------------------------------------------
# Experience Packing Items
# -----------------------------------------------------------------------------
from . import experience_packing_items

# -----------------------------------------------------------------------------
# Experience Photography
# -----------------------------------------------------------------------------
from . import experience_photography

# -----------------------------------------------------------------------------
# Experience Pricing
# -----------------------------------------------------------------------------
from . import experience_pricing

# -----------------------------------------------------------------------------
# Experience Requirements
# -----------------------------------------------------------------------------
from . import experience_requirements

# -----------------------------------------------------------------------------
# Experience Reviews
# -----------------------------------------------------------------------------
from . import experience_reviews

# -----------------------------------------------------------------------------
# Experience Safety Rules
# -----------------------------------------------------------------------------
from . import experience_safety_rules

# -----------------------------------------------------------------------------
# Experience Tags
# -----------------------------------------------------------------------------
from . import experience_tags

# -----------------------------------------------------------------------------
# Experience Wildlife
# -----------------------------------------------------------------------------
from . import experience_wildlife

# =============================================================================
# Media & Homepage
# =============================================================================
# -----------------------------------------------------------------------------
# Homepage
# -----------------------------------------------------------------------------
from . import homepage
from . import admin_legal_help

# -----------------------------------------------------------------------------
# Media Library
# -----------------------------------------------------------------------------
from . import media

# -----------------------------------------------------------------------------
# Stays
# -----------------------------------------------------------------------------
from . import admin_stay
from . import admin_stay_media
from . import admin_stay_room_media
from . import admin_stay_review
from . import admin_stay_room_amenity
from . import admin_stay_room
from . import admin_stay_amenity
