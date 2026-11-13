
"""
THE UNCHARTED ROUTE
Create the remaining approved launch-catalogue experiences.

Run from Flask shell:
    exec(open("scripts/create_remaining_experiences.py", encoding="utf-8").read())
    main()

Safety:
- Creates missing records only.
- Does not update existing experiences.
- All new records are active and not featured.
- Every experience must have an active cancellation policy.
- Stops before writing if a required category, destination, policy, or image is missing.
- Serengeti must exist in the Destinations CMS first.
"""

from extensions import db
from app.models.experience import Experience
from app.models.experience_category import ExperienceCategory
from app.models.destination import Destination
from app.models.media_asset import MediaAsset
from app.models.media_folder import MediaFolder
from app.models.media_asset_folder import MediaAssetFolder
from app.models.cancellation_policy import CancellationPolicy
from app.models.accessibility import Accessibility
from app.models.conservation_story import ConservationStory


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

STANDARD_POLICY_ID = 2
SAFARI_POLICY_ID = 3
STAY_POLICY_ID = 4

# Only the existing Experiences DAM folder is used for catalogue images.
IMAGE_FOLDER_NAME = "Experiences"

# These are catalogue starting values only. Validate actual supplier costs,
# park fees, permits, taxes and profit margins before publishing prices.
EXPERIENCES = [
    # -----------------------------------------------------------------------
    # SAFARI & WILDLIFE — additional products
    # -----------------------------------------------------------------------
    {
        "code": "WNA-009",
        "title": "Ol Pejeta Conservancy & Rhino Experience",
        "slug": "ol-pejeta-conservancy-rhino-experience",
        "category": "Safari & Wildlife",
        "destination": "Ol Pejeta Conservancy",
        "short": "Discover Ol Pejeta's remarkable wildlife and conservation work on a guided conservancy experience.",
        "description": (
            "Explore Ol Pejeta Conservancy, a leading wildlife conservation "
            "landscape in Kenya. This experience combines guided wildlife "
            "viewing with an introduction to the conservancy's conservation "
            "work. Specific wildlife sightings and access to conservation "
            "facilities depend on conditions, availability and permissions."
        ),
        "duration": "Full day",
        "meeting": "Nairobi or an agreed meeting point, subject to itinerary",
        "location": "Ol Pejeta Conservancy, Laikipia County, Kenya",
        "price": 35000,
        "difficulty": "Easy",
        "destination_aliases": ["Ol Pejeta", "Ol Pejeta Conservancy"],
        "accessibility": "Wildlife Terrain",
        "policy_id": SAFARI_POLICY_ID,
        "conservation": "Black Rhino Conservation",
        "order": 1,
    },
    {
        "code": "WNA-010",
        "title": "Serengeti Migration Safari",
        "slug": "serengeti-migration-safari",
        "category": "Safari & Wildlife",
        "destination": "Serengeti National Park",
        "short": "Experience the sweeping landscapes and extraordinary wildlife of Tanzania's Serengeti.",
        "description": (
            "A multi-day safari concept exploring the Serengeti's wildlife, "
            "open plains and seasonal migration landscapes. The route, length "
            "of stay, accommodation and wildlife-viewing areas will be "
            "confirmed according to travel dates, supplier availability, "
            "park regulations and seasonal conditions. Migration sightings "
            "cannot be guaranteed."
        ),
        "duration": "Multi-day",
        "meeting": "Confirmed after itinerary and international travel arrangements",
        "location": "Serengeti National Park, Tanzania",
        "price": 120000,
        "difficulty": "Easy",
        "destination_aliases": [
            "Serengeti",
            "Serengeti National Park",
            "Serengeti National Park, Tanzania",
        ],
        "accessibility": "Wildlife Terrain",
        "policy_id": SAFARI_POLICY_ID,
        "conservation": None,
        "order": 2,
    },

    # -----------------------------------------------------------------------
    # CULTURE, HERITAGE & CITY DISCOVERY
    # -----------------------------------------------------------------------
    {
        "code": "CUL-001",
        "title": "Nairobi City Discovery",
        "slug": "nairobi-city-discovery",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Nairobi",
        "short": "Discover Nairobi through its landmarks, neighbourhoods and everyday city life.",
        "description": (
            "A curated introduction to Nairobi combining selected city "
            "landmarks, local stories and neighbourhood discoveries. The "
            "final route is agreed with the guest and depends on opening "
            "hours, traffic and the selected stops."
        ),
        "duration": "Half day or full day",
        "meeting": "Central Nairobi or an agreed pickup point",
        "location": "Nairobi, Kenya",
        "price": 8500,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 1,
    },
    {
        "code": "CUL-002",
        "title": "Bomas of Kenya Cultural Experience",
        "slug": "bomas-of-kenya-cultural-experience",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Nairobi",
        "short": "Explore Kenyan cultural traditions through a visit to Bomas of Kenya.",
        "description": (
            "A cultural outing centred on Bomas of Kenya and its presentation "
            "of traditions from different Kenyan communities. Performance "
            "times, access and the final itinerary must be confirmed before "
            "the experience is sold."
        ),
        "duration": "Half day",
        "meeting": "Nairobi or an agreed pickup point",
        "location": "Bomas of Kenya, Nairobi, Kenya",
        "price": 7500,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 2,
    },
    {
        "code": "CUL-003",
        "title": "Mombasa Old Town & Fort Jesus",
        "slug": "mombasa-old-town-fort-jesus",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Mombasa",
        "short": "Discover Mombasa's layered coastal history through Old Town and Fort Jesus.",
        "description": (
            "A guided heritage experience exploring the historic streets "
            "and architecture of Mombasa Old Town, with a visit to Fort "
            "Jesus where entry and opening arrangements permit. The route "
            "respects local communities and site rules."
        ),
        "duration": "Half day",
        "meeting": "Mombasa Old Town or an agreed pickup point",
        "location": "Mombasa, Kenya",
        "price": 8500,
        "difficulty": "Easy",
        "accessibility": "Moderate Mobility",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 3,
    },
    {
        "code": "CUL-004",
        "title": "Lamu Old Town Heritage Escape",
        "slug": "lamu-old-town-heritage-escape",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Lamu Old Town",
        "short": "Slow down and explore Lamu's historic streets, Swahili heritage and island atmosphere.",
        "description": (
            "A heritage-led visit to Lamu Old Town focused on its historic "
            "architecture, Swahili culture, local crafts and distinctive "
            "island atmosphere. Boat transfers, accommodation and other "
            "logistics are included only when specified in the confirmed "
            "itinerary."
        ),
        "duration": "Half day or multi-day",
        "meeting": "Lamu, with meeting details confirmed before travel",
        "location": "Lamu Old Town, Lamu County, Kenya",
        "price": 12000,
        "difficulty": "Easy",
        "accessibility": "Moderate Mobility",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 4,
    },
    {
        "code": "CUL-005",
        "title": "Kibera Community-Led Cultural Visit",
        "slug": "kibera-community-led-cultural-visit",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Nairobi",
        "short": "Learn about community initiatives and everyday life through a respectful, locally led visit.",
        "description": (
            "A community-led visit designed around local knowledge, "
            "community initiatives and respectful cultural exchange. "
            "Bookings must use an appropriate local guide or community "
            "partner. Photography, access and donations follow the "
            "community partner's guidance; residents are not treated "
            "as attractions."
        ),
        "duration": "Half day",
        "meeting": "Confirmed with the local guide or community partner",
        "location": "Kibera, Nairobi, Kenya",
        "price": 6500,
        "difficulty": "Easy",
        "accessibility": "Moderate Mobility",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 5,
    },
    {
        "code": "CUL-006",
        "title": "Nairobi Art, Galleries & Creative Spaces",
        "slug": "nairobi-art-galleries-creative-spaces",
        "category": "Culture, Heritage & City Discovery",
        "destination": "Nairobi",
        "short": "Discover Nairobi's art scene through selected galleries, studios and creative spaces.",
        "description": (
            "A curated route through selected Nairobi galleries, art spaces "
            "or creative studios. Stops are chosen according to current "
            "exhibitions, opening hours and any arrangements required by "
            "the participating venues."
        ),
        "duration": "Half day",
        "meeting": "Central Nairobi or an agreed pickup point",
        "location": "Nairobi, Kenya",
        "price": 8500,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 6,
    },

    # -----------------------------------------------------------------------
    # COASTAL & ISLAND ESCAPES
    # -----------------------------------------------------------------------
    {
        "code": "COA-001",
        "title": "Diani Beach Escape",
        "slug": "diani-beach-escape",
        "category": "Coastal & Island Escapes",
        "destination": "Diani Beach",
        "short": "Enjoy a curated coastal escape with time for the beach and optional local experiences.",
        "description": (
            "A flexible Diani getaway built around beach time, coastal "
            "scenery and optional activities selected with the guest. "
            "Accommodation, transfers, meals and marine activities are "
            "included only where explicitly stated in the final package."
        ),
        "duration": "Full day or multi-day",
        "meeting": "Diani Beach or an agreed transfer point",
        "location": "Diani Beach, Kwale County, Kenya",
        "price": 15000,
        "difficulty": "Easy",
        "accessibility": "Coastal & Beach Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 1,
    },
    {
        "code": "COA-002",
        "title": "Watamu Marine Discovery",
        "slug": "watamu-marine-discovery",
        "category": "Coastal & Island Escapes",
        "destination": "Watamu",
        "short": "Discover Watamu's coastal scenery and marine environment through locally available activities.",
        "description": (
            "A coastal experience built around Watamu's marine environment "
            "and shoreline. Any boat trip, snorkelling, marine park entry "
            "or conservation activity depends on conditions, permissions "
            "and confirmed local operators."
        ),
        "duration": "Full day or multi-day",
        "meeting": "Watamu, with meeting details confirmed before travel",
        "location": "Watamu, Kilifi County, Kenya",
        "price": 14000,
        "difficulty": "Easy",
        "accessibility": "Coastal & Beach Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": "Sea Turtle Conservation",
        "order": 2,
    },
    {
        "code": "COA-003",
        "title": "Lamu Island Heritage Escape",
        "slug": "lamu-island-heritage-escape",
        "category": "Coastal & Island Escapes",
        "destination": "Lamu Old Town",
        "short": "Enjoy a slower island escape combining coastal scenery and Lamu's unique heritage.",
        "description": (
            "A coastal getaway focused on Lamu's island atmosphere, "
            "shoreline and heritage. Accommodation, transfers and boat "
            "excursions depend on the selected itinerary and are included "
            "only when stated in the confirmed package."
        ),
        "duration": "Multi-day",
        "meeting": "Lamu, with meeting details confirmed before travel",
        "location": "Lamu County, Kenya",
        "price": 22000,
        "difficulty": "Easy",
        "accessibility": "Coastal & Beach Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 3,
    },
    {
        "code": "COA-004",
        "title": "Zanzibar Island Escape",
        "slug": "zanzibar-island-escape",
        "category": "Coastal & Island Escapes",
        "destination": "Zanzibar",
        "short": "Plan an island getaway combining Zanzibar's coastline, historic Stone Town and relaxed island time.",
        "description": (
            "A curated international island escape combining selected "
            "Zanzibar experiences, coastal downtime and optional heritage "
            "exploration. International flights, entry requirements, "
            "accommodation, transfers and excursions must be explicitly "
            "confirmed in the final package. Travel documents and entry "
            "rules are the traveller's responsibility."
        ),
        "duration": "Multi-day",
        "meeting": "Confirmed after travel arrangements are agreed",
        "location": "Zanzibar, Tanzania",
        "price": 65000,
        "difficulty": "Easy",
        "accessibility": "Coastal & Beach Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 4,
    },

    # -----------------------------------------------------------------------
    # LUXURY ESCAPES
    # -----------------------------------------------------------------------
    {
        "code": "LUX-001",
        "title": "Luxury Maasai Mara Safari",
        "slug": "luxury-maasai-mara-safari",
        "category": "Luxury Escapes",
        "destination": "Maasai Mara National Reserve",
        "short": "A premium Mara safari concept with carefully selected accommodation and personalized planning.",
        "description": (
            "A premium safari package designed around selected Mara "
            "accommodation, guided wildlife viewing and personalized "
            "service. Camp or lodge, park fees, transport, meals and "
            "activities are specified in the final quotation. Wildlife "
            "sightings cannot be guaranteed."
        ),
        "duration": "Multi-day",
        "meeting": "Nairobi or an agreed departure point",
        "location": "Maasai Mara, Kenya",
        "price": 85000,
        "difficulty": "Easy",
        "accessibility": "Wildlife Terrain",
        "policy_id": SAFARI_POLICY_ID,
        "conservation": None,
        "order": 1,
    },
    {
        "code": "LUX-002",
        "title": "Nanyuki Luxury Mountain Escape",
        "slug": "nanyuki-luxury-mountain-escape",
        "category": "Luxury Escapes",
        "destination": "Nanyuki",
        "short": "A premium countryside escape with mountain views, a selected stay and unhurried time away.",
        "description": (
            "A curated Nanyuki getaway focused on comfort, scenic "
            "surroundings and a carefully selected accommodation partner. "
            "Mount Kenya views depend on weather; accommodation, meals, "
            "activities and transfers are specified in the final package."
        ),
        "duration": "Two days or longer",
        "meeting": "Nairobi or an agreed departure point",
        "location": "Nanyuki, Laikipia County, Kenya",
        "price": 45000,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 2,
    },

    # -----------------------------------------------------------------------
    # FAMILY & GROUP EXPERIENCES
    # -----------------------------------------------------------------------
    {
        "code": "FAM-001",
        "title": "Nairobi Family Wildlife Day",
        "slug": "nairobi-family-wildlife-day",
        "category": "Family & Group Experiences",
        "destination": "Nairobi",
        "short": "A flexible family day built around suitable Nairobi wildlife and nature stops.",
        "description": (
            "A family-oriented day combining selected wildlife or nature "
            "stops in Nairobi. The final route depends on children's ages, "
            "venue opening hours, transport needs and confirmed entry "
            "arrangements. Each venue's age and supervision rules apply."
        ),
        "duration": "Full day",
        "meeting": "Nairobi or an agreed pickup point",
        "location": "Nairobi, Kenya",
        "price": 15000,
        "difficulty": "Easy",
        "accessibility": "Family & Gentle Adventure",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 1,
    },
    {
        "code": "FAM-002",
        "title": "Lake Naivasha Family Escape",
        "slug": "lake-naivasha-family-escape",
        "category": "Family & Group Experiences",
        "destination": "Lake Naivasha",
        "short": "A family-friendly lakeside getaway with nature activities selected for the group.",
        "description": (
            "A flexible Naivasha getaway for families, with suitable "
            "lakeside and nature activities selected according to the "
            "ages and interests of the group. Boat trips, wildlife walks, "
            "accommodation and entry fees depend on the final itinerary "
            "and confirmed providers."
        ),
        "duration": "Full day or overnight",
        "meeting": "Nairobi or an agreed meeting point",
        "location": "Lake Naivasha, Nakuru County, Kenya",
        "price": 18000,
        "difficulty": "Easy",
        "accessibility": "Family & Gentle Adventure",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 2,
    },

    # -----------------------------------------------------------------------
    # CORPORATE & TEAM EXPERIENCES
    # -----------------------------------------------------------------------
    {
        "code": "COR-001",
        "title": "Naivasha Corporate Retreat",
        "slug": "naivasha-corporate-retreat",
        "category": "Corporate & Team Experiences",
        "destination": "Lake Naivasha",
        "short": "A customizable company retreat with a selected venue, team activities and time in nature.",
        "description": (
            "A customizable retreat for teams seeking a change of setting "
            "near Lake Naivasha. Venue, meeting facilities, meals, transport, "
            "team-building activities and accommodation are quoted according "
            "to the company's requirements and confirmed supplier arrangements."
        ),
        "duration": "One day or multi-day",
        "meeting": "Agreed company pickup point or retreat venue",
        "location": "Lake Naivasha, Kenya",
        "price": 25000,
        "difficulty": "Easy",
        "accessibility": "Moderate Mobility",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 1,
    },

    # -----------------------------------------------------------------------
    # WELLNESS & SLOW TRAVEL
    # -----------------------------------------------------------------------
    {
        "code": "WEL-001",
        "title": "Lake Naivasha Rest & Reset",
        "slug": "lake-naivasha-rest-and-reset",
        "category": "Wellness & Slow Travel",
        "destination": "Lake Naivasha",
        "short": "A slower lakeside escape built around restful surroundings and optional gentle nature activities.",
        "description": (
            "A relaxed Naivasha getaway designed around unhurried time, "
            "scenic surroundings and optional gentle nature activities. "
            "Accommodation, meals, transport and activities depend on "
            "the chosen package and are specified before confirmation."
        ),
        "duration": "Overnight or weekend",
        "meeting": "Nairobi or an agreed departure point",
        "location": "Lake Naivasha, Kenya",
        "price": 22000,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STAY_POLICY_ID,
        "conservation": None,
        "order": 1,
    },

    # -----------------------------------------------------------------------
    # CULINARY & FARM EXPERIENCES
    # -----------------------------------------------------------------------
    {
        "code": "CULI-001",
        "title": "Nairobi Market-to-Table Cooking Experience",
        "slug": "nairobi-market-to-table-cooking-experience",
        "category": "Culinary & Farm Experiences",
        "destination": "Nairobi",
        "short": "Discover local ingredients, learn about Kenyan food and enjoy a guided cooking experience.",
        "description": (
            "A proposed culinary experience combining an introduction to "
            "local ingredients with a guided Kenyan cooking session and "
            "shared meal. The market, host, menu, dietary options and "
            "availability must be confirmed with the supplier before "
            "this experience is made bookable."
        ),
        "duration": "Half day",
        "meeting": "Confirmed with the cooking host",
        "location": "Nairobi, Kenya",
        "price": 8500,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 1,
    },
    {
        "code": "CULI-002",
        "title": "Brown's Cheese & Farm Experience",
        "slug": "browns-cheese-farm-experience",
        "category": "Culinary & Farm Experiences",
        "destination": "Nairobi",
        "short": "Explore artisanal cheese-making and farm-to-table flavours on a curated countryside outing.",
        "description": (
            "A proposed culinary outing centred on an arranged visit to "
            "Brown's Food Co. in the Tigoni area. Potential elements include "
            "learning about cheese production, tasting and a meal, subject "
            "to the operator's current visitor programme, availability and "
            "booking terms. The location and transfer plan must be confirmed "
            "before this experience is published as bookable."
        ),
        "duration": "Half day or full day",
        "meeting": "Confirmed with the experience provider",
        "location": "Tigoni, Kiambu County, Kenya",
        "price": 12000,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 2,
    },
    {
        "code": "CULI-003",
        "title": "Coffee Farm & Tasting Experience",
        "slug": "coffee-farm-tasting-experience",
        "category": "Culinary & Farm Experiences",
        "destination": "Nairobi",
        "short": "Discover Kenya's coffee story through a farm visit and tasting with an arranged local partner.",
        "description": (
            "A proposed coffee-focused outing introducing guests to coffee "
            "growing, processing or preparation and tasting. The specific "
            "farm, tour content, seasonal availability and tasting format "
            "must be confirmed with a suitable provider before booking "
            "are accepted."
        ),
        "duration": "Half day",
        "meeting": "Confirmed with the coffee farm or tour provider",
        "location": "Nairobi region, Kenya",
        "price": 10000,
        "difficulty": "Easy",
        "accessibility": "Easy Access",
        "policy_id": STANDARD_POLICY_ID,
        "conservation": None,
        "order": 3,
    },
]


