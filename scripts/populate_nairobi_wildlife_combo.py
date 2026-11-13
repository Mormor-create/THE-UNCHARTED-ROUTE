# ================================================================
# THE UNCHARTED ROUTE
# Nairobi Wildlife Combo Package
# Code: WNA-COMBO-001
#
# DEFAULT: DRY RUN
# APPLY:   python scripts/populate_nairobi_wildlife_combo.py --apply
# ================================================================

import argparse
import sys

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from extensions import db
from sqlalchemy import or_

from app.models import (
    Experience,
    ExperienceCategory,
    Destination,
    CancellationPolicy,
    Accessibility,
    ConservationStory,
    ExperienceTag,
    SignatureMoment,
    WildlifeSpecies,
    PhotographySpot,
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
    ExperiencePhotography,
)


# ================================================================
# EXPERIENCE IDENTITY
# ================================================================

EXPERIENCE_CODE = "WNA-COMBO-001"
EXPERIENCE_SLUG = "nairobi-wildlife-combo-package"

CATEGORY_ID = 1
DESTINATION_ID = 1
CANCELLATION_POLICY_ID = 3
ACCESSIBILITY_PROFILE_ID = 9
CONSERVATION_STORY_ID = 1

TAG_IDS = [
    1,  # Wildlife
    2,  # Conservation
    3,  # Game Drive
    4,  # Photography
    5,  # Nairobi
]

SIGNATURE_MOMENT_IDS = [
    1,  # Sunrise Over the Natural World
    2,  # An Unforgettable Wildlife Encounter
    3,  # Watching Wildlife in Its Natural Habitat
]

PHOTOGRAPHY_SPOT_IDS = [
    2,  # Nairobi National Park Savannah
    3,  # Giraffe Centre Viewing Area
]


# ================================================================
# WILDLIFE ASSOCIATIONS
# ================================================================

WILDLIFE_DATA = [
    {
        "species_id": 1,
        "probability": "Occasional",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "Lion sightings are possible during the game drive but "
            "are never guaranteed. Follow the Experience Leader's "
            "instructions and maintain a respectful distance."
        ),
    },
    {
        "species_id": 2,
        "probability": "Occasional",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "Black rhino sightings are possible but not guaranteed. "
            "Observe quietly and follow all park and guide instructions."
        ),
    },
    {
        "species_id": 3,
        "probability": "Common",
        "season": "All Year",
        "time": "Afternoon",
        "notes": (
            "Giraffe viewing is associated with the Giraffe Centre "
            "conservation visit. This is not a promise of a wild "
            "giraffe sighting during the game drive."
        ),
    },
    {
        "species_id": 4,
        "probability": "Common",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "Buffalo may be encountered during the game drive. "
            "Observe from the vehicle and follow guide instructions."
        ),
    },
    {
        "species_id": 5,
        "probability": "Common",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "Zebra may be encountered during the game drive. "
            "Sightings depend on wildlife movement and natural conditions."
        ),
    },
    {
        "species_id": 6,
        "probability": "Occasional",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "Cheetah sightings are not guaranteed and depend on "
            "wildlife movement and prevailing conditions."
        ),
    },
    {
        "species_id": 7,
        "probability": "Occasional",
        "season": "All Year",
        "time": "Morning",
        "notes": (
            "White rhino sightings are possible but not guaranteed. "
            "Observe quietly from approved areas."
        ),
    },
]


# ================================================================
# ITINERARY
# ================================================================

