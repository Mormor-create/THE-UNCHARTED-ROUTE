"""
===============================================================================
THE UNCHARTED ROUTE
BATCH 1 — KENYAN COAST EXPERIENCE POPULATION
===============================================================================

Destinations:
    Watamu        ID 7
    Mombasa       ID 8
    Lamu Old Town ID 9
    Diani         ID 25
    Malindi       ID 17 (currently INACTIVE; remains inactive)

This script creates the complete CMS/content structure for the approved
Kenyan Coast experience batch.

IMPORTANT:
    - Existing experiences are NEVER modified.
    - Existing CMS records are NEVER duplicated.
    - No media associations are created.
    - No schedules are created.
    - No bookings are created.
    - Inactive destinations remain inactive.
    - Experiences themselves are created active so they are ready when the
      destination is activated.
    - DEFAULT: dry run.
    - APPLY: python scripts/populate_kenyan_coast_batch.py --apply

The batch is transactional. Any error rolls the entire batch back.
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
    ExperienceWildlife,
    WildlifeSpecies,
)


# =============================================================================
# SHARED CMS IDS
# =============================================================================

CATEGORY_COASTAL = 4
CATEGORY_CULTURE = 3
CATEGORY_CULINARY = 9

CANCELLATION_POLICY_ID = 2
ACCESSIBILITY_PROFILE_ID = 5

TAG_WILDLIFE = 1
TAG_CONSERVATION = 2
TAG_PHOTOGRAPHY = 4
TAG_NAIROBI = 5
TAG_HALF_DAY = 6
TAG_CULTURE = 12
TAG_COASTAL = 13
TAG_CULINARY = 14
TAG_NATURE = 17
TAG_HISTORICAL = 19
TAG_ARCHITECTURE = 20
TAG_LOCAL_CRAFTS = 21
TAG_FOOD = 22
TAG_PRIVATE = 30

MOMENT_HERITAGE = 12
MOMENT_ARTISANS = 13
MOMENT_TRADITION = 14
MOMENT_FARM_TABLE = 17
MOMENT_COFFEE = 18
MOMENT_LOCAL_CUISINE = 19
MOMENT_RECIPE = 20
MOMENT_MARINE_LIFE = 24
MOMENT_OCEAN_VIEW = 25
MOMENT_HIDDEN_GEMS = 26
MOMENT_MARKET = 27
MOMENT_EXTRAORDINARY_ESCAPE = 30

CONSERVATION_TURTLES = 6
CONSERVATION_CORAL = 7


# =============================================================================
# HELPERS
# =============================================================================

def ordered(records):
    result = []
    for index, record in enumerate(records, 1):
        item = dict(record)
        item["display_order"] = index
        item["active"] = True
        result.append(item)
    return result


def itinerary(title, time, description):
    return {
        "day_number": 1,
        "title": title,
        "activity_time": time,
        "description": description,
    }


def pricing(explorer, signature, luxury, notes):
    return [
        {
            "minimum_people": 1,
            "maximum_people": 1,
            "experience_level": "Explorer",
            "price": explorer[0],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 1,
            "maximum_people": 1,
            "experience_level": "Signature",
            "price": explorer[1],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 1,
            "maximum_people": 1,
            "experience_level": "Luxury",
            "price": explorer[2],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 2,
            "maximum_people": 3,
            "experience_level": "Explorer",
            "price": signature[0],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 2,
            "maximum_people": 3,
            "experience_level": "Signature",
            "price": signature[1],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 2,
            "maximum_people": 3,
            "experience_level": "Luxury",
            "price": signature[2],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 4,
            "maximum_people": None,
            "experience_level": "Explorer",
            "price": luxury[0],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 4,
            "maximum_people": None,
            "experience_level": "Signature",
            "price": luxury[1],
            "currency": "KES",
            "notes": notes,
        },
        {
            "minimum_people": 4,
            "maximum_people": None,
            "experience_level": "Luxury",
            "price": luxury[2],
            "currency": "KES",
            "notes": notes,
        },
    ]


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


def highlight(title, description, icon, highlight_type="Experience"):
    return {
        "title": title,
        "description": description,
        "icon": icon,
        "highlight_type": highlight_type,
        "featured": False,
    }


def addon(name, short_description, description, price, pricing_type):
    return {
        "name": name,
        "short_description": short_description,
        "description": description,
        "price": price,
        "currency": "KES",
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


def safety(title, description, category="General", icon="shield"):
    return {
        "title": title,
        "description": description,
        "category": category,
        "icon": icon,
    }


def requirement(title, description, category="General", mandatory=False, icon="info"):
    return {
        "title": title,
        "description": description,
        "category": category,
        "mandatory": mandatory,
        "icon": icon,
    }


def faq(question, answer, category="Booking", featured=False):
    return {
        "question": question,
        "answer": answer,
        "category": category,
        "featured": featured,
    }


def wildlife(species_id, probability, season, time, notes):
    return {
        "species_id": species_id,
        "sighting_probability": probability,
        "best_season": season,
        "best_time_of_day": time,
        "guide_notes": notes,
        "photography_notes": "",
        "featured": False,
    }


# =============================================================================
# EXPERIENCE DATA
# =============================================================================

EXPERIENCES = [
    {
        "code": "COA-WAT-001",
        "slug": "watamu-marine-discovery",
        "title": "Watamu Marine Discovery — Dhow, Reef & Sandbank",
        "destination_id": 7,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A private coastal day exploring Watamu's marine landscape by boat, "
            "with reef viewing, optional snorkelling and time on a sandbank."
        ),
        "description": (
            "Discover Watamu from the water on a carefully arranged marine "
            "experience combining traditional dhow travel, reef exploration "
            "and time on the coast. Depending on sea conditions, the route may "
            "include snorkelling, shallow-water reef viewing and a sandbank "
            "stop. Your host will adapt the outing to weather, tides, sea "
            "conditions and the agreed operating plan. Marine wildlife such as "
            "dolphins, turtles, rays and reef fish may be encountered, but "
            "sightings are never guaranteed."
        ),
        "duration": "Full Day",
        "meeting_point": (
            "Designated Watamu marine departure point; private pickup from the "
            "guest's hotel, Airbnb or agreed accommodation is confirmed after booking."
        ),
        "location": "Watamu, Kilifi County, Kenya",
        "price_from": 11500,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "watamu-marine-discovery",
        "banner_image": None,
        "meta_title": "Watamu Marine Discovery | The Uncharted Route",
        "meta_description": (
            "Explore Watamu by dhow with reef viewing, optional snorkelling, "
            "sandbank time and a private coastal experience."
        ),
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 1,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": CONSERVATION_CORAL,
        "tags": [TAG_COASTAL, TAG_NATURE, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_OCEAN_VIEW, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (18500, 25500, 39500),
            (14500, 20500, 31500),
            (11500, 16500, 25500),
            "Indicative TUR selling price per person. Final supplier, park, boat and seasonal charges must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Private Pickup & Coastal Departure", "Morning", "Collect guests from the agreed accommodation and transfer to the designated marine departure point. Meet the boat crew and receive a safety briefing before departure."),
            itinerary("Dhow Cruise & Marine Exploration", "Morning", "Travel along the Watamu coast while the guide introduces the marine environment, reef systems and coastal landscape. The route is adjusted to sea and weather conditions."),
            itinerary("Reef Viewing, Snorkelling & Sandbank", "Late Morning–Afternoon", "Where conditions permit, enjoy reef viewing and optional snorkelling followed by time at an appropriate sandbank or coastal stop. Marine wildlife sightings are possible but not guaranteed."),
            itinerary("Return & Drop-Off", "Afternoon", "Return to the departure point and transfer guests back to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Private Experience Coordination", "TUR coordination of the confirmed pickup, boat arrangement and experience schedule.", "route"),
            inc("Marine Guide / Crew", "Local boat crew and marine guidance according to the confirmed supplier arrangement.", "user"),
            inc("Boat Excursion", "Boat travel for the agreed Watamu marine route.", "ship"),
            inc("Safety Briefing", "Operational and marine safety briefing before departure.", "shield"),
            inc("Snorkelling Equipment", "Basic snorkelling equipment where included by the confirmed supplier and suitable for the day's conditions.", "water"),
        ],
        "exclusions": [
            exc("Park or Marine Conservation Fees", "Applicable protected-area entry or conservation fees unless explicitly included in the booking confirmation.", "ticket"),
            exc("Meals & Drinks", "Meals, snacks and drinks unless specifically stated in the confirmed package.", "utensils"),
            exc("Personal Expenses", "Personal purchases, gratuities and other incidental expenses.", "wallet"),
            exc("Guaranteed Wildlife Sightings", "Marine wildlife encounters depend on natural conditions and are never guaranteed.", "binoculars"),
        ],
        "highlights": [
            highlight("Traditional Dhow Journey", "Travel along the Watamu coast by boat and experience the landscape from the water.", "ship", "Signature"),
            highlight("Reef Exploration", "Explore Watamu's reef environment through viewing and, where conditions permit, snorkelling.", "water", "Nature"),
            highlight("Sandbank Escape", "Enjoy time at an appropriate sandbank or coastal stop subject to tides and conditions.", "sun", "Coastal"),
            highlight("Marine Wildlife Possibilities", "Dolphins, turtles, rays and reef fish may be encountered, but sightings are not guaranteed.", "fish", "Wildlife"),
        ],
        "addons": [
            addon("Private Premium Boat Upgrade", "Upgrade the boat arrangement for a more exclusive outing.", "A premium private boat arrangement may be added subject to vessel availability, route and supplier confirmation.", 12000, "Per Booking"),
            addon("Private Coastal Lunch", "Add a pre-arranged coastal lunch.", "A lunch arrangement can be added where the selected supplier and route support it. Menu and location must be confirmed before booking.", 4500, "Per Person"),
        ],
        "packing": [
            packing("Swimwear", "Bring swimwear if you plan to enter the water.", "Clothing", "swim"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat suitable for strong coastal sun.", "Health", "sun"),
            packing("Water Shoes", "Water shoes can be useful around rocky or reef areas.", "Footwear", "shoe"),
            packing("Dry Bag", "Protect phones, cameras and other valuables from spray and water.", "Equipment", "bag"),
            packing("Drinking Water", "Carry drinking water and confirm whether bottled water is included in your package.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Follow Marine Crew Instructions", "Remain attentive to the boat crew's instructions during boarding, cruising, swimming and snorkelling.", "Marine Safety", "shield"),
            safety("Sea Conditions Can Change", "The route may be shortened, changed or rescheduled when tides, weather or sea conditions make the planned activity unsuitable.", "Weather", "cloud"),
            safety("Swimming Ability", "Guests entering the water should be comfortable with the agreed water activity and follow guide instructions. Non-swimmers must notify the host before departure.", "Water", "life-buoy"),
            safety("Wildlife Distance", "Never approach, feed or attempt to touch marine wildlife.", "Wildlife", "fish"),
        ],
        "requirements": [
            requirement("Confirmed Pickup Location", "Provide the accommodation name and location when booking so the pickup arrangement can be confirmed.", "Booking", True, "map-pin"),
            requirement("Punctuality", "Be ready at the confirmed pickup point at the agreed time.", "General", True, "clock"),
            requirement("Water Activity Disclosure", "Tell the host in advance about swimming limitations, mobility needs or other requirements affecting water activities.", "Health", False, "info"),
        ],
        "faqs": [
            faq("Are dolphins guaranteed?", "No. Dolphins and other marine wildlife are wild animals, so sightings depend on natural behaviour, season, tides, weather and location.", "Wildlife", True),
            faq("Is pickup included?", "Pickup is coordinated from the guest's hotel, Airbnb or other agreed accommodation within the applicable service area, subject to the confirmed package.", "Transport", True),
            faq("Is snorkelling always possible?", "No. Snorkelling depends on sea conditions, weather, tides, safety considerations and the confirmed route.", "Activity"),
            faq("Are marine park fees included?", "Only if the booking confirmation specifically states that applicable park or conservation fees are included.", "Fees"),
            faq("What happens if the sea is rough?", "The route may be adjusted, shortened, postponed or replaced with an alternative arrangement where operationally possible.", "Weather"),
        ],
    },

    {
        "code": "COA-WAT-002",
        "slug": "mida-creek-mangrove-canoe",
        "title": "Mida Creek — Mangrove, Canoe & Coastal Dining",
        "destination_id": 7,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A guided Mida Creek experience combining mangrove exploration, "
            "canoe travel, coastal ecology and an optional local dining moment."
        ),
        "description": (
            "Slow down beside Mida Creek and discover the relationship between "
            "mangrove forests, tidal waters, birdlife and coastal communities. "
            "The experience combines guided interpretation with canoe or boat "
            "exploration and can be extended with a locally inspired meal. "
            "The exact route and timing depend on tides, weather and the "
            "confirmed operating arrangement."
        ),
        "duration": "Half Day",
        "meeting_point": "Mida Creek departure point; accommodation pickup is confirmed after booking.",
        "location": "Mida Creek, Watamu, Kilifi County, Kenya",
        "price_from": 8000,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",
        "featured_image": "mida-creek-mangrove-canoe",
        "banner_image": None,
        "meta_title": "Mida Creek Mangrove & Canoe Experience | The Uncharted Route",
        "meta_description": "Explore Mida Creek's mangroves by canoe and discover coastal ecology and local traditions.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 2,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_COASTAL, TAG_NATURE, TAG_PHOTOGRAPHY],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_OCEAN_VIEW, MOMENT_HIDDEN_GEMS],
        "pricing": pricing(
            (12500, 18500, 28500),
            (10000, 15000, 23000),
            (8000, 12000, 18500),
            "Indicative TUR selling price per person. Final supplier and dining arrangements must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Mida Creek Introduction", "Morning / Afternoon", "Collect guests from the agreed accommodation and travel to the Mida Creek departure point. Meet the local guide and receive an introduction to the creek ecosystem."),
            itinerary("Mangrove & Canoe Exploration", "Main Activity", "Explore the creek by canoe or agreed boat while learning about mangroves, tidal systems, coastal plants and birdlife."),
            itinerary("Local Coastal Dining", "Optional / Afternoon", "Where included in the selected package, enjoy a locally inspired meal or refreshments in an appropriate coastal setting."),
            itinerary("Return to Accommodation", "Late Afternoon", "Conclude the creek experience and transfer guests back to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Pickup from the guest's agreed accommodation within the service area.", "car"),
            inc("Local Guide", "Guided interpretation of Mida Creek's mangrove and coastal environment.", "user"),
            inc("Canoe / Boat Experience", "Canoe or boat arrangement according to the confirmed supplier package.", "ship"),
            inc("Safety Briefing", "Basic water and activity safety briefing.", "shield"),
        ],
        "exclusions": [
            exc("Meals Unless Selected", "Food and drinks are excluded unless the selected package explicitly includes dining.", "utensils"),
            exc("Personal Purchases", "Personal purchases and gratuities are excluded.", "wallet"),
            exc("Private Vehicle Upgrade", "A premium private vehicle arrangement is excluded unless specifically selected.", "car"),
        ],
        "highlights": [
            highlight("Mangrove Ecology", "Understand how mangroves protect coastal environments and support marine life.", "leaf", "Nature"),
            highlight("Canoe Exploration", "Travel through the creek at a slower pace that allows close observation of the landscape.", "ship", "Adventure"),
            highlight("Birdwatching Possibilities", "Mida Creek is an important coastal habitat where a variety of birdlife may be encountered.", "bird", "Wildlife"),
            highlight("Local Coastal Flavours", "Add a locally inspired dining moment to deepen the cultural experience.", "utensils", "Culinary"),
        ],
        "addons": [
            addon("Swahili Coastal Lunch", "Add a pre-arranged local lunch.", "A locally inspired meal can be added subject to the selected supplier, menu and availability.", 3500, "Per Person"),
        ],
        "packing": [
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Light Clothing", "Wear light, comfortable clothing suitable for warm coastal weather.", "Clothing", "shirt"),
            packing("Insect Repellent", "Consider insect repellent, particularly around mangrove areas.", "Health", "bug"),
            packing("Waterproof Bag", "Protect electronics and valuables from water and spray.", "Equipment", "bag"),
        ],
        "safety": [
            safety("Follow the Guide", "Follow the local guide's instructions while boarding, paddling and moving around the creek.", "Water Safety", "shield"),
            safety("Tidal Conditions", "Routes and timing may change according to tides and weather.", "Weather", "cloud"),
            safety("Mangrove Terrain", "Do not leave the agreed route or enter sensitive mangrove areas without the guide.", "Environment", "leaf"),
        ],
        "requirements": [
            requirement("Pickup Details", "Provide the accommodation location when booking so the pickup can be coordinated.", "Booking", True, "map-pin"),
            requirement("Punctuality", "Be ready at the confirmed pickup time.", "General", True, "clock"),
        ],
        "faqs": [
            faq("Is the canoe suitable for beginners?", "The experience is designed for ordinary leisure paddling, but the final activity arrangement depends on the selected supplier and prevailing conditions.", "Activity", True),
            faq("Will we see birds?", "Birdlife may be encountered, but sightings are not guaranteed because wildlife moves freely through the creek.", "Wildlife", True),
            faq("Can we add lunch?", "Yes. A local dining arrangement can be added where available and confirmed before booking.", "Dining"),
            faq("What happens during bad weather?", "The route may be adjusted or rescheduled when conditions make the activity unsafe.", "Weather"),
        ],
    },

    {
        "code": "COA-WAT-003",
        "slug": "watamu-ocean-guardians-turtle-conservation",
        "title": "Ocean Guardians — Watamu Turtle Conservation Discovery",
        "destination_id": 7,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A conservation-led visit exploring turtle rehabilitation, marine "
            "education and the work behind protecting Watamu's coastal ecosystem."
        ),
        "description": (
            "Visit Watamu's marine conservation community to learn how turtles "
            "and their habitat are protected, rehabilitated and returned to the "
            "ocean when ready. The experience focuses on education rather than "
            "guaranteed wildlife encounters. Rehabilitation turtles may not be "
            "present at the time of the visit because recovered animals are "
            "released when ready."
        ),
        "duration": "Half Day",
        "meeting_point": "Local Ocean Conservation visitor facility; accommodation pickup is confirmed after booking.",
        "location": "Watamu, Kilifi County, Kenya",
        "price_from": 6500,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 6,
        "difficulty": "Easy",
        "featured_image": "watamu-ocean-guardians-turtle-conservation",
        "banner_image": None,
        "meta_title": "Watamu Turtle Conservation Experience | The Uncharted Route",
        "meta_description": "Discover turtle rehabilitation and marine conservation in Watamu with a guided educational visit.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 3,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": CONSERVATION_TURTLES,
        "tags": [TAG_COASTAL, TAG_CONSERVATION, TAG_NATURE],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_HIDDEN_GEMS, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (9500, 13500, 21500),
            (8000, 11500, 18000),
            (6500, 9500, 15000),
            "Indicative TUR selling price per person. Conservation contribution and supplier terms must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Arrival", "Morning / Afternoon", "Collect guests from the agreed accommodation and travel to the conservation facility."),
            itinerary("Marine Conservation Introduction", "Main Activity", "Meet the conservation team or guide and learn about local marine ecosystems, threats to turtles and the role of rehabilitation."),
            itinerary("Rehabilitation & Education Visit", "Main Activity", "Explore the visitor areas and learn about turtle rescue, treatment and release processes. Rehabilitation turtles are not guaranteed to be present."),
            itinerary("Reflection & Return", "Late Afternoon", "Conclude the educational visit and return guests to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Private pickup coordination from the guest's agreed accommodation.", "car"),
            inc("Conservation Visit", "Access to the confirmed conservation education experience.", "leaf"),
            inc("Guided Interpretation", "Conservation interpretation and educational guidance.", "user"),
            inc("Conservation Contribution", "The confirmed supplier or conservation contribution where included in the final package.", "heart"),
        ],
        "exclusions": [
            exc("Guaranteed Turtle Sightings", "Turtles are wild animals and rehabilitation animals may be absent because recovered animals are released.", "fish"),
            exc("Meals & Drinks", "Meals and drinks are excluded unless explicitly included in the confirmed booking.", "utensils"),
            exc("Personal Purchases", "Souvenirs, donations beyond the included contribution and personal expenses are excluded.", "wallet"),
        ],
        "highlights": [
            highlight("Turtle Rehabilitation", "Understand the work involved in rescuing, rehabilitating and releasing sea turtles.", "fish", "Conservation"),
            highlight("Marine Education", "Learn how coastal ecosystems and human activity affect marine wildlife.", "leaf", "Education"),
            highlight("Conservation in Action", "See how local conservation work connects education, community participation and marine protection.", "heart", "Conservation"),
        ],
        "addons": [],
        "packing": [
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Comfortable Shoes", "Wear comfortable shoes suitable for a short educational visit.", "Footwear", "shoe"),
            packing("Water", "Carry drinking water.", "General", "bottle-water"),
            packing("Camera", "A camera may be brought where photography is permitted by the facility.", "Electronics", "camera"),
        ],
        "safety": [
            safety("Do Not Touch Wildlife", "Never touch, feed or interfere with turtles or other marine animals unless specifically instructed by authorised conservation staff.", "Wildlife", "fish"),
            safety("Follow Facility Rules", "Follow all conservation facility instructions, visitor restrictions and photography rules.", "Conservation", "shield"),
            safety("Respect Release Protocols", "Do not obstruct or interfere with turtle rehabilitation or release activities.", "Conservation", "leaf"),
        ],
        "requirements": [
            requirement("Confirmed Pickup Details", "Provide accommodation details for pickup coordination.", "Booking", True, "map-pin"),
            requirement("Respect Conservation Rules", "Guests must follow conservation staff instructions throughout the visit.", "Conservation", True, "shield"),
        ],
        "faqs": [
            faq("Will we definitely see turtles?", "No. Rehabilitation turtles may not be present because healthy recovered turtles are released when ready. Wildlife sightings are never guaranteed.", "Wildlife", True),
            faq("Is this a wildlife viewing experience?", "It is primarily an educational conservation experience. It should not be marketed as a guaranteed wildlife encounter.", "Experience", True),
            faq("Is the conservation contribution included?", "The final booking confirmation will state exactly which conservation or visitor fees are included.", "Fees"),
            faq("Can children participate?", "Children can participate when accompanied by a responsible adult and subject to the facility's current visitor requirements.", "Family"),
        ],
    },

    {
        "code": "COA-MSA-001",
        "slug": "mombasa-heritage-old-town-fort-jesus",
        "title": "Mombasa Heritage Journey — Old Town & Fort Jesus",
        "destination_id": 8,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A guided heritage journey through Mombasa Old Town and Fort Jesus, "
            "exploring Swahili architecture, history and living coastal culture."
        ),
        "description": (
            "Walk through the layered history of Mombasa, beginning around Fort "
            "Jesus and continuing through the narrow streets, carved doors, "
            "historic buildings and living neighbourhoods of Old Town. Your "
            "guide brings together Portuguese, Arab, Swahili, Indian and modern "
            "coastal influences while allowing time for architecture, local "
            "stories and optional market exploration."
        ),
        "duration": "Half Day",
        "meeting_point": "Fort Jesus / Mombasa Old Town area; private accommodation pickup is confirmed after booking.",
        "location": "Mombasa Old Town, Mombasa County, Kenya",
        "price_from": 7500,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "mombasa-heritage-old-town-fort-jesus",
        "banner_image": None,
        "meta_title": "Mombasa Old Town & Fort Jesus Heritage Experience",
        "meta_description": "Explore Mombasa Old Town and Fort Jesus with a private guided heritage experience.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 4,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_CULTURE, TAG_HISTORICAL, TAG_ARCHITECTURE, TAG_LOCAL_CRAFTS, TAG_PRIVATE],
        "moments": [MOMENT_HERITAGE, MOMENT_TRADITION, MOMENT_HIDDEN_GEMS, MOMENT_MARKET],
        "pricing": pricing(
            (11500, 16500, 25500),
            (9500, 14000, 21500),
            (7500, 11000, 17500),
            "Indicative TUR selling price per person. Fort Jesus admission and other attraction fees are excluded unless the confirmed package states otherwise."
        ),
        "itinerary": [
            itinerary("Pickup & Heritage Introduction", "Morning / Afternoon", "Collect guests from the agreed accommodation and introduce the historical context of Mombasa's coastal trading city."),
            itinerary("Fort Jesus", "Main Activity", "Explore Fort Jesus with guided interpretation of its architecture, history and role in the Indian Ocean world."),
            itinerary("Old Town Walking Journey", "Main Activity", "Walk through Old Town's historic streets, architecture, carved doors and living cultural spaces."),
            itinerary("Local Flavours & Optional Market Stop", "Late Afternoon", "Where selected, pause for a local refreshment or market exploration before returning to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Private Pickup Coordination", "Pickup and drop-off coordination from the guest's agreed accommodation within the service area.", "car"),
            inc("Local Heritage Guide", "Guided interpretation throughout the Old Town and heritage experience.", "user"),
            inc("Walking Heritage Experience", "Curated walking route through the historic Old Town.", "walk"),
            inc("Experience Coordination", "TUR coordination of the confirmed itinerary and supplier arrangements.", "route"),
        ],
        "exclusions": [
            exc("Fort Jesus Admission", "Fort Jesus admission is excluded unless specifically included in the confirmed package.", "ticket"),
            exc("Meals & Drinks", "Meals and drinks are excluded unless explicitly included.", "utensils"),
            exc("Shopping", "Purchases from markets, galleries, craft sellers and other vendors are paid directly by guests.", "shopping-bag"),
            exc("Personal Expenses", "Gratuities and personal purchases are excluded.", "wallet"),
        ],
        "highlights": [
            highlight("Fort Jesus", "Explore one of Mombasa's defining historic landmarks with guided interpretation.", "landmark", "Heritage"),
            highlight("Swahili Architecture", "Discover carved doors, courtyards and architectural details throughout Old Town.", "building", "Architecture"),
            highlight("Living Coastal Culture", "Experience Old Town as a living neighbourhood rather than only a historic monument.", "users", "Culture"),
            highlight("Local Stories", "Hear stories connecting Mombasa to centuries of Indian Ocean trade and cultural exchange.", "book", "Heritage"),
        ],
        "addons": [
            addon("Swahili Coastal Tasting", "Add a guided tasting of selected local flavours.", "A short tasting arrangement can be added subject to supplier availability and venue confirmation.", 2500, "Per Person"),
        ],
        "packing": [
            packing("Comfortable Walking Shoes", "Wear comfortable shoes suitable for walking on uneven historic streets.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Modest Clothing", "Wear respectful clothing appropriate for visiting historic religious and residential areas.", "Clothing", "shirt"),
            packing("Water", "Carry drinking water, especially during warmer periods.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Stay With the Guide", "Remain with the guide in busy streets and follow agreed meeting points.", "General", "users"),
            safety("Secure Valuables", "Keep phones, cameras, wallets and other valuables secure in crowded areas.", "Personal Safety", "lock"),
            safety("Respect Local Communities", "Ask before photographing people, businesses or private spaces.", "Cultural Respect", "camera"),
        ],
        "requirements": [
            requirement("Punctuality", "Be ready at the confirmed pickup point at the agreed time.", "General", True, "clock"),
            requirement("Respectful Dress", "Guests should dress respectfully when entering religious or culturally sensitive spaces.", "Culture", True, "shirt"),
        ],
        "faqs": [
            faq("Is Fort Jesus entry included?", "Not automatically. The booking confirmation will state whether admission is included in your selected package.", "Fees", True),
            faq("Is this a private tour?", "The standard TUR structure is designed around a private guest experience, subject to the final supplier arrangement.", "Booking", True),
            faq("Can we shop in Old Town?", "Yes. Shopping can be incorporated where practical, but purchases are paid directly by the guest.", "Shopping"),
            faq("Is the walking difficult?", "The route is generally easy but includes uneven streets, steps and periods of walking in warm weather.", "Accessibility"),
        ],
    },

    {
        "code": "COA-MSA-002",
        "slug": "haller-park-conservation-experience",
        "title": "Haller Park — Conservation & Wildlife Encounter",
        "destination_id": 8,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A guided nature experience through Haller Park combining wildlife, "
            "botanical landscapes, conservation learning and birdwatching."
        ),
        "description": (
            "Explore Haller Park's rehabilitated quarry landscape and discover "
            "how an industrial site was transformed into a thriving ecological "
            "space. The experience can include guided nature walks, botanical "
            "areas, birdwatching and scheduled wildlife interactions where "
            "available. Animal sightings and specific wildlife encounters are "
            "not guaranteed."
        ),
        "duration": "Half Day",
        "meeting_point": "Haller Park visitor entrance; accommodation pickup is confirmed after booking.",
        "location": "Bamburi, Mombasa County, Kenya",
        "price_from": 8000,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 6,
        "difficulty": "Easy",
        "featured_image": "haller-park-conservation-experience",
        "banner_image": None,
        "meta_title": "Haller Park Conservation Experience | The Uncharted Route",
        "meta_description": "Discover Haller Park's wildlife, botanical landscapes and conservation story near Mombasa.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 5,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_CONSERVATION, TAG_NATURE, TAG_PHOTOGRAPHY],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_HIDDEN_GEMS, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (12500, 17500, 27500),
            (10000, 14500, 22500),
            (8000, 12000, 18500),
            "Indicative TUR selling price per person. Park admission and supplier-guided components must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Arrival", "Morning / Afternoon", "Collect guests from the agreed accommodation and travel to Haller Park."),
            itinerary("Guided Nature & Conservation Walk", "Main Activity", "Explore the park's rehabilitated landscape and learn how conservation, habitat restoration and wildlife management are connected."),
            itinerary("Wildlife & Botanical Areas", "Main Activity", "Visit selected wildlife, botanical and birdwatching areas according to the day's operational programme."),
            itinerary("Return Journey", "Afternoon", "Conclude the visit and return guests to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Pickup coordination from the guest's agreed accommodation.", "car"),
            inc("Guided Park Experience", "Guided interpretation of Haller Park's conservation and natural environment.", "leaf"),
            inc("Experience Coordination", "TUR coordination of the confirmed park itinerary.", "route"),
        ],
        "exclusions": [
            exc("Park Entry Fees", "Park admission is excluded unless explicitly included in the confirmed package.", "ticket"),
            exc("Meals & Drinks", "Meals and drinks are excluded unless selected.", "utensils"),
            exc("Guaranteed Animal Sightings", "Wildlife moves freely and specific sightings cannot be guaranteed.", "paw"),
        ],
        "highlights": [
            highlight("Rehabilitated Landscape", "Discover how a former quarry landscape was transformed into a functioning ecological environment.", "leaf", "Conservation"),
            highlight("Wildlife Encounters", "Observe wildlife where available while respecting animal welfare and park rules.", "paw", "Wildlife"),
            highlight("Birdwatching", "Explore habitats that support a variety of bird species.", "bird", "Nature"),
            highlight("Botanical Discovery", "Experience the park's plant life and restored landscapes.", "flower", "Nature"),
        ],
        "addons": [
            addon("Private Specialist Guide", "Upgrade to a specialist nature or birding guide.", "Subject to guide availability and advance confirmation.", 6000, "Per Booking"),
        ],
        "packing": [
            packing("Comfortable Walking Shoes", "Wear shoes suitable for walking on outdoor paths.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Binoculars", "Optional binoculars can improve bird and wildlife observation.", "Equipment", "binoculars"),
            packing("Water", "Carry drinking water.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Maintain Safe Distance", "Do not approach, feed or touch wildlife unless authorised staff explicitly permit an interaction.", "Wildlife", "paw"),
            safety("Follow Park Rules", "Follow all park instructions and remain on designated paths where required.", "General", "shield"),
            safety("Heat & Hydration", "Stay hydrated and take appropriate breaks in hot weather.", "Health", "sun"),
        ],
        "requirements": [
            requirement("Confirmed Pickup", "Provide accommodation details for pickup coordination.", "Booking", True, "map-pin"),
            requirement("Follow Park Instructions", "Guests must follow the park's visitor and wildlife-safety rules.", "Wildlife", True, "shield"),
        ],
        "faqs": [
            faq("Will we see specific animals?", "Wildlife sightings are possible but not guaranteed. Animal movement and behaviour are natural and unpredictable.", "Wildlife", True),
            faq("Is entry included?", "Only if the confirmed booking explicitly states that Haller Park admission is included.", "Fees", True),
            faq("Can children join?", "Yes, subject to the park's current visitor requirements and adult supervision.", "Family"),
        ],
    },

    {
        "code": "COA-DIA-001",
        "slug": "kaya-kinondo-sacred-forest",
        "title": "Kaya Kinondo — Sacred Forest & Digo Heritage",
        "destination_id": 25,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A locally guided journey into Kaya Kinondo exploring sacred forest "
            "traditions, biodiversity and Digo cultural heritage."
        ),
        "description": (
            "Walk with a local guide through Kaya Kinondo and learn why the "
            "forest is both an ecological landscape and a sacred cultural space "
            "for the Digo community. The experience combines gentle walking, "
            "stories, traditional knowledge and reflection on the relationship "
            "between community, nature and heritage."
        ),
        "duration": "Half Day",
        "meeting_point": "Kaya Kinondo visitor meeting point; accommodation pickup is confirmed after booking.",
        "location": "Kaya Kinondo, Diani / Kwale County, Kenya",
        "price_from": 9500,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "kaya-kinondo-sacred-forest",
        "banner_image": None,
        "meta_title": "Kaya Kinondo Sacred Forest Experience | The Uncharted Route",
        "meta_description": "Discover Kaya Kinondo's sacred forest, biodiversity and Digo cultural heritage near Diani.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 6,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_CULTURE, TAG_LOCAL_CRAFTS, TAG_NATURE, TAG_PRIVATE],
        "moments": [MOMENT_HERITAGE, MOMENT_TRADITION, MOMENT_HIDDEN_GEMS],
        "pricing": pricing(
            (14500, 20500, 31500),
            (11500, 17000, 26500),
            (9500, 14000, 22000),
            "Indicative TUR selling price per person. Community fees, guide arrangements and transport must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Cultural Introduction", "Morning / Afternoon", "Collect guests from the agreed accommodation and introduce the cultural significance of the Kaya."),
            itinerary("Guided Sacred Forest Walk", "Main Activity", "Walk through the forest with a local guide while learning about Digo traditions, sacred spaces, plants and community stewardship."),
            itinerary("Heritage Stories & Reflection", "Main Activity", "Hear stories about the Kaya's role in community life and the importance of protecting cultural landscapes."),
            itinerary("Return to Diani", "Afternoon", "Conclude the experience and return guests to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Pickup and drop-off coordination from the agreed accommodation.", "car"),
            inc("Local Community Guide", "Guided interpretation from a local host familiar with the Kaya's cultural significance.", "user"),
            inc("Forest Experience", "Guided walk through approved visitor areas.", "leaf"),
            inc("Community Experience Coordination", "TUR coordination of the confirmed local arrangements.", "route"),
        ],
        "exclusions": [
            exc("Personal Purchases", "Crafts, souvenirs and other personal purchases are excluded.", "shopping-bag"),
            exc("Meals", "Meals are excluded unless explicitly included in the confirmed package.", "utensils"),
            exc("Unapproved Access", "Guests may not enter restricted or sacred areas outside the agreed visitor route.", "lock"),
        ],
        "highlights": [
            highlight("Sacred Forest", "Explore a culturally significant forest landscape protected through community traditions.", "leaf", "Culture"),
            highlight("Digo Heritage", "Learn about Digo traditions and the cultural meaning of the Kaya.", "users", "Heritage"),
            highlight("Local Knowledge", "Hear locally held knowledge about plants, place and community stewardship.", "book", "Culture"),
        ],
        "addons": [],
        "packing": [
            packing("Closed Comfortable Shoes", "Wear comfortable shoes suitable for a forest walk.", "Footwear", "shoe"),
            packing("Modest Clothing", "Wear respectful clothing suitable for visiting a culturally sacred site.", "Clothing", "shirt"),
            packing("Insect Repellent", "Consider insect repellent for the forest environment.", "Health", "bug"),
            packing("Water", "Carry drinking water.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Stay With the Guide", "Remain on the agreed route and follow the community guide's instructions.", "General", "users"),
            safety("Respect Sacred Areas", "Do not enter restricted spaces, touch sacred objects or remove plants or materials.", "Cultural Respect", "shield"),
            safety("Forest Terrain", "Watch your footing on roots, uneven ground and natural surfaces.", "Terrain", "shoe"),
        ],
        "requirements": [
            requirement("Respectful Conduct", "Guests must respect community traditions and sacred-site rules.", "Culture", True, "heart"),
            requirement("Confirmed Pickup", "Provide accommodation details for pickup coordination.", "Booking", True, "map-pin"),
        ],
        "faqs": [
            faq("Is this a normal forest walk?", "No. Kaya Kinondo is a culturally significant sacred forest, so the experience includes both ecological and cultural interpretation.", "Experience", True),
            faq("Can we enter every part of the forest?", "No. Guests remain within areas approved for visitors and follow the local guide's instructions.", "Culture", True),
            faq("What should I wear?", "Comfortable, modest clothing and closed walking shoes are recommended.", "Packing"),
        ],
    },

    {
        "code": "COA-DIA-002",
        "slug": "kisite-marine-wasini",
        "title": "Kisite Marine Escape — Reef, Dolphins & Wasini",
        "destination_id": 25,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A full-day marine journey combining boat travel, reef exploration, "
            "optional snorkelling and a Wasini Island cultural touchpoint."
        ),
        "description": (
            "Travel south from the Diani coast toward Shimoni and the Kisite "
            "marine environment for a day on the water. Depending on the "
            "confirmed route and conditions, guests may enjoy reef viewing, "
            "snorkelling, a boat journey and time connected to Wasini Island. "
            "Dolphins, turtles and other marine life may be encountered but are "
            "never guaranteed."
        ),
        "duration": "Full Day",
        "meeting_point": "Shimoni / confirmed marine departure point; accommodation pickup is coordinated after booking.",
        "location": "Kisite-Mpunguti / Shimoni / Wasini, Kwale County, Kenya",
        "price_from": 12000,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "kisite-marine-wasini",
        "banner_image": None,
        "meta_title": "Kisite Marine & Wasini Experience | The Uncharted Route",
        "meta_description": "Explore Kisite marine waters and Wasini Island with a private coastal experience from Diani.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 7,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": CONSERVATION_CORAL,
        "tags": [TAG_COASTAL, TAG_NATURE, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_OCEAN_VIEW, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (17500, 25500, 39500),
            (14000, 20500, 31500),
            (11000, 16500, 25500),
            "Indicative TUR selling price per person. Marine park fees, boat charges and supplier terms must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Diani Pickup & Transfer to Shimoni", "Early Morning", "Collect guests from their accommodation and transfer to the confirmed marine departure point."),
            itinerary("Boat Journey & Marine Exploration", "Morning", "Board the confirmed boat and travel through the coastal waters toward the Kisite marine environment."),
            itinerary("Reef / Snorkelling & Wildlife Possibilities", "Late Morning–Afternoon", "Where conditions permit, enjoy reef viewing and snorkelling. Marine wildlife may be encountered but sightings are not guaranteed."),
            itinerary("Wasini / Coastal Lunch Arrangement", "Afternoon", "Where included in the selected package, enjoy a locally arranged meal or cultural stop before returning."),
            itinerary("Return to Diani", "Late Afternoon", "Return to the departure point and transfer guests back to their accommodation.")
        ],
        "inclusions": [
            inc("Private Pickup Coordination", "Pickup and drop-off coordination from the agreed Diani accommodation.", "car"),
            inc("Boat Excursion", "Boat transport according to the confirmed marine package.", "ship"),
            inc("Marine Guide / Crew", "Local crew and marine guidance according to the confirmed supplier arrangement.", "user"),
            inc("Snorkelling Equipment", "Basic equipment where included and suitable for the conditions.", "water"),
        ],
        "exclusions": [
            exc("Marine Park Fees", "Applicable protected-area entry fees are excluded unless explicitly included in the booking.", "ticket"),
            exc("Meals Unless Included", "Lunch and drinks are excluded unless stated in the confirmed package.", "utensils"),
            exc("Guaranteed Dolphins", "Dolphin and other wildlife sightings are not guaranteed.", "fish"),
        ],
        "highlights": [
            highlight("Kisite Marine Environment", "Explore one of Kenya's recognised marine conservation areas.", "water", "Nature"),
            highlight("Reef Viewing", "Discover coral and shallow marine habitats through guided viewing or snorkelling where conditions permit.", "fish", "Marine"),
            highlight("Wasini Connection", "Add a coastal cultural or dining moment connected to Wasini Island where included.", "users", "Culture"),
            highlight("Wildlife Possibilities", "Dolphins, turtles, rays and reef fish may be encountered naturally but are never guaranteed.", "fish", "Wildlife"),
        ],
        "addons": [
            addon("Private Premium Boat", "Upgrade to a premium private boat arrangement.", "Subject to vessel availability, route and supplier confirmation.", 15000, "Per Booking"),
            addon("Wasini Seafood Lunch", "Add a locally arranged seafood lunch.", "Subject to menu availability, dietary requirements and supplier confirmation.", 4500, "Per Person"),
        ],
        "packing": [
            packing("Swimwear", "Bring swimwear if you intend to enter the water.", "Clothing", "swim"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water Shoes", "Recommended for reef and shoreline activity.", "Footwear", "shoe"),
            packing("Dry Bag", "Protect electronics and valuables from water.", "Equipment", "bag"),
            packing("Motion-Sickness Medication", "Guests prone to seasickness should bring their usual medication and inform the host.", "Health", "medkit"),
        ],
        "safety": [
            safety("Marine Safety Briefing", "Follow the boat crew's safety instructions at all times.", "Marine Safety", "shield"),
            safety("Sea Conditions", "The route may change or be cancelled when weather, tides or sea conditions make the activity unsafe.", "Weather", "cloud"),
            safety("Wildlife Distance", "Do not chase, feed, touch or otherwise interfere with marine wildlife.", "Wildlife", "fish"),
            safety("Swimming Conditions", "Only enter the water when the guide confirms that conditions are suitable.", "Water", "life-buoy"),
        ],
        "requirements": [
            requirement("Accommodation Details", "Provide the Diani accommodation details for pickup coordination.", "Booking", True, "map-pin"),
            requirement("Swimming Disclosure", "Inform the host about swimming limitations or medical considerations before the water activity.", "Health", False, "info"),
        ],
        "faqs": [
            faq("Are dolphins guaranteed?", "No. Dolphin sightings depend on natural wildlife behaviour, sea conditions and location and are never guaranteed.", "Wildlife", True),
            faq("Are marine park fees included?", "Only where explicitly stated in your booking confirmation.", "Fees", True),
            faq("Is snorkelling guaranteed?", "No. Snorkelling depends on sea conditions, weather, tides and safety considerations.", "Activity"),
            faq("Can non-swimmers join?", "Non-swimmers may be able to join the boat-based portions, but they must tell the host in advance and follow all safety instructions.", "Accessibility"),
        ],
    },

    {
        "code": "COA-LAM-001",
        "slug": "lamu-living-heritage",
        "title": "Lamu Living Heritage — Old Town, Crafts & Swahili Culture",
        "destination_id": 9,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A guided journey through Lamu Old Town exploring Swahili heritage, "
            "architecture, local crafts and living cultural traditions."
        ),
        "description": (
            "Discover Lamu Old Town as a living Swahili cultural landscape. "
            "Walk through historic streets, admire carved doors and traditional "
            "architecture, meet local makers where available and explore the "
            "relationship between coastal trade, faith, family life and craft. "
            "The experience can be extended with a cooking or craft session "
            "subject to availability."
        ),
        "duration": "Half Day",
        "meeting_point": "Lamu Old Town / agreed waterfront meeting point; accommodation pickup is confirmed after booking.",
        "location": "Lamu Old Town, Lamu County, Kenya",
        "price_from": 7500,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "lamu-living-heritage",
        "banner_image": None,
        "meta_title": "Lamu Living Heritage Experience | The Uncharted Route",
        "meta_description": "Explore Lamu Old Town, Swahili architecture, crafts and living coastal culture.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 8,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_CULTURE, TAG_HISTORICAL, TAG_ARCHITECTURE, TAG_LOCAL_CRAFTS, TAG_PRIVATE],
        "moments": [MOMENT_HERITAGE, MOMENT_ARTISANS, MOMENT_TRADITION, MOMENT_HIDDEN_GEMS],
        "pricing": pricing(
            (11500, 16500, 25500),
            (9500, 14000, 21500),
            (7500, 11000, 17500),
            "Indicative TUR selling price per person. Museum, workshop, meal and other attraction fees are excluded unless specifically included."
        ),
        "itinerary": [
            itinerary("Old Town Introduction", "Morning / Afternoon", "Meet the local guide and receive an introduction to Lamu's history and Swahili cultural landscape."),
            itinerary("Heritage Walking Route", "Main Activity", "Explore selected streets, historic buildings, carved doors and public spaces while learning about Lamu's Indian Ocean history."),
            itinerary("Craft & Living Culture", "Main Activity", "Visit a local craft or cultural activity where available and learn directly from the people maintaining these traditions."),
            itinerary("Optional Culinary Moment", "Afternoon", "Where selected, add a Swahili tasting or cooking experience before concluding the tour.")
        ],
        "inclusions": [
            inc("Local Heritage Guide", "Guided interpretation by a local host.", "user"),
            inc("Walking Heritage Experience", "Curated Old Town walking route.", "walk"),
            inc("Pickup Coordination", "Accommodation pickup coordination where included in the confirmed package.", "car"),
            inc("TUR Experience Coordination", "Coordination of confirmed cultural activities and timings.", "route"),
        ],
        "exclusions": [
            exc("Museum Admissions", "Museum or heritage-site admission is excluded unless explicitly included.", "ticket"),
            exc("Craft Purchases", "Crafts, souvenirs and artwork are paid directly by guests.", "shopping-bag"),
            exc("Meals Unless Selected", "Meals and tastings are excluded unless selected in the package.", "utensils"),
        ],
        "highlights": [
            highlight("Swahili Architecture", "Admire Lamu's distinctive doors, courtyards and historic buildings.", "building", "Architecture"),
            highlight("Living Heritage", "Experience Lamu as a living community rather than a static museum.", "users", "Culture"),
            highlight("Local Craftsmanship", "Meet or observe local makers where availability allows.", "hammer", "Craft"),
            highlight("Indian Ocean History", "Connect Lamu's present-day culture with centuries of coastal trade.", "book", "Heritage"),
        ],
        "addons": [
            addon("Swahili Cooking Session", "Add a hands-on introduction to local cooking.", "A cooking experience can be added subject to host availability, menu and timing.", 4500, "Per Person"),
            addon("Traditional Craft Workshop", "Add a practical craft-making session.", "Subject to artisan availability and workshop confirmation.", 3500, "Per Person"),
        ],
        "packing": [
            packing("Comfortable Shoes", "Wear comfortable shoes for walking on uneven streets.", "Footwear", "shoe"),
            packing("Modest Clothing", "Wear respectful clothing suitable for a culturally significant community.", "Clothing", "shirt"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water", "Carry drinking water.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Respect Private Spaces", "Lamu Old Town is a living community. Do not enter private spaces without permission.", "Cultural Respect", "home"),
            safety("Photography Etiquette", "Ask before photographing people, homes, businesses or religious activities.", "Cultural Respect", "camera"),
            safety("Watch Your Step", "Historic streets may have uneven surfaces, steps and narrow passages.", "Terrain", "shoe"),
        ],
        "requirements": [
            requirement("Respectful Conduct", "Guests must respect local customs, homes, religious spaces and community traditions.", "Culture", True, "heart"),
            requirement("Confirmed Meeting Arrangement", "Provide accommodation details and follow the confirmed meeting instructions.", "Booking", True, "map-pin"),
        ],
        "faqs": [
            faq("Is Lamu Old Town a museum?", "No. It is a living historic town where people continue to live, work and practice cultural traditions.", "Experience", True),
            faq("Can we buy local crafts?", "Yes. Where appropriate, the guide can help guests discover local craft makers. Purchases are separate.", "Shopping"),
            faq("Can we add a cooking class?", "Yes, subject to host availability and advance confirmation.", "Activities"),
        ],
    },

    {
        "code": "COA-LAM-002",
        "slug": "lamu-private-dhow-sunset",
        "title": "Lamu by Dhow — Private Sailing & Sunset",
        "destination_id": 9,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A private traditional dhow sailing experience with sunset views, "
            "coastal scenery and optional Swahili dining."
        ),
        "description": (
            "Step aboard a traditional Lamu dhow for a private coastal sailing "
            "experience. Choose a relaxed sunset route or a longer sailing "
            "arrangement depending on the season, weather and supplier schedule. "
            "The experience is designed around quiet ocean views, traditional "
            "sailing and the distinctive rhythm of Lamu's coastline."
        ),
        "duration": "2–4 Hours",
        "meeting_point": "Agreed Lamu waterfront / dhow boarding point; accommodation pickup is coordinated after booking.",
        "location": "Lamu, Lamu County, Kenya",
        "price_from": 11000,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 6,
        "difficulty": "Easy",
        "featured_image": "lamu-private-dhow-sunset",
        "banner_image": None,
        "meta_title": "Lamu Private Dhow Sunset | The Uncharted Route",
        "meta_description": "Sail Lamu's coast on a private traditional dhow with sunset views and optional Swahili dining.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 9,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_COASTAL, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        "moments": [MOMENT_OCEAN_VIEW, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (18000, 28000, 42000),
            (14500, 22000, 33000),
            (11000, 17000, 25500),
            "Indicative TUR selling price per person. Final dhow charter, dining and seasonal supplier costs must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Waterfront Meeting & Boarding", "Afternoon / Sunset", "Meet at the confirmed dhow boarding point and receive a short safety briefing before departure."),
            itinerary("Traditional Dhow Sailing", "Main Activity", "Sail along the Lamu coast while enjoying views of the shoreline, islands and changing light."),
            itinerary("Sunset Coastal Moment", "Sunset", "Pause for the sunset experience and photography where weather and route conditions allow."),
            itinerary("Optional Swahili Dinner", "Evening", "Where selected, continue with a pre-arranged Swahili dinner before returning to the agreed drop-off point.")
        ],
        "inclusions": [
            inc("Private Dhow Arrangement", "Private dhow charter according to the confirmed vessel and route.", "ship"),
            inc("Boat Crew", "Experienced local dhow crew for the sailing experience.", "user"),
            inc("Safety Briefing", "Pre-departure safety briefing.", "shield"),
            inc("Sunset Experience", "A sailing route timed around sunset where weather and seasonal conditions permit.", "sun"),
        ],
        "exclusions": [
            exc("Dinner Unless Selected", "Swahili dinner is excluded unless specifically included in the confirmed package.", "utensils"),
            exc("Personal Purchases", "Personal purchases and gratuities are excluded.", "wallet"),
            exc("Weather Guarantee", "Sunset visibility depends on weather and natural conditions.", "cloud"),
        ],
        "highlights": [
            highlight("Traditional Dhow", "Experience Lamu's iconic sailing tradition aboard a local dhow.", "ship", "Coastal"),
            highlight("Sunset Sailing", "Enjoy changing coastal light from the water.", "sun", "Photography"),
            highlight("Private Atmosphere", "A private arrangement creates a more intimate coastal experience.", "heart", "Private"),
        ],
        "addons": [
            addon("Swahili Sunset Dinner", "Add a locally arranged evening meal.", "A dinner arrangement can be added subject to venue, menu and supplier confirmation.", 6500, "Per Person"),
        ],
        "packing": [
            packing("Light Layer", "Bring a light layer for the return journey after sunset.", "Clothing", "shirt"),
            packing("Sun Protection", "Bring sunscreen and sunglasses for the daytime portion.", "Health", "sun"),
            packing("Camera", "Bring a camera or phone for coastal photography.", "Electronics", "camera"),
            packing("Non-Slip Shoes", "Wear comfortable footwear suitable for boarding and moving on a boat.", "Footwear", "shoe"),
        ],
        "safety": [
            safety("Follow Crew Instructions", "Follow the dhow crew's instructions during boarding, sailing and disembarkation.", "Marine Safety", "shield"),
            safety("Weather Conditions", "The route may be altered or postponed if weather or sea conditions are unsuitable.", "Weather", "cloud"),
            safety("Boat Movement", "Move carefully on the dhow and hold secure handrails where provided.", "Marine Safety", "ship"),
        ],
        "requirements": [
            requirement("Confirmed Boarding Point", "Follow the confirmed waterfront meeting instructions.", "Booking", True, "map-pin"),
            requirement("Punctuality", "Arrive at the agreed boarding point on time.", "General", True, "clock"),
        ],
        "faqs": [
            faq("Is the dhow private?", "The intended TUR package is a private dhow arrangement, subject to final vessel confirmation.", "Booking", True),
            faq("Is dinner included?", "Only if you select the dining option and it appears on your booking confirmation.", "Dining"),
            faq("What if the sunset is cloudy?", "The sailing continues where conditions are safe, but sunset visibility is naturally dependent on weather.", "Weather"),
        ],
    },

    {
        "code": "COA-MAL-001",
        "slug": "gedi-lost-swahili-city",
        "title": "Gedi — The Lost Swahili City",
        "destination_id": 17,
        "category_id": CATEGORY_CULTURE,
        "short_description": (
            "A guided archaeological and nature experience exploring the coral-stone "
            "ruins and forest setting of the historic Swahili settlement of Gedi."
        ),
        "description": (
            "Step into the remains of one of the East African coast's most "
            "intriguing historic settlements. Explore coral-stone structures, "
            "mosques, houses and forest pathways while your guide explains the "
            "trade, architecture and daily life associated with the medieval "
            "Swahili world. The experience connects archaeology with the natural "
            "landscape surrounding the ruins."
        ),
        "duration": "Half Day",
        "meeting_point": "Gedi Ruins visitor entrance; accommodation pickup is coordinated from Malindi/Watamu service areas.",
        "location": "Gede, Kilifi County, Kenya",
        "price_from": 7500,
        "minimum_people": 1,
        "maximum_people": 10,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "gedi-lost-swahili-city",
        "banner_image": None,
        "meta_title": "Gedi Ruins Experience | The Uncharted Route",
        "meta_description": "Explore the archaeological ruins and Swahili history of Gedi with a private guided experience.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 10,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_CULTURE, TAG_HISTORICAL, TAG_ARCHITECTURE, TAG_NATURE, TAG_PRIVATE],
        "moments": [MOMENT_HERITAGE, MOMENT_HIDDEN_GEMS],
        "pricing": pricing(
            (11500, 16500, 25500),
            (9500, 14000, 21500),
            (7500, 11000, 17500),
            "Indicative TUR selling price per person. Heritage admission and supplier transport costs must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Journey to Gedi", "Morning / Afternoon", "Collect guests from the agreed accommodation and travel to the Gedi archaeological site."),
            itinerary("Archaeological Exploration", "Main Activity", "Walk through the ruins with a guide and explore the settlement's architecture, religious structures and residential remains."),
            itinerary("Swahili History & Forest Context", "Main Activity", "Connect the archaeological remains with the wider Swahili trading world and surrounding forest ecosystem."),
            itinerary("Return Journey", "Afternoon", "Conclude the visit and return guests to their agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Pickup and drop-off coordination within the confirmed service area.", "car"),
            inc("Local Guide", "Guided interpretation of the archaeological site and Swahili history.", "user"),
            inc("Heritage Experience", "Curated visit through approved visitor areas of Gedi.", "landmark"),
        ],
        "exclusions": [
            exc("Site Admission", "Heritage-site admission is excluded unless explicitly included in the confirmed package.", "ticket"),
            exc("Meals & Drinks", "Meals and drinks are excluded unless selected.", "utensils"),
            exc("Personal Purchases", "Souvenirs and personal expenses are excluded.", "wallet"),
        ],
        "highlights": [
            highlight("Coral-Stone Ruins", "Explore the distinctive architecture built from coral stone.", "building", "Heritage"),
            highlight("Swahili History", "Learn about the historic settlement and Indian Ocean trading world.", "book", "History"),
            highlight("Forest Setting", "Experience archaeology within a lush coastal forest landscape.", "leaf", "Nature"),
        ],
        "addons": [],
        "packing": [
            packing("Walking Shoes", "Wear comfortable shoes suitable for uneven paths.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Insect Repellent", "Consider insect repellent in the forested environment.", "Health", "bug"),
            packing("Water", "Carry drinking water.", "General", "bottle-water"),
        ],
        "safety": [
            safety("Stay on Approved Paths", "Remain within designated visitor areas and follow guide instructions.", "Heritage", "shield"),
            safety("Uneven Terrain", "Watch your footing around ruins, roots and uneven ground.", "Terrain", "shoe"),
            safety("Protect Archaeological Remains", "Do not climb, remove stones, touch fragile structures or disturb archaeological material.", "Heritage", "landmark"),
        ],
        "requirements": [
            requirement("Confirmed Pickup Details", "Provide accommodation details for transport coordination.", "Booking", True, "map-pin"),
            requirement("Heritage Respect", "Guests must follow archaeological-site rules and protect the historic remains.", "Heritage", True, "shield"),
        ],
        "faqs": [
            faq("What is Gedi?", "Gedi is an archaeological site representing the remains of a historic Swahili settlement on Kenya's coast.", "History", True),
            faq("Is the site suitable for children?", "Older children can participate with responsible adult supervision and appropriate footwear.", "Family"),
            faq("Are entry fees included?", "Only where explicitly stated in the confirmed booking.", "Fees"),
        ],
    },

    {
        "code": "COA-MAL-002",
        "slug": "marafa-hells-kitchen-sunset",
        "title": "Marafa — Hell's Kitchen Sunset Expedition",
        "destination_id": 17,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "An afternoon journey into Marafa's dramatic sandstone canyon timed "
            "around the changing colours of the late-day landscape."
        ),
        "description": (
            "Travel inland from the Malindi coast to Marafa and explore the "
            "dramatic sandstone formations known locally as Hell's Kitchen. "
            "The experience is intentionally timed for the cooler afternoon and "
            "late-day light, when the canyon's colours can change dramatically. "
            "The exact route and timing depend on weather, road conditions and "
            "local operating arrangements."
        ),
        "duration": "Half Day",
        "meeting_point": "Guest accommodation pickup in the Malindi service area; exact pickup confirmed after booking.",
        "location": "Marafa, Kilifi County, Kenya",
        "price_from": 8500,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Moderate",
        "featured_image": "marafa-hells-kitchen-sunset",
        "banner_image": None,
        "meta_title": "Marafa Hell's Kitchen Sunset | The Uncharted Route",
        "meta_description": "Explore Marafa's dramatic sandstone canyon on a guided afternoon and sunset experience.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 11,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": None,
        "tags": [TAG_NATURE, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        "moments": [MOMENT_HIDDEN_GEMS, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (13500, 19500, 29500),
            (10500, 15500, 23500),
            (8500, 12500, 19000),
            "Indicative TUR selling price per person. Final transport, local guide and site-related charges must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Afternoon Pickup", "2:00–3:00 PM", "Collect guests from their Malindi-area accommodation and begin the journey toward Marafa."),
            itinerary("Canyon Exploration", "Late Afternoon", "Explore selected viewpoints and paths while the guide explains the landscape, local stories and natural formations."),
            itinerary("Golden-Hour Landscape", "Late Afternoon / Sunset", "Enjoy the changing colours and light across the sandstone formations where weather and visibility permit."),
            itinerary("Return to Malindi", "Evening", "Begin the return journey and drop guests at the agreed accommodation.")
        ],
        "inclusions": [
            inc("Private Pickup Coordination", "Pickup and drop-off coordination from the agreed Malindi-area accommodation.", "car"),
            inc("Local Guide", "Guided interpretation of Marafa and the surrounding landscape.", "user"),
            inc("Private Experience Coordination", "TUR coordination of the route, timing and supplier arrangements.", "route"),
        ],
        "exclusions": [
            exc("Meals & Drinks", "Meals and drinks are excluded unless explicitly selected.", "utensils"),
            exc("Personal Expenses", "Personal purchases and gratuities are excluded.", "wallet"),
            exc("Weather Guarantee", "Sunset colour and visibility depend on natural conditions.", "cloud"),
        ],
        "highlights": [
            highlight("Sandstone Canyon", "Explore the striking red and ochre formations of Marafa.", "mountain", "Landscape"),
            highlight("Golden-Hour Photography", "The late afternoon light can create dramatic changes in the canyon's colours.", "camera", "Photography"),
            highlight("Coastal Hinterland", "See a different side of Kenya's coast beyond the beaches.", "route", "Discovery"),
        ],
        "addons": [],
        "packing": [
            packing("Closed Walking Shoes", "Wear shoes suitable for uneven and dusty terrain.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water", "Carry sufficient drinking water.", "General", "bottle-water"),
            packing("Light Layer", "A light layer can be useful during the return journey.", "Clothing", "shirt"),
        ],
        "safety": [
            safety("Stay With the Guide", "Remain within the agreed route and follow local guide instructions.", "Terrain", "shield"),
            safety("Heat Exposure", "The area can become hot; hydrate regularly and take breaks.", "Health", "sun"),
            safety("Edge Awareness", "Stay away from unstable edges and do not climb formations outside approved routes.", "Terrain", "mountain"),
        ],
        "requirements": [
            requirement("Accommodation Details", "Provide the Malindi-area accommodation details for pickup coordination.", "Booking", True, "map-pin"),
            requirement("Comfort With Uneven Ground", "Guests should be comfortable walking on uneven natural surfaces.", "Activity", True, "shoe"),
        ],
        "faqs": [
            faq("Why is the experience in the afternoon?", "The afternoon generally provides more manageable temperatures and can offer better late-day light across the sandstone formations.", "Timing", True),
            faq("Is sunset guaranteed?", "No. Sunset visibility and colour depend on weather and atmospheric conditions.", "Weather", True),
            faq("Is the walk difficult?", "The experience includes uneven natural terrain and is best suited to guests comfortable with ordinary outdoor walking.", "Accessibility"),
        ],
    },

    {
        "code": "COA-MAL-003",
        "slug": "malindi-marine-discovery",
        "title": "Malindi Marine Discovery — Coral Gardens & Coastal Waters",
        "destination_id": 17,
        "category_id": CATEGORY_COASTAL,
        "short_description": (
            "A guided marine excursion exploring Malindi's protected coastal "
            "waters by boat, with reef viewing and optional snorkelling."
        ),
        "description": (
            "Explore Malindi's marine environment on a private or small-group "
            "boat excursion through the protected coastal waters. Depending on "
            "the confirmed route and sea conditions, guests may enjoy reef "
            "viewing, snorkelling, sandbank time or a relaxed coastal cruise. "
            "Marine wildlife encounters are possible but never guaranteed."
        ),
        "duration": "Half Day",
        "meeting_point": "Confirmed Malindi marine departure point; accommodation pickup is coordinated after booking.",
        "location": "Malindi, Kilifi County, Kenya",
        "price_from": 10000,
        "minimum_people": 1,
        "maximum_people": 8,
        "minimum_age": 8,
        "difficulty": "Easy",
        "featured_image": "malindi-marine-discovery",
        "banner_image": None,
        "meta_title": "Malindi Marine Discovery | The Uncharted Route",
        "meta_description": "Explore Malindi's marine park waters with reef viewing, snorkelling and a private coastal boat experience.",
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": 12,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": CONSERVATION_CORAL,
        "tags": [TAG_COASTAL, TAG_NATURE, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        "moments": [MOMENT_MARINE_LIFE, MOMENT_OCEAN_VIEW, MOMENT_EXTRAORDINARY_ESCAPE],
        "pricing": pricing(
            (15500, 22500, 34500),
            (12500, 18500, 28500),
            (10000, 14500, 22500),
            "Indicative TUR selling price per person. Marine park fees, boat charges and supplier terms must be confirmed before booking."
        ),
        "itinerary": [
            itinerary("Pickup & Marine Departure", "Morning / Afternoon", "Collect guests from the agreed accommodation and travel to the confirmed marine departure point."),
            itinerary("Boat Journey", "Main Activity", "Board the boat and travel through Malindi's coastal waters while the guide introduces the marine environment."),
            itinerary("Reef Viewing & Optional Snorkelling", "Main Activity", "Where conditions permit, explore reef areas through viewing or snorkelling. Wildlife sightings are not guaranteed."),
            itinerary("Return & Drop-Off", "Afternoon", "Return to the departure point and transfer guests back to the agreed accommodation.")
        ],
        "inclusions": [
            inc("Accommodation Pickup Coordination", "Pickup coordination from the guest's agreed accommodation.", "car"),
            inc("Boat Excursion", "Boat travel according to the confirmed marine route.", "ship"),
            inc("Marine Crew / Guide", "Local crew and marine guidance according to the confirmed supplier arrangement.", "user"),
            inc("Snorkelling Equipment", "Basic equipment where included and suitable for conditions.", "water"),
        ],
        "exclusions": [
            exc("Marine Park Fees", "Applicable park or conservation fees are excluded unless explicitly included.", "ticket"),
            exc("Meals & Drinks", "Meals and drinks are excluded unless selected.", "utensils"),
            exc("Guaranteed Wildlife", "Marine wildlife sightings are not guaranteed.", "fish"),
        ],
        "highlights": [
            highlight("Malindi Marine Environment", "Explore protected coastal waters and marine habitats.", "water", "Nature"),
            highlight("Coral Reef Viewing", "Discover shallow marine habitats through viewing or snorkelling where conditions permit.", "fish", "Marine"),
            highlight("Coastal Boat Journey", "Enjoy the coastline from the water at a relaxed pace.", "ship", "Coastal"),
            highlight("Marine Wildlife Possibilities", "Turtles, dolphins, rays and reef fish may be encountered naturally but are never guaranteed.", "fish", "Wildlife"),
        ],
        "addons": [
            addon("Private Premium Boat", "Upgrade to a premium private vessel.", "Subject to vessel availability and supplier confirmation.", 12000, "Per Booking"),
            addon("Private Coastal Picnic", "Add a pre-arranged coastal picnic.", "Subject to weather, route, menu and supplier confirmation.", 4000, "Per Person"),
        ],
        "packing": [
            packing("Swimwear", "Bring swimwear if you plan to enter the water.", "Clothing", "swim"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water Shoes", "Recommended for shoreline and reef activity.", "Footwear", "shoe"),
            packing("Dry Bag", "Protect electronics and valuables from water.", "Equipment", "bag"),
        ],
        "safety": [
            safety("Marine Safety Briefing", "Follow all boat crew and guide instructions.", "Marine Safety", "shield"),
            safety("Sea Conditions", "Routes may change or be cancelled when weather, tides or sea conditions make activities unsafe.", "Weather", "cloud"),
            safety("Wildlife Respect", "Do not chase, feed, touch or interfere with marine wildlife.", "Wildlife", "fish"),
            safety("Water Entry", "Enter the water only when the guide confirms conditions are appropriate.", "Water", "life-buoy"),
        ],
        "requirements": [
            requirement("Accommodation Details", "Provide the accommodation location for pickup coordination.", "Booking", True, "map-pin"),
            requirement("Water Activity Disclosure", "Inform the host about swimming limitations before the experience.", "Health", False, "info"),
        ],
        "faqs": [
            faq("Are marine animals guaranteed?", "No. Dolphins, turtles, rays and reef fish are wild and sightings depend on natural conditions.", "Wildlife", True),
            faq("Are park fees included?", "Only when explicitly stated in the confirmed booking.", "Fees", True),
            faq("Is snorkelling always available?", "No. Snorkelling depends on sea conditions, weather, tides and safety considerations.", "Activity"),
            faq("Can non-swimmers join?", "Guests can often enjoy the boat portion without entering the water, but they should disclose this when booking.", "Accessibility"),
        ],
    },
]


# =============================================================================
# VALIDATION
# =============================================================================

def require_active(model, record_id, label):
    record = db.session.get(model, record_id)

    if record is None:
        raise RuntimeError(f"Required {label} ID {record_id} does not exist.")

    if hasattr(record, "active") and not record.active:
        raise RuntimeError(f"Required {label} ID {record_id} is inactive.")

    return record


def require_destination(record_id):
    destination = db.session.get(Destination, record_id)

    if destination is None:
        raise RuntimeError(f"Destination ID {record_id} does not exist.")

    # IMPORTANT:
    # An inactive destination is intentionally allowed here. Its experience
    # records are being prepared now so the destination can be activated later.
    return destination


def validate_unique_batch():
    seen_codes = set()
    seen_slugs = set()

    for data in EXPERIENCES:
        if data["code"] in seen_codes:
            raise RuntimeError(f"Duplicate batch experience code: {data['code']}")

        if data["slug"] in seen_slugs:
            raise RuntimeError(f"Duplicate batch experience slug: {data['slug']}")

        seen_codes.add(data["code"])
        seen_slugs.add(data["slug"])


def add_children(model, experience_id, records):
    db.session.add_all([
        model(experience_id=experience_id, **record)
        for record in records
    ])


def validate_reusable_cms(data):
    require_active(
        ExperienceCategory,
        data["category_id"],
        "Experience category",
    )

    require_destination(data["destination_id"])

    require_active(
        CancellationPolicy,
        data["cancellation_policy_id"],
        "Cancellation policy",
    )

    require_active(
        Accessibility,
        data["accessibility_profile_id"],
        "Accessibility profile",
    )

    if data.get("conservation_story_id"):
        require_active(
            ConservationStory,
            data["conservation_story_id"],
            "Conservation story",
        )

    for tag_id in data["tags"]:
        require_active(ExperienceTag, tag_id, "Experience tag")

    for moment_id in data["moments"]:
        require_active(SignatureMoment, moment_id, "Signature moment")


def validate_duplicate_experience(data):
    existing = Experience.query.filter(
        or_(
            Experience.experience_code == data["code"],
            Experience.slug == data["slug"],
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


# =============================================================================
# POPULATION
# =============================================================================

def populate(apply_changes=False):
    app = create_app()

    with app.app_context():
        try:
            validate_unique_batch()

            print("\n" + "=" * 110)
            print("THE UNCHARTED ROUTE — BATCH 1: KENYAN COAST")
            print("=" * 110)
            print(f"Experiences in batch: {len(EXPERIENCES)}")
            print("Mode:", "APPLY" if apply_changes else "DRY RUN")
            print("=" * 110)

            # ---------------------------------------------------------------
            # Validate all reusable records before creating anything.
            # ---------------------------------------------------------------

            for data in EXPERIENCES:
                validate_reusable_cms(data)
                validate_duplicate_experience(data)

            print("\nReusable CMS records validated.")
            print("Duplicate protection validated.")

            created = []

            # ---------------------------------------------------------------
            # Create each experience and every approved child relationship.
            # ---------------------------------------------------------------

            for batch_index, data in enumerate(EXPERIENCES, 1):
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
                    featured_image=data["featured_image"],
                    banner_image=data["banner_image"],
                    meta_title=data["meta_title"],
                    meta_description=data["meta_description"],
                    featured=data["featured"],
                    show_on_homepage=data["show_on_homepage"],
                    active=data["active"],
                    display_order=data["display_order"],
                    category_id=data["category_id"],
                    destination_id=data["destination_id"],
                    conservation_story_id=data.get("conservation_story_id"),
                    cancellation_policy_id=data["cancellation_policy_id"],
                    accessibility_profile_id=data["accessibility_profile_id"],
                )

                db.session.add(experience)
                db.session.flush()

                # Existing reusable CMS associations.
                experience.tags.extend([
                    db.session.get(ExperienceTag, tag_id)
                    for tag_id in data["tags"]
                ])

                experience.signature_moments.extend([
                    db.session.get(SignatureMoment, moment_id)
                    for moment_id in data["moments"]
                ])

                # ITINERARY
                itinerary_rows = [
                    {
                        **record,
                        "display_order": index,
                    }
                    for index, record in enumerate(data["itinerary"], 1)
                ]

                add_children(
                    ExperienceItinerary,
                    experience.id,
                    itinerary_rows,
                )

                # INCLUSIONS
                add_children(
                    ExperienceInclusion,
                    experience.id,
                    ordered(data["inclusions"]),
                )

                # EXCLUSIONS
                add_children(
                    ExperienceExclusion,
                    experience.id,
                    ordered(data["exclusions"]),
                )

                # HIGHLIGHTS
                add_children(
                    ExperienceHighlight,
                    experience.id,
                    ordered(data["highlights"]),
                )

                # PRICING
                pricing_rows = []

                for order, record in enumerate(data["pricing"], 1):
                    item = dict(record)
                    item["display_order"] = order
                    item["active"] = True
                    pricing_rows.append(item)

                add_children(
                    ExperiencePricing,
                    experience.id,
                    pricing_rows,
                )

                # OPTIONAL ADD-ONS
                add_children(
                    ExperienceAddon,
                    experience.id,
                    ordered(data["addons"]),
                )

                # PACKING
                add_children(
                    ExperiencePackingItem,
                    experience.id,
                    ordered(data["packing"]),
                )

                # SAFETY
                add_children(
                    ExperienceSafetyRule,
                    experience.id,
                    ordered(data["safety"]),
                )

                # REQUIREMENTS
                add_children(
                    ExperienceRequirement,
                    experience.id,
                    ordered(data["requirements"]),
                )

                # FAQS
                add_children(
                    ExperienceFAQ,
                    experience.id,
                    ordered(data["faqs"]),
                )

                # WILDLIFE
                # None of the current WildlifeSpecies records are marine
                # species, so no wildlife association is fabricated for these
                # coastal experiences.
                #
                # Marine wildlife is instead described in the experience
                # content as possible, never guaranteed.

                created.append(experience)

                print(
                    f"\n[{batch_index:02d}/{len(EXPERIENCES)}] "
                    f"{experience.experience_code} — {experience.title}"
                )
                print(
                    f"    Destination ID: {experience.destination_id}"
                    f" | Destination active: "
                    f"{db.session.get(Destination, experience.destination_id).active}"
                )
                print(
                    f"    Itinerary: {len(data['itinerary'])}"
                    f" | Inclusions: {len(data['inclusions'])}"
                    f" | Exclusions: {len(data['exclusions'])}"
                    f" | Highlights: {len(data['highlights'])}"
                )
                print(
                    f"    Pricing: {len(data['pricing'])}"
                    f" | Add-ons: {len(data['addons'])}"
                    f" | Packing: {len(data['packing'])}"
                    f" | Safety: {len(data['safety'])}"
                )
                print(
                    f"    Requirements: {len(data['requirements'])}"
                    f" | FAQs: {len(data['faqs'])}"
                    f" | Tags: {len(data['tags'])}"
                    f" | Signature moments: {len(data['moments'])}"
                )

            # ---------------------------------------------------------------
            # Verification before commit.
            # ---------------------------------------------------------------

            print("\n" + "=" * 110)
            print("BATCH VERIFICATION")
            print("=" * 110)

            for experience in created:
                checks = {
                    "pricing": experience.pricing.count(),
                    "itinerary": experience.itinerary.count(),
                    "inclusions": experience.inclusions.count(),
                    "exclusions": experience.exclusions.count(),
                    "highlights": experience.highlights.count(),
                    "addons": experience.addons.count(),
                    "packing": experience.packing_items.count(),
                    "safety": experience.safety_rules.count(),
                    "requirements": experience.requirements.count(),
                    "faqs": experience.faqs.count(),
                    "tags": experience.tags.count(),
                    "signature_moments": experience.signature_moments.count(),
                    "media": experience.media.count(),
                    "schedules": experience.schedules.count(),
                    "bookings": experience.bookings.count(),
                }

                expected = {
                    "pricing": 9,
                    "itinerary": len(next(
                        x["itinerary"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "inclusions": len(next(
                        x["inclusions"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "exclusions": len(next(
                        x["exclusions"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "highlights": len(next(
                        x["highlights"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "addons": len(next(
                        x["addons"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "packing": len(next(
                        x["packing"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "safety": len(next(
                        x["safety"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "requirements": len(next(
                        x["requirements"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "faqs": len(next(
                        x["faqs"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "tags": len(next(
                        x["tags"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "signature_moments": len(next(
                        x["moments"] for x in EXPERIENCES
                        if x["code"] == experience.experience_code
                    )),
                    "media": 0,
                    "schedules": 0,
                    "bookings": 0,
                }

                for key, expected_value in expected.items():
                    actual = checks[key]
                    if actual != expected_value:
                        raise RuntimeError(
                            f"Verification failed for {experience.experience_code}: "
                            f"{key} expected {expected_value}, got {actual}."
                        )

                print(
                    f"VERIFIED {experience.experience_code} "
                    f"| all content counts correct "
                    f"| media=0 schedules=0 bookings=0"
                )

            print("\nAll batch records passed verification.")

            if apply_changes:
                db.session.commit()

                print("\n" + "=" * 110)
                print("BATCH 1 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(
                    f"Created {len(created)} complete Kenyan Coast experiences."
                )
                print(
                    "Inactive destination Malindi remains inactive."
                )
            else:
                db.session.rollback()

                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)
                print(
                    f"Validated {len(created)} complete experience records."
                )
                print(
                    "No database changes were committed."
                )
                print(
                    "Run with --apply only after reviewing the dry-run output."
                )

        except Exception:
            db.session.rollback()

            print("\n" + "=" * 110)
            print("BATCH FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)

            raise


def main():
    parser = argparse.ArgumentParser(
        description="Populate The Uncharted Route Kenyan Coast experience batch."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the batch. Default behavior is dry-run.",
    )

    args = parser.parse_args()

    populate(apply_changes=args.apply)


if __name__ == "__main__":
    main()