# ---------------------------------------------------------------------------
# LOOKUP HELPERS
# ---------------------------------------------------------------------------

def normalize(value):
    return " ".join(str(value or "").strip().lower().replace("&", "and").split())


def get_by_name(model, name, aliases=None):
    aliases = aliases or []
    wanted = {normalize(name), *(normalize(x) for x in aliases)}
    for obj in model.query.all():
        for field in ("name", "title", "slug"):
            value = getattr(obj, field, None)
            if value and normalize(value) in wanted:
                return obj
    return None


def get_category(name):
    aliases = {
        "Safari & Wildlife": ["safari-wildlife"],
        "Culture, Heritage & City Discovery": [
            "culture-heritage-city-discovery",
            "culture-heritage-and-city-discovery",
        ],
        "Coastal & Island Escapes": ["coastal-island-escapes"],
        "Luxury Escapes": ["luxury-escapes"],
        "Family & Group Experiences": ["family-group-experiences"],
        "Corporate & Team Experiences": ["corporate-team-experiences"],
        "Wellness & Slow Travel": ["wellness-slow-travel"],
        "Culinary & Farm Experiences": ["culinary-farm-experiences"],
    }
    return get_by_name(ExperienceCategory, name, aliases.get(name, []))


def get_destination(name, aliases=None):
    return get_by_name(Destination, name, aliases or [])