ITINERARY_DATA = [
    {
        "title": "Private Hotel Pickup",
        "time": "05:45",
        "description": (
            "Meet your professional Experience Leader and driver "
            "at your Nairobi hotel for a private departure. "
            "The pickup time is planned and may be adjusted "
            "according to the confirmed booking."
        ),
    },
    {
        "title": "Arrival at Nairobi National Park",
        "time": "06:15",
        "description": (
            "Arrive at Nairobi National Park and complete the "
            "required entry arrangements. Park admission is paid "
            "separately at the prevailing rate for each guest category."
        ),
    },
    {
        "title": "Private Sunrise Game Drive",
        "time": "06:30",
        "description": (
            "Explore Nairobi National Park with a professional guide, "
            "looking for wildlife in its natural habitat. "
            "Wildlife sightings are never guaranteed."
        ),
    },
    {
        "title": "Transfer to Conservation Experiences",
        "time": "09:30",
        "description": (
            "Leave the park and transfer towards the day's "
            "conservation visits."
        ),
    },
    {
        "title": "David Sheldrick Elephant Orphanage Visit",
        "time": "10:30",
        "description": (
            "Visit the David Sheldrick Wildlife Trust elephant "
            "conservation experience. This visit is subject to the "
            "Trust's operating arrangements, advance reservation "
            "requirements and separately payable visit fees."
        ),
    },
    {
        "title": "Lunch Break",
        "time": "12:30",
        "description": (
            "Time is reserved for lunch. A premium restaurant lunch "
            "is an optional paid add-on and is not included in the "
            "base package."
        ),
    },
    {
        "title": "Giraffe Centre Conservation Experience",
        "time": "14:00",
        "description": (
            "Visit the Giraffe Centre to learn about giraffe "
            "conservation and observe the resident giraffes. "
            "Admission is paid separately at the prevailing rate."
        ),
    },
    {
        "title": "Optional Nairobi Safari Walk Extension",
        "time": "15:30",
        "description": (
            "Guests who select this optional paid extension visit "
            "Nairobi Safari Walk, subject to operating hours, "
            "availability and separately payable admission."
        ),
    },
    {
        "title": "Return Journey",
        "time": "16:45",
        "description": (
            "Begin the return journey to the agreed Nairobi "
            "drop-off point."
        ),
    },
    {
        "title": "Hotel Drop-off",
        "time": "17:30",
        "description": (
            "Arrive back at the hotel. Actual return time depends "
            "on traffic, park conditions and venue operations."
        ),
    },
]


# ================================================================
# INCLUSIONS
# ================================================================

INCLUSIONS_DATA = [
    (
        "Private professional Experience Leader",
        "A dedicated Experience Leader to coordinate the day and "
        "provide context throughout the experience.",
        "user",
    ),
    (
        "Professional driver",
        "A professional driver for the private journey and planned transfers.",
        "car",
    ),
    (
        "Premium private transportation",
        "Private transport for the planned Nairobi itinerary.",
        "car",
    ),
    (
        "Hotel pickup and drop-off",
        "Pickup and drop-off at an agreed Nairobi hotel or accommodation.",
        "map-pin",
    ),
    (
        "Wildlife interpretation",
        "Guided interpretation during the Nairobi National Park game drive.",
        "binoculars",
    ),
    (
        "Conservation storytelling",
        "Context and learning around the conservation work encountered "
        "during the experience.",
        "leaf",
    ),
    (
        "Bottled drinking water",
        "Bottled drinking water during the experience.",
        "droplet",
    ),
    (
        "Flexible itinerary management",
        "Coordination of the day's sequence around confirmed venue "
        "arrangements and reasonable operational changes.",
        "clock",
    ),
    (
        "Attraction coordination",
        "Pre-trip coordination of the listed attraction visits and "
        "their booking requirements.",
        "ticket",
    ),
]


# ================================================================
# EXCLUSIONS
# ================================================================

EXCLUSIONS_DATA = [
    (
        "Attraction and park entrance fees",
        "All park, attraction and conservation-visit admission fees "
        "are paid separately at prevailing rates according to "
        "each guest's category.",
        "ticket",
    ),
    (
        "Meals",
        "Meals are excluded unless a meal add-on is selected "
        "and confirmed.",
        "utensils",
    ),
    (
        "Personal purchases",
        "Souvenirs, personal shopping and other personal purchases "
        "are not included.",
        "shopping-bag",
    ),
    (
        "Tips and gratuities",
        "Tips and gratuities are optional and at the guest's discretion.",
        "hand-coins",
    ),
    (
        "Travel insurance",
        "Guests are responsible for arranging suitable travel insurance.",
        "shield",
    ),
    (
        "Unselected optional activities",
        "The Nairobi Safari Walk extension and activities not expressly "
        "listed as included are excluded unless separately booked.",
        "plus-circle",
    ),
]


# ================================================================
# HIGHLIGHTS
# ================================================================

