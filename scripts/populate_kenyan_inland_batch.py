"""
===============================================================================
THE UNCHARTED ROUTE
BATCH 2 — KENYAN LAKES, RIFT & HIGHLANDS EXPERIENCE POPULATION
===============================================================================

Destinations:
    Lake Nakuru National Park ID 12 — currently INACTIVE; remains inactive
    Elementaita                 ID 36 — ACTIVE
    Kisumu                      ID 20 — currently INACTIVE; remains inactive
    Kericho                     ID 22 — currently INACTIVE; remains inactive

This batch creates complete, sellable Experience records with reusable CMS
associations and all approved child content.

IMPORTANT:
    - Existing experiences are NEVER modified.
    - Existing CMS records are NEVER duplicated.
    - No media associations are created.
    - No schedules are created.
    - No bookings are created.
    - Inactive destinations remain inactive.
    - Experiences are created active so they are ready when their destination
      is activated later.
    - DEFAULT: dry run.
    - APPLY: python scripts/populate_kenyan_inland_batch.py --apply

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


def pricing(one, two_three, four_plus, notes):
    return [
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Explorer", "price": one[0], "currency": "KES", "notes": notes},
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Signature", "price": one[1], "currency": "KES", "notes": notes},
        {"minimum_people": 1, "maximum_people": 1, "experience_level": "Luxury", "price": one[2], "currency": "KES", "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Explorer", "price": two_three[0], "currency": "KES", "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Signature", "price": two_three[1], "currency": "KES", "notes": notes},
        {"minimum_people": 2, "maximum_people": 3, "experience_level": "Luxury", "price": two_three[2], "currency": "KES", "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Explorer", "price": four_plus[0], "currency": "KES", "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Signature", "price": four_plus[1], "currency": "KES", "notes": notes},
        {"minimum_people": 4, "maximum_people": None, "experience_level": "Luxury", "price": four_plus[2], "currency": "KES", "notes": notes},
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
    # LAKE NAKURU — INACTIVE DESTINATION
    # -------------------------------------------------------------------------
    experience(
        code="RIF-NAK-001",
        slug="lake-nakuru-rhino-wildlife-safari",
        title="Lake Nakuru Rhino & Wildlife Safari",
        destination_id=12,
        category_id=CATEGORY_SAFARI,
        short_description="A private wildlife day in Lake Nakuru National Park focused on rhino country, scenic landscapes and varied wildlife viewing.",
        description="Explore Lake Nakuru National Park on a privately coordinated game-drive experience through a landscape of lake, grassland, acacia woodland and rocky viewpoints. The park is a major rhino sanctuary and supports diverse wildlife and birdlife. Sightings are always subject to natural conditions, animal movement, weather and park access rules.",
        duration="Full Day",
        meeting_point="Agreed pickup point in Nakuru or confirmed accommodation; Nairobi pickup can be arranged as a separate transport option.",
        location="Lake Nakuru National Park, Nakuru County, Kenya",
        price_from=12500,
        minimum_people=1, maximum_people=6, minimum_age=6, difficulty="Easy",
        meta_title="Lake Nakuru Rhino & Wildlife Safari | The Uncharted Route",
        meta_description="Explore Lake Nakuru National Park with a private wildlife safari focused on rhinos, wildlife and scenic Rift Valley landscapes.",
        conservation_story_id=CONSERVATION_RHINO,
        tags=[TAG_WILDLIFE, TAG_CONSERVATION, TAG_PHOTOGRAPHY, TAG_BIG_FIVE, TAG_NATURE],
        moments=[MOMENT_SUNRISE, MOMENT_WILDLIFE, MOMENT_WILDLIFE_HABITAT, MOMENT_LANDSCAPES],
        pricing_rows=pricing((19500, 27500, 42500), (15500, 22500, 34500), (12500, 18500, 28500), "Indicative TUR selling price per person. Current KWS park fees, vehicle arrangements and any seasonal supplier charges must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Pickup & Park Entry", "Early Morning", "Collect guests from the confirmed pickup point, brief the group and enter Lake Nakuru National Park through the agreed gate."),
            itinerary("Morning Wildlife Drive", "Morning", "Explore the park's open habitats and lake-edge areas with time for wildlife observation and photography. Rhino and other wildlife sightings are possible but never guaranteed."),
            itinerary("Scenic Picnic / Lunch Stop", "Midday", "Pause at an approved picnic or lodge setting for lunch and a chance to appreciate the Rift Valley landscape."),
            itinerary("Afternoon Game Drive & Return", "Afternoon", "Continue wildlife viewing before exiting the park and returning guests to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the confirmed itinerary, pickup and park visit.", "route"),
            inc("Private Safari Vehicle", "Private vehicle arrangement for the confirmed wildlife drive, subject to supplier confirmation.", "car"),
            inc("Experienced Driver-Guide", "A driver-guide to coordinate the route and interpret the wildlife landscape.", "user"),
            inc("Wildlife Viewing", "Guided wildlife observation within the permitted park routes.", "binoculars"),
        ],
        exclusions=[
            exc("Park Entry Fees", "KWS park entry and applicable conservation charges unless explicitly included in the confirmed quotation.", "ticket"),
            exc("Meals & Drinks", "Lunch, snacks and drinks unless specifically included in the selected package.", "utensils"),
            exc("Personal Expenses", "Gratuities, purchases and other personal expenses.", "wallet"),
        ],
        highlights=[
            highlight("Rhino Country", "Explore one of Kenya's important rhino conservation landscapes and look for black and white rhinos.", "shield", "Conservation"),
            highlight("Diverse Wildlife", "The park supports a varied wildlife community beyond its famous rhino populations.", "paw-print", "Wildlife"),
            highlight("Lake & Rift Valley Scenery", "Enjoy changing views across the lake, escarpments, woodland and open habitats.", "mountain", "Scenic"),
            highlight("Photography Opportunities", "Use changing morning and afternoon light for wildlife and landscape photography.", "camera", "Photography"),
        ],
        addons=[addon("Premium Picnic Lunch", "Upgrade to a pre-arranged picnic lunch.", "A premium picnic lunch can be arranged subject to location, supplier and park rules.", 4500, "Per Person")],
        packing_rows=[
            packing("Binoculars", "Useful for distant wildlife and bird observation.", "Equipment", "binoculars"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Warm Layer", "Early mornings can be cool in the Rift Valley.", "Clothing", "jacket"),
            packing("Camera", "Bring a camera with enough battery and storage for the day.", "Equipment", "camera"),
            packing("Drinking Water", "Carry adequate drinking water unless your confirmed package states otherwise.", "General", "bottle-water"),
        ],
        safety_rows=[
            safety("Remain With the Vehicle", "Stay inside the safari vehicle except at designated safe areas and when instructed by the guide.", "Wildlife", "shield"),
            safety("Respect Wildlife Distance", "Never approach, feed, call or attempt to touch wild animals.", "Wildlife", "paw-print"),
            safety("Follow Park Rules", "Observe KWS speed limits, route restrictions, entry times and all park instructions.", "Park Safety", "clipboard-check"),
            safety("Weather & Road Conditions", "Routes may change when rain, poor visibility or road conditions affect safe access.", "Weather", "cloud"),
        ],
        requirements=[
            requirement("Confirmed Pickup", "Provide the accommodation or pickup location before the experience date.", "Booking", True, "map-pin"),
            requirement("Park Fee Confirmation", "Final park entry and related charges must be confirmed before booking is considered fully priced.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("Are rhinos guaranteed?", "No. Rhinos are wild animals and sightings depend on their movement, weather, vegetation and other natural conditions.", "Wildlife", True),
            faq("Is this suitable for families?", "Yes, provided children can comfortably manage the early start and full-day vehicle-based itinerary.", "Family"),
            faq("Can we start from Nairobi?", "A Nairobi pickup and return can be arranged as an expanded transport option; the final price depends on the vehicle and timing required.", "Transport"),
            faq("Are park fees included?", "Only when the confirmed quotation explicitly states that the applicable KWS fees are included.", "Fees"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_BLACK_RHINO, "Occasional", "All Year", "Morning", "A major conservation focus of Lake Nakuru; sightings remain subject to natural conditions.", "Use a long lens and maintain the guide's required viewing distance."),
            wildlife(WILDLIFE_WHITE_RHINO, "Common", "All Year", "Morning", "White rhinos are among the park's important large mammal encounters.", "Photograph from the vehicle without crowding animals."),
            wildlife(WILDLIFE_BUFFALO, "Common", "All Year", "Morning", "Buffalo occur across suitable grassland and woodland habitats.", "Watch herd behaviour and keep a safe distance."),
            wildlife(WILDLIFE_ZEBRA, "Common", "All Year", "Morning", "Plains zebra may be encountered in open habitats.", "Morning light can be particularly useful for landscape-and-wildlife frames."),
        ],
        display_order=1,
    ),

    experience(
        code="RIF-NAK-002",
        slug="lake-nakuru-birding-wildlife-discovery",
        title="Lake Nakuru Birding & Wildlife Discovery",
        destination_id=12,
        category_id=CATEGORY_SAFARI,
        short_description="A birding-focused Lake Nakuru experience combining lake views, wetland habitats and wider wildlife observation.",
        description="Discover Lake Nakuru through a slower-paced wildlife and birding experience. The park is renowned for exceptional bird diversity, while its lake, woodland, grassland and escarpment habitats support many other species. Bird numbers and species vary with water conditions, season and natural movement, so no particular sighting is guaranteed.",
        duration="Full Day",
        meeting_point="Confirmed accommodation or agreed pickup point in Nakuru.",
        location="Lake Nakuru National Park, Nakuru County, Kenya",
        price_from=11000,
        minimum_people=1, maximum_people=6, minimum_age=6, difficulty="Easy",
        meta_title="Lake Nakuru Birding & Wildlife Discovery | The Uncharted Route",
        meta_description="Explore Lake Nakuru's birdlife, lake habitats and wildlife with a guided nature-focused experience.",
        conservation_story_id=CONSERVATION_RHINO,
        tags=[TAG_WILDLIFE, TAG_BIRD, TAG_PHOTOGRAPHY, TAG_NATURE, TAG_CONSERVATION],
        moments=[MOMENT_BIRDS, MOMENT_WILDLIFE_HABITAT, MOMENT_SUNRISE],
        pricing_rows=pricing((17500, 24500, 37500), (14000, 20500, 31500), (11000, 16500, 25500), "Indicative TUR selling price per person. Park entry, specialist guiding and any supplier charges must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Early Pickup & Birding Brief", "Early Morning", "Meet the guide, review the day's target habitats and enter the park during the early wildlife-viewing period."),
            itinerary("Lake & Wetland Birding", "Morning", "Explore lake-edge and wetland habitats while observing waterbirds and other species. Exact sightings depend on current conditions."),
            itinerary("Woodland & Grassland Wildlife", "Midday", "Move through different habitats to broaden the day's bird and wildlife list while allowing time for photography."),
            itinerary("Final Birding Stop & Return", "Afternoon", "Finish with a final observation stop before exiting the park and returning to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Birding Experience Coordination", "TUR coordination of the agreed route, guide and pickup.", "route"),
            inc("Driver-Guide", "A guide/driver familiar with the park's wildlife-viewing routes.", "user"),
            inc("Wildlife & Birding Route", "Guided exploration of suitable lake, woodland and grassland habitats.", "bird"),
            inc("Basic Birding Support", "Time for observation, identification and photography during the route.", "binoculars"),
        ],
        exclusions=[
            exc("Park Entry Fees", "Applicable KWS fees unless explicitly included in the confirmed quotation.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Specialist Optics", "High-end spotting scopes or specialist optics are excluded unless separately arranged.", "binoculars"),
        ],
        highlights=[
            highlight("Lake Nakuru Birdlife", "Explore one of Kenya's recognised birding landscapes and observe changing waterbird activity.", "bird", "Birding"),
            highlight("Habitat Diversity", "Move between lake-edge, grassland and woodland habitats during the same experience.", "leaf", "Nature"),
            highlight("Wildlife Beyond Birds", "Large mammals may also be encountered during the wider park route.", "paw-print", "Wildlife"),
            highlight("Photography Time", "Build in deliberate stops for bird and landscape photography.", "camera", "Photography"),
        ],
        addons=[addon("Specialist Birding Guide", "Add a specialist birding guide where available.", "A specialist guide can be requested in advance, subject to availability and final quotation.", 6500, "Per Booking")],
        packing_rows=[
            packing("Binoculars", "Bring binoculars for distant birds and wildlife.", "Equipment", "binoculars"),
            packing("Field Notebook", "Useful for recording species and observations.", "Equipment", "book-open"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Warm Layer", "Early mornings may be cool.", "Clothing", "jacket"),
        ],
        safety_rows=[
            safety("Stay in Designated Areas", "Remain inside the vehicle except where the guide identifies a permitted area for stopping or walking.", "Park Safety", "shield"),
            safety("Do Not Disturb Birds", "Avoid loud calls, sudden movements and actions that disturb nesting or feeding birds.", "Birding", "bird"),
            safety("Respect Wildlife", "Do not approach, feed or attempt to touch wildlife.", "Wildlife", "paw-print"),
        ],
        requirements=[
            requirement("Early Start", "Guests should be ready at the confirmed pickup time to take advantage of the best early viewing period.", "General", True, "clock"),
            requirement("Park Fee Confirmation", "Confirm applicable park charges before final booking.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("Is this only for expert birders?", "No. The experience can be enjoyed by beginners as well as experienced birders; the guide adjusts the interpretation to the group.", "Activity", True),
            faq("Will we see flamingos?", "Flamingo presence varies with lake conditions and season, so sightings are possible but not guaranteed.", "Wildlife"),
            faq("Can children join?", "Yes, provided they can manage the early start and follow wildlife-viewing instructions.", "Family"),
            faq("Can we use a private vehicle?", "Yes. The experience is designed around a privately coordinated vehicle arrangement unless another setup is agreed.", "Transport"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_BLACK_RHINO, "Occasional", "All Year", "Morning", "Rhino sightings are possible during wider wildlife routes but are never guaranteed.", "Use long lenses and avoid disturbing animals."),
            wildlife(WILDLIFE_WHITE_RHINO, "Common", "All Year", "Morning", "White rhinos may be encountered in suitable habitats.", "Photograph from a safe vehicle position."),
            wildlife(WILDLIFE_ZEBRA, "Common", "All Year", "Morning", "Zebra may be seen across open habitats.", "Look for opportunities involving habitat and herd behaviour."),
        ],
        display_order=2,
    ),

    experience(
        code="RIF-NAK-003",
        slug="lake-nakuru-makalia-falls-scenic-escape",
        title="Lake Nakuru Scenic Escape — Viewpoints & Makalia Falls",
        destination_id=12,
        category_id=CATEGORY_SAFARI,
        short_description="A scenic Lake Nakuru day combining wildlife-country viewpoints, Makalia Falls and relaxed landscape exploration.",
        description="Experience the landscape of Lake Nakuru National Park beyond the classic game-drive rhythm. The route combines scenic viewpoints, selected picnic areas and Makalia Falls when accessible, with opportunities for short walks only where park rules and current conditions permit. Wildlife may be encountered along the way but is not the sole focus and sightings are never guaranteed.",
        duration="Full Day",
        meeting_point="Confirmed accommodation or agreed pickup point in Nakuru.",
        location="Lake Nakuru National Park, Nakuru County, Kenya",
        price_from=10500,
        minimum_people=1, maximum_people=6, minimum_age=8, difficulty="Easy",
        meta_title="Lake Nakuru Scenic Escape | The Uncharted Route",
        meta_description="Discover Lake Nakuru's viewpoints, landscapes and Makalia Falls through a relaxed private nature experience.",
        conservation_story_id=None,
        tags=[TAG_NATURE, TAG_PHOTOGRAPHY, TAG_WILDLIFE, TAG_HIKING],
        moments=[MOMENT_VIEWPOINT, MOMENT_TRAIL, MOMENT_LANDSCAPES],
        pricing_rows=pricing((16500, 23500, 35500), (13500, 19500, 29500), (10500, 15500, 23500), "Indicative TUR selling price per person. Park fees, vehicle arrangements and current access conditions must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Pickup & Park Entry", "Morning", "Meet the guide, review the route and enter the park through the agreed gate."),
            itinerary("Scenic Viewpoints & Wildlife Country", "Morning", "Travel through scenic sections of the park with time for photography and relaxed interpretation of the landscape."),
            itinerary("Makalia Falls / Picnic Area", "Midday–Afternoon", "Visit Makalia Falls when accessible and conditions permit, or use an approved scenic stop as the alternative."),
            itinerary("Final Scenic Drive & Return", "Afternoon", "Continue through suitable routes before exiting the park and returning guests to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Private Route Coordination", "TUR coordination of the confirmed scenic itinerary and transport arrangement.", "route"),
            inc("Driver-Guide", "Driver-guide support throughout the experience.", "user"),
            inc("Scenic Exploration", "Guided access to permitted viewpoints and scenic areas.", "mountain"),
            inc("Makalia Falls Visit", "Visit to Makalia Falls when accessible and included in the final route.", "droplets"),
        ],
        exclusions=[
            exc("Park Entry Fees", "Applicable KWS fees unless explicitly included in the quotation.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Restricted-Area Access", "Any area closed by park management or made inaccessible by weather is excluded.", "lock"),
        ],
        highlights=[
            highlight("Rift Valley Landscapes", "Take time to appreciate the changing lake, escarpment and woodland scenery.", "mountain", "Scenic"),
            highlight("Makalia Falls", "Visit the park's waterfall when current access and conditions allow.", "droplets", "Nature"),
            highlight("Photography Stops", "Build in time for deliberate landscape and nature photography.", "camera", "Photography"),
            highlight("Gentler Safari Rhythm", "Enjoy a less rushed itinerary with scenery and interpretation sharing the focus with wildlife.", "clock", "Slow Travel"),
        ],
        addons=[addon("Private Picnic Setup", "Add a pre-arranged scenic picnic setup.", "A picnic can be arranged at an approved location subject to park rules, weather and supplier availability.", 5000, "Per Booking")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable closed shoes for short permitted walks.", "Footwear", "shoe"),
            packing("Rain Layer", "Weather can change quickly; carry a light waterproof layer.", "Clothing", "cloud-rain"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water Bottle", "Carry drinking water for the day.", "General", "bottle-water"),
        ],
        safety_rows=[
            safety("Use Only Approved Trails", "Do not walk beyond designated or guide-approved areas.", "Trail Safety", "route"),
            safety("Waterfall Edge Awareness", "Keep away from slippery edges, steep drops and unstable ground near the falls.", "Terrain", "alert-triangle"),
            safety("Weather Changes", "The waterfall route may be changed or omitted when rain or conditions make it unsafe.", "Weather", "cloud"),
        ],
        requirements=[
            requirement("Suitable Footwear", "Wear shoes suitable for uneven or potentially damp ground.", "Equipment", True, "shoe"),
            requirement("Park Fee Confirmation", "Confirm applicable KWS charges before final booking.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("Will we definitely visit Makalia Falls?", "Not always. Access depends on park conditions, weather, route availability and safety considerations.", "Activity", True),
            faq("Is this a hiking experience?", "It includes short walks where permitted, but it is primarily a scenic vehicle-based experience rather than a strenuous hike.", "Activity"),
            faq("Can we see wildlife?", "Yes, wildlife may be encountered because the route remains within a wildlife landscape, but sightings are not guaranteed.", "Wildlife"),
            faq("Is lunch included?", "Only when explicitly included in the confirmed package; a picnic add-on can be requested.", "Dining"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_ZEBRA, "Occasional", "All Year", "Morning", "Zebra may appear along open scenic routes.", "Landscape framing can work well with herds at a distance."),
            wildlife(WILDLIFE_BUFFALO, "Occasional", "All Year", "Morning", "Buffalo may be encountered in suitable habitats.", "Keep a safe distance and remain with the vehicle."),
        ],
        display_order=3,
    ),

    # -------------------------------------------------------------------------
    # ELEMENTAITA — ACTIVE DESTINATION
    # -------------------------------------------------------------------------
    experience(
        code="RIF-ELM-001",
        slug="lake-elementaita-birding-wildlife-discovery",
        title="Lake Elementaita — Flamingo, Birding & Wildlife Discovery",
        destination_id=36,
        category_id=CATEGORY_SAFARI,
        short_description="A nature-focused Lake Elementaita experience exploring the lake, birdlife and surrounding wildlife habitats.",
        description="Explore Lake Elementaita's wetland landscape, a globally important birding area and part of the Kenya Lakes System. The experience combines lake-edge observation with wider wildlife and landscape viewing. Flamingos, pelicans, spoonbills and other waterbirds may be encountered, while sightings vary with water conditions, season and natural movement.",
        duration="Full Day",
        meeting_point="Confirmed accommodation or agreed meeting point around Lake Elementaita.",
        location="Lake Elementaita, Nakuru County, Kenya",
        price_from=9500,
        minimum_people=1, maximum_people=6, minimum_age=6, difficulty="Easy",
        meta_title="Lake Elementaita Birding & Wildlife Discovery | The Uncharted Route",
        meta_description="Discover Lake Elementaita's birdlife, wetland landscapes and surrounding wildlife on a private nature experience.",
        conservation_story_id=CONSERVATION_GREVEYS,
        tags=[TAG_BIRD, TAG_WILDLIFE, TAG_NATURE, TAG_PHOTOGRAPHY, TAG_CONSERVATION],
        moments=[MOMENT_BIRDS, MOMENT_WILDLIFE_HABITAT, MOMENT_LANDSCAPES],
        pricing_rows=pricing((15500, 21500, 32500), (12500, 18000, 27500), (9500, 14500, 22000), "Indicative TUR selling price per person. Sanctuary fees, specialist guiding and transport charges must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Pickup & Lake Introduction", "Morning", "Meet the guide and begin with an overview of the lake's wetland, wildlife and conservation significance."),
            itinerary("Lake-Edge Birding", "Morning", "Explore suitable lake-edge viewpoints and observe waterbirds and other species. Exact sightings are never guaranteed."),
            itinerary("Wildlife & Landscape Circuit", "Afternoon", "Continue through surrounding habitats with time for wildlife observation, photography and scenic stops."),
            itinerary("Final View & Return", "Late Afternoon", "Finish with a final lakeside observation stop before returning guests to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the confirmed route, pickup and guiding arrangement.", "route"),
            inc("Local Guide / Driver-Guide", "Guided interpretation of the lake and surrounding habitats.", "user"),
            inc("Birding & Wildlife Route", "Guided exploration of suitable viewing locations.", "bird"),
            inc("Photography Stops", "Time for bird and landscape photography at appropriate stops.", "camera"),
        ],
        exclusions=[
            exc("Sanctuary / Site Fees", "Applicable conservation or site charges unless explicitly included.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Specialist Optics", "Spotting scopes and specialist optics unless separately arranged.", "binoculars"),
        ],
        highlights=[
            highlight("Waterbird Habitat", "Explore a wetland landscape supporting important bird populations.", "bird", "Birding"),
            highlight("Flamingo Possibilities", "Flamingos may be present depending on current lake conditions and natural movement.", "feather", "Wildlife"),
            highlight("Rift Valley Scenery", "Enjoy open views across the lake basin and surrounding highlands.", "mountain", "Scenic"),
            highlight("Slow Nature Observation", "A relaxed pace allows more time to notice bird behaviour and landscape detail.", "leaf", "Nature"),
        ],
        addons=[addon("Specialist Birding Guide", "Request a specialist birding guide.", "A specialist birding guide may be arranged in advance subject to availability.", 6000, "Per Booking")],
        packing_rows=[
            packing("Binoculars", "Bring binoculars for distant birds.", "Equipment", "binoculars"),
            packing("Warm Layer", "Lake-country mornings can be cool.", "Clothing", "jacket"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Field Notebook", "Useful for recording bird observations.", "Equipment", "book-open"),
        ],
        safety_rows=[
            safety("Keep to Approved Viewing Areas", "Use established paths and guide-approved viewing points.", "Environment", "route"),
            safety("Do Not Disturb Birds", "Avoid approaching nests, roosts or feeding birds and keep noise low.", "Birding", "bird"),
            safety("Water Safety", "Stay away from unstable lake edges and follow the guide's instructions near water.", "Water", "droplets"),
        ],
        requirements=[
            requirement("Early Start", "An early start is recommended for the strongest birding conditions.", "General", False, "clock"),
            requirement("Confirm Site Fees", "Any applicable site or conservation fees must be confirmed before final booking.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("Are flamingos guaranteed?", "No. Their presence changes with lake conditions, food availability, water levels and seasonal movement.", "Wildlife", True),
            faq("Can beginners join?", "Yes. The experience is suitable for general nature lovers as well as birding enthusiasts.", "Activity"),
            faq("Can children join?", "Yes, provided they can follow the guide's instructions and manage the outdoor itinerary.", "Family"),
            faq("Is this a walking tour?", "It combines vehicle access with short walks and viewing stops rather than a strenuous hike.", "Activity"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_ZEBRA, "Common", "All Year", "Morning", "Zebra may be seen in surrounding terrestrial habitats.", "Use landscape framing to show the relationship between wildlife and the lake basin."),
            wildlife(WILDLIFE_GIRAFFE, "Occasional", "All Year", "Morning", "Giraffes may occur in suitable surrounding habitats.", "Observe quietly and maintain distance."),
            wildlife(WILDLIFE_BUFFALO, "Occasional", "All Year", "Morning", "Buffalo may be encountered in suitable habitats around the wider area.", "Remain with the guide and keep a safe distance."),
        ],
        display_order=4,
    ),

    experience(
        code="RIF-ELM-002",
        slug="kariandusi-archaeology-lake-elementaita",
        title="Kariandusi & Lake Elementaita — Archaeology, Lake & Living Landscape",
        destination_id=36,
        category_id=CATEGORY_CULTURE,
        short_description="A heritage-led day combining the Kariandusi prehistoric site with Lake Elementaita's archaeological and natural landscape.",
        description="Travel through one of the Great Rift Valley's most compelling combinations of archaeology and landscape. Visit Kariandusi, an early Lower Paleolithic site associated with Acheulian handaxe culture, then continue to Lake Elementaita for a broader understanding of the basin's geological, ecological and human history. The experience is designed for travellers who want context as well as scenery.",
        duration="Full Day",
        meeting_point="Confirmed accommodation or agreed meeting point around Elementaita.",
        location="Kariandusi & Lake Elementaita, Nakuru County, Kenya",
        price_from=9000,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Kariandusi & Lake Elementaita Heritage Experience | The Uncharted Route",
        meta_description="Explore Kariandusi archaeology and Lake Elementaita's remarkable natural and human history on a private heritage experience.",
        conservation_story_id=None,
        tags=[TAG_CULTURE, TAG_HISTORICAL, TAG_NATURE, TAG_PHOTOGRAPHY],
        moments=[MOMENT_HERITAGE, MOMENT_HIDDEN_NATURE, MOMENT_LANDSCAPES],
        pricing_rows=pricing((14500, 20500, 30500), (11500, 17500, 26500), (9000, 13500, 20500), "Indicative TUR selling price per person. National Museums of Kenya entry charges and any specialist guide fees must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Pickup & Rift Valley Introduction", "Morning", "Meet the guide and travel to Kariandusi while introducing the geological and archaeological story of the wider basin."),
            itinerary("Kariandusi Prehistoric Site", "Morning", "Explore the archaeological site, museum interpretation, designated trails and key landscape features with guided context."),
            itinerary("Lake Elementaita Landscape", "Afternoon", "Continue to the lake basin for scenic observation and discussion of its wetland, wildlife and human history."),
            itinerary("Reflection Stop & Return", "Late Afternoon", "Use a final scenic stop for photography and reflection before returning to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the route, timing and site visits.", "route"),
            inc("Heritage Interpretation", "Guided interpretation of Kariandusi and the wider Rift Valley landscape.", "book-open"),
            inc("Site Exploration", "Time to explore designated museum, archaeological and landscape areas.", "landmark"),
            inc("Lake Landscape Stop", "A guided stop around Lake Elementaita for natural and cultural context.", "mountain"),
        ],
        exclusions=[
            exc("Site Entry Fees", "National Museums of Kenya and other applicable entry fees unless explicitly included.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Specialist Archaeology Research Guide", "Specialist academic or research-level guiding is excluded unless separately arranged.", "graduation-cap"),
        ],
        highlights=[
            highlight("Early Human Heritage", "Explore a site associated with some of East Africa's earliest known stone-tool discoveries.", "landmark", "Heritage"),
            highlight("Acheulian Story", "Learn about Kariandusi's connection to Acheulian handaxe culture and prehistoric research.", "hammer", "History"),
            highlight("Lake Basin Landscapes", "Connect archaeological history with the living Rift Valley landscape around Elementaita.", "mountain", "Scenic"),
            highlight("Thoughtful Interpretation", "Go beyond sightseeing with context linking geology, archaeology and ecology.", "book-open", "Learning"),
        ],
        addons=[addon("Private Archaeology Specialist", "Request specialist heritage interpretation.", "A specialist guide can be requested subject to availability and advance confirmation.", 7000, "Per Booking")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes for designated trails and uneven ground.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Water", "Carry drinking water for the day.", "General", "bottle-water"),
            packing("Camera", "Photography is useful for landscapes and site details where permitted.", "Equipment", "camera"),
        ],
        safety_rows=[
            safety("Stay on Designated Trails", "Follow site guidance and do not climb archaeological features or enter restricted areas.", "Heritage", "route"),
            safety("Uneven Ground", "Watch your footing around archaeological trails, rocks and natural features.", "Terrain", "footprints"),
            safety("Respect Heritage", "Do not touch, remove or disturb archaeological materials or site structures.", "Conservation", "shield"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable with short walks over uneven ground.", "Mobility", True, "shoe"),
            requirement("Entry Fee Confirmation", "Confirm current site admission charges before final booking.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("Is Kariandusi suitable for children?", "Yes. The site can be engaging for families, especially when the guide explains the prehistoric story in an accessible way.", "Family", True),
            faq("How old is the site?", "Kariandusi is associated with Lower Paleolithic archaeology dating roughly 700,000 to 1 million years ago.", "Heritage"),
            faq("Is this a strenuous hike?", "No. The experience uses designated trails and short walks rather than a strenuous trek.", "Activity"),
            faq("Can we add a specialist guide?", "Yes, subject to availability and advance confirmation.", "Guiding"),
        ],
        display_order=5,
    ),

    # -------------------------------------------------------------------------
    # KISUMU — INACTIVE DESTINATION
    # -------------------------------------------------------------------------
    experience(
        code="WES-KSM-001",
        slug="kisumu-impala-sanctuary-wildlife-discovery",
        title="Kisumu Impala Sanctuary — Wildlife & Lakeside Nature Discovery",
        destination_id=20,
        category_id=CATEGORY_SAFARI,
        short_description="A relaxed wildlife and nature experience at Kisumu Impala Sanctuary beside Lake Victoria.",
        description="Discover Kisumu Impala Sanctuary through a guided nature experience combining wildlife observation, walking trails and lakeside scenery. The sanctuary supports impalas, sitatunga, giraffes, zebras, buffaloes and other species, while birding and scenic viewing add a slower dimension to the visit. Wildlife encounters are never guaranteed.",
        duration="Half Day",
        meeting_point="Confirmed Kisumu accommodation or agreed meeting point.",
        location="Kisumu Impala Sanctuary, Kisumu County, Kenya",
        price_from=6500,
        minimum_people=1, maximum_people=8, minimum_age=6, difficulty="Easy",
        meta_title="Kisumu Impala Sanctuary Wildlife Experience | The Uncharted Route",
        meta_description="Explore Kisumu Impala Sanctuary with wildlife viewing, nature trails, birding and Lake Victoria scenery.",
        conservation_story_id=CONSERVATION_GIRAFFE,
        tags=[TAG_WILDLIFE, TAG_CONSERVATION, TAG_BIRD, TAG_NATURE, TAG_PHOTOGRAPHY],
        moments=[MOMENT_WILDLIFE, MOMENT_WILDLIFE_HABITAT, MOMENT_VIEWPOINT],
        pricing_rows=pricing((10500, 14500, 22500), (8500, 12000, 18500), (6500, 9500, 14500), "Indicative TUR selling price per person. Sanctuary entry, guiding and transport charges must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Pickup & Sanctuary Introduction", "Morning / Afternoon", "Meet the guide and travel to the sanctuary for an introduction to the lakeside ecosystem."),
            itinerary("Wildlife & Nature Walk", "Main Activity", "Explore permitted trails and viewing areas while looking for impalas, sitatunga, giraffes, zebras and other wildlife."),
            itinerary("Birding & Lakeside Views", "Late Activity", "Pause for birding and scenic observation with views toward the Lake Victoria landscape."),
            itinerary("Return to Kisumu", "Late Afternoon", "Conclude the visit and transfer guests back to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Experience Coordination", "TUR coordination of the sanctuary visit and agreed pickup.", "route"),
            inc("Guided Nature Experience", "Guided interpretation of wildlife, habitat and conservation themes.", "user"),
            inc("Nature Trail Access", "Access to permitted sanctuary trails and viewing areas according to the confirmed package.", "footprints"),
            inc("Lakeside Viewing", "Time for scenic and birding observation around the sanctuary landscape.", "binoculars"),
        ],
        exclusions=[
            exc("Sanctuary Entry", "Applicable entry charges unless explicitly included.", "ticket"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Private Vehicle Upgrade", "Premium vehicle arrangements are excluded unless selected.", "car"),
        ],
        highlights=[
            highlight("Impala & Antelope Country", "Observe impalas and look for other antelope species within the sanctuary.", "paw-print", "Wildlife"),
            highlight("Lakeside Nature", "Combine wildlife viewing with the distinctive setting of Lake Victoria.", "waves", "Scenic"),
            highlight("Birding Possibilities", "Birdlife adds another layer to the sanctuary's nature experience.", "bird", "Birding"),
            highlight("Gentle Outdoor Experience", "A manageable nature outing suited to travellers who want wildlife without a full-day safari.", "leaf", "Nature"),
        ],
        addons=[addon("Private Lakeside Picnic", "Add a pre-arranged picnic where permitted.", "A picnic arrangement can be requested subject to sanctuary rules, location and supplier availability.", 3500, "Per Person")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes for the nature trails.", "Footwear", "shoe"),
            packing("Binoculars", "Useful for birds and distant wildlife.", "Equipment", "binoculars"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Insect Repellent", "Useful around lakeside and wetland habitats.", "Health", "bug"),
        ],
        safety_rows=[
            safety("Follow Sanctuary Rules", "Remain on approved paths and follow guide and sanctuary staff instructions.", "Wildlife", "shield"),
            safety("Keep Wildlife Distance", "Do not approach, feed or touch animals.", "Wildlife", "paw-print"),
            safety("Lakeside Awareness", "Stay away from unstable edges and follow guidance around water.", "Water", "droplets"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable with short nature walks.", "Mobility", True, "shoe"),
            requirement("Entry Fee Confirmation", "Confirm current sanctuary charges before final booking.", "Fees", True, "ticket"),
        ],
        faqs=[
            faq("What wildlife can we see?", "Possible encounters include impalas, sitatunga, giraffes, zebras, buffaloes and several other species, but sightings are not guaranteed.", "Wildlife", True),
            faq("Is it suitable for children?", "Yes, provided children can follow guide instructions and remain with the group.", "Family"),
            faq("Can we birdwatch?", "Yes. Birding can be incorporated into the nature walk and lakeside observation.", "Birding"),
            faq("How long is the experience?", "The standard experience is a half-day outing, with timing confirmed during booking.", "Timing"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_GIRAFFE, "Occasional", "All Year", "Morning", "Giraffes may be encountered in suitable sanctuary habitats.", "Use a telephoto lens and avoid crowding animals."),
            wildlife(WILDLIFE_ZEBRA, "Occasional", "All Year", "Morning", "Zebra may be seen in open areas.", "Observe quietly from permitted viewing positions."),
            wildlife(WILDLIFE_BUFFALO, "Occasional", "All Year", "Morning", "Buffalo may be present; treat them as wild and potentially dangerous.", "Follow guide instructions and maintain distance."),
        ],
        display_order=6,
    ),

    experience(
        code="WES-KSM-002",
        slug="dunga-wetland-lake-victoria-discovery",
        title="Dunga Wetland & Lake Victoria — Boat, Birding & Lakeside Discovery",
        destination_id=20,
        category_id=CATEGORY_CULTURE,
        short_description="A lakeside experience combining Dunga Wetland exploration, birding and a locally coordinated Lake Victoria boat outing.",
        description="Explore the Dunga wetland landscape on the edge of Lake Victoria through a guided nature and community-oriented experience. Depending on the confirmed local arrangement, the outing can combine wetland interpretation, birdwatching and a boat trip on the lake. Water conditions, weather, tides and local operating decisions determine the final route.",
        duration="Half Day",
        meeting_point="Confirmed Dunga-area departure point or accommodation pickup where arranged.",
        location="Dunga, Kisumu County, Kenya",
        price_from=7000,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Dunga Wetland & Lake Victoria Experience | The Uncharted Route",
        meta_description="Explore Dunga Wetland and Lake Victoria through birding, local interpretation and a boat experience.",
        conservation_story_id=None,
        tags=[TAG_NATURE, TAG_BIRD, TAG_PHOTOGRAPHY, TAG_CULTURE],
        moments=[MOMENT_BIRDS, MOMENT_VIEWPOINT, MOMENT_HIDDEN_NATURE],
        pricing_rows=pricing((11500, 16500, 24500), (9000, 13500, 20500), (7000, 10500, 16000), "Indicative TUR selling price per person. Boat, guide and local service charges depend on the confirmed supplier arrangement."),
        itinerary_rows=[
            itinerary("Pickup & Wetland Introduction", "Morning / Afternoon", "Meet the local guide and begin with an introduction to Dunga's wetland and lakeside environment."),
            itinerary("Wetland & Birding Walk", "Main Activity", "Explore suitable wetland areas on foot while observing birdlife and learning about the local ecosystem."),
            itinerary("Lake Victoria Boat Experience", "Later Activity", "Where conditions permit, board the confirmed local boat for a short lakeside exploration and scenic viewing."),
            itinerary("Lakeside Refreshment & Return", "Late Afternoon", "Conclude at the agreed lakeside point and return guests to the confirmed drop-off location."),
        ],
        inclusions=[
            inc("Local Experience Coordination", "TUR coordination of the agreed Dunga route and local service providers.", "route"),
            inc("Local Guide", "Guided interpretation of the wetland and lakeside environment.", "user"),
            inc("Boat Experience", "Boat outing according to the confirmed supplier and weather conditions.", "ship"),
            inc("Birding & Nature Exploration", "Guided observation of wetland habitats and birdlife.", "bird"),
        ],
        exclusions=[
            exc("Boat Upgrade", "Premium or extended boat arrangements are excluded unless selected.", "ship"),
            exc("Meals & Drinks", "Food and drinks unless specifically included.", "utensils"),
            exc("Personal Expenses", "Personal purchases and gratuities are excluded.", "wallet"),
        ],
        highlights=[
            highlight("Dunga Wetland", "Discover a lakeside wetland landscape shaped by water, vegetation and local livelihoods.", "leaf", "Nature"),
            highlight("Birdwatching", "Observe birds in a wetland setting where species and activity vary naturally.", "bird", "Birding"),
            highlight("Lake Victoria by Boat", "See the lakeside landscape from the water when conditions permit.", "ship", "Water"),
            highlight("Local Perspective", "Connect the landscape with local knowledge and everyday life around the lake.", "users", "Culture"),
        ],
        addons=[addon("Private Premium Boat", "Upgrade to a more exclusive boat arrangement.", "A premium private boat can be requested subject to vessel availability and weather conditions.", 6000, "Per Booking")],
        packing_rows=[
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Insect Repellent", "Useful around wetland vegetation.", "Health", "bug"),
            packing("Waterproof Bag", "Protect electronics around the lake and boat.", "Equipment", "bag"),
            packing("Light Clothing", "Wear comfortable clothing suitable for warm lakeside conditions.", "Clothing", "shirt"),
        ],
        safety_rows=[
            safety("Boat Safety", "Follow the boat operator's instructions and remain seated or positioned as directed.", "Marine Safety", "life-buoy"),
            safety("Weather Conditions", "Boat activity may be changed or cancelled if conditions are unsuitable.", "Weather", "cloud"),
            safety("Wetland Terrain", "Stay on guide-approved paths and avoid unstable wetland edges.", "Terrain", "route"),
        ],
        requirements=[
            requirement("Water Activity Disclosure", "Tell the host about swimming limitations or mobility concerns before the experience.", "Health", False, "info"),
            requirement("Confirmed Departure Point", "Provide accommodation and pickup details before the experience date.", "Booking", True, "map-pin"),
        ],
        faqs=[
            faq("Is swimming part of the experience?", "No. The standard experience is focused on wetland exploration and boat viewing; swimming is not included.", "Activity", True),
            faq("Will we see birds?", "Birds are likely in suitable wetland habitats, but particular species and sightings cannot be guaranteed.", "Birding"),
            faq("Can the boat trip be cancelled?", "Yes. Weather, lake conditions and operator safety decisions can require the boat portion to be changed or cancelled.", "Weather"),
            faq("Is this suitable for families?", "It can be suitable for families with older children who can follow wetland and boat safety instructions.", "Family"),
        ],
        display_order=7,
    ),

    experience(
        code="WES-KSM-003",
        slug="ndere-island-national-park-escape",
        title="Ndere Island National Park — Lake Victoria Island Escape",
        destination_id=20,
        category_id=CATEGORY_SAFARI,
        short_description="A full-day island escape from Kisumu combining boat access, nature walks, scenic viewpoints and wildlife observation.",
        description="Travel from Kisumu into the Winam Gulf for a guided day at Ndere Island National Park. The island offers scenic hiking and nature walks, lakeside views and wildlife encounters including impalas, zebras, hippos and crocodiles. Boat access and island activity are subject to weather, water conditions, park rules and the confirmed operating arrangement.",
        duration="Full Day",
        meeting_point="Confirmed Kisumu accommodation or agreed boat departure point.",
        location="Ndere Island National Park, Lake Victoria, Kenya",
        price_from=14500,
        minimum_people=1, maximum_people=6, minimum_age=10, difficulty="Moderate",
        meta_title="Ndere Island National Park Escape | The Uncharted Route",
        meta_description="Escape from Kisumu to Ndere Island for boat travel, nature walks, wildlife and Lake Victoria views.",
        conservation_story_id=None,
        tags=[TAG_WILDLIFE, TAG_NATURE, TAG_HIKING, TAG_PHOTOGRAPHY, TAG_PRIVATE],
        moments=[MOMENT_VIEWPOINT, MOMENT_TRAIL, MOMENT_WILDLIFE_HABITAT],
        pricing_rows=pricing((22000, 31000, 46500), (18000, 25500, 38500), (14500, 21000, 31500), "Indicative TUR selling price per person. KWS park fees, boat charges and guide arrangements must be confirmed before booking."),
        itinerary_rows=[
            itinerary("Kisumu Departure & Boat Transfer", "Morning", "Meet at the confirmed departure point and travel by boat toward Ndere Island, subject to lake conditions."),
            itinerary("Island Nature Walk & Wildlife", "Morning", "Explore permitted trails while observing island vegetation, landscapes and wildlife. Encounters are never guaranteed."),
            itinerary("Scenic Picnic & Lakeside Views", "Midday", "Pause for lunch or a confirmed picnic arrangement and enjoy views across the Winam Gulf."),
            itinerary("Final Walk & Boat Return", "Afternoon", "Complete the island visit and return by boat to the mainland before the agreed Kisumu drop-off."),
        ],
        inclusions=[
            inc("Island Experience Coordination", "TUR coordination of the park visit, boat arrangement and timing.", "route"),
            inc("Boat Transfer", "Boat transport between the agreed mainland departure point and Ndere Island according to the confirmed arrangement.", "ship"),
            inc("Nature & Wildlife Guiding", "Guided exploration of permitted island trails and wildlife habitats.", "user"),
            inc("Scenic Exploration", "Time for island viewpoints, landscapes and photography.", "camera"),
        ],
        exclusions=[
            exc("KWS Park Fees", "Applicable Ndere Island National Park entry and conservation charges unless explicitly included.", "ticket"),
            exc("Meals", "Lunch and drinks unless specifically included or selected as an add-on.", "utensils"),
            exc("Weather-Related Costs", "Additional costs arising from weather-related rescheduling or extended transport are excluded unless agreed.", "cloud"),
        ],
        highlights=[
            highlight("Island Wilderness", "Explore a distinctive island landscape within Lake Victoria.", "island", "Nature"),
            highlight("Boat Access", "Approach the island by water and experience the lake as part of the journey.", "ship", "Water"),
            highlight("Wildlife Possibilities", "Impala, zebra and other wildlife may be encountered, while hippos and crocodiles require particular caution.", "paw-print", "Wildlife"),
            highlight("Panoramic Lake Views", "Enjoy open views across the Winam Gulf and surrounding landscapes.", "mountain", "Scenic"),
        ],
        addons=[addon("Private Island Picnic", "Add a pre-arranged picnic on the island.", "A picnic can be arranged subject to park rules, suitable location and supplier availability.", 5000, "Per Booking")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes suitable for uneven island trails.", "Footwear", "shoe"),
            packing("Sun Protection", "Bring sunscreen, sunglasses and a hat.", "Health", "sun"),
            packing("Waterproof Bag", "Protect valuables during the boat transfer.", "Equipment", "bag"),
            packing("Insect Repellent", "Useful for outdoor island exploration.", "Health", "bug"),
            packing("Drinking Water", "Carry water unless your confirmed package states otherwise.", "General", "bottle-water"),
        ],
        safety_rows=[
            safety("Boat Safety", "Follow the operator's boarding, seating and life-jacket instructions throughout the crossing.", "Water", "life-buoy"),
            safety("Wildlife Distance", "Never approach hippos, crocodiles or other wildlife; follow the guide's positioning instructions.", "Wildlife", "paw-print"),
            safety("Trail Awareness", "Stay on approved trails and watch for uneven ground, rocks and changing weather.", "Terrain", "footprints"),
            safety("Lake Conditions", "Boat departure and return times may change when wind, waves or weather make travel unsuitable.", "Weather", "cloud"),
        ],
        requirements=[
            requirement("Comfortable Walking", "Guests should be comfortable with moderate walking on uneven natural terrain.", "Mobility", True, "shoe"),
            requirement("Boat Activity Disclosure", "Inform the host of any concerns affecting boat travel before booking.", "Health", False, "info"),
        ],
        faqs=[
            faq("How long is the boat crossing?", "KWS information indicates approximately 45 minutes from Kisumu by speed boat, although actual timing depends on the departure point and conditions.", "Transport", True),
            faq("Can we see hippos or crocodiles?", "They may be present, but sightings are not guaranteed and guests must follow strict guide safety instructions around them.", "Wildlife"),
            faq("Is hiking difficult?", "The experience involves natural trails and moderate walking rather than technical hiking, but terrain can be uneven.", "Activity"),
            faq("What happens if the lake is rough?", "The boat schedule or entire outing may be changed or postponed if conditions are unsuitable for safe travel.", "Weather"),
        ],
        wildlife_rows=[
            wildlife(WILDLIFE_HIPPO, "Occasional", "All Year", "Morning", "Hippos may occur around suitable island and lake habitats; they are highly dangerous and must be observed from a safe distance.", "Do not attempt close approaches or leave the guide-approved route."),
            wildlife(WILDLIFE_ZEBRA, "Common", "All Year", "Morning", "Zebra are among the wildlife species supported by the island landscape.", "Observe quietly and use telephoto lenses where possible."),
            wildlife(WILDLIFE_GIRAFFE, "Occasional", "All Year", "Morning", "Giraffes may be encountered where habitat and current movement allow.", "Maintain distance and avoid sudden movements."),
        ],
        display_order=8,
    ),

    # -------------------------------------------------------------------------
    # KERICHO — INACTIVE DESTINATION
    # -------------------------------------------------------------------------
    experience(
        code="HIG-KER-001",
        slug="kericho-tea-country-estate-experience",
        title="Kericho Tea Country — Estate, Factory & Tea Tasting",
        destination_id=22,
        category_id=CATEGORY_CULINARY,
        short_description="A curated Kericho tea-country experience exploring tea landscapes, production and tasting through a confirmed estate or factory arrangement.",
        description="Step into Kericho's highland tea country and discover the journey from green tea fields to the finished cup. The experience is built around a confirmed tea-estate or factory partner and may include a guided plantation walk, an introduction to cultivation and processing, and a tasting. Estate access, factory operating days and production areas vary, so the final route is confirmed before booking.",
        duration="Half Day",
        meeting_point="Confirmed tea-estate or factory entrance; private pickup from Kericho accommodation can be coordinated.",
        location="Kericho, Kericho County, Kenya",
        price_from=8500,
        minimum_people=1, maximum_people=8, minimum_age=8, difficulty="Easy",
        meta_title="Kericho Tea Estate & Tasting Experience | The Uncharted Route",
        meta_description="Discover Kericho's tea country through a guided estate visit, tea production story and tasting experience.",
        conservation_story_id=None,
        tags=[TAG_CULINARY, TAG_FARM, TAG_COFFEE_TEA, TAG_NATURE, TAG_PHOTOGRAPHY],
        moments=[MOMENT_TEA, MOMENT_FARM_TABLE, MOMENT_LANDSCAPES],
        pricing_rows=pricing((13500, 19500, 29500), (10500, 15500, 23500), (8500, 12500, 19000), "Indicative TUR selling price per person. Estate/factory access, tasting and private transport arrangements must be confirmed with the selected partner before booking."),
        itinerary_rows=[
            itinerary("Highland Pickup & Tea Country Introduction", "Morning / Afternoon", "Collect guests from the confirmed meeting point and travel through Kericho's tea landscape while introducing the region's agricultural story."),
            itinerary("Tea Estate Walk", "Main Activity", "Walk through selected tea fields with a local host and learn about cultivation, harvesting and the rhythms of tea production."),
            itinerary("Factory / Processing Story", "Later Activity", "Where the confirmed partner permits, follow the tea journey through selected processing stages and learn how leaf becomes the finished product."),
            itinerary("Tea Tasting & Return", "Late Activity", "Taste selected teas and discuss flavour, preparation and the character of Kericho tea before returning guests to the agreed drop-off point."),
        ],
        inclusions=[
            inc("Estate Visit Coordination", "TUR coordination with the confirmed tea-estate or factory partner.", "route"),
            inc("Guided Tea Experience", "Local interpretation of tea cultivation and the estate landscape.", "leaf"),
            inc("Tea Tasting", "A tasting of selected teas where included by the confirmed partner.", "coffee"),
            inc("Highland Landscape Experience", "Time to appreciate the tea-country scenery and agricultural landscape.", "mountain"),
        ],
        exclusions=[
            exc("Factory Access Not Guaranteed", "Production areas may be closed on certain days or restricted for operational reasons.", "lock"),
            exc("Meals", "Meals are excluded unless specifically included in the selected package.", "utensils"),
            exc("Personal Purchases", "Tea purchases, gratuities and other personal expenses are excluded.", "wallet"),
        ],
        highlights=[
            highlight("Tea Country Landscape", "Experience Kericho's distinctive highland tea estates and green rolling scenery.", "leaf", "Scenic"),
            highlight("From Leaf to Cup", "Understand how tea moves from cultivation and harvest toward processing and tasting.", "coffee", "Culinary"),
            highlight("Guided Tea Tasting", "Taste selected teas and learn how preparation affects flavour and character.", "cup-saucer", "Culinary"),
            highlight("Working Landscape", "Connect the beauty of the tea fields with the people and production systems behind them.", "users", "Culture"),
        ],
        addons=[addon("Premium Tea Tasting", "Expand the tasting with a curated selection.", "A premium tasting can be requested where the selected estate or factory offers the service.", 3000, "Per Person")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes suitable for estate paths.", "Footwear", "shoe"),
            packing("Light Rain Layer", "Kericho's highland weather can change quickly.", "Clothing", "cloud-rain"),
            packing("Sun Protection", "Bring sunscreen and a hat even on cooler days.", "Health", "sun"),
            packing("Camera", "Tea landscapes offer strong photography opportunities where permitted.", "Equipment", "camera"),
        ],
        safety_rows=[
            safety("Follow Estate Instructions", "Stay on approved paths and follow the host's instructions around working areas and machinery.", "Farm Safety", "shield"),
            safety("Factory Safety", "Do not enter restricted production areas or touch machinery unless specifically permitted.", "Factory", "alert-triangle"),
            safety("Wet Ground", "Tea fields can become slippery after rain; use appropriate footwear and watch your footing.", "Terrain", "shoe"),
        ],
        requirements=[
            requirement("Advance Partner Confirmation", "Tea-estate or factory access must be confirmed before the experience date.", "Booking", True, "calendar-check"),
            requirement("Comfortable Walking", "Guests should be comfortable with short walks on estate paths.", "Mobility", True, "shoe"),
        ],
        faqs=[
            faq("Can we visit a tea factory?", "Factory access depends on the confirmed partner's operating schedule and visitor permissions; it is not automatically guaranteed.", "Activity", True),
            faq("Is tea tasting included?", "Yes where the selected partner package includes it; the exact tasting format is confirmed before booking.", "Dining"),
            faq("Can we buy tea?", "Tea purchases may be available at the estate or factory, subject to the partner's retail arrangements.", "Shopping"),
            faq("Is this suitable for children?", "Older children can enjoy the experience, but guests must follow estate and factory safety rules.", "Family"),
        ],
        display_order=9,
    ),

    experience(
        code="HIG-KER-002",
        slug="kericho-highlands-tea-landscape-escape",
        title="Kericho Highlands — Tea Landscapes, Arboretum & Slow Escape",
        destination_id=22,
        category_id=CATEGORY_CULTURE,
        short_description="A slower-paced Kericho escape combining tea-country viewpoints, a selected arboretum and relaxed highland exploration.",
        description="Experience Kericho beyond the factory floor through a relaxed highland day shaped by tea estates, greenery and selected nature spaces. Depending on the confirmed local route, the experience may include an arboretum visit, scenic tea-country viewpoints and time for a quiet local lunch or tea stop. It is designed as a gentle escape rather than a strenuous hike.",
        duration="Half Day",
        meeting_point="Confirmed Kericho accommodation or agreed meeting point.",
        location="Kericho, Kericho County, Kenya",
        price_from=7500,
        minimum_people=1, maximum_people=8, minimum_age=6, difficulty="Easy",
        meta_title="Kericho Highlands Tea Landscape Escape | The Uncharted Route",
        meta_description="Explore Kericho's highland tea landscapes, selected arboretum spaces and scenic viewpoints through a relaxed private escape.",
        conservation_story_id=None,
        tags=[TAG_NATURE, TAG_COFFEE_TEA, TAG_PHOTOGRAPHY, TAG_CULTURE, TAG_FAMILY],
        moments=[MOMENT_VIEWPOINT, MOMENT_TEA, MOMENT_LANDSCAPES],
        pricing_rows=pricing((12000, 17000, 25500), (9500, 14000, 21500), (7500, 11000, 16500), "Indicative TUR selling price per person. Local site entry, transport and dining charges depend on the confirmed route and suppliers."),
        itinerary_rows=[
            itinerary("Pickup & Highland Drive", "Morning / Afternoon", "Meet guests at the agreed point and travel through the tea-country landscape while introducing Kericho's agricultural identity."),
            itinerary("Tea Estate Viewpoints", "Main Activity", "Stop at suitable viewpoints to appreciate the tea estates, highland contours and surrounding scenery."),
            itinerary("Arboretum / Nature Stop", "Later Activity", "Visit a selected arboretum or green space where access is confirmed, with time for a gentle walk and photography."),
            itinerary("Tea / Local Refreshment & Return", "Late Activity", "Finish with a tea or local refreshment stop where arranged before returning guests to their accommodation."),
        ],
        inclusions=[
            inc("Private Route Coordination", "TUR coordination of the agreed highland route and timing.", "route"),
            inc("Driver-Guide", "Driver-guide support and local landscape interpretation.", "user"),
            inc("Scenic Stops", "Selected tea-country viewpoints and nature stops according to the confirmed route.", "mountain"),
            inc("Tea / Refreshment Stop", "A simple tea or refreshment stop where included in the confirmed package.", "coffee"),
        ],
        exclusions=[
            exc("Site Entry Fees", "Any applicable arboretum or attraction entry charges unless explicitly included.", "ticket"),
            exc("Full Meals", "Lunch and full meals unless specifically included.", "utensils"),
            exc("Private Specialty Guide", "Specialist botanical or tea-production guiding is excluded unless separately arranged.", "user"),
        ],
        highlights=[
            highlight("Rolling Tea Estates", "See the distinctive green geometry of Kericho's highland tea country.", "leaf", "Scenic"),
            highlight("Quiet Nature Stop", "Slow down in a selected green space or arboretum away from a crowded itinerary.", "tree-deciduous", "Nature"),
            highlight("Highland Photography", "Capture tea fields, tree lines and changing highland light.", "camera", "Photography"),
            highlight("Tea-Country Rhythm", "Pair scenic exploration with a relaxed tea or refreshment moment.", "coffee", "Slow Travel"),
        ],
        addons=[addon("Private Highland Picnic", "Add a pre-arranged scenic picnic.", "A picnic can be arranged at a suitable private or approved location subject to weather and supplier confirmation.", 4500, "Per Booking")],
        packing_rows=[
            packing("Walking Shoes", "Wear comfortable shoes for gentle nature walks.", "Footwear", "shoe"),
            packing("Light Jacket", "Kericho can feel cool, particularly in the morning and evening.", "Clothing", "jacket"),
            packing("Rain Layer", "Carry a light waterproof layer for changeable highland weather.", "Clothing", "cloud-rain"),
            packing("Camera", "Bring a camera for tea landscapes and nature scenes.", "Equipment", "camera"),
        ],
        safety_rows=[
            safety("Weather Awareness", "Highland weather can change quickly; follow the guide's route adjustments when necessary.", "Weather", "cloud"),
            safety("Estate Boundaries", "Do not enter private tea fields or working areas without permission.", "Farm Safety", "shield"),
            safety("Uneven Paths", "Use care on wet or uneven nature trails.", "Terrain", "footprints"),
        ],
        requirements=[
            requirement("Comfortable Outdoor Clothing", "Dress for cool, changeable highland weather.", "Clothing", True, "shirt"),
            requirement("Confirmed Route", "Final attraction and tea-estate stops depend on access and supplier confirmation.", "Booking", True, "calendar-check"),
        ],
        faqs=[
            faq("Is this a hiking trip?", "No. It is a gentle scenic experience with short walks rather than a strenuous hike.", "Activity", True),
            faq("Will we walk through tea fields?", "Only where the selected estate or landowner has granted access; otherwise the experience uses approved viewpoints.", "Access"),
            faq("Can we add lunch?", "Yes, a dining arrangement can be requested depending on the selected route and supplier.", "Dining"),
            faq("What makes Kericho special?", "Its highland setting, extensive tea estates and cool green landscapes give it a distinctive character within Kenya's South Rift tourism circuit.", "Destination"),
        ],
        display_order=10,
    ),
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
            print("THE UNCHARTED ROUTE — BATCH 2: KENYAN LAKES, RIFT & HIGHLANDS")
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
                print("BATCH 2 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(f"Created {len(created)} complete Kenyan Lakes, Rift & Highlands experiences.")
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
            print("BATCH 2 FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Commit the population to the database.")
    args = parser.parse_args()
    populate(apply_changes=args.apply)
