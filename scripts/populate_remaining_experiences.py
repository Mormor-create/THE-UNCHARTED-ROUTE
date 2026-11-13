# ================================================================
# THE UNCHARTED ROUTE
# Batch population: four Nairobi experiences
#
# DEFAULT: DRY RUN
# APPLY:   python scripts/populate_remaining_experiences.py --apply
#
# Creates:
#   COE-CAF-001  Connect Coffee Museum
#   COE-CAF-002  Karunguru Coffee Farm
#   COE-CUL-001  Brown's Cheese Factory
#   CUL-ART-001  Nairobi Art, Galleries & Creative Spaces
#
# Uses existing CMS records only.
# Does not create media, schedules, bookings or CMS records.
# Existing experiences are never modified.
# ================================================================

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import or_

from app import create_app
from extensions import db

from app.models import (
    Experience,
    ExperienceCategory,
    Destination,
    CancellationPolicy,
    Accessibility,
    ExperienceTag,
    SignatureMoment,
    ExperiencePricing,
    ExperienceItinerary,
    ExperienceInclusion,
    ExperienceExclusion,
    ExperienceHighlight,
    ExperienceAddon,
    ExperiencePackingItem,
    ExperienceSafetyRule,
    ExperienceRequirement,
    ExperienceFAQ,
    ExperienceWildlife,
    ExperiencePhotography,)

# ================================================================
# SHARED CONFIGURATION
# ================================================================
DESTINATION_ID = 1                  # Nairobi, as explicitly agreed
CANCELLATION_POLICY_ID = 2          # Standard Experience Policy
ACCESSIBILITY_PROFILE_ID = 5        # Easy Access

CATEGORY_CULINARY = 9
CATEGORY_CULTURE = 3

# No conservation story is assigned to these experiences.
# No wildlife or photography associations are appropriate by default.


# ================================================================
# DATA HELPERS
# ================================================================

def itinerary(title, time, description):
    return {
        "day_number": 1,
        "title": title,
        "activity_time": time,
        "description": description,
    }


def inclusion(title, description, icon):
    return {
        "title": title,
        "description": description,
        "icon": icon,
    }


def exclusion(title, description, icon):
    return {
        "title": title,
        "description": description,
        "icon": icon,
    }


def highlight(title, description, icon, highlight_type):
    return {
        "title": title,
        "description": description,
        "icon": icon,
        "highlight_type": highlight_type,
    }


def packing(name, description, category, icon,
            recommended=True, required=False):
    return {
        "name": name,
        "description": description,
        "category": category,
        "icon": icon,
        "recommended": recommended,
        "required": required,
    }


def safety(title, description, category, priority, icon):
    return {
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "icon": icon,
    }


def requirement(title, description, category,
                mandatory, icon):
    return {
        "title": title,
        "description": description,
        "category": category,
        "mandatory": mandatory,
        "icon": icon,
    }


def faq(question, answer, category):
    return {
        "question": question,
        "answer": answer,
        "category": category,
    }


def pricing(explorer, signature, luxury):
    """
    Each argument contains:
        (minimum_people, maximum_people, price)

    The returned list follows the existing TUR pricing model.
    """
    rows = []

    for tier, tier_rows in (
        ("Explorer", explorer),
        ("Signature", signature),
        ("Luxury", luxury),
    ):
        for minimum, maximum, amount in tier_rows:
            rows.append({
                "experience_level": tier,
                "minimum_people": minimum,
                "maximum_people": maximum,
                "price": amount,
                "currency": "KES",
                "notes": (
                    "Per person. Final arrangements are subject to "
                    "the confirmed itinerary and supplier availability."
                ),
            })

    return rows


def ordered(records):
    """Add display order and active status to child records."""
    result = []

    for index, record in enumerate(records, 1):
        item = dict(record)
        item["display_order"] = index
        item["active"] = True
        result.append(item)

    return result


