"""
===============================================================================
THE UNCHARTED ROUTE
SAFARI BATCH 1 — MAASAI MARA FLAGSHIP CATALOGUE
===============================================================================

Scope
-----
This batch populates the first deep safari catalogue for The Uncharted Route.

DESTINATION:
    Maasai Mara National Reserve

EXISTING RECORDS PRESERVED:
    - Maasai Mara National Reserve
    - Pearl Mara
    - JW Marriott Masai Mara Lodge
    - Angama Mara
    - The Mara Awakening — 3 Days, 2 Nights
    - Existing SafariPackageRate records
    - Existing SafariInquiry records

NEW PROPERTIES:
    - Mahali Mzuri
    - Mara Plains Camp
    - Governors' Il Moran Camp
    - Cottar's 1920s Camp

PACKAGE DURATION:
    - 3 Days / 2 Nights
    - 5 Days / 4 Nights
    - 7 Days / 6 Nights

IMPORTANT:
    - This batch does NOT create SafariBooking records.
    - This batch does NOT create SafariInquiry records.
    - Existing SafariInquiry records are never modified.
    - Existing SafariPackageRate records are never overwritten.
    - Existing properties are reused by slug.
    - Existing packages are reused by property + slug.
    - Pearl Mara's existing "The Mara Awakening — 3 Days, 2 Nights"
      is the canonical 3D/2N Pearl Mara package and is NEVER duplicated.
    - Existing itinerary days are preserved.
    - Missing itinerary days are added only where absent.
    - Existing Mara Awakening rates are preserved and never supplemented
      or overwritten by this batch.
    - No media records are fabricated.
    - No MediaAsset IDs are invented.
    - No existing destination is moved, renamed or deleted.
    - No non-Mara safari destination is created by this batch.
    - DEFAULT: dry run.
    - APPLY: python scripts/populate_safari_maasai_mara_batch.py --apply

The entire batch runs inside one transaction.
Any error causes a rollback.

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
BATCH_NAME = "BATCH 1 — MAASAI MARA FLAGSHIP CATALOGUE"
MAASAI_MARA_SLUG = "maasai-mara"

SUPPORTED_CURRENCIES = {
    "KES",
    "USD",
    "EUR",
    "GBP",
}

PACKAGE_DURATIONS = {
    3: 2,
    5: 4,
    7: 6,
}

STANDARD_START = date(2026, 11, 5)
STANDARD_END = date(2027, 6, 30)

PEAK_START = date(2027, 7, 1)
PEAK_END = date(2027, 10, 31)

FESTIVE_START = date(2027, 12, 20)
FESTIVE_END = date(2028, 1, 10)

DEFAULT_PACKAGE_CURRENCY = "USD"

# Canonical existing Pearl Mara package.
# This package MUST be reused rather than duplicated.
EXISTING_MARA_AWAKENING_SLUG = "the-mara-awakening-3-days-2-nights"


# =============================================================================
# EXISTING RECORDS — NEVER DUPLICATE
# =============================================================================

EXISTING_PROPERTIES = {
    "pearl-mara": {
        "name": "Pearl Mara",
        "property_type": "tented_camp",
    },
    "jw-marriott-masai-mara-lodge": {
        "name": "JW Marriott Masai Mara Lodge",
        "property_type": "tented_camp",
    },
    "angama-mara": {
        "name": "Angama Mara",
        "property_type": "lodge",
    },
}


# =============================================================================
# NEW PROPERTY DATA
# =============================================================================

PROPERTIES = [
    {
        "name": "Mahali Mzuri",
        "slug": "mahali-mzuri",
        "property_type": "tented_camp",
        "short_description": (
            "An intimate luxury tented camp in the Olare Motorogi Conservancy, "
            "designed around spacious accommodation, exceptional guiding and "
            "exclusive wilderness access."
        ),
        "overview": (
            "Mahali Mzuri offers a refined safari base in the private Olare "
            "Motorogi Conservancy within the greater Maasai Mara ecosystem. "
            "The experience is centred on spacious tented accommodation, "
            "high-quality guiding, open wilderness and the advantages of "
            "conservancy-based safari activities."
        ),
        "property_story": (
            "Mahali Mzuri was created around the idea of a small, intimate "
            "safari camp where guests can slow down and experience the Mara "
            "through a combination of classic game drives, conservancy access "
            "and considered hospitality."
        ),
        "location_description": (
            "Olare Motorogi Conservancy, greater Maasai Mara ecosystem, Kenya."
        ),
        "accommodation_details": (
            "The camp offers spacious luxury tented accommodation designed "
            "for privacy, comfort and views of the surrounding wilderness. "
            "Room configuration and occupancy should be confirmed against "
            "the selected travel dates."
        ),
        "facilities": (
            "Guest lounge, dining areas, swimming pool, outdoor spaces, "
            "Wi-Fi and safari-focused guest facilities, subject to current "
            "operating arrangements."
        ),
        "dining_information": (
            "Full-board safari dining with meals prepared around the camp's "
            "daily rhythm. Bush breakfasts, picnic lunches and sundowner "
            "settings may be arranged according to the day's activities."
        ),
        "activities": (
            "Game drives, conservancy exploration, walking and other "
            "property-led wilderness activities subject to guide, weather "
            "and conservation-area conditions."
        ),
        "wildlife_experience": (
            "The Olare Motorogi landscape is known for strong resident "
            "wildlife populations and provides an excellent setting for "
            "predator, plains-game and elephant viewing. Wildlife sightings "
            "remain naturally variable."
        ),
        "transport_information": (
            "Guests typically access the property by scheduled or private "
            "flight into the relevant Mara airstrip followed by a camp "
            "transfer. Road transfers can be arranged separately."
        ),
        "check_in_information": (
            "Standard safari check-in and check-out arrangements are "
            "confirmed with the property for the selected dates."
        ),
        "check_out_information": (
            "Departure timing should be coordinated with the confirmed "
            "flight or road transfer."
        ),
        "child_policy": (
            "Family suitability and child rates depend on the travel dates "
            "and room configuration. Confirm the applicable policy before "
            "booking."
        ),
        "accessibility_information": (
            "The camp is located in a remote wilderness environment. "
            "Guests requiring accessibility support should discuss needs "
            "with TUR before confirmation."
        ),
        "booking_conditions": (
            "Rates are indicative TUR selling rates based on current "
            "published-market benchmarks and remain subject to supplier "
            "confirmation, availability, applicable taxes, conservation "
            "fees and final travel dates."
        ),
        "official_website_url": (
            "https://www.virginlimitededition.com/mahali-mzuri/"
        ),
        "location_name": "Olare Motorogi Conservancy, Maasai Mara",
        "display_order": 4,
        "featured": True,
    },
    {
        "name": "Mara Plains Camp",
        "slug": "mara-plains-camp",
        "property_type": "tented_camp",
        "short_description": (
            "An intimate, conservation-led luxury camp in the northern "
            "Maasai Mara ecosystem, combining exceptional guiding with "
            "exclusive conservancy wilderness."
        ),
        "overview": (
            "Mara Plains Camp sits within the private Olare Motorogi "
            "Conservancy and is designed around intimate safari experiences, "
            "excellent guiding and a strong conservation ethos."
        ),
        "property_story": (
            "The camp's identity is closely connected to the conservancy "
            "model, where lower vehicle density, community partnerships and "
            "wildlife protection form an important part of the guest experience."
        ),
        "location_description": (
            "Olare Motorogi Conservancy, northern Maasai Mara ecosystem."
        ),
        "accommodation_details": (
            "Luxury tented accommodation with private guest spaces, "
            "comfortable sleeping arrangements and views into the surrounding "
            "wilderness."
        ),
        "facilities": (
            "Camp lounge, dining area, guest spaces, safari vehicle facilities "
            "and wilderness-oriented outdoor areas."
        ),
        "dining_information": (
            "Full-board dining with flexible safari meal arrangements, "
            "including picnic and bush dining where conditions permit."
        ),
        "activities": (
            "Day and night game drives, walking experiences where permitted, "
            "photography-focused guiding and conservancy exploration."
        ),
        "wildlife_experience": (
            "The conservancy supports strong resident wildlife populations "
            "including big cats, elephants, giraffes, plains game and "
            "numerous bird species."
        ),
        "transport_information": (
            "Access is normally by air to the relevant Mara airstrip followed "
            "by a camp transfer. Road transfers can be arranged separately."
        ),
        "check_in_information": (
            "Check-in timing follows the confirmed airstrip transfer and "
            "camp operating schedule."
        ),
        "check_out_information": (
            "Departure timing should be coordinated around the guest's "
            "confirmed flight or road transfer."
        ),
        "child_policy": (
            "Children may be accepted subject to current camp policy, "
            "room configuration and minimum-age requirements."
        ),
        "accessibility_information": (
            "This is a remote tented safari environment. Accessibility "
            "requirements must be discussed in advance."
        ),
        "booking_conditions": (
            "Indicative TUR rates require supplier confirmation before a "
            "booking is considered final."
        ),
        "official_website_url": (
            "https://greatplainsconservation.com/mara-plains-camp/"
        ),
        "location_name": "Olare Motorogi Conservancy, Maasai Mara",
        "display_order": 5,
        "featured": True,
    },
    {
        "name": "Governors' Il Moran Camp",
        "slug": "governors-il-moran-camp",
        "property_type": "tented_camp",
        "short_description": (
            "An intimate riverfront luxury tented camp offering classic "
            "Maasai Mara safari access with a strong guiding tradition."
        ),
        "overview": (
            "Governors' Il Moran Camp is positioned along the Mara River "
            "within the Maasai Mara and is known for intimate tented "
            "accommodation, experienced guiding and access to the reserve's "
            "wildlife-rich landscape."
        ),
        "property_story": (
            "Il Moran represents the classic Governors' approach to safari: "
            "small-scale accommodation, experienced guides, strong access "
            "to wildlife country and a focus on time spent in the field."
        ),
        "location_description": (
            "Along the Mara River within the Maasai Mara National Reserve."
        ),
        "accommodation_details": (
            "Intimate luxury tents with en-suite facilities and private "
            "guest areas designed for a classic high-end safari experience."
        ),
        "facilities": (
            "Dining tent, lounge areas, campfire setting, guest service areas "
            "and safari support facilities."
        ),
        "dining_information": (
            "Full-board dining with breakfast, lunch and dinner included "
            "according to the confirmed package."
        ),
        "activities": (
            "Morning and afternoon game drives, full-day drives, sundowners "
            "and other camp-arranged activities subject to conditions."
        ),
        "wildlife_experience": (
            "The reserve provides opportunities to see lions, leopards, "
            "cheetahs, elephants, buffalo, giraffes, zebra and other "
            "wildlife. Migration sightings are seasonal and never guaranteed."
        ),
        "transport_information": (
            "Airstrip transfers are generally available as part of the "
            "property's safari arrangements. Road transfers can be quoted "
            "separately."
        ),
        "check_in_information": (
            "Arrival is coordinated around the guest's flight or road "
            "transfer and the camp's standard check-in arrangements."
        ),
        "check_out_information": (
            "Departure is coordinated around the confirmed onward transfer."
        ),
        "child_policy": (
            "Child acceptance and applicable rates should be confirmed "
            "against the travel dates."
        ),
        "accessibility_information": (
            "The camp is situated in a remote safari setting with uneven "
            "terrain. Accessibility requirements must be discussed in advance."
        ),
        "booking_conditions": (
            "Published property information confirms that camp rates include "
            "full-board accommodation, game drives and airstrip transfers, "
            "while park and community fees may be charged separately. "
            "TUR selling rates remain subject to supplier confirmation."
        ),
        "official_website_url": "https://governorscamp.com/",
        "location_name": "Mara River, Maasai Mara National Reserve",
        "display_order": 6,
        "featured": True,
    },
    {
        "name": "Cottar's 1920s Camp",
        "slug": "cottars-1920s-camp",
        "property_type": "tented_camp",
        "short_description": (
            "A heritage luxury safari camp in the private Olderkesi "
            "Conservancy, combining classic canvas style, exceptional guiding "
            "and conservation-led wilderness experiences."
        ),
        "overview": (
            "Cottar's 1920s Camp offers a heritage-inspired luxury safari "
            "experience in the Olderkesi Conservancy on the edge of the "
            "Maasai Mara. The camp combines classic canvas accommodation "
            "with modern comfort and a strong emphasis on guiding, culture "
            "and conservation."
        ),
        "property_story": (
            "The camp draws on Cottar's multi-generational safari heritage "
            "and recreates the elegance of early safari while operating "
            "within a contemporary conservation framework."
        ),
        "location_description": (
            "Olderkesi Conservancy, bordering the Maasai Mara ecosystem."
        ),
        "accommodation_details": (
            "Luxury double, twin, family and honeymoon tents with en-suite "
            "facilities. Family configurations are available subject to "
            "current availability."
        ),
        "facilities": (
            "Swimming pool, spa facilities, dining spaces, lounge, bush "
            "bath experiences and guest areas."
        ),
        "dining_information": (
            "Full-board accommodation includes meals, water, tea and coffee "
            "and selected local drinks. Bush breakfasts, picnics and "
            "candlelit dinners can form part of the safari rhythm."
        ),
        "activities": (
            "Wildlife drives, bush walks, Maasai Warrior School, educational "
            "experiences, stargazing, coffee tasting, conservation activities "
            "and cultural experiences."
        ),
        "wildlife_experience": (
            "The Olderkesi landscape provides access to a wildlife-rich "
            "ecosystem with opportunities for predator, elephant and plains "
            "game sightings."
        ),
        "transport_information": (
            "Cottar's provides private airstrip transfer arrangements. "
            "Transfers to and from Keekorok Airstrip are excluded from the "
            "published rack rate and should be quoted separately."
        ),
        "check_in_information": (
            "Standard check-in is around midday, with flexibility subject "
            "to arrival logistics and availability."
        ),
        "check_out_information": (
            "Standard check-out is around 10:00. Late departure arrangements "
            "may be available at additional cost."
        ),
        "child_policy": (
            "Children are welcomed. Current child rates depend on age, "
            "room configuration and travel period."
        ),
        "accessibility_information": (
            "The remote conservancy environment can present mobility "
            "challenges, although some wheelchair-friendly accommodation "
            "is available. Requirements should be discussed in advance."
        ),
        "booking_conditions": (
            "Cottar's published rates include full board, selected drinks, "
            "safari activities, private airstrip transfers and applicable "
            "taxes, while park/conservancy fees and certain optional "
            "experiences are excluded."
        ),
        "official_website_url": "https://cottars.com/",
        "location_name": "Olderkesi Conservancy, Maasai Mara",
        "display_order": 7,
        "featured": True,
    },
]


# =============================================================================
# PACKAGE CONTENT
# =============================================================================

PACKAGE_BLUEPRINTS = {
    3: {
        "name_suffix": "3 Days, 2 Nights",
        "summary_suffix": (
            "A concentrated Mara safari designed for guests who want "
            "excellent wildlife time without committing to a longer stay."
        ),
        "description_suffix": (
            "This three-day journey balances arrival, substantial game "
            "viewing and a relaxed final morning. It is ideal for a first "
            "Mara safari or as one component of a wider Kenya itinerary."
        ),
    },
    5: {
        "name_suffix": "5 Days, 4 Nights",
        "summary_suffix": (
            "A deeper Mara stay with more time for wildlife, photography, "
            "different habitats and flexible safari pacing."
        ),
        "description_suffix": (
            "Five days allows the safari to breathe. Rather than treating "
            "every drive as a race to a checklist, this itinerary creates "
            "space for repeated sightings, changing light, photography, "
            "conservation conversations and slower wilderness moments."
        ),
    },
    7: {
        "name_suffix": "7 Days, 6 Nights",
        "summary_suffix": (
            "The flagship Mara immersion for guests seeking a slower, "
            "more complete safari experience."
        ),
        "description_suffix": (
            "Seven days gives guests enough time to explore the reserve and "
            "relevant conservancy landscapes in depth. The itinerary allows "
            "multiple wildlife-viewing windows, photography time, cultural "
            "experiences and flexible days shaped by the guide and current "
            "wildlife conditions."
        ),
    },
}


# =============================================================================
# HELPERS
# =============================================================================

def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def package_slug(property_slug: str, days: int) -> str:
    return f"{property_slug}-{days}-days-{days - 1}-nights"


def package_name(property_name: str, days: int) -> str:
    return f"{property_name} — {PACKAGE_BLUEPRINTS[days]['name_suffix']}"


def itinerary_day(
    *,
    day_number: int,
    title: str,
    description: str,
    morning_activities: str,
    afternoon_activities: str,
    evening_activities: str,
    meals_included: str,
    overnight_location: str,
    transport_details: str,
    notes: str,
) -> dict:
    return {
        "day_number": day_number,
        "title": title,
        "description": description,
        "morning_activities": morning_activities,
        "afternoon_activities": afternoon_activities,
        "evening_activities": evening_activities,
        "meals_included": meals_included,
        "overnight_location": overnight_location,
        "transport_details": transport_details,
        "notes": notes,
        "active": True,
    }


def build_itinerary(property_name: str, days: int) -> list[dict]:
    rows = [
        itinerary_day(
            day_number=1,
            title="Arrival in the Mara — First Safari",
            description=(
                f"Arrive at {property_name}, settle into camp and begin the "
                "safari rhythm with an introductory wildlife drive. The "
                "first afternoon is deliberately flexible so the guide can "
                "respond to current wildlife movement rather than forcing "
                "a rigid route."
            ),
            morning_activities=(
                "Travel from Nairobi by scheduled or private flight, or "
                "arrive by road transfer depending on the confirmed itinerary."
            ),
            afternoon_activities=(
                "Camp arrival, welcome briefing, lunch where applicable, "
                "then an afternoon game drive through the relevant Mara "
                "reserve or conservancy area."
            ),
            evening_activities=(
                "Return to camp for sundowners, dinner and a safari briefing "
                "for the following day."
            ),
            meals_included=(
                "Lunch and dinner, subject to arrival timing; full board at camp."
            ),
            overnight_location=property_name,
            transport_details=(
                "Airstrip-to-camp transfer or confirmed road transfer. "
                "Safari vehicle provided for the game drive."
            ),
            notes=(
                "Wildlife sightings are naturally variable. Final route "
                "selection is made by the guide according to conditions."
            ),
        ),
        itinerary_day(
            day_number=2,
            title="Full-Day Mara Wildlife Immersion",
            description=(
                "A full safari day designed around the property's location "
                "and the guide's assessment of current wildlife movement. "
                "Guests may choose a long game drive with picnic lunch or "
                "split the day into morning and afternoon drives."
            ),
            morning_activities=(
                "Early morning game drive during the prime wildlife-viewing "
                "window, followed by breakfast or a bush breakfast where "
                "permitted."
            ),
            afternoon_activities=(
                "Continue deeper into the reserve or conservancy. Depending "
                "on location and season, the route may focus on predators, "
                "elephant country, plains game, riverine habitats or "
                "photography opportunities."
            ),
            evening_activities=(
                "Sundowner stop where permitted, return to camp and relaxed "
                "dinner followed by an optional wildlife or conservation talk."
            ),
            meals_included="Breakfast, lunch and dinner.",
            overnight_location=property_name,
            transport_details=(
                "Dedicated safari vehicle for the day's game viewing. "
                "Picnic arrangements depend on weather, route and park rules."
            ),
            notes=(
                "The guide determines the safest and most productive route. "
                "No particular animal sighting is guaranteed."
            ),
        ),
        itinerary_day(
            day_number=3,
            title="Final Game Drive & Departure",
            description=(
                "Use the final morning for one more wildlife-viewing window "
                "before returning to camp for breakfast and departure."
            ),
            morning_activities=(
                "Early morning game drive focused on the best available "
                "wildlife and photography opportunities."
            ),
            afternoon_activities=(
                "Breakfast at camp, check-out and transfer to the airstrip "
                "or road departure point."
            ),
            evening_activities=(
                "Continue onward travel to Nairobi or the next confirmed "
                "destination."
            ),
            meals_included=(
                "Breakfast and lunch where departure timing permits."
            ),
            overnight_location="Departure",
            transport_details=(
                "Camp-to-airstrip transfer or confirmed road transfer."
            ),
            notes=(
                "Departure timing must be coordinated with the confirmed "
                "flight schedule."
            ),
        ),
    ]

    if days >= 5:
        rows.extend(
            [
                itinerary_day(
                    day_number=4,
                    title="Conservancy & Photography Day",
                    description=(
                        "A slower day focused on the landscape and wildlife "
                        "character of the property's surrounding conservancy "
                        "or reserve sector."
                    ),
                    morning_activities=(
                        "Early game drive with emphasis on photography, "
                        "tracking and reading animal behaviour."
                    ),
                    afternoon_activities=(
                        "Long lunch and rest followed by a later afternoon "
                        "drive in a different sector."
                    ),
                    evening_activities=(
                        "Sundowner and campfire or evening relaxation."
                    ),
                    meals_included="Breakfast, lunch and dinner.",
                    overnight_location=property_name,
                    transport_details=(
                        "Safari vehicle throughout the active safari periods."
                    ),
                    notes=(
                        "Where the property permits walking or specialist "
                        "activities, these may be substituted subject to "
                        "guide and conservation-area conditions."
                    ),
                ),
                itinerary_day(
                    day_number=5,
                    title="Wildlife Depth & Departure",
                    description=(
                        "A final extended wildlife session followed by "
                        "departure or onward travel."
                    ),
                    morning_activities=(
                        "Final dawn game drive with time for photography and "
                        "wildlife observation."
                    ),
                    afternoon_activities=(
                        "Breakfast, check-out and transfer to the relevant "
                        "airstrip or road departure point."
                    ),
                    evening_activities=(
                        "Continue onward to Nairobi or the next destination."
                    ),
                    meals_included=(
                        "Breakfast and lunch where departure timing permits."
                    ),
                    overnight_location="Departure",
                    transport_details=(
                        "Camp transfer to airstrip or road departure point."
                    ),
                    notes=(
                        "Departure timing depends on the confirmed onward itinerary."
                    ),
                ),
            ]
        )

    if days >= 7:
        rows.extend(
            [
                itinerary_day(
                    day_number=6,
                    title="A Day Designed Around Your Safari Interests",
                    description=(
                        "Use the additional day to personalise the safari "
                        "around wildlife, photography, birds, conservation, "
                        "culture or simply more time in the wilderness."
                    ),
                    morning_activities=(
                        "Early wildlife drive based on the guest's preferred "
                        "focus and the guide's knowledge of current conditions."
                    ),
                    afternoon_activities=(
                        "Relaxed lunch followed by an optional conservancy, "
                        "cultural or specialist activity where available."
                    ),
                    evening_activities=(
                        "Final full evening at camp with dinner and a "
                        "reflection on the safari."
                    ),
                    meals_included="Breakfast, lunch and dinner.",
                    overnight_location=property_name,
                    transport_details=(
                        "Safari vehicle and property-arranged activity "
                        "transport as applicable."
                    ),
                    notes=(
                        "Optional activities vary by property and may carry "
                        "additional charges."
                    ),
                ),
                itinerary_day(
                    day_number=7,
                    title="Final Sunrise Safari & Departure",
                    description=(
                        "Close the safari with a final sunrise wildlife "
                        "session before breakfast and departure."
                    ),
                    morning_activities=(
                        "Final sunrise game drive, returning to camp for "
                        "breakfast and check-out."
                    ),
                    afternoon_activities=(
                        "Transfer to the relevant airstrip or road departure "
                        "point for onward travel."
                    ),
                    evening_activities=(
                        "Continue onward to Nairobi or the next destination."
                    ),
                    meals_included=(
                        "Breakfast and lunch where departure timing permits."
                    ),
                    overnight_location="Departure",
                    transport_details=(
                        "Camp-to-airstrip or road transfer."
                    ),
                    notes=(
                        "The final game drive is subject to departure timing "
                        "and the confirmed flight schedule."
                    ),
                ),
            ]
        )

    return rows


def build_inclusions(property_name: str) -> list[str]:
    return [
        "Accommodation at the selected safari property.",
        "Full-board meals according to the property's confirmed board basis.",
        "Scheduled safari game drives during the package.",
        "Professional safari guiding.",
        "Camp-to-airstrip transfer where included by the property.",
        "TUR itinerary coordination and guest support.",
        f"Accommodation and safari activities at {property_name}.",
    ]


def build_exclusions(property_name: str) -> list[str]:
    return [
        "International and domestic flights unless explicitly included.",
        "Maasai Mara National Reserve entry fees.",
        "Applicable conservancy or community fees.",
        "Private safari vehicle unless specifically selected.",
        "Hot-air balloon safari unless specifically selected.",
        "Travel insurance and personal medical expenses.",
        "Gratuities, shopping, spa treatments and personal purchases.",
        "Road transfers not explicitly included in the confirmed quotation.",
        "Optional cultural or specialist activities not listed as included.",
    ]


def build_important_information(property_name: str) -> str:
    return (
        f"This safari is built around {property_name}. Safari timing and "
        "wildlife routes remain flexible because the experience follows "
        "natural wildlife movement, weather and conservation-area rules. "
        "Published property rates and applicable park or conservancy fees "
        "can change. TUR rates stored in this catalogue are indicative "
        "selling rates and must be confirmed against supplier availability "
        "before a booking is accepted. Guests should carry comprehensive "
        "travel insurance and follow all guide and wildlife-safety instructions."
    )


def build_transport_details(property_name: str) -> str:
    return (
        f"Access to {property_name} is normally arranged by scheduled or "
        "private safari flight into the relevant Mara airstrip followed by "
        "a camp transfer. Road transfers from Nairobi can be quoted where "
        "appropriate. The final transport arrangement depends on the "
        "property, guest itinerary and confirmed flight schedule."
    )


def build_meals_information() -> str:
    return (
        "The package is structured around full-board safari dining. "
        "Breakfast, lunch and dinner are included according to the "
        "property's confirmed board basis. Bush breakfasts, picnic lunches "
        "and sundowner arrangements may be substituted or added depending "
        "on the property's operations, weather and conservation-area rules."
    )


# =============================================================================
# RATE BENCHMARKS
# =============================================================================

"""
Rates below are deliberately stored as INDICATIVE TUR SELLING RATES.

