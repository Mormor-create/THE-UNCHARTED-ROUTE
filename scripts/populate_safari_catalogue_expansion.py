"""
===============================================================================
THE UNCHARTED ROUTE
Safari Catalogue Expansion — Samburu, Amboseli & Lewa
===============================================================================

PURPOSE
-------
Expand the Kenya safari catalogue with:

SAMBURU
-------
• Soroi Samburu Lodge
• Sarara Treehouses
• Samburu Sopa Lodge

AMBOSELI
--------
• Kibo Safari Camp
• Satao Elerai

LEWA WILDLIFE CONSERVANCY
-------------------------
• Elewana Lewa Safari Camp
• Elewana Kifaru House
• Lewa Wilderness

PACKAGE STRUCTURE
-----------------
Every new property receives:

• 3 Days / 2 Nights
• 5 Days / 4 Nights
• 7 Days / 6 Nights

Each package receives three indicative seasonal rates:

• Standard
• Peak
• Festive

IMPORTANT
---------
Rates in this script are INTERNAL PLANNING / SELLING BENCHMARKS ONLY.

They are NOT contracted supplier rates and must be confirmed with the
property before a quotation or booking is finalized.

SAFETY / DATA RULES
-------------------
• Existing SafariDestination records are reused.
• Existing Samburu and Amboseli records are NOT modified.
• Lewa is created if it does not already exist.
• Existing SafariProperty records are reused if their slug exists.
• Existing packages are reused.
• Existing itinerary days are preserved.
• Existing package rates are preserved.
• Missing itinerary days are added only where necessary.
• Missing seasonal rates are added only where necessary.
• SafariInquiry records are never created or modified.
• SafariBooking is not imported or touched.
• No media records are created.
• No media assets are modified.
• No unrelated catalogue records are modified.
• Dry-run performs no database writes.
• --apply uses one transaction and rolls back on failure.
• Script is safe to run repeatedly.

RUN
---
Dry run:

    python scripts/populate_safari_catalogue_expansion.py

Apply:

    python scripts/populate_safari_catalogue_expansion.py --apply

===============================================================================
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


# -----------------------------------------------------------------------------
# Ensure project root is importable
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# -----------------------------------------------------------------------------
# Application imports
# -----------------------------------------------------------------------------
from app import create_app, db
from app.models.safari import SafariDestination
from app.models.safari import SafariProperty
from app.models.safari import SafariPackageOption
from app.models.safari import SafariItineraryDay
from app.models.safari import SafariPackageRate
from app.models.safari import SafariInquiry

# =============================================================================
# CONFIGURATION
# =============================================================================

BATCH_NAME = (
    "SAFARI CATALOGUE EXPANSION — SAMBURU, AMBOSELI & LEWA"
)

DEFAULT_CURRENCY = "USD"

SUPPORTED_DURATIONS = (
    (3, 2),
    (5, 4),
    (7, 6),
)

SEASONS = (
    {
        "name": "Standard",
        "valid_from": date(2026, 11, 5),
        "valid_to": date(2027, 6, 30),
    },
    {
        "name": "Peak",
        "valid_from": date(2027, 7, 1),
        "valid_to": date(2027, 10, 31),
    },
    {
        "name": "Festive",
        "valid_from": date(2027, 12, 20),
        "valid_to": date(2028, 1, 10),
    },
)


# =============================================================================
# DESTINATIONS
# =============================================================================

DESTINATIONS = {
    "samburu": {
        "name": "Samburu National Reserve",
        "slug": "samburu",
        "short_description": (
            "A striking northern Kenya safari landscape shaped by the Ewaso Nyiro "
            "River, rugged hills, dry savannah and distinctive northern wildlife."
        ),
        "introduction": (
            "Samburu offers a very different expression of Kenya's safari country. "
            "The landscape is dry, dramatic and deeply atmospheric, with the Ewaso "
            "Nyiro River supporting wildlife and communities through an otherwise "
            "arid ecosystem. The reserve is especially known for its northern "
            "specialties, including Grevy's zebra, reticulated giraffe, gerenuk, "
            "Beisa oryx and Somali ostrich."
        ),
        "history": (
            "The Samburu region has long been shaped by pastoral communities, "
            "wildlife movement and the seasonal rhythms of the Ewaso Nyiro. "
            "Samburu National Reserve forms part of a wider northern Kenya "
            "landscape where conservation, community livelihoods and tourism "
            "increasingly intersect."
        ),
        "landscape_and_wildlife": (
            "Expect dry riverine forest, open plains, rocky escarpments and "
            "mountain-backed horizons. Wildlife commonly encountered includes "
            "elephant, lion, leopard, cheetah, buffalo, reticulated giraffe, "
            "Grevy's zebra, gerenuk, Beisa oryx, Somali ostrich and numerous "
            "bird species."
        ),
        "conservation_story": (
            "Conservation in northern Kenya depends heavily on maintaining "
            "wildlife corridors, supporting neighbouring communities and creating "
            "economic value from living landscapes. Responsible safari tourism "
            "can contribute to these efforts when it supports locally connected "
            "conservation and community initiatives."
        ),
        "travel_information": (
            "Samburu can be reached by road from Nairobi or by scheduled and "
            "charter flights to the region's safari airstrips. Road transfers "
            "within the wider northern Kenya safari circuit can be long, making "
            "fly-in itineraries particularly useful for shorter premium stays."
        ),
        "display_order": 2,
        "active": True,
        "featured": True,
    },
    "amboseli": {
        "name": "Amboseli National Park",
        "slug": "amboseli",
        "short_description": (
            "A spectacular Kilimanjaro-facing safari destination known for "
            "elephants, open plains, wetlands and dramatic mountain views."
        ),
        "introduction": (
            "Amboseli is one of Kenya's most recognisable safari landscapes. "
            "The ecosystem combines open plains, seasonal wetlands, woodland and "
            "dry country beneath the dramatic presence of Mount Kilimanjaro. "
            "Large elephant herds are among the destination's defining wildlife "
            "experiences."
        ),
        "history": (
            "The Amboseli landscape has long supported pastoral communities and "
            "wildlife movement. The national park forms part of a much larger "
            "ecosystem extending beyond its formal boundaries into community "
            "lands and conservancies."
        ),
        "landscape_and_wildlife": (
            "Amboseli's combination of open grassland, swamps and dry plains "
            "creates excellent conditions for elephants, lions, cheetahs, "
            "buffalo, giraffes, zebras, wildebeest, hippos and an impressive "
            "variety of birdlife. Clear mornings can reveal spectacular views "
            "of Mount Kilimanjaro."
        ),
        "conservation_story": (
            "The long-term future of Amboseli wildlife depends on maintaining "
            "movement routes between protected areas and community land. "
            "Conservation tourism contributes to this wider ecosystem by "
            "creating value for wildlife and supporting local livelihoods."
        ),
        "travel_information": (
            "Amboseli is accessible by road from Nairobi and by scheduled or "
            "charter safari flights. Properties may be located inside the park "
            "or within neighbouring conservancies and community areas, so exact "
            "transfer arrangements depend on the selected property."
        ),
        "display_order": 3,
        "active": True,
        "featured": True,
    },
    "lewa": {
        "name": "Lewa Wildlife Conservancy",
        "slug": "lewa-wildlife-conservancy",
        "short_description": (
            "A conservation-led safari landscape in northern Kenya known for "
            "rhino conservation, Grevy's zebra, extraordinary scenery and "
            "community-focused wildlife protection."
        ),
        "introduction": (
            "Lewa Wildlife Conservancy offers a more intimate and conservation-"
            "focused safari experience than a conventional national park circuit. "
            "Set against the foothills of Mount Kenya, the conservancy combines "
            "open grasslands, wooded country and dramatic northern landscapes "
            "with some of Kenya's most important wildlife conservation work."
        ),
        "history": (
            "Lewa's conservation story developed from a private ranching landscape "
            "into one of Kenya's best-known conservation areas. The conservancy "
            "has become internationally recognised for its work protecting "
            "black and white rhinoceros, Grevy's zebra and other wildlife while "
            "supporting neighbouring communities."
        ),
        "landscape_and_wildlife": (
            "The landscape includes open plains, rolling hills, acacia country "
            "and views towards Mount Kenya. Wildlife experiences may include "
            "black and white rhinoceros, Grevy's zebra, elephant, lion, leopard, "
            "buffalo, giraffe, zebra, eland and a rich variety of birdlife."
        ),
        "conservation_story": (
            "Conservation is central to the Lewa experience. Tourism contributes "
            "to a wider model that supports wildlife protection, community "
            "development, education and other conservation programmes. Guests "
            "therefore experience the destination as both a safari landscape and "
            "a working conservation story."
        ),
        "travel_information": (
            "Lewa is commonly reached by light aircraft from Nairobi or by "
            "private charter, followed by a lodge transfer. Access is best "
            "planned around the selected property's airstrip and transfer "
            "arrangements. Guests should allow flexibility for conservation "
            "and airstrip operating requirements."
        ),
        "display_order": 4,
        "active": True,
        "featured": True,
    },
}


# =============================================================================
# PROPERTY DATA
# =============================================================================

PROPERTIES = [
    # -------------------------------------------------------------------------
    # SAMBURU
    # -------------------------------------------------------------------------
    {
        "destination_slug": "samburu",
        "name": "Soroi Samburu Lodge",
        "slug": "soroi-samburu",
        "property_type": "lodge",
        "short_description": (
            "A refined Samburu safari lodge overlooking the Ewaso Nyiro landscape "
            "with comfortable accommodation, dining, wellness and safari access."
        ),
        "overview": (
            "Soroi Samburu Lodge combines a classic northern Kenya safari setting "
            "with a comfortable lodge experience. The property is positioned "
            "within the Samburu National Reserve landscape and provides access to "
            "game drives, riverine wildlife and the distinctive northern species "
            "for which the region is known."
        ),
        "property_story": (
            "Soroi's Samburu offering is designed around the relationship between "
            "the lodge, the river landscape and the wildlife-rich reserve. It "
            "provides a relaxed base from which guests can experience the dry "
            "country of northern Kenya without sacrificing comfort."
        ),
        "location_description": (
            "Within Samburu National Reserve in northern Kenya, close to the "
            "Ewaso Nyiro River and the reserve's principal wildlife areas."
        ),
        "accommodation_details": (
            "Accommodation includes standard and superior guest rooms together "
            "with an executive villa. The property is designed for guests seeking "
            "a comfortable full-service safari lodge in the Samburu landscape."
        ),
        "facilities": (
            "Swimming pool, spa and wellness facilities, dining areas, lounge "
            "spaces, conference facilities and safari guest services."
        ),
        "dining_information": (
            "Full-board safari dining with breakfast, lunch and dinner, together "
            "with drinks and refreshments according to the property's selected "
            "meal plan."
        ),
        "activities": (
            "Game drives, guided nature experiences, birding, cultural encounters "
            "and relaxation around the lodge."
        ),
        "wildlife_experience": (
            "Samburu's northern specialties including Grevy's zebra, reticulated "
            "giraffe, gerenuk, Beisa oryx and Somali ostrich, together with "
            "elephant, lion, leopard, buffalo and other wildlife."
        ),
        "transport_information": (
            "Accessible by road from Nairobi or by safari flight connections into "
            "the Samburu region, followed by a lodge transfer."
        ),
        "check_in_information": (
            "Standard safari lodge check-in is generally arranged around arrival "
            "and game-drive schedules. Exact times should be reconfirmed with "
            "the property before travel."
        ),
        "check_out_information": (
            "Check-out is normally coordinated with the day's safari and onward "
            "transfer schedule."
        ),
        "child_policy": (
            "Families may be accommodated subject to the property's current "
            "age restrictions and room configuration. Confirm child policy "
            "before quotation."
        ),
        "accessibility_information": (
            "Accessibility varies across safari terrain and accommodation areas. "
            "Specific mobility requirements should be confirmed before booking."
        ),
        "booking_conditions": (
            "Rates are planning benchmarks only. Final availability, inclusions, "
            "seasonal pricing, conservation or park fees and booking conditions "
            "must be confirmed with the property."
        ),
        "official_website_url": (
            "https://soroi.com/samburu-camp-portfolio/soroi-samburu-lodge/"
        ),
        "location_name": "Samburu National Reserve, Kenya",
        "display_order": 5,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("950.00"),
            "Peak": Decimal("1250.00"),
            "Festive": Decimal("1500.00"),
        },
    },
    {
        "destination_slug": "samburu",
        "name": "Sarara Treehouses",
        "slug": "sarara-treehouses",
        "property_type": "tented_camp",
        "short_description": (
            "An intimate, conservation-led treehouse camp in Namunyak Conservancy "
            "offering a distinctive northern Kenya wilderness experience."
        ),
        "overview": (
            "Sarara Treehouses offers an atmospheric stay in the wider Samburu "
            "ecosystem, combining elevated accommodation, wilderness immersion "
            "and community-connected conservation. The property is located in "
            "Namnuyak Conservancy in northern Kenya rather than inside Samburu "
            "National Reserve."
        ),
        "property_story": (
            "Sarara is closely connected to the Namunyak community conservation "
            "landscape and the wider northern Kenya conservation movement. The "
            "experience is intentionally intimate, with a strong emphasis on "
            "wilderness, community relationships and low-impact living."
        ),
        "location_description": (
            "Namnuyak Conservancy in northern Kenya, within the wider Samburu "
            "ecosystem. The property is not located inside Samburu National Reserve."
        ),
        "accommodation_details": (
            "The Treehouses provide elevated tented accommodation surrounded by "
            "the northern Kenya landscape, including eight tented rooms and a "
            "family room configuration."
        ),
        "facilities": (
            "Infinity pool, dining areas, natural outdoor spaces, solar-powered "
            "facilities and intimate camp areas designed around the wilderness "
            "setting."
        ),
        "dining_information": (
            "Fresh safari meals served around the camp experience, with dining "
            "arrangements shaped by the day's activities and camp schedule."
        ),
        "activities": (
            "Guided hikes, horseback experiences, wildlife drives, Samburu "
            "community experiences and visits connected to local conservation "
            "initiatives."
        ),
        "wildlife_experience": (
            "Northern Kenya wildlife and landscape experiences, with particular "
            "emphasis on the wider conservancy ecosystem, community conservation "
            "and wilderness rather than conventional reserve-only game viewing."
        ),
        "transport_information": (
            "Access is normally arranged by safari vehicle or light aircraft "
            "depending on the itinerary and the selected arrival airstrip."
        ),
        "check_in_information": (
            "Arrival times should be coordinated with the camp because activities "
            "and transfers are closely linked to the remote conservancy setting."
        ),
        "check_out_information": (
            "Departure is coordinated around the morning activity schedule and "
            "onward transfer."
        ),
        "child_policy": (
            "Family accommodation is available in suitable configurations, subject "
            "to the property's current age and room policies."
        ),
        "accessibility_information": (
            "The remote and elevated nature of the property means accessibility "
            "can be limited. Mobility requirements must be discussed before booking."
        ),
        "booking_conditions": (
            "Indicative planning rates only. Confirm availability, conservation "
            "fees, transfers, child policy and all inclusions with the property."
        ),
        "official_website_url": "https://sarara.co/sarara-treehouses",
        "location_name": "Namnuyak Conservancy, Northern Kenya",
        "display_order": 6,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("1400.00"),
            "Peak": Decimal("1800.00"),
            "Festive": Decimal("2200.00"),
        },
    },
    {
        "destination_slug": "samburu",
        "name": "Samburu Sopa Lodge",
        "slug": "samburu-sopa-lodge",
        "property_type": "lodge",
        "short_description": (
            "A spacious Samburu safari lodge overlooking the Ewaso Nyiro landscape "
            "with comfortable accommodation and classic safari facilities."
        ),
        "overview": (
            "Samburu Sopa Lodge provides a traditional full-service lodge base "
            "for exploring the Samburu National Reserve and surrounding northern "
            "Kenya landscape. Its setting supports classic game-drive itineraries "
            "while providing a comfortable retreat between safari activities."
        ),
        "property_story": (
            "The lodge is designed around the classic Samburu safari experience, "
            "bringing together wildlife viewing, open landscape, relaxed dining "
            "and comfortable lodge facilities."
        ),
        "location_description": (
            "Within the Samburu National Reserve landscape overlooking the "
            "Ewaso Nyiro area of northern Kenya."
        ),
        "accommodation_details": (
            "The lodge provides a large collection of guest rooms suited to "
            "couples, families and safari groups."
        ),
        "facilities": (
            "Swimming pool, restaurant, bar, laundry services, lounge areas and "
            "guest safari facilities."
        ),
        "dining_information": (
            "Restaurant and bar service with full-board safari meal plans available "
            "for guests on safari itineraries."
        ),
        "activities": (
            "Game drives, birding, nature experiences, cultural encounters and "
            "leisure around the lodge."
        ),
        "wildlife_experience": (
            "Access to Samburu's distinctive northern wildlife including elephant, "
            "lion, leopard, reticulated giraffe, Grevy's zebra, gerenuk, oryx "
            "and Somali ostrich."
        ),
        "transport_information": (
            "Road access from Nairobi or air connections into the Samburu region "
            "followed by a lodge transfer."
        ),
        "check_in_information": (
            "Check-in is coordinated around arrival and the safari activity schedule."
        ),
        "check_out_information": (
            "Departure is normally coordinated with the morning game drive and "
            "onward transfer."
        ),
        "child_policy": (
            "Children may be accommodated subject to current lodge policy and "
            "available room configurations."
        ),
        "accessibility_information": (
            "Accessibility should be confirmed in advance because safari roads "
            "and some lodge areas may present mobility limitations."
        ),
        "booking_conditions": (
            "Indicative planning benchmark only. Confirm final rates, park fees, "
            "meal plans, availability and booking conditions with the lodge."
        ),
        "official_website_url": "https://www.sopalodges.com/",
        "location_name": "Samburu National Reserve, Kenya",
        "display_order": 7,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("500.00"),
            "Peak": Decimal("650.00"),
            "Festive": Decimal("800.00"),
        },
    },

    # -------------------------------------------------------------------------
    # AMBOSELI
    # -------------------------------------------------------------------------
    {
        "destination_slug": "amboseli",
        "name": "Kibo Safari Camp",
        "slug": "kibo-safari-camp",
        "property_type": "tented_camp",
        "short_description": (
            "A comfortable tented safari camp near Amboseli with views towards "
            "Mount Kilimanjaro and easy access to the Amboseli ecosystem."
        ),
        "overview": (
            "Kibo Safari Camp provides a classic tented safari experience near "
            "Amboseli National Park. The camp is positioned outside the national "
            "park near Kimana Gate, making it an excellent base for guests seeking "
            "Amboseli wildlife and Kilimanjaro views."
        ),
        "property_story": (
            "Kibo is built around the idea of a comfortable safari camp close to "
            "the wildlife landscape, combining spacious tented accommodation, "
            "traditional safari hospitality and a strong connection to the "
            "surrounding community and environment."
        ),
        "location_description": (
            "Near Kimana Gate, just outside Amboseli National Park in the wider "
            "Amboseli ecosystem. The property is not inside the national park."
        ),
        "accommodation_details": (
            "Approximately 110 self-contained safari tents and related guest "
            "facilities, providing a comfortable base for couples, families "
            "and safari groups."
        ),
        "facilities": (
            "Swimming pool, restaurant, bar, lounge spaces, outdoor areas and "
            "guest safari services."
        ),
        "dining_information": (
            "Full-board safari meal arrangements with breakfast, lunch and dinner "
            "served according to the camp's daily schedule."
        ),
        "activities": (
            "Amboseli game drives, nature experiences, community encounters, "
            "birding and relaxation at camp."
        ),
        "wildlife_experience": (
            "Excellent access to Amboseli's elephant herds, lions, cheetahs, "
            "buffalo, giraffe, zebra, wildebeest, hippos and birdlife, with "
            "possible views of Mount Kilimanjaro."
        ),
        "transport_information": (
            "Road access from Nairobi or safari flights into the Amboseli region, "
            "followed by a transfer to camp."
        ),
        "check_in_information": (
            "Arrival is normally coordinated around game-drive schedules and "
            "the selected transfer."
        ),
        "check_out_information": (
            "Departure is coordinated with the morning safari and onward transfer."
        ),
        "child_policy": (
            "Families are welcome subject to current room and child policy."
        ),
        "accessibility_information": (
            "Guests with mobility requirements should confirm room access and "
            "safari vehicle arrangements in advance."
        ),
        "booking_conditions": (
            "Planning benchmark only. Confirm final rates, park fees, meal plan, "
            "availability and conditions with the property."
        ),
        "official_website_url": "https://kibosafaricamp.com/",
        "location_name": "Near Kimana Gate, Amboseli Ecosystem, Kenya",
        "display_order": 6,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("450.00"),
            "Peak": Decimal("600.00"),
            "Festive": Decimal("750.00"),
        },
    },
    {
        "destination_slug": "amboseli",
        "name": "Satao Elerai",
        "slug": "satao-elerai",
        "property_type": "tented_camp",
        "short_description": (
            "A conservation-focused camp in Elerai Conservancy offering an "
            "intimate Amboseli experience beyond the national park boundary."
        ),
        "overview": (
            "Satao Elerai sits within Elerai Conservancy in the wider Amboseli "
            "ecosystem, offering a more intimate alternative to a conventional "
            "national park lodge. The camp combines wildlife, community and "
            "conservation experiences in a private conservancy setting."
        ),
        "property_story": (
            "The camp is closely connected to the Elerai community and the wider "
            "conservation landscape around Amboseli. Its model highlights how "
            "tourism can support community ownership, wildlife corridors and "
            "local conservation initiatives."
        ),
        "location_description": (
            "Elerai Conservancy in the Amboseli ecosystem, approximately 10 km "
            "southeast of Amboseli National Park."
        ),
        "accommodation_details": (
            "A small collection of lodge-style suites and deluxe safari tents "
            "designed for an intimate conservancy stay."
        ),
        "facilities": (
            "Dining areas, lounge spaces, outdoor areas and safari guest facilities "
            "within a low-density conservancy setting."
        ),
        "dining_information": (
            "Full-board safari dining with meals shaped around the daily safari "
            "and conservancy activity schedule."
        ),
        "activities": (
            "Game drives, guided walks where permitted, community experiences, "
            "birding, conservation experiences and cultural activities."
        ),
        "wildlife_experience": (
            "Wildlife of the wider Amboseli ecosystem including elephant, giraffe, "
            "zebra, wildebeest, buffalo, predators and birdlife, with the added "
            "value of a private conservancy setting."
        ),
        "transport_information": (
            "Road transfers from Amboseli-area access points or coordinated "
            "safari transfers from Nairobi."
        ),
        "check_in_information": (
            "Arrival is coordinated around conservancy access and scheduled "
            "safari activities."
        ),
        "check_out_information": (
            "Departure normally follows a morning activity and onward transfer."
        ),
        "child_policy": (
            "Children may be accepted depending on accommodation and current "
            "conservancy policy. Confirm before quotation."
        ),
        "accessibility_information": (
            "Remote conservancy terrain can limit accessibility. Discuss specific "
            "mobility requirements before booking."
        ),
        "booking_conditions": (
            "Indicative benchmark only. Confirm accommodation, conservancy fees, "
            "park access, meals, transfers and final supplier conditions."
        ),
        "official_website_url": "https://www.ecotourismkenya.org/",
        "location_name": "Elerai Conservancy, Amboseli Ecosystem, Kenya",
        "display_order": 7,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("650.00"),
            "Peak": Decimal("850.00"),
            "Festive": Decimal("1050.00"),
        },
    },

    # -------------------------------------------------------------------------
    # LEWA
    # -------------------------------------------------------------------------
    {
        "destination_slug": "lewa",
        "name": "Elewana Lewa Safari Camp",
        "slug": "elewana-lewa-safari-camp",
        "property_type": "tented_camp",
        "short_description": (
            "A classic tented safari camp inside Lewa Wildlife Conservancy, "
            "combining wildlife viewing with a strong conservation story."
        ),
        "overview": (
            "Elewana Lewa Safari Camp provides an intimate safari base within "
            "Lewa Wildlife Conservancy. The camp places guests close to the "
            "conservancy's wildlife and conservation work while offering a "
            "comfortable classic safari camp experience."
        ),
        "property_story": (
            "The camp is deeply connected to Lewa's conservation identity. "
            "Guests experience the conservancy not simply as a wildlife destination "
            "but as a working landscape where tourism contributes to conservation "
            "and community initiatives."
        ),
        "location_description": (
            "Inside Lewa Wildlife Conservancy in northern Kenya, with access to "
            "the conservancy's wildlife areas and conservation programmes."
        ),
        "accommodation_details": (
            "Comfortable safari tents arranged around a central camp experience, "
            "with private guest accommodation designed for couples and safari groups."
        ),
        "facilities": (
            "Swimming pool, dining and lounge areas, campfire spaces and safari "
            "guest facilities."
        ),
        "dining_information": (
            "Full-board safari dining with meals served in camp and selected "
            "outdoor locations depending on the day's programme."
        ),
        "activities": (
            "Game drives, guided nature experiences, conservation visits, birding "
            "and selected cultural or community activities."
        ),
        "wildlife_experience": (
            "Strong opportunities for black and white rhino, Grevy's zebra, "
            "elephant, lion, leopard, buffalo, giraffe and other northern Kenya "
            "wildlife."
        ),
        "transport_information": (
            "Light-aircraft access to the Lewa area followed by a property transfer, "
            "with road access possible as part of longer northern Kenya circuits."
        ),
        "check_in_information": (
            "Arrival is coordinated with the conservancy airstrip and daily "
            "safari schedule."
        ),
        "check_out_information": (
            "Departure is coordinated around morning activities and the onward "
            "air or road transfer."
        ),
        "child_policy": (
            "Families may be accommodated subject to current camp policies and "
            "room configurations."
        ),
        "accessibility_information": (
            "Safari terrain and tented accommodation may limit accessibility. "
            "Specific requirements should be confirmed before booking."
        ),
        "booking_conditions": (
            "Planning benchmark only. Confirm conservation fees, accommodation, "
            "transfers, availability and supplier conditions."
        ),
        "official_website_url": (
            "https://www.elewanacollection.com/lewa-safari-camp"
        ),
        "location_name": "Lewa Wildlife Conservancy, Kenya",
        "display_order": 1,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("950.00"),
            "Peak": Decimal("1250.00"),
            "Festive": Decimal("1550.00"),
        },
    },
    {
        "destination_slug": "lewa",
        "name": "Elewana Kifaru House",
        "slug": "elewana-kifaru-house",
        "property_type": "lodge",
        "short_description": (
            "An intimate luxury safari house in Lewa Wildlife Conservancy "
            "designed around privacy, conservation and personalised hospitality."
        ),
        "overview": (
            "Elewana Kifaru House offers a refined, intimate safari experience "
            "within Lewa Wildlife Conservancy. The property is particularly well "
            "suited to guests seeking privacy, personalised service and close "
            "engagement with Lewa's conservation landscape."
        ),
        "property_story": (
            "Kifaru House is built around the idea of a private safari home, "
            "where the rhythms of conservation and wildlife are part of the "
            "guest experience. Its small-scale character makes it especially "
            "appropriate for private safaris, couples and special occasions."
        ),
        "location_description": (
            "Within Lewa Wildlife Conservancy in northern Kenya, surrounded by "
            "the conservancy's wildlife and open landscapes."
        ),
        "accommodation_details": (
            "Small-scale luxury accommodation designed to provide a private "
            "house-style safari experience with personalised service."
        ),
        "facilities": (
            "Private and shared guest spaces, swimming pool, dining areas, "
            "lounge spaces and safari support facilities."
        ),
        "dining_information": (
            "Personalised full-board safari dining with flexible meal locations "
            "and menus arranged around the guest experience."
        ),
        "activities": (
            "Private game drives, guided experiences, conservation activities, "
            "birding and selected community experiences."
        ),
        "wildlife_experience": (
            "Lewa's renowned rhino conservation landscape, Grevy's zebra, elephant, "
            "lion, leopard, buffalo, giraffe and other wildlife."
        ),
        "transport_information": (
            "Light-aircraft access into Lewa followed by a private property transfer."
        ),
        "check_in_information": (
            "Arrival is coordinated with the property's airstrip transfer and "
            "private safari schedule."
        ),
        "check_out_information": (
            "Departure is arranged around morning activities and onward transport."
        ),
        "child_policy": (
            "Family arrangements may be possible depending on current property "
            "policy and accommodation configuration."
        ),
        "accessibility_information": (
            "Remote safari terrain may present accessibility limitations. "
            "Specific requirements must be discussed before booking."
        ),
        "booking_conditions": (
            "Indicative planning benchmark only. Confirm current rates, conservation "
            "fees, inclusions, transfers and availability directly with the supplier."
        ),
        "official_website_url": (
            "https://www.elewanacollection.com/kifaru-house"
        ),
        "location_name": "Lewa Wildlife Conservancy, Kenya",
        "display_order": 2,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("1500.00"),
            "Peak": Decimal("2000.00"),
            "Festive": Decimal("2500.00"),
        },
    },
    {
        "destination_slug": "lewa",
        "name": "Lewa Wilderness",
        "slug": "lewa-wilderness",
        "property_type": "lodge",
        "short_description": (
            "A long-established family-run safari property within Lewa, combining "
            "classic hospitality, conservation and a broad range of activities."
        ),
        "overview": (
            "Lewa Wilderness provides an intimate and characterful safari stay "
            "within the conservancy. Its atmosphere combines family-style "
            "hospitality, wildlife viewing, conservation and a broad selection "
            "of activities beyond conventional game drives."
        ),
        "property_story": (
            "Lewa Wilderness is closely associated with the wider history and "
            "development of conservation tourism in Lewa. The property offers "
            "guests an opportunity to experience the conservancy through wildlife, "
            "landscape, hospitality and conservation activities."
        ),
        "location_description": (
            "Within Lewa Wildlife Conservancy in northern Kenya, with access to "
            "the conservancy's wildlife and activity areas."
        ),
        "accommodation_details": (
            "Characterful lodge accommodation set within the conservancy, suited "
            "to couples, families and private safari groups."
        ),
        "facilities": (
            "Swimming pool, dining spaces, lounge areas, outdoor areas and "
            "activity facilities linked to the wider conservancy."
        ),
        "dining_information": (
            "Full-board dining with flexible meal locations and menus coordinated "
            "around the day's safari and activity programme."
        ),
        "activities": (
            "Game drives, guided walks, horseback riding, birding, cultural "
            "experiences, conservation activities and other outdoor experiences."
        ),
        "wildlife_experience": (
            "Rhino, Grevy's zebra, elephant, lion, leopard, buffalo, giraffe, "
            "zebra and extensive birdlife, together with a strong conservation "
            "interpretation component."
        ),
        "transport_information": (
            "Light aircraft access to the Lewa region followed by lodge transfer, "
            "with road access available for selected itineraries."
        ),
        "check_in_information": (
            "Arrival is coordinated around airstrip transfers and the day's "
            "activity programme."
        ),
        "check_out_information": (
            "Departure is normally coordinated with the morning activity and "
            "onward transfer."
        ),
        "child_policy": (
            "Families are generally well suited to the property, subject to "
            "current age, room and activity policies."
        ),
        "accessibility_information": (
            "Some safari activities involve uneven terrain. Specific mobility "
            "requirements should be discussed with the property in advance."
        ),
        "booking_conditions": (
            "Indicative planning benchmark only. Confirm final rates, conservation "
            "fees, inclusions, transfers, activities and availability."
        ),
        "official_website_url": "https://www.lewawilderness.com/",
        "location_name": "Lewa Wildlife Conservancy, Kenya",
        "display_order": 3,
        "active": True,
        "featured": True,
        "nightly_benchmarks": {
            "Standard": Decimal("1250.00"),
            "Peak": Decimal("1650.00"),
            "Festive": Decimal("2100.00"),
        },
    },
]


# =============================================================================
# HELPERS
# =============================================================================

def package_slug(property_slug: str, duration_days: int) -> str:
    return f"{property_slug}-{duration_days}-days"


def package_name(property_name: str, duration_days: int, duration_nights: int) -> str:
    return (
        f"{property_name} — "
        f"{duration_days} Days, {duration_nights} Nights"
    )


def rate_amount(
    nightly_rate: Decimal,
    duration_nights: int,
) -> Decimal:
    return (nightly_rate * Decimal(duration_nights)).quantize(
        Decimal("0.01")
    )


def get_destination(slug: str):
    return (
        SafariDestination.query
        .filter_by(slug=slug)
        .first()
    )


def get_property(destination_id: int, slug: str):
    return (
        SafariProperty.query
        .filter_by(
            destination_id=destination_id,
            slug=slug,
        )
        .first()
    )


def get_package(property_id: int, slug: str):
    return (
        SafariPackageOption.query
        .filter_by(
            property_id=property_id,
            slug=slug,
        )
        .first()
    )


def existing_day_numbers(package_id: int) -> set[int]:
    rows = (
        SafariItineraryDay.query
        .filter_by(package_option_id=package_id)
        .all()
    )

    return {
        row.day_number
        for row in rows
    }


def existing_rate_seasons(package_id: int) -> set[str]:
    rows = (
        SafariPackageRate.query
        .filter_by(package_option_id=package_id)
        .all()
    )

    return {
        row.season_name
        for row in rows
        if row.season_name
    }


def property_benchmark_text(property_data: dict[str, Any]) -> str:
    return (
        "Indicative TUR planning benchmark. "
        "This amount is not a contracted supplier rate and must be confirmed "
        "with the property before quotation or booking."
    )


# =============================================================================
# DESTINATION CONTENT
# =============================================================================

def create_lewa_destination() -> SafariDestination:
    data = DESTINATIONS["lewa"]

    destination = SafariDestination(
        name=data["name"],
        slug=data["slug"],
        short_description=data["short_description"],
        introduction=data["introduction"],
        history=data["history"],
        landscape_and_wildlife=data["landscape_and_wildlife"],
        conservation_story=data["conservation_story"],
        travel_information=data["travel_information"],
        display_order=data["display_order"],
        active=data["active"],
        featured=data["featured"],
    )

    db.session.add(destination)

    return destination


# =============================================================================
# PACKAGE CONTENT
# =============================================================================

def package_content(
    property_data: dict[str, Any],
    destination_data: dict[str, Any],
    duration_days: int,
    duration_nights: int,
) -> dict[str, Any]:

    destination_name = destination_data["name"]
    property_name = property_data["name"]

    is_samburu = property_data["destination_slug"] == "samburu"
    is_amboseli = property_data["destination_slug"] == "amboseli"
    is_lewa = property_data["destination_slug"] == "lewa"

    if is_samburu:
        wildlife_focus = (
            "reticulated giraffe, Grevy's zebra, gerenuk, Beisa oryx, "
            "Somali ostrich, elephant, lion, leopard and other Samburu wildlife"
        )
        signature = (
            "Northern Kenya's distinctive wildlife and the dramatic Ewaso Nyiro "
            "landscape"
        )
    elif is_amboseli:
        wildlife_focus = (
            "large elephant herds, lion, cheetah, buffalo, giraffe, zebra, "
            "wildebeest, hippo and abundant birdlife"
        )
        signature = (
            "Amboseli's elephant country and spectacular Mount Kilimanjaro views"
        )
    else:
        wildlife_focus = (
            "black and white rhinoceros, Grevy's zebra, elephant, lion, leopard, "
            "buffalo, giraffe and other Lewa wildlife"
        )
        signature = (
            "Lewa's conservation landscape and exceptional rhino experience"
        )

    if duration_days == 3:
        summary = (
            f"A focused {duration_days}-day safari at {property_name}, designed "
            f"for guests who want a premium introduction to {destination_name} "
            f"without a long itinerary."
        )

        description = (
            f"Spend {duration_nights} nights at {property_name} on a carefully "
            f"paced safari through {destination_name}. The journey combines "
            f"morning and afternoon wildlife viewing with time to settle into "
            f"the property and experience the landscape beyond a rushed "
            f"checklist-style safari. The signature experience is {signature}."
        )

        highlights = (
            f"{property_name}; "
            f"{wildlife_focus}; "
            "guided safari activities; "
            "slow-paced lodge or camp time; "
            "sunrise and sunset landscape experiences"
        )

        itinerary = [
            {
                "title": "Arrival & First Wilderness Drive",
                "description": (
                    f"Arrive into the {destination_name} area and transfer to "
                    f"{property_name}. Settle into camp, enjoy lunch or refreshments "
                    "and receive a safari briefing. Later, head out for the first "
                    "game drive, using the afternoon light to begin exploring the "
                    "landscape. Return to camp for dinner and an evening around "
                    "the property."
                ),
                "morning": "Arrival transfer or morning flight connection.",
                "afternoon": "Check-in, lunch and first game drive.",
                "evening": "Dinner and relaxed camp or lodge evening.",
                "meals": "Lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Full Safari Day",
                "description": (
                    f"Start early for a full safari experience focused on the "
                    f"wildlife and landscapes of {destination_name}. Depending "
                    "on wildlife movement and guest preference, the day may "
                    "include a longer game drive with a picnic breakfast or "
                    "lunch. Return to the property later for rest, followed by "
                    "an optional sunset activity."
                ),
                "morning": "Early breakfast and extended game drive.",
                "afternoon": "Lunch, rest and afternoon wildlife activity.",
                "evening": "Sunset experience and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Final Game Drive & Departure",
                "description": (
                    "Enjoy a final early-morning safari activity before breakfast. "
                    "Use the remaining time for photography, relaxation or a "
                    "property-based experience before checking out and transferring "
                    "to the airstrip or onward road connection."
                ),
                "morning": "Final game drive and breakfast.",
                "afternoon": "Check-out and onward transfer.",
                "evening": "Onward travel.",
                "meals": "Breakfast and lunch where departure timing permits.",
                "overnight": "—",
            },
        ]

    elif duration_days == 5:
        summary = (
            f"A balanced {duration_days}-day safari at {property_name}, allowing "
            f"more time to explore {destination_name}, vary safari routes and "
            "enjoy the property at a relaxed pace."
        )

        description = (
            f"This {duration_days}-day safari combines {duration_nights} nights "
            f"at {property_name} with multiple wildlife-viewing opportunities "
            f"across {destination_name}. The itinerary allows guests to slow "
            "down, photograph the landscape, spend meaningful time in the field "
            "and experience more than one rhythm of safari. The defining focus "
            f"is {signature}."
        )

        highlights = (
            f"{property_name}; "
            f"{wildlife_focus}; "
            "multiple game-drive windows; "
            "flexible full-day safari opportunity; "
            "guided nature or cultural experiences where available; "
            "slow safari pacing"
        )

        itinerary = [
            {
                "title": "Arrival & First Safari",
                "description": (
                    f"Arrive in {destination_name}, transfer to {property_name} "
                    "and settle into the safari environment. After lunch and "
                    "a briefing, head out for an introductory afternoon drive."
                ),
                "morning": "Arrival transfer.",
                "afternoon": "Check-in, lunch and introductory game drive.",
                "evening": "Dinner and camp or lodge evening.",
                "meals": "Lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Dawn Wildlife & River / Plains Exploration",
                "description": (
                    f"Begin with an early safari drive while wildlife is active. "
                    f"Explore different habitats within {destination_name}, "
                    "returning for breakfast and time to rest before a second "
                    "afternoon activity."
                ),
                "morning": "Early game drive and breakfast.",
                "afternoon": "Lunch, rest and second safari activity.",
                "evening": "Sunset and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Full-Day Wilderness Safari",
                "description": (
                    "Set out after an early breakfast for a longer safari day. "
                    "Carry a picnic or enjoy a field lunch depending on the "
                    "property's operating style. The day is designed to cover "
                    "more ground while allowing time for photography and "
                    "wildlife observation."
                ),
                "morning": "Extended morning game drive.",
                "afternoon": "Full-day safari and field lunch.",
                "evening": "Return to camp and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Conservation, Culture & Safari",
                "description": (
                    f"Use the fourth day to experience a different side of "
                    f"{destination_name}. Depending on the property, this may "
                    "include conservation interpretation, a guided nature walk, "
                    "birding, cultural engagement or another specialist activity, "
                    "followed by a final afternoon safari."
                ),
                "morning": "Guided activity, conservation or cultural experience.",
                "afternoon": "Lunch and afternoon game drive.",
                "evening": "Sunset and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Final Safari & Departure",
                "description": (
                    "Take a final early-morning wildlife drive before returning "
                    "for breakfast. Check out and transfer onward, carrying the "
                    "memories and photographs of the safari with you."
                ),
                "morning": "Final game drive and breakfast.",
                "afternoon": "Check-out and onward transfer.",
                "evening": "Onward travel.",
                "meals": "Breakfast and lunch where applicable.",
                "overnight": "—",
            },
        ]

    else:
        summary = (
            f"A comprehensive {duration_days}-day safari at {property_name}, "
            f"designed for guests who want time to explore {destination_name} "
            "without rushing the experience."
        )

        description = (
            f"Spend {duration_nights} nights at {property_name} on an immersive "
            f"{destination_name} safari. The longer format creates space for "
            "repeat wildlife encounters, different habitats, photography, "
            "conservation interpretation and genuine downtime at the property. "
            f"The journey is anchored by {signature}."
        )

        highlights = (
            f"{property_name}; "
            f"{wildlife_focus}; "
            "multiple full safari days; "
            "flexible wildlife-viewing routes; "
            "conservation or cultural interpretation; "
            "photography opportunities; "
            "slow luxury safari pacing"
        )

        itinerary = [
            {
                "title": "Arrival & Introduction to the Wild",
                "description": (
                    f"Arrive in {destination_name}, transfer to {property_name} "
                    "and settle into the safari rhythm. After lunch and a briefing, "
                    "enjoy an introductory afternoon game drive."
                ),
                "morning": "Arrival transfer.",
                "afternoon": "Check-in, lunch and introductory game drive.",
                "evening": "Dinner and camp or lodge evening.",
                "meals": "Lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Dawn Safari",
                "description": (
                    "Rise early for a dawn game drive when predators and other "
                    "wildlife may still be active. Return for breakfast and "
                    "enjoy a relaxed midday period before a second safari activity."
                ),
                "morning": "Dawn game drive and breakfast.",
                "afternoon": "Rest, lunch and afternoon safari.",
                "evening": "Sunset and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Full-Day Wildlife Exploration",
                "description": (
                    f"Spend a full day exploring {destination_name}. The route "
                    "can be adapted around recent wildlife sightings, seasonal "
                    "conditions and guest interests. A field breakfast or picnic "
                    "lunch may be arranged where appropriate."
                ),
                "morning": "Early departure and extended safari.",
                "afternoon": "Full-day game viewing and field lunch.",
                "evening": "Return to property and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Conservation & Landscape",
                "description": (
                    "Experience the landscape beyond conventional game drives. "
                    "Depending on location and property, this may include a "
                    "conservation visit, guided nature activity, birding, "
                    "community interaction or specialist interpretation."
                ),
                "morning": "Guided conservation, nature or cultural activity.",
                "afternoon": "Lunch, rest and afternoon safari.",
                "evening": "Sunset and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Specialist Safari Day",
                "description": (
                    "Use another full day to follow wildlife movement and explore "
                    "a different section of the ecosystem. The safari team can "
                    "adapt the route around photography, birding, predators, "
                    "elephants, rhino or other guest priorities."
                ),
                "morning": "Early safari and specialist wildlife focus.",
                "afternoon": "Picnic or property lunch followed by another drive.",
                "evening": "Sunset and dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Slow Safari & Final Encounters",
                "description": (
                    "Enjoy a slower safari day with time for another wildlife "
                    "drive, property experience or conservation-focused activity. "
                    "The aim is to leave space for the unexpected rather than "
                    "overloading the final full day."
                ),
                "morning": "Morning game drive or guided activity.",
                "afternoon": "Leisure, lunch and final afternoon safari.",
                "evening": "Farewell dinner.",
                "meals": "Breakfast, lunch and dinner.",
                "overnight": property_name,
            },
            {
                "title": "Final Game Drive & Departure",
                "description": (
                    "Take one final early-morning safari before breakfast. "
                    "Check out and transfer to the airstrip or onward road "
                    "connection for the next chapter of the journey."
                ),
                "morning": "Final game drive and breakfast.",
                "afternoon": "Check-out and onward transfer.",
                "evening": "Onward travel.",
                "meals": "Breakfast and lunch where applicable.",
                "overnight": "—",
            },
        ]

    return {
        "summary": summary,
        "description": description,
        "inclusions": (
            "Accommodation at the selected safari property; "
            "full-board meal plan unless otherwise confirmed; "
            "scheduled safari activities; "
            "professional safari guiding; "
            "standard shared safari vehicle arrangements; "
            "applicable property services included in the confirmed rate"
        ),
        "exclusions": (
            "International flights; "
            "domestic flights unless specifically quoted; "
            "park entry fees unless explicitly included; "
            "conservation or conservancy fees unless explicitly included; "
            "premium drinks; "
            "laundry and personal expenses; "
            "tips and gratuities; "
            "travel insurance; "
            "visa and passport costs; "
            "items not expressly included in the confirmed quotation"
        ),
        "transport_details": (
            "Road transfers and safari vehicle movements are arranged around "
            "the selected property and itinerary. Air transfers can be quoted "
            "separately where applicable."
        ),
        "meals_information": (
            "Full-board safari dining is assumed for planning purposes. "
            "Final meal plan must be confirmed against the supplier quotation."
        ),
        "important_information": (
            f"{property_benchmark_text(property_data)} "
            "Wildlife sightings are never guaranteed. Safari routes and activity "
            "times may change because of weather, wildlife movement, conservation "
            "requirements and operational conditions."
        ),
        "highlights": highlights,
        "itinerary": itinerary,
    }


# =============================================================================
# CREATE / REUSE HELPERS
# =============================================================================

def create_or_get_destination(
    slug: str,
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    existing = get_destination(slug)

    if existing:
        stats["destinations_reused"] += 1
        print(
            f"DESTINATION REUSED: "
            f"{existing.name} (ID={existing.id})"
        )
        return existing

    if slug != "lewa":
        raise RuntimeError(
            f"Required existing destination '{slug}' was not found. "
            "The script will not create or replace Samburu/Amboseli "
            "automatically."
        )

    data = DESTINATIONS[slug]

    if not apply_changes:
        stats["destinations_created"] += 1
        print(
            f"DESTINATION WOULD BE CREATED: "
            f"{data['name']} ({data['slug']})"
        )
        return None

    destination = create_lewa_destination()

    db.session.flush()

    stats["destinations_created"] += 1

    print(
        f"DESTINATION CREATED: "
        f"{destination.name} (ID={destination.id})"
    )

    return destination


def create_or_get_property(
    destination,
    property_data: dict[str, Any],
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    if destination is None:
        stats["properties_created"] += 1

        print(
            f"PROPERTY WOULD BE CREATED: "
            f"{property_data['name']}"
        )

        return None

    existing = get_property(
        destination.id,
        property_data["slug"],
    )

    if existing:
        stats["properties_reused"] += 1

        print(
            f"PROPERTY REUSED: "
            f"{existing.name} (ID={existing.id})"
        )

        return existing

    if not apply_changes:
        stats["properties_created"] += 1

        print(
            f"PROPERTY WOULD BE CREATED: "
            f"{property_data['name']}"
        )

        return None

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

    stats["properties_created"] += 1

    print(
        f"PROPERTY CREATED: "
        f"{property_record.name} (ID={property_record.id})"
    )

    return property_record


def create_or_get_package(
    property_record,
    property_data: dict[str, Any],
    destination_data: dict[str, Any],
    duration_days: int,
    duration_nights: int,
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    slug = package_slug(
        property_data["slug"],
        duration_days,
    )

    name = package_name(
        property_data["name"],
        duration_days,
        duration_nights,
    )

    if property_record is None:
        stats["packages_created"] += 1

        print(
            f"  PACKAGE WOULD BE CREATED: {name}"
        )

        return None

    existing = get_package(
        property_record.id,
        slug,
    )

    if existing:
        stats["packages_reused"] += 1

        print(
            f"  PACKAGE REUSED: {existing.name} (ID={existing.id})"
        )

        return existing

    content = package_content(
        property_data,
        destination_data,
        duration_days,
        duration_nights,
    )

    if not apply_changes:
        stats["packages_created"] += 1

        print(
            f"  PACKAGE WOULD BE CREATED: {name}"
        )

        return None

    package = SafariPackageOption(
        property_id=property_record.id,
        name=name,
        slug=slug,
        summary=content["summary"],
        description=content["description"],
        duration_days=duration_days,
        duration_nights=duration_nights,
        display_currency=DEFAULT_CURRENCY,
        inclusions=content["inclusions"],
        exclusions=content["exclusions"],
        transport_details=content["transport_details"],
        meals_information=content["meals_information"],
        important_information=content["important_information"],
        display_order=duration_days,
        active=True,
        featured=(duration_days == 5),
    )

    db.session.add(package)
    db.session.flush()

    stats["packages_created"] += 1

    print(
        f"  PACKAGE CREATED: {package.name} (ID={package.id})"
    )

    return package


# =============================================================================
# ITINERARY
# =============================================================================

def add_itinerary_days(
    package,
    property_data: dict[str, Any],
    destination_data: dict[str, Any],
    duration_days: int,
    duration_nights: int,
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    if package is None:
        content = package_content(
            property_data,
            destination_data,
            duration_days,
            duration_nights,
        )

        for day_number, day in enumerate(
            content["itinerary"],
            start=1,
        ):
            stats["itinerary_days_added"] += 1

            print(
                f"    DAY {day_number} WOULD BE CREATED: "
                f"{day['title']}"
            )

        return

    existing_days = existing_day_numbers(package.id)

    content = package_content(
        property_data,
        destination_data,
        duration_days,
        duration_nights,
    )

    for day_number, day in enumerate(
        content["itinerary"],
        start=1,
    ):
        if day_number in existing_days:
            stats["itinerary_days_reused"] += 1

            print(
                f"    DAY {day_number} PRESERVED"
            )

            continue

        if not apply_changes:
            stats["itinerary_days_added"] += 1

            print(
                f"    DAY {day_number} WOULD BE CREATED: "
                f"{day['title']}"
            )

            continue

        itinerary_day = SafariItineraryDay(
            package_option_id=package.id,
            day_number=day_number,
            title=day["title"],
            description=day["description"],
            active=True,
            morning_activities=day["morning"],
            afternoon_activities=day["afternoon"],
            evening_activities=day["evening"],
            meals_included=day["meals"],
            overnight_location=day["overnight"],
            transport_details=(
                "Safari vehicle transfers and property transport "
                "according to the confirmed itinerary."
            ),
            notes=(
                "Daily activities are indicative and may be adjusted "
                "according to wildlife movement, weather, conservation "
                "requirements and guest preferences."
            ),
        )

        db.session.add(itinerary_day)

        stats["itinerary_days_added"] += 1

        print(
            f"    DAY {day_number} CREATED: "
            f"{day['title']}"
        )


# =============================================================================
# RATES
# =============================================================================

def add_package_rates(
    package,
    property_data: dict[str, Any],
    duration_nights: int,
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    if package is None:
        for season in SEASONS:
            nightly = property_data["nightly_benchmarks"][
                season["name"]
            ]

            total = rate_amount(
                nightly,
                duration_nights,
            )

            stats["rates_added"] += 1

            print(
                f"    RATE WOULD BE CREATED: "
                f"{season['name']} — "
                f"{total} USD"
            )

        return

    existing_seasons = existing_rate_seasons(
        package.id
    )

    for season in SEASONS:
        season_name = season["name"]

        if season_name in existing_seasons:
            stats["rates_reused"] += 1

            print(
                f"    RATE PRESERVED: "
                f"{season_name}"
            )

            continue

        nightly = property_data["nightly_benchmarks"][
            season_name
        ]

        total = rate_amount(
            nightly,
            duration_nights,
        )

        if not apply_changes:
            stats["rates_added"] += 1

            print(
                f"    RATE WOULD BE CREATED: "
                f"{season_name} — {total} USD"
            )

            continue

        rate = SafariPackageRate(
            package_option_id=package.id,
            name=f"{season_name} — Adult Sharing",
            pricing_basis="per_person_sharing",
            guest_category="adult",
            min_guest_age=18,
            max_guest_age=None,
            occupancy_type="sharing",
            min_guests=2,
            max_guests=None,
            amount=total,
            currency=DEFAULT_CURRENCY,
            season_name=season_name,
            valid_from=season["valid_from"],
            valid_to=season["valid_to"],
            board_basis="Full Board",
            supplier_rate_reference=None,
            rate_notes=(
                "Indicative TUR planning / selling benchmark only. "
                "Not a contracted supplier rate. Supplier confirmation "
                "is required before quotation or booking."
            ),
            active=True,
            display_order=season["valid_from"].year,
        )

        db.session.add(rate)

        stats["rates_added"] += 1

        print(
            f"    RATE CREATED: "
            f"{season_name} — {total} USD"
        )


# =============================================================================
# PROPERTY PROCESSING
# =============================================================================

def process_property(
    property_data: dict[str, Any],
    destinations: dict[str, Any],
    *,
    apply_changes: bool,
    stats: dict[str, int],
):
    destination_slug = property_data["destination_slug"]

    destination = destinations[destination_slug]

    destination_data = DESTINATIONS[destination_slug]

    property_record = create_or_get_property(
        destination,
        property_data,
        apply_changes=apply_changes,
        stats=stats,
    )

    for duration_days, duration_nights in SUPPORTED_DURATIONS:
        package = create_or_get_package(
            property_record,
            property_data,
            destination_data,
            duration_days,
            duration_nights,
            apply_changes=apply_changes,
            stats=stats,
        )

        add_itinerary_days(
            package,
            property_data,
            destination_data,
            duration_days,
            duration_nights,
            apply_changes=apply_changes,
            stats=stats,
        )

        add_package_rates(
            package,
            property_data,
            duration_nights,
            apply_changes=apply_changes,
            stats=stats,
        )


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_target_catalogue(
    *,
    before_inquiries: int | None = None,
    apply_changes: bool,
):
    print()
    print("=" * 79)
    print("VERIFICATION")
    print("=" * 79)

    expected_properties = {
        property_data["slug"]
        for property_data in PROPERTIES
    }

    found_properties = set()

    for property_data in PROPERTIES:
        destination = get_destination(
            property_data["destination_slug"]
        )

        if destination is None:
            print(
                f"ERROR: Destination missing: "
                f"{property_data['destination_slug']}"
            )
            continue

        property_record = get_property(
            destination.id,
            property_data["slug"],
        )

        if property_record is None:
            print(
                f"ERROR: Property missing: "
                f"{property_data['name']}"
            )
            continue

        found_properties.add(
            property_record.slug
        )

        print(
            f"PROPERTY VERIFIED: "
            f"{property_record.name} "
            f"(ID={property_record.id})"
        )

        for duration_days, duration_nights in SUPPORTED_DURATIONS:
            slug = package_slug(
                property_data["slug"],
                duration_days,
            )

            package = get_package(
                property_record.id,
                slug,
            )

            if package is None:
                print(
                    f"  ERROR: Missing package: "
                    f"{duration_days} days"
                )
                continue

            day_count = (
                SafariItineraryDay.query
                .filter_by(
                    package_option_id=package.id
                )
                .count()
            )

            rate_count = (
                SafariPackageRate.query
                .filter_by(
                    package_option_id=package.id
                )
                .count()
            )

            print(
                f"  {duration_days}D/{duration_nights}N — "
                f"days={day_count}, rates={rate_count}"
            )

    print()
    print(
        f"Target properties verified: "
        f"{len(found_properties)} / {len(expected_properties)}"
    )

    total_target_packages = 0
    total_target_days = 0
    total_target_rates = 0

    for property_data in PROPERTIES:
        destination = get_destination(
            property_data["destination_slug"]
        )

        if destination is None:
            continue

        property_record = get_property(
            destination.id,
            property_data["slug"],
        )

        if property_record is None:
            continue

        for duration_days, duration_nights in SUPPORTED_DURATIONS:
            package = get_package(
                property_record.id,
                package_slug(
                    property_data["slug"],
                    duration_days,
                ),
            )

            if package is None:
                continue

            total_target_packages += 1

            total_target_days += (
                SafariItineraryDay.query
                .filter_by(
                    package_option_id=package.id
                )
                .count()
            )

            total_target_rates += (
                SafariPackageRate.query
                .filter_by(
                    package_option_id=package.id
                )
                .count()
            )

    expected_package_count = 24
    expected_day_count = 120
    expected_rate_count = 72

    print()
    print(
        f"Target packages: "
        f"{total_target_packages} / {expected_package_count}"
    )

    print(
        f"Target itinerary days: "
        f"{total_target_days} / {expected_day_count}"
    )

    print(
        f"Target rates: "
        f"{total_target_rates} / {expected_rate_count}"
    )

    if before_inquiries is not None:
        after_inquiries = SafariInquiry.query.count()

        print(
            f"Safari inquiries preserved: "
            f"{before_inquiries} → {after_inquiries}"
        )

        if before_inquiries != after_inquiries:
            raise RuntimeError(
                "SafariInquiry count changed. "
                "This script must never create or modify inquiries."
            )

    print()
    print("Safari bookings touched: 0")
    print("Safari media records created: 0")


# =============================================================================
# MAIN POPULATION
# =============================================================================

def populate(apply_changes: bool = False):
    app = create_app()

    with app.app_context():

        print()
        print("=" * 79)
        print(BATCH_NAME)
        print("=" * 79)

        print()
        print(
            f"Mode: "
            f"{'APPLY' if apply_changes else 'DRY RUN'}"
        )

        print(
            "Existing SafariInquiry records will be preserved."
        )

        print(
            "SafariBooking records are not imported or touched."
        )

        print(
            "No media records will be created."
        )

        print()

        stats = {
            "destinations_created": 0,
            "destinations_reused": 0,
            "properties_created": 0,
            "properties_reused": 0,
            "packages_created": 0,
            "packages_reused": 0,
            "itinerary_days_added": 0,
            "itinerary_days_reused": 0,
            "rates_added": 0,
            "rates_reused": 0,
        }

        before_inquiries = SafariInquiry.query.count()

        destinations = {}

        # ---------------------------------------------------------------------
        # Resolve existing Samburu and Amboseli.
        # Lewa may be created.
        # ---------------------------------------------------------------------

        for destination_slug in (
            "samburu",
            "amboseli",
            "lewa",
        ):
            destinations[destination_slug] = (
                create_or_get_destination(
                    destination_slug,
                    apply_changes=apply_changes,
                    stats=stats,
                )
            )

        # ---------------------------------------------------------------------
        # Process all eight new properties.
        # ---------------------------------------------------------------------

        print()
        print("-" * 79)
        print("PROCESSING PROPERTIES")
        print("-" * 79)

        transaction_started = False

        try:
            if apply_changes:
                transaction_started = True

            for property_data in PROPERTIES:
                print()
                print(
                    f"[{property_data['destination_slug'].upper()}] "
                    f"{property_data['name']}"
                )

                process_property(
                    property_data,
                    destinations,
                    apply_changes=apply_changes,
                    stats=stats,
                )

            # ---------------------------------------------------------------
            # Apply mode
            # ---------------------------------------------------------------

            if apply_changes:
                print()
                print("-" * 79)
                print("COMMITTING TRANSACTION")
                print("-" * 79)

                db.session.commit()

                transaction_started = False

                print(
                    "Transaction committed successfully."
                )

            # ---------------------------------------------------------------
            # Dry-run mode
            # ---------------------------------------------------------------

            else:
                print()
                print("-" * 79)
                print("DRY RUN COMPLETE")
                print("-" * 79)

                print(
                    "No database writes were performed."
                )

                return

        except Exception:
            if transaction_started:
                db.session.rollback()

            print()
            print("=" * 79)
            print("ERROR")
            print("=" * 79)

            print(
                "Population failed. "
                "All changes from this transaction were rolled back."
            )

            raise

        # ---------------------------------------------------------------------
        # Verification after successful commit
        # ---------------------------------------------------------------------

        verify_target_catalogue(
            before_inquiries=before_inquiries,
            apply_changes=apply_changes,
        )

        # ---------------------------------------------------------------------
        # Final summary
        # ---------------------------------------------------------------------

        print()
        print("=" * 79)
        print("FINAL SUMMARY")
        print("=" * 79)

        print(
            f"Destination created       : "
            f"{stats['destinations_created']}"
        )

        print(
            f"Destinations reused       : "
            f"{stats['destinations_reused']}"
        )

        print(
            f"Properties created        : "
            f"{stats['properties_created']}"
        )

        print(
            f"Properties reused         : "
            f"{stats['properties_reused']}"
        )

        print(
            f"Packages created          : "
            f"{stats['packages_created']}"
        )

        print(
            f"Packages reused           : "
            f"{stats['packages_reused']}"
        )

        print(
            f"Itinerary days added      : "
            f"{stats['itinerary_days_added']}"
        )

        print(
            f"Itinerary days preserved  : "
            f"{stats['itinerary_days_reused']}"
        )

        print(
            f"Package rates added       : "
            f"{stats['rates_added']}"
        )

        print(
            f"Package rates preserved   : "
            f"{stats['rates_reused']}"
        )

        print(
            f"Safari inquiries          : "
            f"{before_inquiries}"
        )

        print(
            "Safari bookings touched   : 0"
        )

        print(
            "Media records created     : 0"
        )

        print()
        print(
            "Safari expansion batch completed successfully."
        )

        print(
            "This batch adds no SafariBooking functionality."
        )

        print(
            "Existing catalogue records were preserved."
        )

        print(
            "Indicative rates require supplier confirmation."
        )

        print("=" * 79)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Populate The Uncharted Route's Kenya safari catalogue "
            "expansion for Samburu, Amboseli and Lewa."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply database changes. Default is a read-only dry run.",
    )

    args = parser.parse_args()

    populate(
        apply_changes=args.apply
    )


if __name__ == "__main__":
    main()