# ================================================================
# EXPERIENCE CONTENT
# ================================================================
EXPERIENCES = [

    # ------------------------------------------------------------
    # 1. CONNECT COFFEE MUSEUM
    # ------------------------------------------------------------

    {
        "code": "COE-CAF-001",
        "slug": "connect-coffee-museum",
        "title": "Connect Coffee Museum",
        "category_id": CATEGORY_CULINARY,

        "short_description": (
            "Discover the story of Kenyan coffee through an engaging "
            "coffee experience exploring its origins, production, "
            "preparation and flavour."
        ),

        "description": (
            "Explore the world of Kenyan coffee through a hosted "
            "experience at Connect Coffee Museum. Discover the journey "
            "from coffee cultivation and processing to roasting, "
            "preparation and the cup. Learn about the people, methods "
            "and characteristics that shape coffee, while enjoying "
            "an opportunity to taste and appreciate the finished drink.\n\n"
            "The experience is designed for coffee enthusiasts, "
            "curious travellers and guests interested in Kenya's "
            "coffee culture. The museum visit includes one coffee "
            "and a small dessert as part of the stated venue package.\n\n"
            "The experience is subject to venue availability and "
            "confirmation of the selected visit time. Any additional "
            "purchases, food or drinks beyond the stated package "
            "are paid separately."
        ),

        "duration": "Approximately 2–3 hours",
        "meeting_point": (
            "Connect Coffee Museum, Nairobi; exact meeting instructions "
            "provided after confirmation"
        ),
        "location": "Nairobi, Kenya",
        "price_from": 6500,
        "minimum_people": 1,
        "maximum_people": None,
        "minimum_age": None,
        "difficulty": "Easy",

        "meta_title": (
            "Connect Coffee Museum Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Discover Kenyan coffee at Connect Coffee Museum with "
            "The Uncharted Route. Explore coffee culture, production, "
            "preparation and tasting."
        ),

        "featured": False,
        "display_order": 10,

        "tag_ids": [5, 14, 22, 24],
        "moment_ids": [18, 19],

        "itinerary": [
            itinerary(
                "Arrival and Welcome",
                "To be confirmed",
                "Meet the venue host and receive an introduction "
                "to the experience and the coffee museum."
            ),
            itinerary(
                "Discovering Coffee",
                "To be confirmed",
                "Explore the story of coffee, including its origins, "
                "cultivation, processing and place in Kenyan coffee culture."
            ),
            itinerary(
                "From Processing to Preparation",
                "To be confirmed",
                "Learn about the stages that bring coffee from its "
                "harvested form to the prepared drink."
            ),
            itinerary(
                "Coffee Tasting",
                "To be confirmed",
                "Enjoy the included coffee and discover its flavour "
                "and characteristics."
            ),
            itinerary(
                "Dessert and Departure",
                "To be confirmed",
                "Enjoy the included small dessert and conclude "
                "the museum experience."
            ),
        ],

        "inclusions": [
            inclusion(
                "Hosted museum experience",
                "Access to the confirmed Connect Coffee Museum "
                "experience and its hosted activities.",
                "coffee"
            ),
            inclusion(
                "Coffee experience",
                "One coffee is included in the stated venue package.",
                "coffee"
            ),
            inclusion(
                "Small dessert",
                "One small dessert is included in the stated venue package.",
                "cake-slice"
            ),
            inclusion(
                "Experience coordination",
                "Pre-visit coordination and communication of "
                "confirmed venue arrangements.",
                "calendar-check"
            ),
        ],

        "exclusions": [
            exclusion(
                "Additional food and beverages",
                "Food and drinks beyond the one included coffee "
                "and small dessert are paid separately.",
                "utensils"
            ),
            exclusion(
                "Personal purchases",
                "Retail products, coffee purchases and other "
                "personal purchases are not included.",
                "shopping-bag"
            ),
            exclusion(
                "Transport",
                "Transport is not included unless expressly stated "
                "in the confirmed booking.",
                "car"
            ),
            exclusion(
                "Unlisted activities",
                "Activities or services not expressly included "
                "in the confirmed package are excluded.",
                "plus-circle"
            ),
        ],

        "highlights": [
            highlight(
                "Discover Kenyan Coffee",
                "Explore the story and character of coffee "
                "through a dedicated museum experience.",
                "coffee",
                "Culinary"
            ),
            highlight(
                "Understand the Coffee Journey",
                "Learn about the journey from cultivation "
                "and processing to preparation.",
                "sprout",
                "Learning"
            ),
            highlight(
                "Coffee Tasting",
                "Enjoy the included coffee and discover "
                "its flavour characteristics.",
                "cup-soda",
                "Tasting"
            ),
            highlight(
                "A Sweet Finish",
                "Conclude the visit with the included small dessert.",
                "cake-slice",
                "Dining"
            ),
        ],

        "addons": [],

        "packing": [
            packing(
                "Comfortable clothing",
                "Wear comfortable clothing suitable for an indoor "
                "museum and tasting experience.",
                "Clothing",
                "shirt"
            ),
            packing(
                "Personal identification",
                "Carry identification if required by the venue "
                "or booking arrangements.",
                "Documentation",
                "id-card",
                False
            ),
            packing(
                "Camera or phone",
                "Photography should follow the venue's photography "
                "and visitor guidelines.",
                "Photography",
                "camera",
                False
            ),
        ],

        "safety": [
            safety(
                "Follow venue instructions",
                "Follow instructions from the venue host and staff "
                "throughout the visit.",
                "General",
                "High",
                "shield-check"
            ),
            safety(
                "Respect museum displays",
                "Do not touch equipment, displays or restricted "
                "items unless invited to do so by the host.",
                "Venue",
                "Medium",
                "hand"
            ),
            safety(
                "Communicate dietary needs",
                "Inform the venue and TUR of relevant dietary "
                "requirements before the visit.",
                "Food",
                "Medium",
                "utensils"
            ),
        ],

        "requirements": [
            requirement(
                "Confirm the visit",
                "The visit must be coordinated and confirmed "
                "before arrival.",
                "Booking",
                True,
                "calendar-check"
            ),
            requirement(
                "Share dietary requirements",
                "Communicate allergies or dietary requirements "
                "before the experience.",
                "Guest Information",
                False,
                "info"
            ),
            requirement(
                "Arrive at the agreed time",
                "Arrive at the confirmed meeting point at the "
                "agreed time.",
                "Logistics",
                True,
                "clock"
            ),
        ],

        "faqs": [
            faq(
                "What is included in the Connect Coffee Museum visit?",
                "The stated venue package includes the museum "
                "experience, one coffee and a small dessert. "
                "Any additional purchases are separate.",
                "Inclusions"
            ),
            faq(
                "Is this a coffee farm tour?",
                "No. This is a museum-based coffee experience. "
                "It is distinct from the Karunguru Coffee Farm visit.",
                "Experience"
            ),
            faq(
                "Is transport included?",
                "Transport is not included unless expressly stated "
                "in your confirmed booking.",
                "Transport"
            ),
            faq(
                "Can I buy coffee at the venue?",
                "Any retail purchases are subject to venue "
                "availability and are paid separately.",
                "Shopping"
            ),
            faq(
                "Does the experience need advance confirmation?",
                "Yes. The visit time and venue arrangements "
                "must be confirmed before arrival.",
                "Booking"
            ),
        ],
    },

    # ------------------------------------------------------------
    # 2. KARUNGURU COFFEE FARM
    # ------------------------------------------------------------

    {
        "code": "COE-CAF-002",
        "slug": "karunguru-coffee-farm",
        "title": "Karunguru Coffee Farm",
        "category_id": CATEGORY_CULINARY,

        "short_description": (
            "Explore the journey of Kenyan coffee at Karunguru Coffee "
            "Farm, from the coffee fields and production process "
            "to a guided tasting."
        ),

        "description": (
            "Discover the journey behind Kenyan coffee at Karunguru "
            "Coffee Farm. This guided farm experience introduces "
            "guests to coffee cultivation and the stages involved "
            "in transforming harvested coffee into the drink "
            "enjoyed around the world.\n\n"
            "Walk through the farm, learn about coffee growing "
            "and processing, and gain an appreciation of the work "
            "that takes place before coffee reaches the cup. "
            "The experience concludes with a coffee tasting.\n\n"
            "The published morning tour window is 11:00 to 13:00. "
            "The final visit time, farm access and activities must "
            "be confirmed before the experience date. Seasonal "
            "conditions and farm operations may influence what "
            "guests are able to observe."
        ),

        "duration": "Approximately 2 hours",
        "meeting_point": (
            "Karunguru Coffee Farm; exact arrival instructions "
            "provided after confirmation"
        ),
        "location": "Karunguru Coffee Farm, Kiambu County, Kenya",
        "price_from": 10500,
        "minimum_people": 1,
        "maximum_people": None,
        "minimum_age": None,
        "difficulty": "Easy",

        "meta_title": (
            "Karunguru Coffee Farm Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore coffee cultivation, farm life, processing "
            "and tasting at Karunguru Coffee Farm with "
            "The Uncharted Route."
        ),

        "featured": False,
        "display_order": 11,

        "tag_ids": [5, 14, 22, 23, 24],
        "moment_ids": [17, 18, 19],

        "itinerary": [
            itinerary(
                "Arrival at Karunguru Coffee Farm",
                "11:00",
                "Arrive at the farm and meet the host for "
                "the introduction to the visit."
            ),
            itinerary(
                "Guided Farm Walk",
                "11:15",
                "Explore the coffee farm and learn about "
                "coffee cultivation and growing conditions."
            ),
            itinerary(
                "Coffee Production Journey",
                "12:00",
                "Discover the stages involved in coffee "
                "harvesting and processing, subject to "
                "the farm's operating activities."
            ),
            itinerary(
                "Coffee Tasting",
                "12:30",
                "Enjoy a guided coffee tasting and learn "
                "about the characteristics of the coffee."
            ),
            itinerary(
                "Conclusion",
                "13:00",
                "Conclude the visit and depart from the farm."
            ),
        ],

        "inclusions": [
            inclusion(
                "Guided coffee farm visit",
                "A hosted visit to Karunguru Coffee Farm.",
                "coffee"
            ),
            inclusion(
                "Farm walk",
                "A guided walk through the farm and an introduction "
                "to coffee cultivation.",
                "footprints"
            ),
            inclusion(
                "Coffee production interpretation",
                "An introduction to the coffee production process "
                "from cultivation through processing.",
                "sprout"
            ),
            inclusion(
                "Coffee tasting",
                "A guided opportunity to taste coffee and "
                "appreciate its characteristics.",
                "coffee"
            ),
            inclusion(
                "Experience coordination",
                "Pre-visit coordination and confirmation "
                "of farm arrangements.",
                "calendar-check"
            ),
        ],

        "exclusions": [
            exclusion(
                "Transport",
                "Transport to and from the farm is excluded "
                "unless expressly included in the confirmed booking.",
                "car"
            ),
            exclusion(
                "Meals",
                "Meals are not included unless expressly stated "
                "in the confirmed package.",
                "utensils"
            ),
            exclusion(
                "Personal purchases",
                "Coffee purchases, merchandise and other personal "
                "purchases are paid separately.",
                "shopping-bag"
            ),
            exclusion(
                "Unlisted activities",
                "Activities not expressly listed in the confirmed "
                "package are excluded.",
                "plus-circle"
            ),
        ],

        "highlights": [
            highlight(
                "Walk Through a Working Coffee Farm",
                "Discover the farm environment and the growing "
                "conditions behind Kenyan coffee.",
                "sprout",
                "Farm"
            ),
            highlight(
                "Understand Coffee Cultivation",
                "Learn about the cultivation process and "
                "the work involved in growing coffee.",
                "leaf",
                "Learning"
            ),
            highlight(
                "Discover Coffee Processing",
                "Explore the stages that transform harvested "
                "coffee into a product ready for preparation.",
                "settings",
                "Learning"
            ),
            highlight(
                "From Farm to Cup",
                "Bring the experience together through "
                "a guided coffee tasting.",
                "coffee",
                "Tasting"
            ),
        ],

        "addons": [],

        "packing": [
            packing(
                "Comfortable walking shoes",
                "Wear comfortable closed shoes suitable "
                "for walking around a farm.",
                "Clothing",
                "footprints"
            ),
            packing(
                "Sun protection",
                "Bring a hat, sunscreen and sunglasses "
                "for outdoor portions.",
                "Personal Care",
                "sun"
            ),
            packing(
                "Light jacket",
                "A light layer may be useful depending "
                "on the weather.",
                "Clothing",
                "shirt"
            ),
            packing(
                "Camera or phone",
                "Photography is subject to farm and host guidelines.",
                "Photography",
                "camera",
                False
            ),
            packing(
                "Personal medication",
                "Carry any personal medication you may need.",
                "Personal Care",
                "pill",
                False
            ),
        ],

        "safety": [
            safety(
                "Follow the farm guide",
                "Remain with the guide and follow instructions "
                "throughout the farm walk.",
                "General",
                "High",
                "user-check"
            ),
            safety(
                "Use designated paths",
                "Use designated visitor paths and avoid entering "
                "restricted production or working areas.",
                "Farm",
                "High",
                "footprints"
            ),
            safety(
                "Respect farm equipment",
                "Do not operate or touch machinery and equipment "
                "unless explicitly invited by the host.",
                "Equipment",
                "High",
                "shield-check"
            ),
            safety(
                "Observe weather conditions",
                "Take care on outdoor paths, particularly "
                "if surfaces are wet or uneven.",
                "Environment",
                "Medium",
                "cloud-rain"
            ),
        ],

        "requirements": [
            requirement(
                "Advance visit confirmation",
                "The farm visit must be confirmed before arrival.",
                "Booking",
                True,
                "calendar-check"
            ),
            requirement(
                "Arrive within the confirmed tour window",
                "The published morning tour window is 11:00–13:00. "
                "Your exact arrival instructions will be confirmed.",
                "Timing",
                True,
                "clock"
            ),
            requirement(
                "Share mobility or dietary needs",
                "Inform TUR of relevant mobility or dietary "
                "requirements before the visit.",
                "Guest Information",
                False,
                "info"
            ),
        ],

        "faqs": [
            faq(
                "How long is the Karunguru Coffee Farm experience?",
                "The published morning tour is approximately "
                "two hours, from 11:00 to 13:00.",
                "Duration"
            ),
            faq(
                "What will we do during the visit?",
                "The experience includes a farm walk, an introduction "
                "to coffee cultivation and processing, and coffee tasting.",
                "Itinerary"
            ),
            faq(
                "Is this the same as Connect Coffee Museum?",
                "No. Karunguru is a farm-based experience, while "
                "Connect Coffee Museum is a separate museum-based visit.",
                "Experience"
            ),
            faq(
                "Is transport included?",
                "Transport is excluded unless it is expressly "
                "listed in your confirmed booking.",
                "Transport"
            ),
            faq(
                "Can we visit outside the morning tour window?",
                "The published morning tour window is 11:00–13:00. "
                "Any alternative time must be confirmed directly "
                "through the booking arrangements.",
                "Booking"
            ),
        ],
    },

    # ------------------------------------------------------------
    # 3. BROWN'S CHEESE FACTORY
    # ------------------------------------------------------------

    {
        "code": "COE-CUL-001",
        "slug": "browns-cheese-factory",
        "title": "Brown's Cheese Factory",
        "category_id": CATEGORY_CULINARY,

        "short_description": (
            "Discover artisan cheese-making at Brown's Cheese Factory "
            "through a guided factory and ageing-caves tour, tasting "
            "and a three-course lunch."
        ),

        "description": (
            "Enjoy a guided culinary experience at Brown's Cheese "
            "Factory, discovering the craft and processes behind "
            "artisan cheese production. The visit introduces guests "
            "to the factory and ageing caves, with an opportunity "
            "to learn about cheese-making and the stages involved "
            "in developing flavour and texture.\n\n"
            "The experience includes a cheese-making demonstration, "
            "a garden foraging element, a tasting of approximately "
            "8–10 cheeses and a three-course lunch as part of "
            "the supplier package.\n\n"
            "The experience operates by reservation. The published "
            "reservation window is 11:30 to 15:30. The standard "
            "supplier package is included in the TUR selling price "
            "and must not be charged to the guest a second time.\n\n"
            "Dietary requirements, final reservation details and "
            "availability must be communicated and confirmed "
            "before the visit."
        ),

        "duration": "Approximately 4 hours",
        "meeting_point": (
            "Brown's Cheese Factory, Limuru; exact arrival instructions "
            "provided after confirmation"
        ),
        "location": "Limuru, Kiambu County, Kenya",
        "price_from": 11500,
        "minimum_people": 1,
        "maximum_people": None,
        "minimum_age": None,
        "difficulty": "Easy",

        "meta_title": (
            "Brown's Cheese Factory Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Discover artisan cheese-making, ageing caves, cheese "
            "tasting and a three-course lunch at Brown's Cheese Factory."
        ),

        "featured": False,
        "display_order": 12,

        "tag_ids": [5, 14, 22],
        "moment_ids": [17, 19, 21],

        "itinerary": [
            itinerary(
                "Arrival and Welcome",
                "11:30",
                "Arrive for the confirmed reservation and receive "
                "an introduction to the experience."
            ),
            itinerary(
                "Factory and Ageing-Caves Tour",
                "To be confirmed",
                "Explore the cheese factory and ageing caves "
                "with the host, learning about the production "
                "and maturation process."
            ),
            itinerary(
                "Cheese-Making Demonstration",
                "To be confirmed",
                "Observe a cheese-making demonstration and "
                "learn about the craft behind the finished product."
            ),
            itinerary(
                "Garden Foraging",
                "To be confirmed",
                "Enjoy the garden foraging element as part "
                "of the hosted culinary experience."
            ),
            itinerary(
                "Cheese Tasting",
                "To be confirmed",
                "Taste a selection of approximately 8–10 cheeses "
                "and discover their different characteristics."
            ),
            itinerary(
                "Three-Course Lunch",
                "To be confirmed",
                "Enjoy the three-course lunch included in "
                "the standard supplier package."
            ),
            itinerary(
                "Conclusion and Departure",
                "15:30",
                "Conclude the visit and depart following "
                "the confirmed reservation arrangements."
            ),
        ],

        "inclusions": [
            inclusion(
                "Factory and ageing-caves tour",
                "A guided tour introducing guests to the cheese "
                "factory and ageing caves.",
                "factory"
            ),
            inclusion(
                "Cheese-making demonstration",
                "A hosted demonstration introducing the "
                "cheese-making process.",
                "book-open"
            ),
            inclusion(
                "Garden foraging experience",
                "The garden foraging element included "
                "in the standard supplier package.",
                "sprout"
            ),
            inclusion(
                "Cheese tasting",
                "A tasting of approximately 8–10 cheeses.",
                "utensils"
            ),
            inclusion(
                "Three-course lunch",
                "The three-course lunch included in the "
                "standard supplier package.",
                "utensils"
            ),
            inclusion(
                "Experience coordination",
                "Reservation coordination and communication "
                "of confirmed visit arrangements.",
                "calendar-check"
            ),
        ],

        "exclusions": [
            exclusion(
                "Transport",
                "Transport is excluded unless expressly included "
                "in the confirmed booking.",
                "car"
            ),
            exclusion(
                "Additional purchases",
                "Retail products and purchases beyond the "
                "included supplier package are paid separately.",
                "shopping-bag"
            ),
            exclusion(
                "Additional food and beverages",
                "Food or beverages beyond the stated supplier "
                "package are excluded.",
                "utensils"
            ),
            exclusion(
                "Unlisted services",
                "Services not expressly included in the "
                "confirmed supplier package are excluded.",
                "plus-circle"
            ),
        ],

        "highlights": [
            highlight(
                "Behind the Cheese-Making Process",
                "Discover the craft and processes involved "
                "in producing artisan cheese.",
                "factory",
                "Culinary"
            ),
            highlight(
                "Explore the Ageing Caves",
                "Learn how cheese is matured and how "
                "ageing contributes to its character.",
                "warehouse",
                "Learning"
            ),
            highlight(
                "Taste 8–10 Cheeses",
                "Explore a selection of approximately "
                "8–10 cheeses during the tasting.",
                "utensils",
                "Tasting"
            ),
            highlight(
                "A Three-Course Lunch",
                "Enjoy the lunch included in the standard "
                "supplier package.",
                "chef-hat",
                "Dining"
            ),
        ],

        "addons": [],

        "packing": [
            packing(
                "Comfortable shoes",
                "Wear comfortable shoes suitable for moving "
                "around visitor and garden areas.",
                "Clothing",
                "footprints"
            ),
            packing(
                "Light layers",
                "Bring a light layer suitable for the "
                "outdoor and indoor portions.",
                "Clothing",
                "shirt"
            ),
            packing(
                "Personal medication",
                "Carry any personal medication you may need.",
                "Personal Care",
                "pill",
                False
            ),
            packing(
                "Dietary information",
                "Be ready to communicate any dietary "
                "requirements or allergies before the visit.",
                "Food",
                "utensils",
                True
            ),
        ],

        "safety": [
            safety(
                "Follow factory safety instructions",
                "Follow the host's instructions throughout "
                "the factory and production areas.",
                "Factory",
                "High",
                "shield-check"
            ),
            safety(
                "Respect restricted production areas",
                "Do not enter restricted areas or touch "
                "equipment unless invited by the host.",
                "Factory",
                "High",
                "ban"
            ),
            safety(
                "Communicate food allergies",
                "Inform TUR and the venue of food allergies "
                "and dietary restrictions before the visit.",
                "Food",
                "Critical",
                "alert-circle"
            ),
            safety(
                "Observe garden guidance",
                "Follow instructions during the garden "
                "foraging element and do not consume "
                "unidentified plants.",
                "Garden",
                "High",
                "leaf"
            ),
        ],

        "requirements": [
            requirement(
                "Reservation required",
                "The experience is reservation-only. "
                "A confirmed reservation is required before arrival.",
                "Booking",
                True,
                "calendar-check"
            ),
            requirement(
                "Confirm dietary requirements",
                "Communicate allergies and dietary requirements "
                "before the reservation is finalized.",
                "Food",
                True,
                "utensils"
            ),
            requirement(
                "Arrive within the reservation window",
                "The published reservation window is 11:30–15:30. "
                "Your exact arrival instructions will be confirmed.",
                "Timing",
                True,
                "clock"
            ),
            requirement(
                "Share accessibility needs",
                "Inform TUR of mobility or accessibility "
                "requirements before the visit.",
                "Guest Information",
                False,
                "accessibility"
            ),
        ],

        "faqs": [
            faq(
                "What is included in the Brown's Cheese Factory visit?",
                "The standard supplier package includes a factory "
                "and ageing-caves tour, cheese-making demonstration, "
                "garden foraging, a tasting of approximately 8–10 "
                "cheeses and a three-course lunch.",
                "Inclusions"
            ),
            faq(
                "Is lunch included?",
                "Yes. The three-course lunch is included in "
                "the standard supplier package and is already "
                "accounted for in the TUR selling price.",
                "Meals"
            ),
            faq(
                "Do I pay the factory package fee separately?",
                "No. The standard supplier package is included "
                "in the TUR selling price. It should not be "
                "charged to you a second time.",
                "Pricing"
            ),
            faq(
                "Does the experience require a reservation?",
                "Yes. The experience is reservation-only. "
                "The published reservation window is 11:30–15:30.",
                "Booking"
            ),
            faq(
                "Can dietary requirements be accommodated?",
                "Dietary requirements and allergies must be "
                "communicated before the reservation. Any "
                "accommodation is subject to venue confirmation.",
                "Food"
            ),
            faq(
                "Is transport included?",
                "Transport is excluded unless expressly listed "
                "in your confirmed booking.",
                "Transport"
            ),
        ],
    },

    # ------------------------------------------------------------
    # 4. NAIROBI ART, GALLERIES & CREATIVE SPACES
    # ------------------------------------------------------------

    {
        "code": "CUL-ART-001",
        "slug": "nairobi-art-galleries-creative-spaces",
        "title": "Nairobi Art, Galleries & Creative Spaces",
        "category_id": CATEGORY_CULTURE,

        "short_description": (
            "Discover Nairobi's contemporary creative scene through "
            "a privately guided journey across selected galleries, "
            "art spaces and creative communities."
        ),

        "description": (
            "Discover Nairobi through its creative expression. "
            "This privately guided experience introduces guests "
            "to selected art galleries, creative spaces and "
            "contemporary artistic perspectives across the city.\n\n"
            "Explore works, spaces and stories with a curated "
            "host who provides context and helps connect the "
            "different stops into a thoughtful city experience. "
            "The route is shaped around confirmed venue availability, "
            "the guest's interests and the time available.\n\n"
            "The experience includes private transport and "
            "curation/hosting as part of the confirmed arrangement. "
            "Gallery admission fees, artwork purchases and meals "
            "are separate unless expressly included in the "
            "confirmed booking.\n\n"
            "Individual galleries and creative spaces may have "
            "different opening hours, admission arrangements "
            "and photography policies. The final route is "
            "confirmed before the experience."
        ),

        "duration": "Approximately 4–5 hours",
        "meeting_point": (
            "Agreed Nairobi hotel or accommodation pickup"
        ),
        "location": "Nairobi, Kenya",
        "price_from": 8500,
        "minimum_people": 1,
        "maximum_people": None,
        "minimum_age": None,
        "difficulty": "Easy",

        "meta_title": (
            "Nairobi Art & Galleries Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore Nairobi's galleries, art spaces and creative "
            "scene through a privately guided experience with "
            "The Uncharted Route."
        ),

        "featured": False,
        "display_order": 13,

        "tag_ids": [5, 12, 19, 20, 27, 30],
        "moment_ids": [12, 16, 26],

        "itinerary": [
            itinerary(
                "Private Pickup and Introduction",
                "To be confirmed",
                "Meet your Experience Leader and receive "
                "an introduction to the curated art route."
            ),
            itinerary(
                "First Gallery or Creative Space",
                "To be confirmed",
                "Visit the first confirmed gallery or creative "
                "space and explore its selected works and stories."
            ),
            itinerary(
                "Nairobi Creative Scene",
                "To be confirmed",
                "Continue to another selected creative venue, "
                "with interpretation from your host."
            ),
            itinerary(
                "Art, Design and Local Perspectives",
                "To be confirmed",
                "Discover further works or creative spaces "
                "included in the confirmed route."
            ),
            itinerary(
                "Conclusion and Private Drop-off",
                "To be confirmed",
                "Conclude the curated experience and return "
                "to the agreed Nairobi drop-off point."
            ),
        ],

        "inclusions": [
            inclusion(
                "Private Experience Leader",
                "A dedicated host to coordinate the experience "
                "and provide context throughout the route.",
                "user"
            ),
            inclusion(
                "Curated gallery route",
                "A curated selection of galleries and creative "
                "spaces based on confirmed venue availability.",
                "palette"
            ),
            inclusion(
                "Private transportation",
                "Private transport for the planned route "
                "and agreed Nairobi pickup/drop-off.",
                "car"
            ),
            inclusion(
                "Creative interpretation",
                "Context and storytelling to help guests "
                "engage with the selected works and spaces.",
                "book-open"
            ),
            inclusion(
                "Experience coordination",
                "Pre-visit coordination of the route, "
                "venue arrangements and meeting details.",
                "calendar-check"
            ),
        ],

        "exclusions": [
            exclusion(
                "Gallery admission fees",
                "Admission fees and paid exhibitions are "
                "separate unless expressly included in "
                "the confirmed booking.",
                "ticket"
            ),
            exclusion(
                "Artwork purchases",
                "Artwork, prints, merchandise and other "
                "purchases are paid separately by the guest.",
                "shopping-bag"
            ),
            exclusion(
                "Meals and refreshments",
                "Meals, snacks and refreshments are not "
                "included unless expressly stated.",
                "utensils"
            ),
            exclusion(
                "Unlisted activities",
                "Venues, activities or services not listed "
                "in the confirmed route are excluded.",
                "plus-circle"
            ),
        ],

        "highlights": [
            highlight(
                "Discover Nairobi's Creative Scene",
                "Explore selected galleries and creative "
                "spaces that contribute to the city's "
                "artistic identity.",
                "palette",
                "Culture"
            ),
            highlight(
                "Curated Gallery Visits",
                "Experience a considered route through "
                "selected venues and exhibitions.",
                "images",
                "Art"
            ),
            highlight(
                "Stories Behind the Work",
                "Gain context and perspective through "
                "your host's interpretation.",
                "book-open",
                "Learning"
            ),
            highlight(
                "Private City Experience",
                "Discover Nairobi's creative spaces "
                "with private transport and hosting.",
                "map",
                "Private"
            ),
        ],

        "addons": [],

        "packing": [
            packing(
                "Comfortable walking shoes",
                "Wear comfortable shoes for moving between "
                "venues and gallery spaces.",
                "Clothing",
                "footprints"
            ),
            packing(
                "Camera or phone",
                "Photography is subject to each gallery's "
                "and venue's individual policies.",
                "Photography",
                "camera",
                False
            ),
            packing(
                "Personal identification",
                "Carry identification where required "
                "by individual venues.",
                "Documentation",
                "id-card",
                False
            ),
            packing(
                "Payment method",
                "Bring a suitable payment method for "
                "admission fees, meals or personal purchases "
                "not included in the confirmed package.",
                "Personal Items",
                "wallet",
                True
            ),
        ],

        "safety": [
            safety(
                "Follow gallery instructions",
                "Follow visitor instructions and respect "
                "the rules of each gallery and creative space.",
                "Venue",
                "High",
                "shield-check"
            ),
            safety(
                "Respect artworks and displays",
                "Do not touch artworks, installations "
                "or display items unless expressly permitted.",
                "Art",
                "High",
                "hand"
            ),
            safety(
                "Follow photography policies",
                "Ask before photographing artworks, "
                "artists or other visitors and observe "
                "any photography restrictions.",
                "Photography",
                "Medium",
                "camera"
            ),
            safety(
                "Use agreed transport arrangements",
                "Follow pickup, drop-off and movement "
                "instructions from your Experience Leader.",
                "Transport",
                "High",
                "car"
            ),
        ],

        "requirements": [
            requirement(
                "Confirm the curated route",
                "The selected venues and route must be "
                "confirmed before the experience.",
                "Booking",
                True,
                "calendar-check"
            ),
            requirement(
                "Share creative interests",
                "Guests may share preferred art styles, "
                "artists or creative interests before "
                "the route is finalized.",
                "Preferences",
                False,
                "palette"
            ),
            requirement(
                "Confirm pickup details",
                "Provide the agreed Nairobi pickup location "
                "and a reachable contact number.",
                "Logistics",
                True,
                "map-pin"
            ),
            requirement(
                "Allow for venue opening hours",
                "The route is subject to the opening hours "
                "and availability of participating venues.",
                "Timing",
                True,
                "clock"
            ),
        ],

        "faqs": [
            faq(
                "What does the Nairobi art experience include?",
                "The experience includes a curated gallery route, "
                "private hosting/curation and private transport "
                "as stated in the confirmed package.",
                "Inclusions"
            ),
            faq(
                "Are gallery admission fees included?",
                "Gallery admission fees and paid exhibitions "
                "are separate unless expressly included "
                "in your confirmed booking.",
                "Pricing"
            ),
            faq(
                "Can I buy artwork during the experience?",
                "Yes, subject to the gallery or artist's "
                "availability and purchasing arrangements. "
                "Artwork purchases are paid separately.",
                "Shopping"
            ),
            faq(
                "Can the route be tailored to my interests?",
                "You may share your interests before the visit. "
                "The final route depends on venue availability "
                "and confirmed arrangements.",
                "Experience"
            ),
            faq(
                "Is transport included?",
                "Yes. Private transport for the planned route "
                "is included in the confirmed package.",
                "Transport"
            ),
            faq(
                "Are meals included?",
                "Meals and refreshments are excluded unless "
                "expressly stated in the confirmed package.",
                "Meals"
            ),
            faq(
                "Can I take photographs?",
                "Photography depends on the rules of each "
                "participating gallery or creative space. "
                "Your host will help communicate the applicable "
                "venue guidelines.",
                "Photography"
            ),
        ],
    },
]