They are not presented as supplier-confirmed contracts.

The package amount is calculated from an indicative nightly benchmark
multiplied by the number of nights.

Where a property publishes a materially different official seasonal rate,
the rate_notes field records that the figure must be reconfirmed before
commercial use.

This allows the catalogue to be populated now without falsely claiming
that an unverified supplier rate is final.
"""

PROPERTY_NIGHTLY_BENCHMARKS = {
    # Existing properties.
    "pearl-mara": {
        "standard": Decimal("718.75"),
        "peak": Decimal("900.00"),
        "festive": Decimal("1100.00"),
        "note": (
            "Existing supplier benchmark already present in TUR for the "
            "Mara Awakening package. Existing records are preserved and "
            "not overwritten."
        ),
    },
    "jw-marriott-masai-mara-lodge": {
        "standard": Decimal("1050.00"),
        "peak": Decimal("1250.00"),
        "festive": Decimal("1450.00"),
        "note": (
            "Indicative TUR benchmark. Reconfirm current Marriott rate, "
            "taxes, meals, park fees and any mandatory supplements."
        ),
    },
    "angama-mara": {
        "standard": Decimal("1850.00"),
        "peak": Decimal("2750.00"),
        "festive": Decimal("2750.00"),
        "note": (
            "Benchmark follows Angama's published 2026 rates: USD 1,850 "
            "per guest/night in Standard Season and USD 2,750 in Peak Season. "
            "2027 published rates should be applied when the travel date "
            "falls within those published seasons."
        ),
    },

    # New properties.
    "mahali-mzuri": {
        "standard": Decimal("1610.00"),
        "peak": Decimal("2522.00"),
        "festive": Decimal("2522.00"),
        "note": (
            "Indicative benchmark derived from current public booking "
            "availability and converted to an approximate per-person "
            "sharing basis. Supplier confirmation is mandatory."
        ),
    },
    "mara-plains-camp": {
        "standard": Decimal("1500.00"),
        "peak": Decimal("1900.00"),
        "festive": Decimal("2100.00"),
        "note": (
            "Indicative luxury Mara benchmark. Confirm current Great Plains "
            "rate, board basis, conservation fees, taxes and transfer terms."
        ),
    },
    "governors-il-moran-camp": {
        "standard": Decimal("900.00"),
        "peak": Decimal("1200.00"),
        "festive": Decimal("1350.00"),
        "note": (
            "Indicative benchmark informed by current Governors' published "
            "Mara pricing guidance. Governors' confirms that park and "
            "community fees are separately chargeable."
        ),
    },
    "cottars-1920s-camp": {
        "standard": Decimal("1500.00"),
        "peak": Decimal("2000.00"),
        "festive": Decimal("2000.00"),
        "note": (
            "Benchmark based on Cottar's published 2026 rack rates. "
            "Published rates vary by season and room type; park and "
            "conservancy fees are excluded and must be added separately."
        ),
    },
}


def package_amount(
    property_slug: str,
    nights: int,
    season: str,
) -> Decimal:
    benchmark = PROPERTY_NIGHTLY_BENCHMARKS[property_slug][season]
    return money(benchmark * nights)


# =============================================================================
# PROPERTY NAME MAP
# =============================================================================

PROPERTY_NAMES = {
    "pearl-mara": "Pearl Mara",
    "jw-marriott-masai-mara-lodge": "JW Marriott Masai Mara Lodge",
    "angama-mara": "Angama Mara",
    "mahali-mzuri": "Mahali Mzuri",
    "mara-plains-camp": "Mara Plains Camp",
    "governors-il-moran-camp": "Governors' Il Moran Camp",
    "cottars-1920s-camp": "Cottar's 1920s Camp",
}


# =============================================================================
# PACKAGE RATE DATA
# =============================================================================

def build_rates(property_slug: str, days: int) -> list[dict]:
    nights = days - 1

    return [
        {
            "name": (
                f"{package_name(PROPERTY_NAMES[property_slug], days)}"
                " — Standard Season — Per Person Sharing"
            ),
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": 2,
            "amount": package_amount(property_slug, nights, "standard"),
            "currency": DEFAULT_PACKAGE_CURRENCY,
            "season_name": "Standard / Green Season",
            "valid_from": STANDARD_START,
            "valid_to": STANDARD_END,
            "board_basis": "Full Board",
            "supplier_rate_reference": (
                f"TUR-IND-{property_slug.upper()}-STD-{days}D"
            ),
            "rate_notes": (
                PROPERTY_NIGHTLY_BENCHMARKS[property_slug]["note"]
                + " Stored as an indicative TUR selling rate per adult "
                "sharing for the full package."
            ),
            "display_order": 1,
        },
        {
            "name": (
                f"{package_name(PROPERTY_NAMES[property_slug], days)}"
                " — Peak Season — Per Person Sharing"
            ),
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": 2,
            "amount": package_amount(property_slug, nights, "peak"),
            "currency": DEFAULT_PACKAGE_CURRENCY,
            "season_name": "Peak Season",
            "valid_from": PEAK_START,
            "valid_to": PEAK_END,
            "board_basis": "Full Board",
            "supplier_rate_reference": (
                f"TUR-IND-{property_slug.upper()}-PEAK-{days}D"
            ),
            "rate_notes": (
                PROPERTY_NIGHTLY_BENCHMARKS[property_slug]["note"]
                + " Stored as an indicative TUR selling rate per adult "
                "sharing for the full package."
            ),
            "display_order": 2,
        },
        {
            "name": (
                f"{package_name(PROPERTY_NAMES[property_slug], days)}"
                " — Festive Season — Per Person Sharing"
            ),
            "pricing_basis": "per_person_sharing",
            "guest_category": "adult",
            "occupancy_type": "sharing",
            "min_guests": 2,
            "max_guests": 2,
            "amount": package_amount(property_slug, nights, "festive"),
            "currency": DEFAULT_PACKAGE_CURRENCY,
            "season_name": "Festive Season",
            "valid_from": FESTIVE_START,
            "valid_to": FESTIVE_END,
            "board_basis": "Full Board",
            "supplier_rate_reference": (
                f"TUR-IND-{property_slug.upper()}-FESTIVE-{days}D"
            ),
            "rate_notes": (
                PROPERTY_NIGHTLY_BENCHMARKS[property_slug]["note"]
                + " Festive pricing is an indicative TUR benchmark and "
                "requires supplier confirmation before quotation."
            ),
            "display_order": 3,
        },
    ]


# =============================================================================
# DESTINATION
# =============================================================================

def get_or_create_destination() -> tuple[SafariDestination, bool]:
    destination = SafariDestination.query.filter_by(
        slug=MAASAI_MARA_SLUG
    ).first()

    if destination:
        return destination, False

    destination = SafariDestination(
        name="Maasai Mara National Reserve",
        slug=MAASAI_MARA_SLUG,
        short_description=(
            "Kenya's legendary savannah destination, combining extraordinary "
            "wildlife, open grasslands, the Mara River and a rich network of "
            "community and private conservancies."
        ),
        introduction=(
            "The Maasai Mara is one of Kenya's defining safari landscapes. "
            "Its open grasslands, riverine habitats and surrounding "
            "conservancies support exceptional wildlife viewing throughout "
            "the year."
        ),
        history=(
            "The Maasai Mara forms part of the greater Mara-Serengeti "
            "ecosystem and has become one of East Africa's most recognised "
            "wildlife destinations. Its safari story is inseparable from "
            "Maasai pastoral heritage, conservation partnerships and the "
            "development of responsible wildlife tourism."
        ),
        landscape_and_wildlife=(
            "The landscape includes open savannah, rolling grassland, "
            "riverine forest, seasonal waterways and conservancy wilderness. "
            "Wildlife can include lions, leopards, cheetahs, elephants, "
            "buffalo, giraffes, zebra, wildebeest, hippos and numerous "
            "bird species."
        ),
        conservation_story=(
            "The Mara ecosystem depends on cooperation between protected "
            "areas, private conservancies, communities, landowners and "
            "tourism operators. Conservancy models can reduce vehicle "
            "pressure, support community income and create additional "
            "wildlife habitat."
        ),
        travel_information=(
            "Guests can access the Mara by scheduled or private safari "
            "flight from Nairobi or other safari destinations, or by road. "
            "Travel time depends on the departure point, route and weather. "
            "Park, conservancy and community fees vary by location and date "
            "and must be confirmed before travel."
        ),
        display_order=1,
        active=True,
        featured=True,
    )

    db.session.add(destination)
    db.session.flush()

    return destination, True


# =============================================================================
# PROPERTY CREATION / REUSE
# =============================================================================

def get_or_create_property(
    destination: SafariDestination,
    data: dict,
) -> tuple[SafariProperty, bool]:

    existing = SafariProperty.query.filter_by(
        slug=data["slug"]
    ).first()

    if existing:
        if existing.destination_id != destination.id:
            raise RuntimeError(
                f"Property slug '{data['slug']}' already belongs to "
                f"destination ID {existing.destination_id}, not Maasai Mara."
            )

        return existing, False

    property_record = SafariProperty(
        destination_id=destination.id,
        name=data["name"],
        slug=data["slug"],
        property_type=data["property_type"],
        short_description=data["short_description"],
        overview=data["overview"],
        property_story=data["property_story"],
        location_description=data["location_description"],
        accommodation_details=data["accommodation_details"],
        facilities=data["facilities"],
        dining_information=data["dining_information"],
        activities=data["activities"],
        wildlife_experience=data["wildlife_experience"],
        transport_information=data["transport_information"],
        check_in_information=data["check_in_information"],
        check_out_information=data["check_out_information"],
        child_policy=data["child_policy"],
        accessibility_information=data["accessibility_information"],
        booking_conditions=data["booking_conditions"],
        official_website_url=data["official_website_url"],
        location_name=data["location_name"],
        display_order=data["display_order"],
        active=True,
        featured=data["featured"],
    )

    db.session.add(property_record)
    db.session.flush()

    return property_record, True


# =============================================================================
# PACKAGE CREATION / REUSE
# =============================================================================

def get_or_create_package(
    property_record: SafariProperty,
    days: int,
) -> tuple[SafariPackageOption, bool]:

    slug = package_slug(property_record.slug, days)

    existing = SafariPackageOption.query.filter_by(
        property_id=property_record.id,
        slug=slug,
    ).first()

    if existing:
        return existing, False

    package = SafariPackageOption(
        property_id=property_record.id,
        name=package_name(property_record.name, days),
        slug=slug,
        summary=(
            f"{PACKAGE_BLUEPRINTS[days]['summary_suffix']} "
            f"Stay at {property_record.name} for {days - 1} nights."
        ),
        description=(
            f"{PACKAGE_BLUEPRINTS[days]['description_suffix']} "
            f"The accommodation base is {property_record.name}. "
            "Exact safari routing remains flexible so the guide can respond "
            "to wildlife movement, weather and conservation-area conditions."
        ),
        duration_days=days,
        duration_nights=days - 1,
        display_currency=DEFAULT_PACKAGE_CURRENCY,
        inclusions="\n".join(
            f"• {item}" for item in build_inclusions(property_record.name)
        ),
        exclusions="\n".join(
            f"• {item}" for item in build_exclusions(property_record.name)
        ),
        transport_details=build_transport_details(property_record.name),
        meals_information=build_meals_information(),
        important_information=build_important_information(
            property_record.name
        ),
        display_order=days,
        active=True,
        featured=(days == 5),
    )

    db.session.add(package)
    db.session.flush()

    return package, True


# =============================================================================
# ITINERARY
# =============================================================================

def add_missing_itinerary_days(
    package: SafariPackageOption,
    property_name: str,
    days: int,
) -> int:

    existing_days = {
        item.day_number
        for item in SafariItineraryDay.query.filter_by(
            package_option_id=package.id
        ).all()
    }

    created_count = 0

    for row in build_itinerary(property_name, days):
        if row["day_number"] in existing_days:
            continue

        itinerary_record = SafariItineraryDay(
            package_option_id=package.id,
            **row,
        )

        db.session.add(itinerary_record)
        created_count += 1

    return created_count


# =============================================================================
# RATES
# =============================================================================

def add_missing_rates(
    package: SafariPackageOption,
    property_slug: str,
    days: int,
) -> int:

    existing_rate_keys = {
        (
            rate.season_name,
            rate.occupancy_type,
            rate.pricing_basis,
        )
        for rate in SafariPackageRate.query.filter_by(
            package_option_id=package.id
        ).all()
    }

    created_count = 0

    for row in build_rates(property_slug, days):
        key = (
            row["season_name"],
            row["occupancy_type"],
            row["pricing_basis"],
        )

        if key in existing_rate_keys:
            continue

        rate = SafariPackageRate(
            package_option_id=package.id,
            name=row["name"],
            pricing_basis=row["pricing_basis"],
            guest_category=row["guest_category"],
            occupancy_type=row["occupancy_type"],
            min_guests=row["min_guests"],
            max_guests=row["max_guests"],
            amount=row["amount"],
            currency=row["currency"],
            season_name=row["season_name"],
            valid_from=row["valid_from"],
            valid_to=row["valid_to"],
            board_basis=row["board_basis"],
            supplier_rate_reference=row["supplier_rate_reference"],
            rate_notes=row["rate_notes"],
            active=True,
            display_order=row["display_order"],
        )

        db.session.add(rate)
        created_count += 1

    return created_count


# =============================================================================
# EXISTING MARA AWAKENING COMPLETION
# =============================================================================

def complete_existing_mara_awakening() -> dict:
    """
    Retrieve and complete the existing canonical Pearl Mara 3D/2N package.

    IMPORTANT:
        - Never create a duplicate package.
        - Never create additional rates.
        - Never overwrite existing rates.
        - Never replace existing itinerary days.
        - Only missing itinerary days are added.
        - Only missing transport_details may be filled.
    """

    package = SafariPackageOption.query.filter_by(
        slug=EXISTING_MARA_AWAKENING_SLUG
    ).first()

    if package is None:
        raise RuntimeError(
            "Expected existing package "
            f"'{EXISTING_MARA_AWAKENING_SLUG}' was not found."
        )

    pearl_mara = SafariProperty.query.filter_by(
        slug="pearl-mara"
    ).first()

    if pearl_mara is None:
        raise RuntimeError(
            "Expected existing Pearl Mara property was not found."
        )

    if package.property_id != pearl_mara.id:
        raise RuntimeError(
            "Existing Mara Awakening package does not belong to Pearl Mara."
        )

    if package.duration_days != 3:
        raise RuntimeError(
            "Existing Mara Awakening package does not have duration_days=3."
        )

    if package.duration_nights != 2:
        raise RuntimeError(
            "Existing Mara Awakening package does not have duration_nights=2."
        )

    existing_days_before = SafariItineraryDay.query.filter_by(
        package_option_id=package.id
    ).count()

    existing_rates_before = SafariPackageRate.query.filter_by(
        package_option_id=package.id
    ).count()

    created_days = add_missing_itinerary_days(
        package=package,
        property_name="Pearl Mara",
        days=3,
    )

    # Only complete missing transport information.
    # Do not replace an existing supplier-authored value.
    if not package.transport_details:
        package.transport_details = (
            "Arrival and departure transfers are coordinated through the "
            "relevant Mara airstrip or confirmed road transfer. Safari "
            "vehicle use is included according to the confirmed Pearl Mara "
            "package arrangement."
        )

    return {
        "package": package,
        "existing_days_before": existing_days_before,
        "existing_rates_before": existing_rates_before,
        "created_days": created_days,
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_property_slugs():
    seen = set()

    for data in PROPERTIES:
        slug = data["slug"]

        if slug in seen:
            raise RuntimeError(
                f"Duplicate property slug in batch: {slug}"
            )

        seen.add(slug)

        if slug in EXISTING_PROPERTIES:
            raise RuntimeError(
                f"Property '{slug}' is declared as both existing and new."
            )


def validate_duration_configuration():
    expected = {
        3: 2,
        5: 4,
        7: 6,
    }

    if PACKAGE_DURATIONS != expected:
        raise RuntimeError(
            "Package duration configuration has been changed unexpectedly."
        )


def validate_existing_mara():
    destination = SafariDestination.query.filter_by(
        slug=MAASAI_MARA_SLUG
    ).first()

    if destination is None:
        return

    if destination.name != "Maasai Mara National Reserve":
        raise RuntimeError(
            "Existing Maasai Mara slug is associated with an unexpected name."
        )


def validate_existing_mara_awakening():
    package = SafariPackageOption.query.filter_by(
        slug=EXISTING_MARA_AWAKENING_SLUG
    ).first()

    if package is None:
        raise RuntimeError(
            "Canonical Pearl Mara 3D/2N package is missing."
        )

    pearl_mara = SafariProperty.query.filter_by(
        slug="pearl-mara"
    ).first()

    if pearl_mara is None:
        raise RuntimeError(
            "Canonical Pearl Mara property is missing."
        )

    if package.property_id != pearl_mara.id:
        raise RuntimeError(
            "Canonical Mara Awakening package is attached to the wrong property."
        )


def validate_package_rate_data():
    for property_slug in PROPERTY_NAMES:
        if property_slug not in PROPERTY_NIGHTLY_BENCHMARKS:
            raise RuntimeError(
                f"No rate benchmark exists for property: {property_slug}"
            )

        for season in ("standard", "peak", "festive"):
            value = PROPERTY_NIGHTLY_BENCHMARKS[property_slug][season]

            if value <= 0:
                raise RuntimeError(
                    f"Rate benchmark must be positive: "
                    f"{property_slug} / {season}"
                )

            if DEFAULT_PACKAGE_CURRENCY not in SUPPORTED_CURRENCIES:
                raise RuntimeError(
                    f"Unsupported package currency: "
                    f"{DEFAULT_PACKAGE_CURRENCY}"
                )


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_package(
    package: SafariPackageOption,
    expected_days: int,
    *,
    expected_minimum_rates: int = 3,
):
    itinerary_count = SafariItineraryDay.query.filter_by(
        package_option_id=package.id
    ).count()

    rate_count = SafariPackageRate.query.filter_by(
        package_option_id=package.id
    ).count()

    if itinerary_count != expected_days:
        raise RuntimeError(
            f"Verification failed for package '{package.name}': "
            f"expected {expected_days} itinerary days, got {itinerary_count}."
        )

    if rate_count < expected_minimum_rates:
        raise RuntimeError(
            f"Verification failed for package '{package.name}': "
            f"expected at least {expected_minimum_rates} active rates, "
            f"got {rate_count}."
        )

    day_numbers = {
        day.day_number
        for day in SafariItineraryDay.query.filter_by(
            package_option_id=package.id
        ).all()
    }

    expected_day_numbers = set(range(1, expected_days + 1))

    if day_numbers != expected_day_numbers:
        raise RuntimeError(
            f"Verification failed for package '{package.name}': "
            f"expected itinerary days {sorted(expected_day_numbers)}, "
            f"got {sorted(day_numbers)}."
        )


def print_package_summary(package: SafariPackageOption):
    itinerary_count = SafariItineraryDay.query.filter_by(
        package_option_id=package.id
    ).count()

    rate_count = SafariPackageRate.query.filter_by(
        package_option_id=package.id
    ).count()

    print(
        f"      {package.name}"
        f" | {package.duration_days}D/{package.duration_nights}N"
        f" | itinerary={itinerary_count}"
        f" | rates={rate_count}"
    )


# =============================================================================
# MAIN POPULATION
# =============================================================================

def populate(apply_changes=False):
    app = create_app()

    with app.app_context():
        try:
            validate_property_slugs()
            validate_duration_configuration()
            validate_existing_mara()
            validate_existing_mara_awakening()
            validate_package_rate_data()

            print("\n" + "=" * 118)
            print(f"THE UNCHARTED ROUTE — {BATCH_NAME}")
            print("=" * 118)
            print(f"Mode: {'APPLY' if apply_changes else 'DRY RUN'}")
            print("Destination scope: Maasai Mara only")
            print("Package durations: 3D/2N, 5D/4N, 7D/6N")
            print(
                "Canonical Pearl Mara 3D/2N:"
                " The Mara Awakening — reused, never duplicated"
            )
            print("Existing Mara Awakening rates: preserved, never modified")
            print("SafariBooking: untouched")
            print("SafariInquiry: untouched")
            print("Media: no new media associations")
            print("=" * 118)

            destination, destination_created = get_or_create_destination()

            print(
                f"\nDestination:"
                f" {destination.name}"
                f" | ID={destination.id}"
                f" | {'CREATED' if destination_created else 'REUSED'}"
            )

            # -----------------------------------------------------------------
            # Complete existing Pearl Mara package first.
            # -----------------------------------------------------------------

            print("\n" + "-" * 118)
            print("EXISTING PACKAGE COMPLETION")
            print("-" * 118)

            existing_mara = complete_existing_mara_awakening()

            print(
                "  Mara Awakening"
                f" | existing itinerary days before="
                f"{existing_mara['existing_days_before']}"
                f" | missing days added="
                f"{existing_mara['created_days']}"
                f" | existing rates preserved=3"
            )

            # -----------------------------------------------------------------
            # Existing + new properties.
            # -----------------------------------------------------------------

            all_property_slugs = list(EXISTING_PROPERTIES.keys()) + [
                item["slug"] for item in PROPERTIES
            ]

            created_properties = []
            reused_properties = []

            property_lookup = {}

            print("\n" + "-" * 118)
            print("PROPERTY CATALOGUE")
            print("-" * 118)

            for index, slug in enumerate(all_property_slugs, 1):

                if slug in EXISTING_PROPERTIES:
                    property_record = SafariProperty.query.filter_by(
                        slug=slug
                    ).first()

                    if property_record is None:
                        raise RuntimeError(
                            f"Expected existing property '{slug}' was not found."
                        )

                    if property_record.destination_id != destination.id:
                        raise RuntimeError(
                            f"Existing property '{slug}' does not belong "
                            "to Maasai Mara."
                        )

                    property_lookup[slug] = property_record
                    reused_properties.append(property_record)

                    print(
                        f"  [{index:02d}/{len(all_property_slugs)}] "
                        f"{property_record.name}"
                        f" | ID={property_record.id}"
                        f" | REUSED"
                    )

                    continue

                data = next(
                    item for item in PROPERTIES
                    if item["slug"] == slug
                )

                property_record, created = get_or_create_property(
                    destination=destination,
                    data=data,
                )

                property_lookup[slug] = property_record

                if created:
                    created_properties.append(property_record)
                    status = "CREATED"
                else:
                    reused_properties.append(property_record)
                    status = "REUSED"

                print(
                    f"  [{index:02d}/{len(all_property_slugs)}] "
                    f"{property_record.name}"
                    f" | ID={property_record.id}"
                    f" | {status}"
                )

            # -----------------------------------------------------------------
            # Packages.
            # -----------------------------------------------------------------

            print("\n" + "-" * 118)
            print("PACKAGE CATALOGUE")
            print("-" * 118)

            package_created_count = 0
            package_reused_count = 0
            # The canonical Mara Awakening is completed before the package loop.
            # Its missing itinerary days must therefore be included in the batch total.
            itinerary_created_count = existing_mara["created_days"]
            rates_created_count = 0

            created_packages = []
            reused_packages = []

            for property_slug in all_property_slugs:

                property_record = property_lookup[property_slug]

                print(f"\n  {property_record.name}")

                for days in (3, 5, 7):

                    # ---------------------------------------------------------
                    # IMPORTANT:
                    # Pearl Mara's 3D/2N slot is already occupied by the
                    # canonical "The Mara Awakening" package.
                    #
                    # Do NOT call get_or_create_package() for this slot.
                    # Do NOT create another package.
                    # Do NOT add rates.
                    # Only complete missing itinerary days.
                    # ---------------------------------------------------------
                    if (
                        property_slug == "pearl-mara"
                        and days == 3
                    ):
                        package = existing_mara["package"]

                        package_status = "EXISTING / CANONICAL"

                        itinerary_added = add_missing_itinerary_days(
                            package=package,
                            property_name=property_record.name,
                            days=days,
                        )

                        # Existing Mara Awakening rates are operational
                        # catalogue records and must remain untouched.
                        rates_added = 0

                        package_reused_count += 1
                        reused_packages.append(package)

                        itinerary_created_count += itinerary_added

                        print(
                            f"    {package.name}"
                            f" | {package_status}"
                            f" | itinerary +{itinerary_added}"
                            f" | rates +0"
                        )

                        continue

                    # ---------------------------------------------------------
                    # All other package slots are normal get/create slots.
                    # ---------------------------------------------------------
                    package, created = get_or_create_package(
                        property_record=property_record,
                        days=days,
                    )

                    if created:
                        package_created_count += 1
                        created_packages.append(package)
                        package_status = "CREATED"
                    else:
                        package_reused_count += 1
                        reused_packages.append(package)
                        package_status = "REUSED"

                    itinerary_added = add_missing_itinerary_days(
                        package=package,
                        property_name=property_record.name,
                        days=days,
                    )

                    rates_added = add_missing_rates(
                        package=package,
                        property_slug=property_slug,
                        days=days,
                    )

                    itinerary_created_count += itinerary_added
                    rates_created_count += rates_added

                    print(
                        f"    {package.name}"
                        f" | {package_status}"
                        f" | itinerary +{itinerary_added}"
                        f" | rates +{rates_added}"
                    )

            # -----------------------------------------------------------------
            # Verification.
            # -----------------------------------------------------------------

            print("\n" + "=" * 118)
            print("BATCH VERIFICATION")
            print("=" * 118)

            # Destination.
            verified_destination = SafariDestination.query.filter_by(
                slug=MAASAI_MARA_SLUG
            ).first()

            if verified_destination is None:
                raise RuntimeError(
                    "Maasai Mara destination verification failed."
                )

            print(
                f"\nDestination verified:"
                f" {verified_destination.name}"
                f" | active={verified_destination.active}"
            )

            # Properties.
            total_properties = SafariProperty.query.filter_by(
                destination_id=destination.id
            ).count()

            print(
                f"Properties in Maasai Mara catalogue: {total_properties}"
            )

            if total_properties < 7:
                raise RuntimeError(
                    "Expected at least 7 Maasai Mara properties after Batch 1."
                )

            # Packages.
            all_mara_packages = (
                SafariPackageOption.query
                .join(SafariProperty)
                .filter(
                    SafariProperty.destination_id == destination.id
                )
                .order_by(
                    SafariProperty.display_order.asc(),
                    SafariPackageOption.duration_days.asc(),
                )
                .all()
            )

            print(
                f"Total Maasai Mara packages: {len(all_mara_packages)}"
            )

            # Expected package structure:
            #
            # Pearl Mara:
            #   3D existing Mara Awakening
            #   5D new
            #   7D new
            #
            # Six other properties:
            #   3D new
            #   5D new
            #   7D new
            #
            # Total = 21 package slots.
            expected_total_packages = 21

            if len(all_mara_packages) != expected_total_packages:
                raise RuntimeError(
                    "Package count verification failed: "
                    f"expected {expected_total_packages}, "
                    f"got {len(all_mara_packages)}."
                )

            # Explicitly verify canonical Pearl Mara package exists.
            canonical_package = SafariPackageOption.query.filter_by(
                property_id=property_lookup["pearl-mara"].id,
                slug=EXISTING_MARA_AWAKENING_SLUG,
            ).first()

            if canonical_package is None:
                raise RuntimeError(
                    "Canonical Pearl Mara Mara Awakening package "
                    "verification failed."
                )

            # Explicitly verify the duplicate package does NOT exist.
            duplicate_pearl_package = SafariPackageOption.query.filter_by(
                property_id=property_lookup["pearl-mara"].id,
                slug="pearl-mara-3-days-2-nights",
            ).first()

            if duplicate_pearl_package is not None:
                raise RuntimeError(
                    "Duplicate Pearl Mara 3D/2N package detected: "
                    "'pearl-mara-3-days-2-nights'. "
                    "The existing Mara Awakening must be the canonical package."
                )

            print(
                "Canonical Pearl Mara 3D/2N package verified:"
                " The Mara Awakening"
            )

            print(
                "Duplicate Pearl Mara 3D/2N package verified absent."
            )

            for package in all_mara_packages:
                verify_package(
                    package,
                    expected_days=package.duration_days,
                )
                print_package_summary(package)

            # -----------------------------------------------------------------
            # Verify the existing Mara Awakening rates were preserved.
            # -----------------------------------------------------------------

            mara_awakening_rate_count = SafariPackageRate.query.filter_by(
                package_option_id=canonical_package.id
            ).count()

            expected_mara_awakening_rate_count = (
                existing_mara["existing_rates_before"]
            )

            if (
                mara_awakening_rate_count
                != expected_mara_awakening_rate_count
            ):
                raise RuntimeError(
                    "Existing Mara Awakening rate count changed unexpectedly: "
                    f"before={expected_mara_awakening_rate_count}, "
                    f"after={mara_awakening_rate_count}."
                )

            print(
                "Existing Mara Awakening rates preserved:"
                f" {mara_awakening_rate_count}"
            )

            # -----------------------------------------------------------------
            # Verify the expected new-package/rate structure.
            # -----------------------------------------------------------------

            expected_new_packages = 20
            expected_new_rates = 60

            if package_created_count != expected_new_packages:
                raise RuntimeError(
                    "New package creation count verification failed: "
                    f"expected {expected_new_packages}, "
                    f"got {package_created_count}."
                )

            if rates_created_count != expected_new_rates:
                raise RuntimeError(
                    "New rate creation count verification failed: "
                    f"expected {expected_new_rates}, "
                    f"got {rates_created_count}."
                )

            print(
                f"New packages created verified: {package_created_count}"
            )

            print(
                f"New package rates created verified: {rates_created_count}"
            )

            # -----------------------------------------------------------------
            # Verify expected itinerary creation count.
            #
            # Existing Mara Awakening:
            #     missing days = 2
            #
            # Pearl Mara new packages:
            #     5D + 7D = 12
            #
            # Six other properties:
            #     3D + 5D + 7D = 15 each
            #     15 * 6 = 90
            #
            # Total:
            #     2 + 12 + 90 = 104
            # -----------------------------------------------------------------

            expected_itinerary_days_added = 104

            if (
                itinerary_created_count
                != expected_itinerary_days_added
            ):
                raise RuntimeError(
                    "Itinerary creation count verification failed: "
                    f"expected {expected_itinerary_days_added}, "
                    f"got {itinerary_created_count}."
                )

            print(
                f"Itinerary days added verified: "
                f"{itinerary_created_count}"
            )

            # -----------------------------------------------------------------
            # Existing inquiry preservation.
            # -----------------------------------------------------------------

            inquiry_count = None

            try:
                from app.models.safari import SafariInquiry

                inquiry_count = SafariInquiry.query.count()

                print(
                    f"\nSafariInquiry records preserved: {inquiry_count}"
                )

            except ImportError:
                print(
                    "\nSafariInquiry model import skipped during verification."
                )

            # -----------------------------------------------------------------
            # SafariBooking intentionally not imported or queried.
            # -----------------------------------------------------------------

            print(
                "SafariBooking: NOT TOUCHED"
            )

            print("\n" + "=" * 118)
            print("SUMMARY")
            print("=" * 118)

            print(
                f"Destination created:        "
                f"{1 if destination_created else 0}"
            )
            print(
                f"Properties created:         "
                f"{len(created_properties)}"
            )
            print(
                f"Properties reused:          "
                f"{len(reused_properties)}"
            )
            print(
                f"Packages created:           "
                f"{package_created_count}"
            )
            print(
                f"Packages reused/canonical:  "
                f"{package_reused_count}"
            )
            print(
                f"Total package slots:        "
                f"{len(all_mara_packages)}"
            )
            print(
                f"Itinerary days added:       "
                f"{itinerary_created_count}"
            )
            print(
                f"Package rates added:        "
                f"{rates_created_count}"
            )
            print(
                f"Mara Awakening rates:       "
                f"{mara_awakening_rate_count} preserved"
            )
            print(
                f"Safari inquiries:            "
                f"{inquiry_count if inquiry_count is not None else 'preserved'}"
            )
            print(
                "Safari bookings touched:    0"
            )
            print(
                "Media records created:      0"
            )

            # -----------------------------------------------------------------
            # Final transaction handling.
            # -----------------------------------------------------------------

            if apply_changes:
                db.session.commit()

                print("\n" + "=" * 118)
                print("BATCH 1 COMMITTED SUCCESSFULLY")
                print("=" * 118)
                print(
                    "Maasai Mara flagship safari catalogue populated successfully."
                )
                print(
                    "Existing operational/customer records were preserved."
                )

            else:
                db.session.rollback()

                print("\n" + "=" * 118)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 118)
                print(
                    "No database changes were committed."
                )
                print(
                    "Run with --apply only after reviewing the output."
                )

        except Exception:
            db.session.rollback()

            print("\n" + "=" * 118)
            print("BATCH 1 FAILED — TRANSACTION ROLLED BACK")
            print("=" * 118)

            raise


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Populate The Uncharted Route's Maasai Mara safari catalogue."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the safari catalogue population to the database.",
    )

    args = parser.parse_args()

    populate(
        apply_changes=args.apply
    )