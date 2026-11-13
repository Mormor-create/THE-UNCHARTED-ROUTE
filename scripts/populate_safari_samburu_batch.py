"""
===============================================================================
THE UNCHARTED ROUTE — BATCH 2 — SAMBURU SAFARI CATALOGUE
===============================================================================

Purpose
-------
Populate the independent Safari catalogue for Samburu.

Scope
-----
Destination:
    Samburu National Reserve

Properties:
    1. Sasaab
    2. Saruni Samburu
    3. Elephant Bedroom Camp
    4. Samburu Intrepids

Package durations:
    3 Days / 2 Nights
    5 Days / 4 Nights
    7 Days / 6 Nights

Total package slots:
    4 properties x 3 durations = 12

Population rules
----------------
- Reuse existing Samburu destination if present.
- Reuse existing Samburu properties if present.
- Never duplicate properties by slug.
- Never duplicate package options by property + slug.
- Never modify existing package rates.
- Never create fake SafariInquiry records.
- Never touch SafariBooking.
- Do not create media associations.
- Complete missing itinerary days only where a canonical existing package
  is reused and incomplete.
- Create three indicative TUR selling-rate records for each newly-created
  package.
- Use one transaction.
- Roll back the entire batch on failure.
- Default mode is DRY RUN.
- --apply commits the batch.

Pricing note
------------
The rates in this seed are indicative TUR catalogue selling benchmarks.
They are NOT represented as contracted supplier rates.

Supplier/property confirmation is required before quoting a traveller.
Seasonal validity is deliberately explicit so that the catalogue can later
be replaced with confirmed contracted rates without changing package
structure.

SafariBooking and SafariInquiry are operational/customer records and are
explicitly excluded from this population batch.
===============================================================================
"""

from __future__ import annotations
import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from extensions import db
from app.models.safari import (
    SafariDestination,
    SafariProperty,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
)

# =============================================================================
# CONSTANTS
# =============================================================================

BATCH_NAME = "BATCH 2 — SAMBURU SAFARI CATALOGUE"

DESTINATION_NAME = "Samburu National Reserve"
DESTINATION_SLUG = "samburu"

SUPPORTED_DURATIONS = (
    (3, 2),
    (5, 4),
    (7, 6),
)

DEFAULT_CURRENCY = "USD"

STANDARD_VALID_FROM = date(2026, 11, 5)
STANDARD_VALID_TO = date(2027, 6, 30)

PEAK_VALID_FROM = date(2027, 7, 1)
PEAK_VALID_TO = date(2027, 10, 31)

FESTIVE_VALID_FROM = date(2027, 12, 20)
FESTIVE_VALID_TO = date(2028, 1, 10)


# =============================================================================
# PROPERTY CATALOGUE
# =============================================================================