def is_active(obj):
    return bool(
        getattr(obj, "active", getattr(obj, "is_active", True))
    )


def get_policy(policy_id):
    policy = db.session.get(CancellationPolicy, policy_id)
    if policy and is_active(policy):
        return policy
    raise ValueError(
        f"Required active cancellation policy ID {policy_id} was not found. "
        "Check the existing Cancellation Policies CMS."
    )


def get_accessibility(name):
    if not name:
        return None
    profile = get_by_name(Accessibility, name)
    if not profile or not is_active(profile):
        raise ValueError(
            f"Required active accessibility profile '{name}' was not found."
        )
    return profile


def get_conservation_story(name):
    if not name:
        return None
    story = get_by_name(ConservationStory, name)
    if not story:
        raise ValueError(
            f"Conservation story '{name}' was not found. "
            "Correct the name or set conservation to None."
        )
    return story


def get_experience_image_ids():
    """Find active image assets in the existing Experiences DAM folder tree."""
    folders = MediaFolder.query.all()
    root = next(
        (
            folder for folder in folders
            if normalize(getattr(folder, "name", "")) == normalize(IMAGE_FOLDER_NAME)
        ),
        None,
    )

    folder_ids = set()
    if root:
        folder_ids.add(root.id)

        # Include descendants where the model exposes parent_id.
        changed = True
        while changed:
            changed = False
            for folder in folders:
                parent_id = getattr(folder, "parent_id", None)
                if parent_id in folder_ids and folder.id not in folder_ids:
                    folder_ids.add(folder.id)
                    changed = True

    asset_ids = set()

    if folder_ids:
        links = MediaAssetFolder.query.filter(
            MediaAssetFolder.folder_id.in_(folder_ids)
        ).all()
        asset_ids.update(link.media_asset_id for link in links)

    # Also support installations using the older direct folder field.
    for asset in MediaAsset.query.all():
        legacy_folder = getattr(asset, "folder", None)
        if normalize(legacy_folder) == normalize(IMAGE_FOLDER_NAME):
            asset_ids.add(asset.id)

    images = []
    for asset_id in asset_ids:
        asset = db.session.get(MediaAsset, asset_id)
        if not asset or not is_active(asset):
            continue

        media_type = normalize(getattr(asset, "media_type", ""))
        if media_type in {"image", "photo", "photograph"}:
            images.append(asset.id)

    return sorted(set(images))


