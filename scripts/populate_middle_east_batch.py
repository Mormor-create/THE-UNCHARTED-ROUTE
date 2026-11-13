"""
===============================================================================
THE UNCHARTED ROUTE
BATCH 5 — MIDDLE EAST EXPERIENCE POPULATION
===============================================================================

Destinations:
    Dubai  ID 29 — ACTIVE
    Egypt  ID 35 — ACTIVE

This batch creates complete, sellable Experience records with reusable CMS
associations and all approved child content.

IMPORTANT:
    - Existing experiences are NEVER modified.
    - Existing CMS records are NEVER duplicated.
    - No media associations are created.
    - No schedules are created.
    - No bookings are created.
    - Existing destination activation states are NOT changed.
    - Experiences are created active.
    - DEFAULT: dry run.
    - APPLY: python scripts/populate_middle_east_batch.py --apply

The batch is transactional. Any error rolls the entire batch back.

Experience scope:
    Dubai:
        - Old Dubai — Al Fahidi, Creek & Souks
        - Dubai Modern Icons — Burj Khalifa, Downtown & Skyline
        - Dubai Desert Dunes — Landscapes, Sunset & Bedouin Culture

    Egypt:
        - Giza Plateau — Pyramids, Sphinx & Ancient Egypt
        - Islamic Cairo — Historic Mosques, Al-Azhar & Khan el-Khalili
        - Luxor — Temples, Nile & Ancient Thebes

IMPORTANT:
    - No Kenya-specific wildlife species are attached.
    - No Kenya-specific conservation stories are attached.
    - No wildlife associations are created unless an appropriate reusable
      non-Kenya wildlife CMS record exists.
===============================================================================
"""

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
    ConservationStory,
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
)


# =============================================================================
# CLI
# =============================================================================

parser = argparse.ArgumentParser(
    description="Populate Batch 5 — Middle East experiences."
)

parser.add_argument(
    "--apply",
    action="store_true",
    help="Commit the batch instead of rolling it back as a dry run.",
)

args = parser.parse_args()


# =============================================================================
# REUSABLE CMS RECORDS
# =============================================================================

CATEGORY_CULTURE = 3
CATEGORY_ADVENTURE = 2
CATEGORY_COASTAL = 4
CATEGORY_LUXURY = 5
CATEGORY_CITY = 3

CANCELLATION_STANDARD = 2
CANCELLATION_HIGH_COMMITMENT = 3

ACCESS_EASY = 5
ACCESS_MODERATE = 3
ACCESS_ADVENTURE = 6


# Existing ExperienceTag IDs
TAG_WILDLIFE = 1
TAG_CONSERVATION = 2
TAG_PHOTOGRAPHY = 4
TAG_CULTURE = 12
TAG_COASTAL = 13
TAG_HIKING = 15
TAG_NATURE = 17
TAG_HISTORICAL = 19
TAG_ARCHITECTURE = 20
TAG_ISLAND = 25
TAG_MARINE = 26
TAG_CITY = 27
TAG_MARKETS = 28
TAG_PRIVATE = 30


# Existing SignatureMoment IDs
MOMENT_SUNRISE = 1
MOMENT_WILDLIFE = 2
MOMENT_HIDDEN_NATURE = 6
MOMENT_VIEWPOINT = 7
MOMENT_OUTDOOR = 8
MOMENT_TRAIL = 9
MOMENT_LANDSCAPES = 11
MOMENT_HERITAGE = 12
MOMENT_CRAFT = 13
MOMENT_CULTURAL = 14
MOMENT_HISTORY = 15
MOMENT_ARCHITECTURE = 16
MOMENT_CITY = 26
MOMENT_MARKET = 27
MOMENT_SKYLINE = 28
MOMENT_RELAXATION = 29
MOMENT_EXTRAORDINARY = 30


# We deliberately do not attach Kenya-specific conservation stories
# to Middle Eastern experiences.
CONSERVATION_NONE = None


# =============================================================================
# HELPER FACTORIES
# =============================================================================

def pricing(one, two_three, four_plus, notes, currency="USD"):
    def price_value(value):
        if isinstance(value, (tuple, list)):
            return value[0]
        return value

    return [
        {
            "minimum_people": 1,
            "maximum_people": 1,
            "experience_level": "Explorer",
            "price": price_value(one),
            "currency": currency,
            "notes": notes,
        },
        {
            "minimum_people": 2,
            "maximum_people": 3,
            "experience_level": "Signature",
            "price": price_value(two_three),
            "currency": currency,
            "notes": notes,
        },
        {
            "minimum_people": 4,
            "maximum_people": None,
            "experience_level": "Luxury",
            "price": price_value(four_plus),
            "currency": currency,
            "notes": notes,
        },
    ]


def itinerary(title, timing, description):
    return {
        "title": title,
        "timing": timing,
        "description": description,
    }


def inc(title, description, icon):
    return {
        "title": title,
        "description": description,
        "icon": icon,
    }


def exc(title, description, icon):
    return {
        "title": title,
        "description": description,
        "icon": icon,
    }


def highlight(title, description, icon, category):
    return {
        "title": title,
        "description": description,
        "icon": icon,
        "category": category,
    }


def addon(name, short_description, description, price, pricing_type):
    return {
        "name": name,
        "short_description": short_description,
        "description": description,
        "price": price,
        "currency": "USD",
        "pricing_type": pricing_type,
        "optional": True,
        "available_online": False,
    }


def packing(
    name,
    description,
    category,
    icon,
    recommended=True,
    required=False,
):
    return {
        "name": name,
        "description": description,
        "category": category,
        "icon": icon,
        "recommended": recommended,
        "required": required,
    }


def safety(title, description, category, icon):
    return {
        "title": title,
        "description": description,
        "category": category,
        "icon": icon,
    }


def requirement(title, description, category, required, icon):
    return {
        "title": title,
        "description": description,
        "category": category,
        "required": required,
        "icon": icon,
    }


def faq(question, answer, category, featured=False):
    return {
        "question": question,
        "answer": answer,
        "category": category,
        "featured": featured,
    }


# =============================================================================
# EXPERIENCE DATA
# =============================================================================