PROPERTIES = [
    {
        "name": "Sasaab",
        "slug": "sasaab",
        "property_type": "lodge",
        "short_description": (
            "An intimate luxury lodge overlooking the Samburu landscape, "
            "combining dramatic views, private space, cultural connection "
            "and exceptional northern Kenya wildlife."
        ),
        "overview": (
            "Sasaab is a distinctive Samburu safari retreat positioned above "
            "the Ewaso Ng'iro landscape. The property combines spacious "
            "private accommodation, dramatic northern Kenya scenery and "
            "access to wildlife and cultural experiences around Samburu."
        ),
        "property_story": (
            "Sasaab's character comes from the meeting of northern Kenya "
            "landscape, refined hospitality and a strong sense of place. "
            "The experience is designed around space, privacy, views and "
            "meaningful encounters rather than a conventional high-volume "
            "safari model."
        ),
        "location_description": (
            "Located in the Samburu region with elevated views across the "
            "surrounding landscape and access to Samburu wildlife areas."
        ),
        "accommodation_details": (
            "Spacious private suites designed around comfort, privacy and "
            "views, with outdoor space and a strong connection to the "
            "surrounding landscape."
        ),
        "facilities": (
            "Private accommodation, swimming pool, dining areas, lounge "
            "spaces, wellness facilities and outdoor areas."
        ),
        "dining_information": (
            "Full-board dining with meals prepared around fresh ingredients "
            "and flexible safari-day timing. Special dietary requirements "
            "should be communicated before arrival."
        ),
        "activities": (
            "Game drives, guided nature experiences where available, "
            "cultural encounters, scenic exploration, photography and "
            "property-based relaxation."
        ),
        "wildlife_experience": (
            "Excellent access to Samburu wildlife including elephants, "
            "reticulated giraffe, Grevy's zebra, gerenuk, Beisa oryx, "
            "Somali ostrich and other northern Kenya species."
        ),
        "transport_information": (
            "Road transfers from Nairobi can be arranged. Air access may "
            "also be available through regional safari airstrips depending "
            "on the final itinerary and operating schedule."
        ),
        "check_in_information": (
            "Check-in is coordinated with the property's arrival schedule. "
            "Guests should provide final arrival and transfer details in advance."
        ),
        "check_out_information": (
            "Check-out is coordinated around the final morning activity and "
            "the onward transfer schedule."
        ),
        "child_policy": (
            "Family suitability and child minimum-age requirements should be "
            "confirmed with the property before booking."
        ),
        "accessibility_information": (
            "Accessibility varies by accommodation and terrain. Specific "
            "mobility requirements should be confirmed before booking."
        ),
        "booking_conditions": (
            "Rates are indicative TUR selling benchmarks and require supplier "
            "confirmation before final quotation. Property terms, cancellation "
            "conditions and conservation or park fees may apply separately."
        ),
        "official_website_url": "https://www.sasaab.com/",
        "location_name": "Samburu, Kenya",
        "display_order": 1,
        "featured": True,
        "active": True,
        "rates": {
            "standard": 1500.00,
            "peak": 1850.00,
            "festive": 2150.00,
        },
    },
    {
        "name": "Saruni Samburu",
        "slug": "saruni-samburu",
        "property_type": "lodge",
        "short_description": (
            "A distinctive luxury safari lodge in Kalama Conservancy, "
            "known for dramatic northern Kenya views, spacious architecture "
            "and immersive wildlife and cultural experiences."
        ),
        "overview": (
            "Saruni Samburu sits within the wider Samburu ecosystem and "
            "offers a high-end safari experience shaped by elevated views, "
            "open landscapes, conservation and access to both wildlife and "
            "cultural experiences."
        ),
        "property_story": (
            "Saruni Samburu is designed to make the northern Kenya landscape "
            "part of the stay itself. The experience combines architecture, "
            "wilderness, conservation and community connection, making it "
            "particularly suited to travellers seeking a more interpretive "
            "safari rather than a conventional lodge-only stay."
        ),
        "location_description": (
            "Set in Kalama Conservancy above the Samburu ecosystem, with "
            "dramatic views across the surrounding northern Kenya landscape."
        ),
        "accommodation_details": (
            "Spacious individually styled bandas and private accommodation "
            "designed to maximise privacy, views and connection to the "
            "surrounding landscape."
        ),
        "facilities": (
            "Swimming pool, dining areas, lounge spaces, wellness facilities, "
            "viewing areas and outdoor spaces."
        ),
        "dining_information": (
            "Full-board safari dining with meals coordinated around game "
            "drives and other activities. Dietary requirements should be "
            "provided before arrival."
        ),
        "activities": (
            "Game drives, guided walks where permitted, cultural experiences, "
            "conservation experiences, scenic exploration, photography and "
            "relaxation."
        ),
        "wildlife_experience": (
            "Strong access to Samburu's northern species including Grevy's "
            "zebra, reticulated giraffe, gerenuk, Beisa oryx and Somali "
            "ostrich, alongside elephants, lions, leopards and other wildlife."
        ),
        "transport_information": (
            "Road and scheduled or chartered air connections may be used "
            "depending on the final itinerary. Transfer arrangements should "
            "be confirmed before travel."
        ),
        "check_in_information": (
            "Arrival timing should be coordinated with the lodge and the "
            "planned safari transfer."
        ),
        "check_out_information": (
            "Departure is normally coordinated around the final morning "
            "activity and onward transfer."
        ),
        "child_policy": (
            "Children may be accommodated subject to current property policy "
            "and room configuration. Confirm minimum ages before booking."
        ),
        "accessibility_information": (
            "The property is located in a natural conservancy environment "
            "with uneven terrain. Specific accessibility requirements require "
            "advance confirmation."
        ),
        "booking_conditions": (
            "Rates are indicative TUR selling benchmarks and require supplier "
            "confirmation. Conservation, park and other mandatory charges may "
            "be additional depending on the final arrangement."
        ),
        "official_website_url": "https://sarunibasecamp.com/saruni-samburu/",
        "location_name": "Kalama Conservancy, Samburu, Kenya",
        "display_order": 2,
        "featured": True,
        "active": True,
        "rates": {
            "standard": 1750.00,
            "peak": 2250.00,
            "festive": 2550.00,
        },
    },
    {
        "name": "Elephant Bedroom Camp",
        "slug": "elephant-bedroom-camp",
        "property_type": "tented_camp",
        "short_description": (
            "An intimate riverside safari camp in Samburu, offering a "
            "strong elephant-watching experience alongside classic northern "
            "Kenya wildlife and tented-camp atmosphere."
        ),
        "overview": (
            "Elephant Bedroom Camp is positioned along the Ewaso Nyiro River "
            "in the Samburu ecosystem. Its setting makes riverine wildlife, "
            "elephants and intimate tented safari experiences central to the "
            "stay."
        ),
        "property_story": (
            "The camp's identity is rooted in the relationship between the "
            "river, elephants and the surrounding Samburu wilderness. It "
            "offers a more intimate safari atmosphere while retaining strong "
            "access to the reserve's wildlife."
        ),
        "location_description": (
            "Riverside setting along the Ewaso Nyiro River within the "
            "Samburu wildlife ecosystem."
        ),
        "accommodation_details": (
            "Spacious luxury safari tents with private outdoor space and "
            "views toward the river and surrounding wilderness."
        ),
        "facilities": (
            "Swimming pool, dining area, lounge, private tented accommodation "
            "and outdoor safari spaces."
        ),
        "dining_information": (
            "Full-board safari meals served around the daily game-drive "
            "schedule. Bush dining may be available subject to conditions "
            "and lodge arrangements."
        ),
        "activities": (
            "Game drives, elephant viewing, birding, photography, cultural "
            "experiences and selected guided nature activities."
        ),
        "wildlife_experience": (
            "Particularly well suited to elephant encounters and riverine "
            "wildlife, while also offering access to Samburu's Special Five "
            "and broader northern Kenya wildlife."
        ),
        "transport_information": (
            "Road transfer and safari-air access may be used depending on "
            "the itinerary. Final transfer arrangements require confirmation."
        ),
        "check_in_information": (
            "Arrival is coordinated with camp transfer schedules and the "
            "day's safari activities."
        ),
        "check_out_information": (
            "Departure is normally coordinated after breakfast and the "
            "morning safari activity."
        ),
        "child_policy": (
            "Children are subject to current camp age and accommodation "
            "policies. Confirm before booking."
        ),
        "accessibility_information": (
            "Natural camp terrain can be uneven. Mobility requirements should "
            "be discussed with the property in advance."
        ),
        "booking_conditions": (
            "Rates are indicative TUR selling benchmarks and require supplier "
            "confirmation. Conservation, park and applicable mandatory fees "
            "may be charged separately."
        ),
        "official_website_url": "https://www.elephantbedroomcamp.com/",
        "location_name": "Samburu National Reserve, Kenya",
        "display_order": 3,
        "featured": True,
        "active": True,
        "rates": {
            "standard": 1250.00,
            "peak": 1550.00,
            "festive": 1800.00,
        },
    },
    {
        "name": "Samburu Intrepids",
        "slug": "samburu-intrepids",
        "property_type": "tented_camp",
        "short_description": (
            "A polished riverside tented safari camp offering classic "
            "Samburu game viewing, family-friendly safari appeal and access "
            "to the reserve's distinctive northern wildlife."
        ),
        "overview": (
            "Samburu Intrepids provides a classic tented safari experience "
            "along the Ewaso Nyiro River, combining comfortable accommodation "
            "with strong access to Samburu game drives and wildlife."
        ),
        "property_story": (
            "The camp is designed around the traditional safari rhythm: "
            "early mornings, wildlife-rich game drives, relaxed midday hours "
            "and evening storytelling around the wilderness setting."
        ),
        "location_description": (
            "Riverside location within the Samburu ecosystem, providing "
            "convenient access to wildlife areas."
        ),
        "accommodation_details": (
            "Comfortable safari tents with private facilities and outdoor "
            "spaces, arranged to retain the feel of a classic tented camp."
        ),
        "facilities": (
            "Swimming pool, dining area, lounge, safari activity areas and "
            "family-oriented guest facilities."
        ),
        "dining_information": (
            "Full-board meals structured around safari activities, with "
            "special dietary requests accommodated where arranged in advance."
        ),
        "activities": (
            "Game drives, birding, cultural experiences, photography, "
            "nature-based activities and selected family-oriented experiences."
        ),
        "wildlife_experience": (
            "Excellent opportunity to encounter elephants, lions, leopards, "
            "reticulated giraffe, Grevy's zebra, gerenuk, Beisa oryx, "
            "Somali ostrich and other Samburu wildlife."
        ),
        "transport_information": (
            "Accessible by road and regional safari air connections depending "
            "on the itinerary. Transfers should be arranged in advance."
        ),
        "check_in_information": (
            "Check-in follows the property's safari transfer schedule."
        ),
        "check_out_information": (
            "Check-out is coordinated with the final safari activity and "
            "onward transport."
        ),
        "child_policy": (
            "The camp can be suitable for families subject to current "
            "property policies, room configuration and age requirements."
        ),
        "accessibility_information": (
            "Natural camp terrain may be uneven. Guests requiring assistance "
            "should advise TUR before confirmation."
        ),
        "booking_conditions": (
            "Rates are indicative TUR selling benchmarks and require supplier "
            "confirmation before final quotation. Applicable conservation, "
            "park and mandatory charges may be additional."
        ),
        "official_website_url": "https://www.intrepids.co.ke/samburu-intrepids/",
        "location_name": "Samburu National Reserve, Kenya",
        "display_order": 4,
        "featured": True,
        "active": True,
        "rates": {
            "standard": 1100.00,
            "peak": 1350.00,
            "festive": 1550.00,
        },
    },
]