# ---------------------------------------------------------------------------
# VALIDATION AND CREATION
# ---------------------------------------------------------------------------

def main():
    print("\nTHE UNCHARTED ROUTE — REMAINING CATALOGUE CREATION")
    print("=" * 62)

    # Resolve all references before creating any records.
    resolved = []
    errors = []

    for item in EXPERIENCES:
        category = get_category(item["category"])
        destination = get_destination(
            item["destination"],
            item.get("destination_aliases"),
        )

        try:
            policy = get_policy(item["policy_id"])
        except ValueError as exc:
            policy = None
            errors.append(f"{item['title']}: {exc}")

        try:
            accessibility = get_accessibility(item.get("accessibility"))
        except ValueError as exc:
            accessibility = None
            errors.append(f"{item['title']}: {exc}")

        try:
            story = get_conservation_story(item.get("conservation"))
        except ValueError as exc:
            story = None
            errors.append(f"{item['title']}: {exc}")

        if not category:
            errors.append(
                f"Category not found: '{item['category']}'. "
                "Use the existing Experience Categories CMS."
            )

        if not destination:
            errors.append(
                f"Destination not found: '{item['destination']}' "
                f"(experience: {item['title']}). Add/select the destination "
                "in the existing Destinations CMS before running this script."
            )

        resolved.append({
            "item": item,
            "category": category,
            "destination": destination,
            "policy": policy,
            "accessibility": accessibility,
            "story": story,
        })

    image_ids = get_experience_image_ids()
    if not image_ids:
        errors.append(
            "No active image assets were found in the existing Experiences "
            "DAM folder or its descendants. Add/activate an image in the DAM."
        )

    if errors:
        print("\nPRE-FLIGHT CHECK FAILED. No experiences were created.")
        for error in errors:
            print(f"  - {error}")
        return

    # Read existing records before adding anything to avoid accidental autoflush.
    existing = Experience.query.all()
    by_code = {e.experience_code: e for e in existing}
    by_slug = {e.slug: e for e in existing}

    conflicts = []
    to_create = []

    for entry in resolved:
        item = entry["item"]
        code_match = by_code.get(item["code"])
        slug_match = by_slug.get(item["slug"])

        if code_match and code_match.slug != item["slug"]:
            conflicts.append(
                f"Code {item['code']} already belongs to "
                f"'{code_match.title}' ({code_match.slug})."
            )
        elif slug_match and slug_match.experience_code != item["code"]:
            conflicts.append(
                f"Slug {item['slug']} already belongs to "
                f"code {slug_match.experience_code}."
            )
        elif code_match and slug_match and code_match.id != slug_match.id:
            conflicts.append(
                f"Code/slug mismatch for {item['title']}."
            )
        elif code_match or slug_match:
            print(f"SKIP existing: {item['title']}")
        else:
            to_create.append(entry)

    if conflicts:
        print("\nCONFLICT CHECK FAILED. No experiences were created.")
        for conflict in conflicts:
            print(f"  - {conflict}")
        return

    if not to_create:
        print("\nAll requested records already exist. Nothing to create.")
        return

    try:
        created = []

        for index, entry in enumerate(to_create):
            item = entry["item"]

            experience = Experience(
                experience_code=item["code"],
                title=item["title"],
                slug=item["slug"],
                short_description=item["short"],
                description=item["description"],
                duration=item["duration"],
                meeting_point=item["meeting"],
                location=item["location"],
                price_from=item["price"],
                currency="KES",
                minimum_people=1,
                maximum_people=None,
                minimum_age=0,
                difficulty=item["difficulty"],
                featured_image=image_ids[index % len(image_ids)],
                banner_image=None,
                meta_title=item["title"][:60],
                meta_description=item["short"][:160],
                featured=False,
                active=True,
                display_order=item["order"],
                category_id=entry["category"].id,
                destination_id=entry["destination"].id,
                conservation_story_id=(
                    entry["story"].id if entry["story"] else None
                ),
                cancellation_policy_id=entry["policy"].id,
                accessibility_profile_id=(
                    entry["accessibility"].id
                    if entry["accessibility"] else None
                ),
            )

            db.session.add(experience)
            created.append(experience)

        db.session.commit()

        print(f"\nSUCCESS: Created {len(created)} experiences.")
        print("-" * 62)
        for experience in created:
            print(
                f"{experience.experience_code} | "
                f"{experience.title} | "
                f"{experience.slug} | "
                f"active={experience.active} | "
                f"featured={experience.featured}"
            )

        print("\nImportant:")
        print("- Existing experiences were not modified.")
        print("- All new experiences are active and not featured.")
        print("- Prices are provisional catalogue placeholders.")
        print("- Confirm supplier arrangements and costs before publishing.")

    except Exception:
        db.session.rollback()
        print("\nERROR: Creation failed. Database changes were rolled back.")
        raise


if __name__ == "__main__":
    main()