EXPERIENCES = [

    # =========================================================================
    # DUBAI — ID 29
    # =========================================================================

    {
        "code": "ME-DXB-001",
        "slug": "old-dubai-al-fahidi-creek-souks",
        "title": "Old Dubai — Al Fahidi, Creek & Souks",
        "destination_id": 29,
        "category_id": CATEGORY_CULTURE,

        "short_description": (
            "A heritage-focused Dubai journey through Al Fahidi, Dubai Creek "
            "and the traditional souks, revealing the city's life before the "
            "modern skyline."
        ),

        "description": (
            "Step away from Dubai's futuristic skyline and discover the city "
            "through its older neighbourhoods, creekside traditions and "
            "historic trading culture. Explore the Al Fahidi area, experience "
            "the atmosphere of Dubai Creek and continue through selected "
            "traditional souks with a locally informed guide. The experience "
            "connects architecture, trade, food, craftsmanship and the "
            "cultural foundations of modern Dubai."
        ),

        "duration": "Half Day",

        "meeting_point": (
            "Confirmed Dubai hotel or agreed central meeting point."
        ),

        "location": "Old Dubai, Dubai, United Arab Emirates",

        "price_from": 95,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 1,

        "meta_title": (
            "Old Dubai Al Fahidi & Souks Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Discover Old Dubai through Al Fahidi, Dubai Creek, traditional "
            "souks, architecture and the city's trading heritage."
        ),

        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_CULTURE,
            TAG_HISTORICAL,
            TAG_ARCHITECTURE,
            TAG_MARKETS,
            TAG_PRIVATE,
        ],

        "moments": [
            MOMENT_HISTORY,
            MOMENT_HERITAGE,
            MOMENT_ARCHITECTURE,
            MOMENT_MARKET,
        ],

        "pricing_rows": pricing(
            (165, 165, 165),
            (125, 125, 125),
            (105, 105, 105),
            (
                "Indicative TUR selling price per person in USD. "
                "Any abra, museum or attraction admission is subject to "
                "current official tariffs."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Heritage Welcome",
                "Morning / Afternoon",
                (
                    "Meet your guide and receive an introduction to Dubai's "
                    "development from a regional trading settlement into a "
                    "global city."
                ),
            ),
            itinerary(
                "Al Fahidi Heritage Quarter",
                "Main Activity",
                (
                    "Explore selected historic lanes, courtyard architecture "
                    "and cultural spaces while learning about traditional "
                    "Emirati urban life."
                ),
            ),
            itinerary(
                "Dubai Creek",
                "Later Activity",
                (
                    "Continue toward the Creek and experience the historic "
                    "waterway that connected Dubai's communities and trading "
                    "routes."
                ),
            ),
            itinerary(
                "Souks & Local Flavours",
                "Final Hour",
                (
                    "Explore selected souks and conclude with time for "
                    "shopping, traditional refreshments or an optional "
                    "local tasting."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Experience Coordination",
                "TUR coordination of the agreed Old Dubai itinerary.",
                "route",
            ),
            inc(
                "Local Guide Support",
                "Locally informed interpretation throughout the experience.",
                "user",
            ),
            inc(
                "Heritage Route",
                "Curated route through selected Old Dubai cultural areas.",
                "landmark",
            ),
            inc(
                "Photography Stops",
                "Time for respectful architecture, creek and market photography.",
                "camera",
            ),
        ],

        "exclusions": [
            exc(
                "Attraction Admissions",
                "Museum and attraction entrance fees are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Shopping",
                "Souk purchases and personal expenses are excluded.",
                "shopping-bag",
            ),
        ],

        "highlights": [
            highlight(
                "Al Fahidi",
                "Explore one of Dubai's most atmospheric historic neighbourhoods.",
                "landmark",
                "Heritage",
            ),
            highlight(
                "Dubai Creek",
                "Discover the waterway at the heart of Dubai's historic trading identity.",
                "anchor",
                "Culture",
            ),
            highlight(
                "Traditional Souks",
                "Experience the colour, aromas and commerce of Dubai's traditional markets.",
                "shopping-bag",
                "Markets",
            ),
            highlight(
                "Old & New Dubai",
                "Understand how a historic trading city evolved into today's global metropolis.",
                "city",
                "City",
            ),
        ],

        "addons": [
            addon(
                "Traditional Emirati Tasting",
                "Add a curated tasting of selected local flavours.",
                (
                    "TUR-arranged tasting at a suitable venue, subject to "
                    "availability and dietary requirements."
                ),
                45,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Wear comfortable shoes for walking through historic streets and markets.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat for outdoor sections.",
                "Weather",
                "sun",
            ),
            packing(
                "Light Layer",
                "Indoor venues and transport may be strongly air-conditioned.",
                "Clothing",
                "wind",
            ),
            packing(
                "Water",
                "Carry drinking water, particularly during warmer months.",
                "Hydration",
                "droplet",
            ),
        ],

        "safety_rows": [
            safety(
                "Heat & Sun",
                "Outdoor walking can be hot, especially during warmer months.",
                "Weather",
                "sun",
            ),
            safety(
                "Market Awareness",
                "Keep valuables secure and remain aware in busy market areas.",
                "Urban",
                "lock",
            ),
            safety(
                "Respect Cultural Spaces",
                "Follow photography, dress and conduct guidance at heritage and religious sites.",
                "Culture",
                "shield",
            ),
        ],

        "requirements": [
            requirement(
                "Respect Cultural Guidelines",
                "Guests must respect local customs, dress expectations and photography restrictions.",
                "Culture",
                True,
                "heart",
            ),
            requirement(
                "Walking Comfort",
                "Guests should be comfortable with moderate walking through historic areas.",
                "Mobility",
                True,
                "footprints",
            ),
        ],

        "faqs": [
            faq(
                "Is Old Dubai very different from modern Dubai?",
                (
                    "Yes. The experience focuses on historic neighbourhoods, "
                    "traditional commerce and the Creek rather than the modern skyline."
                ),
                "Culture",
                True,
            ),
            faq(
                "Can we ride an abra?",
                (
                    "Where appropriate and operationally available, an abra "
                    "crossing can be included or arranged as an optional component."
                ),
                "Logistics",
                False,
            ),
            faq(
                "Can we shop in the souks?",
                "Yes. Guests have time for shopping, although purchases are personal expenses.",
                "Markets",
                False,
            ),
            faq(
                "Is this suitable for families?",
                "Yes. The experience is suitable for families and the minimum age is six.",
                "Family",
                False,
            ),
        ],

        "wildlife_rows": [],
    },


    {
        "code": "ME-DXB-002",
        "slug": "dubai-modern-icons-burj-khalifa-downtown-skyline",
        "title": "Dubai Modern Icons — Burj Khalifa, Downtown & Skyline",
        "destination_id": 29,
        "category_id": CATEGORY_CITY,

        "short_description": (
            "A polished Dubai city experience combining Downtown Dubai, "
            "Burj Khalifa views, architectural landmarks and the energy of "
            "the modern metropolis."
        ),

        "description": (
            "Experience Dubai through the architecture and public spaces that "
            "have come to define its global identity. Explore Downtown Dubai, "
            "the Burj Khalifa district and selected skyline viewpoints while "
            "learning how Dubai's ambitions shaped its contemporary urban form. "
            "The experience is designed around architecture, photography, "
            "design and the city's extraordinary contrast between scale, "
            "luxury and desert environment."
        ),

        "duration": "Half Day",

        "meeting_point": (
            "Confirmed Dubai hotel or agreed Downtown Dubai meeting point."
        ),

        "location": "Downtown Dubai, Dubai, United Arab Emirates",

        "price_from": 125,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 2,

        "meta_title": (
            "Dubai Modern Icons & Burj Khalifa Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Explore Downtown Dubai, Burj Khalifa and the city's iconic "
            "architecture through a private urban experience."
        ),

        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_CITY,
            TAG_ARCHITECTURE,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],

        "moments": [
            MOMENT_SKYLINE,
            MOMENT_ARCHITECTURE,
            MOMENT_CITY,
            MOMENT_EXTRAORDINARY,
        ],

        "pricing_rows": pricing(
            (195, 195, 195),
            (155, 155, 155),
            (125, 125, 125),
            (
                "Indicative TUR selling price per person in USD. "
                "Burj Khalifa observation deck admission is excluded "
                "unless specifically included in the final quotation."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Downtown Welcome",
                "Morning / Afternoon",
                (
                    "Meet your guide and begin with an overview of Dubai's "
                    "rapid urban transformation and Downtown district."
                ),
            ),
            itinerary(
                "Burj Khalifa District",
                "Main Activity",
                (
                    "Explore the Burj Khalifa precinct, surrounding public "
                    "spaces and key architectural viewpoints."
                ),
            ),
            itinerary(
                "Dubai Architecture Route",
                "Later Activity",
                (
                    "Continue through selected Downtown landmarks and "
                    "architecture-focused stops with time for photography."
                ),
            ),
            itinerary(
                "Skyline Farewell",
                "Final Hour",
                (
                    "Conclude at an agreed viewpoint or waterfront setting "
                    "for a final Dubai skyline experience."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Vehicle & Driver",
                "Dedicated transport for the agreed city route.",
                "car",
            ),
            inc(
                "City Guide Support",
                "Local guide support and architectural interpretation.",
                "user",
            ),
            inc(
                "Curated Skyline Route",
                "Planned route connecting key Downtown viewpoints.",
                "route",
            ),
            inc(
                "Photography Stops",
                "Time for skyline and architectural photography.",
                "camera",
            ),
        ],

        "exclusions": [
            exc(
                "Burj Khalifa Admission",
                "Observation deck tickets are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Expenses",
                "Shopping and personal purchases are excluded.",
                "wallet",
            ),
        ],

        "highlights": [
            highlight(
                "Burj Khalifa",
                "Experience the district surrounding the world's defining skyscraper.",
                "landmark",
                "Architecture",
            ),
            highlight(
                "Dubai Skyline",
                "Capture dramatic views across one of the world's most recognisable modern skylines.",
                "camera",
                "Scenic",
            ),
            highlight(
                "Downtown Dubai",
                "Explore the public spaces and architectural language of modern Dubai.",
                "city",
                "City",
            ),
            highlight(
                "Modern Ambition",
                "Understand the urban vision behind Dubai's transformation.",
                "building",
                "Culture",
            ),
        ],

        "addons": [
            addon(
                "Burj Khalifa Observation Deck",
                "Add official observation deck admission.",
                (
                    "Official admission ticket arranged according to the "
                    "selected time slot and current availability."
                ),
                75,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "The experience includes walking through large urban spaces.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen and sunglasses for outdoor viewpoints.",
                "Weather",
                "sun",
            ),
            packing(
                "Light Layer",
                "Indoor venues can be strongly air-conditioned.",
                "Clothing",
                "wind",
            ),
            packing(
                "Camera",
                "A camera or phone is recommended for architecture and skyline photography.",
                "Photography",
                "camera",
            ),
        ],

        "safety_rows": [
            safety(
                "Heat Exposure",
                "Outdoor sections can become hot; follow hydration and shade guidance.",
                "Weather",
                "sun",
            ),
            safety(
                "Crowded Areas",
                "Stay aware of personal belongings in busy Downtown locations.",
                "Urban",
                "lock",
            ),
            safety(
                "Observation Deck Rules",
                "Follow all official attraction rules and instructions when visiting observation areas.",
                "Attraction",
                "shield",
            ),
        ],

        "requirements": [
            requirement(
                "Comfortable Walking",
                "Guests should be comfortable walking through Downtown's large public spaces.",
                "Mobility",
                True,
                "footprints",
            ),
            requirement(
                "Attraction Timing",
                "Observation deck access depends on official ticket availability and selected time slots.",
                "Booking",
                False,
                "clock",
            ),
        ],

        "faqs": [
            faq(
                "Does the experience include Burj Khalifa tickets?",
                (
                    "The base experience does not include observation deck admission. "
                    "It can be added as an optional upgrade."
                ),
                "Booking",
                True,
            ),
            faq(
                "Can we visit at sunset?",
                "Yes, subject to attraction ticket availability and the final route timing.",
                "Timing",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Yes. The city experience is family-friendly and the minimum age is six.",
                "Family",
                False,
            ),
            faq(
                "Can this be made more luxurious?",
                "Yes. Private dining, premium observation timings and other upgrades can be incorporated into a bespoke quotation.",
                "Luxury",
                False,
            ),
        ],

        "wildlife_rows": [],
    },


    {
        "code": "ME-DXB-003",
        "slug": "dubai-desert-dunes-sunset-bedouin-culture",
        "title": "Dubai Desert Dunes — Landscapes, Sunset & Bedouin Culture",
        "destination_id": 29,
        "category_id": CATEGORY_ADVENTURE,

        "short_description": (
            "A private desert experience combining dramatic dunes, sunset "
            "landscapes and a respectful introduction to Bedouin-inspired "
            "desert culture."
        ),

        "description": (
            "Leave Dubai's towers behind and enter the desert landscape through "
            "a carefully paced private experience. The route focuses on dune "
            "landscapes, sunset photography and cultural interpretation rather "
            "than treating the desert as a theme-park backdrop. Depending on "
            "the selected operating package, guests may add dune driving, "
            "sandboarding or a traditional-style desert dinner."
        ),

        "duration": "Half Day / Evening",

        "meeting_point": (
            "Confirmed Dubai hotel pickup or agreed central meeting point."
        ),

        "location": "Dubai Desert Conservation Reserve area, Dubai, United Arab Emirates",

        "price_from": 165,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Moderate",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 3,

        "meta_title": (
            "Dubai Desert Sunset & Dunes Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Experience Dubai's desert landscapes through dunes, sunset, "
            "photography and culturally respectful desert interpretation."
        ),

        "cancellation_policy_id": CANCELLATION_HIGH_COMMITMENT,
        "accessibility_profile_id": ACCESS_ADVENTURE,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_NATURE,
            TAG_PHOTOGRAPHY,
            TAG_CITY,
            TAG_PRIVATE,
            TAG_CULTURE,
        ],

        "moments": [
            MOMENT_SUNRISE,
            MOMENT_LANDSCAPES,
            MOMENT_OUTDOOR,
            MOMENT_EXTRAORDINARY,
        ],

        "pricing_rows": pricing(
            (245, 245, 245),
            (195, 195, 195),
            (165, 165, 165),
            (
                "Indicative TUR selling price per person in USD. "
                "Desert access, dune activities and dining components vary "
                "by selected operator and final package."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Dubai Departure",
                "Afternoon",
                (
                    "Meet your driver and depart Dubai for the desert with "
                    "an introduction to the landscape and evening plan."
                ),
            ),
            itinerary(
                "Desert Landscapes",
                "Late Afternoon",
                (
                    "Enter the desert and explore selected dunes and scenic "
                    "locations according to the agreed operating route."
                ),
            ),
            itinerary(
                "Sunset Experience",
                "Sunset",
                (
                    "Pause in a carefully selected desert setting for "
                    "photography and quiet appreciation of the landscape."
                ),
            ),
            itinerary(
                "Desert Culture & Return",
                "Evening",
                (
                    "Continue with the selected cultural or dining component "
                    "before returning to Dubai."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Desert Transport",
                "Dedicated transport from Dubai to the agreed desert route and return.",
                "car",
            ),
            inc(
                "Desert Experience Coordination",
                "TUR coordination of the selected desert itinerary.",
                "route",
            ),
            inc(
                "Scenic Photography Stops",
                "Time at selected desert viewpoints for landscape photography.",
                "camera",
            ),
            inc(
                "Cultural Interpretation",
                "Context on desert landscapes and regional desert traditions.",
                "book-open",
            ),
        ],

        "exclusions": [
            exc(
                "Optional Dune Activities",
                "Dune driving, sandboarding and other optional activities are excluded unless specifically included.",
                "mountain",
            ),
            exc(
                "Dinner",
                "Desert dinner is excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Expenses",
                "Shopping, gratuities and personal purchases are excluded.",
                "wallet",
            ),
        ],

        "highlights": [
            highlight(
                "Desert Dunes",
                "Leave the city behind and experience the scale and silence of the Arabian desert.",
                "mountain",
                "Nature",
            ),
            highlight(
                "Sunset",
                "Watch the desert change colour as the sun drops across the dunes.",
                "sun",
                "Scenic",
            ),
            highlight(
                "Desert Photography",
                "Capture sweeping dunes, textures, silhouettes and evening light.",
                "camera",
                "Photography",
            ),
            highlight(
                "Cultural Context",
                "Explore the desert through regional traditions rather than a purely commercial lens.",
                "book-open",
                "Culture",
            ),
        ],

        "addons": [
            addon(
                "Private Desert Dinner",
                "Add a curated evening meal in a desert setting.",
                (
                    "Private or premium desert dining arrangement subject "
                    "to selected operator, location and availability."
                ),
                95,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Closed Shoes",
                "Wear closed, comfortable footwear suitable for sand and outdoor terrain.",
                "Footwear",
                "footprints",
                True,
                True,
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat.",
                "Weather",
                "sun",
            ),
            packing(
                "Light Jacket",
                "Desert temperatures can drop after sunset.",
                "Clothing",
                "wind",
            ),
            packing(
                "Water",
                "Carry adequate drinking water throughout the desert outing.",
                "Hydration",
                "droplet",
                True,
            ),
        ],

        "safety_rows": [
            safety(
                "Desert Heat",
                "Heat exposure can be significant during the day; hydration and shade are important.",
                "Weather",
                "sun",
            ),
            safety(
                "Dune Terrain",
                "Guests must follow operator instructions around vehicles, dunes and optional activities.",
                "Terrain",
                "mountain",
            ),
            safety(
                "Vehicle Safety",
                "Seat belts must be worn and all vehicle safety instructions followed during dune activities.",
                "Transport",
                "shield",
            ),
        ],

        "requirements": [
            requirement(
                "Physical Comfort",
                "Guests participating in dune activities should be comfortable with movement over uneven terrain.",
                "Mobility",
                True,
                "footprints",
            ),
            requirement(
                "Activity Selection",
                "Guests must disclose relevant mobility or medical considerations before selecting optional dune activities.",
                "Safety",
                True,
                "heart",
            ),
        ],

        "faqs": [
            faq(
                "Is this a desert safari?",
                (
                    "It is a desert experience, but TUR positions it around "
                    "landscape, sunset and cultural discovery. Optional dune "
                    "activities can be added separately."
                ),
                "Experience",
                True,
            ),
            faq(
                "Can children join?",
                "Yes, provided they meet the minimum age and any operator requirements for selected activities.",
                "Family",
                False,
            ),
            faq(
                "Will we see desert wildlife?",
                (
                    "Wildlife is not guaranteed and is not the primary focus "
                    "of this experience."
                ),
                "Nature",
                False,
            ),
            faq(
                "Can we skip dune driving?",
                "Yes. The experience can be structured around landscapes, sunset and cultural elements without optional high-intensity activities.",
                "Customisation",
                False,
            ),
        ],

        "wildlife_rows": [],
    },


    # =========================================================================
    # EGYPT — ID 35
    # =========================================================================

    {
        "code": "ME-EGY-001",
        "slug": "giza-plateau-pyramids-sphinx-ancient-egypt",
        "title": "Giza Plateau — Pyramids, Sphinx & Ancient Egypt",
        "destination_id": 35,
        "category_id": CATEGORY_CULTURE,

        "short_description": (
            "A private Giza experience centred on the Great Pyramids, the "
            "Sphinx and the extraordinary story of ancient Egyptian civilisation."
        ),

        "description": (
            "Encounter one of humanity's most recognisable archaeological "
            "landscapes through a carefully paced private visit to the Giza "
            "Plateau. Explore the pyramids and Sphinx with historical context "
            "that goes beyond photographs, connecting architecture, engineering, "
            "religion and the wider civilisation that built them. Optional "
            "interior access is subject to official ticketing, opening hours "
            "and site conditions."
        ),

        "duration": "Half Day",

        "meeting_point": (
            "Confirmed Cairo or Giza hotel pickup."
        ),

        "location": "Giza Plateau, Giza, Egypt",

        "price_from": 145,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 4,

        "meta_title": (
            "Giza Pyramids & Sphinx Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Explore the Giza Pyramids and Sphinx through a private "
            "experience combining ancient history, architecture and archaeology."
        ),

        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_HISTORICAL,
            TAG_ARCHITECTURE,
            TAG_CULTURE,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],

        "moments": [
            MOMENT_HISTORY,
            MOMENT_ARCHITECTURE,
            MOMENT_HERITAGE,
            MOMENT_EXTRAORDINARY,
        ],

        "pricing_rows": pricing(
            (225, 225, 225),
            (175, 175, 175),
            (145, 145, 145),
            (
                "Indicative TUR selling price per person in USD. "
                "Official site admissions and optional pyramid interior "
                "tickets are subject to current tariffs."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Cairo / Giza Departure",
                "Morning / Afternoon",
                (
                    "Meet your guide and travel to the Giza Plateau with "
                    "an introduction to ancient Egyptian history."
                ),
            ),
            itinerary(
                "Great Pyramid & Plateau",
                "Main Activity",
                (
                    "Explore the pyramid complex and learn about its "
                    "construction, purpose and place within ancient Egyptian civilisation."
                ),
            ),
            itinerary(
                "Sphinx",
                "Later Activity",
                (
                    "Continue to the Sphinx and surrounding viewpoints "
                    "for historical interpretation and photography."
                ),
            ),
            itinerary(
                "Ancient Egypt Farewell",
                "Final Hour",
                (
                    "Conclude with time for questions, photography and "
                    "an optional local lunch before returning."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Transport",
                "Dedicated transport for the agreed Giza itinerary.",
                "car",
            ),
            inc(
                "Egyptology Guide Support",
                "Guide support and historical interpretation throughout the visit.",
                "user",
            ),
            inc(
                "Curated Archaeological Route",
                "Planned route through the principal Giza landmarks.",
                "route",
            ),
            inc(
                "Photography Stops",
                "Time for appropriate pyramid and Sphinx photography.",
                "camera",
            ),
        ],

        "exclusions": [
            exc(
                "Site Admissions",
                "Official Giza Plateau and optional interior admission fees are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Expenses",
                "Shopping, gratuities and personal purchases are excluded.",
                "wallet",
            ),
        ],

        "highlights": [
            highlight(
                "Great Pyramid",
                "Stand before one of the world's most enduring architectural achievements.",
                "landmark",
                "History",
            ),
            highlight(
                "The Sphinx",
                "Encounter the iconic Sphinx and explore the historical questions surrounding its construction and role.",
                "landmark",
                "Heritage",
            ),
            highlight(
                "Ancient Engineering",
                "Discover the planning, engineering and cultural ideas behind the pyramid complex.",
                "building",
                "Architecture",
            ),
            highlight(
                "Giza Landscapes",
                "Capture extraordinary views across the plateau and surrounding desert landscape.",
                "camera",
                "Scenic",
            ),
        ],

        "addons": [
            addon(
                "Pyramid Interior Admission",
                "Add official access to an available pyramid interior.",
                (
                    "Official interior admission arranged according to "
                    "current ticket availability and site restrictions."
                ),
                45,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Wear comfortable footwear for uneven archaeological surfaces.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat.",
                "Weather",
                "sun",
            ),
            packing(
                "Water",
                "Carry sufficient drinking water for the outdoor visit.",
                "Hydration",
                "droplet",
                True,
            ),
            packing(
                "Light Clothing",
                "Choose breathable clothing suitable for warm outdoor conditions while respecting local customs.",
                "Clothing",
                "shirt",
            ),
        ],

        "safety_rows": [
            safety(
                "Heat Exposure",
                "The Giza Plateau can become very hot; hydration and shade breaks are important.",
                "Weather",
                "sun",
            ),
            safety(
                "Uneven Ground",
                "Archaeological areas include uneven and sandy surfaces.",
                "Terrain",
                "mountain",
            ),
            safety(
                "Site Rules",
                "Follow official archaeological-site access and photography rules.",
                "Heritage",
                "shield",
            ),
        ],

        "requirements": [
            requirement(
                "Respect Heritage Sites",
                "Guests must follow site rules and avoid touching or climbing protected structures.",
                "Heritage",
                True,
                "shield",
            ),
            requirement(
                "Walking Comfort",
                "Guests should be comfortable walking outdoors on sandy and uneven surfaces.",
                "Mobility",
                True,
                "footprints",
            ),
        ],

        "faqs": [
            faq(
                "Can we enter a pyramid?",
                (
                    "Yes, where an interior is open and official tickets are "
                    "available. Interior access is an optional addition."
                ),
                "Booking",
                True,
            ),
            faq(
                "How hot is the Giza Plateau?",
                "Conditions vary by season, but the plateau can become very hot, especially around midday.",
                "Weather",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Yes. Families can participate, although younger children should be prepared for heat and outdoor walking.",
                "Family",
                False,
            ),
            faq(
                "Can we add lunch?",
                "Yes. A suitable Cairo or Giza lunch can be incorporated into the final itinerary.",
                "Dining",
                False,
            ),
        ],

        "wildlife_rows": [],
    },


    {
        "code": "ME-EGY-002",
        "slug": "islamic-cairo-al-azhar-khan-el-khalili",
        "title": "Islamic Cairo — Historic Mosques, Al-Azhar & Khan el-Khalili",
        "destination_id": 35,
        "category_id": CATEGORY_CULTURE,

        "short_description": (
            "A heritage journey through historic Cairo connecting monumental "
            "mosques, Al-Azhar, traditional streets and the atmosphere of "
            "Khan el-Khalili."
        ),

        "description": (
            "Discover Cairo through its historic Islamic heart. Explore selected "
            "architectural landmarks, mosque courtyards and historic streets "
            "with a locally informed guide, then continue into Khan el-Khalili "
            "for traditional commerce, crafts and atmosphere. The experience "
            "focuses on architecture, faith, scholarship, craftsmanship and "
            "the layered history of one of the world's great cities."
        ),

        "duration": "Half Day",

        "meeting_point": (
            "Confirmed Cairo hotel or agreed central meeting point."
        ),

        "location": "Historic Cairo, Cairo, Egypt",

        "price_from": 105,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 5,

        "meta_title": (
            "Islamic Cairo & Khan el-Khalili Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Explore Historic Cairo through Islamic architecture, Al-Azhar, "
            "historic streets and Khan el-Khalili."
        ),

        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_MODERATE,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_CULTURE,
            TAG_HISTORICAL,
            TAG_ARCHITECTURE,
            TAG_MARKETS,
            TAG_PRIVATE,
        ],

        "moments": [
            MOMENT_HISTORY,
            MOMENT_HERITAGE,
            MOMENT_ARCHITECTURE,
            MOMENT_MARKET,
        ],

        "pricing_rows": pricing(
            (175, 175, 175),
            (135, 135, 135),
            (115, 115, 115),
            (
                "Indicative TUR selling price per person in USD. "
                "Mosque, museum and monument admissions are subject to "
                "current official tariffs."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Historic Cairo Welcome",
                "Morning / Afternoon",
                (
                    "Meet your guide and begin with an introduction to "
                    "Cairo's historic districts and Islamic architectural heritage."
                ),
            ),
            itinerary(
                "Mosques & Al-Azhar",
                "Main Activity",
                (
                    "Explore selected historic mosques and the Al-Azhar "
                    "area while learning about Cairo's religious and scholarly heritage."
                ),
            ),
            itinerary(
                "Historic Streets",
                "Later Activity",
                (
                    "Walk through selected historic lanes and architectural "
                    "spaces connecting the major monuments."
                ),
            ),
            itinerary(
                "Khan el-Khalili",
                "Final Hour",
                (
                    "Explore the famous market district with time for "
                    "crafts, shopping and traditional refreshments."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Transport",
                "Dedicated transport for the agreed Cairo heritage route.",
                "car",
            ),
            inc(
                "Local Heritage Guide",
                "Guide support and architectural interpretation.",
                "user",
            ),
            inc(
                "Curated Historic Route",
                "Planned route through selected heritage landmarks.",
                "route",
            ),
            inc(
                "Photography Stops",
                "Time for appropriate architectural and market photography.",
                "camera",
            ),
        ],

        "exclusions": [
            exc(
                "Monument Admissions",
                "Entrance fees to paid monuments are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Shopping",
                "Khan el-Khalili purchases and personal expenses are excluded.",
                "shopping-bag",
            ),
        ],

        "highlights": [
            highlight(
                "Historic Mosques",
                "Explore remarkable Islamic architecture and the religious history of Cairo.",
                "landmark",
                "Architecture",
            ),
            highlight(
                "Al-Azhar",
                "Discover the significance of one of the historic centres of Islamic scholarship.",
                "book-open",
                "Culture",
            ),
            highlight(
                "Historic Cairo",
                "Walk through layered streets where architecture and everyday life meet.",
                "city",
                "Heritage",
            ),
            highlight(
                "Khan el-Khalili",
                "Experience the atmosphere of one of Cairo's most famous traditional market districts.",
                "shopping-bag",
                "Markets",
            ),
        ],

        "addons": [
            addon(
                "Traditional Egyptian Lunch",
                "Add a curated lunch featuring Egyptian cuisine.",
                (
                    "TUR-arranged lunch at a suitable local venue, subject "
                    "to opening hours and dietary requirements."
                ),
                50,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Historic Cairo involves walking over uneven streets and surfaces.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Respectful Clothing",
                "Dress appropriately for religious and cultural sites.",
                "Clothing",
                "shirt",
                True,
                True,
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen and sunglasses for outdoor sections.",
                "Weather",
                "sun",
            ),
            packing(
                "Water",
                "Carry drinking water during the walking sections.",
                "Hydration",
                "droplet",
            ),
        ],

        "safety_rows": [
            safety(
                "Crowded Markets",
                "Remain aware of personal belongings in busy market areas.",
                "Urban",
                "lock",
            ),
            safety(
                "Religious Sites",
                "Follow local dress, photography and conduct requirements.",
                "Culture",
                "shield",
            ),
            safety(
                "Uneven Streets",
                "Historic streets may include uneven paving and steps.",
                "Terrain",
                "footprints",
            ),
        ],

        "requirements": [
            requirement(
                "Respect Religious Spaces",
                "Guests must follow dress, photography and conduct guidance at religious sites.",
                "Culture",
                True,
                "heart",
            ),
            requirement(
                "Walking Comfort",
                "Guests should be comfortable walking through historic streets and markets.",
                "Mobility",
                True,
                "footprints",
            ),
        ],

        "faqs": [
            faq(
                "Can we enter the mosques?",
                (
                    "Where visitor access is permitted, guests can enter selected "
                    "mosques while following local dress and conduct requirements."
                ),
                "Culture",
                True,
            ),
            faq(
                "Can we shop at Khan el-Khalili?",
                "Yes. Guests have time for shopping, although purchases are personal expenses.",
                "Markets",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Yes, particularly for older children interested in history, architecture and culture.",
                "Family",
                False,
            ),
            faq(
                "Can we add Egyptian food?",
                "Yes. A curated local lunch can be added as an optional upgrade.",
                "Dining",
                False,
            ),
        ],

        "wildlife_rows": [],
    },


    {
        "code": "ME-EGY-003",
        "slug": "luxor-temples-nile-ancient-thebes",
        "title": "Luxor — Temples, Nile & Ancient Thebes",
        "destination_id": 35,
        "category_id": CATEGORY_CULTURE,

        "short_description": (
            "A private Luxor heritage journey through the monumental temples "
            "and landscapes of ancient Thebes, with time to experience the Nile."
        ),

        "description": (
            "Travel into the heart of ancient Thebes through a curated Luxor "
            "experience connecting major temple landscapes with the Nile and "
            "the stories of ancient Egyptian civilisation. Depending on the "
            "final route and operating conditions, the experience can include "
            "Karnak, Luxor Temple and selected West Bank heritage sites. It is "
            "designed for guests who want depth, context and time to appreciate "
            "the scale of ancient Egypt rather than simply collecting landmarks."
        ),

        "duration": "Full Day",

        "meeting_point": (
            "Confirmed Luxor hotel or agreed Luxor meeting point."
        ),

        "location": "Luxor, Egypt",

        "price_from": 165,

        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Moderate",

        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 6,

        "meta_title": (
            "Luxor Temples & Ancient Thebes Experience | The Uncharted Route"
        ),

        "meta_description": (
            "Explore Luxor's temples, ancient Thebes and Nile landscapes "
            "through a private Egypt heritage experience."
        ),

        "cancellation_policy_id": CANCELLATION_HIGH_COMMITMENT,
        "accessibility_profile_id": ACCESS_MODERATE,
        "conservation_story_id": CONSERVATION_NONE,

        "tags": [
            TAG_HISTORICAL,
            TAG_ARCHITECTURE,
            TAG_CULTURE,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],

        "moments": [
            MOMENT_HISTORY,
            MOMENT_ARCHITECTURE,
            MOMENT_LANDSCAPES,
            MOMENT_EXTRAORDINARY,
        ],

        "pricing_rows": pricing(
            (275, 275, 275),
            (215, 215, 215),
            (185, 185, 185),
            (
                "Indicative TUR selling price per person in USD. "
                "Temple, tomb and optional Nile excursion admissions are "
                "subject to current official tariffs."
            ),
            "USD",
        ),

        "itinerary_rows": [
            itinerary(
                "Luxor Welcome",
                "Morning",
                (
                    "Meet your guide and receive an introduction to ancient "
                    "Thebes and the day's archaeological route."
                ),
            ),
            itinerary(
                "Karnak & Temple Heritage",
                "Main Activity",
                (
                    "Explore selected temple complexes and learn about "
                    "their religious, architectural and dynastic significance."
                ),
            ),
            itinerary(
                "West Bank Discovery",
                "Afternoon",
                (
                    "Continue to selected West Bank heritage sites according "
                    "to the agreed route, access and operating conditions."
                ),
            ),
            itinerary(
                "Nile Farewell",
                "Late Afternoon",
                (
                    "Conclude with a relaxed Nile-side moment or optional "
                    "short boat experience before returning."
                ),
            ),
        ],

        "inclusions": [
            inc(
                "Private Transport",
                "Dedicated transport for the agreed Luxor itinerary.",
                "car",
            ),
            inc(
                "Egyptology Guide",
                "Specialist historical interpretation throughout the experience.",
                "user",
            ),
            inc(
                "Curated Temple Route",
                "Planned route through selected ancient Thebes landmarks.",
                "route",
            ),
            inc(
                "Photography Stops",
                "Time for architectural and Nile landscape photography.",
                "camera",
            ),
        ],

        "exclusions": [
            exc(
                "Site Admissions",
                "Temple, tomb and attraction entrance fees are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Optional Nile Activities",
                "Boat rides and other optional activities are excluded unless specifically included.",
                "waves",
            ),
        ],

        "highlights": [
            highlight(
                "Ancient Thebes",
                "Explore the monumental heritage of one of ancient Egypt's greatest centres.",
                "landmark",
                "History",
            ),
            highlight(
                "Karnak",
                "Discover extraordinary temple architecture, columns and religious history.",
                "building",
                "Architecture",
            ),
            highlight(
                "West Bank",
                "Connect the monumental landscape with the tombs and heritage of ancient Thebes.",
                "mountain",
                "Heritage",
            ),
            highlight(
                "Nile Landscapes",
                "Experience the river that shaped life, agriculture and civilisation in ancient Egypt.",
                "waves",
                "Scenic",
            ),
        ],

        "addons": [
            addon(
                "Private Nile Boat",
                "Add a short private Nile boat experience.",
                (
                    "Private boat arrangement subject to weather, river "
                    "conditions, operator availability and local regulations."
                ),
                75,
                "Per person",
            ),
        ],

        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Wear supportive shoes for temple grounds and archaeological surfaces.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat.",
                "Weather",
                "sun",
            ),
            packing(
                "Water",
                "Carry adequate drinking water throughout the day.",
                "Hydration",
                "droplet",
                True,
            ),
            packing(
                "Light Layer",
                "Early mornings and Nile-side conditions can be cooler than expected.",
                "Clothing",
                "wind",
            ),
        ],

        "safety_rows": [
            safety(
                "Heat Exposure",
                "Temple and archaeological sites can be very hot and exposed.",
                "Weather",
                "sun",
            ),
            safety(
                "Uneven Archaeological Surfaces",
                "Ancient sites include uneven paving, steps and sandy ground.",
                "Terrain",
                "mountain",
            ),
            safety(
                "Nile Safety",
                "Follow all operator instructions during any optional boat activity.",
                "Marine",
                "waves",
            ),
        ],

        "requirements": [
            requirement(
                "Walking Comfort",
                "Guests should be comfortable with extended walking over archaeological terrain.",
                "Mobility",
                True,
                "footprints",
            ),
            requirement(
                "Weather Flexibility",
                "Outdoor timings may be adjusted for heat, weather or site operating conditions.",
                "Weather",
                True,
                "sun",
            ),
        ],

        "faqs": [
            faq(
                "Is Luxor suitable for a day experience?",
                (
                    "Yes, particularly for guests already staying in Luxor. "
                    "A longer stay is recommended for travellers who want to "
                    "explore the region at a slower pace."
                ),
                "Timing",
                True,
            ),
            faq(
                "Can we visit the West Bank?",
                "Yes. Selected West Bank sites can be included according to access, opening hours and the final itinerary.",
                "Heritage",
                False,
            ),
            faq(
                "Can we take a boat on the Nile?",
                "Yes. A private Nile boat can be added where weather, river conditions and operator availability permit.",
                "Nile",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Yes, although the full-day format and walking requirements make it better suited to children aged eight and above.",
                "Family",
                False,
            ),
        ],

        "wildlife_rows": [],
    },
]


