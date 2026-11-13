"""
Populate reusable Experience Tags and Signature Moments
for The Uncharted Route.
"""

import sys
from pathlib import Path
from importlib import import_module

# ============================================================
# PROJECT PATH BOOTSTRAP
# ============================================================

# Resolve the actual project root from this script's location.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Give our local project priority over installed packages.
project_root_string = str(PROJECT_ROOT)

if project_root_string in sys.path:
    sys.path.remove(project_root_string)

sys.path.insert(0, project_root_string)

# ============================================================
# VERIFY LOCAL APPLICATION PACKAGE
# ============================================================

LOCAL_APP_PACKAGE = PROJECT_ROOT / "app" / "__init__.py"

if not LOCAL_APP_PACKAGE.exists():
    raise FileNotFoundError(
        f"Cannot find the TUR application package: {LOCAL_APP_PACKAGE}"
    )

print(f"\nProject root: {PROJECT_ROOT}")
print(f"Application package: {LOCAL_APP_PACKAGE}")

# ============================================================
# IMPORT THE TUR APPLICATION
# ============================================================

from app import create_app

# ============================================================
# MODEL IMPORTS
# ============================================================

def load_model(model_name):
    module_candidates = [
        "app.models",
        "app.models.experience",
        "app.models.experience_tag",
        "app.models.signature_moment",
        "app.models.tag",
    ]

    for module_name in module_candidates:
        try:
            module = import_module(module_name)
            model = getattr(module, model_name, None)

            if model is not None:
                return model

        except ImportError:
            continue

    raise ImportError(
        f"Could not locate {model_name}. "
        "Check the model's actual module inside app/models/."
    )


ExperienceTag = load_model("ExperienceTag")
SignatureMoment = load_model("SignatureMoment")

# ============================================================
# CREATE FLASK APPLICATION
# ============================================================
app = create_app()

# ============================================================
# MODEL IMPORTS
# ============================================================
def load_model(model_name):
    """
    Resolve a model from the application's existing model modules.
    This accommodates models being exported from different modules.
    """
    module_candidates = [
        "app.models",
        "app.models.experience",
        "app.models.experience_tag",
        "app.models.signature_moment",
        "app.models.tag",
    ]

    for module_name in module_candidates:
        try:
            module = import_module(module_name)
            model = getattr(module, model_name, None)

            if model is not None:
                return model

        except ImportError:
            continue

    raise ImportError(
        f"Could not locate {model_name}. "
        f"Check the model's module inside app/models/."
    )


ExperienceTag = load_model("ExperienceTag")
SignatureMoment = load_model("SignatureMoment")


# ============================================================
# APPLICATION
# ============================================================

app = create_app()


# ============================================================
# EXPERIENCE TAGS
# ============================================================

# The six existing tags are deliberately excluded.
# Their IDs, descriptions, icons, colours and SEO fields remain
# exactly as they currently exist in the database.

