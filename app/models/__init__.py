"""
===============================================================================
The Uncharted Route
Database Models Package
This module imports all SQLAlchemy models so that they are registered with
SQLAlchemy when the application starts.

IMPORTANT
---------
Every model should be imported here.
This allows Flask-Migrate / Alembic to discover the complete database schema.
===============================================================================
"""
# =============================================================================
# Core User Model
# =============================================================================
from .user import User

# =============================================================================
# Destination
# =============================================================================
from .destination import Destination
from .destination_journey import DestinationJourney, DestinationJourneyStop
from .destination_booking import DestinationBooking

# =============================================================================
# Experience Core
# =============================================================================
from .experience_category import ExperienceCategory
from .experience import Experience
from .experience_pricing import ExperiencePricing
from .experience_itinerary import ExperienceItinerary
from .experience_inclusion import ExperienceInclusion
from .experience_exclusion import ExperienceExclusion
from .experience_highlight import ExperienceHighlight
from .experience_addon import ExperienceAddon
from .experience_inquiry import ExperienceInquiry

# =============================================================================
# Experience Preparation & Guest Information
# =============================================================================
from .experience_packing_item import ExperiencePackingItem
from .experience_safety_rule import ExperienceSafetyRule
from .experience_requirement import ExperienceRequirement
from .experience_faq import ExperienceFAQ

# =============================================================================
# Experience Media
# =============================================================================
from .media_asset import MediaAsset
from .experience_media import ExperienceMedia
from .media_folder import MediaFolder
from .media_asset_folder import MediaAssetFolder

# =============================================================================
# ADMIN Homepage
# =============================================================================
from .homepage import Homepage
from .homepage_section import HomepageSection
from .promotion import Promotion

# =============================================================================
# Wildlife & Conservation
# =============================================================================
from .wildlife_species import WildlifeSpecies
from .experience_wildlife import ExperienceWildlife
from .conservation_story import ConservationStory

# =============================================================================
# Photography
# =============================================================================
from .photography_spot import PhotographySpot
from .experience_photography import ExperiencePhotography

# =============================================================================
# Experience Signature Content
# =============================================================================
from .signature_moment import SignatureMoment

# =============================================================================
# Safari
# =============================================================================
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPropertyMedia,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
    SafariInquiry,)
from .safari_booking import SafariBooking
# =============================================================================
# Policies & Accessibility
# =============================================================================
from .cancellation_policy import CancellationPolicy
from .accessibility import Accessibility
from .page_hero import PageHero

# =============================================================================
# Experience Classification
# =============================================================================
from .experience_review import ExperienceReview
from .experience_tag import ExperienceTag

# =============================================================================
# Booking
# =============================================================================
from .booking import Booking
from .experience_booking import ExperienceBooking
from .booking_addon import BookingAddon
from .booking_payment import BookingPayment
from .booking_note import BookingNote
from .booking_document import BookingDocument
from .booking_traveller import BookingTraveller
from .booking_request import BookingRequest
from .addon_catalogue import AddonCatalogue

# =============================================================================
# Customer & Communication
# =============================================================================
from .testimonial import Testimonial
from .testimonial_taxonomy import (
    TestimonialCategory,
    TestimonialTag,)
from .contact import Contact
from .contact_reply import ContactReply
from .contact_note import ContactNote
from .newsletter import Newsletter, NewsletterSubscriber
from .notification import Notification
from .site_setting import SiteSetting

# =============================================================================
# Blog
# =============================================================================
from .blog_category import BlogCategory
from .blog_post import BlogPost

# =============================================================================
# Legal & Help
# =============================================================================
from app.models.faq import FAQ
from app.models.legal_help_page import LegalHelpPage
from app.models.legal_help_section import LegalHelpSection
from app.models.legal_help_item import LegalHelpItem

# =============================================================================
# Staff Management
# =============================================================================
from .staff import Staff
from .staff_availability import StaffAvailability
from .staff_schedule import StaffSchedule
from .staff_assignment import StaffAssignment
from .task import Task
from .task_assignment import TaskAssignment

# =============================================================================
# Stays Management
# =============================================================================
from .stay import Stay
from .stay_room import StayRoom
from .stay_media import StayMedia
from .stay_amenity import StayAmenity
from .stay_room_amenity import StayRoomAmenity
from .stay_review import StayReview
from .stay_booking import StayBooking
from app.models.stay_inquiry import StayInquiry

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # User
    "User",

    #Homepage
    "Homepage",
    "HomepageSection",
    "Promotion",

    # Destination
    "Destination",
    "DestinationJourney",
    "DestinationBooking",
    "DestinationJourneyStop",

    # Experience
    "ExperienceCategory",
    "Experience",
    "ExperiencePricing",
    "ExperienceItinerary",
    "ExperienceInclusion",
    "ExperienceExclusion",
    "ExperienceHighlight",
    "ExperienceAddon",
    "ExperienceInquiry",

    # Experience preparation
    "ExperiencePackingItem",
    "ExperienceSafetyRule",
    "ExperienceRequirement",
    "ExperienceFAQ",

    #Safari
    "SafariDestination",
    "SafariProperty",
    "SafariPropertyMedia",
    "SafariPackageOption",
    "SafariItineraryDay",
    "SafariPackageRate",
    "SafariInquiry",
    "SafariBooking",

    # Media
    "MediaAsset",
    "ExperienceMedia",
    "MediaFolder",
    "MediaAssetFolder",

    # Wildlife
    "WildlifeSpecies",
    "ExperienceWildlife",
    "ConservationStory",

    # Photography
    "PhotographySpot",
    "ExperiencePhotography",

    # Signature content
    "SignatureMoment",

    # Policies
    "CancellationPolicy",
    "Accessibility",
    "PageHero",

    # Experience classification
    "ExperienceReview",
    "ExperienceTag",

    # Booking
    "Booking",
    "ExperienceBooking",
    "BookingAddon",
    "BookingPayment",
    "BookingDocument",
    "BookingNote",
    "BookingTraveller",
    "BookingRequest",
    "AddonCatalogue",

    "Staff",
    "StaffSchedule",
    "StaffAssignment",
    "StaffAvailability",
    "Task",
    "TaskAssignment",

    # Communication
    "Testimonial",
    "TestimonialTag",
    "TestimonialCategory",
    "Contact",
    "ContactReply",
    "ContactNote",
    "Newsletter",
    "NewsletterSubscriber",
    "Notification",
    "SiteSetting",

    # Blog
    "BlogCategory",
    "BlogPost",

    #Stays
    "Stay",
    "StayMedia",
    "StayReview",
    "StayRoom",
    "StayBooking",
    "StayAmenity",
    "StayRoomAmenity",
    "StayInquiry"]