# =============================================================================
# MODEL / CHILD-RECORD HELPERS
# =============================================================================

def model_columns(model):
    return {column.name for column in model.__table__.columns}


def set_supported_fields(model, payload):
    columns = model_columns(model)

    return {
        key: value
        for key, value in payload.items()
        if key in columns
    }


def add_children(model, experience_id, rows):
    for row in rows:
        payload = dict(row)
        payload["experience_id"] = experience_id

        db.session.add(
            model(
                **set_supported_fields(
                    model,
                    payload,
                )
            )
        )


def ordered(rows):
    result = []

    for index, row in enumerate(rows, 1):
        item = dict(row)
        item["display_order"] = index
        result.append(item)

    return result


# =============================================================================
# VALIDATION
# =============================================================================

def validate_reusable_cms(data):
    category = db.session.get(
        ExperienceCategory,
        data["category_id"],
    )

    destination = db.session.get(
        Destination,
        data["destination_id"],
    )

    cancellation = db.session.get(
        CancellationPolicy,
        data["cancellation_policy_id"],
    )

    accessibility = db.session.get(
        Accessibility,
        data["accessibility_profile_id"],
    )

    if not category:
        raise ValueError(
            f"Missing ExperienceCategory ID "
            f"{data['category_id']} for {data['code']}"
        )

    if not destination:
        raise ValueError(
            f"Missing Destination ID "
            f"{data['destination_id']} for {data['code']}"
        )

    if not cancellation:
        raise ValueError(
            f"Missing CancellationPolicy ID "
            f"{data['cancellation_policy_id']} "
            f"for {data['code']}"
        )

    if not accessibility:
        raise ValueError(
            f"Missing Accessibility ID "
            f"{data['accessibility_profile_id']} "
            f"for {data['code']}"
        )

    for tag_id in data["tags"]:
        if not db.session.get(
            ExperienceTag,
            tag_id,
        ):
            raise ValueError(
                f"Missing ExperienceTag ID "
                f"{tag_id} for {data['code']}"
            )

    for moment_id in data["moments"]:
        if not db.session.get(
            SignatureMoment,
            moment_id,
        ):
            raise ValueError(
                f"Missing SignatureMoment ID "
                f"{moment_id} for {data['code']}"
            )


