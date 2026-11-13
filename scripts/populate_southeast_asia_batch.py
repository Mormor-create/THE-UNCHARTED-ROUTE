"""
THE UNCHARTED ROUTE — BATCH 6: SOUTHEAST ASIA

Destinations:
    - Kuala Lumpur, Malaysia
    - Bangkok, Thailand
    - Phuket, Thailand

Experiences:
    01. SEA-KUL-001 — Kuala Lumpur Heritage, Batu Caves & Cultural Discovery
    02. SEA-KUL-002 — Kuala Lumpur Modern City, Towers & Skyline Experience
    03. SEA-BKK-001 — Bangkok Grand Palace, Temples & Old City Discovery
    04. SEA-BKK-002 — Bangkok Canals, Floating Market & Local Life Experience
    05. SEA-PKT-001 — Phuket Old Town, Viewpoints & Island Culture Experience
    06. SEA-PKT-002 — Phi Phi Islands, Lagoons & Andaman Adventure

IMPORTANT:
    - DRY RUN is the default.
    - Use --apply to commit.
    - Existing experiences are never modified.
    - Duplicate code/slug protection is enforced.
    - No media, schedules or bookings are created.
    - Prices are actual USD selling prices per person for the individual
      experience, NOT KES conversions and NOT the cost of an entire trip.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app import create_app, db
from app.models.experience import Experience


BATCH_NAME = "BATCH 6: SOUTHEAST ASIA"

# The current Experience schema requires a non-null legacy featured_image.
# Batch 6 intentionally creates no ExperienceMedia records, so all new
# experiences use the application's generic placeholder until real DAM media
# is assigned later.
DEFAULT_FEATURED_IMAGE = "images/experiences/default-experience.jpg"


# ---------------------------------------------------------------------------
# EXPERIENCE DATA
# ---------------------------------------------------------------------------

EXPERIENCES = [
    {
        "code": "SEA-KUL-001",
        "title": "Kuala Lumpur Heritage, Batu Caves & Cultural Discovery",
        "slug": "kuala-lumpur-heritage-batu-caves-cultural-discovery",
        "short_description": (
            "A full cultural introduction to Kuala Lumpur combining historic "
            "neighbourhoods, Batu Caves, religious landmarks and the city's "
            "multicultural character."
        ),
        "description": (
            "Discover Kuala Lumpur through the layers of Malay, Chinese and "
            "Indian heritage that shaped the city. The experience combines "
            "the historic heart of Kuala Lumpur with Batu Caves and selected "
            "cultural landmarks, creating an accessible introduction to the "
            "city's architecture, traditions, food culture and religious "
            "heritage."
        ),
        "duration": "7–8 hours",
        "meeting_point": "Central Kuala Lumpur hotel or agreed city meeting point",
        "location": "Kuala Lumpur, Malaysia",
        "price_from": Decimal("75.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages; children must be accompanied by an adult",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 601,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "kuala-lumpur",
        "seo_title": "Kuala Lumpur Heritage, Batu Caves & Cultural Discovery",
        "seo_description": (
            "Explore Kuala Lumpur's heritage districts, Batu Caves and "
            "multicultural landmarks on a curated cultural experience."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("75.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("105.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],
        "itinerary": [
            {
                "title": "Central Kuala Lumpur",
                "description": (
                    "Meet your host and begin with an orientation through "
                    "the historic and multicultural heart of Kuala Lumpur."
                ),
            },
            {
                "title": "Merdeka Square & Heritage Quarter",
                "description": (
                    "Explore the historic civic district and learn how "
                    "colonial, Malay, Chinese and Indian influences shaped "
                    "the city's architecture and identity."
                ),
            },
            {
                "title": "Batu Caves",
                "description": (
                    "Visit the famous limestone cave complex and Hindu "
                    "pilgrimage site, with time to explore the temple area "
                    "and surrounding cultural setting."
                ),
            },
            {
                "title": "Local Flavours & Cultural Wrap-Up",
                "description": (
                    "Enjoy time around a carefully selected local food or "
                    "market setting before returning to central Kuala Lumpur."
                ),
            },
        ],
        "inclusions": [
            "Professional local experience host",
            "Curated heritage and cultural experience",
            "Batu Caves visit",
            "Private or small-group experience according to selected option",
            "Local cultural interpretation",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks unless specifically stated",
            "Personal shopping",
            "Travel insurance",
            "Personal expenses",
            "Optional activities not listed in the itinerary",
        ],
        "highlights": [
            "Explore Kuala Lumpur's multicultural heritage",
            "Visit the iconic Batu Caves",
            "Discover Merdeka Square and the historic city centre",
            "Experience the cultural meeting point of Malay, Chinese and Indian traditions",
            "Travel in a small-group or private format",
        ],
        "addons": [
            {
                "title": "Local Food Tasting",
                "description": "Add a curated tasting of selected Malaysian dishes.",
            },
            {
                "title": "Private Evening Extension",
                "description": (
                    "Extend the experience into Kuala Lumpur's evening food "
                    "and cultural scene."
                ),
            },
        ],
        "packing_items": [
            "Comfortable walking shoes",
            "Light breathable clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
            "Modest clothing suitable for religious sites",
        ],
        "safety_rules": [
            "Follow host instructions at all religious and heritage sites.",
            "Wear appropriate clothing when entering religious sites.",
            "Stay hydrated in hot and humid conditions.",
            "Use designated walking routes around Batu Caves.",
        ],
        "requirements": [
            "Guests should be comfortable with moderate urban walking.",
            "Children must be accompanied by an adult.",
            "Visitors entering religious sites must observe local dress and conduct requirements.",
        ],
        "faqs": [
            {
                "question": "Is Batu Caves suitable for children?",
                "answer": (
                    "Yes, although the main stairway requires a reasonable "
                    "level of mobility and adult supervision for children."
                ),
            },
            {
                "question": "Is this a private tour?",
                "answer": (
                    "The standard option is designed for a small group. "
                    "A private option is also available."
                ),
            },
            {
                "question": "What should I wear?",
                "answer": (
                    "Wear comfortable clothing and carry modest clothing "
                    "suitable for religious sites."
                ),
            },
        ],
        "tags": [
            "Kuala Lumpur",
            "Malaysia",
            "Culture",
            "Heritage",
            "Batu Caves",
            "City Discovery",
            "Local Life",
        ],
        "signature_moments": [
            {
                "title": "The Batu Caves Reveal",
                "description": (
                    "Arriving beneath the towering limestone cliffs and "
                    "colourful temple staircase."
                ),
            },
            {
                "title": "Kuala Lumpur's Cultural Crossroads",
                "description": (
                    "Seeing Malay, Chinese and Indian influences come together "
                    "within one city."
                ),
            },
        ],
    },

    {
        "code": "SEA-KUL-002",
        "title": "Kuala Lumpur Modern City, Towers & Skyline Experience",
        "slug": "kuala-lumpur-modern-city-towers-skyline-experience",
        "short_description": (
            "A polished city experience exploring Kuala Lumpur's modern "
            "architecture, iconic towers, premium districts and skyline."
        ),
        "description": (
            "Experience the contemporary side of Kuala Lumpur through its "
            "iconic skyline, modern architecture, premium shopping districts "
            "and evolving urban identity. The experience balances landmark "
            "sights with local interpretation rather than simply ticking off "
            "photography stops."
        ),
        "duration": "5–6 hours",
        "meeting_point": "Central Kuala Lumpur hotel or agreed city meeting point",
        "location": "Kuala Lumpur, Malaysia",
        "price_from": Decimal("95.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 602,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "kuala-lumpur",
        "seo_title": "Kuala Lumpur Modern City, Towers & Skyline Experience",
        "seo_description": (
            "Discover Kuala Lumpur's modern skyline, iconic towers and "
            "contemporary city districts on a curated urban experience."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("95.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("135.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],
        "itinerary": [
            {
                "title": "City Orientation",
                "description": (
                    "Meet your host and begin with an overview of Kuala "
                    "Lumpur's rapid transformation into a global city."
                ),
            },
            {
                "title": "Petronas Twin Towers",
                "description": (
                    "Visit the landmark Twin Towers precinct and explore "
                    "the surrounding KLCC district."
                ),
            },
            {
                "title": "Contemporary Kuala Lumpur",
                "description": (
                    "Continue through selected modern districts, architecture "
                    "and premium urban spaces."
                ),
            },
            {
                "title": "Skyline & Evening Option",
                "description": (
                    "Finish with a curated skyline viewpoint, with an "
                    "optional evening extension available."
                ),
            },
        ],
        "inclusions": [
            "Professional local experience host",
            "Curated Kuala Lumpur city experience",
            "KLCC and Twin Towers precinct visit",
            "Small-group or private format according to selected option",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Attraction tickets unless specifically included",
            "Personal shopping",
            "Travel insurance",
            "Personal expenses",
        ],
        "highlights": [
            "See the Petronas Twin Towers",
            "Explore Kuala Lumpur's modern city districts",
            "Discover the city's architectural transformation",
            "Enjoy curated skyline viewpoints",
            "Combine landmark sightseeing with local interpretation",
        ],
        "addons": [
            {
                "title": "KLCC Observation Experience",
                "description": (
                    "Add entry to an available observation attraction."
                ),
            },
            {
                "title": "Private Night Skyline Extension",
                "description": (
                    "Continue into Kuala Lumpur's illuminated evening skyline."
                ),
            },
        ],
        "packing_items": [
            "Comfortable shoes",
            "Light clothing",
            "Sun protection",
            "Phone or camera",
            "Small day bag",
        ],
        "safety_rules": [
            "Remain with the group in busy public areas.",
            "Keep personal belongings secure in crowded districts.",
            "Follow attraction-specific safety instructions.",
        ],
        "requirements": [
            "Guests should be comfortable walking between urban stops.",
            "Attraction access may be subject to operating schedules and ticket availability.",
        ],
        "faqs": [
            {
                "question": "Does the price include entry to the Twin Towers?",
                "answer": (
                    "The standard experience does not automatically include "
                    "paid attraction admission unless explicitly stated in "
                    "the selected option."
                ),
            },
            {
                "question": "Can this be done privately?",
                "answer": "Yes. A private option is available.",
            },
            {
                "question": "Is this suitable for families?",
                "answer": (
                    "Yes. The experience is suitable for families and guests "
                    "of different ages."
                ),
            },
        ],
        "tags": [
            "Kuala Lumpur",
            "Malaysia",
            "City",
            "Modern Architecture",
            "Petronas",
            "Skyline",
            "Luxury",
        ],
        "signature_moments": [
            {
                "title": "The Twin Towers Moment",
                "description": (
                    "Standing beneath one of the world's most recognisable "
                    "modern city landmarks."
                ),
            },
            {
                "title": "Kuala Lumpur After Dark",
                "description": (
                    "Seeing the city's contemporary skyline come alive in "
                    "the evening."
                ),
            },
        ],
    },

    {
        "code": "SEA-BKK-001",
        "title": "Bangkok Grand Palace, Temples & Old City Discovery",
        "slug": "bangkok-grand-palace-temples-old-city-discovery",
        "short_description": (
            "A cultural journey through Bangkok's historic heart, combining "
            "the Grand Palace precinct, major temples and the character of "
            "the Old City."
        ),
        "description": (
            "Step into Bangkok's historic centre and explore the religious, "
            "royal and architectural traditions that define the city. The "
            "experience focuses on context and storytelling while allowing "
            "time to appreciate the details of Thailand's temple architecture "
            "and historic neighbourhoods."
        ),
        "duration": "6–7 hours",
        "meeting_point": "Central Bangkok hotel or agreed city meeting point",
        "location": "Bangkok, Thailand",
        "price_from": Decimal("85.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 603,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "bangkok",
        "seo_title": "Bangkok Grand Palace, Temples & Old City Discovery",
        "seo_description": (
            "Explore Bangkok's Grand Palace, historic temples and Old City "
            "on a curated cultural experience."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("85.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("125.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],
        "itinerary": [
            {
                "title": "Bangkok Old City",
                "description": (
                    "Meet your host and begin exploring the historic heart "
                    "of Bangkok."
                ),
            },
            {
                "title": "Grand Palace Precinct",
                "description": (
                    "Explore the royal complex and learn about Thailand's "
                    "monarchical and cultural history."
                ),
            },
            {
                "title": "Temple Discovery",
                "description": (
                    "Visit selected historic temples and interpret their "
                    "architecture, symbolism and role in Thai life."
                ),
            },
            {
                "title": "Old City Wrap-Up",
                "description": (
                    "Conclude with time to explore the surrounding historic "
                    "streets and local atmosphere before returning."
                ),
            },
        ],
        "inclusions": [
            "Professional local experience host",
            "Curated Old City cultural experience",
            "Historic temple visits",
            "Grand Palace precinct visit",
            "Small-group or private format according to selected option",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Temple or attraction entrance fees unless specifically stated",
            "Personal expenses",
            "Travel insurance",
            "Shopping",
        ],
        "highlights": [
            "Explore Bangkok's historic Old City",
            "Visit the Grand Palace precinct",
            "Discover major Buddhist temples",
            "Learn about Thai royal and religious traditions",
            "Experience Bangkok beyond its modern skyline",
        ],
        "addons": [
            {
                "title": "Thai Lunch Experience",
                "description": (
                    "Add a curated local lunch at a selected restaurant."
                ),
            },
            {
                "title": "Evening River Extension",
                "description": (
                    "Extend the experience toward Bangkok's riverside "
                    "after sunset."
                ),
            },
        ],
        "packing_items": [
            "Comfortable walking shoes",
            "Modest clothing",
            "Sun protection",
            "Reusable water bottle",
            "Small day bag",
        ],
        "safety_rules": [
            "Observe temple dress codes and local customs.",
            "Stay hydrated in Bangkok's heat and humidity.",
            "Keep valuables secure in busy public areas.",
            "Follow the host's instructions around traffic and crossings.",
        ],
        "requirements": [
            "Guests entering temples must observe local dress requirements.",
            "The experience involves walking over uneven historic surfaces.",
        ],
        "faqs": [
            {
                "question": "What should I wear for the temples?",
                "answer": (
                    "Shoulders and knees should be covered when entering "
                    "temples and other religious sites."
                ),
            },
            {
                "question": "Is the Grand Palace entrance included?",
                "answer": (
                    "Entrance is included only where explicitly stated in "
                    "the selected experience option."
                ),
            },
            {
                "question": "Can children join?",
                "answer": (
                    "Yes, children are welcome when accompanied by an adult."
                ),
            },
        ],
        "tags": [
            "Bangkok",
            "Thailand",
            "Culture",
            "Temples",
            "Grand Palace",
            "Old City",
            "Heritage",
        ],
        "signature_moments": [
            {
                "title": "The Grand Palace Reveal",
                "description": (
                    "Entering Bangkok's historic royal precinct and taking "
                    "in its intricate architecture."
                ),
            },
            {
                "title": "Temple Quiet",
                "description": (
                    "A reflective moment inside one of Bangkok's historic "
                    "Buddhist temple spaces."
                ),
            },
        ],
    },

    {
        "code": "SEA-BKK-002",
        "title": "Bangkok Canals, Floating Market & Local Life Experience",
        "slug": "bangkok-canals-floating-market-local-life-experience",
        "short_description": (
            "A lively Bangkok experience exploring canals, traditional "
            "markets and the everyday rhythms of local life."
        ),
        "description": (
            "See a different side of Bangkok beyond the major monuments. "
            "Travel through the city's waterways and market culture while "
            "discovering how traditional commerce, food and neighbourhood "
            "life continue alongside the modern metropolis."
        ),
        "duration": "6–7 hours",
        "meeting_point": "Central Bangkok hotel or agreed city meeting point",
        "location": "Bangkok, Thailand",
        "price_from": Decimal("110.00"),
        "currency": "USD",
        "group_size": "2–6 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 604,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "bangkok",
        "seo_title": "Bangkok Canals, Floating Market & Local Life Experience",
        "seo_description": (
            "Explore Bangkok's canals, traditional markets and local "
            "neighbourhood life through a curated cultural experience."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("110.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 6,
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
                "title": "Morning Departure",
                "description": (
                    "Meet your host and travel toward Bangkok's canal and "
                    "market districts."
                ),
            },
            {
                "title": "Canal Discovery",
                "description": (
                    "Explore selected waterways and learn about the historic "
                    "role of canals in Bangkok's development."
                ),
            },
            {
                "title": "Traditional Market",
                "description": (
                    "Experience the colours, flavours and rhythms of a "
                    "traditional market environment."
                ),
            },
            {
                "title": "Local Life & Return",
                "description": (
                    "Continue through selected neighbourhoods before "
                    "returning to central Bangkok."
                ),
            },
        ],
        "inclusions": [
            "Professional local experience host",
            "Curated canal and market experience",
            "Small-group or private format according to selected option",
            "Local cultural interpretation",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Optional boat fees unless specifically included",
            "Personal shopping",
            "Travel insurance",
            "Personal expenses",
        ],
        "highlights": [
            "Discover Bangkok's historic canal culture",
            "Explore a traditional market",
            "See local neighbourhood life beyond the main tourist districts",
            "Learn how waterways shaped Bangkok",
            "Enjoy a more intimate side of the city",
        ],
        "addons": [
            {
                "title": "Private Long-Tail Boat Extension",
                "description": (
                    "Extend the waterway experience with a private boat "
                    "arrangement where available."
                ),
            },
            {
                "title": "Thai Street Food Tasting",
                "description": (
                    "Add a curated tasting of selected local market dishes."
                ),
            },
        ],
        "packing_items": [
            "Comfortable shoes",
            "Sun protection",
            "Light breathable clothing",
            "Reusable water bottle",
            "Small day bag",
        ],
        "safety_rules": [
            "Follow boat safety instructions at all times.",
            "Remain seated while boats are moving.",
            "Keep valuables secure in crowded market areas.",
            "Stay hydrated in hot conditions.",
        ],
        "requirements": [
            "Guests should be comfortable boarding and exiting small boats where applicable.",
            "Boat routes and market activity may vary according to weather and local conditions.",
        ],
        "faqs": [
            {
                "question": "Is this the same as a standard Bangkok city tour?",
                "answer": (
                    "No. The focus is on waterways, traditional markets and "
                    "local neighbourhood life rather than major monuments."
                ),
            },
            {
                "question": "Will we definitely see a floating market?",
                "answer": (
                    "Market and waterway access can vary by operating "
                    "conditions, so the exact market route may be adjusted "
                    "while preserving the experience's core focus."
                ),
            },
            {
                "question": "Is the experience family-friendly?",
                "answer": (
                    "Yes, although children should be supervised carefully "
                    "around waterways and boats."
                ),
            },
        ],
        "tags": [
            "Bangkok",
            "Thailand",
            "Canals",
            "Markets",
            "Local Life",
            "Food",
            "Culture",
        ],
        "signature_moments": [
            {
                "title": "Bangkok by Water",
                "description": (
                    "Seeing the city from the waterways that once formed "
                    "its everyday transport network."
                ),
            },
            {
                "title": "Market Morning",
                "description": (
                    "Experiencing the colours, sounds and flavours of a "
                    "traditional Thai market."
                ),
            },
        ],
    },

    {
        "code": "SEA-PKT-001",
        "title": "Phuket Old Town, Viewpoints & Island Culture Experience",
        "slug": "phuket-old-town-viewpoints-island-culture-experience",
        "short_description": (
            "A curated Phuket discovery combining colourful Old Town streets, "
            "island viewpoints, local culture and southern Thai flavours."
        ),
        "description": (
            "Discover Phuket beyond its beaches through its distinctive "
            "Sino-Portuguese architecture, historic Old Town, viewpoints and "
            "local food culture. This experience connects Phuket's commercial "
            "history with the landscapes and communities that define the island "
            "today."
        ),
        "duration": "6–7 hours",
        "meeting_point": "Phuket hotel or agreed island meeting point",
        "location": "Phuket, Thailand",
        "price_from": Decimal("95.00"),
        "currency": "USD",
        "group_size": "2–8 guests",
        "age_range": "All ages",
        "difficulty": "Easy",
        "featured": False,
        "active": True,
        "display_order": 605,
        "category_slug": "culture-heritage-city-discovery",
        "destination_slug": "phuket",
        "seo_title": "Phuket Old Town, Viewpoints & Island Culture Experience",
        "seo_description": (
            "Explore Phuket Old Town, island viewpoints and local culture "
            "on a curated full-day experience."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("95.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 8,
            },
            {
                "label": "Private",
                "amount": Decimal("135.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 4,
            },
        ],
        "itinerary": [
            {
                "title": "Phuket Old Town",
                "description": (
                    "Begin with a guided walk through the colourful historic "
                    "streets and Sino-Portuguese architecture."
                ),
            },
            {
                "title": "Local Culture",
                "description": (
                    "Discover Phuket's multicultural history and its historic "
                    "trading connections."
                ),
            },
            {
                "title": "Island Viewpoint",
                "description": (
                    "Travel to a selected viewpoint for expansive views "
                    "across Phuket's landscape and coastline."
                ),
            },
            {
                "title": "Southern Thai Flavours",
                "description": (
                    "Finish with an opportunity to experience selected local "
                    "food and refreshments before returning."
                ),
            },
        ],
        "inclusions": [
            "Professional local experience host",
            "Curated Phuket cultural experience",
            "Old Town walking discovery",
            "Selected island viewpoint visit",
            "Small-group or private format according to selected option",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Meals and drinks",
            "Optional attraction entrance fees",
            "Personal expenses",
            "Travel insurance",
            "Shopping",
        ],
        "highlights": [
            "Explore colourful Phuket Old Town",
            "Discover Sino-Portuguese architecture",
            "Visit a scenic island viewpoint",
            "Learn about Phuket's multicultural trading history",
            "Experience southern Thai food culture",
        ],
        "addons": [
            {
                "title": "Private Food Tasting",
                "description": (
                    "Add a curated tasting of selected Phuket and southern "
                    "Thai dishes."
                ),
            },
            {
                "title": "Sunset Viewpoint Extension",
                "description": (
                    "Extend the experience into a selected sunset viewpoint."
                ),
            },
        ],
        "packing_items": [
            "Comfortable walking shoes",
            "Sun protection",
            "Light clothing",
            "Reusable water bottle",
            "Small day bag",
            "Light rain layer during wet-season travel",
        ],
        "safety_rules": [
            "Take care on steep or uneven viewpoint paths.",
            "Stay hydrated in tropical conditions.",
            "Follow host instructions around roads and viewpoints.",
            "Respect local communities and religious sites.",
        ],
        "requirements": [
            "Guests should be comfortable with urban walking and short viewpoint walks.",
            "Weather may affect viewpoint access.",
        ],
        "faqs": [
            {
                "question": "Is this mainly a beach tour?",
                "answer": (
                    "No. The experience focuses on Phuket's culture, Old "
                    "Town, architecture, viewpoints and local food."
                ),
            },
            {
                "question": "Can families join?",
                "answer": "Yes. The experience is suitable for families.",
            },
            {
                "question": "Can the experience be private?",
                "answer": "Yes. A private option is available.",
            },
        ],
        "tags": [
            "Phuket",
            "Thailand",
            "Old Town",
            "Culture",
            "Architecture",
            "Food",
            "Viewpoints",
        ],
        "signature_moments": [
            {
                "title": "Phuket Old Town Colours",
                "description": (
                    "Walking through the vibrant historic streets and "
                    "distinctive Sino-Portuguese facades."
                ),
            },
            {
                "title": "Island Horizon",
                "description": (
                    "Taking in the tropical Phuket landscape from an "
                    "elevated viewpoint."
                ),
            },
        ],
    },

    {
        "code": "SEA-PKT-002",
        "title": "Phi Phi Islands, Lagoons & Andaman Adventure",
        "slug": "phi-phi-islands-lagoons-andaman-adventure",
        "short_description": (
            "A premium island day exploring the Phi Phi archipelago, "
            "limestone scenery, clear waters and iconic Andaman landscapes."
        ),
        "description": (
            "Set out across the Andaman Sea for a full-day island adventure "
            "around the Phi Phi archipelago. Explore dramatic limestone "
            "formations, clear-water bays and carefully selected island stops "
            "while balancing sightseeing with time on the water."
        ),
        "duration": "8–10 hours",
        "meeting_point": "Phuket hotel or designated marina meeting point",
        "location": "Phuket, Thailand",
        "price_from": Decimal("125.00"),
        "currency": "USD",
        "group_size": "2–12 guests",
        "age_range": "All ages; children must be accompanied by an adult",
        "difficulty": "Moderate",
        "featured": True,
        "active": True,
        "display_order": 606,
        "category_slug": "coastal-island-escapes",
        "destination_slug": "phuket",
        "seo_title": "Phi Phi Islands, Lagoons & Andaman Adventure",
        "seo_description": (
            "Explore the Phi Phi Islands and Andaman Sea through a curated "
            "island adventure from Phuket."
        ),
        "pricing": [
            {
                "label": "Standard",
                "amount": Decimal("125.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 2,
                "maximum_guests": 12,
            },
            {
                "label": "Private",
                "amount": Decimal("185.00"),
                "currency": "USD",
                "basis": "per person",
                "minimum_guests": 1,
                "maximum_guests": 6,
            },
        ],
        "itinerary": [
            {
                "title": "Marina Departure",
                "description": (
                    "Meet at the designated marina and depart Phuket for "
                    "the Phi Phi archipelago."
                ),
            },
            {
                "title": "Limestone Islands",
                "description": (
                    "Cruise through the dramatic limestone formations and "
                    "selected scenic bays of the Phi Phi region."
                ),
            },
            {
                "title": "Lagoon & Beach Time",
                "description": (
                    "Enjoy time around selected clear-water locations for "
                    "swimming, photography and relaxed exploration where "
                    "conditions permit."
                ),
            },
            {
                "title": "Return Across the Andaman",
                "description": (
                    "Continue the island route before returning to Phuket "
                    "and the mainland."
                ),
            },
        ],
        "inclusions": [
            "Professional experience host",
            "Boat-based Phi Phi island experience",
            "Selected island and lagoon stops",
            "Drinking water",
            "Small-group or private format according to selected option",
        ],
        "exclusions": [
            "International flights",
            "Accommodation",
            "Personal expenses",
            "Travel insurance",
            "Optional water activities",
            "National park or local conservation fees where charged separately",
            "Meals unless specifically stated",
        ],
        "highlights": [
            "Explore the Phi Phi archipelago",
            "Cruise beneath dramatic limestone cliffs",
            "Discover clear-water bays and lagoons",
            "Enjoy time on selected island beaches",
            "Experience the Andaman Sea from the water",
        ],
        "addons": [
            {
                "title": "Private Long-Tail Boat Extension",
                "description": (
                    "Add a private traditional boat arrangement for selected "
                    "island movements where available."
                ),
            },
            {
                "title": "Private Snorkelling Extension",
                "description": (
                    "Add additional snorkelling time at suitable locations "
                    "and conditions."
                ),
            },
        ],
        "packing_items": [
            "Swimwear",
            "Reef-safe sunscreen",
            "Hat and sunglasses",
            "Light cover-up",
            "Waterproof phone pouch",
            "Reusable water bottle",
            "Dry bag or waterproof day bag",
        ],
        "safety_rules": [
            "Follow crew instructions throughout the boat journey.",
            "Wear a life jacket when instructed.",
            "Do not enter the water when sea conditions are unsafe.",
            "Respect marine life and never touch coral or wildlife.",
            "Stay hydrated and protected from prolonged sun exposure.",
        ],
        "requirements": [
            "Guests should be comfortable with a full day on the water.",
            "Swimming is optional unless a guest chooses a water activity.",
            "Boat routes and stops may change due to sea conditions, weather or local regulations.",
            "Children must be accompanied by an adult.",
        ],
        "faqs": [
            {
                "question": "Do I have to swim?",
                "answer": (
                    "No. Swimming is optional. Guests can enjoy the scenery "
                    "and island stops without entering the water."
                ),
            },
            {
                "question": "Is this a private boat trip?",
                "answer": (
                    "The standard option is small-group. A private option "
                    "is available."
                ),
            },
            {
                "question": "Can the itinerary change?",
                "answer": (
                    "Yes. Island routes and stops may be adjusted for weather, "
                    "sea conditions, safety and local regulations."
                ),
            },
        ],
        "tags": [
            "Phuket",
            "Thailand",
            "Phi Phi",
            "Andaman Sea",
            "Islands",
            "Adventure",
            "Marine",
            "Beach",
        ],
        "signature_moments": [
            {
                "title": "The Limestone Horizon",
                "description": (
                    "Cruising beneath the towering limestone formations of "
                    "the Phi Phi archipelago."
                ),
            },
            {
                "title": "Andaman Blue",
                "description": (
                    "A quiet moment surrounded by the clear tropical waters "
                    "and island landscapes of the Andaman Sea."
                ),
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def model_column_names(model_class) -> set[str]:
    """Return real SQLAlchemy column names for a model."""
    try:
        return {
            column.name
            for column in model_class.__table__.columns
        }
    except Exception:
        return set()


def set_supported_fields(
    obj: Any,
    values: dict[str, Any],
) -> Any:
    """
    Safely assign only fields that actually exist on the model.

    This keeps the batch script resilient to optional fields while avoiding
    accidental creation of arbitrary attributes.
    """
    columns = model_column_names(type(obj))

    for key, value in values.items():
        if key in columns and value is not None:
            setattr(obj, key, value)

    return obj


def get_relationship_model(
    parent_model,
    relationship_name: str,
):
    """Resolve the mapped model behind an Experience relationship."""
    relationship = parent_model.__mapper__.relationships.get(
        relationship_name
    )

    if relationship is None:
        return None

    return relationship.mapper.class_


def add_related(
    parent,
    relationship_name: str,
    rows: list[dict[str, Any]],
) -> int:
    """
    Create one-to-many / many-to-many related records using the actual
    SQLAlchemy relationship mapper.

    Add-ons are normalized separately because the ExperienceAddon model
    requires `name`, while Batch 6 source data intentionally uses the
    human-readable `title` key.
    """
    relationship = type(parent).__mapper__.relationships.get(
        relationship_name
    )

    if relationship is None:
        return 0

    related_model = relationship.mapper.class_
    created = 0

    collection = getattr(parent, relationship_name)

    parent_currency = getattr(
        parent,
        "currency",
        None,
    ) or "USD"

    for row in rows:
        normalized_row = dict(row)

        # ---------------------------------------------------------------
        # EXPERIENCE ADDONS
        # ---------------------------------------------------------------
        #
        # The database schema requires:
        #     experience_addons.name
        #
        # Batch data uses:
        #     title
        #
        # Therefore title must explicitly become name.
        #
        # The previous generic field mapper silently ignored title and
        # allowed name=None to reach SQLite.
        #
        # Also ensure the add-on uses the experience's currency rather
        # than the application's unrelated default currency (KES).
        #
        if relationship_name == "addons":
            addon_name = (
                normalized_row.get("name")
                or normalized_row.get("title")
            )

            if not addon_name or not str(addon_name).strip():
                raise RuntimeError(
                    f"Experience add-on name is required for "
                    f"{getattr(parent, 'experience_code', 'unknown experience')}."
                )

            addon_description = (
                normalized_row.get("description")
                or normalized_row.get("short_description")
                or ""
            )

            normalized_row["name"] = str(
                addon_name
            ).strip()

            # Preserve the supplied description in the actual description
            # field where supported.
            normalized_row["description"] = addon_description

            # The model may have short_description as a separate field.
            # Populate it as well when available.
            if "short_description" not in normalized_row:
                normalized_row["short_description"] = addon_description

            # Batch 6 prices are actual USD prices. These add-ons currently
            # have no separately defined selling amount, so retain a zero
            # price rather than inventing a price.
            normalized_row.setdefault(
                "price",
                Decimal("0.00"),
            )

            normalized_row["currency"] = parent_currency

            normalized_row.setdefault(
                "pricing_type",
                "Per Person",
            )

            normalized_row.setdefault(
                "optional",
                True,
            )

            normalized_row.setdefault(
                "available_online",
                True,
            )

            normalized_row.setdefault(
                "active",
                True,
            )

        obj = related_model()

        set_supported_fields(
            obj,
            normalized_row,
        )

        # ---------------------------------------------------------------
        # REQUIRED-FIELD SAFETY FOR ADD-ONS
        # ---------------------------------------------------------------

        if relationship_name == "addons":
            columns = model_column_names(
                related_model
            )

            if "name" in columns:
                actual_name = getattr(
                    obj,
                    "name",
                    None,
                )

                if not actual_name:
                    raise RuntimeError(
                        f"Could not populate required "
                        f"experience_addons.name for "
                        f"{getattr(parent, 'experience_code', 'unknown experience')}."
                    )

            if "currency" in columns:
                actual_currency = getattr(
                    obj,
                    "currency",
                    None,
                )

                if actual_currency != parent_currency:
                    raise RuntimeError(
                        f"Add-on currency mismatch for "
                        f"{getattr(parent, 'experience_code', 'unknown experience')}: "
                        f"expected {parent_currency}, got {actual_currency}."
                    )

        collection.append(obj)
        created += 1

    return created

def slugify_tag(value: str) -> str:
    """
    Convert a tag name into a URL-safe slug without requiring
    an external slugify dependency.
    """
    import re

    value = str(value or "").strip().lower()

    # Replace ampersands with a readable word.
    value = value.replace("&", " and ")

    # Remove apostrophes.
    value = value.replace("'", "")

    # Replace all non-alphanumeric characters with hyphens.
    value = re.sub(r"[^a-z0-9]+", "-", value)

    # Collapse repeated hyphens and trim them.
    value = re.sub(r"-+", "-", value).strip("-")

    return value


def add_tags(parent, rows):
    """
    Create or reuse Tag records for an experience.

    The Tag model requires:
        name
        slug

    Batch data supplies tag names only, so the slug is generated
    automatically from the name.
    """
    relationship = type(parent).__mapper__.relationships.get("tags")

    if relationship is None:
        return 0

    tag_model = relationship.mapper.class_
    collection = getattr(parent, "tags")
    columns = model_column_names(tag_model)

    created_or_attached = 0

    for index, row in enumerate(rows):

        # Support both simple strings and dictionary-style tag rows.
        if isinstance(row, str):
            tag_name = row.strip()
            tag_values = {}

        elif isinstance(row, dict):
            tag_name = (
                row.get("name")
                or row.get("label")
                or row.get("title")
            )

            tag_values = dict(row)

        else:
            raise RuntimeError(
                f"Unsupported tag row type for "
                f"{parent.experience_code}: "
                f"{type(row).__name__}"
            )

        if not tag_name or not str(tag_name).strip():
            raise RuntimeError(
                f"Tag name is required for "
                f"{parent.experience_code}."
            )

        tag_name = str(tag_name).strip()

        # Use an explicitly supplied slug if the batch provides one;
        # otherwise generate it from the tag name.
        tag_slug = (
            tag_values.get("slug")
            or slugify_tag(tag_name)
        )

        if not tag_slug:
            raise RuntimeError(
                f"Could not generate a valid tag slug for "
                f"{parent.experience_code}: {tag_name!r}"
            )

        # First try to reuse an existing tag by slug.
        existing_tag = None

        if "slug" in columns:
            existing_tag = (
                db.session.query(tag_model)
                .filter(tag_model.slug == tag_slug)
                .first()
            )

        # If no slug match exists, also try the exact tag name.
        if existing_tag is None and "name" in columns:
            existing_tag = (
                db.session.query(tag_model)
                .filter(tag_model.name == tag_name)
                .first()
            )

        if existing_tag is not None:
            collection.append(existing_tag)
            created_or_attached += 1
            continue

        # Create a new tag.
        obj = tag_model()

        normalized_values = {
            "name": tag_name,
            "slug": tag_slug,
            "description": tag_values.get("description"),
            "color": tag_values.get("color", "#10B981"),
            "icon": tag_values.get("icon"),
            "featured": tag_values.get("featured", False),
            "meta_title": tag_values.get("meta_title"),
            "meta_description": tag_values.get("meta_description"),
            "active": tag_values.get("active", True),
            "sort_order": tag_values.get("sort_order", index),
        }

        for key, value in normalized_values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        # Hard validation before this object is attached to the
        # experience. This prevents another autoflush failure later.
        if "name" in columns:
            actual_name = getattr(obj, "name", None)
            if not actual_name:
                raise RuntimeError(
                    f"Could not populate required tags.name for "
                    f"{parent.experience_code}."
                )

        if "slug" in columns:
            actual_slug = getattr(obj, "slug", None)
            if not actual_slug:
                raise RuntimeError(
                    f"Could not populate required tags.slug for "
                    f"{parent.experience_code} "
                    f"({tag_name})."
                )

        collection.append(obj)
        created_or_attached += 1

    return created_or_attached

def add_packing_items(parent, rows):
    relationship = type(parent).__mapper__.relationships.get("packing_items")

    if relationship is None:
        return 0

    packing_model = relationship.mapper.class_
    collection = getattr(parent, "packing_items")
    columns = model_column_names(packing_model)
    created = 0

    for index, row in enumerate(rows):
        obj = packing_model()

        if isinstance(row, str):
            values = {
                "name": row,
                "description": None,
                "category": "General",
                "icon": "backpack",
                "recommended": True,
                "required": False,
                "display_order": index,
                "active": True,
            }
        elif isinstance(row, dict):
            values = {
                "name": row.get("name") or row.get("title"),
                "description": (
                    row.get("description")
                    or row.get("short_description")
                ),
                "category": row.get("category") or "General",
                "icon": row.get("icon") or "backpack",
                "recommended": row.get("recommended", True),
                "required": row.get("required", False),
                "display_order": row.get("display_order", index),
                "active": row.get("active", True),
            }
        else:
            raise RuntimeError(
                f"Unsupported packing item type for "
                f"{parent.experience_code}: {type(row).__name__}"
            )

        for key, value in values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        if "name" in columns and not getattr(obj, "name", None):
            raise RuntimeError(
                f"Experience packing item name is required for "
                f"{parent.experience_code}."
            )

        collection.append(obj)
        created += 1

    return created


def add_pricing(parent, rows):
    """
    Create experience pricing records using the actual ExperiencePricing
    schema while normalizing the Batch 6 pricing data.

    Batch pricing uses:
        label
        amount
        minimum_guests
        maximum_guests
        basis

    The database model uses:
        experience_level
        price
        minimum_people
        maximum_people
        currency
        notes
    """
    relationship = type(parent).__mapper__.relationships.get("pricing")

    if relationship is None:
        return 0

    pricing_model = relationship.mapper.class_
    collection = getattr(parent, "pricing")
    columns = model_column_names(pricing_model)
    created = 0

    parent_currency = (
        getattr(parent, "currency", None)
        or "USD"
    )

    for index, row in enumerate(rows):

        obj = pricing_model()

        # ---------------------------------------------------------------
        # NORMALIZE BATCH PRICING DATA
        # ---------------------------------------------------------------

        if isinstance(row, str):
            experience_level = row

            values = {
                "experience_level": experience_level,
                "minimum_people": 1,
                "maximum_people": None,
                "price": None,
                "currency": parent_currency,
                "notes": None,
                "display_order": index,
                "active": True,
            }

        elif isinstance(row, dict):

            # Batch 6 uses `label`, while the database requires
            # `experience_level`.
            experience_level = (
                row.get("experience_level")
                or row.get("label")
                or row.get("level")
                or row.get("title")
                or row.get("name")
            )

            # Batch 6 uses `amount`, while the database requires `price`.
            price = (
                row.get("price")
                if row.get("price") is not None
                else row.get("amount")
            )

            # Batch 6 uses minimum_guests / maximum_guests,
            # while the database uses minimum_people / maximum_people.
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

            # Preserve the human-readable pricing basis in notes if the
            # actual model has a notes field.
            notes = row.get("notes")

            if not notes and row.get("basis"):
                notes = str(row["basis"])

            values = {
                "experience_level": experience_level,
                "minimum_people": minimum_people,
                "maximum_people": maximum_people,
                "price": price,
                "currency": row.get("currency") or parent_currency,
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

        else:
            raise RuntimeError(
                f"Unsupported pricing row type for "
                f"{parent.experience_code}: "
                f"{type(row).__name__}"
            )

        # ---------------------------------------------------------------
        # ASSIGN ONLY REAL MODEL COLUMNS
        # ---------------------------------------------------------------

        for key, value in values.items():
            if key in columns and value is not None:
                setattr(obj, key, value)

        # ---------------------------------------------------------------
        # REQUIRED-FIELD VALIDATION
        # ---------------------------------------------------------------

        if "experience_level" in columns:
            actual_level = getattr(
                obj,
                "experience_level",
                None,
            )

            if not actual_level:
                raise RuntimeError(
                    f"Experience pricing level is required for "
                    f"{parent.experience_code}."
                )

        if "price" in columns:
            actual_price = getattr(
                obj,
                "price",
                None,
            )

            if actual_price is None:
                raise RuntimeError(
                    f"Experience pricing amount is required for "
                    f"{parent.experience_code} "
                    f"({actual_level})."
                )

        if "currency" in columns:
            actual_currency = getattr(
                obj,
                "currency",
                None,
            )

            if actual_currency != parent_currency:
                raise RuntimeError(
                    f"Pricing currency mismatch for "
                    f"{parent.experience_code} "
                    f"({actual_level}): "
                    f"expected {parent_currency}, "
                    f"got {actual_currency}."
                )

        collection.append(obj)
        created += 1

    return created

def add_signature_moments(
    parent,
    moments: list[dict[str, Any]],
) -> int:
    """Create signature-moment records through the existing relationship."""
    relationship = type(parent).__mapper__.relationships.get(
        "signature_moments"
    )

    if relationship is None:
        return 0

    moment_model = relationship.mapper.class_
    collection = getattr(parent, "signature_moments")

    created = 0

    for row in moments:
        obj = moment_model()
        set_supported_fields(obj, row)
        collection.append(obj)
        created += 1

    return created


def find_destination(slug: str):
    """Find an existing destination without creating or modifying it."""
    destination_model = get_relationship_model(
        Experience,
        "destination",
    )

    if destination_model is None:
        raise RuntimeError(
            "Could not resolve the Experience.destination relationship."
        )

    destination = destination_model.query.filter_by(
        slug=slug
    ).first()

    if destination is None:
        raise RuntimeError(
            f"Required destination does not exist: {slug}"
        )

    return destination


def find_category(slug: str):
    """
    Find an existing ExperienceCategory without creating or modifying it.

    Experience.category is confirmed to point to:
        app.models.experience_category.ExperienceCategory
        -> experience_categories
    """
    category_model = get_relationship_model(
        Experience,
        "category",
    )

    if category_model is None:
        raise RuntimeError(
            "Could not resolve the Experience.category relationship."
        )

    normalized_slug = (slug or "").strip().lower()

    if not normalized_slug:
        raise RuntimeError(
            "Experience category slug cannot be empty."
        )

    category = category_model.query.filter_by(
        slug=normalized_slug
    ).first()

    if category is None:
        raise RuntimeError(
            f"Required experience category does not exist: "
            f"{normalized_slug}"
        )

    return category


def duplicate_exists(
    code: str,
    slug: str,
) -> bool:
    """Protect existing records by both code and slug."""
    by_code = Experience.query.filter_by(
        experience_code=code
    ).first()

    if by_code:
        return True

    by_slug = Experience.query.filter_by(
        slug=slug
    ).first()

    return by_slug is not None


def create_experience(
    data: dict[str, Any],
):
    """Create a complete new experience and all supported child records."""

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
        "currency": "USD",
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

    # Existing destination/category records only.
    if "destination_id" in model_column_names(Experience):
        experience.destination_id = destination.id

    if "category_id" in model_column_names(Experience):
        if category is None:
            raise RuntimeError(
                f"Category resolution returned None for "
                f"{data['category_slug']}."
            )

        experience.category_id = category.id

    db.session.add(experience)
    db.session.flush()

    # -----------------------------------------------------------------------
    # CHILD RELATIONSHIPS
    # -----------------------------------------------------------------------
    add_pricing(
        experience,
        data["pricing"],
    )

    add_related(
        experience,
        "itinerary",
        data["itinerary"],
    )

    add_related(
        experience,
        "inclusions",
        [
            {"title": item}
            for item in data["inclusions"]
        ],
    )

    add_related(
        experience,
        "exclusions",
        [
            {"title": item}
            for item in data["exclusions"]
        ],
    )

    add_related(
        experience,
        "highlights",
        [
            {"title": item}
            for item in data["highlights"]
        ],
    )

    add_related(
        experience,
        "addons",
        data["addons"],
    )

    add_packing_items(
        experience,
        data["packing_items"],
    )

    add_related(
        experience,
        "safety_rules",
        [
            {"title": item}
            for item in data["safety_rules"]
        ],
    )

    add_related(
        experience,
        "requirements",
        [
            {"title": item}
            for item in data["requirements"]
        ],
    )

    add_related(
        experience,
        "faqs",
        data["faqs"],
    )

    add_tags(
        experience,
        data["tags"],
    )

    add_signature_moments(
        experience,
        data["signature_moments"],
    )

    return experience


def relationship_count(
    obj,
    relationship_name: str,
) -> int:
    """
    Count relationship records safely.

    AppenderQuery relationships expose .count(); normal lists use len().
    """
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
    """Verify the expected child-record structure before commit."""

    checks = {
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

    return checks


def print_verification(
    code: str,
    checks: dict[str, int],
):
    print(f"\n  Verification: {code}")

    for key, value in checks.items():
        print(f"    {key:<20} {value}")


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------
def validate_batch_data():
    print("Validating batch data...")

    if not DEFAULT_FEATURED_IMAGE.strip():
        raise RuntimeError(
            "DEFAULT_FEATURED_IMAGE cannot be empty because "
            "Experience.featured_image is required."
        )

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
            "Duplicate experience code inside Batch 6."
        )

    if len(slugs) != len(set(slugs)):
        raise RuntimeError(
            "Duplicate experience slug inside Batch 6."
        )

    for item in EXPERIENCES:
        if item["currency"] != "USD":
            raise RuntimeError(
                f"{item['code']} must use USD."
            )

        if Decimal(str(item["price_from"])) <= 0:
            raise RuntimeError(
                f"{item['code']} has an invalid price_from."
            )

        for price in item["pricing"]:
            if price["currency"] != "USD":
                raise RuntimeError(
                    f"{item['code']} contains a non-USD pricing record."
                )

            if Decimal(str(price["amount"])) <= 0:
                raise RuntimeError(
                    f"{item['code']} contains an invalid USD price."
                )

        for addon in item.get("addons", []):
            addon_name = (
                addon.get("name")
                or addon.get("title")
            )

            if not addon_name or not str(addon_name).strip():
                raise RuntimeError(
                    f"{item['code']} contains an add-on without a name/title."
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

    print("\nRequired existing destinations:")

    for slug in required:
        destination = find_destination(slug)

        label = (
            getattr(destination, "title", None)
            or getattr(destination, "name", None)
            or slug
        )

        print(
            f"  ✓ {label} ({slug})"
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
        category = find_category(slug)

        label = (
            getattr(category, "name", None)
            or getattr(category, "title", None)
            or slug
        )

        print(
            f"  ✓ {label} ({slug})"
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
        print("\nDuplicate records detected:")

        for duplicate in duplicates:
            print(f"  - {duplicate}")

        raise RuntimeError(
            "Batch 6 contains existing experience records. "
            "No records will be modified."
        )

    print(
        "\nNo existing Batch 6 experience duplicates found."
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Populate THE UNCHARTED ROUTE Batch 6."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit Batch 6 to the database.",
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
            f"Experiences in batch: {len(EXPERIENCES)}"
        )
        print(
            f"Mode: "
            f"{'APPLY — COMMIT' if args.apply else 'DRY RUN'}"
        )
        print("=" * 110)

        try:
            # ---------------------------------------------------------------
            # VALIDATION
            # ---------------------------------------------------------------

            validate_batch_data()
            validate_destinations()
            validate_categories()
            validate_existing_records()

            # ---------------------------------------------------------------
            # PLAN
            # ---------------------------------------------------------------

            print("\n" + "=" * 110)
            print("EXPERIENCE PLAN")
            print("=" * 110)

            for index, item in enumerate(
                EXPERIENCES,
                start=1,
            ):
                print(
                    f"\n[{index:02d}/{len(EXPERIENCES)}] "
                    f"{item['code']} — {item['title']}"
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
                    f"USD {item['price_from']:.2f} per person"
                )

                print(
                    f"    Duration    : "
                    f"{item['duration']}"
                )

            # ---------------------------------------------------------------
            # DRY RUN
            # ---------------------------------------------------------------

            if not args.apply:
                print("\n" + "=" * 110)
                print("DRY RUN COMPLETE")
                print("=" * 110)
                print(
                    "No database records were committed."
                )
                print(
                    "Run with --apply to commit Batch 6."
                )
                return

            # ---------------------------------------------------------------
            # CREATE
            # ---------------------------------------------------------------

            print("\n" + "=" * 110)
            print("CREATING BATCH 6")
            print("=" * 110)

            created = []

            for index, item in enumerate(
                EXPERIENCES,
                start=1,
            ):
                print(
                    f"\n[{index:02d}/{len(EXPERIENCES)}] "
                    f"{item['code']} — {item['title']}"
                )

                experience = create_experience(item)

                created.append(experience)

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

            # ---------------------------------------------------------------
            # PRE-COMMIT VERIFICATION
            # ---------------------------------------------------------------

            print("\n" + "=" * 110)
            print("PRE-COMMIT VERIFICATION")
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

            # ---------------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------------

            db.session.commit()

            print("\n" + "=" * 110)
            print("BATCH 6 COMMITTED SUCCESSFULLY")
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

            print(
                "  - culture-heritage-city-discovery"
            )

            print(
                "  - coastal-island-escapes"
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

            print("\n" + "=" * 110)
            print("BATCH 6 FAILED — ROLLED BACK")
            print("=" * 110)

            print(
                f"Error: {exc}"
            )
            print("=" * 110)
            raise

if __name__ == "__main__":
    main()