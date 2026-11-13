"""
===============================================================================
THE UNCHARTED ROUTE
BATCH 4 — SOUTHERN AFRICA EXPERIENCE POPULATION
===============================================================================

Destinations:
    Cape Town    ID 27 — ACTIVE
    Johannesburg ID 28 — ACTIVE

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
    - APPLY: python scripts/populate_southern_africa_batch.py --apply

The batch is transactional. Any error rolls the entire batch back.

Research basis:
    Cape Town: official Cape Town Tourism and SANParks material supports Table
    Mountain, Robben Island, Cape Point, Boulders Beach and the Peninsula as
    major nature, heritage and coastal anchors.

    Johannesburg: official Apartheid Museum and Maropeng material supports the
    Apartheid Museum, Soweto heritage and the Cradle of Humankind/Maropeng as
    major history, culture, science and heritage anchors.
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
    description="Populate Batch 4 — Southern Africa experiences."
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

# Existing Conservation Story IDs.
# We intentionally do not attach Kenya-specific wildlife conservation stories
# to these Southern African experiences.
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

def packing(name, description, category, icon, recommended=True, required=False):
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
    # CAPE TOWN — ID 27
    # =========================================================================

    {
        "code": "SA-CPT-001",
        "slug": "table-mountain-summit-city-views-cape-nature",
        "title": "Table Mountain — Summit, City Views & Cape Nature",
        "destination_id": 27,
        "category_id": CATEGORY_ADVENTURE,
        "short_description": (
            "A private Table Mountain experience combining the summit, "
            "extraordinary Cape Town views and a carefully paced introduction "
            "to the mountain's natural landscape."
        ),
        "description": (
            "Experience one of Cape Town's defining natural landmarks through "
            "a thoughtfully paced private outing. Depending on conditions and "
            "ticket availability, guests can ascend Table Mountain by cableway "
            "or undertake an agreed walking route with an appropriate guide. "
            "The experience focuses on the mountain's dramatic geology, "
            "fynbos landscapes, panoramic city and ocean views, and the "
            "importance of protecting this exceptional natural environment."
        ),
        "duration": "Half Day",
        "meeting_point": (
            "Confirmed Cape Town hotel or agreed Table Mountain meeting point."
        ),
        "location": "Table Mountain, Cape Town, South Africa",
        "price_from": 125,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Moderate",
        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 1,
        "meta_title": (
            "Table Mountain Cape Town Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore Table Mountain with panoramic Cape Town views, "
            "fynbos landscapes and a private, thoughtfully paced experience."
        ),
        "cancellation_policy_id": CANCELLATION_HIGH_COMMITMENT,
        "accessibility_profile_id": ACCESS_MODERATE,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_NATURE,
            TAG_HIKING,
            TAG_PHOTOGRAPHY,
            TAG_CITY,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_VIEWPOINT,
            MOMENT_TRAIL,
            MOMENT_LANDSCAPES,
            MOMENT_EXTRAORDINARY,
        ],
        "pricing_rows": pricing(
            (225, 225, 225),
            (175, 175, 175),
            (145, 145, 145),
            (
                "Indicative TUR selling price per person in USD. "
                "Cableway tickets, where required, are subject to official "
                "availability and current tariffs."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Mountain Welcome",
                "Morning / Afternoon",
                "Meet your guide and receive a briefing on mountain conditions, "
                "the day's route and the experience plan.",
            ),
            itinerary(
                "Table Mountain Ascent",
                "Main Activity",
                "Ascend by cableway or undertake the agreed walking route "
                "depending on conditions, guest preference and operational availability.",
            ),
            itinerary(
                "Summit Exploration",
                "Main Activity",
                "Explore selected viewpoints and natural areas while learning "
                "about the mountain's landscape, fynbos and conservation context.",
            ),
            itinerary(
                "Cape Town Panorama",
                "Final Hour",
                "Enjoy time for photography across the city, Atlantic coastline "
                "and surrounding mountains before descending.",
            ),
        ],
        "inclusions": [
            inc(
                "Private Experience Coordination",
                "TUR coordination of the agreed Table Mountain experience.",
                "route",
            ),
            inc(
                "Local Guide Support",
                "Guide support appropriate to the selected route.",
                "user",
            ),
            inc(
                "Mountain Interpretation",
                "Context on the mountain's geology, vegetation and cultural significance.",
                "mountain",
            ),
            inc(
                "Photography Stops",
                "Time at selected viewpoints for landscape and city photography.",
                "camera",
            ),
        ],
        "exclusions": [
            exc(
                "Cableway Tickets",
                "Official cableway tickets are excluded unless specifically included in the final quotation.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Expenses",
                "Shopping, gratuities and personal expenses are excluded.",
                "wallet",
            ),
        ],
        "highlights": [
            highlight(
                "Table Mountain Summit",
                "Stand above Cape Town on one of the city's most iconic natural landmarks.",
                "mountain",
                "Nature",
            ),
            highlight(
                "Panoramic Cape Town",
                "Take in dramatic views across the city, Atlantic coastline and surrounding mountains.",
                "camera",
                "Scenic",
            ),
            highlight(
                "Cape Fynbos",
                "Discover the distinctive plant life and ecological character of the Cape Floristic Region.",
                "leaf",
                "Nature",
            ),
            highlight(
                "Flexible Route",
                "Choose a cableway-led or walking approach according to conditions and guest capability.",
                "route",
                "Adventure",
            ),
        ],
        "addons": [
            addon(
                "Private Mountain Picnic",
                "Upgrade to a curated picnic with a scenic Table Mountain setting.",
                "TUR-arranged picnic subject to weather, access and suitable location.",
                75,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Comfortable Walking Shoes",
                "Wear shoes suitable for uneven terrain and walking.",
                "Footwear",
                "footprints",
                True,
            ),
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat.",
                "Weather",
                "sun",
            ),
            packing(
                "Warm Layer",
                "Mountain conditions can be significantly cooler and windier than the city.",
                "Clothing",
                "wind",
            ),
            packing(
                "Water",
                "Carry adequate drinking water for the duration of the outing.",
                "Hydration",
                "droplet",
                True,
            ),
        ],
        "safety_rows": [
            safety(
                "Mountain Weather",
                "Weather can change rapidly and the route may be adjusted or postponed when conditions are unsafe.",
                "Weather",
                "cloud",
            ),
            safety(
                "Uneven Terrain",
                "Walking routes may include uneven, rocky or steep sections.",
                "Terrain",
                "mountain",
            ),
            safety(
                "Follow Guide Advice",
                "Guests must follow the guide's instructions and stay within agreed routes.",
                "Guidance",
                "shield",
            ),
        ],
        "requirements": [
            requirement(
                "Weather Flexibility",
                "Guests must accept route changes where mountain weather or operational conditions require them.",
                "Weather",
                True,
                "cloud",
            ),
            requirement(
                "Suitable Footwear",
                "Closed, comfortable footwear is required for walking sections.",
                "Safety",
                True,
                "footprints",
            ),
        ],
        "faqs": [
            faq(
                "Can we take the cableway?",
                "Yes, where operating conditions and ticket availability permit. A walking option can be discussed where appropriate.",
                "Logistics",
                True,
            ),
            faq(
                "Is Table Mountain suitable for children?",
                "Yes for children comfortable with the selected route. The minimum age for this product is eight.",
                "Family",
                False,
            ),
            faq(
                "What happens if the cableway closes?",
                "TUR will assess safe alternatives, rescheduling or an appropriate replacement experience depending on the circumstances.",
                "Weather",
                False,
            ),
            faq(
                "Will we see wildlife?",
                "The focus is landscape and nature rather than wildlife viewing. Small wildlife and birds may be encountered but are never guaranteed.",
                "Nature",
                False,
            ),
        ],
        "wildlife_rows": [],
    },

    {
        "code": "SA-CPT-002",
        "slug": "cape-peninsula-cape-point-boulders-coastal-landscapes",
        "title": "Cape Peninsula — Cape Point, Boulders & Coastal Landscapes",
        "destination_id": 27,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A full-day Cape Peninsula journey connecting dramatic coastal "
            "landscapes, Cape Point, Boulders Beach and the winding roads of "
            "the southern Cape."
        ),
        "description": (
            "Travel the Cape Peninsula through a private, scenic route designed "
            "around Cape Point, Boulders Beach and the dramatic Atlantic and "
            "False Bay coastlines. The day balances iconic viewpoints with "
            "nature, photography and relaxed exploration. African penguins may "
            "be encountered at Boulders Beach, but wildlife sightings are never "
            "guaranteed."
        ),
        "duration": "Full Day",
        "meeting_point": (
            "Confirmed Cape Town hotel or agreed central pickup point."
        ),
        "location": "Cape Peninsula, Cape Town, South Africa",
        "price_from": 165,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",
        "featured": True,
        "show_on_homepage": True,
        "active": True,
        "display_order": 2,
        "meta_title": (
            "Cape Peninsula Cape Point & Boulders Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore Cape Point, Boulders Beach and the dramatic Cape Peninsula "
            "coast through a private full-day experience."
        ),
        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_COASTAL,
            TAG_NATURE,
            TAG_PHOTOGRAPHY,
            TAG_WILDLIFE,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_LANDSCAPES,
            MOMENT_WILDLIFE,
            MOMENT_VIEWPOINT,
            MOMENT_EXTRAORDINARY,
        ],
        "pricing_rows": pricing(
            (285, 285, 285),
            (225, 225, 225),
            (195, 195, 195),
            (
                "Indicative TUR selling price per person in USD. "
                "Park and attraction admissions are excluded unless specifically included."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Cape Town Departure",
                "Morning",
                "Meet your guide and begin the scenic drive toward the Cape Peninsula.",
            ),
            itinerary(
                "Boulders & Coastal Route",
                "Late Morning",
                "Explore Boulders Beach and the surrounding coastline, with time for respectful wildlife observation and photography.",
            ),
            itinerary(
                "Cape Point",
                "Afternoon",
                "Continue through the Cape of Good Hope area to Cape Point and selected viewpoints.",
            ),
            itinerary(
                "Scenic Return",
                "Late Afternoon",
                "Return via an agreed scenic route with stops for photography where time and road conditions permit.",
            ),
        ],
        "inclusions": [
            inc(
                "Private Vehicle & Driver",
                "Dedicated vehicle and driver for the agreed Cape Peninsula route.",
                "car",
            ),
            inc(
                "Experience Coordination",
                "TUR coordination of the day's route and guest logistics.",
                "route",
            ),
            inc(
                "Scenic Stops",
                "Planned stops at key coastal and landscape viewpoints.",
                "camera",
            ),
            inc(
                "Local Interpretation",
                "Context on Cape Peninsula landscapes, history and natural environment.",
                "leaf",
            ),
        ],
        "exclusions": [
            exc(
                "Park Admissions",
                "Cape Point and other official attraction entrance fees are excluded unless specifically included.",
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
                "Cape Point",
                "Stand at the dramatic southern Cape viewpoint surrounded by ocean and rugged landscapes.",
                "landmark",
                "Nature",
            ),
            highlight(
                "Boulders Beach",
                "Visit one of the Cape's best-known African penguin viewing locations.",
                "bird",
                "Wildlife",
            ),
            highlight(
                "Coastal Drive",
                "Experience the dramatic road and coastline of the Cape Peninsula.",
                "car",
                "Scenic",
            ),
            highlight(
                "Photography",
                "Capture ocean, cliffs, beaches, wildlife and mountain landscapes throughout the day.",
                "camera",
                "Photography",
            ),
        ],
        "addons": [
            addon(
                "Private Coastal Lunch",
                "Add a curated lunch at a suitable Cape Peninsula venue.",
                "TUR-arranged lunch subject to venue availability and dietary requirements.",
                85,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Sun Protection",
                "Bring sunscreen, sunglasses and a hat.",
                "Weather",
                "sun",
            ),
            packing(
                "Comfortable Shoes",
                "Wear comfortable shoes for viewpoints and short walking sections.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Light Jacket",
                "Coastal conditions can be windy and cool even on warm days.",
                "Clothing",
                "wind",
            ),
            packing(
                "Camera",
                "A camera or phone is recommended for the Peninsula's landscapes and wildlife.",
                "Photography",
                "camera",
            ),
        ],
        "safety_rows": [
            safety(
                "Coastal Wind",
                "Strong wind can occur around exposed viewpoints; follow guide instructions.",
                "Weather",
                "wind",
            ),
            safety(
                "Wildlife Distance",
                "Maintain respectful distance from wildlife and never feed or approach animals.",
                "Wildlife",
                "shield",
            ),
            safety(
                "Road Conditions",
                "Some Peninsula roads are winding and exposed; travel times may change with traffic and weather.",
                "Transport",
                "car",
            ),
        ],
        "requirements": [
            requirement(
                "Respect Wildlife",
                "Guests must follow all wildlife viewing guidance and never feed or touch animals.",
                "Wildlife",
                True,
                "shield",
            ),
            requirement(
                "Weather Flexibility",
                "Coastal stops may be adjusted where weather creates unsafe conditions.",
                "Weather",
                True,
                "cloud",
            ),
        ],
        "faqs": [
            faq(
                "Will we definitely see penguins?",
                "No. African penguins are present around Boulders Beach, but wildlife sightings and viewing conditions are never guaranteed.",
                "Wildlife",
                True,
            ),
            faq(
                "Is Cape Point the Cape of Good Hope?",
                "Cape Point and the Cape of Good Hope are distinct landmarks within the same protected area.",
                "Geography",
                False,
            ),
            faq(
                "Can children join?",
                "Yes. The experience is suitable for families and the minimum age is six.",
                "Family",
                False,
            ),
            faq(
                "Can we add lunch?",
                "Yes. A suitable coastal lunch can be added as an optional upgrade.",
                "Dining",
                False,
            ),
        ],
        "wildlife_rows": [],
    },

    {
        "code": "SA-CPT-003",
        "slug": "robben-island-v-and-a-waterfront-history-memory",
        "title": "Robben Island & V&A Waterfront — History, Memory & Cape Town",
        "destination_id": 27,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A heritage-focused Cape Town journey connecting Robben Island's "
            "history with the contemporary energy of the V&A Waterfront."
        ),
        "description": (
            "Explore one of Cape Town's most significant heritage experiences "
            "through a carefully paced visit to Robben Island followed by a "
            "curated V&A Waterfront heritage walk. The experience connects "
            "political history, memory, architecture and contemporary harbour "
            "life. Robben Island visits are subject to ferry and tour "
            "availability; where the island is unavailable, TUR can propose a "
            "suitable heritage alternative rather than misrepresenting access."
        ),
        "duration": "Full Day",
        "meeting_point": (
            "Nelson Mandela Gateway at the V&A Waterfront or confirmed Cape Town hotel pickup, depending on final ticketing arrangements."
        ),
        "location": "Robben Island & V&A Waterfront, Cape Town, South Africa",
        "price_from": 175,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 10,
        "difficulty": "Easy",
        "active": True,
        "featured": True,
        "show_on_homepage": False,
        "display_order": 3,
        "meta_title": (
            "Robben Island & V&A Waterfront Heritage Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore Robben Island's history and Cape Town's V&A Waterfront through a private, thoughtfully paced heritage experience."
        ),
        "cancellation_policy_id": CANCELLATION_HIGH_COMMITMENT,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_CULTURE,
            TAG_HISTORICAL,
            TAG_CITY,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_HISTORY,
            MOMENT_HERITAGE,
            MOMENT_ARCHITECTURE,
            MOMENT_EXTRAORDINARY,
        ],
        "pricing_rows": pricing(
            (285, 285, 285),
            (225, 225, 225),
            (195, 195, 195),
            (
                "Indicative TUR selling price per person in USD. "
                "Robben Island ferry and tour tickets are subject to official availability and current tariffs."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Waterfront Welcome",
                "Morning",
                "Meet at the agreed point and receive a briefing on the day's ferry timing, heritage context and guest priorities.",
            ),
            itinerary(
                "Robben Island Journey",
                "Morning / Midday",
                "Travel by ferry and participate in the official island tour, exploring the prison and wider historical context.",
            ),
            itinerary(
                "Return to the Waterfront",
                "Afternoon",
                "Return to Cape Town and take a relaxed guided walk around selected V&A Waterfront areas, harbour spaces and heritage points.",
            ),
            itinerary(
                "Waterfront Farewell",
                "Late Afternoon",
                "Conclude with time for optional shopping, a café stop or an agreed waterfront dining experience.",
            ),
        ],
        "inclusions": [
            inc(
                "Experience Coordination",
                "TUR coordination of the heritage itinerary and guest logistics.",
                "route",
            ),
            inc(
                "Local Guide Support",
                "Local host support before and after the official Robben Island tour.",
                "user",
            ),
            inc(
                "Waterfront Heritage Walk",
                "Curated interpretation of selected V&A Waterfront heritage and public spaces.",
                "landmark",
            ),
            inc(
                "Photography Stops",
                "Time for skyline, harbour and architectural photography.",
                "camera",
            ),
        ],
        "exclusions": [
            exc(
                "Robben Island Tickets",
                "Official ferry and island tour tickets are excluded unless specifically included in the final quotation.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Shopping",
                "Shopping and personal purchases at the Waterfront are excluded.",
                "shopping-bag",
            ),
        ],
        "highlights": [
            highlight(
                "Robben Island Heritage",
                "Engage with a UNESCO-listed site central to South Africa's modern history.",
                "landmark",
                "Heritage",
            ),
            highlight(
                "Layered History",
                "Connect political history, memory, place and contemporary Cape Town through guided interpretation.",
                "book-open",
                "History",
            ),
            highlight(
                "Harbour Life",
                "Experience the contrast between historic island memory and the energy of Cape Town's working waterfront.",
                "anchor",
                "City",
            ),
            highlight(
                "Mountain & Ocean Views",
                "Capture memorable views toward Table Mountain and the Atlantic from the waterfront and ferry route.",
                "camera",
                "Scenic",
            ),
        ],
        "addons": [
            addon(
                "Private Waterfront Dining",
                "Upgrade to a reserved waterfront lunch or early dinner.",
                "TUR-arranged dining reservation at a suitable V&A Waterfront venue, subject to availability.",
                90,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Expect walking on ferry terminals, the island and waterfront areas.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Sun Protection",
                "Bring sunglasses, a hat and sunscreen for outdoor sections.",
                "Weather",
                "sun",
            ),
            packing(
                "Light Jacket",
                "Ferry and waterfront conditions can be cool or windy.",
                "Clothing",
                "wind",
            ),
            packing(
                "Identification",
                "Carry the identification required by the ferry and official visitor operation.",
                "Documents",
                "id-card",
                True,
            ),
        ],
        "safety_rows": [
            safety(
                "Ferry Conditions",
                "Robben Island ferry operations are weather and sea-state dependent and may change at short notice.",
                "Marine",
                "waves",
            ),
            safety(
                "Follow Official Instructions",
                "Guests must follow Robben Island Museum, ferry and guide instructions throughout the visit.",
                "Heritage",
                "shield",
            ),
            safety(
                "Walking Pace",
                "The island and Waterfront include walking sections; guests should disclose mobility requirements in advance.",
                "Mobility",
                "footprints",
            ),
        ],
        "requirements": [
            requirement(
                "Advance Ticketing",
                "Robben Island access depends on official ticket availability; early booking is strongly recommended.",
                "Booking",
                True,
                "ticket",
            ),
            requirement(
                "Identification",
                "Guests must carry the identification required for the booked ferry/tour operation.",
                "Entry",
                True,
                "id-card",
            ),
        ],
        "faqs": [
            faq(
                "Is Robben Island guaranteed?",
                "No. Ferry and tour availability is controlled by the official operation and can be affected by weather, maintenance or capacity.",
                "Booking",
                True,
            ),
            faq(
                "How long is the ferry ride?",
                "The crossing is roughly an hour each way under normal operating conditions, with total island visit time determined by the official tour schedule.",
                "Logistics",
                False,
            ),
            faq(
                "Can children join?",
                "Yes, but the subject matter is serious and the minimum age for this TUR product is ten.",
                "Family",
                False,
            ),
            faq(
                "Can we add lunch?",
                "Yes. A private or curated Waterfront dining option can be added where availability permits.",
                "Dining",
                False,
            ),
        ],
        "wildlife_rows": [],
    },

    # =========================================================================
    # JOHANNESBURG — ID 28
    # =========================================================================

    {
        "code": "SA-JNB-001",
        "slug": "soweto-apartheid-history-heritage",
        "title": "Soweto — History, Heritage & Living Johannesburg",
        "destination_id": 28,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A locally guided Soweto journey connecting major historical "
            "landmarks, neighbourhood life and the stories that shaped modern "
            "South Africa."
        ),
        "description": (
            "Explore Soweto through a thoughtful, locally guided route that "
            "moves beyond landmark photography into the history and living "
            "character of the township. Depending on the agreed itinerary, the "
            "experience can include Vilakazi Street, the Mandela House area, "
            "Hector Pieterson Memorial and other relevant heritage points, with "
            "time for local food, craft or community-led interpretation."
        ),
        "duration": "Half Day",
        "meeting_point": (
            "Confirmed Johannesburg hotel or agreed central meeting point."
        ),
        "location": "Soweto, Johannesburg, South Africa",
        "price_from": 95,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured": True,
        "show_on_homepage": True,
        "display_order": 4,
        "meta_title": (
            "Soweto Heritage & History Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Discover Soweto's history, heritage and living culture through a locally guided private Johannesburg experience."
        ),
        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_CULTURE,
            TAG_HISTORICAL,
            TAG_CITY,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_HISTORY,
            MOMENT_HERITAGE,
            MOMENT_CULTURAL,
            MOMENT_ARCHITECTURE,
        ],
        "pricing_rows": pricing(
            (175, 175, 175),
            (135, 135, 135),
            (115, 115, 115),
            (
                "Indicative TUR selling price per person in USD. "
                "Museum and memorial admissions are quoted according to current official tariffs."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Johannesburg Departure",
                "Morning / Afternoon",
                "Meet your guide and travel into Soweto with a briefing on the day's route and historical context.",
            ),
            itinerary(
                "Vilakazi Street & Mandela Heritage",
                "Main Activity",
                "Explore the Vilakazi Street area and discuss Nelson Mandela's Johannesburg story and the wider history of Soweto.",
            ),
            itinerary(
                "Hector Pieterson & Struggle History",
                "Later Activity",
                "Visit selected memorial or museum sites according to opening hours and the agreed route, focusing on the history of the struggle against apartheid.",
            ),
            itinerary(
                "Local Perspective & Farewell",
                "Final Hour",
                "Conclude with a locally appropriate food, craft or neighbourhood stop and return to the agreed drop-off point.",
            ),
        ],
        "inclusions": [
            inc(
                "Private Vehicle & Driver",
                "Dedicated transport for the agreed Soweto route.",
                "car",
            ),
            inc(
                "Local Heritage Guide",
                "Locally informed guide support and historical interpretation.",
                "user",
            ),
            inc(
                "Curated Heritage Route",
                "A planned route linking selected historical and cultural points.",
                "route",
            ),
            inc(
                "Photography Stops",
                "Time for respectful photography at appropriate public and heritage locations.",
                "camera",
            ),
        ],
        "exclusions": [
            exc(
                "Museum Admissions",
                "Entry fees to Mandela House, Hector Pieterson Memorial or other paid sites are excluded unless specifically included.",
                "ticket",
            ),
            exc(
                "Meals & Drinks",
                "Food and drinks are excluded unless specifically included.",
                "utensils",
            ),
            exc(
                "Personal Purchases",
                "Shopping, gratuities and personal expenses are excluded.",
                "wallet",
            ),
        ],
        "highlights": [
            highlight(
                "Living History",
                "Understand Soweto through both major historical events and the community life of today.",
                "book-open",
                "History",
            ),
            highlight(
                "Vilakazi Street",
                "Visit one of the township's most significant heritage streets and connect it to the wider Johannesburg story.",
                "landmark",
                "Heritage",
            ),
            highlight(
                "Local Interpretation",
                "Learn through local guiding rather than relying only on landmark plaques and exhibits.",
                "user",
                "Culture",
            ),
            highlight(
                "Johannesburg Perspectives",
                "See how history, identity, culture and contemporary life intersect across Soweto.",
                "city",
                "City",
            ),
        ],
        "addons": [
            addon(
                "Curated Local Lunch",
                "Add a locally hosted lunch or tasting stop.",
                "TUR-arranged lunch or tasting at a suitable local venue, subject to operating hours and dietary requirements.",
                55,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Wear comfortable shoes for walking between selected heritage points.",
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
                "Water Bottle",
                "Carry drinking water for the duration of the walking sections.",
                "Hydration",
                "droplet",
            ),
            packing(
                "Respectful Clothing",
                "Dress comfortably and respectfully for community and memorial spaces.",
                "Clothing",
                "shirt",
            ),
        ],
        "safety_rows": [
            safety(
                "Follow Local Guidance",
                "Remain with the guide and follow agreed route and photography guidance throughout the experience.",
                "Community",
                "shield",
            ),
            safety(
                "Respectful Photography",
                "Ask before photographing people, private property or sensitive community activities.",
                "Photography",
                "camera",
            ),
            safety(
                "Urban Awareness",
                "Keep valuables secure and follow the guide's advice on movement and meeting points.",
                "Urban",
                "lock",
            ),
        ],
        "requirements": [
            requirement(
                "Respect Community Guidelines",
                "Guests must follow local guidance and behave respectfully within residential and heritage areas.",
                "Community",
                True,
                "heart",
            ),
            requirement(
                "Museum Timing",
                "Paid heritage stops are subject to opening hours and current admission arrangements.",
                "Booking",
                False,
                "clock",
            ),
        ],
        "faqs": [
            faq(
                "Is Soweto safe to visit?",
                "The experience uses a planned route with local guiding and transport. Guests should follow the guide's instructions and avoid independent detours.",
                "Safety",
                True,
            ),
            faq(
                "Can we visit Mandela House?",
                "Yes, where opening hours and ticket availability permit; it can be included in the agreed route.",
                "Heritage",
                False,
            ),
            faq(
                "Can we eat local food?",
                "Yes. A suitable local lunch or tasting stop can be added as an optional upgrade.",
                "Food",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Older children can participate, but the historical subject matter includes difficult themes and should be considered when booking.",
                "Family",
                False,
            ),
        ],
        "wildlife_rows": [],
    },

    {
        "code": "SA-JNB-002",
        "slug": "apartheid-museum-johannesburg-gold-reef-heritage",
        "title": "Apartheid Museum & Johannesburg — History, Memory & Modern City",
        "destination_id": 28,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A focused Johannesburg history experience centred on the Apartheid "
            "Museum and the city's wider transformation from gold-rush metropolis "
            "to modern African city."
        ),
        "description": (
            "Spend a deeply considered day engaging with Johannesburg's history "
            "through the Apartheid Museum and selected city landmarks. The "
            "experience gives guests time to absorb the museum rather than "
            "rushing through it, then connects its historical narrative to "
            "Johannesburg's changing urban landscape. Museum content is serious "
            "and can be emotionally demanding."
        ),
        "duration": "Full Day",
        "meeting_point": (
            "Confirmed Johannesburg hotel or agreed central meeting point."
        ),
        "location": "Johannesburg, South Africa",
        "price_from": 135,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 11,
        "difficulty": "Easy",
        "featured": True,
        "show_on_homepage": True,
        "display_order": 5,
        "meta_title": (
            "Apartheid Museum Johannesburg Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore Johannesburg's Apartheid Museum and urban history through a thoughtful private heritage experience."
        ),
        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_CULTURE,
            TAG_HISTORICAL,
            TAG_CITY,
            TAG_ARCHITECTURE,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_HISTORY,
            MOMENT_HERITAGE,
            MOMENT_ARCHITECTURE,
            MOMENT_EXTRAORDINARY,
        ],
        "pricing_rows": pricing(
            (215, 215, 215),
            (165, 165, 165),
            (145, 145, 145),
            (
                "Indicative TUR selling price per person in USD. "
                "Apartheid Museum admission is subject to the museum's current official tariff and operating schedule."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Johannesburg Welcome",
                "Morning",
                "Meet your guide and begin with an overview of Johannesburg's origins, growth and the historical context of the day.",
            ),
            itinerary(
                "Apartheid Museum",
                "Main Activity",
                "Allow substantial time for the museum's exhibitions and historical narrative, with optional guide-supported interpretation around the visit.",
            ),
            itinerary(
                "City Heritage Drive",
                "Afternoon",
                "Travel through selected Johannesburg districts and landmarks to connect museum history with the city's physical transformation.",
            ),
            itinerary(
                "Reflection & Farewell",
                "Late Afternoon",
                "Conclude with a quiet reflection stop or café break before returning to the agreed drop-off point.",
            ),
        ],
        "inclusions": [
            inc(
                "Private Vehicle & Driver",
                "Dedicated transport for the agreed Johannesburg route.",
                "car",
            ),
            inc(
                "Heritage Guide",
                "Experienced local guide support and contextual interpretation.",
                "user",
            ),
            inc(
                "Museum Visit Coordination",
                "TUR coordination around the museum visit and timing.",
                "ticket",
            ),
            inc(
                "City Heritage Route",
                "Curated route linking the museum to selected Johannesburg landmarks.",
                "route",
            ),
        ],
        "exclusions": [
            exc(
                "Museum Admission",
                "Apartheid Museum admission is excluded unless specifically included in the final quotation.",
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
                "Apartheid Museum",
                "Spend meaningful time with one of South Africa's most important historical museums.",
                "landmark",
                "History",
            ),
            highlight(
                "Johannesburg's Transformation",
                "Connect political history with the city's changing architecture, neighbourhoods and identity.",
                "city",
                "City",
            ),
            highlight(
                "Thoughtful Pace",
                "Allow enough time to absorb difficult historical material without rushing between attractions.",
                "clock",
                "Experience",
            ),
            highlight(
                "Private Interpretation",
                "Discuss the day's historical themes with your guide and connect them to Johannesburg today.",
                "book-open",
                "Heritage",
            ),
        ],
        "addons": [
            addon(
                "Curated Johannesburg Lunch",
                "Add a carefully selected lunch experience after the museum visit.",
                "TUR-arranged lunch at a suitable Johannesburg venue, subject to availability.",
                65,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "The experience includes walking and museum exploration.",
                "Footwear",
                "footprints",
            ),
            packing(
                "Water",
                "Carry drinking water for the day's activities.",
                "Hydration",
                "droplet",
            ),
            packing(
                "Light Layer",
                "Johannesburg weather can change during the day.",
                "Clothing",
                "wind",
            ),
            packing(
                "Identification",
                "Carry appropriate identification for ticketing and venue access where required.",
                "Documents",
                "id-card",
            ),
        ],
        "safety_rows": [
            safety(
                "Emotional Content",
                "Museum exhibitions address traumatic and difficult periods in South African history.",
                "Wellbeing",
                "heart",
            ),
            safety(
                "Urban Awareness",
                "Follow guide advice regarding movement, meeting points and personal belongings.",
                "Urban",
                "lock",
            ),
            safety(
                "Museum Rules",
                "Follow all museum photography, conduct and access rules.",
                "Heritage",
                "shield",
            ),
        ],
        "requirements": [
            requirement(
                "Age Awareness",
                "Guests should consider whether the serious historical content is appropriate for younger travellers.",
                "Family",
                True,
                "users",
            ),
            requirement(
                "Museum Timing",
                "The itinerary depends on current museum opening hours and admission arrangements.",
                "Booking",
                False,
                "clock",
            ),
        ],
        "faqs": [
            faq(
                "Is the Apartheid Museum suitable for children?",
                "Older children and teenagers may participate, but the exhibitions address serious and sometimes disturbing historical subjects.",
                "Family",
                True,
            ),
            faq(
                "How much time should we spend in the museum?",
                "TUR recommends allowing substantial time rather than rushing the visit. The exact duration depends on guest interest and museum operations.",
                "Timing",
                False,
            ),
            faq(
                "Can the experience include other Johannesburg landmarks?",
                "Yes. The city heritage portion can be tailored around available time and the guest's interests.",
                "Customisation",
                False,
            ),
            faq(
                "Can lunch be added?",
                "Yes. A curated Johannesburg lunch can be arranged as an optional upgrade.",
                "Dining",
                False,
            ),
        ],
        "wildlife_rows": [],
    },

    {
        "code": "SA-JNB-003",
        "slug": "cradle-of-humankind-maropeng-fossils-human-origins",
        "title": "Cradle of Humankind — Maropeng, Fossils & Human Origins",
        "destination_id": 28,
        "category_id": CATEGORY_ADVENTURE,
        "short_description": (
            "A full-day journey from Johannesburg into the Cradle of Humankind, "
            "combining Maropeng, human-origins interpretation and the remarkable "
            "landscapes of the UNESCO World Heritage Site."
        ),
        "description": (
            "Travel beyond Johannesburg to explore the Cradle of Humankind, one "
            "of the world's most important palaeoanthropological landscapes. "
            "The experience centres on Maropeng's human-origins interpretation "
            "and can include an agreed fossil or cave-related visit where "
            "available and appropriate. It is designed as an educational yet "
            "immersive journey connecting science, archaeology, geology and "
            "the wider African story of human origins."
        ),
        "duration": "Full Day",
        "meeting_point": (
            "Confirmed Johannesburg hotel or agreed central meeting point."
        ),
        "location": "Cradle of Humankind, Gauteng, South Africa",
        "price_from": 155,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured": True,
        "show_on_homepage": True,
        "display_order": 6,
        "meta_title": (
            "Cradle of Humankind & Maropeng Experience | The Uncharted Route"
        ),
        "meta_description": (
            "Explore the Cradle of Humankind from Johannesburg through Maropeng, fossils, archaeology and human-origins discovery."
        ),
        "cancellation_policy_id": CANCELLATION_STANDARD,
        "accessibility_profile_id": ACCESS_EASY,
        "conservation_story_id": CONSERVATION_NONE,
        "tags": [
            TAG_NATURE,
            TAG_HISTORICAL,
            TAG_CULTURE,
            TAG_PHOTOGRAPHY,
            TAG_PRIVATE,
        ],
        "moments": [
            MOMENT_HIDDEN_NATURE,
            MOMENT_HISTORY,
            MOMENT_LANDSCAPES,
            MOMENT_EXTRAORDINARY,
        ],
        "pricing_rows": pricing(
            (245, 245, 245),
            (195, 195, 195),
            (165, 165, 165),
            (
                "Indicative TUR selling price per person in USD. "
                "Maropeng, cave and specialist attraction admissions are excluded unless specifically included."
            ),
            "USD",
        ),
        "itinerary_rows": [
            itinerary(
                "Johannesburg Departure",
                "Morning",
                "Meet your guide and depart Johannesburg for the Cradle of Humankind with an introduction to the day's scientific and heritage themes.",
            ),
            itinerary(
                "Maropeng Discovery",
                "Late Morning",
                "Explore Maropeng's exhibitions and interpretation of human evolution, archaeology and the deep history of the region.",
            ),
            itinerary(
                "Fossil & Landscape Experience",
                "Afternoon",
                "Continue to an agreed cave, fossil or landscape attraction where current access and operating conditions permit.",
            ),
            itinerary(
                "Return to Johannesburg",
                "Late Afternoon",
                "Reflect on the day's discoveries and return to the agreed Johannesburg drop-off point.",
            ),
        ],
        "inclusions": [
            inc(
                "Private Vehicle & Driver",
                "Dedicated transport from Johannesburg to the Cradle of Humankind and return.",
                "car",
            ),
            inc(
                "Experience Coordination",
                "TUR coordination of the day's educational and heritage itinerary.",
                "route",
            ),
            inc(
                "Local Guide Support",
                "Guide support and interpretation throughout the agreed route.",
                "user",
            ),
            inc(
                "Landscape & Photography Stops",
                "Time for appropriate scenic and landscape photography.",
                "camera",
            ),
        ],
        "exclusions": [
            exc(
                "Attraction Admissions",
                "Maropeng, cave and other attraction entrance fees are excluded unless specifically included.",
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
                "Human Origins",
                "Explore one of the world's most important regions for understanding human evolution.",
                "book-open",
                "Science",
            ),
            highlight(
                "Maropeng",
                "Engage with exhibitions that interpret the deep history of humanity and the African continent.",
                "landmark",
                "Heritage",
            ),
            highlight(
                "Fossil Landscapes",
                "Discover the geological and palaeoanthropological significance of the wider Cradle landscape.",
                "mountain",
                "Nature",
            ),
            highlight(
                "African Story",
                "Connect scientific discovery with the broader story of humanity's origins in Africa.",
                "globe",
                "Culture",
            ),
        ],
        "addons": [
            addon(
                "Specialist Cave Visit",
                "Add a specialist cave or fossil-focused visit where access and current operating schedules permit.",
                "Additional attraction admission, specialist guiding and logistics quoted separately according to the selected site.",
                95,
                "Per person",
            ),
        ],
        "packing_rows": [
            packing(
                "Comfortable Shoes",
                "Wear comfortable footwear for museum, outdoor and potential cave-related sections.",
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
                "Cave and indoor environments can feel cooler than outdoor conditions.",
                "Clothing",
                "wind",
            ),
            packing(
                "Water Bottle",
                "Carry drinking water for the day's activities.",
                "Hydration",
                "droplet",
            ),
        ],
        "safety_rows": [
            safety(
                "Cave Conditions",
                "Any cave visit is subject to site-specific safety instructions, physical access requirements and operating conditions.",
                "Terrain",
                "mountain",
            ),
            safety(
                "Walking Sections",
                "Guests should expect some walking on museum, outdoor and attraction surfaces.",
                "Mobility",
                "footprints",
            ),
            safety(
                "Follow Site Rules",
                "Guests must follow Maropeng and attraction-specific safety and conservation instructions.",
                "Guidance",
                "shield",
            ),
        ],
        "requirements": [
            requirement(
                "Comfortable Mobility",
                "Guests should be comfortable with moderate walking during the educational and outdoor sections.",
                "Mobility",
                True,
                "footprints",
            ),
            requirement(
                "Attraction Availability",
                "Specialist cave or fossil visits depend on current opening hours, access rules and availability.",
                "Booking",
                False,
                "clock",
            ),
        ],
        "faqs": [
            faq(
                "What is the Cradle of Humankind?",
                "It is a UNESCO World Heritage Site in Gauteng known for important palaeoanthropological discoveries and fossil-bearing cave systems.",
                "Heritage",
                True,
            ),
            faq(
                "Will we see actual fossils?",
                "The experience includes fossil and human-origins interpretation, while access to specific fossil sites or specialist collections depends on current operations.",
                "Science",
                False,
            ),
            faq(
                "Is this suitable for children?",
                "Yes. It is particularly suitable for curious older children and teenagers interested in science, archaeology and history.",
                "Family",
                False,
            ),
            faq(
                "Can we add a specialist cave visit?",
                "Yes, where the selected site is open and appropriate for the guest group.",
                "Customisation",
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
        db.session.add(model(**set_supported_fields(model, payload)))


def ordered(rows):
    result = []
    for index, row in enumerate(rows, 1):
        item = dict(row)
        item["display_order"] = index
        result.append(item)
    return result


def validate_reusable_cms(data):
    category = db.session.get(ExperienceCategory, data["category_id"])
    destination = db.session.get(Destination, data["destination_id"])
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
            f"Missing ExperienceCategory ID {data['category_id']} "
            f"for {data['code']}"
        )

    if not destination:
        raise ValueError(
            f"Missing Destination ID {data['destination_id']} "
            f"for {data['code']}"
        )

    if not cancellation:
        raise ValueError(
            f"Missing CancellationPolicy ID "
            f"{data['cancellation_policy_id']} for {data['code']}"
        )

    if not accessibility:
        raise ValueError(
            f"Missing Accessibility ID "
            f"{data['accessibility_profile_id']} for {data['code']}"
        )

    for tag_id in data["tags"]:
        if not db.session.get(ExperienceTag, tag_id):
            raise ValueError(
                f"Missing ExperienceTag ID {tag_id} for {data['code']}"
            )

    for moment_id in data["moments"]:
        if not db.session.get(SignatureMoment, moment_id):
            raise ValueError(
                f"Missing SignatureMoment ID {moment_id} for {data['code']}"
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
            f"Duplicate protection triggered for {data['code']} "
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
                f"{key} expected {expected_count}, got {actual_count}"
            )

    if experience.media.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: media must be 0"
        )

    if experience.schedules.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: schedules must be 0"
        )

    if experience.bookings.count() != 0:
        raise ValueError(
            f"Verification failed for {data['code']}: bookings must be 0"
        )


# =============================================================================
# APPLICATION
# =============================================================================

def main():
    app = create_app()

    with app.app_context():
        print("\n" + "=" * 110)
        print(
            "THE UNCHARTED ROUTE — BATCH 4: SOUTHERN AFRICA"
        )
        print("=" * 110)
        print(f"Experiences in batch: {len(EXPERIENCES)}")
        print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
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
            for batch_index, data in enumerate(EXPERIENCES, 1):
                destination = db.session.get(
                    Destination,
                    data["destination_id"],
                )

                print(
                    f"\n[{batch_index:02d}/{len(EXPERIENCES)}] "
                    f"{data['code']} — {data['title']}"
                )
                print(
                    f"    Destination ID: {data['destination_id']} | "
                    f"Destination active: {destination.active}"
                )
                print(
                    f"    Itinerary: {len(data['itinerary_rows'])} | "
                    f"Inclusions: {len(data['inclusions'])} | "
                    f"Exclusions: {len(data['exclusions'])} | "
                    f"Highlights: {len(data['highlights'])}"
                )
                print(
                    f"    Pricing: {len(data['pricing_rows'])} | "
                    f"Add-ons: {len(data['addons'])} | "
                    f"Packing: {len(data['packing_rows'])} | "
                    f"Safety: {len(data['safety_rows'])}"
                )
                print(
                    f"    Requirements: {len(data['requirements'])} | "
                    f"FAQs: {len(data['faqs'])} | "
                    f"Tags: {len(data['tags'])} | "
                    f"Signature moments: {len(data['moments'])} | "
                    f"Wildlife: {len(data['wildlife_rows'])}"
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
                        db.session.get(ExperienceTag, tag_id)
                        for tag_id in data["tags"]
                    ]
                )

                experience.signature_moments.extend(
                    [
                        db.session.get(SignatureMoment, moment_id)
                        for moment_id in data["moments"]
                    ]
                )

                add_children(
                    ExperienceItinerary,
                    experience.id,
                    [
                        {**record, "display_order": index}
                        for index, record in enumerate(
                            data["itinerary_rows"],
                            1,
                        )
                    ],
                )

                add_children(
                    ExperienceInclusion,
                    experience.id,
                    ordered(data["inclusions"]),
                )

                add_children(
                    ExperienceExclusion,
                    experience.id,
                    ordered(data["exclusions"]),
                )

                add_children(
                    ExperienceHighlight,
                    experience.id,
                    ordered(data["highlights"]),
                )

                add_children(
                    ExperiencePricing,
                    experience.id,
                    ordered(data["pricing_rows"]),
                )

                add_children(
                    ExperienceAddon,
                    experience.id,
                    ordered(data["addons"]),
                )

                add_children(
                    ExperiencePackingItem,
                    experience.id,
                    ordered(data["packing_rows"]),
                )

                add_children(
                    ExperienceSafetyRule,
                    experience.id,
                    ordered(data["safety_rows"]),
                )

                add_children(
                    ExperienceRequirement,
                    experience.id,
                    ordered(data["requirements"]),
                )

                add_children(
                    ExperienceFAQ,
                    experience.id,
                    ordered(data["faqs"]),
                )

                # Wildlife is deliberately empty for these six experiences.
                # We do not attach unrelated Kenya wildlife species.
                created.append(experience)

            db.session.flush()

            # -----------------------------------------------------------------
            # Verification
            # -----------------------------------------------------------------
            print("\n" + "=" * 110)
            print("BATCH VERIFICATION")
            print("=" * 110)

            for experience, data in zip(created, EXPERIENCES):
                verify_experience(experience, data)

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
                print("BATCH 4 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(
                    "Created 6 complete Southern Africa experiences."
                )
                print(
                    "Cape Town and Johannesburg remain active."
                )
            else:
                db.session.rollback()

                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)
                print(
                    "Validated 6 complete Southern Africa experiences."
                )
                print(
                    "No database changes were committed."
                )
                print(
                    "Run with --apply only after reviewing the dry-run output."
                )

        except Exception as exc:
            db.session.rollback()

            print("\n" + "=" * 110)
            print("BATCH FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)
            print(f"{type(exc).__name__}: {exc}")
            print(
                "No database changes were committed."
            )

            raise


if __name__ == "__main__":
    main()