def validate_duplicate_experience(data):
    existing = Experience.query.filter(
        or_(
            Experience.experience_code == data["code"],
            Experience.slug == data["slug"],
        )
    ).first()

    if existing:
        raise ValueError(
            f"Duplicate protection triggered for "
            f"{data['code']} "
            f"(existing experience ID {existing.id})"
        )


def verify_experience(experience, data):
    expected = {
        "itinerary": len(data["itinerary_rows"]),
        "inclusions": len(data["inclusions"]),
        "exclusions": len(data["exclusions"]),
        "highlights": len(data["highlights"]),
        "pricing": len(data["pricing_rows"]),
        "addons": len(data["addons"]),
        "packing": len(data["packing_rows"]),
        "safety": len(data["safety_rows"]),
        "requirements": len(data["requirements"]),
        "faqs": len(data["faqs"]),
        "tags": len(data["tags"]),
        "signature_moments": len(data["moments"]),
        "wildlife": len(data["wildlife_rows"]),
    }

    actual = {
        "itinerary": experience.itinerary.count(),
        "inclusions": experience.inclusions.count(),
        "exclusions": experience.exclusions.count(),
        "highlights": experience.highlights.count(),
        "pricing": experience.pricing.count(),
        "addons": experience.addons.count(),
        "packing": experience.packing_items.count(),
        "safety": experience.safety_rules.count(),
        "requirements": experience.requirements.count(),
        "faqs": experience.faqs.count(),
        "tags": experience.tags.count(),
        "signature_moments": experience.signature_moments.count(),
        "wildlife": experience.wildlife.count(),
    }

    for key, expected_count in expected.items():
        actual_count = actual[key]

        if actual_count != expected_count:
            raise ValueError(
                f"Verification failed for {data['code']}: "
                f"{key} expected {expected_count}, "
                f"got {actual_count}"
            )

    if experience.media.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: "
            f"media must be 0"
        )

    if experience.schedules.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: "
            f"schedules must be 0"
        )

    if experience.bookings.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: "
            f"bookings must be 0"
        )


