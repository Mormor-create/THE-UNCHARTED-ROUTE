"""
===============================================================================
THE UNCHARTED ROUTE
BATCH 3 — EAST AFRICAN ISLANDS EXPERIENCE POPULATION
===============================================================================

Destinations:
    Zanzibar    ID 26 — ACTIVE
    Mauritius   ID 33 — ACTIVE
    Madagascar  ID 34 — ACTIVE

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
    - APPLY: python scripts/populate_east_african_islands_batch.py --apply

The batch is transactional. Any error rolls the entire batch back.

Research basis:
    Zanzibar: UNESCO confirms Stone Town's World Heritage status and its
    Swahili/Indian Ocean cultural fusion. Jozani is treated as a forest and
    conservation experience, with wildlife sightings explicitly non-guaranteed.

    Mauritius: official tourism material supports Le Morne, Black River Gorges,
    Chamarel and Port Louis as major heritage, nature and food/market anchors.

    Madagascar: official tourism material supports Andasibe, Morondava/Avenue
    of the Baobabs and Nosy Be as major wildlife, baobab and marine circuits.
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
# REUSABLE CMS IDS
# =============================================================================

CATEGORY_SAFARI = 1
CATEGORY_CULTURE = 3
CATEGORY_COASTAL = 4
CATEGORY_LUXURY = 5
CATEGORY_CULINARY = 9

CANCELLATION_POLICY_ID = 2
ACCESSIBILITY_EASY = 5
ACCESSIBILITY_MODERATE = 3
ACCESSIBILITY_COASTAL = 10

TAG_WILDLIFE = 1
TAG_CONSERVATION = 2
TAG_PHOTOGRAPHY = 4
TAG_HALF_DAY = 6
TAG_CULTURE = 12
TAG_CULINARY = 14
TAG_NATURE = 17
TAG_HISTORICAL = 19
TAG_ARCHITECTURE = 20
TAG_FOOD = 22
TAG_FARM = 23
TAG_COFFEE_TEA = 24
TAG_CITY = 27
TAG_PRIVATE = 30
TAG_BIRD = 9
TAG_FAMILY = 11
TAG_HIKING = 15
TAG_COASTAL = 13
TAG_MARINE = 26
TAG_WATER = 18
TAG_ISLAND = 25

MOMENT_WILDLIFE = 2
MOMENT_WILDLIFE_HABITAT = 3
MOMENT_BIRDS = 4
MOMENT_HIDDEN_NATURE = 6
MOMENT_VIEWPOINT = 7
MOMENT_TRAIL = 9
MOMENT_LANDSCAPES = 11
MOMENT_HERITAGE = 12
MOMENT_ARTISANS = 13
MOMENT_CULTURAL = 14
MOMENT_HISTORY = 15
MOMENT_ARCHITECTURE = 16
MOMENT_FARM_TABLE = 17
MOMENT_LOCAL_CUISINE = 19
MOMENT_RELAXATION = 29
MOMENT_EXTRAORDINARY = 30
MOMENT_MARINE = 24
MOMENT_OCEAN_VIEW = 25
MOMENT_PRIVATE_SUNSET = 22

# Existing wildlife species in the CMS are Kenya-focused. No unrelated species
# are attached to these island experiences merely to create wildlife counts.

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
# REUSABLE CMS IDS
# =============================================================================

CATEGORY_SAFARI = 1
CATEGORY_CULTURE = 3
CATEGORY_CULINARY = 9

CANCELLATION_POLICY_ID = 2
ACCESSIBILITY_PROFILE_ID = 5

TAG_WILDLIFE = 1
TAG_CONSERVATION = 2
TAG_PHOTOGRAPHY = 4
TAG_HALF_DAY = 6
TAG_CULTURE = 12
TAG_CULINARY = 14
TAG_NATURE = 17
TAG_HISTORICAL = 19
TAG_ARCHITECTURE = 20
TAG_FOOD = 22
TAG_FARM = 23
TAG_COFFEE_TEA = 24
TAG_CITY = 27
TAG_PRIVATE = 30
TAG_BIRD = 9
TAG_BIG_FIVE = 10
TAG_FAMILY = 11
TAG_HIKING = 15

MOMENT_SUNRISE = 1
MOMENT_WILDLIFE = 2
MOMENT_WILDLIFE_HABITAT = 3
MOMENT_BIRDS = 4
MOMENT_HIDDEN_NATURE = 6
MOMENT_VIEWPOINT = 7
MOMENT_TRAIL = 9
MOMENT_LANDSCAPES = 11
MOMENT_HERITAGE = 12
MOMENT_FARM_TABLE = 17
MOMENT_TEA = 18
MOMENT_LOCAL_CUISINE = 19

CONSERVATION_RHINO = 2
CONSERVATION_GREVEYS = 4
CONSERVATION_GIRAFFE = 5

# Existing wildlife species from the TUR CMS.
WILDLIFE_LION = 1
WILDLIFE_BLACK_RHINO = 2
WILDLIFE_GIRAFFE = 3
WILDLIFE_BUFFALO = 4
WILDLIFE_ZEBRA = 5
WILDLIFE_CHEETAH = 6
WILDLIFE_WHITE_RHINO = 7
WILDLIFE_HIPPO = 8


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


def pricing(one, two_three, four_plus, notes, currency="USD"):
    return [
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Explorer", "price": one[0], "currency": currency, "notes": notes},
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Signature", "price": one[1], "currency": currency, "notes": notes},
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Luxury", "price": one[2], "currency": currency, "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Explorer", "price": two_three[0], "currency": currency, "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Signature", "price": two_three[1], "currency": currency, "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Luxury", "price": two_three[2], "currency": currency, "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Explorer", "price": four_plus[0], "currency": currency, "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Signature", "price": four_plus[1], "currency": currency, "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Luxury", "price": four_plus[2], "currency": currency, "notes": notes},
    ]


def inc(title, description, icon):
    return {"title": title, "description": description, "icon": icon}


def exc(title, description, icon):
    return {"title": title, "description": description, "icon": icon}


def highlight(title, description, icon, highlight_type="Experience"):
    return {"title": title, "description": description, "icon": icon, "highlight_type": highlight_type, "featured": False}


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


def safety(title, description, category="General", icon="shield"):
    return {"title": title, "description": description, "category": category, "icon": icon}


def requirement(title, description, category="General", mandatory=False, icon="info"):
    return {"title": title, "description": description, "category": category, "mandatory": mandatory, "icon": icon}


def faq(question, answer, category="Booking", featured=False):
    return {"question": question, "answer": answer, "category": category, "featured": featured}


def wildlife(species_id, probability, season, time, notes, photography_notes=""):
    return {
        "species_id": species_id,
        "sighting_probability": probability,
        "best_season": season,
        "best_time_of_day": time,
        "guide_notes": notes,
        "photography_notes": photography_notes,
        "featured": False,
        "active": True,
    }


def experience(
    *, code, slug, title, destination_id, category_id, short_description,
    description, duration, meeting_point, location, price_from, minimum_people,
    maximum_people, minimum_age, difficulty, meta_title, meta_description,
    conservation_story_id, tags, moments, pricing_rows, itinerary_rows,
    inclusions, exclusions, highlights, addons, packing_rows, safety_rows,
    requirements, faqs, wildlife_rows=None, display_order=1,
):
    return {
        "code": code,
        "slug": slug,
        "title": title,
        "destination_id": destination_id,
        "category_id": category_id,
        "short_description": short_description,
        "description": description,
        "duration": duration,
        "meeting_point": meeting_point,
        "location": location,
        "price_from": price_from,
        "minimum_people": minimum_people,
        "maximum_people": maximum_people,
        "minimum_age": minimum_age,
        "difficulty": difficulty,
        "featured_image": slug,
        "banner_image": None,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "featured": False,
        "show_on_homepage": False,
        "active": True,
        "display_order": display_order,
        "cancellation_policy_id": CANCELLATION_POLICY_ID,
        "accessibility_profile_id": ACCESSIBILITY_PROFILE_ID,
        "conservation_story_id": conservation_story_id,
        "tags": tags,
        "moments": moments,
        "pricing": pricing_rows,
        "itinerary": itinerary_rows,
        "inclusions": inclusions,
        "exclusions": exclusions,
        "highlights": highlights,
        "addons": addons,
        "packing": packing_rows,
        "safety": safety_rows,
        "requirements": requirements,
        "faqs": faqs,
        "wildlife": wildlife_rows or [],
    }



# =============================================================================
# EXPERIENCE DATA
# =============================================================================

EXPERIENCES = [
    # -------------------------------------------------------------------------
    # ZANZIBAR — ACTIVE DESTINATION ID 26
    # -------------------------------------------------------------------------
    experience(
        code="EA-ZNZ-001",
        slug="stone-town-heritage-swahili-culture",
        title="Stone Town Heritage — Architecture, History & Swahili Culture",
        destination_id=26,
        category_id=CATEGORY_CULTURE,
        short_description="A guided Stone Town journey through Swahili architecture, Indian Ocean trade history, living neighbourhoods and Zanzibar's layered cultural heritage.",
        description="Explore Stone Town with a local guide through a carefully paced walking experience that connects carved doors, courtyard houses, historic waterfront spaces, markets and the wider story of Zanzibar's Swahili and Indian Ocean heritage. The route focuses on interpretation rather than simply collecting landmarks, with time for photography and respectful engagement with the living community.",
        duration="Half Day",
        meeting_point="Confirmed Stone Town hotel or agreed central meeting point.",
        location="Stone Town, Zanzibar, Tanzania",
        price_from=85,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Stone Town Heritage & Swahili Culture | The Uncharted Route",
        meta_description="Discover Stone Town's architecture, Swahili heritage, Indian Ocean history and living culture with a private guided experience.",
        conservation_story_id=None,
        tags=[TAG_CULTURE, TAG_HISTORICAL, TAG_ARCHITECTURE, TAG_CITY, TAG_PHOTOGRAPHY],
        moments=[MOMENT_HERITAGE, MOMENT_HISTORY, MOMENT_ARCHITECTURE, MOMENT_CULTURAL],
        pricing_rows=pricing((145, 195, 295), (115, 165, 245), (95, 135, 205), "Indicative TUR selling price per person in USD. Museum admissions, premium guides and special access are confirmed separately.", "USD"),
        itinerary_rows=[
            itinerary("Welcome & Heritage Briefing", "Morning / Afternoon", "Meet the guide and begin with the story of Stone Town as a Swahili coastal trading town shaped by African, Arab, Indian and European influences."),
            itinerary("Historic Streets & Architecture", "Main Activity", "Walk through selected historic streets, carved-door houses, courtyards, bazaars and waterfront areas while discussing architecture and everyday life."),
            itinerary("Markets, Heritage & Local Stories", "Later Activity", "Explore an agreed market or heritage stop and hear local perspectives on food, craft, trade and the continuing life of the old town."),
            itinerary("Seafront Reflection & Farewell", "Final Hour", "Finish near the waterfront with time for photography and a final conversation about Zanzibar's cultural layers."),
        ],
        inclusions=[
            inc("Private Experience Coordination", "TUR coordination of the agreed walking route and guide.", "route"),
            inc("Local Heritage Guide", "A locally based guide providing historical and cultural interpretation.", "user"),
            inc("Guided Heritage Walk", "A curated walking route through selected Stone Town areas.", "landmark"),
            inc("Photography Stops", "Time for respectful architecture and street photography.", "camera"),
        ],
        exclusions=[
            exc("Museum Admissions", "Entry to museums or paid heritage sites unless explicitly included in the quotation.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Personal Purchases", "Shopping, gratuities and personal expenses are excluded.", "wallet"),
        ],
        highlights=[
            highlight("Living Swahili Heritage", "Experience Stone Town as a living neighbourhood rather than an open-air museum.", "landmark", "Heritage"),
            highlight("Indian Ocean Architecture", "Read the town through carved doors, balconies, courtyards and layered building traditions.", "building", "Architecture"),
            highlight("Stories Behind the Streets", "Connect trade, migration, religion and everyday life through local interpretation.", "book-open", "History"),
            highlight("Golden-Hour Waterfront", "End with an atmospheric seafront perspective when timing allows.", "sun", "Scenic"),
        ],
        addons=[addon("Private Heritage Specialist", "Upgrade to a specialist heritage guide.", "Request a specialist heritage or architecture guide subject to availability.", 45, "Per Booking")],
        packing_rows=[
            packing("Comfortable Walking Shoes", "Wear shoes suitable for uneven historic streets.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Light Clothing", "Wear breathable clothing suitable for Zanzibar's warm climate.", "Clothing", "shirt"),
            packing("Water Bottle", "Carry drinking water for the walk.", "General", "bottle-water"),
        ],
        safety_rows=[
            safety("Stay With the Guide", "Stone Town has narrow streets and busy areas; remain with the guide at agreed meeting points.", "Urban Safety", "map"),
            safety("Respect Local Culture", "Dress and behave respectfully around religious sites, homes and community spaces.", "Cultural Safety", "heart"),
            safety("Street Awareness", "Watch for traffic, bicycles, motorcycles and uneven surfaces.", "Urban Safety", "alert-triangle"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable walking for several hours on uneven urban surfaces.", "Mobility", True, "shoe"),
            requirement("Respectful Dress", "Modest clothing is recommended, especially when entering religious or community spaces.", "Culture", True, "shirt"),
        ],
        faqs=[
            faq("Is Stone Town a UNESCO World Heritage Site?", "Yes. Stone Town was inscribed on the UNESCO World Heritage List in 2000 and is recognised for its Swahili coastal urban fabric and cultural fusion.", "Heritage", True),
            faq("Is this a strenuous walking tour?", "No. It is an easy-paced heritage walk, although the streets can be uneven and the tropical heat can make walking tiring.", "Activity"),
            faq("Can we visit a museum?", "Yes, where the selected route and opening hours allow; admission is handled according to the confirmed quotation.", "Heritage"),
            faq("Can this be private?", "Yes. The standard TUR format is privately coordinated for the confirmed party.", "Booking"),
        ],
        wildlife_rows=[],
        display_order=1,
    ),

    experience(
        code="EA-ZNZ-002",
        slug="jozani-forest-red-colobus-conservation",
        title="Jozani Forest — Red Colobus, Mangroves & Conservation",
        destination_id=26,
        category_id=CATEGORY_SAFARI,
        short_description="A guided nature experience in Jozani combining forest interpretation, red colobus conservation, native flora and the wider Zanzibar wetland landscape.",
        description="Discover Jozani's forest ecosystem with a local guide, focusing on the endemic Zanzibar red colobus and the relationship between forest, wildlife and community conservation. The route may include the forest trail and mangrove boardwalk where operating conditions permit. Wildlife remains wild: red colobus and other encounters are possible but never guaranteed.",
        duration="Half Day",
        meeting_point="Confirmed Zanzibar accommodation or agreed Jozani-area meeting point.",
        location="Jozani, Unguja, Zanzibar, Tanzania",
        price_from=95,
        minimum_people=1, maximum_people=8, minimum_age=6, difficulty="Easy",
        meta_title="Jozani Forest & Red Colobus Experience | The Uncharted Route",
        meta_description="Explore Jozani Forest with guided wildlife interpretation, red colobus conservation and Zanzibar's native forest landscape.",
        conservation_story_id=None,
        tags=[TAG_WILDLIFE, TAG_CONSERVATION, TAG_NATURE, TAG_PHOTOGRAPHY, TAG_FAMILY],
        moments=[MOMENT_WILDLIFE, MOMENT_WILDLIFE_HABITAT, MOMENT_HIDDEN_NATURE],
        pricing_rows=pricing((155, 215, 325), (125, 175, 265), (105, 145, 225), "Indicative TUR selling price per person in USD. Forest/site fees and any specialist conservation guide are confirmed before booking.", "USD"),
        itinerary_rows=[
            itinerary("Forest Introduction", "Morning / Afternoon", "Meet the guide and receive an introduction to Jozani's forest ecosystem, conservation work and visitor guidelines."),
            itinerary("Forest Trail & Red Colobus Search", "Main Activity", "Walk the approved forest route while looking for Zanzibar red colobus and learning about native plants and forest ecology."),
            itinerary("Mangrove Boardwalk", "Later Activity", "Where open and conditions permit, continue to the mangrove area for interpretation of the wetland ecosystem and its role in the wider landscape."),
            itinerary("Conservation Reflection & Return", "Final Hour", "Discuss conservation pressures and responsible visitation before returning to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the confirmed Jozani visit and pickup.", "route"),
            inc("Local Nature Guide", "Guided interpretation of forest ecology and wildlife.", "user"),
            inc("Forest Exploration", "Access to the approved visitor route according to current park/site rules.", "leaf"),
            inc("Wildlife Observation", "Time to look for red colobus and other naturally occurring forest wildlife.", "paw-print"),
        ],
        exclusions=[
            exc("Site Entry Fees", "Applicable Jozani/site charges unless explicitly included in the confirmed quotation.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Private Vehicle Upgrade", "Premium private transport beyond the confirmed arrangement is excluded unless selected.", "car"),
        ],
        highlights=[
            highlight("Zanzibar Red Colobus", "Look for the endemic Zanzibar red colobus in its natural forest habitat; sightings are never guaranteed.", "paw-print", "Wildlife"),
            highlight("Forest Ecology", "Learn how native forest and wetland habitats support Zanzibar's biodiversity.", "leaf", "Nature"),
            highlight("Mangrove Landscape", "Where operating conditions permit, connect the forest experience with the coastal wetland ecosystem.", "tree", "Conservation"),
            highlight("Responsible Wildlife Viewing", "Explore with a guide who prioritises distance, quiet observation and habitat respect.", "shield", "Conservation"),
        ],
        addons=[addon("Private Conservation Guide", "Request a specialist conservation-focused guide.", "A specialist guide may be arranged subject to availability and advance confirmation.", 55, "Per Booking")],
        packing_rows=[
            packing("Closed Walking Shoes", "Wear shoes suitable for forest trails and boardwalk surfaces.", "Footwear", "shoe"),
            packing("Insect Repellent", "Useful in forest and wetland environments.", "Health", "bug"),
            packing("Sun & Rain Protection", "Carry sunscreen, a hat and a light rain layer.", "Health", "cloud-rain"),
            packing("Binoculars", "Useful for observing wildlife without approaching it.", "Equipment", "binoculars"),
        ],
        safety_rows=[
            safety("Do Not Approach Wildlife", "Never feed, touch or chase red colobus or other wildlife.", "Wildlife", "paw-print"),
            safety("Stay on Approved Routes", "Remain on designated paths and follow guide instructions.", "Forest Safety", "route"),
            safety("Forest Conditions", "Roots, wet ground and slippery surfaces may occur after rain.", "Terrain", "alert-triangle"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable with an easy forest walk.", "Mobility", True, "shoe"),
            requirement("Wildlife Respect", "Guests must follow wildlife-viewing and no-feeding rules.", "Conservation", True, "shield"),
        ],
        faqs=[
            faq("Will we definitely see red colobus?", "No. They are wild animals and sightings depend on their movement, weather and forest conditions.", "Wildlife", True),
            faq("Is Jozani suitable for children?", "Yes, the standard forest route can suit families when children can follow guide instructions.", "Family"),
            faq("Can we walk through mangroves?", "A mangrove boardwalk may be included when open and conditions permit.", "Activity"),
            faq("What should we wear?", "Comfortable closed shoes, light clothing, sun protection and insect repellent are recommended.", "Packing"),
        ],
        wildlife_rows=[],
        display_order=2,
    ),

    experience(
        code="EA-ZNZ-003",
        slug="zanzibar-dhow-sandbank-marine-sunset",
        title="Zanzibar by Dhow — Sandbank, Marine Life & Sunset",
        destination_id=26,
        category_id=CATEGORY_COASTAL,
        short_description="A private coastal escape combining traditional dhow sailing, a sandbank stop, reef-edge marine viewing and a Zanzibar sunset.",
        description="Spend a relaxed day on the water with a privately coordinated dhow experience around Zanzibar's coastal islands and sandbanks. The exact sandbank, reef stop and sailing route depend on tides, weather and local operating conditions. Snorkelling or shallow-water viewing may be included where conditions are safe; marine life is wild and sightings are never guaranteed.",
        duration="Full Day",
        meeting_point="Confirmed coastal departure point or hotel pickup according to the selected route.",
        location="Zanzibar coastal waters, Tanzania",
        price_from=165,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Zanzibar Private Dhow & Sandbank Experience | The Uncharted Route",
        meta_description="Sail Zanzibar by dhow with a private sandbank, marine viewing and sunset coastal escape.",
        conservation_story_id=7,
        tags=[TAG_COASTAL, TAG_MARINE, TAG_WATER, TAG_ISLAND, TAG_PRIVATE],
        moments=[MOMENT_MARINE, MOMENT_OCEAN_VIEW, MOMENT_PRIVATE_SUNSET, MOMENT_EXTRAORDINARY],
        pricing_rows=pricing((265, 365, 525), (215, 295, 425), (175, 245, 365), "Indicative TUR selling price per person in USD. Boat, marine fees, lunch and weather-dependent route details are confirmed before booking.", "USD"),
        itinerary_rows=[
            itinerary("Coastal Departure & Safety Briefing", "Morning", "Meet at the confirmed departure point, receive the boat and water-safety briefing, and begin the coastal journey."),
            itinerary("Dhow Sailing & Sandbank", "Morning–Midday", "Sail toward the selected sandbank or island area, with the route adjusted for tide and weather conditions."),
            itinerary("Marine Viewing & Coastal Lunch", "Midday–Afternoon", "Enjoy a safe shallow-water or snorkelling stop where conditions permit, followed by a confirmed coastal lunch arrangement."),
            itinerary("Sunset Sail & Return", "Late Afternoon", "Cruise back through the changing light and enjoy the sunset before returning to the agreed landing point."),
        ],
        inclusions=[
            inc("Private Dhow Coordination", "TUR coordination of the confirmed private or exclusive dhow arrangement.", "ship"),
            inc("Boat Crew", "Local dhow crew for navigation and safe operation.", "user"),
            inc("Sandbank / Coastal Stop", "A tide- and weather-dependent coastal stop at the selected route.", "island"),
            inc("Marine Experience", "Time for safe marine viewing or snorkelling where included and conditions permit.", "waves"),
        ],
        exclusions=[
            exc("Marine Park / Site Fees", "Applicable marine or site charges unless explicitly included.", "ticket"),
            exc("Premium Seafood Upgrade", "Special dining upgrades are excluded unless selected.", "utensils"),
            exc("Weather-Related Extensions", "Unexpected additional transport or rescheduling costs may apply when weather disrupts the confirmed route.", "cloud"),
        ],
        highlights=[
            highlight("Traditional Dhow Sailing", "Experience Zanzibar's coastal waters aboard a locally operated dhow.", "ship", "Coastal"),
            highlight("Private Sandbank Escape", "Pause on a tide-dependent sandbank for swimming, photography or quiet relaxation.", "island", "Beach"),
            highlight("Marine Life Possibilities", "Look for reef fish, sea life and other marine encounters without any guarantee of a particular sighting.", "fish", "Marine"),
            highlight("Sunset on the Indian Ocean", "Finish the day with an intimate sunset cruise over the Zanzibar coast.", "sun", "Sunset"),
        ],
        addons=[addon("Premium Seafood Lunch", "Upgrade the coastal lunch.", "A premium seafood lunch can be arranged where the selected supplier offers it, subject to availability and dietary requirements.", 35, "Per Person")],
        packing_rows=[
            packing("Swimwear", "Bring swimwear if participating in water activities.", "Clothing", "waves"),
            packing("Reef-Safe Sun Protection", "Use reef-conscious sunscreen and bring sunglasses and a hat.", "Health", "sun"),
            packing("Dry Bag", "Protect phones, cameras and valuables from spray and splashes.", "Equipment", "bag"),
            packing("Light Cover-Up", "Bring a light cover-up for sun protection and boat comfort.", "Clothing", "shirt"),
        ],
        safety_rows=[
            safety("Life Jacket & Boat Rules", "Follow the crew's boarding, seating and life-jacket instructions.", "Marine Safety", "life-buoy"),
            safety("Swimming Conditions", "Only enter the water when the crew confirms that conditions and the selected site are safe.", "Water", "waves"),
            safety("Tide & Weather", "Sandbank access and sailing routes can change with tides, wind and weather.", "Weather", "cloud"),
        ],
        requirements=[
            requirement("Water Activity Disclosure", "Tell TUR about swimming limitations, mobility concerns or medical considerations affecting water activities.", "Health", False, "info"),
            requirement("Boat Safety Compliance", "Guests must follow crew instructions throughout the marine experience.", "Safety", True, "life-buoy"),
        ],
        faqs=[
            faq("Is snorkelling guaranteed?", "No. Water activity depends on the selected route, visibility, tide, weather and operator safety decision.", "Marine", True),
            faq("Will we see dolphins?", "Dolphins or other marine life may be encountered, but no wildlife sighting is guaranteed.", "Wildlife"),
            faq("Can non-swimmers join?", "Yes. Non-swimmers can enjoy the dhow and sandbank experience without entering the water, subject to safe boarding arrangements.", "Family"),
            faq("Can the route change?", "Yes. Tides, wind, sea conditions and local operating decisions can change the sandbank or sailing route.", "Weather"),
        ],
        wildlife_rows=[],
        display_order=3,
    ),

    # -------------------------------------------------------------------------
    # MAURITIUS — ACTIVE DESTINATION ID 33
    # -------------------------------------------------------------------------
    experience(
        code="EA-MRU-001",
        slug="le-morne-black-river-gorges-nature-heritage",
        title="Le Morne & Black River Gorges — Heritage, Hiking & Nature",
        destination_id=33,
        category_id=CATEGORY_CULTURE,
        short_description="A curated southwest Mauritius journey combining Le Morne's heritage landscape with Black River Gorges forest, viewpoints and nature.",
        description="Connect Mauritius's natural grandeur with its human history on a southwest island journey. The experience combines the Le Morne cultural landscape with selected Black River Gorges viewpoints or trails, depending on fitness, weather and current access. A summit hike is a separate higher-intensity option and is not assumed in the standard route.",
        duration="Full Day",
        meeting_point="Confirmed Mauritius accommodation or agreed southwest meeting point.",
        location="Le Morne & Black River Gorges, Mauritius",
        price_from=175,
        minimum_people=1, maximum_people=6, minimum_age=12, difficulty="Moderate",
        meta_title="Le Morne & Black River Gorges Experience | The Uncharted Route",
        meta_description="Explore Le Morne heritage and Black River Gorges landscapes through a curated Mauritius nature and culture experience.",
        conservation_story_id=None,
        tags=[TAG_CULTURE, TAG_HISTORICAL, TAG_HIKING, TAG_NATURE, TAG_PHOTOGRAPHY],
        moments=[MOMENT_HERITAGE, MOMENT_TRAIL, MOMENT_VIEWPOINT, MOMENT_LANDSCAPES],
        pricing_rows=pricing((285, 395, 595), (235, 325, 485), (195, 275, 405), "Indicative TUR selling price per person in USD. Park access, specialist hiking guide and private transport are confirmed against the selected route.", "USD"),
        itinerary_rows=[
            itinerary("Southwest Departure & Le Morne Story", "Morning", "Meet the guide and travel toward Le Morne while introducing the mountain's cultural landscape and its history of refuge and freedom."),
            itinerary("Le Morne Viewpoint / Optional Hike", "Morning", "Explore the cultural landscape and, where booked and conditions permit, undertake the appropriate guided walking section."),
            itinerary("Black River Gorges", "Afternoon", "Continue into the national park for a selected trail, viewpoint or waterfall-focused nature stop according to the group's ability and current conditions."),
            itinerary("Scenic Return", "Late Afternoon", "Finish with a final southwest landscape stop before returning to the confirmed accommodation."),
        ],
        inclusions=[
            inc("Private Route Coordination", "TUR coordination of the selected southwest itinerary.", "route"),
            inc("Local Driver-Guide", "Driver-guide support and landscape interpretation throughout the route.", "user"),
            inc("Guided Nature Walk", "A selected easy-to-moderate walk according to the confirmed itinerary.", "footprints"),
            inc("Scenic & Heritage Stops", "Curated stops at Le Morne and Black River Gorges.", "mountain"),
        ],
        exclusions=[
            exc("Specialist Summit Guide", "A specialist guide for a full Le Morne summit hike is excluded unless specifically booked.", "mountain"),
            exc("Meals & Drinks", "Food and drinks unless explicitly included.", "utensils"),
            exc("Optional Activity Fees", "Separate adventure or attraction fees are excluded unless selected.", "ticket"),
        ],
        highlights=[
            highlight("Le Morne Cultural Landscape", "Understand the mountain's significance as a symbol of suffering, resistance and freedom.", "landmark", "Heritage"),
            highlight("Black River Gorges", "Explore Mauritius's largest national park through selected trails and viewpoints.", "leaf", "Nature"),
            highlight("Mountain & Ocean Views", "Capture dramatic relationships between volcanic mountains, forest and lagoon.", "mountain", "Scenic"),
            highlight("Guided Interpretation", "Travel with context connecting ecology, history and landscape.", "book-open", "Learning"),
        ],
        addons=[addon("Le Morne Summit Upgrade", "Upgrade to a guided summit-focused hike.", "A higher-intensity summit itinerary can be arranged subject to guide availability, weather and guest fitness.", 95, "Per Person")],
        packing_rows=[
            packing("Hiking Shoes", "Wear sturdy shoes suitable for uneven trails.", "Footwear", "shoe", True, True),
            packing("Water", "Carry sufficient drinking water for outdoor walking.", "General", "bottle-water", True, True),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Light Rain Layer", "Mountain and forest weather can change quickly.", "Clothing", "cloud-rain"),
        ],
        safety_rows=[
            safety("Use a Qualified Guide", "Mountain routes should be undertaken with an appropriate guide and only on the confirmed route.", "Mountain Safety", "shield"),
            safety("Weather Awareness", "Summit or trail activity may be changed when wind, rain or visibility makes conditions unsuitable.", "Weather", "cloud"),
            safety("Uneven Terrain", "Expect rocks, roots, slopes and changing trail surfaces.", "Terrain", "alert-triangle"),
        ],
        requirements=[
            requirement("Moderate Fitness", "Guests selecting the walking component should be comfortable on uneven terrain and inclines.", "Mobility", True, "footprints"),
            requirement("Weather Flexibility", "Guests must accept route changes when mountain or park conditions require them.", "Safety", True, "cloud"),
        ],
        faqs=[
            faq("Is this a full Le Morne summit hike?", "Not by default. The standard experience includes the cultural landscape and a suitable walking section; a summit-focused upgrade is separately arranged.", "Activity", True),
            faq("Is Black River Gorges suitable for beginners?", "Yes. The park has routes ranging from easier walks to challenging trails, and TUR selects the route according to the confirmed itinerary.", "Hiking"),
            faq("Can the hike be cancelled?", "Yes. Weather and trail conditions can require a safer alternative route.", "Weather"),
            faq("What is Le Morne's significance?", "Le Morne is a UNESCO World Heritage cultural landscape associated with the history of escaped enslaved people and is widely recognised as a symbol of freedom.", "Heritage"),
        ],
        wildlife_rows=[],
        display_order=4,
    ),

    experience(
        code="EA-MRU-002",
        slug="chamarel-seven-coloured-earth-waterfall",
        title="Chamarel — Seven Coloured Earth, Waterfall & Island Landscapes",
        destination_id=33,
        category_id=CATEGORY_CULINARY,
        short_description="A southwest Mauritius discovery combining Chamarel's geological landscapes, waterfall viewpoints, native forest and optional local rum or tasting experiences.",
        description="Discover the volcanic landscapes of southwest Mauritius through a relaxed Chamarel journey. Visit the Seven Coloured Earth and Chamarel Waterfall viewpoints, with optional native-forest or local tasting elements depending on the selected package. The experience prioritises interpretation of geology, landscape and local production rather than rushing between attractions.",
        duration="Full Day",
        meeting_point="Confirmed Mauritius accommodation or agreed southwest meeting point.",
        location="Chamarel, Mauritius",
        price_from=155,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Chamarel Seven Coloured Earth & Waterfall | The Uncharted Route",
        meta_description="Explore Chamarel's Seven Coloured Earth, waterfall, volcanic landscapes and local flavours on a curated Mauritius day experience.",
        conservation_story_id=None,
        tags=[TAG_NATURE, TAG_PHOTOGRAPHY, TAG_CULINARY, TAG_FOOD, TAG_PRIVATE],
        moments=[MOMENT_HIDDEN_NATURE, MOMENT_VIEWPOINT, MOMENT_LANDSCAPES, MOMENT_FARM_TABLE],
        pricing_rows=pricing((245, 335, 495), (205, 285, 415), (165, 235, 345), "Indicative TUR selling price per person in USD. Attraction admissions, tastings and premium transport are confirmed in the selected package.", "USD"),
        itinerary_rows=[
            itinerary("Southwest Departure", "Morning", "Collect guests and travel into the southwest highlands with an introduction to the region's volcanic landscape."),
            itinerary("Chamarel Waterfall", "Morning", "Visit the waterfall viewpoints and learn about the geology and landscape that shape the area."),
            itinerary("Seven Coloured Earth & Forest", "Afternoon", "Explore the coloured-earth landscape and, where selected, add a native-forest or scenic viewpoint stop."),
            itinerary("Local Tasting & Return", "Late Afternoon", "Finish with a selected local tasting or rum-country experience where included before returning to the accommodation."),
        ],
        inclusions=[
            inc("Private Experience Coordination", "TUR coordination of the selected Chamarel route.", "route"),
            inc("Driver-Guide", "Driver-guide support and interpretation throughout the day.", "user"),
            inc("Scenic Attraction Visits", "Visits to the confirmed Chamarel viewpoints and attractions.", "mountain"),
            inc("Landscape Interpretation", "Guided explanation of geology, vegetation and local production.", "leaf"),
        ],
        exclusions=[
            exc("Attraction Admissions", "Entry fees are excluded unless explicitly included in the selected package.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Alcoholic Tasting", "Alcoholic tastings are excluded unless selected and legally available to the guest.", "glass"),
        ],
        highlights=[
            highlight("Seven Coloured Earth", "See the distinctive multicoloured volcanic earth formations of Chamarel.", "mountain", "Geology"),
            highlight("Chamarel Waterfall", "Take in the dramatic waterfall from the available viewing areas.", "droplets", "Nature"),
            highlight("Volcanic Landscapes", "Connect the island's scenery with its volcanic geological story.", "globe", "Landscape"),
            highlight("Local Flavours", "Add a tasting element to connect landscape with Mauritian production.", "cup-saucer", "Culinary"),
        ],
        addons=[addon("Premium Rum & Local Tasting", "Add a curated local tasting.", "A premium tasting can be arranged at a confirmed licensed venue, subject to availability and age requirements.", 45, "Per Person")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes for scenic paths and viewpoints.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water Bottle", "Carry water throughout the day.", "General", "bottle-water"),
            packing("Light Rain Layer", "Southwest weather can change quickly.", "Clothing", "cloud-rain"),
        ],
        safety_rows=[
            safety("Stay on Viewing Paths", "Remain within marked visitor areas around geological features and waterfalls.", "Site Safety", "route"),
            safety("Slippery Surfaces", "Rain can make paths and viewing areas slippery.", "Terrain", "alert-triangle"),
            safety("Tasting Responsibility", "Any alcohol tasting is optional and should never be combined with unsafe driving or activities.", "Wellbeing", "shield"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable with short walks on visitor paths.", "Mobility", True, "shoe"),
            requirement("Age Requirement for Alcohol", "Guests selecting alcohol tastings must meet the applicable legal age requirements.", "Dining", True, "info"),
        ],
        faqs=[
            faq("Is the waterfall accessible all year?", "The waterfall viewpoint is generally accessible, but weather and site conditions can affect the exact visitor route.", "Activity", True),
            faq("Can children join?", "Yes. The standard scenic route is suitable for families, subject to normal site safety rules.", "Family"),
            faq("Is rum tasting included?", "Not by default. It is an optional add-on or package component at a confirmed licensed venue.", "Dining"),
            faq("Can we add a hike?", "A longer guided forest or mountain walk can be arranged separately where conditions and guide availability allow.", "Hiking"),
        ],
        wildlife_rows=[],
        display_order=5,
    ),

    experience(
        code="EA-MRU-003",
        slug="port-louis-heritage-markets-flavours",
        title="Port Louis — Heritage, Markets & Mauritian Flavours",
        destination_id=33,
        category_id=CATEGORY_CULINARY,
        short_description="A guided Port Louis discovery combining heritage landmarks, markets, multicultural food traditions and the city's everyday energy.",
        description="Explore Mauritius's capital through its layered history and food culture. Walk through selected heritage areas, markets and waterfront spaces while learning how African, Indian, Chinese, French and Creole influences have shaped the city's identity. The route is designed around tasting and interpretation rather than a generic sightseeing checklist.",
        duration="Half Day",
        meeting_point="Confirmed Port Louis hotel or agreed central meeting point.",
        location="Port Louis, Mauritius",
        price_from=105,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Port Louis Heritage & Food Experience | The Uncharted Route",
        meta_description="Discover Port Louis through heritage, markets, multicultural food and Mauritian local stories.",
        conservation_story_id=None,
        tags=[TAG_CITY, TAG_CULTURE, TAG_HISTORICAL, TAG_ARCHITECTURE, TAG_FOOD],
        moments=[MOMENT_HERITAGE, MOMENT_HISTORY, MOMENT_ARCHITECTURE, MOMENT_LOCAL_CUISINE],
        pricing_rows=pricing((175, 245, 365), (145, 205, 305), (115, 165, 245), "Indicative TUR selling price per person in USD. Food tastings, attraction admissions and private transport are confirmed in the final quotation.", "USD"),
        itinerary_rows=[
            itinerary("City Welcome & Heritage Introduction", "Morning / Afternoon", "Meet the guide and introduce Port Louis's history as a multicultural Indian Ocean port."),
            itinerary("Markets & Everyday Port Louis", "Main Activity", "Explore selected market and neighbourhood areas while learning about local produce, crafts and daily commerce."),
            itinerary("Heritage & Waterfront", "Later Activity", "Visit selected heritage landmarks and waterfront areas, with time for architecture and photography."),
            itinerary("Mauritian Tasting", "Final Hour", "Sample selected local flavours and discuss the cultural influences behind Mauritian cuisine before concluding."),
        ],
        inclusions=[
            inc("Private City Coordination", "TUR coordination of the agreed Port Louis route.", "route"),
            inc("Local Guide", "Local cultural interpretation throughout the walk.", "user"),
            inc("Heritage Walk", "Guided exploration of selected city landmarks and neighbourhoods.", "landmark"),
            inc("Food Tasting", "Selected local tastings according to the confirmed package.", "utensils"),
        ],
        exclusions=[
            exc("Full Meal", "The experience includes selected tastings rather than a full restaurant meal unless explicitly upgraded.", "utensils"),
            exc("Museum Admissions", "Paid museum or attraction entry is excluded unless included in the quotation.", "ticket"),
            exc("Personal Shopping", "Market purchases and personal expenses are excluded.", "shopping-bag"),
        ],
        highlights=[
            highlight("Multicultural Mauritius", "See how several cultural traditions meet in the capital's streets, markets and food.", "users", "Culture"),
            highlight("Port Louis Markets", "Experience the energy of local commerce and produce markets.", "shopping-bag", "Markets"),
            highlight("Indian Ocean Heritage", "Connect the capital's architecture and port history with wider Indian Ocean exchange.", "landmark", "History"),
            highlight("Taste of Mauritius", "Sample local flavours while learning their cultural background.", "utensils", "Culinary"),
        ],
        addons=[addon("Private Chef-Led Tasting", "Upgrade the food component with a curated tasting.", "A chef-led or premium tasting experience can be requested subject to venue availability.", 55, "Per Person")],
        packing_rows=[
            packing("Comfortable Shoes", "Wear shoes suitable for several hours of city walking.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Reusable Water Bottle", "Carry water during the walk.", "General", "bottle-water"),
            packing("Small Day Bag", "A compact bag is useful for personal items.", "Equipment", "bag"),
        ],
        safety_rows=[
            safety("Urban Awareness", "Keep valuables secure and follow the guide through busy market areas.", "Urban Safety", "shield"),
            safety("Food Allergies", "Tell the guide about allergies or dietary restrictions before tasting.", "Food Safety", "alert-triangle"),
            safety("Respect Market Vendors", "Ask before photographing people, stalls or private activities.", "Cultural Safety", "camera"),
        ],
        requirements=[
            requirement("Dietary Disclosure", "Share dietary restrictions and food allergies before the experience.", "Dining", True, "utensils"),
            requirement("Comfortable Walking", "Guests should be comfortable walking through busy urban areas.", "Mobility", True, "shoe"),
        ],
        faqs=[
            faq("What kind of food will we taste?", "The final tasting depends on the confirmed route and may draw from Mauritian Creole, Indian, Chinese, French and other island influences.", "Dining", True),
            faq("Is this suitable for children?", "Yes, provided children are comfortable with city walking and the selected food stops.", "Family"),
            faq("Can we skip the food tasting?", "Yes. The experience can be configured as a heritage-focused city walk.", "Customisation"),
            faq("Can we visit Aapravasi Ghat?", "Where opening hours and the selected route permit, a heritage-site visit can be incorporated with admission handled separately.", "Heritage"),
        ],
        wildlife_rows=[],
        display_order=6,
    ),

    # -------------------------------------------------------------------------
    # MADAGASCAR — ACTIVE DESTINATION ID 34
    # -------------------------------------------------------------------------
    experience(
        code="EA-MDG-001",
        slug="andasibe-indri-rainforest-wildlife",
        title="Andasibe — Indri, Rainforest & Wildlife Discovery",
        destination_id=34,
        category_id=CATEGORY_SAFARI,
        short_description="A rainforest experience focused on Madagascar's endemic wildlife, especially the indri, with guided forest interpretation and conservation-minded viewing.",
        description="Explore the Andasibe rainforest with a specialist local guide in search of Madagascar's extraordinary endemic wildlife. The experience centres on indri and other lemurs, native birds and forest ecology. Wildlife sightings depend on animal movement, weather and forest conditions, and no species is guaranteed.",
        duration="Full Day",
        meeting_point="Confirmed Andasibe accommodation or agreed park-area meeting point.",
        location="Andasibe, Analanjirofo Region, Madagascar",
        price_from=195,
        minimum_people=1, maximum_people=6, minimum_age=8, difficulty="Moderate",
        meta_title="Andasibe Indri & Rainforest Wildlife | The Uncharted Route",
        meta_description="Explore Madagascar's Andasibe rainforest with guided indri, lemur and endemic wildlife viewing.",
        conservation_story_id=None,
        tags=[TAG_WILDLIFE, TAG_CONSERVATION, TAG_BIRD, TAG_PHOTOGRAPHY, TAG_NATURE],
        moments=[MOMENT_WILDLIFE, MOMENT_WILDLIFE_HABITAT, MOMENT_BIRDS, MOMENT_TRAIL],
        pricing_rows=pricing((315, 435, 645), (255, 355, 525), (215, 295, 435), "Indicative TUR selling price per person in USD. Park fees, specialist guiding, transfers and night-walk components are confirmed against the selected itinerary.", "USD"),
        itinerary_rows=[
            itinerary("Forest Briefing & Park Entry", "Morning", "Meet the guide, review forest etiquette and enter the confirmed protected-area route."),
            itinerary("Indri & Lemur Search", "Morning–Midday", "Walk through rainforest habitat listening and looking for indri, lemurs and other endemic species. Sightings are never guaranteed."),
            itinerary("Forest Ecology & Birding", "Afternoon", "Continue through suitable trails with time for birds, plants, insects and wider ecological interpretation."),
            itinerary("Final Forest Walk & Return", "Late Afternoon", "Complete the selected route and return to the confirmed accommodation or meeting point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the confirmed Andasibe route and local guiding.", "route"),
            inc("Local Wildlife Guide", "A local guide experienced in forest wildlife interpretation.", "user"),
            inc("Forest Exploration", "Guided access to the confirmed visitor route.", "leaf"),
            inc("Wildlife Observation", "Dedicated time for lemur, bird and forest wildlife observation.", "paw-print"),
        ],
        exclusions=[
            exc("Park Entry Fees", "Applicable park or reserve fees unless explicitly included.", "ticket"),
            exc("Night Walk", "Night-walk permits and specialist arrangements are excluded unless selected.", "moon"),
            exc("Meals & Drinks", "Food and drinks unless explicitly included.", "utensils"),
        ],
        highlights=[
            highlight("Indri Country", "Search for Madagascar's iconic indri in its rainforest habitat.", "paw-print", "Wildlife"),
            highlight("Endemic Biodiversity", "Discover a forest ecosystem known for exceptionally high levels of endemic species.", "leaf", "Nature"),
            highlight("Forest Birding", "Look and listen for Madagascar's distinctive forest birdlife.", "bird", "Birding"),
            highlight("Conservation-Minded Viewing", "Observe wildlife without feeding, touching or pursuing animals.", "shield", "Conservation"),
        ],
        addons=[addon("Guided Night Walk", "Add a specialist nocturnal wildlife outing.", "A night walk can be requested where permitted and subject to local guide, park and weather conditions.", 65, "Per Person")],
        packing_rows=[
            packing("Closed Hiking Shoes", "Wear sturdy shoes suitable for wet and uneven forest trails.", "Footwear", "shoe", True, True),
            packing("Insect Repellent", "Useful in rainforest conditions.", "Health", "bug"),
            packing("Rain Jacket", "Rain can occur even when the day begins dry.", "Clothing", "cloud-rain"),
            packing("Binoculars", "Useful for distant birds and canopy wildlife.", "Equipment", "binoculars"),
        ],
        safety_rows=[
            safety("Stay With the Guide", "Remain on the approved trail and follow the guide's positioning instructions.", "Forest Safety", "route"),
            safety("Do Not Touch Wildlife", "Never feed, touch, chase or call animals closer for photographs.", "Wildlife", "paw-print"),
            safety("Wet Trail Conditions", "Roots, mud and slippery ground are common after rain.", "Terrain", "alert-triangle"),
        ],
        requirements=[
            requirement("Moderate Walking Ability", "Guests should be comfortable walking on uneven rainforest trails.", "Mobility", True, "footprints"),
            requirement("Wildlife Etiquette", "Guests must follow local wildlife and park rules.", "Conservation", True, "shield"),
        ],
        faqs=[
            faq("Will we definitely see indri?", "No. Indri are wild and sightings depend on movement, weather, forest conditions and the route available that day.", "Wildlife", True),
            faq("Can children join?", "Yes, older children who can manage forest walking and follow wildlife rules can participate.", "Family"),
            faq("Is a night walk included?", "Not in the standard experience. It can be added where local regulations and permits allow.", "Activity"),
            faq("What should we wear?", "Closed walking shoes, light layers, rain protection and insect repellent are recommended.", "Packing"),
        ],
        wildlife_rows=[],
        display_order=7,
    ),

    experience(
        code="EA-MDG-002",
        slug="avenue-of-baobabs-sunset-menabe",
        title="Avenue of the Baobabs — Sunset & Menabe Landscapes",
        destination_id=34,
        category_id=CATEGORY_CULTURE,
        short_description="A cinematic Menabe experience centred on Madagascar's iconic baobab landscape, rural communities and sunset photography.",
        description="Travel through the Menabe landscape to experience Madagascar's famous Avenue of the Baobabs at the most atmospheric time of day. The experience combines landscape interpretation, photography and respectful observation of the surrounding rural environment. Seasonal road conditions and local access can affect timing, so the final route is confirmed before departure.",
        duration="Half Day",
        meeting_point="Confirmed Morondava-area accommodation or agreed meeting point.",
        location="Avenue of the Baobabs, Menabe, Madagascar",
        price_from=135,
        minimum_people=1, maximum_people=8, minimum_age=6, difficulty="Easy",
        meta_title="Avenue of the Baobabs Sunset Experience | The Uncharted Route",
        meta_description="Experience Madagascar's iconic Avenue of the Baobabs at sunset with guided landscape interpretation and photography.",
        conservation_story_id=None,
        tags=[TAG_NATURE, TAG_PHOTOGRAPHY, TAG_CULTURE, TAG_PRIVATE, TAG_HISTORICAL],
        moments=[MOMENT_VIEWPOINT, MOMENT_LANDSCAPES, MOMENT_EXTRAORDINARY, MOMENT_PRIVATE_SUNSET],
        pricing_rows=pricing((215, 295, 445), (175, 245, 365), (145, 205, 305), "Indicative TUR selling price per person in USD. Local guide, road conditions, vehicle and any conservation/site charges are confirmed before booking.", "USD"),
        itinerary_rows=[
            itinerary("Morondava Departure", "Afternoon", "Leave the confirmed accommodation and travel toward the baobab landscape with a local guide."),
            itinerary("Rural Landscape & Baobab Interpretation", "Late Afternoon", "Explore the surrounding landscape and learn about baobabs, local livelihoods and the changing ecology of the Menabe region."),
            itinerary("Avenue of the Baobabs", "Sunset", "Position for the classic baobab avenue views, allowing time for photography and quiet observation."),
            itinerary("Return to Morondava", "After Sunset", "Return by the confirmed vehicle route after the light fades, subject to road and local conditions."),
        ],
        inclusions=[
            inc("Private Route Coordination", "TUR coordination of the confirmed Morondava and baobab route.", "route"),
            inc("Local Guide", "Local interpretation of the baobab landscape and surrounding communities.", "user"),
            inc("Private Vehicle Arrangement", "Confirmed vehicle transport for the agreed route.", "car"),
            inc("Sunset Photography Time", "Dedicated time for landscape photography and viewing.", "camera"),
        ],
        exclusions=[
            exc("Specialist Photography Guide", "A professional photography guide is excluded unless selected.", "camera"),
            exc("Meals & Drinks", "Food and drinks unless explicitly included.", "utensils"),
            exc("Road-Related Extensions", "Additional costs caused by unexpected road delays or route changes are excluded unless agreed.", "car"),
        ],
        highlights=[
            highlight("Iconic Baobab Avenue", "Experience one of Madagascar's most recognisable landscapes at golden hour.", "tree", "Landscape"),
            highlight("Menabe Story", "Connect the trees and landscape with the people and rural communities of the region.", "users", "Culture"),
            highlight("Golden-Hour Photography", "Use changing light and silhouettes for memorable landscape images.", "camera", "Photography"),
            highlight("Slow Sunset Moment", "End the day with an unhurried view over an extraordinary natural landscape.", "sun", "Sunset"),
        ],
        addons=[addon("Professional Photography Guide", "Add a photography-focused guide.", "A photography guide can be arranged subject to local availability and advance booking.", 75, "Per Booking")],
        packing_rows=[
            packing("Camera & Spare Battery", "Bring charged batteries and sufficient storage.", "Equipment", "camera"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Light Jacket", "Temperatures can fall after sunset.", "Clothing", "jacket"),
            packing("Closed Shoes", "Wear comfortable shoes for uneven ground.", "Footwear", "shoe"),
        ],
        safety_rows=[
            safety("Stay With the Guide", "Remain with the group around roadside and rural viewing areas.", "General", "shield"),
            safety("Road Awareness", "Road conditions and visibility can change, particularly after sunset.", "Transport", "car"),
            safety("Respect Local Communities", "Ask before photographing people and avoid entering private land without permission.", "Cultural Safety", "users"),
        ],
        requirements=[
            requirement("Sunset Timing", "Guests should be prepared for a later return after sunset.", "Timing", True, "clock"),
            requirement("Photography Respect", "Photography of people and private property requires appropriate permission.", "Culture", True, "camera"),
        ],
        faqs=[
            faq("Is the Avenue of the Baobabs guaranteed to be accessible?", "The attraction is a major visitor site, but road, weather and local operating conditions can affect access and timing.", "Access", True),
            faq("Is this a hiking experience?", "No. It is primarily a scenic vehicle-based experience with short walking and photography stops.", "Activity"),
            faq("Can children join?", "Yes. The experience is suitable for families who can manage the travel timing.", "Family"),
            faq("Can we arrange sunrise instead?", "A sunrise version can be requested where vehicle timing and local access make it practical.", "Customisation"),
        ],
        wildlife_rows=[],
        display_order=8,
    ),

    experience(
        code="EA-MDG-003",
        slug="nosy-be-marine-island-escape",
        title="Nosy Be — Marine Life, Islands & Tropical Escape",
        destination_id=34,
        category_id=CATEGORY_COASTAL,
        short_description="A private Nosy Be marine escape combining island scenery, reef-edge snorkelling, coastal relaxation and responsible marine viewing.",
        description="Explore the tropical waters around Nosy Be through a privately coordinated boat day with an island or reef stop selected for the confirmed conditions. Snorkelling and marine viewing are offered only where weather, sea conditions and operator safety allow. Dolphins, turtles, reef fish and other marine life may be encountered, but no wildlife sighting is guaranteed.",
        duration="Full Day",
        meeting_point="Confirmed Nosy Be hotel or agreed boat departure point.",
        location="Nosy Be, Madagascar",
        price_from=175,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Nosy Be Marine & Island Escape | The Uncharted Route",
        meta_description="Discover Nosy Be by boat with island scenery, responsible marine viewing and optional snorkelling.",
        conservation_story_id=7,
        tags=[TAG_COASTAL, TAG_MARINE, TAG_WATER, TAG_ISLAND, TAG_PHOTOGRAPHY],
        moments=[MOMENT_MARINE, MOMENT_OCEAN_VIEW, MOMENT_EXTRAORDINARY, MOMENT_RELAXATION],
        pricing_rows=pricing((285, 395, 595), (235, 325, 485), (195, 275, 405), "Indicative TUR selling price per person in USD. Boat, marine fees, lunch and any protected-area charges are confirmed in the final quotation.", "USD"),
        itinerary_rows=[
            itinerary("Boat Departure & Safety Briefing", "Morning", "Meet the crew, receive the marine-safety briefing and depart from the confirmed Nosy Be landing point."),
            itinerary("Island / Reef Exploration", "Morning–Midday", "Cruise toward the selected island or reef area, with route decisions guided by sea conditions and local operating knowledge."),
            itinerary("Snorkelling & Marine Viewing", "Midday", "Enjoy a safe water session or surface-level marine viewing where conditions permit, followed by a confirmed lunch arrangement."),
            itinerary("Coastal Cruise & Return", "Afternoon", "Continue the scenic return journey with time for photography and relaxed island viewing."),
        ],
        inclusions=[
            inc("Private Boat Coordination", "TUR coordination of the confirmed boat and route.", "ship"),
            inc("Boat Crew", "Local crew responsible for navigation and safe operation.", "user"),
            inc("Island / Reef Stop", "A selected marine or island stop according to weather and sea conditions.", "island"),
            inc("Marine Viewing", "Time for safe snorkelling or surface-level marine observation where conditions permit.", "waves"),
        ],
        exclusions=[
            exc("Protected Area Fees", "Applicable marine or protected-area charges unless explicitly included.", "ticket"),
            exc("Premium Seafood Lunch", "Premium dining upgrades are excluded unless selected.", "utensils"),
            exc("Private Dive", "Scuba diving and specialist dive arrangements are excluded unless separately booked.", "waves"),
        ],
        highlights=[
            highlight("Nosy Be Island Waters", "Experience Madagascar's tropical northwest from the sea.", "ship", "Marine"),
            highlight("Reef & Marine Life", "Look for reef fish and other marine life while keeping a respectful distance.", "fish", "Wildlife"),
            highlight("Island Escape", "Combine time on or near a selected island with a relaxed coastal rhythm.", "island", "Island"),
            highlight("Ocean Photography", "Use clear water, island horizons and changing light for coastal photography.", "camera", "Photography"),
        ],
        addons=[addon("Private Marine Guide", "Upgrade to specialist marine interpretation.", "A specialist marine guide can be requested subject to availability and route.", 65, "Per Booking")],
        packing_rows=[
            packing("Swimwear", "Bring swimwear for optional water activities.", "Clothing", "waves"),
            packing("Reef-Safe Sun Protection", "Use reef-conscious sunscreen and bring a hat and sunglasses.", "Health", "sun"),
            packing("Dry Bag", "Protect electronics and valuables from spray.", "Equipment", "bag"),
            packing("Light Cover-Up", "Useful for sun protection between water activities.", "Clothing", "shirt"),
        ],
        safety_rows=[
            safety("Boat Safety", "Follow crew instructions and use safety equipment as directed.", "Marine Safety", "life-buoy"),
            safety("Sea Conditions", "Water activities may be shortened, relocated or cancelled when conditions are unsafe.", "Weather", "cloud"),
            safety("Marine Wildlife Distance", "Never chase, touch, feed or corner marine animals.", "Wildlife", "fish"),
        ],
        requirements=[
            requirement("Water Activity Disclosure", "Tell TUR about swimming ability and any health or mobility considerations affecting water activities.", "Health", False, "info"),
            requirement("Marine Safety Compliance", "Guests must follow crew instructions during boat and water activities.", "Safety", True, "life-buoy"),
        ],
        faqs=[
            faq("Will we see dolphins or turtles?", "They may be encountered in Nosy Be waters, but marine wildlife sightings are never guaranteed.", "Wildlife", True),
            faq("Do I have to snorkel?", "No. Guests can remain on the boat or enjoy the island stop without entering the water.", "Activity"),
            faq("Can children join?", "Yes, older children who can follow boat and water-safety instructions can participate.", "Family"),
            faq("Can the boat route change?", "Yes. Wind, swell, visibility and local safety decisions can change the selected island or reef stop.", "Weather"),
        ],
        wildlife_rows=[],
        display_order=9,
    ),
]

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
    # Inactive destinations are intentionally allowed.
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
    db.session.add_all([model(experience_id=experience_id, **record) for record in records])


def validate_reusable_cms(data):
    require_active(ExperienceCategory, data["category_id"], "Experience category")
    require_destination(data["destination_id"])
    require_active(CancellationPolicy, data["cancellation_policy_id"], "Cancellation policy")
    require_active(Accessibility, data["accessibility_profile_id"], "Accessibility profile")

    if data.get("conservation_story_id"):
        require_active(ConservationStory, data["conservation_story_id"], "Conservation story")

    for tag_id in data["tags"]:
        require_active(ExperienceTag, tag_id, "Experience tag")
    for moment_id in data["moments"]:
        require_active(SignatureMoment, moment_id, "Signature moment")
    for row in data.get("wildlife", []):
        require_active(WildlifeSpecies, row["species_id"], "Wildlife species")


def validate_duplicate_experience(data):
    existing = Experience.query.filter(
        or_(Experience.experience_code == data["code"], Experience.slug == data["slug"])
    ).first()
    if existing:
        raise RuntimeError(
            "An experience already uses this code or slug. "
            f"Existing ID: {existing.id}; Code: {existing.experience_code}; "
            f"Slug: {existing.slug}. No changes have been made."
        )


def populate(apply_changes=False):
    app = create_app()

    with app.app_context():
        try:
            validate_unique_batch()

            print("\n" + "=" * 110)
            print("THE UNCHARTED ROUTE — BATCH 3: KENYAN LAKES, RIFT & HIGHLANDS")
            print("=" * 110)
            print(f"Experiences in batch: {len(EXPERIENCES)}")
            print("Mode:", "APPLY" if apply_changes else "DRY RUN")
            print("=" * 110)

            for data in EXPERIENCES:
                validate_reusable_cms(data)
                validate_duplicate_experience(data)

            print("\nReusable CMS records validated.")
            print("Duplicate protection validated.")

            created = []

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

                experience.tags.extend([db.session.get(ExperienceTag, tag_id) for tag_id in data["tags"]])
                experience.signature_moments.extend([db.session.get(SignatureMoment, moment_id) for moment_id in data["moments"]])

                add_children(ExperienceItinerary, experience.id, [
                    {**record, "display_order": index}
                    for index, record in enumerate(data["itinerary"], 1)
                ])
                add_children(ExperienceInclusion, experience.id, ordered(data["inclusions"]))
                add_children(ExperienceExclusion, experience.id, ordered(data["exclusions"]))
                add_children(ExperienceHighlight, experience.id, ordered(data["highlights"]))
                add_children(ExperiencePricing, experience.id, [
                    {**record, "display_order": index, "active": True}
                    for index, record in enumerate(data["pricing"], 1)
                ])
                add_children(ExperienceAddon, experience.id, ordered(data["addons"]))
                add_children(ExperiencePackingItem, experience.id, ordered(data["packing"]))
                add_children(ExperienceSafetyRule, experience.id, ordered(data["safety"]))
                add_children(ExperienceRequirement, experience.id, ordered(data["requirements"]))
                add_children(ExperienceFAQ, experience.id, ordered(data["faqs"]))
                add_children(ExperienceWildlife, experience.id, ordered(data.get("wildlife", [])))

                created.append(experience)
                destination = db.session.get(Destination, experience.destination_id)

                print(f"\n[{batch_index:02d}/{len(EXPERIENCES)}] {experience.experience_code} — {experience.title}")
                print(f"    Destination ID: {experience.destination_id} | Destination active: {destination.active}")
                print(f"    Itinerary: {len(data['itinerary'])} | Inclusions: {len(data['inclusions'])} | Exclusions: {len(data['exclusions'])} | Highlights: {len(data['highlights'])}")
                print(f"    Pricing: {len(data['pricing'])} | Add-ons: {len(data['addons'])} | Packing: {len(data['packing'])} | Safety: {len(data['safety'])}")
                print(f"    Requirements: {len(data['requirements'])} | FAQs: {len(data['faqs'])} | Tags: {len(data['tags'])} | Signature moments: {len(data['moments'])} | Wildlife: {len(data.get('wildlife', []))}")

            print("\n" + "=" * 110)
            print("BATCH VERIFICATION")
            print("=" * 110)

            for experience in created:
                data = next(x for x in EXPERIENCES if x["code"] == experience.experience_code)
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
                    "wildlife": experience.wildlife.count(),
                    "tags": experience.tags.count(),
                    "signature_moments": experience.signature_moments.count(),
                    "media": experience.media.count(),
                    "schedules": experience.schedules.count(),
                    "bookings": experience.bookings.count(),
                }
                expected = {
                    "pricing": 9,
                    "itinerary": len(data["itinerary"]),
                    "inclusions": len(data["inclusions"]),
                    "exclusions": len(data["exclusions"]),
                    "highlights": len(data["highlights"]),
                    "addons": len(data["addons"]),
                    "packing": len(data["packing"]),
                    "safety": len(data["safety"]),
                    "requirements": len(data["requirements"]),
                    "faqs": len(data["faqs"]),
                    "wildlife": len(data.get("wildlife", [])),
                    "tags": len(data["tags"]),
                    "signature_moments": len(data["moments"]),
                    "media": 0,
                    "schedules": 0,
                    "bookings": 0,
                }
                for key, expected_value in expected.items():
                    actual = checks[key]
                    if actual != expected_value:
                        raise RuntimeError(f"Verification failed for {experience.experience_code}: {key} expected {expected_value}, got {actual}.")

                print(f"VERIFIED {experience.experience_code} | all content counts correct | wildlife={checks['wildlife']} media=0 schedules=0 bookings=0")

            print("\nAll batch records passed verification.")

            if apply_changes:
                db.session.commit()
                print("\n" + "=" * 110)
                print("BATCH 3 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(f"Created {len(created)} complete East African Islands experiences.")
                print("Inactive destinations Lake Nakuru, Kisumu and Kericho remain inactive.")
            else:
                db.session.rollback()
                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)
                print(f"Validated {len(created)} complete experience records.")
                print("No database changes were committed.")
                print("Run with --apply only after reviewing the dry-run output.")

        except Exception:
            db.session.rollback()
            print("\n" + "=" * 110)
            print("BATCH 3 FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Commit the population to the database.")
    args = parser.parse_args()
    populate(apply_changes=args.apply)