HIGHLIGHTS_DATA = [
    (
        "Sunrise wildlife drive in Nairobi National Park",
        "Begin the day with a private guided game drive in a unique "
        "wildlife setting close to the city.",
        "binoculars",
        "Wildlife",
    ),
    (
        "Elephant conservation visit",
        "Learn about elephant rescue and conservation through the "
        "David Sheldrick Wildlife Trust visit.",
        "heart",
        "Conservation",
    ),
    (
        "Giraffe conservation encounter",
        "Discover the conservation story of the Giraffe Centre "
        "and observe its resident giraffes.",
        "leaf",
        "Conservation",
    ),
    (
        "One privately coordinated Nairobi day",
        "Connect wildlife viewing and conservation visits through "
        "private transport and an Experience Leader.",
        "route",
        "Convenience",
    ),
]


# ================================================================
# OPTIONAL ADD-ONS
# Prices marked "starting from" are indicative floors.
# They are NOT automatically available for online checkout.
# ================================================================

ADDONS_DATA = [
    (
        "Professional Wildlife Photographer",
        "A professional photographer to document the experience.",
        "Photography coverage during the experience. Deliverables "
        "and availability are confirmed before booking.",
        15000,
        "Per Booking",
    ),
    (
        "Luxury Safari Land Cruiser Upgrade",
        "Upgrade the private vehicle for the safari portion.",
        "Starting from KES 25,000 per vehicle/booking, subject to "
        "vehicle availability and final confirmation.",
        25000,
        "Per Vehicle",
    ),
    (
        "Premium Restaurant Lunch Experience",
        "Add a premium restaurant lunch during the midday break.",
        "Starting from KES 8,500 per person. Venue, menu and final "
        "price are confirmed before booking.",
        8500,
        "Per Person",
    ),
    (
        "Professional Videography Package",
        "Add professional video coverage of the day.",
        "Starting from KES 25,000 per booking. Scope and deliverables "
        "are confirmed before booking.",
        25000,
        "Per Booking",
    ),
    (
        "Nairobi Safari Walk Extension",
        "Extend the day with a visit to Nairobi Safari Walk.",
        "Starting from KES 5,000 per person. Availability and any "
        "separately charged admission must be confirmed.",
        5000,
        "Per Person",
    ),
    (
        "Private Concierge Host",
        "Add a private concierge host for additional guest assistance "
        "and coordination.",
        "Starting from KES 20,000 per booking, subject to scope "
        "and confirmation.",
        20000,
        "Per Booking",
    ),
    (
        "Airport Transfer Extension",
        "Add an airport transfer to the planned Nairobi arrangements.",
        "Starting from KES 8,500 per booking, subject to pickup "
        "details and confirmation.",
        8500,
        "Per Booking",
    ),
]


# ================================================================
# PACKING ITEMS
# ================================================================

PACKING_DATA = [
    (
        "Comfortable walking shoes",
        "Closed, comfortable shoes for moving around visitor facilities.",
        "Clothing",
        "footprints",
        True,
        False,
    ),
    (
        "Light layers",
        "A light jacket or layer for the early morning departure.",
        "Clothing",
        "shirt",
        True,
        False,
    ),
    (
        "Sun protection",
        "Bring sunscreen, sunglasses and a hat for outdoor portions.",
        "Personal Care",
        "sun",
        True,
        False,
    ),
    (
        "Camera or phone",
        "Bring a camera or phone. Follow venue and guide instructions "
        "on photography.",
        "Photography",
        "camera",
        False,
        False,
    ),
    (
        "Personal medication",
        "Carry any personal medication you may need during the day.",
        "Personal Care",
        "pill",
        False,
        False,
    ),
]


# ================================================================
# SAFETY RULES
# ================================================================

