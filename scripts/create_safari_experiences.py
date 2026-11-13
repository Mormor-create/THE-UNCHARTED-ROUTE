
"""
THE UNCHARTED ROUTE
Safari & Wildlife Experience Catalogue

Creates the seven missing experiences while preserving the existing
Nairobi National Park Experience (WNA-001).

All newly created experiences:
    active = True
    featured = False

This script only creates or updates the core Experience records.
It does not populate pricing tiers, itineraries, inclusions, exclusions,
highlights, wildlife, photography, FAQs, or other detail records.

Safe to rerun: matches existing records by slug and experience code.
"""

from decimal import Decimal

from sqlalchemy import or_

from extensions import db

from app.models.experience import Experience
from app.models.experience_category import ExperienceCategory
from app.models.destination import Destination
from app.models.cancellation_policy import CancellationPolicy
from app.models.conservation_story import ConservationStory
from app.models.accessibility import Accessibility
from app.models.media_asset import MediaAsset
from app.models.media_folder import MediaFolder
from app.models.media_asset_folder import MediaAssetFolder


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

CATEGORY_ID = 1
CANCELLATION_POLICY_ID = 3

# WNA-001 is already used by the existing Nairobi National Park Experience.
# Do not create or modify that record in this script.

EXPERIENCES = [
    {
        "code": "WNA-002",
        "title": "Nairobi Wildlife Combo Package",
        "slug": "nairobi-wildlife-combo-package",
        "destination_id": 1,
        "short_description": (
            "A full-day Nairobi wildlife experience combining a national "
            "park safari, elephant conservation, giraffe encounters, lunch "
            "and a choice of nature walk."
        ),
        "description": (
            "Explore Nairobi's remarkable wildlife and green spaces in one "
            "curated day. The planned route includes Nairobi National Park, "
            "Sheldrick Wildlife Trust, the Giraffe Centre, lunch, Nairobi "
            "Safari Walk and a choice between Karura Forest and Oloolua "
            "Nature Trail. Final timings, venue availability, admission fees "
            "and the day's route will be confirmed during itinerary planning."
        ),
        "duration": "Full day",
        "meeting_point": "Nairobi; meeting point to be confirmed",
        "location": "Nairobi, Kenya",
        "price_from": Decimal("18500"),
        "difficulty": "Easy",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": 1,
        "accessibility_profile_id": 9,
        "display_order": 1,
    },
    {
        "code": "WNA-003",
        "title": "The Elephant Orphanage Experience",
        "slug": "elephant-orphanage-experience",
        "destination_id": 1,
        "short_description": (
            "Learn about elephant rescue, rehabilitation and conservation "
            "through the work of the Sheldrick Wildlife Trust."
        ),
        "description": (
            "Discover the conservation work of the Sheldrick Wildlife Trust "
            "and learn about the care and rehabilitation of orphaned "
            "elephants. Visits are subject to the organisation's booking "
            "procedures, admission arrangements and available visiting sessions."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Sheldrick Wildlife Trust, Nairobi",
        "location": "Nairobi, Kenya",
        "price_from": Decimal("8500"),
        "difficulty": "Easy",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": 1,
        "accessibility_profile_id": 5,
        "display_order": 2,
    },
    {
        "code": "WNA-004",
        "title": "The Giraffe Encounter",
        "slug": "giraffe-encounter",
        "destination_id": 1,
        "short_description": (
            "Enjoy an educational giraffe encounter and discover the "
            "importance of giraffe conservation in Kenya."
        ),
        "description": (
            "Visit the Giraffe Centre for an educational wildlife experience "
            "focused on giraffes and their conservation. Visit timings, "
            "admission arrangements and venue rules will be confirmed "
            "during itinerary planning."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Giraffe Centre, Nairobi",
        "location": "Nairobi, Kenya",
        "price_from": Decimal("8500"),
        "difficulty": "Easy",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": 5,
        "accessibility_profile_id": 5,
        "display_order": 3,
    },
    {
        "code": "WNA-005",
        "title": "The Great Maasai Mara Safari",
        "slug": "great-maasai-mara-safari",
        "destination_id": 2,
        "short_description": (
            "Explore the iconic Maasai Mara landscape on a wildlife safari "
            "shaped by the season and the rhythms of the savannah."
        ),
        "description": (
            "Discover the open plains and wildlife of the Maasai Mara "
            "National Reserve on a planned safari. Wildlife sightings and "
            "seasonal migration activity cannot be guaranteed. Duration, "
            "accommodation, transport, reserve fees and final routing will "
            "be confirmed during itinerary planning."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Nairobi or an agreed departure point",
        "location": "Maasai Mara National Reserve, Kenya",
        "price_from": Decimal("45000"),
        "difficulty": "Moderate",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": None,
        "accessibility_profile_id": 9,
        "display_order": 4,
    },
    {
        "code": "WNA-006",
        "title": "Amboseli National Park Safari",
        "slug": "amboseli-national-park-safari",
        "destination_id": 3,
        "short_description": (
            "Explore Amboseli's wildlife-rich landscapes, with opportunities "
            "for views of Mount Kilimanjaro when conditions allow."
        ),
        "description": (
            "Experience a safari in Amboseli National Park, known for its "
            "elephants and expansive landscapes. Views of Mount Kilimanjaro "
            "depend on weather and visibility. Final duration, transport, "
            "accommodation if applicable, and park fees will be confirmed "
            "during itinerary planning."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Nairobi or an agreed departure point",
        "location": "Amboseli National Park, Kenya",
        "price_from": Decimal("35000"),
        "difficulty": "Moderate",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": None,
        "accessibility_profile_id": 9,
        "display_order": 5,
    },
    {
        "code": "WNA-007",
        "title": "Samburu National Reserve Safari",
        "slug": "samburu-national-reserve-safari",
        "destination_id": 10,
        "short_description": (
            "Discover northern Kenya's striking landscapes and distinctive "
            "wildlife on a guided Samburu safari."
        ),
        "description": (
            "Explore Samburu National Reserve and its distinctive arid "
            "landscapes and wildlife. Sightings depend on natural conditions "
            "and the season. Final itinerary, transport, accommodation, "
            "reserve fees and departure arrangements will be confirmed "
            "during planning."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Nairobi or an agreed departure point",
        "location": "Samburu National Reserve, Kenya",
        "price_from": Decimal("42000"),
        "difficulty": "Moderate",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": None,
        "accessibility_profile_id": 9,
        "display_order": 6,
    },
    {
        "code": "WNA-008",
        "title": "Aberdare National Park Safari",
        "slug": "aberdare-national-park-safari",
        "destination_id": 19,
        "short_description": (
            "Explore the forested mountains, moorlands and wildlife habitats "
            "of Aberdare National Park on a nature-focused safari."
        ),
        "description": (
            "Discover the varied landscapes of Aberdare National Park, from "
            "montane forest to open moorland. Routes, road conditions, "
            "wildlife viewing opportunities and suitable activities depend "
            "on the season and selected itinerary. Final transport, "
            "accommodation and park fees will be confirmed during planning."
        ),
        "duration": "To be confirmed",
        "meeting_point": "Nairobi or an agreed departure point",
        "location": "Aberdare National Park, Kenya",
        "price_from": Decimal("25000"),
        "difficulty": "Moderate",
        "minimum_people": 1,
        "minimum_age": 0,
        "conservation_story_id": None,
        "accessibility_profile_id": 9,
        "display_order": 7,
    },
]


# ---------------------------------------------------------------------
# MEDIA HELPERS
# ---------------------------------------------------------------------

def get_experience_image_ids():
    """
    Find active image assets in the Experiences folder and its descendants.
    Returns actual MediaAsset IDs; never invents image IDs.
    """
    folders = MediaFolder.query.filter_by(active=True).all()

    root_ids = {
        folder.id
        for folder in folders
        if (folder.name or "").strip().lower() == "experiences"
    }

    if not root_ids:
        return []

    included_folder_ids = set(root_ids)

    changed = True
    while changed:
        changed = False

        for folder in folders:
            if (
                folder.parent_id in included_folder_ids
                and folder.id not in included_folder_ids
            ):
                included_folder_ids.add(folder.id)
                changed = True

    links = MediaAssetFolder.query.filter(
        MediaAssetFolder.folder_id.in_(included_folder_ids)
    ).all()

    linked_asset_ids = {link.media_asset_id for link in links}

    # Support the legacy folder field as well.
    assets = MediaAsset.query.filter_by(active=True).all()

    for asset in assets:
        folder_value = getattr(asset, "folder", None)

        if (
            isinstance(folder_value, str)
            and folder_value.strip().lower() == "experiences"
        ):
            linked_asset_ids.add(asset.id)

    image_ids = []

    for asset in assets:
        if asset.id not in linked_asset_ids:
            continue

        media_type = (getattr(asset, "media_type", "") or "").lower()

        if media_type in ("image", "photo"):
            image_ids.append(asset.id)

    return sorted(set(image_ids))


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------

def validate_references():
    """Validate all foreign-key references before adding any experiences."""

    category = db.session.get(ExperienceCategory, CATEGORY_ID)
    if category is None or not getattr(category, "active", True):
        raise RuntimeError(
            f"Experience category {CATEGORY_ID} is missing or inactive."
        )

    policy = db.session.get(
        CancellationPolicy, CANCELLATION_POLICY_ID
    )
    if policy is None or not getattr(policy, "active", True):
        raise RuntimeError(
            f"Cancellation policy {CANCELLATION_POLICY_ID} is missing or inactive."
        )

    for destination_id in {
        item["destination_id"] for item in EXPERIENCES
    }:
        destination = db.session.get(Destination, destination_id)

        if destination is None:
            raise RuntimeError(
                f"Destination ID {destination_id} does not exist."
            )

    for story_id in {
        item["conservation_story_id"]
        for item in EXPERIENCES
        if item["conservation_story_id"] is not None
    }:
        story = db.session.get(ConservationStory, story_id)

        if story is None or not getattr(story, "active", True):
            raise RuntimeError(
                f"Conservation story ID {story_id} is missing or inactive."
            )

    for profile_id in {
        item["accessibility_profile_id"]
        for item in EXPERIENCES
        if item["accessibility_profile_id"] is not None
    }:
        profile = db.session.get(Accessibility, profile_id)

        if profile is None or not getattr(profile, "active", True):
            raise RuntimeError(
                f"Accessibility profile ID {profile_id} is missing or inactive."
            )

    image_ids = get_experience_image_ids()

    if not image_ids:
        raise RuntimeError(
            "No active image assets were found in the Experiences media "
            "folder or its subfolders. No experiences have been created. "
            "Add an image to that folder, then rerun this script."
        )

    return image_ids


# ---------------------------------------------------------------------
# POPULATION
# ---------------------------------------------------------------------

def main():
    image_ids = validate_references()

    # Fetch existing experiences BEFORE adding anything to the session.
    # This prevents SQLAlchemy's autoflush from trying to insert a new
    # duplicate code during a later query.
    existing_records = Experience.query.filter(
        or_(
            Experience.experience_code.in_(
                [item["code"] for item in EXPERIENCES]
            ),
            Experience.slug.in_(
                [item["slug"] for item in EXPERIENCES]
            ),
        )
    ).all()

    records_by_code = {
        record.experience_code: record
        for record in existing_records
    }

    records_by_slug = {
        record.slug: record
        for record in existing_records
    }

    # Preflight every code/slug pair before making any changes.
    planned_records = []

    for item in EXPERIENCES:
        by_code = records_by_code.get(item["code"])
        by_slug = records_by_slug.get(item["slug"])

        if by_code is not None and by_slug is not None:
            if by_code.id != by_slug.id:
                raise RuntimeError(
                    f"Conflict for {item['title']}: code {item['code']} "
                    f"and slug {item['slug']} belong to different records. "
                    "Nothing has been committed."
                )

        if by_code is not None and by_code.slug != item["slug"]:
            raise RuntimeError(
                f"Code {item['code']} is already used by "
                f"'{by_code.title}' (ID {by_code.id}). "
                "Nothing has been committed; existing records were preserved."
            )

        if by_slug is not None and by_slug.experience_code != item["code"]:
            code_owner = records_by_code.get(item["code"])

            if code_owner is not None and code_owner.id != by_slug.id:
                raise RuntimeError(
                    f"Code conflict for {item['title']}. "
                    "Nothing has been committed."
                )

        existing = by_slug or by_code
        planned_records.append((item, existing))

    created = []
    updated = []

    try:
        for index, (item, existing) in enumerate(planned_records):
            experience = existing if existing is not None else Experience()

            # Set only the core catalogue fields.
            experience.experience_code = item["code"]
            experience.title = item["title"]
            experience.slug = item["slug"]
            experience.short_description = item["short_description"]
            experience.description = item["description"]
            experience.duration = item["duration"]
            experience.meeting_point = item["meeting_point"]
            experience.location = item["location"]
            experience.price_from = float(item["price_from"])
            experience.currency = "KES"
            experience.minimum_people = item["minimum_people"]
            experience.minimum_age = item["minimum_age"]
            experience.difficulty = item["difficulty"]

            # The existing form/model uses featured_image to store the
            # MediaAsset ID, not featured_image_id.
            experience.featured_image = image_ids[index % len(image_ids)]

            experience.category_id = CATEGORY_ID
            experience.destination_id = item["destination_id"]
            experience.conservation_story_id = item["conservation_story_id"]
            experience.cancellation_policy_id = CANCELLATION_POLICY_ID
            experience.accessibility_profile_id = item[
                "accessibility_profile_id"
            ]

            experience.display_order = item["display_order"]

            # Explicit publication settings requested by the user.
            experience.active = True
            experience.featured = False

            if existing is None:
                db.session.add(experience)
                created.append(item["title"])
            else:
                updated.append(item["title"])

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    print("\n" + "=" * 60)
    print("THE UNCHARTED ROUTE — SAFARI CATALOGUE")
    print("=" * 60)
    print(f"New experiences created: {len(created)}")

    for title in created:
        print(f"  + {title}")

    print(f"\nExisting matching experiences updated: {len(updated)}")

    for title in updated:
        print(f"  ~ {title}")

    print("\nAll seven target experiences are active and not featured.")
    print("The existing Nairobi National Park Experience (WNA-001)")
    print("was not included in the target records and remains untouched.")
    print("\nStarting prices are provisional pending the bulk pricing pass.")
    print("Detailed content modules have not been populated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