# =============================================================================
# PACKAGE CONTENT
# =============================================================================

def package_content(property_data, duration_days, duration_nights):
    """
    Build package-level content and itinerary for one property/duration.
    """

    property_name = property_data["name"]

    if duration_days == 3:
        title = f"{property_name} — 3 Days, 2 Nights"
        slug = f"{property_data['slug']}-3-days-2-nights"

        description = (
            f"A focused {property_name} safari designed for travellers who "
            "want to experience Samburu's distinctive northern landscapes "
            "and wildlife without committing to a longer stay. The journey "
            "combines arrival, afternoon wildlife viewing, a full safari day "
            "and a final morning game drive."
        )

        days = [
            {
                "day_number": 1,
                "title": "Into Samburu — Arrival & First Game Drive",
                "description": (
                    f"Travel into Samburu and settle into {property_name}. "
                    "After lunch and a short orientation, head into the "
                    "wilderness for the first game drive, beginning the "
                    "search for elephants and Samburu's distinctive northern "
                    "species."
                ),
                "morning_activities": (
                    "Road or air transfer into Samburu; arrival procedures "
                    "and check-in."
                ),
                "afternoon_activities": (
                    "Lunch followed by an introductory game drive through "
                    "the Samburu ecosystem."
                ),
                "evening_activities": (
                    "Return to camp, sundowners where conditions permit, "
                    "dinner and relaxed safari briefing."
                ),
                "meals_included": "Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": (
                    "Scheduled or private safari transfer depending on the "
                    "confirmed itinerary."
                ),
                "notes": (
                    "Wildlife sightings are naturally unpredictable. "
                    "The first drive is planned around arrival timing."
                ),
            },
            {
                "day_number": 2,
                "title": "The Samburu Special Five — Full Safari Day",
                "description": (
                    "Spend a full day exploring the Samburu ecosystem, with "
                    "time for extended game viewing and photography. The "
                    "focus is on species that make northern Kenya distinctive, "
                    "including Grevy's zebra, reticulated giraffe, gerenuk, "
                    "Beisa oryx and Somali ostrich."
                ),
                "morning_activities": (
                    "Early morning game drive with emphasis on active "
                    "wildlife and the cooler morning hours."
                ),
                "afternoon_activities": (
                    "Breakfast or bush breakfast followed by continued "
                    "wildlife exploration; return for lunch and a later "
                    "afternoon drive."
                ),
                "evening_activities": (
                    "Return to camp, sundowner opportunity, dinner and "
                    "optional stargazing or storytelling."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": (
                    "Safari vehicle for full-day game viewing; picnic or "
                    "bush breakfast may be arranged where appropriate."
                ),
                "notes": (
                    "The day's route is adapted to wildlife movement, "
                    "weather and conservation-area operating conditions."
                ),
            },
            {
                "day_number": 3,
                "title": "Final Wildlife Encounter — Departure",
                "description": (
                    "Rise early for a final safari drive before breakfast. "
                    "After returning to camp, complete check-out and begin "
                    "the onward journey from Samburu."
                ),
                "morning_activities": (
                    "Early morning game drive followed by breakfast."
                ),
                "afternoon_activities": (
                    "Check-out and onward road or air transfer."
                ),
                "evening_activities": (
                    "Arrival at the onward destination according to the "
                    "confirmed transfer schedule."
                ),
                "meals_included": "Breakfast, Lunch",
                "overnight_location": "Departure / onward destination",
                "transport_details": (
                    "Transfer from Samburu to Nairobi or the next destination."
                ),
                "notes": (
                    "Final transfer timing depends on the selected road or "
                    "air connection."
                ),
            },
        ]

    elif duration_days == 5:
        title = f"{property_name} — 5 Days, 4 Nights"
        slug = f"{property_data['slug']}-5-days-4-nights"

        description = (
            f"A deeper Samburu journey at {property_name}, allowing more "
            "time for wildlife tracking, photography, relaxed game drives, "
            "riverine landscapes and cultural discovery."
        )

        days = [
            {
                "day_number": 1,
                "title": "Arrival in Samburu — First Impressions",
                "description": (
                    f"Travel into Samburu, arrive at {property_name}, settle "
                    "into camp and enjoy the first afternoon wildlife drive."
                ),
                "morning_activities": "Transfer into Samburu and arrival.",
                "afternoon_activities": (
                    "Lunch, orientation and first afternoon game drive."
                ),
                "evening_activities": (
                    "Sundowner opportunity, dinner and safari briefing."
                ),
                "meals_included": "Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Road or safari-air transfer.",
                "notes": "Drive timing follows the confirmed arrival schedule.",
            },
            {
                "day_number": 2,
                "title": "Northern Kenya Wildlife — Special Five",
                "description": (
                    "A full safari day dedicated to Samburu's distinctive "
                    "wildlife and the landscapes surrounding the Ewaso Nyiro."
                ),
                "morning_activities": (
                    "Early game drive searching for Grevy's zebra, "
                    "reticulated giraffe, gerenuk and elephants."
                ),
                "afternoon_activities": (
                    "Breakfast, continued exploration, lunch and an "
                    "afternoon game drive."
                ),
                "evening_activities": (
                    "Return to camp, dinner and evening relaxation."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Private or shared safari vehicle.",
                "notes": "Routes adapt to wildlife movement and conditions.",
            },
            {
                "day_number": 3,
                "title": "River, Wildlife & Samburu Culture",
                "description": (
                    "Explore the riverine ecosystem and, where arranged, "
                    "add a responsible cultural experience introducing "
                    "guests to Samburu traditions and community life."
                ),
                "morning_activities": (
                    "Morning game drive around riverine and open habitats."
                ),
                "afternoon_activities": (
                    "Lunch followed by cultural or community experience "
                    "where available and appropriate."
                ),
                "evening_activities": (
                    "Late game drive or camp-based relaxation followed by dinner."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle and local transfer where required.",
                "notes": (
                    "Cultural activities should be conducted through "
                    "responsible community partners."
                ),
            },
            {
                "day_number": 4,
                "title": "Wildlife Photography & Wilderness Rhythm",
                "description": (
                    "Use another full day to explore Samburu at a slower "
                    "pace, allowing time for repeat sightings, photography "
                    "and less hurried wildlife observation."
                ),
                "morning_activities": (
                    "Extended early morning photographic game drive."
                ),
                "afternoon_activities": (
                    "Breakfast, midday rest, lunch and afternoon wildlife drive."
                ),
                "evening_activities": (
                    "Sundowner, dinner and optional stargazing."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle.",
                "notes": (
                    "Photography opportunities depend on wildlife behaviour "
                    "and light conditions."
                ),
            },
            {
                "day_number": 5,
                "title": "Final Game Drive — Departure",
                "description": (
                    "Enjoy a final early safari before breakfast and "
                    "departure from Samburu."
                ),
                "morning_activities": (
                    "Final game drive followed by breakfast and check-out."
                ),
                "afternoon_activities": (
                    "Onward road or air transfer."
                ),
                "evening_activities": (
                    "Arrival at the onward destination."
                ),
                "meals_included": "Breakfast, Lunch",
                "overnight_location": "Departure / onward destination",
                "transport_details": "Transfer from Samburu.",
                "notes": "Final timing depends on onward travel arrangements.",
            },
        ]

    else:
        title = f"{property_name} — 7 Days, 6 Nights"
        slug = f"{property_data['slug']}-7-days-6-nights"

        description = (
            f"An immersive seven-day Samburu safari based at {property_name}, "
            "allowing a slower pace for wildlife viewing, photography, "
            "cultural discovery, conservation interpretation and repeated "
            "exploration of the reserve and surrounding conservancies."
        )

        days = [
            {
                "day_number": 1,
                "title": "Arrival in Samburu — Into the North",
                "description": (
                    f"Travel into Samburu and settle into {property_name}. "
                    "The first afternoon introduces the landscape and "
                    "wildlife of northern Kenya."
                ),
                "morning_activities": "Transfer into Samburu.",
                "afternoon_activities": "Lunch, orientation and first game drive.",
                "evening_activities": "Sundowner and dinner.",
                "meals_included": "Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Road or safari-air transfer.",
                "notes": "Arrival-day activity depends on transfer timing.",
            },
            {
                "day_number": 2,
                "title": "Samburu Special Five — Full Day",
                "description": (
                    "Spend the day searching for the wildlife that gives "
                    "Samburu its distinctive character."
                ),
                "morning_activities": (
                    "Early game drive targeting Grevy's zebra, reticulated "
                    "giraffe, gerenuk and elephants."
                ),
                "afternoon_activities": (
                    "Breakfast or bush breakfast, lunch and continued game viewing."
                ),
                "evening_activities": "Return, sundowner and dinner.",
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle.",
                "notes": "Wildlife sightings are never guaranteed.",
            },
            {
                "day_number": 3,
                "title": "Ewaso Nyiro — River & Wildlife",
                "description": (
                    "Explore the riverine habitats and wildlife corridors "
                    "around the Ewaso Nyiro."
                ),
                "morning_activities": "River-focused morning game drive.",
                "afternoon_activities": (
                    "Lunch and afternoon exploration of open and riverine habitats."
                ),
                "evening_activities": "Dinner and relaxed evening.",
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle.",
                "notes": "Route selected according to wildlife activity.",
            },
            {
                "day_number": 4,
                "title": "Samburu Culture & Conservation",
                "description": (
                    "Explore the human and conservation story of the region "
                    "through a responsible cultural or conservation experience."
                ),
                "morning_activities": (
                    "Morning game drive and wildlife observation."
                ),
                "afternoon_activities": (
                    "Responsible cultural or conservation experience, "
                    "subject to availability."
                ),
                "evening_activities": (
                    "Return to camp and dinner."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": (
                    "Safari vehicle and local transfer where required."
                ),
                "notes": (
                    "Community experiences must be delivered respectfully "
                    "through approved local partners."
                ),
            },
            {
                "day_number": 5,
                "title": "Predators, Elephants & Photography",
                "description": (
                    "Use a full day for patient wildlife observation, "
                    "photography and predator tracking where conditions "
                    "provide opportunities."
                ),
                "morning_activities": (
                    "Early photographic game drive."
                ),
                "afternoon_activities": (
                    "Midday rest followed by afternoon game drive."
                ),
                "evening_activities": (
                    "Sundowner, dinner and optional stargazing."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle.",
                "notes": (
                    "Predator sightings are opportunistic and cannot be guaranteed."
                ),
            },
            {
                "day_number": 6,
                "title": "The Samburu Landscape — Final Full Safari",
                "description": (
                    "A final full day to revisit productive wildlife areas, "
                    "photograph the landscape and enjoy the safari at an "
                    "unhurried pace."
                ),
                "morning_activities": (
                    "Extended early game drive."
                ),
                "afternoon_activities": (
                    "Breakfast, rest, lunch and final extended afternoon drive."
                ),
                "evening_activities": (
                    "Farewell sundowner and dinner."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle.",
                "notes": (
                    "The final route is selected according to wildlife "
                    "movement and guest interests."
                ),
            },
            {
                "day_number": 7,
                "title": "Last Look at Samburu — Departure",
                "description": (
                    "Take a final early morning drive before breakfast, "
                    "check-out and departure from Samburu."
                ),
                "morning_activities": (
                    "Final game drive followed by breakfast."
                ),
                "afternoon_activities": (
                    "Check-out and onward road or air transfer."
                ),
                "evening_activities": (
                    "Arrival at the onward destination."
                ),
                "meals_included": "Breakfast, Lunch",
                "overnight_location": "Departure / onward destination",
                "transport_details": "Transfer from Samburu.",
                "notes": "Departure timing depends on onward arrangements.",
            },
        ]

    return {
        "name": title,
        "slug": slug,
        "summary": (
            f"{duration_days}-day Samburu safari at {property_name}, "
            "combining wildlife, landscapes and carefully paced safari "
            "experiences in northern Kenya."
        ),
        "description": description,
        "duration_days": duration_days,
        "duration_nights": duration_nights,
        "display_currency": DEFAULT_CURRENCY,
        "inclusions": (
            "Accommodation at the selected safari property; full-board "
            "meals as stated; scheduled safari activities; game drives; "
            "professional safari guiding; applicable standard property "
            "services; bottled drinking water during safari activities."
        ),
        "exclusions": (
            "International flights; domestic flights unless specifically "
            "included; travel insurance; visas; personal purchases; "
            "premium drinks; gratuities; laundry; optional activities; "
            "park, conservancy or conservation fees not explicitly included; "
            "medical evacuation; costs arising from itinerary changes."
        ),
        "transport_details": (
            "Road or safari-air transfers can be incorporated according to "
            "the final itinerary. Private vehicle arrangements are available "
            "as a separately confirmed upgrade where applicable."
        ),
        "meals_information": (
            "Full board at the safari property, with breakfast, lunch and "
            "dinner included according to the itinerary. Bush meals may "
            "replace camp meals when operationally appropriate."
        ),
        "important_information": (
            "Safari activities are wildlife experiences in a natural "
            "environment and sightings cannot be guaranteed. Exact routes "
            "depend on wildlife movement, weather, conservation-area rules "
            "and operating conditions. Rates are indicative and require "
            "supplier confirmation before final traveller quotation."
        ),
        "days": days,
    }


# =============================================================================
# RATE BUILDING
# =============================================================================

def package_rate_amounts(property_data, duration_nights):
    """
    Convert indicative nightly benchmarks into indicative package totals.

    The figures intentionally remain simple catalogue benchmarks.
    Supplier confirmation is required before quoting.
    """

    nightly = property_data["rates"]

    return {
        "standard": round(nightly["standard"] * duration_nights, 2),
        "peak": round(nightly["peak"] * duration_nights, 2),
        "festive": round(nightly["festive"] * duration_nights, 2),
    }


def rate_definitions(property_data, duration_nights):
    amounts = package_rate_amounts(property_data, duration_nights)

    return [
        {
            "name": "Standard Season — Per Person Sharing",
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": None,
            "amount": amounts["standard"],
            "currency": DEFAULT_CURRENCY,
            "season_name": "Standard Season",
            "valid_from": STANDARD_VALID_FROM,
            "valid_to": STANDARD_VALID_TO,
            "board_basis": "Full Board",
            "supplier_rate_reference": None,
            "rate_notes": (
                "Indicative TUR selling benchmark. Supplier confirmation "
                "required before final quotation. Package total is based "
                "on the indicative property benchmark multiplied by nights."
            ),
            "display_order": 1,
        },
        {
            "name": "Peak Season — Per Person Sharing",
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": None,
            "amount": amounts["peak"],
            "currency": DEFAULT_CURRENCY,
            "season_name": "Peak Season",
            "valid_from": PEAK_VALID_FROM,
            "valid_to": PEAK_VALID_TO,
            "board_basis": "Full Board",
            "supplier_rate_reference": None,
            "rate_notes": (
                "Indicative TUR selling benchmark. Supplier confirmation "
                "required before final quotation."
            ),
            "display_order": 2,
        },
        {
            "name": "Festive Season — Per Person Sharing",
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": None,
            "amount": amounts["festive"],
            "currency": DEFAULT_CURRENCY,
            "season_name": "Festive Season",
            "valid_from": FESTIVE_VALID_FROM,
            "valid_to": FESTIVE_VALID_TO,
            "board_basis": "Full Board",
            "supplier_rate_reference": None,
            "rate_notes": (
                "Indicative TUR selling benchmark. Festive availability "
                "and supplier pricing must be confirmed before quotation."
            ),
            "display_order": 3,
        },
    ]


# =============================================================================
# HELPERS
# =============================================================================

def get_destination():
    return (
        SafariDestination.query
        .filter(
            SafariDestination.slug.ilike(DESTINATION_SLUG)
        )
        .first()
    )


def get_property(destination_id, slug):
    return (
        SafariProperty.query
        .filter(
            SafariProperty.destination_id == destination_id,
            SafariProperty.slug.ilike(slug),
        )
        .first()
    )


def get_package(property_id, slug):
    return (
        SafariPackageOption.query
        .filter(
            SafariPackageOption.property_id == property_id,
            SafariPackageOption.slug.ilike(slug),
        )
        .first()
    )


def package_rates(package_id):
    return (
        SafariPackageRate.query
        .filter(
            SafariPackageRate.package_option_id == package_id,
        )
        .order_by(
            SafariPackageRate.display_order.asc(),
            SafariPackageRate.id.asc(),
        )
        .all()
    )


def itinerary_days(package_id):
    return (
        SafariItineraryDay.query
        .filter(
            SafariItineraryDay.package_option_id == package_id,
        )
        .order_by(
            SafariItineraryDay.day_number.asc(),
        )
        .all()
    )


def create_destination():
    existing = get_destination()

    if existing:
        return existing, False

    destination = SafariDestination(
        name=DESTINATION_NAME,
        slug=DESTINATION_SLUG,
        short_description=(
            "A distinctive northern Kenya safari destination known for "
            "Samburu's Special Five, elephants, dramatic landscapes, "
            "the Ewaso Nyiro River and rich cultural heritage."
        ),
        introduction=(
            "Samburu offers a very different safari rhythm from Kenya's "
            "southern grasslands. The landscape is shaped by dry-country "
            "rivers, rugged hills, open plains and the Ewaso Nyiro, while "
            "wildlife includes several species strongly associated with "
            "northern Kenya."
        ),
        history=(
            "The Samburu region has a long relationship between pastoralist "
            "communities, wildlife and the dry-country landscape. The "
            "Samburu people and surrounding communities remain an important "
            "part of the region's cultural identity."
        ),
        landscape_and_wildlife=(
            "The landscape combines riverine vegetation, dry plains, rocky "
            "hills and acacia country. Wildlife highlights include elephants, "
            "lions, leopards, reticulated giraffe, Grevy's zebra, gerenuk, "
            "Beisa oryx and Somali ostrich."
        ),
        conservation_story=(
            "Samburu's conservation landscape combines protected reserve "
            "areas with surrounding community and private conservancies. "
            "Tourism contributes to wildlife protection, local employment "
            "and community-linked conservation initiatives."
        ),
        travel_information=(
            "Samburu can be reached by road from Nairobi or through regional "
            "safari air connections. Travel times vary with the selected "
            "route and aircraft schedule. Dry-season and wet-season conditions "
            "can affect road travel."
        ),
        display_order=2,
        active=True,
        featured=True,
    )

    db.session.add(destination)
    db.session.flush()

    return destination, True


def create_property(destination, property_data):
    existing = get_property(
        destination.id,
        property_data["slug"],
    )

    if existing:
        return existing, False

    property_record = SafariProperty(
        destination_id=destination.id,
        name=property_data["name"],
        slug=property_data["slug"],
        property_type=property_data["property_type"],
        short_description=property_data["short_description"],
        overview=property_data["overview"],
        property_story=property_data["property_story"],
        location_description=property_data["location_description"],
        accommodation_details=property_data["accommodation_details"],
        facilities=property_data["facilities"],
        dining_information=property_data["dining_information"],
        activities=property_data["activities"],
        wildlife_experience=property_data["wildlife_experience"],
        transport_information=property_data["transport_information"],
        check_in_information=property_data["check_in_information"],
        check_out_information=property_data["check_out_information"],
        child_policy=property_data["child_policy"],
        accessibility_information=property_data["accessibility_information"],
        booking_conditions=property_data["booking_conditions"],
        official_website_url=property_data["official_website_url"],
        location_name=property_data["location_name"],
        display_order=property_data["display_order"],
        active=property_data["active"],
        featured=property_data["featured"],
    )

    db.session.add(property_record)
    db.session.flush()

    return property_record, True


def create_package(property_record, package_data):
    existing = get_package(
        property_record.id,
        package_data["slug"],
    )

    if existing:
        return existing, False

    package = SafariPackageOption(
        property_id=property_record.id,
        name=package_data["name"],
        slug=package_data["slug"],
        summary=package_data["summary"],
        description=package_data["description"],
        duration_days=package_data["duration_days"],
        duration_nights=package_data["duration_nights"],
        display_currency=package_data["display_currency"],
        inclusions=package_data["inclusions"],
        exclusions=package_data["exclusions"],
        transport_details=package_data["transport_details"],
        meals_information=package_data["meals_information"],
        important_information=package_data["important_information"],
        display_order=package_data["duration_days"],
        active=True,
        featured=(package_data["duration_days"] == 5),
    )

    db.session.add(package)
    db.session.flush()

    return package, True


def create_itinerary_days(package, package_data):
    existing_days = itinerary_days(package.id)
    existing_numbers = {
        day.day_number
        for day in existing_days
    }

    created = 0

    for day_data in package_data["days"]:
        if day_data["day_number"] in existing_numbers:
            continue

        day = SafariItineraryDay(
            package_option_id=package.id,
            day_number=day_data["day_number"],
            title=day_data["title"],
            description=day_data["description"],
            active=True,
            morning_activities=day_data["morning_activities"],
            afternoon_activities=day_data["afternoon_activities"],
            evening_activities=day_data["evening_activities"],
            meals_included=day_data["meals_included"],
            overnight_location=day_data["overnight_location"],
            transport_details=day_data["transport_details"],
            notes=day_data["notes"],
        )

        db.session.add(day)
        created += 1

    db.session.flush()

    return created


def create_rates(package, property_data):
    existing_rates = package_rates(package.id)

    if existing_rates:
        return 0

    definitions = rate_definitions(
        property_data,
        package.duration_nights,
    )

    for rate_data in definitions:
        rate = SafariPackageRate(
            package_option_id=package.id,
            name=rate_data["name"],
            pricing_basis=rate_data["pricing_basis"],
            guest_category=rate_data["guest_category"],
            occupancy_type=rate_data["occupancy_type"],
            min_guest_age=None,
            max_guest_age=None,
            min_guests=rate_data["min_guests"],
            max_guests=rate_data["max_guests"],
            amount=rate_data["amount"],
            currency=rate_data["currency"],
            season_name=rate_data["season_name"],
            valid_from=rate_data["valid_from"],
            valid_to=rate_data["valid_to"],
            board_basis=rate_data["board_basis"],
            supplier_rate_reference=rate_data["supplier_rate_reference"],
            rate_notes=rate_data["rate_notes"],
            active=True,
            display_order=rate_data["display_order"],
        )

        db.session.add(rate)

    db.session.flush()

    return len(definitions)


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_batch(destination):
    print("\n" + "=" * 110)
    print("BATCH VERIFICATION")
    print("=" * 110)

    if destination is None:
        raise RuntimeError("Samburu destination could not be verified.")

    print(
        f"Destination verified: {destination.name} | "
        f"active={destination.active}"
    )

    properties = (
        SafariProperty.query
        .filter(
            SafariProperty.destination_id == destination.id,
        )
        .order_by(
            SafariProperty.display_order.asc(),
            SafariProperty.id.asc(),
        )
        .all()
    )

    if len(properties) != 4:
        raise RuntimeError(
            f"Expected 4 Samburu properties, got {len(properties)}."
        )

    print(f"Properties in Samburu catalogue: {len(properties)}")

    packages = (
        SafariPackageOption.query
        .join(
            SafariProperty,
            SafariPackageOption.property_id
            == SafariProperty.id,
        )
        .filter(
            SafariProperty.destination_id == destination.id,
        )
        .order_by(
            SafariPackageOption.id.asc(),
        )
        .all()
    )

    if len(packages) != 12:
        raise RuntimeError(
            f"Expected 12 Samburu packages, got {len(packages)}."
        )

    print(f"Total Samburu packages: {len(packages)}")

    expected_package_count = 0
    expected_itinerary_count = 0
    expected_rate_count = 0

    for property_data in PROPERTIES:
        property_record = get_property(
            destination.id,
            property_data["slug"],
        )

        if property_record is None:
            raise RuntimeError(
                f"Property verification failed: "
                f"{property_data['name']}"
            )

        for duration_days, duration_nights in SUPPORTED_DURATIONS:
            package_data = package_content(
                property_data,
                duration_days,
                duration_nights,
            )

            package = get_package(
                property_record.id,
                package_data["slug"],
            )

            if package is None:
                raise RuntimeError(
                    f"Package verification failed: "
                    f"{package_data['name']}"
                )

            days = itinerary_days(package.id)
            rates = package_rates(package.id)

            if len(days) != duration_days:
                raise RuntimeError(
                    f"{package.name}: expected "
                    f"{duration_days} itinerary days, got {len(days)}."
                )

            if len(rates) != 3:
                raise RuntimeError(
                    f"{package.name}: expected 3 rates, got {len(rates)}."
                )

            expected_package_count += 1
            expected_itinerary_count += duration_days
            expected_rate_count += 3

            print(
                f"      {package.name} | "
                f"{duration_days}D/{duration_nights}N | "
                f"itinerary={len(days)} | "
                f"rates={len(rates)}"
            )

    if expected_package_count != 12:
        raise RuntimeError(
            f"Package count verification failed: "
            f"expected 12, got {expected_package_count}."
        )

    if expected_itinerary_count != 60:
        raise RuntimeError(
            f"Itinerary expectation failed: "
            f"expected 60, got {expected_itinerary_count}."
        )

    if expected_rate_count != 36:
        raise RuntimeError(
            f"Rate expectation failed: "
            f"expected 36, got {expected_rate_count}."
        )

    print(f"All Samburu packages verified: {expected_package_count}")
    print(f"All itinerary days verified: {expected_itinerary_count}")
    print(f"All package rates verified: {expected_rate_count}")

    # Operational/customer data must remain untouched.
    from app.models import SafariInquiry

    inquiry_count = SafariInquiry.query.count()

    print(f"\nSafariInquiry records preserved: {inquiry_count}")
    print("SafariBooking: NOT TOUCHED")
    print("Media records created: 0")


# =============================================================================
# MAIN POPULATION
# =============================================================================

def populate(apply_changes=False):
    app = create_app()

    with app.app_context():

        print("\n" + "=" * 110)
        print("THE UNCHARTED ROUTE — BATCH 2 — SAMBURU SAFARI CATALOGUE")
        print("=" * 110)
        print(f"Mode: {'APPLY' if apply_changes else 'DRY RUN'}")
        print("Destination scope: Samburu only")
        print("Package durations: 3D/2N, 5D/4N, 7D/6N")
        print("Existing records: reused and preserved")
        print("Existing package rates: preserved, never modified")
        print("SafariBooking: untouched")
        print("SafariInquiry: untouched")
        print("Media: no new media associations")
        print("=" * 110)

        destination_created = 0
        properties_created = 0
        properties_reused = 0
        packages_created = 0
        packages_reused = 0
        itinerary_days_added = 0
        package_rates_added = 0

        try:
            # -----------------------------------------------------------------
            # DESTINATION
            # -----------------------------------------------------------------

            destination, was_created = create_destination()

            if was_created:
                destination_created += 1
                destination_status = "CREATED"
            else:
                destination_status = "REUSED"

            print(
                f"\nDestination: {destination.name} | "
                f"ID={destination.id} | {destination_status}"
            )

            # -----------------------------------------------------------------
            # PROPERTY CATALOGUE
            # -----------------------------------------------------------------

            print("\n" + "-" * 110)
            print("PROPERTY CATALOGUE")
            print("-" * 110)

            property_records = []

            for index, property_data in enumerate(PROPERTIES, start=1):

                property_record, was_created = create_property(
                    destination,
                    property_data,
                )

                if was_created:
                    properties_created += 1
                    status = "CREATED"
                else:
                    properties_reused += 1
                    status = "REUSED"

                property_records.append(
                    (property_record, property_data)
                )

                print(
                    f"  [{index:02d}/{len(PROPERTIES)}] "
                    f"{property_record.name} | "
                    f"ID={property_record.id} | {status}"
                )

            # -----------------------------------------------------------------
            # PACKAGE CATALOGUE
            # -----------------------------------------------------------------

            print("\n" + "-" * 110)
            print("PACKAGE CATALOGUE")
            print("-" * 110)

            for property_record, property_data in property_records:

                print(f"\n  {property_record.name}")

                for duration_days, duration_nights in SUPPORTED_DURATIONS:

                    package_data = package_content(
                        property_data,
                        duration_days,
                        duration_nights,
                    )

                    package, was_created = create_package(
                        property_record,
                        package_data,
                    )

                    if was_created:
                        packages_created += 1
                        package_status = "CREATED"

                        days_added = create_itinerary_days(
                            package,
                            package_data,
                        )

                        rates_added = create_rates(
                            package,
                            property_data,
                        )

                        itinerary_days_added += days_added
                        package_rates_added += rates_added

                    else:
                        packages_reused += 1
                        package_status = "EXISTING"

                        # Existing package records are preserved.
                        # Only missing itinerary days are completed.
                        days_added = create_itinerary_days(
                            package,
                            package_data,
                        )

                        # Existing rates are NEVER modified.
                        rates_added = 0

                        itinerary_days_added += days_added

                    print(
                        f"    {package.name} | "
                        f"{package_status} | "
                        f"itinerary +{days_added} | "
                        f"rates +{rates_added}"
                    )

            # -----------------------------------------------------------------
            # VERIFICATION
            # -----------------------------------------------------------------

            verify_batch(destination)

            # -----------------------------------------------------------------
            # SUMMARY
            # -----------------------------------------------------------------

            print("\n" + "=" * 110)
            print("SUMMARY")
            print("=" * 110)

            print(
                f"Destination created:        {destination_created}"
            )
            print(
                f"Properties created:         {properties_created}"
            )
            print(
                f"Properties reused:          {properties_reused}"
            )
            print(
                f"Packages created:           {packages_created}"
            )
            print(
                f"Packages reused:            {packages_reused}"
            )
            print(
                f"Total package slots:        "
                f"{packages_created + packages_reused}"
            )
            print(
                f"Itinerary days added:       {itinerary_days_added}"
            )
            print(
                f"Package rates added:        {package_rates_added}"
            )
            print(
                "Safari inquiries:           "
                f"{__import__('app.models', fromlist=['SafariInquiry']).SafariInquiry.query.count()}"
            )
            print("Safari bookings touched:    0")
            print("Media records created:      0")

            # -----------------------------------------------------------------
            # FINAL TRANSACTION
            # -----------------------------------------------------------------

            if apply_changes:
                db.session.commit()

                print("\n" + "=" * 110)
                print("BATCH 2 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(
                    "Samburu safari catalogue populated successfully."
                )
                print(
                    "Existing operational/customer records were preserved."
                )

            else:
                db.session.rollback()

                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)
                print("No database changes were committed.")
                print(
                    "Run with --apply only after reviewing the output."
                )

        except Exception:
            db.session.rollback()

            print("\n" + "=" * 110)
            print("BATCH 2 FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)

            raise


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate the TUR Samburu Safari catalogue."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the population to the database.",
    )

    args = parser.parse_args()

    populate(
        apply_changes=args.apply,
    )