# ================================================================
# EXISTING CMS RECORD VALIDATION
# ================================================================

def require_active(model, record_id, label):
    record = db.session.get(model, record_id)

    if record is None:
        raise RuntimeError(
            f"Required {label} ID {record_id} does not exist."
        )

    if hasattr(record, "active") and not record.active:
        raise RuntimeError(
            f"Required {label} ID {record_id} is inactive."
        )

    return record


def add_children(model, experience_id, records):
    db.session.add_all([
        model(experience_id=experience_id, **record)
        for record in records
    ])


# ================================================================
# POPULATE ONE EXPERIENCE
# ================================================================

def populate_experience(data, destination, policy, accessibility):

    code = data["code"]
    slug = data["slug"]

    existing = Experience.query.filter(
        or_(
            Experience.experience_code == code,
            Experience.slug == slug,
        )
    ).first()

    if existing:
        raise RuntimeError(
            f"Duplicate protection stopped the batch. "
            f"{code} / {slug} already exists. "
            f"Existing ID: {existing.id}. "
            f"No existing experience will be modified."
        )

    category = require_active(
        ExperienceCategory,
        data["category_id"],
        "Experience category",
    )

    tags = [
        require_active(ExperienceTag, tag_id, "Experience tag")
        for tag_id in data["tag_ids"]
    ]

    moments = [
        require_active(
            SignatureMoment,
            moment_id,
            "Signature moment",
        )
        for moment_id in data["moment_ids"]
    ]

    experience = Experience(
        experience_code=code,
        title=data["title"],
        slug=slug,

        short_description=data["short_description"],
        description=data["description"],

        duration=data["duration"],
        meeting_point=data["meeting_point"],
        location=data["location"],

        price_from=data["price_from"],
        currency="KES",

        minimum_people=data["minimum_people"],
        maximum_people=data["maximum_people"],
        minimum_age=data["minimum_age"],
        difficulty=data["difficulty"],

        # Intentionally blank until media is uploaded and associated.
        featured_image="",
        banner_image=None,

        meta_title=data["meta_title"],
        meta_description=data["meta_description"],

        featured=data["featured"],
        show_on_homepage=False,
        active=True,
        display_order=data["display_order"],

        category_id=category.id,
        destination_id=destination.id,
        cancellation_policy_id=policy.id,
        accessibility_profile_id=accessibility.id,

        # No conservation story applies to these four experiences.
        conservation_story_id=None,
    )

    db.session.add(experience)
    db.session.flush()

    experience_id = experience.id

    # ------------------------------------------------------------
    # REUSABLE CMS ASSOCIATIONS
    # ------------------------------------------------------------

    for tag in tags:
        experience.tags.append(tag)

    for moment in moments:
        experience.signature_moments.append(moment)

    # ------------------------------------------------------------
    # PRICING
    # ------------------------------------------------------------

    pricing_rows = data["pricing"]

    for index, row in enumerate(pricing_rows, 1):
        row["display_order"] = index
        row["active"] = True

    add_children(
        ExperiencePricing,
        experience_id,
        pricing_rows,
    )

    # ------------------------------------------------------------
    # ITINERARY
    # ------------------------------------------------------------

    itinerary_rows = [
        {
            **record,
            "display_order": index,}for index, record in enumerate(data["itinerary"], 1)]

    add_children(
        ExperienceItinerary,
        experience_id,
        itinerary_rows,
    )

    # ------------------------------------------------------------
    # INCLUSIONS
    # ------------------------------------------------------------
    add_children(
        ExperienceInclusion,
        experience_id,
        ordered(data["inclusions"]),
    )

    # ------------------------------------------------------------
    # EXCLUSIONS
    # ------------------------------------------------------------

    add_children(
        ExperienceExclusion,
        experience_id,
        ordered(data["exclusions"]),
    )

    # ------------------------------------------------------------
    # HIGHLIGHTS
    # ------------------------------------------------------------

    highlight_rows = ordered(data["highlights"])

    for index, row in enumerate(highlight_rows, 1):
        row["featured"] = index == 1

    add_children(
        ExperienceHighlight,
        experience_id,
        highlight_rows,
    )

    # ------------------------------------------------------------
    # OPTIONAL ADD-ONS
    # ------------------------------------------------------------

    # No add-on prices or supplier terms have been approved
    # for these four experiences. Do not invent charges.
    #
    # The add-on section is deliberately empty until a specific
    # optional service and its price are confirmed.

    addon_rows = []

    add_children(
        ExperienceAddon,
        experience_id,
        addon_rows,
    )

    # ------------------------------------------------------------
    # PACKING ITEMS
    # ------------------------------------------------------------

    add_children(
        ExperiencePackingItem,
        experience_id,
        ordered(data["packing"]),
    )

    # ------------------------------------------------------------
    # SAFETY RULES
    # ------------------------------------------------------------

    add_children(
        ExperienceSafetyRule,
        experience_id,
        ordered(data["safety"]),
    )

    # ------------------------------------------------------------
    # GUEST REQUIREMENTS
    # ------------------------------------------------------------

    add_children(
        ExperienceRequirement,
        experience_id,
        ordered(data["requirements"]),
    )

    # ------------------------------------------------------------
    # FAQs
    # ------------------------------------------------------------

    faq_rows = ordered(data["faqs"])

    for index, row in enumerate(faq_rows, 1):
        row["featured"] = index <= 3

    add_children(
        ExperienceFAQ,
        experience_id,
        faq_rows,
    )

    # ------------------------------------------------------------
    # WILDLIFE / PHOTOGRAPHY
    # ------------------------------------------------------------

    # These are not wildlife experiences and do not use the
    # existing Nairobi wildlife photography spots.
    #
    # Do not create irrelevant associations.

    add_children(
        ExperienceWildlife,
        experience_id,
        [],
    )

    add_children(
        ExperiencePhotography,
        experience_id,
        [],
    )

    return experience