# =============================================================================
# APPLICATION
# =============================================================================

def main():
    app = create_app()

    with app.app_context():

        print("\n" + "=" * 110)
        print(
            "THE UNCHARTED ROUTE — BATCH 5: MIDDLE EAST"
        )
        print("=" * 110)
        print(
            f"Experiences in batch: {len(EXPERIENCES)}"
        )
        print(
            f"Mode: {'APPLY' if args.apply else 'DRY RUN'}"
        )
        print("=" * 110)

        try:

            # -----------------------------------------------------------------
            # Validate reusable records before creating anything.
            # -----------------------------------------------------------------

            for data in EXPERIENCES:
                validate_reusable_cms(data)
                validate_duplicate_experience(data)

            print("\nReusable CMS records validated.")
            print("Duplicate protection validated.")

            created = []

            # -----------------------------------------------------------------
            # Create experiences.
            # -----------------------------------------------------------------

            for batch_index, data in enumerate(
                EXPERIENCES,
                1,
            ):

                destination = db.session.get(
                    Destination,
                    data["destination_id"],
                )

                print(
                    f"\n[{batch_index:02d}/{len(EXPERIENCES)}] "
                    f"{data['code']} — {data['title']}"
                )

                print(
                    f"    Destination ID: "
                    f"{data['destination_id']} | "
                    f"Destination active: "
                    f"{destination.active}"
                )

                print(
                    f"    Itinerary: "
                    f"{len(data['itinerary_rows'])} | "
                    f"Inclusions: "
                    f"{len(data['inclusions'])} | "
                    f"Exclusions: "
                    f"{len(data['exclusions'])} | "
                    f"Highlights: "
                    f"{len(data['highlights'])}"
                )

                print(
                    f"    Pricing: "
                    f"{len(data['pricing_rows'])} | "
                    f"Add-ons: "
                    f"{len(data['addons'])} | "
                    f"Packing: "
                    f"{len(data['packing_rows'])} | "
                    f"Safety: "
                    f"{len(data['safety_rows'])}"
                )

                print(
                    f"    Requirements: "
                    f"{len(data['requirements'])} | "
                    f"FAQs: "
                    f"{len(data['faqs'])} | "
                    f"Tags: "
                    f"{len(data['tags'])} | "
                    f"Signature moments: "
                    f"{len(data['moments'])} | "
                    f"Wildlife: "
                    f"{len(data['wildlife_rows'])}"
                )

                experience = Experience(
                    experience_code=data["code"],
                    title=data["title"],
                    slug=data["slug"],
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
                    featured_image=data["slug"],
                    banner_image=data["slug"],
                    meta_title=data["meta_title"],
                    meta_description=data["meta_description"],
                    featured=data["featured"],
                    show_on_homepage=data["show_on_homepage"],
                    active=data.get("active", True),
                    display_order=data["display_order"],
                    category_id=data["category_id"],
                    destination_id=data["destination_id"],
                    conservation_story_id=data.get(
                        "conservation_story_id"
                    ),
                    cancellation_policy_id=data[
                        "cancellation_policy_id"
                    ],
                    accessibility_profile_id=data[
                        "accessibility_profile_id"
                    ],
                )

                db.session.add(experience)
                db.session.flush()

                experience.tags.extend(
                    [
                        db.session.get(
                            ExperienceTag,
                            tag_id,
                        )
                        for tag_id in data["tags"]
                    ]
                )

                experience.signature_moments.extend(
                    [
                        db.session.get(
                            SignatureMoment,
                            moment_id,
                        )
                        for moment_id in data["moments"]
                    ]
                )

                add_children(
                    ExperienceItinerary,
                    experience.id,
                    [
                        {
                            **record,
                            "display_order": index,
                        }
                        for index, record in enumerate(
                            data["itinerary_rows"],
                            1,
                        )
                    ],
                )

                add_children(
                    ExperienceInclusion,
                    experience.id,
                    ordered(
                        data["inclusions"]
                    ),
                )

                add_children(
                    ExperienceExclusion,
                    experience.id,
                    ordered(
                        data["exclusions"]
                    ),
                )

                add_children(
                    ExperienceHighlight,
                    experience.id,
                    ordered(
                        data["highlights"]
                    ),
                )

                add_children(
                    ExperiencePricing,
                    experience.id,
                    ordered(
                        data["pricing_rows"]
                    ),
                )

                add_children(
                    ExperienceAddon,
                    experience.id,
                    ordered(
                        data["addons"]
                    ),
                )

                add_children(
                    ExperiencePackingItem,
                    experience.id,
                    ordered(
                        data["packing_rows"]
                    ),
                )

                add_children(
                    ExperienceSafetyRule,
                    experience.id,
                    ordered(
                        data["safety_rows"]
                    ),
                )

                add_children(
                    ExperienceRequirement,
                    experience.id,
                    ordered(
                        data["requirements"]
                    ),
                )

                add_children(
                    ExperienceFAQ,
                    experience.id,
                    ordered(
                        data["faqs"]
                    ),
                )

                # Wildlife intentionally remains empty.
                # We do not attach unrelated Kenya wildlife species.

                created.append(experience)

            db.session.flush()

            # -----------------------------------------------------------------
            # Verification
            # -----------------------------------------------------------------

            print("\n" + "=" * 110)
            print("BATCH VERIFICATION")
            print("=" * 110)

            for experience, data in zip(
                created,
                EXPERIENCES,
            ):

                verify_experience(
                    experience,
                    data,
                )

                print(
                    f"VERIFIED {data['code']} | "
                    f"all content counts correct | "
                    f"wildlife={experience.wildlife.count()} "
                    f"media={experience.media.count()} "
                    f"schedules={experience.schedules.count()} "
                    f"bookings={experience.bookings.count()}"
                )

            print("\nAll batch records passed verification.")

            # -----------------------------------------------------------------
            # Commit or rollback.
            # -----------------------------------------------------------------

            if args.apply:

                db.session.commit()

                print("\n" + "=" * 110)
                print("BATCH 5 COMMITTED SUCCESSFULLY")
                print("=" * 110)

                print(
                    "Created 6 complete Middle East experiences."
                )

                print(
                    "Dubai and Egypt remain active."
                )

            else:

                db.session.rollback()

                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)

                print(
                    "Validated 6 complete Middle East experiences."
                )

                print(
                    "No database changes were committed."
                )

                print(
                    "Run with --apply only after reviewing "
                    "the dry-run output."
                )

        except Exception as exc:

            db.session.rollback()

            print("\n" + "=" * 110)
            print("BATCH FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)

            print(
                f"{type(exc).__name__}: {exc}"
            )

            print(
                "No database changes were committed."
            )

            raise


if __name__ == "__main__":
    main()