"""
THE UNCHARTED ROUTE
BATCH 3 — AMBOSELI SAFARI CATALOGUE

Scope:
    - Amboseli National Park / Amboseli ecosystem only
    - 5 carefully selected properties
    - 3 package durations per property:
        * 3 Days / 2 Nights
        * 5 Days / 4 Nights
        * 7 Days / 6 Nights

Population principles:
    - Dry run by default
    - --apply commits
    - Existing matching records are reused
    - Existing package rates are preserved
    - Missing itinerary days are completed
    - No SafariBooking records are touched
    - No SafariInquiry records are created or modified
    - No media associations are created
    - One transaction with rollback on failure
    - No duplicate package slots
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
from app.models import (
    SafariDestination,
    SafariProperty,
    SafariPackageOption,
    SafariItineraryDay,
    SafariPackageRate,
    SafariInquiry,
)

# ======================================================================================================================
# CONFIGURATION
# ======================================================================================================================

BATCH_NAME = "BATCH 3 — AMBOSELI SAFARI CATALOGUE"

DESTINATION_NAME = "Amboseli National Park"
DESTINATION_SLUG = "amboseli"

DEFAULT_CURRENCY = "USD"

PACKAGE_DURATIONS = [
    (3, 2),
    (5, 4),
    (7, 6),
]

DEFAULT_DISPLAY_ORDER = 1

# These are TUR planning/selling benchmarks, not supplier-contract rates.
# Supplier confirmation is required before issuing a final traveller quotation.
PROPERTY_RATE_BENCHMARKS = {
    "elewana-tortilis-camp": {
        "standard": Decimal("950.00"),
        "peak": Decimal("1250.00"),
        "festive": Decimal("1450.00"),
    },
    "tawi-lodge": {
        "standard": Decimal("850.00"),
        "peak": Decimal("1100.00"),
        "festive": Decimal("1300.00"),
    },
    "angama-amboseli": {
        "standard": Decimal("1250.00"),
        "peak": Decimal("1650.00"),
        "festive": Decimal("1900.00"),
    },
    "amboseli-serena-safari-lodge": {
        "standard": Decimal("550.00"),
        "peak": Decimal("700.00"),
        "festive": Decimal("825.00"),
    },
    "ol-tukai-lodge": {
        "standard": Decimal("600.00"),
        "peak": Decimal("775.00"),
        "festive": Decimal("900.00"),
    },
}

SEASONS = [
    {
        "name": "Standard Season",
        "key": "standard",
        "valid_from": date(2026, 11, 5),
        "valid_to": date(2027, 6, 30),
    },
    {
        "name": "Peak Season",
        "key": "peak",
        "valid_from": date(2027, 7, 1),
        "valid_to": date(2027, 10, 31),
    },
    {
        "name": "Festive Season",
        "key": "festive",
        "valid_from": date(2027, 12, 20),
        "valid_to": date(2028, 1, 10),
    },
]


# ======================================================================================================================
# PROPERTY CATALOGUE
# ======================================================================================================================

PROPERTIES = [
    {
        "name": "Elewana Tortilis Camp",
        "slug": "elewana-tortilis-camp",
        "property_type": "tented_camp",
        "short_description": (
            "An elegant Amboseli tented camp with classic Kilimanjaro views, "
            "strong conservation credentials and a refined safari atmosphere."
        ),
        "overview": (
            "Elewana Tortilis Camp is one of Amboseli's established luxury safari camps, "
            "positioned within the Amboseli ecosystem with a strong emphasis on wildlife, "
            "landscape and responsible tourism. The camp is particularly compelling for "
            "travellers seeking classic safari character, intimate accommodation and "
            "uninterrupted views toward Mount Kilimanjaro when conditions are clear."
        ),
        "property_story": (
            "Tortilis is closely associated with the conservation-led safari tradition of "
            "the Amboseli ecosystem. Its location allows guests to experience the park's "
            "elephant-rich landscapes while also connecting the safari experience with "
            "the wider community and conservation environment surrounding Amboseli."
        ),
        "location_description": (
            "Located in the Amboseli ecosystem with access to Amboseli National Park and "
            "the surrounding wildlife conservancies."
        ),
        "accommodation_details": (
            "Luxury canvas tents with private verandas, en-suite facilities and a strong "
            "connection to the surrounding landscape. Accommodation is designed to feel "
            "immersive while retaining the comforts expected of an upscale safari camp."
        ),
        "facilities": (
            "Swimming pool, dining area, lounge, bar, private verandas, safari vehicle "
            "operations and camp-based guest services."
        ),
        "dining_information": (
            "Full-board safari dining with breakfast, lunch and dinner, with selected "
            "meals and drinks arranged around game-drive schedules."
        ),
        "activities": (
            "Game drives, guided nature experiences, birding, cultural experiences, "
            "conservation-focused activities and time around camp."
        ),
        "wildlife_experience": (
            "Excellent access to Amboseli's elephant population, with opportunities to "
            "encounter lions, cheetahs, buffalo, giraffes, zebras, wildebeest, hippos "
            "and a wide variety of plains and wetland birdlife."
        ),
        "transport_information": (
            "Accessible by road from Nairobi and by scheduled or chartered safari flight "
            "depending on the traveller's itinerary. Transfers should be coordinated "
            "with game-drive timing and park access requirements."
        ),
        "check_in_information": (
            "Check-in is coordinated around arrival transfers and safari schedules. "
            "Early arrival may be accommodated subject to camp operations."
        ),
        "check_out_information": (
            "Check-out is normally coordinated with the final game drive and onward "
            "transfer or flight."
        ),
        "child_policy": (
            "Families may be accommodated subject to current camp age policies, room "
            "configuration and availability. Child rates and activities should be "
            "confirmed before booking."
        ),
        "accessibility_information": (
            "Guests requiring mobility assistance should advise TUR before confirmation "
            "so accommodation and vehicle arrangements can be checked."
        ),
        "booking_conditions": (
            "Rates are indicative planning benchmarks and remain subject to supplier "
            "confirmation, seasonal availability, applicable park fees and final "
            "traveller requirements."
        ),
        "official_website_url": "https://www.elewanacollection.com/tortilis-camp",
        "location_name": "Amboseli ecosystem, Kenya",
        "display_order": 1,
        "featured": True,
    },
    {
        "name": "Tawi Lodge",
        "slug": "tawi-lodge",
        "property_type": "lodge",
        "short_description": (
            "A secluded Amboseli lodge combining private conservancy access, "
            "comfortable accommodation and sweeping views toward Mount Kilimanjaro."
        ),
        "overview": (
            "Tawi Lodge offers a quieter Amboseli experience from a private conservancy "
            "setting, complementing game drives in the national park with a more exclusive "
            "conservancy environment. It is particularly suited to travellers who value "
            "space, privacy and a slower safari rhythm."
        ),
        "property_story": (
            "Tawi's appeal lies in combining the wildlife of the Amboseli region with "
            "the advantages of a conservancy setting. The experience can therefore "
            "extend beyond conventional park game drives into a more flexible and "
            "private safari environment."
        ),
        "location_description": (
            "Situated within the Amboseli ecosystem on a private conservancy near "
            "Amboseli National Park."
        ),
        "accommodation_details": (
            "Spacious private cottages with en-suite bathrooms, private outdoor areas "
            "and views across the surrounding landscape."
        ),
        "facilities": (
            "Swimming pool, dining facilities, lounge, bar, outdoor spaces, safari "
            "vehicle operations and guest activity areas."
        ),
        "dining_information": (
            "Full-board safari meals with menus designed around daily game-drive "
            "schedules and lodge operations."
        ),
        "activities": (
            "Game drives, conservancy drives, guided walks where permitted, cultural "
            "experiences, birding, sundowners and relaxation at the lodge."
        ),
        "wildlife_experience": (
            "Strong opportunities for elephants, lions, buffalo, giraffes, zebras, "
            "wildebeest, antelope and birdlife, with the conservancy setting providing "
            "additional flexibility for safari activities."
        ),
        "transport_information": (
            "Road access from Nairobi and safari-flight connections can be arranged "
            "subject to the final itinerary."
        ),
        "check_in_information": (
            "Arrival is coordinated around lodge operations and safari transfers."
        ),
        "check_out_information": (
            "Departure is coordinated with the final morning activity and onward transfer."
        ),
        "child_policy": (
            "Families can be considered subject to current lodge policy, accommodation "
            "configuration and activity restrictions."
        ),
        "accessibility_information": (
            "Accessibility requirements should be shared before confirmation so the lodge "
            "can advise on accommodation and vehicle suitability."
        ),
        "booking_conditions": (
            "Indicative TUR benchmark only. Final rates, availability, park fees and "
            "supplier conditions must be confirmed before booking."
        ),
        "official_website_url": "https://www.tawilodge.com/",
        "location_name": "Amboseli ecosystem, Kenya",
        "display_order": 2,
        "featured": True,
    },
    {
        "name": "Angama Amboseli",
        "slug": "angama-amboseli",
        "property_type": "lodge",
        "short_description": (
            "A contemporary luxury safari retreat in the Amboseli ecosystem, designed "
            "around dramatic landscapes, elephants and exceptional views."
        ),
        "overview": (
            "Angama Amboseli brings a contemporary luxury approach to the Amboseli "
            "ecosystem, pairing high-end accommodation with an immersive relationship "
            "to the landscape. It is designed for travellers looking for a premium "
            "safari stay with strong attention to design, service and sense of place."
        ),
        "property_story": (
            "The property extends Angama's philosophy of combining distinctive design "
            "with meaningful safari experiences. Amboseli's open plains, elephant "
            "herds and Kilimanjaro backdrop form the central visual character of the stay."
        ),
        "location_description": (
            "Located within the greater Amboseli ecosystem, positioned for access to "
            "the area's wildlife and landscape experiences."
        ),
        "accommodation_details": (
            "High-end private accommodation designed for privacy, comfort and expansive "
            "views of the surrounding Amboseli landscape."
        ),
        "facilities": (
            "Luxury dining, guest lounge areas, swimming facilities, curated guest "
            "experiences and safari operations."
        ),
        "dining_information": (
            "Premium full-board dining with meals tailored to daily safari schedules "
            "and guest preferences."
        ),
        "activities": (
            "Game drives, guided experiences, conservation activities, cultural "
            "experiences, birding, scenic outings and curated sundowners."
        ),
        "wildlife_experience": (
            "Amboseli is renowned for elephants, while the wider ecosystem supports "
            "lions, cheetahs, buffalo, giraffes, zebras, wildebeest, antelope and "
            "rich birdlife."
        ),
        "transport_information": (
            "Accessible by safari flight or road transfer depending on the itinerary. "
            "TUR should coordinate the arrival method with the property's operating "
            "schedule."
        ),
        "check_in_information": (
            "Check-in is coordinated with the guest's arrival transfer and lodge team."
        ),
        "check_out_information": (
            "Departure timing is coordinated around the final safari activity and onward "
            "transport."
        ),
        "child_policy": (
            "Family suitability depends on current property policy and accommodation "
            "availability. Child arrangements must be confirmed at quotation stage."
        ),
        "accessibility_information": (
            "Guests with accessibility requirements should notify TUR before confirmation "
            "so property-specific arrangements can be checked."
        ),
        "booking_conditions": (
            "Indicative planning benchmark only. Supplier rates, availability, park "
            "charges and final inclusions require confirmation."
        ),
        "official_website_url": "https://angama.com/stay/angama-amboseli/",
        "location_name": "Amboseli ecosystem, Kenya",
        "display_order": 3,
        "featured": True,
    },
    {
        "name": "Amboseli Serena Safari Lodge",
        "slug": "amboseli-serena-safari-lodge",
        "property_type": "lodge",
        "short_description": (
            "A classic full-service safari lodge offering convenient access to Amboseli "
            "National Park and its famous elephant-filled plains."
        ),
        "overview": (
            "Amboseli Serena Safari Lodge is a well-established safari lodge designed "
            "around the classic Amboseli experience. Its location makes it a practical "
            "choice for travellers seeking strong park access, dependable safari "
            "infrastructure and a comfortable lodge environment."
        ),
        "property_story": (
            "The lodge reflects the long-standing safari tradition of Amboseli, where "
            "the combination of elephants, open plains, wetlands and Mount Kilimanjaro "
            "creates one of Kenya's most recognizable safari landscapes."
        ),
        "location_description": (
            "Within the Amboseli National Park area, providing convenient access to "
            "the park's principal wildlife zones."
        ),
        "accommodation_details": (
            "Comfortable safari rooms with en-suite facilities and views toward the "
            "surrounding park landscape."
        ),
        "facilities": (
            "Swimming pool, restaurant, bar, lounge, gardens, guest activity areas "
            "and safari vehicle services."
        ),
        "dining_information": (
            "Full-board dining with breakfast, lunch and dinner arranged around safari "
            "activities."
        ),
        "activities": (
            "Game drives, guided nature experiences, birding, cultural experiences "
            "and lodge-based relaxation."
        ),
        "wildlife_experience": (
            "Particularly strong for elephant encounters, with opportunities to see "
            "lions, buffalo, giraffes, zebras, wildebeest, hippos and numerous birds."
        ),
        "transport_information": (
            "Road transfers from Nairobi and safari-flight connections are possible "
            "subject to itinerary design."
        ),
        "check_in_information": (
            "Check-in is coordinated with arrival timing and lodge operations."
        ),
        "check_out_information": (
            "Check-out normally follows the final morning safari activity and onward "
            "transfer schedule."
        ),
        "child_policy": (
            "Family stays are possible subject to current Serena policy, room "
            "configuration and applicable child rates."
        ),
        "accessibility_information": (
            "Accessibility requirements should be communicated in advance for "
            "appropriate room and transfer planning."
        ),
        "booking_conditions": (
            "Indicative TUR benchmark only. Final rates and availability require "
            "confirmation from the property or supplier."
        ),
        "official_website_url": "https://www.serenahotels.com/amboseli",
        "location_name": "Amboseli National Park, Kenya",
        "display_order": 4,
        "featured": False,
    },
    {
        "name": "Ol Tukai Lodge",
        "slug": "ol-tukai-lodge",
        "property_type": "lodge",
        "short_description": (
            "A classic Amboseli lodge set amid the park's iconic elephant country, "
            "with strong access to wetlands, plains and Kilimanjaro views."
        ),
        "overview": (
            "Ol Tukai Lodge is positioned within the heart of the Amboseli experience, "
            "making it particularly attractive to travellers prioritising wildlife "
            "access and the classic park landscape. The lodge is especially associated "
            "with elephant encounters and views toward Mount Kilimanjaro."
        ),
        "property_story": (
            "Ol Tukai has long been part of the Amboseli safari landscape. Its setting "
            "puts guests close to the park's wetlands and open plains, where wildlife "
            "concentrations can be especially rewarding during favourable conditions."
        ),
        "location_description": (
            "Located inside Amboseli National Park near the park's central wildlife "
            "areas and seasonal wetlands."
        ),
        "accommodation_details": (
            "Comfortable lodge rooms and cottages with private facilities and views "
            "toward the surrounding park environment."
        ),
        "facilities": (
            "Swimming pool, restaurant, bar, lounge, gardens, guest recreation areas "
            "and safari operations."
        ),
        "dining_information": (
            "Full-board meals including breakfast, lunch and dinner, coordinated around "
            "daily game drives."
        ),
        "activities": (
            "Game drives, birding, nature experiences, cultural activities where "
            "available and relaxation around the lodge."
        ),
        "wildlife_experience": (
            "Excellent potential for elephants, with additional sightings of lions, "
            "buffalo, giraffes, zebras, wildebeest, hippos, antelope and abundant birds."
        ),
        "transport_information": (
            "Accessible by road from Nairobi and by safari aircraft depending on the "
            "selected itinerary and operating schedules."
        ),
        "check_in_information": (
            "Arrival is coordinated around park entry, transfer and lodge check-in "
            "procedures."
        ),
        "check_out_information": (
            "Departure is normally planned after the final morning safari activity."
        ),
        "child_policy": (
            "Families may be accommodated subject to current lodge policy, room "
            "availability and applicable child arrangements."
        ),
        "accessibility_information": (
            "Guests requiring accessibility assistance should notify TUR before booking "
            "so suitable arrangements can be checked."
        ),
        "booking_conditions": (
            "Indicative planning benchmark only. Final supplier pricing, park fees, "
            "availability and booking conditions must be confirmed."
        ),
        "official_website_url": "https://oltukailodge.com/",
        "location_name": "Amboseli National Park, Kenya",
        "display_order": 5,
        "featured": False,
    },
]


# ======================================================================================================================
# PACKAGE CONTENT
# ======================================================================================================================

PROPERTY_STYLE = {
    "elewana-tortilis-camp": "luxury tented-camp safari",
    "tawi-lodge": "private-conservancy safari",
    "angama-amboseli": "contemporary luxury safari",
    "amboseli-serena-safari-lodge": "classic full-service lodge safari",
    "ol-tukai-lodge": "classic park-based safari",
}


def build_package_content(
    property_data: Dict,
    duration_days: int,
    duration_nights: int,
) -> Dict:
    name = property_data["name"]
    slug = property_data["slug"]
    style = PROPERTY_STYLE[slug]

    summary = (
        f"{duration_days} days / {duration_nights} nights of {style} in Amboseli, "
        f"combining game drives, elephant country, the Amboseli plains and opportunities "
        f"for clear-weather views of Mount Kilimanjaro."
    )

    description = (
        f"This {duration_days}-day Amboseli safari is designed around the character of "
        f"{name}. The journey balances structured game drives with time to experience "
        f"the wider Amboseli ecosystem at a comfortable pace. Guests can explore the "
        f"park's open plains and wetlands, look for the region's famous elephants and "
        f"other wildlife, and enjoy the changing light around Mount Kilimanjaro. "
        f"The itinerary is intentionally flexible because wildlife movement, road "
        f"conditions and weather can influence daily safari timing."
    )

    inclusions = (
        "Accommodation for the stated number of nights; full-board meals unless otherwise "
        "specified; scheduled safari activities described in the itinerary; professional "
        "English-speaking safari guide/driver; private or shared safari vehicle according "
        "to the confirmed quotation; applicable standard safari logistics; park access "
        "planning and TUR trip coordination."
    )

    exclusions = (
        "International flights; domestic flights unless specifically included; visa "
        "costs; travel insurance; personal purchases; alcoholic and premium beverages; "
        "gratuities; laundry; additional activities not listed; conservation or park "
        "fees introduced or changed after quotation; private vehicle supplements unless "
        "included in the confirmed rate; medical and evacuation costs."
    )

    transport_details = (
        "Road transfer from Nairobi or safari-flight connections may be arranged. "
        "Game drives are conducted in a safari vehicle suitable for the Amboseli terrain. "
        "Exact transfer routing depends on the guest's wider Kenya itinerary."
    )

    meals_information = (
        "Full board is planned throughout the safari, normally covering breakfast, "
        "lunch and dinner. Meal timing may shift around early-morning and afternoon "
        "game drives."
    )

    important_information = (
        "Wildlife sightings are never guaranteed. Amboseli's landscape is highly "
        "seasonal, and visibility of Mount Kilimanjaro depends on weather and cloud "
        "conditions. Park rules, conservation fees and operating conditions may change. "
        "Guests should carry suitable sun protection, comfortable walking shoes, "
        "light layers, binoculars where available and a reusable water bottle."
    )

    return {
        "summary": summary,
        "description": description,
        "inclusions": inclusions,
        "exclusions": exclusions,
        "transport_details": transport_details,
        "meals_information": meals_information,
        "important_information": important_information,
    }


def build_itinerary(
    property_data: Dict,
    duration_days: int,
) -> List[Dict]:
    property_name = property_data["name"]

    days = [
        {
            "day_number": 1,
            "title": "Into Amboseli — Arrival & First Game Drive",
            "description": (
                f"Arrive in the Amboseli ecosystem and settle into {property_name}. "
                "After lunch and a safari briefing, head out for the first game drive "
                "across the park or surrounding wildlife area. The first afternoon is "
                "about becoming familiar with the landscape, elephant country and the "
                "rhythm of an Amboseli safari."
            ),
            "morning_activities": (
                "Travel from Nairobi or arrive by safari flight, depending on the "
                "confirmed itinerary."
            ),
            "afternoon_activities": (
                "Check in, lunch and an introductory afternoon game drive."
            ),
            "evening_activities": (
                "Return to camp or lodge, sundowner where conditions permit, dinner "
                "and safari briefing."
            ),
            "meals_included": "Lunch, Dinner",
            "overnight_location": property_name,
            "transport_details": (
                "Road transfer or safari flight arrival followed by safari vehicle "
                "transfer."
            ),
            "notes": (
                "Kilimanjaro views are weather dependent. Wildlife sightings are not "
                "guaranteed."
            ),
        },
        {
            "day_number": 2,
            "title": "Elephant Country — Full-Day Amboseli Safari",
            "description": (
                "Rise early for a full safari day focused on Amboseli's wildlife-rich "
                "plains and wetlands. The ecosystem is particularly famous for elephants, "
                "while the same habitats support lions, buffalo, giraffes, zebras, "
                "wildebeest and numerous bird species."
            ),
            "morning_activities": (
                "Early breakfast followed by an extended morning game drive through "
                "the park."
            ),
            "afternoon_activities": (
                "Picnic lunch or lodge lunch depending on the day's route, followed "
                "by continued wildlife exploration."
            ),
            "evening_activities": (
                "Return to the property, sundowner where appropriate, dinner and rest."
            ),
            "meals_included": "Breakfast, Lunch, Dinner",
            "overnight_location": property_name,
            "transport_details": "Full-day safari vehicle operations.",
            "notes": (
                "The route may change according to wildlife movement, road conditions "
                "and park guidance."
            ),
        },
        {
            "day_number": 3,
            "title": "Kilimanjaro Plains — Final Safari & Departure",
            "description": (
                "Enjoy a final early-morning safari when wildlife is often active and "
                "the light is especially rewarding. After breakfast, return for departure "
                "preparations and begin the onward journey."
            ),
            "morning_activities": (
                "Early game drive followed by breakfast and check-out."
            ),
            "afternoon_activities": (
                "Depart Amboseli by road or safari flight according to the confirmed "
                "travel plan."
            ),
            "evening_activities": (
                "Onward travel or arrival at the next destination."
            ),
            "meals_included": "Breakfast, Lunch",
            "overnight_location": "Onward destination",
            "transport_details": (
                "Safari vehicle transfer to the airstrip or road transfer onward."
            ),
            "notes": "Departure timing depends on the selected onward connection.",
        },
    ]

    if duration_days >= 5:
        days.insert(
            2,
            {
                "day_number": 3,
                "title": "Amboseli Beyond the Main Circuit",
                "description": (
                    "Continue exploring the Amboseli ecosystem at a slower pace. "
                    "Depending on the property's location and operating area, today's "
                    "safari can combine wildlife viewing with a broader look at the "
                    "landscape, birdlife and seasonal wetland habitats."
                ),
                "morning_activities": (
                    "Early breakfast and morning game drive focusing on elephant herds "
                    "and active wildlife."
                ),
                "afternoon_activities": (
                    "Lunch followed by a second safari outing or conservancy experience "
                    "where available."
                ),
                "evening_activities": (
                    "Return for relaxation, sundowner and dinner."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle operations.",
                "notes": (
                    "Activities outside the national park depend on the property's "
                    "location and current operating arrangements."
                ),
            },
        )

        days.insert(
            3,
            {
                "day_number": 4,
                "title": "Wildlife & Landscape — A Deeper Amboseli Day",
                "description": (
                    "Use another full day to explore different sectors of the ecosystem. "
                    "The goal is not to repeat a fixed route but to respond to wildlife "
                    "movement, seasonal water availability and guide observations."
                ),
                "morning_activities": (
                    "Early morning game drive with emphasis on predators, elephants "
                    "and plains wildlife."
                ),
                "afternoon_activities": (
                    "Lunch followed by an afternoon safari, birding or property-based "
                    "experience."
                ),
                "evening_activities": (
                    "Sundowner where conditions permit, dinner and overnight at the property."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle operations.",
                "notes": (
                    "Safari routes are adapted to conditions rather than guaranteed "
                    "to follow a fixed sequence."
                ),
            },
        )

        # Renumber the departure day.
        for index, day in enumerate(days, start=1):
            day["day_number"] = index

    if duration_days >= 7:
        days.insert(
            4,
            {
                "day_number": 5,
                "title": "Conservation, Community & Wildlife",
                "description": (
                    "A more immersive day combining wildlife viewing with the broader "
                    "conservation and community story of the Amboseli ecosystem. "
                    "Where available and appropriate, guests may experience a responsible "
                    "cultural or conservation activity arranged through the property."
                ),
                "morning_activities": (
                    "Morning game drive followed by a conservation or community-focused "
                    "experience where available."
                ),
                "afternoon_activities": (
                    "Lunch and afternoon wildlife exploration."
                ),
                "evening_activities": (
                    "Return to camp, sundowner and dinner."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Safari vehicle and locally arranged activity transfer.",
                "notes": (
                    "Cultural activities should be conducted through responsible, "
                    "community-benefiting arrangements."
                ),
            },
        )

        days.insert(
            5,
            {
                "day_number": 6,
                "title": "The Amboseli Finale — Final Full Safari",
                "description": (
                    "Spend a final full day following the safari rhythm: early wildlife "
                    "viewing, a relaxed midday break and an afternoon drive. This is an "
                    "opportunity to revisit productive areas while allowing the guide "
                    "to respond to current wildlife movement."
                ),
                "morning_activities": (
                    "Extended early-morning game drive."
                ),
                "afternoon_activities": (
                    "Lunch followed by an afternoon game drive targeting wildlife "
                    "activity around plains and wetland habitats."
                ),
                "evening_activities": (
                    "Final sundowner, dinner and preparation for departure."
                ),
                "meals_included": "Breakfast, Lunch, Dinner",
                "overnight_location": property_name,
                "transport_details": "Full-day safari vehicle operations.",
                "notes": (
                    "Final wildlife route remains subject to conditions and guide judgment."
                ),
            },
        )

        for index, day in enumerate(days, start=1):
            day["day_number"] = index

    return days


# ======================================================================================================================
# DATABASE HELPERS
# ======================================================================================================================

def get_destination() -> Tuple[SafariDestination, bool]:
    destination = SafariDestination.query.filter_by(
        slug=DESTINATION_SLUG
    ).first()

    if destination:
        return destination, False

    destination = SafariDestination(
        name=DESTINATION_NAME,
        slug=DESTINATION_SLUG,
        short_description=(
            "A legendary southern Kenya safari destination known for elephants, "
            "open plains, wetlands and dramatic views of Mount Kilimanjaro."
        ),
        introduction=(
            "Amboseli is one of Kenya's defining safari landscapes, where large "
            "elephant herds move across open plains beneath Mount Kilimanjaro. "
            "The ecosystem combines seasonal wetlands, grasslands, acacia country "
            "and surrounding community conservancies."
        ),
        history=(
            "Amboseli has a long history of wildlife conservation and safari tourism. "
            "The landscape became protected through successive conservation measures "
            "and was established as Amboseli National Park in 1974."
        ),
        landscape_and_wildlife=(
            "The ecosystem is characterized by open plains, seasonal swamps and "
            "wetlands fed by underground water originating around Mount Kilimanjaro. "
            "Elephants are a signature attraction, alongside lions, cheetahs, buffalo, "
            "giraffes, zebras, wildebeest, antelope, hippos and extensive birdlife."
        ),
        conservation_story=(
            "Amboseli's conservation story extends beyond the national park into "
            "community land and conservancies. Long-term wildlife protection depends "
            "on maintaining habitat connectivity, supporting local livelihoods and "
            "ensuring tourism contributes positively to surrounding communities."
        ),
        travel_information=(
            "Amboseli can be reached by road from Nairobi or by safari aircraft. "
            "Travel time, park access and game-drive conditions vary by season. "
            "The best-known visual feature, Mount Kilimanjaro, is frequently hidden "
            "by cloud during parts of the day, so clear views should never be promised."
        ),
        display_order=3,
        active=True,
        featured=True,
    )

    db.session.add(destination)
    db.session.flush()

    return destination, True


def get_or_create_property(
    destination: SafariDestination,
    property_data: Dict,
) -> Tuple[SafariProperty, bool]:
    property_obj = SafariProperty.query.filter_by(
        slug=property_data["slug"]
    ).first()

    if property_obj:
        return property_obj, False

    property_obj = SafariProperty(
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
        active=True,
        featured=property_data.get("featured", False),
    )

    db.session.add(property_obj)
    db.session.flush()

    return property_obj, True


def package_slug(property_slug: str, days: int, nights: int) -> str:
    return f"{property_slug}-{days}-days-{nights}-nights"


def get_or_create_package(
    property_obj: SafariProperty,
    property_data: Dict,
    days: int,
    nights: int,
) -> Tuple[SafariPackageOption, bool]:
    slug = package_slug(property_data["slug"], days, nights)

    package = SafariPackageOption.query.filter_by(
        property_id=property_obj.id,
        slug=slug,
    ).first()

    if package:
        return package, False

    content = build_package_content(property_data, days, nights)

    package = SafariPackageOption(
        property_id=property_obj.id,
        name=f"{property_data['name']} — {days} Days, {nights} Nights",
        slug=slug,
        summary=content["summary"],
        description=content["description"],
        duration_days=days,
        duration_nights=nights,
        display_currency=DEFAULT_CURRENCY,
        inclusions=content["inclusions"],
        exclusions=content["exclusions"],
        transport_details=content["transport_details"],
        meals_information=content["meals_information"],
        important_information=content["important_information"],
        display_order=days,
        active=True,
        featured=(days == 5),
    )

    db.session.add(package)
    db.session.flush()

    return package, True


def create_missing_itinerary_days(
    package: SafariPackageOption,
    property_data: Dict,
    days: int,
) -> int:
    existing_days = {
        item.day_number
        for item in SafariItineraryDay.query.filter_by(
            package_option_id=package.id
        ).all()
    }

    itinerary = build_itinerary(property_data, days)
    created = 0

    for item in itinerary:
        if item["day_number"] in existing_days:
            continue

        db.session.add(
            SafariItineraryDay(
                package_option_id=package.id,
                day_number=item["day_number"],
                title=item["title"],
                description=item["description"],
                active=True,
                morning_activities=item["morning_activities"],
                afternoon_activities=item["afternoon_activities"],
                evening_activities=item["evening_activities"],
                meals_included=item["meals_included"],
                overnight_location=item["overnight_location"],
                transport_details=item["transport_details"],
                notes=item["notes"],
            )
        )

        created += 1

    db.session.flush()
    return created


def create_missing_rates(
    package: SafariPackageOption,
    property_slug: str,
    nights: int,
) -> int:
    existing_rate_keys = {
        (
            rate.season_name,
            rate.currency,
            rate.occupancy_type,
            rate.pricing_basis,
        )
        for rate in SafariPackageRate.query.filter_by(
            package_option_id=package.id
        ).all()
    }

    created = 0
    benchmarks = PROPERTY_RATE_BENCHMARKS[property_slug]

    for season in SEASONS:
        rate_key = (
            season["name"],
            DEFAULT_CURRENCY,
            "sharing",
            "per_person_sharing",
        )

        if rate_key in existing_rate_keys:
            continue

        amount = benchmarks[season["key"]] * Decimal(nights)

        db.session.add(
            SafariPackageRate(
                package_option_id=package.id,
                name=(
                    f"{package.name} — Per Person Sharing — "
                    f"{season['name']}"
                ),
                pricing_basis="per_person_sharing",
                guest_category="adult",
                min_guest_age=18,
                max_guest_age=None,
                occupancy_type="sharing",
                min_guests=2,
                max_guests=2,
                amount=amount,
                currency=DEFAULT_CURRENCY,
                season_name=season["name"],
                valid_from=season["valid_from"],
                valid_to=season["valid_to"],
                board_basis="Full Board",
                supplier_rate_reference=(
                    f"TUR-AMBOSELI-{property_slug.upper()}-"
                    f"{season['key'].upper()}-INDICATIVE"
                ),
                rate_notes=(
                    "Indicative TUR planning benchmark based on the property's "
                    "positioning and package duration. Supplier confirmation "
                    "required before final traveller quotation."
                ),
                active=True,
                display_order=(
                    1
                    if season["key"] == "standard"
                    else 2
                    if season["key"] == "peak"
                    else 3
                ),
            )
        )

        created += 1

    db.session.flush()
    return created


# ======================================================================================================================
# VERIFICATION
# ======================================================================================================================

def verify_batch(destination: SafariDestination) -> Dict:
    properties = SafariProperty.query.filter_by(
        destination_id=destination.id
    ).order_by(SafariProperty.display_order.asc()).all()

    packages = (
        SafariPackageOption.query
        .join(SafariProperty)
        .filter(SafariProperty.destination_id == destination.id)
        .order_by(
            SafariProperty.display_order.asc(),
            SafariPackageOption.duration_days.asc(),
        )
        .all()
    )

    expected_package_count = len(PROPERTIES) * len(PACKAGE_DURATIONS)
    expected_itinerary_count = sum(days for days, _ in PACKAGE_DURATIONS) * len(PROPERTIES)
    expected_rate_count = expected_package_count * len(SEASONS)

    assert len(properties) == len(PROPERTIES), (
        f"Expected {len(PROPERTIES)} Amboseli properties, found {len(properties)}."
    )

    assert len(packages) == expected_package_count, (
        f"Expected {expected_package_count} Amboseli packages, found {len(packages)}."
    )

    itinerary_total = 0
    rate_total = 0

    for package in packages:
        itinerary_count = SafariItineraryDay.query.filter_by(
            package_option_id=package.id
        ).count()

        rate_count = SafariPackageRate.query.filter_by(
            package_option_id=package.id
        ).count()

        assert itinerary_count == package.duration_days, (
            f"{package.name}: expected {package.duration_days} itinerary days, "
            f"found {itinerary_count}."
        )

        assert rate_count == len(SEASONS), (
            f"{package.name}: expected {len(SEASONS)} rates, found {rate_count}."
        )

        itinerary_total += itinerary_count
        rate_total += rate_count

    assert itinerary_total == expected_itinerary_count, (
        f"Expected {expected_itinerary_count} itinerary days, "
        f"found {itinerary_total}."
    )

    assert rate_total == expected_rate_count, (
        f"Expected {expected_rate_count} package rates, found {rate_total}."
    )

    inquiry_count = SafariInquiry.query.count()

    return {
        "properties": len(properties),
        "packages": len(packages),
        "itinerary_days": itinerary_total,
        "rates": rate_total,
        "inquiries": inquiry_count,
        "expected_packages": expected_package_count,
        "expected_itinerary_days": expected_itinerary_count,
        "expected_rates": expected_rate_count,
    }


# ======================================================================================================================
# MAIN
# ======================================================================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate the TUR Amboseli safari catalogue."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit database changes. Without this flag the script rolls back.",
    )

    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY RUN"

    app = create_app()

    with app.app_context():
        destination_created = False
        property_created_count = 0
        property_reused_count = 0
        package_created_count = 0
        package_reused_count = 0
        itinerary_created_count = 0
        rates_created_count = 0

        print()
        print("=" * 110)
        print(f"THE UNCHARTED ROUTE — {BATCH_NAME}")
        print("=" * 110)
        print(f"Mode: {mode}")
        print("Destination scope: Amboseli only")
        print("Package durations: 3D/2N, 5D/4N, 7D/6N")
        print("Existing records: reused and preserved")
        print("Existing package rates: preserved, never modified")
        print("SafariBooking: untouched")
        print("SafariInquiry: untouched")
        print("Media: no new media associations")
        print("=" * 110)

        try:
            destination, destination_created = get_destination()

            print(
                f"\nDestination: {destination.name} | "
                f"ID={destination.id} | "
                f"{'CREATED' if destination_created else 'REUSED'}"
            )

            print()
            print("-" * 110)
            print("PROPERTY CATALOGUE")
            print("-" * 110)

            property_objects = []

            for index, property_data in enumerate(PROPERTIES, start=1):
                property_obj, created = get_or_create_property(
                    destination,
                    property_data,
                )

                property_objects.append((property_obj, property_data))

                if created:
                    property_created_count += 1
                else:
                    property_reused_count += 1

                print(
                    f"  [{index:02d}/{len(PROPERTIES)}] "
                    f"{property_obj.name} | "
                    f"ID={property_obj.id} | "
                    f"{'CREATED' if created else 'REUSED'}"
                )

            print()
            print("-" * 110)
            print("PACKAGE CATALOGUE")
            print("-" * 110)

            for property_obj, property_data in property_objects:
                print()
                print(f"  {property_obj.name}")

                for days, nights in PACKAGE_DURATIONS:
                    package, package_created = get_or_create_package(
                        property_obj,
                        property_data,
                        days,
                        nights,
                    )

                    if package_created:
                        package_created_count += 1
                    else:
                        package_reused_count += 1

                    itinerary_added = create_missing_itinerary_days(
                        package,
                        property_data,
                        days,
                    )

                    rates_added = create_missing_rates(
                        package,
                        property_data["slug"],
                        nights,
                    )

                    itinerary_created_count += itinerary_added
                    rates_created_count += rates_added

                    package_status = (
                        "CREATED"
                        if package_created
                        else "REUSED"
                    )

                    print(
                        f"    {package.name} | "
                        f"{package_status} | "
                        f"itinerary +{itinerary_added} | "
                        f"rates +{rates_added}"
                    )

            print()
            print("=" * 110)
            print("BATCH VERIFICATION")
            print("=" * 110)

            verification = verify_batch(destination)

            print(
                f"Destination verified: {destination.name} | "
                f"active={destination.active}"
            )
            print(
                f"Properties in Amboseli catalogue: "
                f"{verification['properties']}"
            )
            print(
                f"Total Amboseli packages: "
                f"{verification['packages']}"
            )

            packages = (
                SafariPackageOption.query
                .join(SafariProperty)
                .filter(SafariProperty.destination_id == destination.id)
                .order_by(
                    SafariProperty.display_order.asc(),
                    SafariPackageOption.duration_days.asc(),
                )
                .all()
            )

            for package in packages:
                itinerary_count = SafariItineraryDay.query.filter_by(
                    package_option_id=package.id
                ).count()

                rate_count = SafariPackageRate.query.filter_by(
                    package_option_id=package.id
                ).count()

                print(
                    f"      {package.name} | "
                    f"{package.duration_days}D/"
                    f"{package.duration_nights}N | "
                    f"itinerary={itinerary_count} | "
                    f"rates={rate_count}"
                )

            print(
                f"All Amboseli packages verified: "
                f"{verification['packages']}"
            )
            print(
                f"All itinerary days verified: "
                f"{verification['itinerary_days']}"
            )
            print(
                f"All package rates verified: "
                f"{verification['rates']}"
            )

            print()
            print(
                f"SafariInquiry records preserved: "
                f"{verification['inquiries']}"
            )
            print("SafariBooking: NOT TOUCHED")
            print("Media records created: 0")

            print()
            print("=" * 110)
            print("SUMMARY")
            print("=" * 110)
            print(
                f"Destination created:        "
                f"{1 if destination_created else 0}"
            )
            print(
                f"Properties created:         "
                f"{property_created_count}"
            )
            print(
                f"Properties reused:          "
                f"{property_reused_count}"
            )
            print(
                f"Packages created:           "
                f"{package_created_count}"
            )
            print(
                f"Packages reused:            "
                f"{package_reused_count}"
            )
            print(
                f"Total package slots:        "
                f"{verification['packages']}"
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
                f"Safari inquiries:           "
                f"{verification['inquiries']}"
            )
            print("Safari bookings touched:    0")
            print("Media records created:      0")

            if args.apply:
                db.session.commit()

                print()
                print("=" * 110)
                print("BATCH 3 COMMITTED SUCCESSFULLY")
                print("=" * 110)
                print(
                    "Amboseli safari catalogue populated successfully."
                )
                print(
                    "Existing operational/customer records were preserved."
                )
            else:
                db.session.rollback()

                print()
                print("=" * 110)
                print("DRY RUN COMPLETE — ROLLED BACK")
                print("=" * 110)
                print("No database changes were committed.")
                print("Run with --apply only after reviewing the output.")

        except Exception:
            db.session.rollback()

            print()
            print("=" * 110)
            print("BATCH 3 FAILED — TRANSACTION ROLLED BACK")
            print("=" * 110)

            raise


if __name__ == "__main__":
    main()