# ================================================================
# EXPECTED PRICING
# ================================================================

# Per-person KES:
#
#                 1 guest       2–3 guests       4+ guests
#
# CONNECT COFFEE
# Explorer          9,500          7,500           6,500
# Signature        14,500         11,500           9,500
# Luxury           22,500         18,500          15,500
#
# KARUNGURU
# Explorer         15,500         12,500          10,500
# Signature        20,500         17,500          14,500
# Luxury           31,500         26,500          22,500
#
# BROWN'S
# Explorer         16,500         13,500          11,500
# Signature        22,500         18,500          15,500
# Luxury           34,500         28,500          23,500
#
# NAIROBI ART
# Explorer         12,500         10,000           8,500
# Signature        18,500         15,000          12,500
# Luxury           29,500         24,000          20,000


def set_pricing():
    pricing_map = {
        "COE-CAF-001": (
            [(1, 1, 9500), (2, 3, 7500), (4, None, 6500)],
            [(1, 1, 14500), (2, 3, 11500), (4, None, 9500)],
            [(1, 1, 22500), (2, 3, 18500), (4, None, 15500)],
        ),
        "COE-CAF-002": (
            [(1, 1, 15500), (2, 3, 12500), (4, None, 10500)],
            [(1, 1, 20500), (2, 3, 17500), (4, None, 14500)],
            [(1, 1, 31500), (2, 3, 26500), (4, None, 22500)],
        ),
        "COE-CUL-001": (
            [(1, 1, 16500), (2, 3, 13500), (4, None, 11500)],
            [(1, 1, 22500), (2, 3, 18500), (4, None, 15500)],
            [(1, 1, 34500), (2, 3, 28500), (4, None, 23500)],
        ),
        "CUL-ART-001": (
            [(1, 1, 12500), (2, 3, 10000), (4, None, 8500)],
            [(1, 1, 18500), (2, 3, 15000), (4, None, 12500)],
            [(1, 1, 29500), (2, 3, 24000), (4, None, 20000)],
        ),
    }

    for data in EXPERIENCES:
        explorer, signature, luxury = pricing_map[data["code"]]

        data["pricing"] = pricing(
            explorer,
            signature,
            luxury,
        )


