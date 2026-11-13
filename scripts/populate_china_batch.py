"""
THE UNCHARTED ROUTE — BATCH 7: CHINA

Destinations:
    - Beijing
    - Shanghai
    - Hong Kong
    - Xi'an
    - Chongqing
    - Chengdu

Experiences:
    01. CHI-BJS-001 — Beijing Imperial Heritage, Great Wall & Old City Discovery
    02. CHI-SHA-001 — Shanghai Bund, Old Town & Modern City Experience
    03. CHI-HKG-001 — Hong Kong Victoria Harbour, Markets & Island Culture
    04. CHI-XIA-001 — Xi'an Terracotta Army, Ancient City & Silk Road Discovery
    05. CHI-CQ-001 — Chongqing Mountain City, Yangtze & Night Lights Experience
    06. CHI-CD-001 — Chengdu Pandas, Teahouses & Sichuan Culture Experience

IMPORTANT:
    - DRY RUN is the default.
    - Use --apply to commit.
    - Existing experiences are never modified.
    - Duplicate code/slug protection is enforced.
    - Existing destinations/categories are reused only.
    - No media, schedules or bookings are created.
    - Prices are actual USD selling prices per person for the individual
      experience.
"""

from __future__ import annotations

import argparse
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any


# ============================================================================
# PROJECT ROOT
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app import create_app, db
from app.models.experience import Experience


# ============================================================================
# CONFIGURATION
# ============================================================================

BATCH_NAME = "BATCH 7: CHINA"

DEFAULT_FEATURED_IMAGE = (
    "images/experiences/default-experience.jpg"
)

SUPPORTED_CURRENCY = "USD"


# ============================================================================
# EXPERIENCE DATA
# ============================================================================