NEW_TAGS = [
    {
        "name": "Adventure",
        "slug": "adventure",
        "description": (
            "Experiences built around exploration, discovery, "
            "physical activity and memorable outdoor adventures. "
            "These experiences invite travellers to step beyond "
            "the ordinary and engage with their surroundings."
        ),
        "color": "#C96A2C",
        "icon": "mountain",
        "meta_title": "Adventure Experiences | The Uncharted Route",
        "meta_description": (
            "Discover outdoor adventures, active exploration and "
            "exciting experiences across remarkable destinations."
        ),
    },
    {
        "name": "Luxury",
        "slug": "luxury",
        "description": (
            "Elevated experiences defined by exceptional settings, "
            "thoughtful details, comfort, quality and personalised "
            "service. Luxury may be expressed through accommodation, "
            "dining, activities or the overall experience."
        ),
        "color": "#D89B24",
        "icon": "crown",
        "meta_title": "Luxury Experiences | The Uncharted Route",
        "meta_description": (
            "Explore elevated travel experiences, exceptional "
            "settings and thoughtfully curated luxury escapes."
        ),
    },
    {
        "name": "Bird Watching",
        "slug": "bird-watching",
        "description": (
            "Experiences focused on observing, identifying and "
            "appreciating birds in their natural habitats. May include "
            "guided birding, wetland exploration and opportunities "
            "to discover local and migratory species."
        ),
        "color": "#5C6B32",
        "icon": "bird",
        "meta_title": "Bird Watching Experiences | The Uncharted Route",
        "meta_description": (
            "Discover birdwatching experiences, remarkable birdlife "
            "and nature-focused exploration across destinations."
        ),
    },
    {
        "name": "Big Five",
        "slug": "big-five",
        "description": (
            "Wildlife experiences that focus specifically on the "
            "African Big Five: lion, leopard, elephant, rhinoceros "
            "and African buffalo. Sightings depend on natural "
            "conditions and are never guaranteed."
        ),
        "color": "#1F5138",
        "icon": "paw-print",
        "meta_title": "Big Five Wildlife Experiences | The Uncharted Route",
        "meta_description": (
            "Explore African Big Five wildlife experiences and "
            "discover the animals that make these encounters special."
        ),
    },
    {
        "name": "Family Friendly",
        "slug": "family-friendly",
        "description": (
            "Experiences designed or suitable for families travelling "
            "with children. Suitability, age restrictions, supervision "
            "requirements and activity conditions should be confirmed "
            "for each individual experience."
        ),
        "color": "#D89B24",
        "icon": "users",
        "meta_title": "Family Friendly Experiences | The Uncharted Route",
        "meta_description": (
            "Discover family-friendly experiences, activities and "
            "memorable journeys suitable for travelling together."
        ),
    },
    {
        "name": "Culture & Heritage",
        "slug": "culture-heritage",
        "description": (
            "Experiences that introduce travellers to the histories, "
            "identities, traditions, heritage and cultural expressions "
            "of the communities and places they visit. Each experience "
            "should reflect its own local cultural context."
        ),
        "color": "#C96A2C",
        "icon": "landmark",
        "meta_title": "Culture & Heritage Experiences | The Uncharted Route",
        "meta_description": (
            "Explore cultural heritage, local histories, traditions "
            "and meaningful cultural experiences around the world."
        ),
    },
    {
        "name": "Coastal Escape",
        "slug": "coastal-escape",
        "description": (
            "Experiences centred on coastal settings, seaside "
            "landscapes, ocean views and relaxed coastal exploration. "
            "May include coastal retreats, scenic outings and "
            "experiences along the shoreline."
        ),
        "color": "#1F5138",
        "icon": "waves",
        "meta_title": "Coastal Escapes | The Uncharted Route",
        "meta_description": (
            "Discover coastal escapes, seaside experiences and "
            "beautiful ocean landscapes across remarkable destinations."
        ),
    },
    {
        "name": "Culinary",
        "slug": "culinary",
        "description": (
            "Experiences centred on food, gastronomy, culinary "
            "discovery and the relationship between cuisine and "
            "destination identity. May include dining, food culture "
            "and hands-on culinary activities."
        ),
        "color": "#C96A2C",
        "icon": "utensils",
        "meta_title": "Culinary Experiences | The Uncharted Route",
        "meta_description": (
            "Discover culinary experiences, regional cuisine, "
            "food traditions and memorable dining experiences."
        ),
    },
    {
        "name": "Hiking & Trekking",
        "slug": "hiking-trekking",
        "description": (
            "Walking, hiking and trekking experiences through "
            "natural landscapes, mountains, countryside and "
            "designated trails. Terrain, duration and fitness "
            "requirements vary by experience."
        ),
        "color": "#5C6B32",
        "icon": "footprints",
        "meta_title": "Hiking & Trekking Experiences | The Uncharted Route",
        "meta_description": (
            "Explore hiking trails, trekking adventures and "
            "scenic walking experiences across diverse landscapes."
        ),
    },
    {
        "name": "Romantic Escape",
        "slug": "romantic-escape",
        "description": (
            "Experiences designed for couples seeking meaningful "
            "time together, memorable settings and special moments. "
            "May include romantic dining, scenic escapes, private "
            "activities and intimate getaways."
        ),
        "color": "#C96A2C",
        "icon": "heart",
        "meta_title": "Romantic Escapes | The Uncharted Route",
        "meta_description": (
            "Discover romantic escapes, intimate experiences and "
            "memorable journeys designed for couples."
        ),
    },
    {
        "name": "Nature & Landscapes",
        "slug": "nature-landscapes",
        "description": (
            "Experiences that celebrate natural environments, "
            "distinctive landscapes, scenic viewpoints and the "
            "beauty of the outdoors. May include nature walks, "
            "landscape exploration and scenic excursions."
        ),
        "color": "#5C6B32",
        "icon": "trees",
        "meta_title": "Nature & Landscape Experiences | The Uncharted Route",
        "meta_description": (
            "Discover natural landscapes, scenic destinations "
            "and outdoor experiences in remarkable places."
        ),
    },
    {
        "name": "Water Adventures",
        "slug": "water-adventures",
        "description": (
            "Experiences involving water-based activities and "
            "exploration. May include boating, kayaking, rafting, "
            "snorkelling, diving and other aquatic activities "
            "where locally available."
        ),
        "color": "#1F5138",
        "icon": "waves",
        "meta_title": "Water Adventures | The Uncharted Route",
        "meta_description": (
            "Explore water adventures, aquatic activities and "
            "memorable experiences on rivers, lakes and oceans."
        ),
    },
    {
        "name": "Historical Discovery",
        "slug": "historical-discovery",
        "description": (
            "Experiences exploring significant historical places, "
            "events, archaeological sites, monuments and the stories "
            "that shaped a destination. May include guided visits "
            "and historical interpretation."
        ),
        "color": "#D89B24",
        "icon": "scroll",
        "meta_title": "Historical Discovery Experiences | The Uncharted Route",
        "meta_description": (
            "Discover historical landmarks, significant places "
            "and the stories behind destinations around the world."
        ),
    },
    {
        "name": "Architecture",
        "slug": "architecture",
        "description": (
            "Experiences focused on distinctive buildings, "
            "architectural landmarks, urban design and built "
            "environments. May include historic architecture, "
            "contemporary structures and guided architectural walks."
        ),
        "color": "#66736B",
        "icon": "building-2",
        "meta_title": "Architecture Experiences | The Uncharted Route",
        "meta_description": (
            "Explore remarkable architecture, iconic buildings "
            "and the design stories that shape destinations."
        ),
    },
    {
        "name": "Local Traditions & Crafts",
        "slug": "local-traditions-crafts",
        "description": (
            "Experiences that introduce travellers to local "
            "craftsmanship, artisans, traditional skills and "
            "creative practices. Cultural details should reflect "
            "the specific community and tradition being explored."
        ),
        "color": "#C96A2C",
        "icon": "palette",
        "meta_title": "Local Traditions & Crafts | The Uncharted Route",
        "meta_description": (
            "Discover local artisans, traditional crafts and "
            "creative cultural experiences around the world."
        ),
    },
    {
        "name": "Food Tasting",
        "slug": "food-tasting",
        "description": (
            "Experiences centred on sampling and discovering "
            "foods, regional dishes, ingredients and culinary "
            "specialities. May include guided tastings, food tours "
            "and introductions to local flavours."
        ),
        "color": "#C96A2C",
        "icon": "utensils",
        "meta_title": "Food Tasting Experiences | The Uncharted Route",
        "meta_description": (
            "Discover food tastings, regional flavours and "
            "culinary encounters across different destinations."
        ),
    },
    {
        "name": "Farm Experiences",
        "slug": "farm-experiences",
        "description": (
            "Experiences taking place on farms, plantations and "
            "agricultural properties. May introduce guests to "
            "cultivation, production processes, farm life, "
            "harvest activities and farm-to-table discovery."
        ),
        "color": "#5C6B32",
        "icon": "sprout",
        "meta_title": "Farm Experiences | The Uncharted Route",
        "meta_description": (
            "Explore farms, plantations, agricultural experiences "
            "and the stories behind locally produced goods."
        ),
    },
    {
        "name": "Coffee & Tea Experiences",
        "slug": "coffee-tea-experiences",
        "description": (
            "Experiences exploring coffee and tea, from cultivation "
            "and harvesting to processing, preparation and tasting. "
            "May include plantation visits, guided tastings and "
            "introductions to local production."
        ),
        "color": "#5C6B32",
        "icon": "coffee",
        "meta_title": "Coffee & Tea Experiences | The Uncharted Route",
        "meta_description": (
            "Discover coffee and tea farms, plantation visits, "
            "tastings and the stories behind every cup."
        ),
    },
    {
        "name": "Island Experiences",
        "slug": "island-experiences",
        "description": (
            "Experiences based on discovering islands and their "
            "distinctive environments, communities, landscapes "
            "and activities. May include island exploration, "
            "cultural discovery and coastal excursions."
        ),
        "color": "#1F5138",
        "icon": "palmtree",
        "meta_title": "Island Experiences | The Uncharted Route",
        "meta_description": (
            "Explore island experiences, distinctive island "
            "landscapes and memorable coastal discoveries."
        ),
    },
    {
        "name": "Beach & Marine Life",
        "slug": "beach-marine-life",
        "description": (
            "Experiences involving beaches, marine ecosystems "
            "and ocean wildlife. May include responsible marine "
            "observation, beach exploration and activities that "
            "introduce guests to coastal environments."
        ),
        "color": "#1F5138",
        "icon": "fish",
        "meta_title": "Beach & Marine Life Experiences | The Uncharted Route",
        "meta_description": (
            "Discover beaches, marine wildlife and coastal "
            "experiences across beautiful ocean destinations."
        ),
    },
    {
        "name": "City Discovery",
        "slug": "city-discovery",
        "description": (
            "Experiences exploring the character, neighbourhoods, "
            "landmarks, everyday life and distinctive attractions "
            "of cities. May include guided city walks, urban "
            "exploration and local discovery."
        ),
        "color": "#66736B",
        "icon": "map",
        "meta_title": "City Discovery Experiences | The Uncharted Route",
        "meta_description": (
            "Discover cities, neighbourhoods, iconic landmarks "
            "and meaningful urban experiences around the world."
        ),
    },
    {
        "name": "Shopping & Markets",
        "slug": "shopping-markets",
        "description": (
            "Experiences exploring local markets, shopping "
            "districts, artisan stalls and distinctive retail "
            "environments. May include opportunities to discover "
            "local products, crafts and food markets."
        ),
        "color": "#D89B24",
        "icon": "shopping-bag",
        "meta_title": "Shopping & Market Experiences | The Uncharted Route",
        "meta_description": (
            "Explore local markets, shopping experiences, "
            "artisan products and distinctive retail destinations."
        ),
    },
    {
        "name": "Wellness & Spa",
        "slug": "wellness-spa",
        "description": (
            "Experiences focused on relaxation, personal wellbeing "
            "and rejuvenation. May include spa treatments, wellness "
            "rituals, restorative activities and peaceful retreats."
        ),
        "color": "#5C6B32",
        "icon": "flower-2",
        "meta_title": "Wellness & Spa Experiences | The Uncharted Route",
        "meta_description": (
            "Discover wellness experiences, spa retreats, "
            "relaxation and restorative escapes."
        ),
    },
    {
        "name": "Private Experiences",
        "slug": "private-experiences",
        "description": (
            "Experiences arranged for an individual, couple, "
            "family or private group rather than a general shared "
            "departure. Privacy and personalisation depend on "
            "the arrangements confirmed for each experience."
        ),
        "color": "#D89B24",
        "icon": "lock-keyhole",
        "meta_title": "Private Experiences | The Uncharted Route",
        "meta_description": (
            "Explore private and personalised experiences "
            "designed around your interests and travel preferences."
        ),
    },
]