# ================================================================
# COMPONENT COUNT VERIFICATION
# ================================================================

def component_counts(experience):
    experience_id = experience.id

    return {
        "Pricing": ExperiencePricing.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Itinerary": ExperienceItinerary.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Inclusions": ExperienceInclusion.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Exclusions": ExperienceExclusion.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Highlights": ExperienceHighlight.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Add-ons": ExperienceAddon.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Packing items": ExperiencePackingItem.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Safety rules": ExperienceSafetyRule.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Requirements": ExperienceRequirement.query.filter_by(
            experience_id=experience_id
        ).count(),

        "FAQs": ExperienceFAQ.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Wildlife associations": ExperienceWildlife.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Photography associations": ExperiencePhotography.query.filter_by(
            experience_id=experience_id
        ).count(),

        "Tags": experience.tags.count(),

        "Signature moments": experience.signature_moments.count(),

        "Media associations": experience.media.count(),

        "Schedules": experience.schedules.count(),
    }


def expected_counts(data):
    return {
        "Pricing": 9,
        "Itinerary": len(data["itinerary"]),
        "Inclusions": len(data["inclusions"]),
        "Exclusions": len(data["exclusions"]),
        "Highlights": len(data["highlights"]),
        "Add-ons": 0,
        "Packing items": len(data["packing"]),
        "Safety rules": len(data["safety"]),
        "Requirements": len(data["requirements"]),
        "FAQs": len(data["faqs"]),
        "Wildlife associations": 0,
        "Photography associations": 0,
        "Tags": len(data["tag_ids"]),
        "Signature moments": len(data["moment_ids"]),
        "Media associations": 0,
        "Schedules": 0,
    }