EXPERIENCES = [

    # ------------------------------------------------------------------------
    # 01 — BEIJING
    # ------------------------------------------------------------------------

    {
        "code": "CHI-BJS-001",
        "title": (
            "Beijing Imperial Heritage, Great Wall & Old City Discovery"
        ),
        "slug": (
            "beijing-imperial-heritage-great-wall-old-city-discovery"
        ),
        "short_description": (
            "A curated Beijing journey combining imperial heritage, "
            "historic neighbourhoods and an unforgettable Great Wall visit."
        ),
        "description": (
            "Discover Beijing through the layers of imperial history, "
            "traditional neighbourhood life and the landscapes surrounding "
            "the Great Wall. The experience brings together the city's "
            "historic centre with a carefully selected Great Wall section, "
            "allowing guests to understand both the power of imperial Beijing "
            "and the living culture of the modern capital."
        ),
        "duration": "8–10 hours",
        "meeting_point": (
            "Central Beijing hotel or agreed city meeting point"
        ),
        "location": "Beijing, China",
        "price_from": Decimal("125.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": (
            "All ages; children must be accompanied by an adult"
        ),
        "difficulty": "Moderate",
        "featured": True,
        "active": True,
        "display_order": 701,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "beijing",
        "seo_title": (
            "Beijing Imperial Heritage, Great Wall & Old City Discovery"
        ),
        "seo_description": (
            "Explore Beijing's imperial heritage, historic Old City and "
            "the Great Wall on a curated cultural experience."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("125.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("175.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "Beijing Old City",
                "description": (
                    "Meet your host and begin with an orientation through "
                    "Beijing's historic heart and traditional urban landscape."
                ),
            },
            {
                "title": "Imperial Heritage",
                "description": (
                    "Explore the historic imperial district and learn about "
                    "the political, cultural and architectural legacy of "
                    "China's former capital."
                ),
            },
            {
                "title": "Great Wall",
                "description": (
                    "Travel to a selected Great Wall section for a guided "
                    "walk, photography and time to appreciate the scale of "
                    "this extraordinary historic structure."
                ),
            },
            {
                "title": "Historic Neighbourhoods",
                "description": (
                    "Return toward Beijing and explore selected traditional "
                    "streets or hutong areas before concluding the experience."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Beijing heritage experience",
            "Great Wall visit",
            "Historic city and neighbourhood discovery",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks unless specifically stated",
            "Optional attraction admissions not listed",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Discover Beijing's imperial heritage",
            "Walk along a selected section of the Great Wall",
            "Explore historic neighbourhoods",
            "Learn about traditional Beijing culture",
            "Experience the contrast between ancient and modern Beijing",
        ],

        "addons": [
            {
                "title": "Private Great Wall Upgrade",
                "description": (
                    "Upgrade to a private Great Wall experience "
                    "where available."
                ),
            },
            {
                "title": "Traditional Beijing Food Tasting",
                "description": (
                    "Add a curated tasting of selected Beijing dishes "
                    "and local specialities."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Weather-appropriate layers",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
            "Camera or phone",
        ],

        "safety_rules": [
            "Follow host instructions on Great Wall sections.",
            "Use designated walking paths.",
            "Stay hydrated during extended outdoor walking.",
            "Keep valuables secure in crowded public areas.",
        ],

        "requirements": [
            "Guests should be comfortable with moderate walking.",
            "Great Wall sections may include steep and uneven surfaces.",
            "Children must be accompanied by an adult.",
        ],

        "faqs": [
            {
                "question": "Which Great Wall section will we visit?",
                "answer": (
                    "The exact section may vary according to operating "
                    "conditions, season and availability while preserving "
                    "the core Great Wall experience."
                ),
            },
            {
                "question": "Is this suitable for families?",
                "answer": (
                    "Yes, although some Great Wall sections require "
                    "reasonable mobility."
                ),
            },
            {
                "question": "Is the experience private?",
                "answer": (
                    "The standard option is small-group. A private option "
                    "is also available."
                ),
            },
        ],

        "tags": [
            "Beijing",
            "China",
            "Great Wall",
            "Imperial China",
            "Heritage",
            "Old City",
            "Culture",
        ],

        "signature_moments": [
            {
                "title": "The Great Wall Horizon",
                "description": (
                    "Standing above the landscape as the Great Wall "
                    "disappears across the surrounding mountains."
                ),
            },
            {
                "title": "Old Beijing",
                "description": (
                    "Discovering the quieter character of traditional "
                    "Beijing beyond its major avenues."
                ),
            },
        ],
    },


    # ------------------------------------------------------------------------
    # 02 — SHANGHAI
    # ------------------------------------------------------------------------

    {
        "code": "CHI-SHA-001",
        "title": (
            "Shanghai Bund, Old Town & Modern City Experience"
        ),
        "slug": (
            "shanghai-bund-old-town-modern-city-experience"
        ),
        "short_description": (
            "A sophisticated Shanghai discovery connecting the historic "
            "Bund and Old Town with the city's modern skyline and urban energy."
        ),
        "description": (
            "Experience Shanghai as a meeting point between historic China "
            "and one of Asia's most dynamic modern cities. Explore the Bund, "
            "historic streets and traditional neighbourhood character before "
            "seeing the contemporary skyline and the districts that define "
            "Shanghai today."
        ),
        "duration": "6–7 hours",
        "meeting_point": (
            "Central Shanghai hotel or agreed city meeting point"
        ),
        "location": "Shanghai, China",
        "price_from": Decimal("110.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 702,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "shanghai",
        "seo_title": (
            "Shanghai Bund, Old Town & Modern City Experience"
        ),
        "seo_description": (
            "Discover Shanghai's Bund, historic Old Town, modern skyline "
            "and evolving urban identity on a curated city experience."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("110.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("155.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "The Bund",
                "description": (
                    "Begin along Shanghai's iconic waterfront and explore "
                    "the historic architecture facing the Huangpu River."
                ),
            },
            {
                "title": "Historic Shanghai",
                "description": (
                    "Continue into selected historic streets and neighbourhoods "
                    "to understand the city's older commercial and cultural life."
                ),
            },
            {
                "title": "Modern Shanghai",
                "description": (
                    "Discover the contrast between Shanghai's historic "
                    "districts and its contemporary skyline."
                ),
            },
            {
                "title": "Skyline & City Life",
                "description": (
                    "Finish with time to appreciate Shanghai's urban energy "
                    "and selected panoramic views."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Shanghai city experience",
            "Bund waterfront discovery",
            "Historic neighbourhood exploration",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Paid observation deck admissions",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Walk the historic Bund",
            "Discover Shanghai's older neighbourhoods",
            "See the contrast between historic and modern architecture",
            "Experience the city's contemporary skyline",
            "Understand Shanghai's transformation into a global city",
        ],

        "addons": [
            {
                "title": "Shanghai Skyline Observation",
                "description": (
                    "Add admission to a selected skyline observation "
                    "experience where available."
                ),
            },
            {
                "title": "Shanghai Food Discovery",
                "description": (
                    "Add a curated tasting of selected Shanghai dishes "
                    "and local specialities."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Light weather-appropriate clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
        ],

        "safety_rules": [
            "Stay with the host in busy public areas.",
            "Keep valuables secure in crowded districts.",
            "Follow road-crossing instructions.",
        ],

        "requirements": [
            "Guests should be comfortable with urban walking.",
            "Some attractions may require separate admission.",
        ],

        "faqs": [
            {
                "question": "Is this mainly a shopping tour?",
                "answer": (
                    "No. The experience focuses on Shanghai's history, "
                    "architecture, culture and modern city identity."
                ),
            },
            {
                "question": "Can this be private?",
                "answer": (
                    "Yes. A private option is available."
                ),
            },
            {
                "question": "Is it family-friendly?",
                "answer": (
                    "Yes. The experience is suitable for families."
                ),
            },
        ],

        "tags": [
            "Shanghai",
            "China",
            "Bund",
            "Old Town",
            "Skyline",
            "Architecture",
            "City Discovery",
        ],

        "signature_moments": [
            {
                "title": "The Bund Panorama",
                "description": (
                    "Taking in the contrast between Shanghai's historic "
                    "waterfront architecture and its modern skyline."
                ),
            },
            {
                "title": "Old Meets New",
                "description": (
                    "Moving from traditional neighbourhoods into the "
                    "energy of contemporary Shanghai."
                ),
            },
        ],
    },


    # ------------------------------------------------------------------------
    # 03 — HONG KONG
    # ------------------------------------------------------------------------

    {
        "code": "CHI-HKG-001",
        "title": (
            "Hong Kong Victoria Harbour, Markets & Island Culture"
        ),
        "slug": (
            "hong-kong-victoria-harbour-markets-island-culture"
        ),
        "short_description": (
            "A vibrant Hong Kong experience combining Victoria Harbour, "
            "historic markets, neighbourhood life and the city's island character."
        ),
        "description": (
            "Discover Hong Kong beyond the postcard skyline through a "
            "carefully curated journey across harbourfront landmarks, "
            "traditional markets and neighbourhoods where local life continues "
            "alongside the city's financial and commercial energy."
        ),
        "duration": "6–7 hours",
        "meeting_point": (
            "Central Hong Kong hotel or agreed city meeting point"
        ),
        "location": "Hong Kong, China",
        "price_from": Decimal("120.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 703,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "hong-kong",
        "seo_title": (
            "Hong Kong Victoria Harbour, Markets & Island Culture"
        ),
        "seo_description": (
            "Explore Victoria Harbour, historic markets and Hong Kong "
            "neighbourhood life on a curated island culture experience."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("120.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("170.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "Victoria Harbour",
                "description": (
                    "Begin with a guided introduction to Hong Kong's "
                    "world-famous harbour and skyline."
                ),
            },
            {
                "title": "Historic Districts",
                "description": (
                    "Explore selected streets and neighbourhoods where "
                    "historic architecture meets contemporary city life."
                ),
            },
            {
                "title": "Markets & Local Life",
                "description": (
                    "Discover a traditional market setting and learn about "
                    "everyday commerce, food and neighbourhood culture."
                ),
            },
            {
                "title": "Island City Finale",
                "description": (
                    "Conclude with a curated harbour or skyline viewpoint "
                    "before returning to the central city."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Hong Kong cultural experience",
            "Victoria Harbour discovery",
            "Market and neighbourhood exploration",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Optional attraction admissions",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Experience Victoria Harbour",
            "Explore Hong Kong's historic neighbourhoods",
            "Discover traditional market culture",
            "See the contrast between local life and global finance",
            "Understand Hong Kong's unique urban identity",
        ],

        "addons": [
            {
                "title": "Harbour Cruise Extension",
                "description": (
                    "Extend the experience with a selected harbour cruise "
                    "where available."
                ),
            },
            {
                "title": "Hong Kong Food Tasting",
                "description": (
                    "Add a curated tasting of selected local dishes."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Light weather-appropriate clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
        ],

        "safety_rules": [
            "Stay with the host in crowded areas.",
            "Keep valuables secure around markets and transport hubs.",
            "Follow pedestrian and public transport safety instructions.",
            "Stay hydrated during warm-weather walking.",
        ],

        "requirements": [
            "Guests should be comfortable with urban walking.",
            "Some sections may involve stairs or uneven pavements.",
        ],

        "faqs": [
            {
                "question": "Will we visit the famous harbourfront?",
                "answer": (
                    "Yes. Victoria Harbour forms a central part of the "
                    "experience."
                ),
            },
            {
                "question": "Is this suitable for families?",
                "answer": (
                    "Yes. Families are welcome."
                ),
            },
            {
                "question": "Can we add food tasting?",
                "answer": (
                    "Yes. A food-tasting add-on is available."
                ),
            },
        ],

        "tags": [
            "Hong Kong",
            "China",
            "Victoria Harbour",
            "Markets",
            "Local Life",
            "Culture",
            "City Discovery",
        ],

        "signature_moments": [
            {
                "title": "Harbour Lights",
                "description": (
                    "Taking in Hong Kong's dramatic skyline across "
                    "Victoria Harbour."
                ),
            },
            {
                "title": "The Local Hong Kong",
                "description": (
                    "Discovering neighbourhood life beyond the city's "
                    "famous financial skyline."
                ),
            },
        ],
    },


    # ------------------------------------------------------------------------
    # 04 — XI'AN
    # ------------------------------------------------------------------------

    {
        "code": "CHI-XIA-001",
        "title": (
            "Xi'an Terracotta Army, Ancient City & Silk Road Discovery"
        ),
        "slug": (
            "xian-terracotta-army-ancient-city-silk-road-discovery"
        ),
        "short_description": (
            "A deep cultural journey through Xi'an's ancient capital heritage, "
            "the Terracotta Army, historic city walls and Silk Road legacy."
        ),
        "description": (
            "Explore Xi'an, one of China's great ancient capitals, through "
            "the extraordinary Terracotta Army, historic city walls, old "
            "neighbourhoods and the cultural traditions that developed along "
            "the Silk Road. The experience combines archaeology, architecture "
            "and food culture into a rich introduction to the city."
        ),
        "duration": "8–10 hours",
        "meeting_point": (
            "Central Xi'an hotel or agreed city meeting point"
        ),
        "location": "Xi'an, Shaanxi, China",
        "price_from": Decimal("135.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy to Moderate",
        "featured": True,
        "active": True,
        "display_order": 704,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "xian",
        "seo_title": (
            "Xi'an Terracotta Army, Ancient City & Silk Road Discovery"
        ),
        "seo_description": (
            "Discover Xi'an's Terracotta Army, ancient city heritage, "
            "Silk Road history and local culture."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("135.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("190.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "Xi'an Orientation",
                "description": (
                    "Meet your host and begin with an introduction to "
                    "Xi'an's importance as an ancient Chinese capital."
                ),
            },
            {
                "title": "Terracotta Army",
                "description": (
                    "Explore the archaeological site associated with "
                    "China's first emperor and learn about its extraordinary "
                    "historical significance."
                ),
            },
            {
                "title": "Ancient City Walls",
                "description": (
                    "Continue to the historic city wall and discover how "
                    "Xi'an's fortified urban structure shaped the city."
                ),
            },
            {
                "title": "Silk Road & Local Flavours",
                "description": (
                    "Finish with stories of the Silk Road and time around "
                    "Xi'an's distinctive food and cultural traditions."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Xi'an heritage experience",
            "Terracotta Army discovery",
            "Ancient city heritage exploration",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Entry fees unless specifically included",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Discover the Terracotta Army",
            "Explore Xi'an's ancient city heritage",
            "Learn about the Silk Road",
            "Experience the city's distinctive food culture",
            "Understand Xi'an's importance in Chinese history",
        ],

        "addons": [
            {
                "title": "Private Archaeology Extension",
                "description": (
                    "Add additional guided interpretation around "
                    "Xi'an's archaeological heritage."
                ),
            },
            {
                "title": "Xi'an Food Discovery",
                "description": (
                    "Add a curated tasting of selected local dishes "
                    "and traditional street-food favourites."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Sun protection",
            "Weather-appropriate layers",
            "Reusable water bottle",
            "Small day bag",
        ],

        "safety_rules": [
            "Remain with the host at major archaeological sites.",
            "Follow museum and heritage-site rules.",
            "Stay hydrated during extended walking.",
            "Keep valuables secure in busy areas.",
        ],

        "requirements": [
            "Guests should be comfortable with a full day of walking.",
            "Some historic surfaces may be uneven.",
        ],

        "faqs": [
            {
                "question": "Is the Terracotta Army included?",
                "answer": (
                    "The experience includes the curated visit, while "
                    "specific entrance arrangements depend on the selected "
                    "option."
                ),
            },
            {
                "question": "Is Xi'an suitable for families?",
                "answer": (
                    "Yes. The experience is suitable for families."
                ),
            },
            {
                "question": "What food will we try?",
                "answer": (
                    "The optional food discovery focuses on selected "
                    "Xi'an specialities and local street-food traditions."
                ),
            },
        ],

        "tags": [
            "Xi'an",
            "China",
            "Terracotta Army",
            "Silk Road",
            "Ancient China",
            "Heritage",
            "Food",
        ],

        "signature_moments": [
            {
                "title": "The Terracotta Army",
                "description": (
                    "Standing before the remarkable archaeological legacy "
                    "of China's first emperor."
                ),
            },
            {
                "title": "Ancient Xi'an",
                "description": (
                    "Walking through the historic city and imagining its "
                    "role as a gateway between China and the wider world."
                ),
            },
        ],
    },


    # ------------------------------------------------------------------------
    # 05 — CHONGQING
    # ------------------------------------------------------------------------

    {
        "code": "CHI-CQ-001",
        "title": (
            "Chongqing Mountain City, Yangtze & Night Lights Experience"
        ),
        "slug": (
            "chongqing-mountain-city-yangtze-night-lights-experience"
        ),
        "short_description": (
            "A dramatic Chongqing experience exploring layered streets, "
            "river landscapes, historic districts and the city's famous night views."
        ),
        "description": (
            "Discover Chongqing as one of China's most visually distinctive "
            "cities. Built across hills and river valleys, the city reveals "
            "itself through elevated streets, dramatic bridges, historic "
            "neighbourhoods, riverfront districts and unforgettable evening "
            "views."
        ),
        "duration": "6–7 hours",
        "meeting_point": (
            "Central Chongqing hotel or agreed city meeting point"
        ),
        "location": "Chongqing, China",
        "price_from": Decimal("105.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Moderate",
        "featured": False,
        "active": True,
        "display_order": 705,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "chongqing",
        "seo_title": (
            "Chongqing Mountain City, Yangtze & Night Lights Experience"
        ),
        "seo_description": (
            "Explore Chongqing's mountain cityscape, river views, historic "
            "districts and famous night scenery."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("105.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("150.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "Mountain City Orientation",
                "description": (
                    "Meet your host and begin discovering Chongqing's "
                    "unusual vertical geography and layered urban landscape."
                ),
            },
            {
                "title": "Historic Chongqing",
                "description": (
                    "Explore selected historic streets and neighbourhoods "
                    "shaped by the city's mountain terrain."
                ),
            },
            {
                "title": "Yangtze & Riverfront",
                "description": (
                    "Discover the meeting point of the Yangtze and Jialing "
                    "rivers and the role waterways play in Chongqing's identity."
                ),
            },
            {
                "title": "Night Lights",
                "description": (
                    "Finish with a carefully selected evening viewpoint "
                    "showcasing Chongqing's extraordinary illuminated skyline."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Chongqing city experience",
            "Historic neighbourhood discovery",
            "Riverfront and skyline viewpoints",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Optional cruise admissions",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Explore Chongqing's mountain-city geography",
            "See the Yangtze and Jialing rivers",
            "Discover historic hillside neighbourhoods",
            "Experience Chongqing's famous night skyline",
            "Learn about the city's distinctive urban identity",
        ],

        "addons": [
            {
                "title": "Yangtze River Cruise",
                "description": (
                    "Add a selected river cruise experience where "
                    "operating conditions permit."
                ),
            },
            {
                "title": "Chongqing Hotpot Discovery",
                "description": (
                    "Add a curated introduction to Chongqing's famous "
                    "hotpot culture."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Light weather-appropriate clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
        ],

        "safety_rules": [
            "Take care on steep streets and stairways.",
            "Follow host instructions around roads and viewpoints.",
            "Stay with the group in busy areas.",
            "Keep valuables secure.",
        ],

        "requirements": [
            "Guests should be comfortable with hills, stairs and uneven streets.",
            "Evening conditions may affect selected viewpoints.",
        ],

        "faqs": [
            {
                "question": "Why is Chongqing called a mountain city?",
                "answer": (
                    "The city is built across steep hills and river valleys, "
                    "creating its distinctive layered streets and skyline."
                ),
            },
            {
                "question": "Can we add a river cruise?",
                "answer": (
                    "Yes. A river-cruise add-on is available where "
                    "operating conditions permit."
                ),
            },
            {
                "question": "Is the experience suitable for older guests?",
                "answer": (
                    "It can be, provided guests are comfortable with "
                    "stairs, hills and uneven urban surfaces."
                ),
            },
        ],

        "tags": [
            "Chongqing",
            "China",
            "Yangtze",
            "Mountain City",
            "Night Views",
            "Architecture",
            "Local Life",
        ],

        "signature_moments": [
            {
                "title": "The Layered City",
                "description": (
                    "Seeing roads, buildings, bridges and neighbourhoods "
                    "rise dramatically across the mountain landscape."
                ),
            },
            {
                "title": "Chongqing After Dark",
                "description": (
                    "Watching the mountain city transform into a spectacular "
                    "field of lights after sunset."
                ),
            },
        ],
    },


    # ------------------------------------------------------------------------
    # 06 — CHENGDU
    # ------------------------------------------------------------------------

    {
        "code": "CHI-CD-001",
        "title": (
            "Chengdu Pandas, Teahouses & Sichuan Culture Experience"
        ),
        "slug": (
            "chengdu-pandas-teahouses-sichuan-culture-experience"
        ),
        "short_description": (
            "A relaxed Chengdu experience combining giant panda conservation, "
            "traditional teahouse culture and the flavours of Sichuan."
        ),
        "description": (
            "Discover Chengdu through the experiences that define its character: "
            "giant panda conservation, relaxed teahouse culture, historic "
            "neighbourhoods and Sichuan cuisine. The experience connects "
            "wildlife conservation with everyday local life, creating a more "
            "complete introduction to one of southwest China's most distinctive cities."
        ),
        "duration": "7–8 hours",
        "meeting_point": (
            "Central Chengdu hotel or agreed city meeting point"
        ),
        "location": "Chengdu, Sichuan, China",
        "price_from": Decimal("115.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": True,
        "active": True,
        "display_order": 706,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "chengdu",
        "seo_title": (
            "Chengdu Pandas, Teahouses & Sichuan Culture Experience"
        ),
        "seo_description": (
            "Discover Chengdu's giant pandas, traditional teahouses, "
            "Sichuan culture and local food traditions."
        ),

        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("115.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("165.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],

        "itinerary": [
            {
                "title": "Panda Conservation",
                "description": (
                    "Begin with a curated visit focused on giant panda "
                    "conservation, research and the importance of protecting "
                    "the species."
                ),
            },
            {
                "title": "Chengdu Neighbourhoods",
                "description": (
                    "Continue into selected historic or cultural districts "
                    "to experience the city's relaxed everyday rhythm."
                ),
            },
            {
                "title": "Traditional Teahouse",
                "description": (
                    "Experience Chengdu's famous teahouse culture and learn "
                    "why tea remains central to local social life."
                ),
            },
            {
                "title": "Sichuan Flavours",
                "description": (
                    "Finish with an optional introduction to Sichuan cuisine "
                    "and its distinctive flavours."
                ),
            },
        ],

        "inclusions": [
            "Professional local experience host",
            "Curated Chengdu cultural experience",
            "Panda conservation experience",
            "Traditional teahouse discovery",
            "Small-group or private format according to selected option",
        ],

        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Attraction admissions unless specifically included",
            "Travel insurance",
            "Personal shopping",
            "Personal expenses",
        ],

        "highlights": [
            "Discover giant panda conservation",
            "Experience Chengdu's traditional teahouse culture",
            "Explore historic neighbourhoods",
            "Learn about Sichuan food traditions",
            "Experience the relaxed rhythm of Chengdu",
        ],

        "addons": [
            {
                "title": "Sichuan Food Discovery",
                "description": (
                    "Add a curated tasting of selected Sichuan dishes "
                    "and regional specialities."
                ),
            },
            {
                "title": "Private Cultural Evening",
                "description": (
                    "Extend the experience with an evening exploration "
                    "of Chengdu's cultural and food scene."
                ),
            },
        ],

        "packing_items": [
            "Comfortable walking shoes",
            "Light weather-appropriate clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
            "Camera or phone",
        ],

        "safety_rules": [
            "Follow all panda facility rules.",
            "Do not feed or touch wildlife unless specifically permitted.",
            "Respect quiet zones and conservation guidelines.",
            "Stay hydrated during outdoor walking.",
        ],

        "requirements": [
            "Guests should be comfortable with moderate walking.",
            "Panda sightings and animal activity cannot be guaranteed.",
            "Children must be accompanied by an adult.",
        ],

        "faqs": [
            {
                "question": "Will we definitely see pandas?",
                "answer": (
                    "The experience is designed around panda conservation "
                    "facilities, but animal activity and visibility cannot "
                    "be guaranteed."
                ),
            },
            {
                "question": "Is this suitable for children?",
                "answer": (
                    "Yes. It is suitable for families."
                ),
            },
            {
                "question": "Is Sichuan food very spicy?",
                "answer": (
                    "Sichuan cuisine is known for bold flavours and chilli, "
                    "but food selections can be adapted to guest preferences."
                ),
            },
        ],

        "tags": [
            "Chengdu",
            "China",
            "Pandas",
            "Conservation",
            "Sichuan",
            "Teahouses",
            "Food",
            "Culture",
        ],

        "signature_moments": [
            {
                "title": "Panda Country",
                "description": (
                    "Seeing Chengdu's conservation work up close and "
                    "understanding the importance of protecting giant pandas."
                ),
            },
            {
                "title": "Tea in Chengdu",
                "description": (
                    "Slowing down over traditional tea and experiencing "
                    "one of Chengdu's defining social traditions."
                ),
            },
        ],
    },
]


# ============================================================================
# MODEL / FIELD HELPERS
# ============================================================================

def model_column_names(model_class) -> set[str]:
    return {
        column.name
        for column in model_class.__table__.columns
    }


def set_supported_fields(
    obj: Any,
    values: dict[str, Any],
) -> Any:

    columns = model_column_names(type(obj))

    for key, value in values.items():
        if key in columns and value is not None:
            setattr(obj, key, value)

    return obj


def get_relationship_model(
    parent_model,
    relationship_name: str,
):
    relationship = (
        parent_model.__mapper__.relationships.get(
            relationship_name
        )
    )

    if relationship is None:
        return None

    return relationship.mapper.class_


# ============================================================================
# SLUG HELPER
# ============================================================================

def slugify(value: str) -> str:
    value = str(value or "").strip().lower()

    value = value.replace("&", " and ")
    value = value.replace("'", "")

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    value = re.sub(
        r"-+",
        "-",
        value,
    )

    return value.strip("-")


# ============================================================================
# PRICING
# ============================================================================

def add_pricing(
    parent,
    rows: list[dict[str, Any]],
) -> int:

    relationship = (
        type(parent).__mapper__.relationships.get(
            "pricing"
        )
    )

    if relationship is None:
        return 0

    pricing_model = relationship.mapper.class_
    collection = getattr(parent, "pricing")
    columns = model_column_names(pricing_model)

    parent_currency = (
        getattr(parent, "currency", None)
        or SUPPORTED_CURRENCY
    )

    created = 0

    for index, row in enumerate(rows):

        obj = pricing_model()

        experience_level = (
            row.get("experience_level")
            or row.get("label")
            or row.get("level")
            or row.get("title")
            or row.get("name")
        )

        price = (
            row.get("price")
            if row.get("price") is not None
            else row.get("amount")
        )

        minimum_people = (
            row.get("minimum_people")
            if row.get("minimum_people") is not None
            else row.get("minimum_guests", 1)
        )

        maximum_people = (
            row.get("maximum_people")
            if row.get("maximum_people") is not None
            else row.get("maximum_guests")
        )

        notes = row.get("notes")

        if not notes and row.get("basis"):
            notes = str(row["basis"])

        currency = (
            row.get("currency")
            or parent_currency
        )

        values = {
            "experience_level": experience_level,
            "minimum_people": minimum_people,
            "maximum_people": maximum_people,
            "price": price,
            "currency": currency,
            "notes": notes,
            "display_order": row.get(
                "display_order",
                index,
            ),
            "active": row.get(
                "active",
                True,
            ),
        }

        for key, value in values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        if (
            "experience_level" in columns
            and not getattr(
                obj,
                "experience_level",
                None,
            )
        ):
            raise RuntimeError(
                f"Experience pricing level is required for "
                f"{parent.experience_code}."
            )

        if (
            "price" in columns
            and getattr(obj, "price", None) is None
        ):
            raise RuntimeError(
                f"Experience pricing amount is required for "
                f"{parent.experience_code}."
            )

        if (
            "currency" in columns
            and getattr(obj, "currency", None)
            != parent_currency
        ):
            raise RuntimeError(
                f"Pricing currency mismatch for "
                f"{parent.experience_code}: "
                f"expected {parent_currency}, "
                f"got {getattr(obj, 'currency', None)}."
            )

        collection.append(obj)
        created += 1

    return created


# ============================================================================
# ADD-ONS
# ============================================================================

def add_addons(
    parent,
    rows: list[dict[str, Any]],
) -> int:

    relationship = (
        type(parent).__mapper__.relationships.get(
            "addons"
        )
    )

    if relationship is None:
        return 0

    addon_model = relationship.mapper.class_
    collection = getattr(parent, "addons")
    columns = model_column_names(addon_model)

    parent_currency = (
        getattr(parent, "currency", None)
        or SUPPORTED_CURRENCY
    )

    created = 0

    for index, row in enumerate(rows):

        name = (
            row.get("name")
            or row.get("title")
        )

        if not name:
            raise RuntimeError(
                f"Experience add-on name is required for "
                f"{parent.experience_code}."
            )

        description = (
            row.get("description")
            or row.get("short_description")
            or ""
        )

        values = {
            "name": str(name).strip(),
            "description": description,
            "short_description": description,
            "price": row.get(
                "price",
                Decimal("0.00"),
            ),
            "currency": parent_currency,
            "pricing_type": row.get(
                "pricing_type",
                "Per Person",
            ),
            "optional": row.get(
                "optional",
                True,
            ),
            "available_online": row.get(
                "available_online",
                True,
            ),
            "active": row.get(
                "active",
                True,
            ),
            "display_order": row.get(
                "display_order",
                index,
            ),
        }

        obj = addon_model()

        for key, value in values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        if (
            "name" in columns
            and not getattr(obj, "name", None)
        ):
            raise RuntimeError(
                f"Could not populate required "
                f"experience_addons.name for "
                f"{parent.experience_code}."
            )

        if (
            "currency" in columns
            and getattr(obj, "currency", None)
            != parent_currency
        ):
            raise RuntimeError(
                f"Add-on currency mismatch for "
                f"{parent.experience_code}."
            )

        collection.append(obj)
        created += 1

    return created


# ============================================================================
# TAGS
# ============================================================================

def add_tags(
    parent,
    rows: list[str],
) -> int:

    relationship = (
        type(parent).__mapper__.relationships.get(
            "tags"
        )
    )

    if relationship is None:
        return 0

    tag_model = relationship.mapper.class_
    collection = getattr(parent, "tags")
    columns = model_column_names(tag_model)

    created_or_attached = 0

    for index, row in enumerate(rows):

        if isinstance(row, str):
            tag_name = row.strip()
            supplied_slug = None

        elif isinstance(row, dict):
            tag_name = (
                row.get("name")
                or row.get("label")
                or row.get("title")
            )
            supplied_slug = row.get("slug")

        else:
            raise RuntimeError(
                f"Unsupported tag row type for "
                f"{parent.experience_code}."
            )

        if not tag_name:
            raise RuntimeError(
                f"Tag name is required for "
                f"{parent.experience_code}."
            )

        tag_name = str(tag_name).strip()

        tag_slug = (
            supplied_slug
            or slugify(tag_name)
        )

        if not tag_slug:
            raise RuntimeError(
                f"Could not generate tag slug for "
                f"{parent.experience_code}: "
                f"{tag_name}"
            )

        existing = None

        if "slug" in columns:
            existing = (
                db.session.query(tag_model)
                .filter(
                    tag_model.slug == tag_slug
                )
                .first()
            )

        if (
            existing is None
            and "name" in columns
        ):
            existing = (
                db.session.query(tag_model)
                .filter(
                    tag_model.name == tag_name
                )
                .first()
            )

        if existing is not None:
            collection.append(existing)
            created_or_attached += 1
            continue

        tag = tag_model()

        values = {
            "name": tag_name,
            "slug": tag_slug,
            "color": "#10B981",
            "featured": False,
            "active": True,
            "sort_order": index,
        }

        set_supported_fields(
            tag,
            values,
        )

        if (
            "name" in columns
            and not getattr(tag, "name", None)
        ):
            raise RuntimeError(
                f"Could not populate tags.name for "
                f"{parent.experience_code}."
            )

        if (
            "slug" in columns
            and not getattr(tag, "slug", None)
        ):
            raise RuntimeError(
                f"Could not populate tags.slug for "
                f"{parent.experience_code}."
            )

        collection.append(tag)
        created_or_attached += 1

    return created_or_attached


# ============================================================================
# GENERIC CHILD RECORDS
# ============================================================================

def add_related(
    parent,
    relationship_name: str,
    rows: list[dict[str, Any]],
) -> int:

    relationship = (
        type(parent).__mapper__.relationships.get(
            relationship_name
        )
    )

    if relationship is None:
        return 0

    related_model = relationship.mapper.class_
    collection = getattr(parent, relationship_name)

    created = 0

    for index, row in enumerate(rows):

        normalized = dict(row)

        normalized.setdefault(
            "display_order",
            index,
        )

        normalized.setdefault(
            "sort_order",
            index,
        )

        normalized.setdefault(
            "active",
            True,
        )

        obj = related_model()

        set_supported_fields(
            obj,
            normalized,
        )

        collection.append(obj)
        created += 1

    return created


def add_text_children(
    parent,
    relationship_name: str,
    rows: list[str],
) -> int:

    relationship = (
        type(parent).__mapper__.relationships.get(
            relationship_name
        )
    )

    if relationship is None:
        return 0

    related_model = relationship.mapper.class_
    columns = model_column_names(related_model)
    collection = getattr(parent, relationship_name)

    created = 0

    for index, text in enumerate(rows):

        obj = related_model()

        values = {
            "title": text,
            "name": text,
            "description": text,
            "display_order": index,
            "sort_order": index,
            "active": True,
        }

        for key, value in values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        collection.append(obj)
        created += 1

    return created


# ============================================================================
# DESTINATION / CATEGORY
# ============================================================================

def find_destination(slug: str):

    destination_model = get_relationship_model(
        Experience,
        "destination",
    )

    if destination_model is None:
        raise RuntimeError(
            "Could not resolve Experience.destination."
        )

    destination = (
        destination_model.query
        .filter_by(slug=slug)
        .first()
    )

    if destination is None:
        raise RuntimeError(
            f"Required destination does not exist: {slug}"
        )

    return destination


def find_category(slug: str):

    category_model = get_relationship_model(
        Experience,
        "category",
    )

    if category_model is None:
        raise RuntimeError(
            "Could not resolve Experience.category."
        )

    normalized_slug = (
        slug or ""
    ).strip().lower()

    if not normalized_slug:
        raise RuntimeError(
            "Experience category slug cannot be empty."
        )

    category = (
        category_model.query
        .filter_by(slug=normalized_slug)
        .first()
    )

    if category is None:
        raise RuntimeError(
            f"Required experience category does not exist: "
            f"{normalized_slug}"
        )

    return category


# ============================================================================
# DUPLICATE PROTECTION
# ============================================================================

def duplicate_exists(
    code: str,
    slug: str,
) -> bool:

    by_code = (
        Experience.query
        .filter_by(
            experience_code=code
        )
        .first()
    )

    if by_code:
        return True

    by_slug = (
        Experience.query
        .filter_by(
            slug=slug
        )
        .first()
    )

    return by_slug is not None


# ============================================================================
# EXPERIENCE CREATION
# ============================================================================

def create_experience(
    data: dict[str, Any],
):

    destination = find_destination(
        data["destination_slug"]
    )

    category = find_category(
        data["category_slug"]
    )

    experience = Experience()

    base_fields = {
        "experience_code": data["code"],
        "title": data["title"],
        "slug": data["slug"],
        "short_description": data["short_description"],
        "description": data["description"],
        "duration": data["duration"],
        "meeting_point": data["meeting_point"],
        "location": data["location"],
        "price_from": data["price_from"],
        "currency": SUPPORTED_CURRENCY,
        "group_size": data["group_size"],
        "age_range": data["age_range"],
        "difficulty": data["difficulty"],
        "featured": data["featured"],
        "active": data["active"],
        "display_order": data["display_order"],
        "seo_title": data["seo_title"],
        "seo_description": data["seo_description"],
        "featured_image": DEFAULT_FEATURED_IMAGE,
    }

    set_supported_fields(
        experience,
        base_fields,
    )

    experience_columns = model_column_names(
        Experience
    )

    if "destination_id" in experience_columns:
        experience.destination_id = destination.id

    if "category_id" in experience_columns:
        experience.category_id = category.id

    db.session.add(experience)

    db.session.flush()

    # Pricing
    add_pricing(
        experience,
        data["pricing"],
    )

    # Itinerary
    add_related(
        experience,
        "itinerary",
        data["itinerary"],
    )

    # Inclusions
    add_text_children(
        experience,
        "inclusions",
        data["inclusions"],
    )

    # Exclusions
    add_text_children(
        experience,
        "exclusions",
        data["exclusions"],
    )

    # Highlights
    add_text_children(
        experience,
        "highlights",
        data["highlights"],
    )

    # Add-ons
    add_addons(
        experience,
        data["addons"],
    )

    # Packing
    add_text_children(
        experience,
        "packing_items",
        data["packing_items"],
    )

    # Safety
    add_text_children(
        experience,
        "safety_rules",
        data["safety_rules"],
    )

    # Requirements
    add_text_children(
        experience,
        "requirements",
        data["requirements"],
    )

    # FAQs
    add_related(
        experience,
        "faqs",
        data["faqs"],
    )

    # Tags
    add_tags(
        experience,
        data["tags"],
    )

    # Signature moments
    add_related(
        experience,
        "signature_moments",
        data["signature_moments"],
    )

    return experience


# ============================================================================
# RELATIONSHIP VERIFICATION
# ============================================================================

def relationship_count(
    obj,
    relationship_name: str,
) -> int:

    relationship = getattr(
        obj,
        relationship_name,
        None,
    )

    if relationship is None:
        return 0

    count_method = getattr(
        relationship,
        "count",
        None,
    )

    if callable(count_method):
        try:
            return count_method()
        except TypeError:
            pass

    try:
        return len(relationship)
    except TypeError:
        return 0


def verify_experience(
    experience,
) -> dict[str, int]:

    return {
        "pricing": relationship_count(
            experience,
            "pricing",
        ),
        "itinerary": relationship_count(
            experience,
            "itinerary",
        ),
        "inclusions": relationship_count(
            experience,
            "inclusions",
        ),
        "exclusions": relationship_count(
            experience,
            "exclusions",
        ),
        "highlights": relationship_count(
            experience,
            "highlights",
        ),
        "addons": relationship_count(
            experience,
            "addons",
        ),
        "packing_items": relationship_count(
            experience,
            "packing_items",
        ),
        "safety_rules": relationship_count(
            experience,
            "safety_rules",
        ),
        "requirements": relationship_count(
            experience,
            "requirements",
        ),
        "faqs": relationship_count(
            experience,
            "faqs",
        ),
        "tags": relationship_count(
            experience,
            "tags",
        ),
        "signature_moments": relationship_count(
            experience,
            "signature_moments",
        ),
        "media": relationship_count(
            experience,
            "media",
        ),
        "schedules": relationship_count(
            experience,
            "schedules",
        ),
        "bookings": relationship_count(
            experience,
            "bookings",
        ),
    }


def print_verification(
    code: str,
    checks: dict[str, int],
):

    print(
        f"\n  Verification: {code}"
    )

    for key, value in checks.items():
        print(
            f"    {key:<20} {value}"
        )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_batch_data():

    print("Validating batch data...")

    codes = [
        item["code"]
        for item in EXPERIENCES
    ]

    slugs = [
        item["slug"]
        for item in EXPERIENCES
    ]

    if len(codes) != len(set(codes)):
        raise RuntimeError(
            "Duplicate experience code inside Batch 7."
        )

    if len(slugs) != len(set(slugs)):
        raise RuntimeError(
            "Duplicate experience slug inside Batch 7."
        )

    for item in EXPERIENCES:

        if item["currency"] != SUPPORTED_CURRENCY:
            raise RuntimeError(
                f"{item['code']} must use USD."
            )

        if (
            Decimal(str(item["price_from"]))
            <= Decimal("0")
        ):
            raise RuntimeError(
                f"{item['code']} has invalid price_from."
            )

        for price in item["pricing"]:

            if price["currency"] != SUPPORTED_CURRENCY:
                raise RuntimeError(
                    f"{item['code']} contains non-USD pricing."
                )

            if (
                Decimal(str(price["amount"]))
                <= Decimal("0")
            ):
                raise RuntimeError(
                    f"{item['code']} contains invalid pricing."
                )

    print("Batch data validated.")
    print("Currency validation: USD.")
    print("Duplicate protection validated.")


def validate_destinations():

    required = sorted(
        {
            item["destination_slug"]
            for item in EXPERIENCES
        }
    )

    print(
        "\nRequired existing destinations:"
    )

    for slug in required:

        destination = find_destination(
            slug
        )

        name = (
            getattr(
                destination,
                "name",
                None,
            )
            or slug
        )

        print(
            f"  ✓ {name} ({slug})"
        )


def validate_categories():

    required = sorted(
        {
            item["category_slug"]
            for item in EXPERIENCES
        }
    )

    print(
        "\nRequired existing experience categories:"
    )

    for slug in required:

        category = find_category(
            slug
        )

        name = (
            getattr(
                category,
                "name",
                None,
            )
            or getattr(
                category,
                "title",
                None,
            )
            or slug
        )

        print(
            f"  ✓ {name} ({slug})"
        )


def validate_existing_records():

    duplicates = []

    for item in EXPERIENCES:

        if duplicate_exists(
            item["code"],
            item["slug"],
        ):
            duplicates.append(
                f"{item['code']} / {item['slug']}"
            )

    if duplicates:

        print(
            "\nDuplicate records detected:"
        )

        for duplicate in duplicates:
            print(
                f"  - {duplicate}"
            )

        raise RuntimeError(
            "Batch 7 contains existing experience records. "
            "No records will be modified."
        )

    print(
        "\nNo existing Batch 7 experience duplicates found."
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Populate THE UNCHARTED ROUTE Batch 7."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit Batch 7 to the database.",
    )

    args = parser.parse_args()

    app = create_app()

    with app.app_context():

        print()
        print("=" * 110)
        print(
            f"THE UNCHARTED ROUTE — {BATCH_NAME}"
        )
        print("=" * 110)
        print(
            f"Experiences in batch: "
            f"{len(EXPERIENCES)}"
        )
        print(
            "Mode: "
            f"{'APPLY — COMMIT' if args.apply else 'DRY RUN'}"
        )
        print("=" * 110)

        try:

            validate_batch_data()
            validate_destinations()
            validate_categories()
            validate_existing_records()

            print(
                "\n" + "=" * 110
            )
            print("EXPERIENCE PLAN")
            print("=" * 110)

            for index, item in enumerate(
                EXPERIENCES,
                start=1,
            ):

                print(
                    f"\n[{index:02d}/{len(EXPERIENCES)}] "
                    f"{item['code']} — "
                    f"{item['title']}"
                )

                print(
                    f"    Destination : "
                    f"{item['destination_slug']}"
                )

                print(
                    f"    Category    : "
                    f"{item['category_slug']}"
                )

                print(
                    f"    Price       : "
                    f"USD {item['price_from']:.2f} "
                    f"per person"
                )

                print(
                    f"    Duration    : "
                    f"{item['duration']}"
                )

            if not args.apply:

                print(
                    "\n" + "=" * 110
                )
                print("DRY RUN COMPLETE")
                print("=" * 110)
                print(
                    "No database records were committed."
                )
                print(
                    "Run with --apply to commit Batch 7."
                )

                return

            print(
                "\n" + "=" * 110
            )
            print(
                f"CREATING {BATCH_NAME}"
            )
            print("=" * 110)

            created = []

            for index, item in enumerate(
                EXPERIENCES,
                start=1,
            ):

                print(
                    f"\n[{index:02d}/{len(EXPERIENCES)}] "
                    f"{item['code']} — "
                    f"{item['title']}"
                )

                experience = create_experience(
                    item
                )

                created.append(
                    experience
                )

                print(
                    "  ✓ Experience created"
                )

                print(
                    "  ✓ Currency: USD"
                )

                print(
                    "  ✓ Indicative selling price: "
                    f"USD {item['price_from']:.2f} "
                    "per person"
                )

            db.session.flush()

            print(
                "\n" + "=" * 110
            )
            print(
                "PRE-COMMIT VERIFICATION"
            )
            print("=" * 110)

            total_checks = 0

            for experience in created:

                checks = verify_experience(
                    experience
                )

                print_verification(
                    experience.experience_code,
                    checks,
                )

                if checks["media"] != 0:
                    raise RuntimeError(
                        f"{experience.experience_code} "
                        "unexpectedly has media."
                    )

                if checks["schedules"] != 0:
                    raise RuntimeError(
                        f"{experience.experience_code} "
                        "unexpectedly has schedules."
                    )

                if checks["bookings"] != 0:
                    raise RuntimeError(
                        f"{experience.experience_code} "
                        "unexpectedly has bookings."
                    )

                total_checks += sum(
                    checks.values()
                )

            db.session.commit()

            print(
                "\n" + "=" * 110
            )
            print(
                "BATCH 7 COMMITTED SUCCESSFULLY"
            )
            print("=" * 110)

            print(
                f"Experiences committed: "
                f"{len(created)}"
            )

            print(
                f"Child-record checks performed: "
                f"{total_checks}"
            )

            print(
                "Currency: USD"
            )

            print(
                "Categories reused:"
            )

            categories = sorted(
                {
                    item["category_slug"]
                    for item in EXPERIENCES
                }
            )

            for category in categories:
                print(
                    f"  - {category}"
                )

            print(
                f"Legacy featured image: "
                f"{DEFAULT_FEATURED_IMAGE}"
            )

            print(
                "ExperienceMedia created: 0"
            )

            print(
                "Schedules created: 0"
            )

            print(
                "Bookings created: 0"
            )

            print("=" * 110)

        except Exception as exc:

            db.session.rollback()

            print(
                "\n" + "=" * 110
            )
            print(
                "BATCH 7 FAILED — ROLLED BACK"
            )
            print("=" * 110)
            print(
                f"Error: {exc}"
            )
            print("=" * 110)

            raise


if __name__ == "__main__":
    main()