SAFETY_DATA = [
    (
        "Follow wildlife viewing instructions",
        "Remain inside the vehicle during the game drive unless the "
        "guide identifies an approved area to exit. Never approach, "
        "feed or attempt to touch wildlife.",
        "Wildlife",
        "High",
        "shield-check",
    ),
    (
        "Follow the Experience Leader",
        "Follow instructions from the Experience Leader, driver, "
        "park personnel and attraction staff throughout the day.",
        "General",
        "High",
        "user-check",
    ),
    (
        "Respect conservation facilities",
        "Observe visitor rules at conservation facilities. Do not "
        "feed or handle animals unless venue staff explicitly permit it.",
        "Conservation",
        "High",
        "heart",
    ),
    (
        "Use seat belts",
        "Wear a seat belt whenever travelling in the vehicle.",
        "Transport",
        "High",
        "car",
    ),
    (
        "Stay hydrated and protected from the sun",
        "Drink water regularly and use suitable sun protection "
        "during outdoor portions.",
        "Health",
        "Medium",
        "sun",
    ),
]


# ================================================================
# REQUIREMENTS
# ================================================================

REQUIREMENTS_DATA = [
    (
        "Advance reservations",
        "Conservation visits are subject to advance reservation "
        "requirements, venue operating arrangements and availability.",
        "Booking",
        True,
        "calendar",
    ),
    (
        "Valid identification",
        "Carry identification or documentation required by the "
        "relevant attractions for admission and guest-category pricing.",
        "Documentation",
        True,
        "id-card",
    ),
    (
        "Share dietary and accessibility needs",
        "Inform TUR of relevant dietary, mobility or accessibility "
        "needs before the experience so arrangements can be discussed.",
        "Guest Information",
        False,
        "info",
    ),
    (
        "Confirm pickup details",
        "Provide the hotel or agreed pickup location and a reachable "
        "contact number before the experience date.",
        "Logistics",
        True,
        "map-pin",
    ),
]


# ================================================================
# FAQs
# ================================================================

FAQS_DATA = [
    (
        "Are attraction entrance fees included in the package price?",
        "No. Nairobi National Park, David Sheldrick Wildlife Trust, "
        "Giraffe Centre and optional Nairobi Safari Walk admission "
        "fees are paid separately at prevailing rates for each "
        "guest category.",
        "Pricing",
    ),
    (
        "Is lunch included?",
        "No. Lunch is not included in the base package. A premium "
        "restaurant lunch may be added at an additional cost, "
        "starting from KES 8,500 per person, subject to confirmation.",
        "Meals",
    ),
    (
        "Will we definitely see the Big Five?",
        "No. Wildlife sightings are never guaranteed. Sightings "
        "depend on animal movement and natural conditions.",
        "Wildlife",
    ),
    (
        "Is the Nairobi Safari Walk part of the standard itinerary?",
        "It is an optional paid extension, not part of the base "
        "package. It must be selected and confirmed separately.",
        "Itinerary",
    ),
    (
        "Do the conservation visits need advance booking?",
        "Yes. Conservation visits are subject to advance reservation "
        "requirements, venue operating arrangements and availability. "
        "TUR will coordinate the requested visits and confirm "
        "what is available.",
        "Booking",
    ),
    (
        "Can the itinerary or timings change?",
        "The listed times are planned timings. Traffic, park "
        "conditions and venue operations may affect the sequence "
        "or return time. TUR will coordinate reasonable operational "
        "adjustments.",
        "Itinerary",
    ),
    (
        "Are tips compulsory?",
        "No. Tips and gratuities are optional and entirely at "
        "the guest's discretion.",
        "Pricing",
    ),
]


# ================================================================
# PRICING
# Per-person KES rates, as agreed.
# ================================================================

PRICING_DATA = [
    # Minimum people, maximum people, tier, price
    (1, 1, "Explorer", 29500),
    (1, 1, "Signature", 35000),
    (1, 1, "Luxury", 49500),

    (2, 3, "Explorer", 24500),
    (2, 3, "Signature", 28500),
    (2, 3, "Luxury", 42500),

    (4, None, "Explorer", 20500),
    (4, None, "Signature", 23500),
    (4, None, "Luxury", 36500),
]


# ================================================================
# HELPERS
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
    """
    Creates child records using the model's experience_id foreign key.
    """
    db.session.add_all([
        model(experience_id=experience_id, **record)
        for record in records
    ])


# ================================================================
# MAIN POPULATION
# ================================================================