# ============================================================
# SIGNATURE MOMENTS
# ============================================================

# Format:
# title, short_description, full_description, moment_type,
# expected_time, estimated_duration, best_season,
# photography_recommended, emotional_impact

SIGNATURE_MOMENTS = [
    {
        "title": "Sunrise Over the Natural World",
        "short_description": (
            "Welcome the day as the first light transforms "
            "the surrounding natural landscape."
        ),
        "full_description": (
            "Experience the quiet beauty of sunrise as the first "
            "light spreads across the landscape. Changing colours, "
            "soft morning light and the sounds of the natural "
            "environment create a memorable beginning to the day. "
            "The setting and scenery will depend on the destination."
        ),
        "moment_type": "Scenic",
        "expected_time": "Sunrise",
        "estimated_duration": 45,
        "best_season": "Clear-weather mornings",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "An Unforgettable Wildlife Encounter",
        "short_description": (
            "Observe wildlife in a natural setting and appreciate "
            "the privilege of encountering animals in the wild."
        ),
        "full_description": (
            "Spend a memorable moment observing wildlife in its "
            "natural environment. The encounter offers an opportunity "
            "to appreciate animal behaviour, habitat and the "
            "importance of respecting wildlife. The species and "
            "sightings depend on the destination and natural conditions."
        ),
        "moment_type": "Wildlife",
        "expected_time": "Morning",
        "estimated_duration": 60,
        "best_season": "Depends on local wildlife patterns",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "Watching Wildlife in Its Natural Habitat",
        "short_description": (
            "Discover the behaviour and surroundings of animals "
            "as they move through their natural habitats."
        ),
        "full_description": (
            "Take time to observe animals within the environments "
            "where they naturally live. This moment encourages "
            "patience, curiosity and a deeper appreciation of "
            "wildlife and the ecosystems that support it. Sightings "
            "and animal activity cannot be guaranteed."
        ),
        "moment_type": "Wildlife",
        "expected_time": "Morning",
        "estimated_duration": 60,
        "best_season": "Local wildlife-viewing season",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "The Moment Birds Take Flight",
        "short_description": (
            "Witness the movement, colour and beauty of birds "
            "in their natural environment."
        ),
        "full_description": (
            "Observe birds as they move through their natural "
            "surroundings, take flight or gather in their habitats. "
            "The moment offers opportunities to appreciate bird "
            "behaviour, calls, colours and movement. Species and "
            "activity vary according to the location and season."
        ),
        "moment_type": "Wildlife",
        "expected_time": "Morning",
        "estimated_duration": 30,
        "best_season": "Local birding and migration seasons",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Witnessing a Spectacular Wildlife Migration",
        "short_description": (
            "Experience the remarkable movement of wildlife "
            "across natural landscapes during migration."
        ),
        "full_description": (
            "Discover the extraordinary movement of wildlife "
            "during a seasonal migration. This experience can "
            "reveal the scale, instinct and natural rhythms of "
            "animal movement. Migration timing and viewing "
            "opportunities depend entirely on the species, "
            "destination and prevailing environmental conditions."
        ),
        "moment_type": "Wildlife",
        "expected_time": "Morning",
        "estimated_duration": 90,
        "best_season": "During the local migration season",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "Discovering a Hidden Natural Wonder",
        "short_description": (
            "Explore a remarkable natural feature and appreciate "
            "the beauty of an unexpected discovery."
        ),
        "full_description": (
            "Discover a distinctive natural feature such as a "
            "waterfall, geological formation, forest setting, "
            "viewpoint or other remarkable landscape. The experience "
            "encourages curiosity and a closer appreciation of "
            "the natural environment."
        ),
        "moment_type": "Scenic",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "Suitable local weather conditions",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Reaching a Viewpoint Worth the Journey",
        "short_description": (
            "Arrive at a rewarding viewpoint after a journey "
            "through the surrounding landscape."
        ),
        "full_description": (
            "Enjoy the satisfaction of reaching a viewpoint "
            "that reveals a remarkable perspective of the "
            "surrounding environment. The journey may involve "
            "walking, hiking or another form of exploration, "
            "depending on the destination and access conditions."
        ),
        "moment_type": "Adventure",
        "expected_time": "Morning",
        "estimated_duration": 45,
        "best_season": "Favourable hiking conditions",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "The Thrill of an Unforgettable Outdoor Adventure",
        "short_description": (
            "Enjoy an exciting outdoor activity that creates "
            "a lasting sense of achievement and discovery."
        ),
        "full_description": (
            "Take part in an outdoor adventure that brings "
            "excitement, movement and discovery together. "
            "The activity may involve exploration, physical "
            "challenge or interaction with the natural environment. "
            "Specific requirements and safety conditions depend "
            "on the activity provider."
        ),
        "moment_type": "Adventure",
        "expected_time": "Daytime",
        "estimated_duration": 90,
        "best_season": "Suitable activity and weather conditions",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "Exploring a Scenic Trail on Foot",
        "short_description": (
            "Discover the surrounding landscape through a "
            "guided or independent walking experience."
        ),
        "full_description": (
            "Explore a designated trail while taking in the "
            "landscape, natural surroundings and details that "
            "may otherwise be missed. The route, terrain, distance "
            "and physical requirements should be confirmed "
            "for the individual experience."
        ),
        "moment_type": "Adventure",
        "expected_time": "Morning",
        "estimated_duration": 90,
        "best_season": "Suitable trail conditions",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Discovering the World Beneath the Water",
        "short_description": (
            "Explore an underwater environment and discover "
            "the life and scenery beneath the surface."
        ),
        "full_description": (
            "Discover the underwater environment through an "
            "appropriate aquatic activity such as snorkelling "
            "or diving, where available. Observe the colours, "
            "formations and marine life that make each aquatic "
            "environment distinctive. Visibility, safety and "
            "access depend on local conditions."
        ),
        "moment_type": "Adventure",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "Suitable water visibility and conditions",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "A Journey Through Extraordinary Landscapes",
        "short_description": (
            "Travel through distinctive scenery and discover "
            "the changing character of the landscape."
        ),
        "full_description": (
            "Experience a scenic journey through remarkable "
            "surroundings, taking time to appreciate changing "
            "landscapes, natural features and local environments. "
            "The journey may be by road, on foot or through "
            "another appropriate mode of exploration."
        ),
        "moment_type": "Scenic",
        "expected_time": "Daytime",
        "estimated_duration": 90,
        "best_season": "Favourable travel and viewing conditions",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Discovering the Stories Behind Local Heritage",
        "short_description": (
            "Explore the history, identity and stories that "
            "give a place its distinctive character."
        ),
        "full_description": (
            "Discover the people, events, traditions and historical "
            "influences that have shaped a destination. Through "
            "interpretation and storytelling, guests gain a deeper "
            "understanding of the place and the communities "
            "connected to its heritage."
        ),
        "moment_type": "Cultural",
        "expected_time": "Afternoon",
        "estimated_duration": 60,
        "best_season": "Year-round, subject to site availability",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Meeting the Artisans Behind Local Craftsmanship",
        "short_description": (
            "Meet local makers and discover the skill and "
            "creativity behind traditional or contemporary crafts."
        ),
        "full_description": (
            "Spend time discovering the work of local artisans "
            "and the techniques, materials and creative decisions "
            "behind their craft. Where appropriate, guests may "
            "observe demonstrations, ask questions and learn "
            "about the cultural or practical significance of "
            "the work within its local context."
        ),
        "moment_type": "Cultural",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "Year-round, subject to workshop availability",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Experiencing a Living Cultural Tradition",
        "short_description": (
            "Encounter a cultural practice or tradition as "
            "it is meaningfully expressed by its community."
        ),
        "full_description": (
            "Experience a living cultural tradition through "
            "a respectful introduction to the people, practices "
            "and meanings connected to it. The experience should "
            "be presented in collaboration with or with appropriate "
            "context from the relevant community. Traditions and "
            "participation depend on local customs and availability."
        ),
        "moment_type": "Cultural",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "According to the local cultural calendar",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "Walking Through Centuries of History",
        "short_description": (
            "Explore a historic setting and discover the "
            "stories preserved within its streets and landmarks."
        ),
        "full_description": (
            "Walk through a historically significant setting "
            "and discover the architecture, events and stories "
            "that shaped it over time. The experience may include "
            "historic streets, archaeological areas, monuments "
            "or preserved buildings, depending on the destination."
        ),
        "moment_type": "Cultural",
        "expected_time": "Morning",
        "estimated_duration": 75,
        "best_season": "Year-round, subject to site access",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Discovering the Beauty of Remarkable Architecture",
        "short_description": (
            "Appreciate distinctive architecture and the "
            "design stories behind remarkable buildings."
        ),
        "full_description": (
            "Explore architectural features, materials, design "
            "influences and the stories behind notable buildings "
            "or built environments. The experience may include "
            "historic structures, contemporary landmarks or "
            "distinctive urban spaces."
        ),
        "moment_type": "Cultural",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "Year-round, with suitable visiting conditions",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "From Farm to Table: Discovering Local Flavours",
        "short_description": (
            "Explore the connection between local produce, "
            "food traditions and the finished dining experience."
        ),
        "full_description": (
            "Discover how local ingredients and agricultural "
            "products contribute to the food of a destination. "
            "The experience may include an introduction to "
            "production, ingredient selection, preparation "
            "and tasting. Available produce depends on the "
            "location and harvest season."
        ),
        "moment_type": "Dining",
        "expected_time": "Afternoon",
        "estimated_duration": 90,
        "best_season": "According to local harvest seasons",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "From Farm to Cup: A Coffee or Tea Experience",
        "short_description": (
            "Discover the journey from cultivation and processing "
            "to preparing and tasting coffee or tea."
        ),
        "full_description": (
            "Explore the journey behind a cup of coffee or tea, "
            "from growing conditions and harvesting to processing, "
            "preparation and tasting. The experience offers "
            "insight into the people, techniques and characteristics "
            "that shape the final drink."
        ),
        "moment_type": "Dining",
        "expected_time": "Morning",
        "estimated_duration": 60,
        "best_season": "According to local harvest and processing seasons",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "A Guided Taste of Local Cuisine",
        "short_description": (
            "Sample distinctive local dishes and discover "
            "the flavours associated with a destination."
        ),
        "full_description": (
            "Enjoy a guided introduction to local cuisine through "
            "a selection of dishes, ingredients and flavours. "
            "The experience may include explanations of preparation, "
            "regional influences and the place of food within "
            "everyday life and local food culture."
        ),
        "moment_type": "Dining",
        "expected_time": "Afternoon",
        "estimated_duration": 60,
        "best_season": "Year-round, subject to food availability",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Learning the Art of a Traditional Recipe",
        "short_description": (
            "Discover local cooking techniques through "
            "a hands-on culinary learning experience."
        ),
        "full_description": (
            "Learn about a local dish through its ingredients, "
            "preparation methods and culinary traditions. "
            "Where appropriate, guests may take part in preparing "
            "a recipe while learning about its regional and "
            "cultural context from a host or instructor."
        ),
        "moment_type": "Cultural",
        "expected_time": "Daytime",
        "estimated_duration": 90,
        "best_season": "Year-round, subject to ingredient availability",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "An Intimate Dining Experience in a Beautiful Setting",
        "short_description": (
            "Enjoy a memorable dining occasion in a setting "
            "chosen for its atmosphere and surroundings."
        ),
        "full_description": (
            "Enjoy a thoughtfully arranged dining experience "
            "where the setting, atmosphere and food come together "
            "to create a memorable occasion. The experience may "
            "take place in a scenic, private, historic or otherwise "
            "distinctive location, depending on the arrangements."
        ),
        "moment_type": "Dining",
        "expected_time": "Evening",
        "estimated_duration": 120,
        "best_season": "Suitable local weather and dining conditions",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "A Private Coastal Sunset Experience",
        "short_description": (
            "Enjoy the changing colours of sunset in a "
            "beautiful coastal setting."
        ),
        "full_description": (
            "Experience the calm and beauty of sunset along "
            "the coast. Changing light, ocean views and the "
            "surrounding atmosphere create an opportunity to "
            "slow down and appreciate the setting. Privacy "
            "depends on the location and confirmed arrangements."
        ),
        "moment_type": "Coastal",
        "expected_time": "Sunset",
        "estimated_duration": 60,
        "best_season": "Favourable coastal weather",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "Discovering a Secluded Beach",
        "short_description": (
            "Explore a quieter stretch of coastline and "
            "appreciate its natural surroundings."
        ),
        "full_description": (
            "Discover a beach or coastal setting away from "
            "the busiest areas, where the natural surroundings "
            "can be appreciated at a more relaxed pace. Access, "
            "privacy, tides and environmental conditions vary "
            "by location and should be confirmed."
        ),
        "moment_type": "Coastal",
        "expected_time": "Morning",
        "estimated_duration": 60,
        "best_season": "Suitable beach and sea conditions",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Witnessing the Beauty of Marine Life",
        "short_description": (
            "Discover marine life and appreciate the "
            "richness of underwater and coastal ecosystems."
        ),
        "full_description": (
            "Observe marine life in its natural environment "
            "through an appropriate activity or guided encounter. "
            "The experience may introduce guests to the diversity "
            "of marine ecosystems and the importance of responsible "
            "interaction. Sightings depend on natural conditions."
        ),
        "moment_type": "Wildlife",
        "expected_time": "Daytime",
        "estimated_duration": 60,
        "best_season": "Local marine seasons and suitable sea conditions",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
    {
        "title": "A Breathtaking View Over the Ocean",
        "short_description": (
            "Take in a memorable ocean panorama from "
            "a distinctive coastal viewpoint."
        ),
        "full_description": (
            "Pause to appreciate a wide ocean view from "
            "a beach, viewpoint, coastal property or other "
            "distinctive setting. The changing light, horizon "
            "and surrounding landscape create a memorable "
            "scenic moment."
        ),
        "moment_type": "Scenic",
        "expected_time": "Sunset",
        "estimated_duration": 45,
        "best_season": "Clear-weather periods",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Discovering a City's Hidden Gems",
        "short_description": (
            "Explore lesser-known places and discover "
            "the details that give a city its character."
        ),
        "full_description": (
            "Go beyond the most familiar landmarks to discover "
            "interesting neighbourhoods, local spaces, distinctive "
            "businesses and lesser-known places. The experience "
            "offers a more personal perspective on the city's "
            "character and everyday life."
        ),
        "moment_type": "Cultural",
        "expected_time": "Afternoon",
        "estimated_duration": 90,
        "best_season": "Year-round, subject to local opening hours",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Experiencing the Energy of a Local Market",
        "short_description": (
            "Explore a lively market and discover its "
            "products, people and everyday atmosphere."
        ),
        "full_description": (
            "Experience the activity and character of a local "
            "market. Discover its products, food, crafts and "
            "the people who contribute to its daily rhythm. "
            "Market days, opening hours and available products "
            "depend on the destination."
        ),
        "moment_type": "Cultural",
        "expected_time": "Morning",
        "estimated_duration": 60,
        "best_season": "Year-round, according to market days",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "Admiring an Iconic City Skyline",
        "short_description": (
            "Take in the scale and character of a city "
            "from a memorable skyline viewpoint."
        ),
        "full_description": (
            "Enjoy a distinctive view across a city, observing "
            "its skyline, architecture and surrounding urban "
            "landscape. The moment may be experienced from "
            "a public viewpoint, rooftop, landmark or another "
            "suitable location."
        ),
        "moment_type": "Scenic",
        "expected_time": "Evening",
        "estimated_duration": 45,
        "best_season": "Clear-weather evenings",
        "photography_recommended": True,
        "emotional_impact": "High",
    },
    {
        "title": "A Moment of Complete Relaxation",
        "short_description": (
            "Step away from the pace of everyday life "
            "and enjoy a restorative moment."
        ),
        "full_description": (
            "Take time to rest and reconnect through a "
            "relaxing experience in a peaceful setting. "
            "Depending on the offering, this may involve "
            "a spa treatment, wellness activity or quiet "
            "time in surroundings chosen for comfort and calm."
        ),
        "moment_type": "Luxury",
        "expected_time": "Afternoon",
        "estimated_duration": 90,
        "best_season": "Year-round, subject to availability",
        "photography_recommended": False,
        "emotional_impact": "High",
    },
    {
        "title": "An Extraordinary Escape in a Beautiful Setting",
        "short_description": (
            "Enjoy a distinctive escape where the setting "
            "becomes part of the experience."
        ),
        "full_description": (
            "Enjoy time in an exceptional setting selected "
            "for its atmosphere, surroundings and character. "
            "The experience may include a memorable stay, "
            "a private retreat or a carefully arranged "
            "occasion. The specific offering depends on "
            "the destination and confirmed arrangements."
        ),
        "moment_type": "Luxury",
        "expected_time": "Evening",
        "estimated_duration": 90,
        "best_season": "According to local weather and property season",
        "photography_recommended": True,
        "emotional_impact": "Exceptional",
    },
]


# ============================================================
# POPULATION HELPERS
# ============================================================

def insert_missing_tags(session):
    inserted = 0
    skipped = 0

    for data in NEW_TAGS:
        existing = (
            session.query(ExperienceTag)
            .filter_by(slug=data["slug"])
            .first()
        )

        if existing:
            print(f"  SKIPPED TAG: {data['name']} (slug already exists)")
            skipped += 1
            continue

        tag = ExperienceTag(
            **data,
            featured=False,
            active=True,
            sort_order=6 + NEW_TAGS.index(data) + 1,
        )

        session.add(tag)
        inserted += 1

        print(f"  ADDED TAG: {data['name']}")

    return inserted, skipped


def insert_missing_signature_moments(session):
    inserted = 0
    skipped = 0

    for index, data in enumerate(SIGNATURE_MOMENTS, start=1):
        existing = (
            session.query(SignatureMoment)
            .filter(
                SignatureMoment.title.ilike(data["title"])
            )
            .first()
        )

        if existing:
            print(
                f"  SKIPPED MOMENT: {data['title']} "
                "(title already exists)"
            )
            skipped += 1
            continue

        moment = SignatureMoment(
            **data,
            hero_media_id=None,
            featured=True,
            display_order=index,
            active=True,
        )

        session.add(moment)
        inserted += 1

        print(f"  ADDED MOMENT: {data['title']}")

    return inserted, skipped


# ============================================================
# MAIN
# ============================================================

def main():
    with app.app_context():
        session = ExperienceTag.query.session

        print("\n" + "=" * 75)
        print("THE UNCHARTED ROUTE")
        print("GLOBAL REUSABLE CATALOGUE POPULATION")
        print("=" * 75)

        existing_tag_count = session.query(ExperienceTag).count()
        existing_moment_count = session.query(SignatureMoment).count()

        print("\nCURRENT DATABASE COUNTS")
        print("-" * 75)
        print(f"Experience Tags:   {existing_tag_count}")
        print(f"Signature Moments: {existing_moment_count}")

        print("\nINSERTING NEW EXPERIENCE TAGS")
        print("-" * 75)

        tags_inserted, tags_skipped = insert_missing_tags(session)

        print("\nINSERTING SIGNATURE MOMENTS")
        print("-" * 75)

        moments_inserted, moments_skipped = (
            insert_missing_signature_moments(session)
        )

        try:
            session.commit()

        except Exception:
            session.rollback()
            raise

        final_tag_count = session.query(ExperienceTag).count()
        final_moment_count = session.query(SignatureMoment).count()

        print("\n" + "=" * 75)
        print("POPULATION SUMMARY")
        print("=" * 75)

        print("\nEXPERIENCE TAGS")
        print(f"  Inserted: {tags_inserted}")
        print(f"  Skipped:  {tags_skipped}")
        print(f"  Total:    {final_tag_count}")

        print("\nSIGNATURE MOMENTS")
        print(f"  Inserted: {moments_inserted}")
        print(f"  Skipped:  {moments_skipped}")
        print(f"  Total:    {final_moment_count}")

        print("\nFINAL VERIFICATION")
        print("-" * 75)

        print(
            "All Signature Moments without hero media:",
            session.query(SignatureMoment)
            .filter(SignatureMoment.hero_media_id.is_(None))
            .count(),
        )

        print(
            "All Signature Moments without experience associations:",
            session.query(SignatureMoment)
            .filter(~SignatureMoment.experiences.any())
            .count(),
        )

        print("\nCatalogue population completed.")
        print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