# ================================================================
# MAIN TRANSACTION
# ================================================================

def populate(apply_changes=False):

    app = create_app()

    set_pricing()

    with app.app_context():

        try:
            # ----------------------------------------------------
            # SHARED RECORD VALIDATION
            # ----------------------------------------------------

            destination = require_active(
                Destination,
                DESTINATION_ID,
                "Destination",
            )

            policy = require_active(
                CancellationPolicy,
                CANCELLATION_POLICY_ID,
                "Cancellation policy",
            )

            accessibility = require_active(
                Accessibility,
                ACCESSIBILITY_PROFILE_ID,
                "Accessibility profile",
            )

            # ----------------------------------------------------
            # PRE-FLIGHT DUPLICATE CHECK
            # ----------------------------------------------------

            for data in EXPERIENCES:
                existing = Experience.query.filter(
                    or_(
                        Experience.experience_code == data["code"],
                        Experience.slug == data["slug"],
                    )
                ).first()

                if existing:
                    raise RuntimeError(
                        "Batch stopped because an experience "
                        "already exists.\n"
                        f"Code: {data['code']}\n"
                        f"Slug: {data['slug']}\n"
                        f"Existing ID: {existing.id}\n"
                        "No existing experience will be modified."
                    )

            # ----------------------------------------------------
            # CREATE ALL FOUR EXPERIENCES
            # ----------------------------------------------------

            created = []

            for data in EXPERIENCES:
                experience = populate_experience(
                    data,
                    destination,
                    policy,
                    accessibility,
                )

                created.append((data, experience))

            # ----------------------------------------------------
            # FLUSH ALL CHILD RECORDS
            # ----------------------------------------------------

            db.session.flush()

            # ----------------------------------------------------
            # VERIFY COMPONENT COUNTS
            # ----------------------------------------------------

            print()
            print("=" * 78)
            print("THE UNCHARTED ROUTE — EXPERIENCE BATCH")
            print("POPULATION VERIFICATION")
            print("=" * 78)

            verification_failed = False

            for data, experience in created:
                actual = component_counts(experience)
                expected = expected_counts(data)

                print()
                print("-" * 78)
                print(f"{experience.title}")
                print(f"ID: {experience.id}")
                print(f"Code: {experience.experience_code}")
                print(f"Slug: {experience.slug}")
                print(f"Category ID: {experience.category_id}")
                print(f"Destination: {destination.name} (ID {destination.id})")
                print(f"Starting price: KES {experience.price_from:,.0f}")
                print("-" * 78)

                for label, expected_count in expected.items():
                    actual_count = actual[label]
                    passed = actual_count == expected_count

                    if not passed:
                        verification_failed = True

                    status = "OK" if passed else "MISMATCH"

                    print(
                        f"{label:<30} "
                        f"{actual_count:>3} / {expected_count:<3} "
                        f"{status}"
                    )

                if actual["Media associations"] != 0:
                    verification_failed = True

                if actual["Schedules"] != 0:
                    verification_failed = True

            if verification_failed:
                raise RuntimeError(
                    "Component-count verification failed. "
                    "The entire batch will be rolled back."
                )

            # ----------------------------------------------------
            # FINAL SAFETY SUMMARY
            # ----------------------------------------------------

            print()
            print("=" * 78)
            print("BATCH SAFETY CHECK")
            print("=" * 78)
            print("Experiences created in this transaction: 4")
            print("Existing experiences modified:           0")
            print("Reusable CMS records created:             0")
            print("Media associations created:               0")
            print("Schedules created:                        0")
            print("Bookings created:                         0")
            print("Wildlife associations created:            0")
            print("Photography associations created:         0")
            print("Conservation stories assigned:             0")
            print("Destination used:                          Nairobi (ID 1)")
            print()

            # ----------------------------------------------------
            # COMMIT OR ROLLBACK
            # ----------------------------------------------------

            if apply_changes:
                db.session.commit()

                print("=" * 78)
                print("SUCCESS — FOUR EXPERIENCES SAVED")
                print("=" * 78)

                for data, _ in created:
                    saved = Experience.query.filter_by(
                        experience_code=data["code"]
                    ).one()

                    print(
                        f"{saved.id} | "
                        f"{saved.experience_code} | "
                        f"{saved.title} | "
                        f"{saved.slug}"
                    )

            else:
                db.session.rollback()

                print("=" * 78)
                print("DRY RUN COMPLETE")
                print("=" * 78)
                print("All four experiences passed verification.")
                print("No database changes were committed.")
                print()
                print(
                    "To save the batch, run:\n"
                    "python scripts/populate_remaining_experiences.py --apply"
                )

        except Exception as error:
            db.session.rollback()

            print()
            print("=" * 78)
            print("BATCH FAILED — TRANSACTION ROLLED BACK")
            print("=" * 78)
            print(str(error))

            raise


# ================================================================
# COMMAND LINE
# ================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Populate four complete TUR experiences. "
            "Defaults to dry-run."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit all four experiences to the database.",
    )

    arguments = parser.parse_args()

    populate(apply_changes=arguments.apply)