def populate(apply_changes=False):

    app = create_app()

    with app.app_context():

        try:

            # ----------------------------------------------------
            # DUPLICATE PROTECTION
            # ----------------------------------------------------

            existing = Experience.query.filter(
                or_(
                    Experience.experience_code == EXPERIENCE_CODE,
                    Experience.slug == EXPERIENCE_SLUG,
                )
            ).first()

            if existing:
                raise RuntimeError(
                    "An experience already uses this code or slug. "
                    f"Existing ID: {existing.id}; "
                    f"Code: {existing.experience_code}; "
                    f"Slug: {existing.slug}. "
                    "No changes have been made."
                )

            # ----------------------------------------------------
            # VALIDATE REUSABLE CMS RECORDS
            # ----------------------------------------------------

            category = require_active(
                ExperienceCategory, CATEGORY_ID, "Experience category"
            )

            destination = require_active(
                Destination, DESTINATION_ID, "Destination"
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

            conservation = require_active(
                ConservationStory,
                CONSERVATION_STORY_ID,
                "Conservation story",
            )

            tags = [
                require_active(ExperienceTag, record_id, "Experience tag")
                for record_id in TAG_IDS
            ]

            moments = [
                require_active(
                    SignatureMoment, record_id, "Signature moment"
                )
                for record_id in SIGNATURE_MOMENT_IDS
            ]

            photography_spots = [
                require_active(
                    PhotographySpot, record_id, "Photography spot"
                )
                for record_id in PHOTOGRAPHY_SPOT_IDS
            ]

            wildlife_species = {}

            for item in WILDLIFE_DATA:
                species_id = item["species_id"]
                wildlife_species[species_id] = require_active(
                    WildlifeSpecies,
                    species_id,
                    "Wildlife species",
                )

            # ----------------------------------------------------
            # CREATE MAIN EXPERIENCE
            # ----------------------------------------------------

            experience = Experience(
                experience_code=EXPERIENCE_CODE,
                title="Nairobi Wildlife Combo Package",
                slug=EXPERIENCE_SLUG,

                short_description=(
                    "A privately coordinated Nairobi wildlife and "
                    "conservation day combining a sunrise game drive "
                    "with meaningful elephant and giraffe "
                    "conservation visits."
                ),

                description=(
                    "Discover Nairobi's wildlife and conservation "
                    "experiences in one privately coordinated day. "
                    "Begin with a sunrise game drive in Nairobi "
                    "National Park, then continue to the David "
                    "Sheldrick Wildlife Trust and the Giraffe Centre. "
                    "A professional driver and private transport "
                    "connect the planned visits, while your "
                    "Experience Leader provides coordination, "
                    "wildlife interpretation and conservation "
                    "storytelling.\\n\\n"
                    "The itinerary is subject to park and venue "
                    "operating arrangements, advance reservations, "
                    "traffic and availability. Wildlife sightings "
                    "are not guaranteed. All attraction and park "
                    "entrance fees are separate and payable at "
                    "prevailing rates according to each guest's "
                    "category. Lunch and the Nairobi Safari Walk "
                    "extension are optional paid additions and "
                    "are not included in the base package."
                ),

                duration="Full day (approximately 12 hours)",
                meeting_point=(
                    "Hotel or agreed accommodation pickup in Nairobi"
                ),
                location="Nairobi, Kenya",

                price_from=20500,
                currency="KES",

                minimum_people=1,
                maximum_people=None,
                minimum_age=None,
                difficulty="Easy",

                # Deliberately blank until the user uploads images.
                featured_image="",
                banner_image=None,

                meta_title=(
                    "Nairobi Wildlife Combo Package | The Uncharted Route"
                ),
                meta_description=(
                    "A private Nairobi wildlife day with a sunrise "
                    "game drive, elephant conservation visit and "
                    "Giraffe Centre experience. Attraction fees "
                    "are separate."
                ),

                featured=True,
                show_on_homepage=False,
                active=True,
                display_order=2,

                category_id=category.id,
                destination_id=destination.id,
                cancellation_policy_id=policy.id,
                accessibility_profile_id=accessibility.id,
                conservation_story_id=conservation.id,
            )

            db.session.add(experience)
            db.session.flush()

            experience_id = experience.id

            # ----------------------------------------------------
            # REUSABLE CMS ASSOCIATIONS
            # ----------------------------------------------------

            for tag in tags:
                experience.tags.append(tag)
            for moment in moments:
                experience.signature_moments.append(moment)

            # ----------------------------------------------------
            # ITINERARY
            # ----------------------------------------------------

            add_children(
                ExperienceItinerary,
                experience_id,
                [
                    {
                        "day_number": 1,
                        "title": item["title"],
                        "activity_time": item["time"],
                        "description": item["description"],
                        "display_order": order,
                    }
                    for order, item in enumerate(ITINERARY_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # INCLUSIONS
            # ----------------------------------------------------

            add_children(
                ExperienceInclusion,
                experience_id,
                [
                    {
                        "title": title,
                        "description": description,
                        "icon": icon,
                        "display_order": order,
                        "active": True,
                    }
                    for order, (title, description, icon)
                    in enumerate(INCLUSIONS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # EXCLUSIONS
            # ----------------------------------------------------

            add_children(
                ExperienceExclusion,
                experience_id,
                [
                    {
                        "title": title,
                        "description": description,
                        "icon": icon,
                        "display_order": order,
                        "active": True,
                    }
                    for order, (title, description, icon)
                    in enumerate(EXCLUSIONS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # HIGHLIGHTS
            # ----------------------------------------------------

            add_children(
                ExperienceHighlight,
                experience_id,
                [
                    {
                        "title": title,
                        "description": description,
                        "icon": icon,
                        "highlight_type": highlight_type,
                        "display_order": order,
                        "featured": order == 1,
                        "active": True,
                    }
                    for order, (
                        title,
                        description,
                        icon,
                        highlight_type,
                    ) in enumerate(HIGHLIGHTS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # PRICING
            # ----------------------------------------------------

            add_children(
                ExperiencePricing,
                experience_id,
                [
                    {
                        "experience_level": tier,
                        "minimum_people": minimum,
                        "maximum_people": maximum,
                        "price": price,
                        "currency": "KES",
                        "notes": (
                            "Per person. Attraction and park entrance "
                            "fees are excluded and paid separately."
                        ),
                        "display_order": (
                            {"Explorer": 1, "Signature": 2, "Luxury": 3}[tier]
                            + {1: 0, 2: 3, 4: 6}[minimum]
                        ),
                        "active": True,
                    }
                    for minimum, maximum, tier, price in PRICING_DATA
                ],
            )

            # ----------------------------------------------------
            # OPTIONAL ADD-ONS
            # ----------------------------------------------------

            add_children(
                ExperienceAddon,
                experience_id,
                [
                    {
                        "name": name,
                        "short_description": short_description,
                        "description": description,
                        "price": price,
                        "currency": "KES",
                        "pricing_type": pricing_type,
                        "optional": True,

                        # These are indicative starting prices.
                        # Keep online purchasing disabled until
                        # availability and final prices are confirmed.
                        "available_online": False,

                        "display_order": order,
                        "active": True,
                    }
                    for order, (
                        name,
                        short_description,
                        description,
                        price,
                        pricing_type,
                    ) in enumerate(ADDONS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # PACKING ITEMS
            # ----------------------------------------------------

            add_children(
                ExperiencePackingItem,
                experience_id,
                [
                    {
                        "name": name,
                        "description": description,
                        "category": category_name,
                        "icon": icon,
                        "recommended": recommended,
                        "required": required,
                        "display_order": order,
                        "active": True,
                    }
                    for order, (
                        name,
                        description,
                        category_name,
                        icon,
                        recommended,
                        required,
                    ) in enumerate(PACKING_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # SAFETY RULES
            # ----------------------------------------------------

            add_children(
                ExperienceSafetyRule,
                experience_id,
                [
                    {
                        "title": title,
                        "description": description,
                        "category": category_name,
                        "priority": priority,
                        "icon": icon,
                        "display_order": order,
                        "active": True,
                    }
                    for order, (
                        title,
                        description,
                        category_name,
                        priority,
                        icon,
                    ) in enumerate(SAFETY_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # REQUIREMENTS
            # ----------------------------------------------------

            add_children(
                ExperienceRequirement,
                experience_id,
                [
                    {
                        "title": title,
                        "description": description,
                        "category": category_name,
                        "mandatory": mandatory,
                        "icon": icon,
                        "display_order": order,
                        "active": True,
                    }
                    for order, (
                        title,
                        description,
                        category_name,
                        mandatory,
                        icon,
                    ) in enumerate(REQUIREMENTS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # FAQs
            # ----------------------------------------------------

            add_children(
                ExperienceFAQ,
                experience_id,
                [
                    {
                        "question": question,
                        "answer": answer,
                        "category": category_name,
                        "display_order": order,
                        "featured": order <= 3,
                        "active": True,
                    }
                    for order, (
                        question,
                        answer,
                        category_name,
                    ) in enumerate(FAQS_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # WILDLIFE ASSOCIATIONS
            # ----------------------------------------------------

            add_children(
                ExperienceWildlife,
                experience_id,
                [
                    {
                        "species_id": item["species_id"],
                        "sighting_probability": item["probability"],
                        "best_season": item["season"],
                        "best_time_of_day": item["time"],
                        "guide_notes": item["notes"],
                        "photography_notes": (
                            "Photograph only from approved areas and "
                            "follow guide and venue instructions."
                        ),
                        "featured": item["species_id"] in (1, 2, 3),
                        "display_order": order,
                        "active": True,
                    }
                    for order, item in enumerate(WILDLIFE_DATA, 1)
                ],
            )

            # ----------------------------------------------------
            # PHOTOGRAPHY SPOT ASSOCIATIONS
            # ----------------------------------------------------

            add_children(
                ExperiencePhotography,
                experience_id,
                [
                    {
                        "photography_spot_id": spot.id,
                        "stop_order": order,
                        "featured": order == 1,
                        "active": True,
                        "notes": (
                            "Photography during the game drive. "
                            "Sightings and access depend on park conditions."
                            if spot.id == 2
                            else
                            "Photography at the Giraffe Centre only in "
                            "areas and under conditions permitted by "
                            "venue staff."
                        ),
                    }
                    for order, spot in enumerate(photography_spots, 1)
                ],
            )

            # ----------------------------------------------------
            # FLUSH AND VERIFY COUNTS
            # ----------------------------------------------------

            db.session.flush()

            counts = {
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

            print()
            print("=" * 65)
            print("NAIROBI WILDLIFE COMBO PACKAGE")
            print("POPULATION SUMMARY")
            print("=" * 65)

            print(f"Experience ID:       {experience_id}")
            print(f"Code:                {EXPERIENCE_CODE}")
            print(f"Slug:                {EXPERIENCE_SLUG}")
            print(f"Title:               {experience.title}")
            print(f"Category:            {category.name} (ID {category.id})")
            print(f"Destination:         {destination.name} (ID {destination.id})")
            print(f"Cancellation policy: ID {policy.id}")
            print(f"Accessibility:       ID {accessibility.id}")
            print(f"Conservation story:  ID {conservation.id}")
            print(f"Starting price:      KES {experience.price_from:,.0f}")

            print()
            print("-" * 65)
            print("COMPONENT COUNTS")
            print("-" * 65)

            for label, count in counts.items():
                print(f"{label:<28} {count}")

            print()
            print("Media records created: 0")
            print("Schedule records created: 0")
            print("Reusable CMS records created: 0")
            print("Existing experiences modified: 0")

            if apply_changes:
                db.session.commit()

                print()
                print("=" * 65)
                print("SUCCESS: EXPERIENCE SAVED")
                print("=" * 65)

                saved = Experience.query.filter_by(
                    experience_code=EXPERIENCE_CODE
                ).one()

                print(f"Saved experience ID: {saved.id}")
                print(f"Saved title:         {saved.title}")
                print(f"Saved code:          {saved.experience_code}")

            else:
                db.session.rollback()

                print()
                print("=" * 65)
                print("DRY RUN COMPLETE")
                print("=" * 65)
                print("No database changes were committed.")
                print("Review the component counts before applying.")
                print()
                print(
                    "To save the experience, run this script with --apply."
                )

        except Exception as error:
            db.session.rollback()

            print()
            print("=" * 65)
            print("POPULATION FAILED — TRANSACTION ROLLED BACK")
            print("=" * 65)
            print(str(error))

            raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the population to the database.",
    )

    arguments = parser.parse_args()

    populate(apply_changes=arguments.apply)


