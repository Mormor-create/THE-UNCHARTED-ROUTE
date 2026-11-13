"""
===============================================================================
The Uncharted Route
Stay Room Media Folder Population
===============================================================================
Creates and maintains the DAM folder hierarchy for Stay Rooms and links each
StayRoom.media_folder_id to its corresponding room media folder.

Hierarchy:

    Stay Rooms
    ├── Giraffe Manor
    │   ├── Superior Room
    │   └── Superior Family Suite
    ├── JW Marriott Hotel Nairobi
    │   ├── Junior Suite
    │   ├── Deluxe King Room
    │   ├── One Bedroom Residence
    │   ├── Two Bedroom Residence
    │   └── Three Bedroom Residence
    ├── Skynest Residences by CityBlue
    │   ├── One Bedroom Residence
    │   ├── One and a Half Bedroom Residence
    │   ├── Two Bedroom Residence
    │   ├── Three Bedroom Residence
    │   └── Four Bedroom Residence
    ├── Escada Apartments
    │   ├── Mini One Bedroom Apartment
    │   ├── One Bedroom Apartment
    │   └── Two Bedroom Apartment
    ├── Mövenpick Hotel & Residences Nairobi
    │   ├── Classic King Room
    │   ├── Deluxe King Room
    │   ├── One Bedroom Residence
    │   └── Two Bedroom Residence
    └── Fairmont Mount Kenya Safari Club
        ├── Manor Junior Suites
        ├── Manor Equatorial Suites
        ├── Batian Villa
        └── Riverside Accommodation

Design rules
------------
- Dry-run by default.
- --apply commits changes.
- Reuses the existing "Stay Rooms" root.
- Reuses an existing Stay Rooms child by parent + display name.
- Reuses an existing room folder by parent + display name.
- Normalizes folder slugs to the dedicated Stay Rooms namespace.
- Never moves or modifies the existing Stays hierarchy.
- Never deletes existing folders.
- Never creates media assets.
- Never changes StayRoom names or other StayRoom data.
- Never changes stays, bookings, availability, amenities, reviews, inquiries,
  or existing media assets.
- Refuses to replace an existing StayRoom.media_folder_id pointing elsewhere.
- One transaction with rollback on failure.
- Post-commit verification checks the actual parent/child hierarchy.
===============================================================================
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# =============================================================================
# PROJECT BOOTSTRAP
# =============================================================================
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("FLASK_ENV", "development")

from app import create_app
from extensions import db
from app.models.media_folder import MediaFolder
from app.models.stay import Stay
from app.models.stay_room import StayRoom


# =============================================================================
# CONFIGURATION
# =============================================================================
ROOT_FOLDER_NAME = "Stay Rooms"
ROOT_FOLDER_SLUG = "stay-rooms"
ROOT_FOLDER_TYPE = "stay_room"

STAY_FOLDER_SLUG_PREFIX = "stay-rooms-"
ROOM_FOLDER_SLUG_PREFIX = "stay-rooms-"

@dataclass(frozen=True)
class RoomDefinition:
    room_name: str
    folder_name: str


@dataclass(frozen=True)
class StayDefinition:
    stay_name: str
    stay_slug: str
    rooms: tuple[RoomDefinition, ...]


STAYS = (
    StayDefinition(
        stay_name="Giraffe Manor",
        stay_slug="giraffe-manor",
        rooms=(
            RoomDefinition("Superior Room", "Superior Room"),
            RoomDefinition("Superior Family Suite", "Superior Family Suite"),
        ),
    ),
    StayDefinition(
        stay_name="JW Marriott Hotel Nairobi",
        stay_slug="jw-marriott-hotel-nairobi",
        rooms=(
            RoomDefinition("Junior Suite", "Junior Suite"),
            RoomDefinition("Deluxe King Room", "Deluxe King Room"),
            RoomDefinition("One Bedroom Residence", "One Bedroom Residence"),
            RoomDefinition("Two Bedroom Residence", "Two Bedroom Residence"),
            RoomDefinition("Three Bedroom Residence", "Three Bedroom Residence"),
        ),
    ),
    StayDefinition(
        stay_name="Skynest Residences by CityBlue",
        stay_slug="skynest-residences-by-cityblue",
        rooms=(
            RoomDefinition("One Bedroom Residence", "One Bedroom Residence"),
            RoomDefinition(
                "One and a Half Bedroom Residence",
                "One and a Half Bedroom Residence",
            ),
            RoomDefinition("Two Bedroom Residence", "Two Bedroom Residence"),
            RoomDefinition("Three Bedroom Residence", "Three Bedroom Residence"),
            RoomDefinition("Four Bedroom Residence", "Four Bedroom Residence"),
        ),
    ),
    StayDefinition(
        stay_name="Escada Apartments",
        stay_slug="escada-apartments",
        rooms=(
            RoomDefinition(
                "Mini One Bedroom Apartment",
                "Mini One Bedroom Apartment",
            ),
            RoomDefinition("One Bedroom Apartment", "One Bedroom Apartment"),
            RoomDefinition("Two Bedroom Apartment", "Two Bedroom Apartment"),
        ),
    ),
    StayDefinition(
        stay_name="Mövenpick Hotel & Residences Nairobi",
        stay_slug="movenpick-hotel-residences-nairobi",
        rooms=(
            RoomDefinition("Classic King Room", "Classic King Room"),
            RoomDefinition("Deluxe King Room", "Deluxe King Room"),
            RoomDefinition("One Bedroom Residence", "One Bedroom Residence"),
            RoomDefinition("Two Bedroom Residence", "Two Bedroom Residence"),
        ),
    ),
    StayDefinition(
        stay_name="Fairmont Mount Kenya Safari Club",
        stay_slug="fairmont-mount-kenya-safari-club",
        rooms=(
            RoomDefinition("Manor Junior Suite", "Manor Junior Suites"),
            RoomDefinition(
                "Manor Equatorial Suite",
                "Manor Equatorial Suites",
            ),
            RoomDefinition("Batian Villa", "Batian Villa"),
            RoomDefinition(
                "Riverside Accommodation",
                "Riverside Accommodation",
            ),
        ),
    ),
)


# =============================================================================
# HELPERS
# =============================================================================

def slugify(value: str) -> str:
    """
    Convert a display name into a stable lowercase slug.
    """
    value = value.strip().lower()
    value = value.replace("&", " and ")
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def expected_stay_folder_slug(stay_slug: str) -> str:
    return f"{STAY_FOLDER_SLUG_PREFIX}{stay_slug}"


def expected_room_folder_slug(
    stay_slug: str,
    folder_name: str,
) -> str:
    return f"{ROOM_FOLDER_SLUG_PREFIX}{stay_slug}-{slugify(folder_name)}"


def folder_children(parent: MediaFolder) -> list[MediaFolder]:
    """
    Return children as a normal list.

    This avoids relying on the dynamic relationship in multiple places and
    makes hierarchy matching explicit.
    """
    return list(parent.children.all())


def find_child_by_name(
    parent: MediaFolder,
    name: str,
) -> Optional[MediaFolder]:
    """
    Find a child by display name under the specified parent.

    Display name + parent is the authoritative hierarchy identity here.
    Slugs are normalized afterward.
    """
    matches = [
        child
        for child in folder_children(parent)
        if child.name == name
    ]

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple MediaFolder records named '{name}' exist under "
            f"parent '{parent.name}' (id={parent.id})."
        )

    return matches[0] if matches else None


def find_folder_by_slug(slug: str) -> Optional[MediaFolder]:
    return MediaFolder.query.filter_by(slug=slug).first()


def ensure_root_folder() -> tuple[MediaFolder, bool]:
    """
    Resolve the Stay Rooms root.

    The root is identified by its expected slug and/or exact root name.
    """
    root = MediaFolder.query.filter_by(slug=ROOT_FOLDER_SLUG).first()

    if root:
        if root.parent_id is not None:
            raise RuntimeError(
                f"Media folder '{ROOT_FOLDER_SLUG}' exists but is not a root "
                f"folder. ID={root.id}, parent_id={root.parent_id}."
            )

        return root, False

    root = MediaFolder.query.filter_by(
        name=ROOT_FOLDER_NAME,
        parent_id=None,
    ).first()

    if root:
        if root.slug != ROOT_FOLDER_SLUG:
            root.slug = ROOT_FOLDER_SLUG
        return root, False

    root = MediaFolder(
        name=ROOT_FOLDER_NAME,
        slug=ROOT_FOLDER_SLUG,
        description="Media folders for individual stay room types.",
        parent_id=None,
        folder_type=ROOT_FOLDER_TYPE,
        display_order=0,
        active=True,
    )

    db.session.add(root)
    db.session.flush()

    return root, True


def ensure_folder(
    *,
    parent: MediaFolder,
    name: str,
    expected_slug: str,
    folder_type: str,
    display_order: int,
    dry_run: bool,
    level: int,
) -> tuple[MediaFolder, bool, bool]:
    """
    Resolve or create a folder.

    Returns:
        folder,
        created,
        metadata_changed

    Important:
    Existing folders are matched by parent + name first.

    This deliberately handles the previously-created Giraffe Manor branch:

        Stay Rooms
        └── Giraffe Manor
            └── Superior Room

    even if its old slug was:

        giraffe-manor-rooms
        superior-room

    Those folders are normalized to the dedicated namespace rather than
    duplicated.
    """

    existing = find_child_by_name(parent, name)

    if existing:
        metadata_changed = False

        if existing.slug != expected_slug:
            # Protect against an unrelated folder already owning the desired
            # global slug.
            slug_owner = find_folder_by_slug(expected_slug)

            if slug_owner is not None and slug_owner.id != existing.id:
                raise RuntimeError(
                    f"Cannot normalize slug '{existing.slug}' -> "
                    f"'{expected_slug}' for folder '{existing.name}' "
                    f"(id={existing.id}) because MediaFolder id="
                    f"{slug_owner.id} already owns the expected slug."
                )

            if not dry_run:
                existing.slug = expected_slug

            metadata_changed = True

        if existing.folder_type != folder_type:
            if not dry_run:
                existing.folder_type = folder_type
            metadata_changed = True

        if existing.display_order != display_order:
            if not dry_run:
                existing.display_order = display_order
            metadata_changed = True

        if not existing.active:
            if not dry_run:
                existing.active = True
            metadata_changed = True

        if dry_run:
            print(
                f"[REUSE]  {'  ' * level}{name}/ "
                f"(id={existing.id}, slug={existing.slug})"
            )

            if existing.slug != expected_slug:
                print(
                    f"{' ' * (level * 3 + 12)}"
                    f"↳ slug would normalize to '{expected_slug}'"
                )

        else:
            status = "[REUSE]"
            print(
                f"{status}  {'  ' * level}{name}/ "
                f"(id={existing.id}, slug={existing.slug})"
            )

        return existing, False, metadata_changed

    # Before creating, check whether the expected slug exists elsewhere.
    slug_owner = find_folder_by_slug(expected_slug)

    if slug_owner is not None:
        raise RuntimeError(
            f"Folder slug collision detected for '{expected_slug}'. "
            f"Existing folder ID={slug_owner.id}, "
            f"name='{slug_owner.name}', "
            f"parent_id={slug_owner.parent_id}, "
            f"expected parent_id={parent.id}."
        )

    if dry_run:
        print(
            f"[CREATE] {name}/ "
            f"(slug={expected_slug})"
        )

        # Return a temporary in-memory object so callers can continue.
        folder = MediaFolder(
            id=None,
            name=name,
            slug=expected_slug,
            description=None,
            parent_id=parent.id,
            folder_type=folder_type,
            display_order=display_order,
            active=True,
        )

        return folder, True, False

    folder = MediaFolder(
        name=name,
        slug=expected_slug,
        description=None,
        parent_id=parent.id,
        folder_type=folder_type,
        display_order=display_order,
        active=True,
    )

    db.session.add(folder)
    db.session.flush()

    print(
        f"[CREATE] {name}/ "
        f"(id={folder.id}, slug={expected_slug})"
    )

    return folder, True, True


def resolve_stays() -> dict[str, Stay]:
    """
    Resolve the six expected Stay records.
    """
    resolved: dict[str, Stay] = {}

    print()
    print("Resolved stays:")

    for definition in STAYS:
        stay = Stay.query.filter_by(slug=definition.stay_slug).first()

        if stay is None:
            raise RuntimeError(
                f"Expected Stay not found: "
                f"{definition.stay_name} "
                f"(slug={definition.stay_slug})"
            )

        if stay.property_name != definition.stay_name:
            raise RuntimeError(
                f"Stay slug '{definition.stay_slug}' resolves to "
                f"'{stay.property_name}', but expected "
                f"'{definition.stay_name}'."
            )

        resolved[definition.stay_slug] = stay

        print(
            f"  ✓ {stay.property_name} "
            f"(id={stay.id}, slug={stay.slug})"
        )

    return resolved


def resolve_rooms(
    resolved_stays: dict[str, Stay],
) -> dict[tuple[str, str], StayRoom]:
    """
    Resolve every expected StayRoom by its actual database name.
    """
    resolved: dict[tuple[str, str], StayRoom] = {}

    print()
    print("Resolved StayRoom records:")

    for definition in STAYS:
        stay = resolved_stays[definition.stay_slug]

        print(f"  {stay.property_name}")

        for room_definition in definition.rooms:
            room = (
                StayRoom.query
                .filter_by(
                    stay_id=stay.id,
                    name=room_definition.room_name,
                )
                .first()
            )

            if room is None:
                raise RuntimeError(
                    f"Expected StayRoom not found: "
                    f"'{room_definition.room_name}' "
                    f"under '{stay.property_name}'."
                )

            resolved[
                (definition.stay_slug, room_definition.room_name)
            ] = room

            print(
                f"    ✓ {room.name} "
                f"(id={room.id}, "
                f"folder='{room_definition.folder_name}')"
            )

    return resolved


def validate_existing_room_link(
    room: StayRoom,
    expected_folder: MediaFolder,
    *,
    dry_run: bool,
) -> tuple[bool, bool]:
    """
    Validate or establish the StayRoom.media_folder_id relationship.

    Returns:
        link_created,
        link_preserved
    """

    current_id = room.media_folder_id

    if current_id is None:
        if dry_run:
            print(
                f"             ↳ StayRoom #{room.id} "
                f"media_folder_id=None "
                f"(would link to folder)"
            )
        else:
            room.media_folder_id = expected_folder.id
            print(
                f"             ↳ StayRoom #{room.id} "
                f"media_folder_id={expected_folder.id} (link)"
            )

        return True, False

    if current_id == expected_folder.id:
        print(
            f"             ↳ StayRoom #{room.id} "
            f"media_folder_id={current_id} (already linked)"
        )
        return False, True

    current_folder = db.session.get(MediaFolder, current_id)

    if current_folder is None:
        raise RuntimeError(
            f"StayRoom #{room.id} currently references "
            f"MediaFolder id={current_id}, but that folder does not exist."
        )

    raise RuntimeError(
        f"StayRoom #{room.id} ('{room.name}') is already linked to "
        f"MediaFolder id={current_id} "
        f"('{current_folder.name}', slug={current_folder.slug}), "
        f"but expected MediaFolder id={expected_folder.id} "
        f"('{expected_folder.name}', slug={expected_folder.slug}). "
        f"Refusing to overwrite the existing link."
    )


def print_header(apply: bool) -> None:
    print()
    print("=" * 79)
    print("The Uncharted Route")
    print("Stay Room Media Folder Population")
    print("=" * 79)
    print()
    print(f"Mode: {'APPLY' if apply else 'DRY RUN'}")
    print(f"Root folder: {ROOT_FOLDER_NAME}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Populate Stay Room Media Library folders."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create/update folders and link StayRoom records.",
    )

    args = parser.parse_args()
    apply_mode = args.apply
    dry_run = not apply_mode

    app = create_app()

    with app.app_context():
        print_header(apply_mode)

        try:
            resolved_stays = resolve_stays()
            resolved_rooms = resolve_rooms(resolved_stays)

            expected_stay_count = len(STAYS)
            expected_room_count = sum(
                len(definition.rooms)
                for definition in STAYS
            )

            print()
            print(f"Expected stays: {expected_stay_count}")
            print(f"Expected rooms: {expected_room_count}")
            print()

            root, root_created = ensure_root_folder()

            if root_created:
                print(
                    f"[CREATE] {ROOT_FOLDER_NAME} "
                    f"(slug={ROOT_FOLDER_SLUG})"
                )
            else:
                print(
                    f"[REUSE] {ROOT_FOLDER_NAME} "
                    f"(id={root.id}, slug={root.slug})"
                )

            print()
            print("-" * 79)
            print("Folder hierarchy")
            print("-" * 79)

            stay_created_count = 0
            stay_reused_count = 0
            room_created_count = 0
            room_reused_count = 0
            metadata_changed_count = 0
            room_links_created = 0
            room_links_preserved = 0

            for stay_index, definition in enumerate(STAYS):
                stay = resolved_stays[definition.stay_slug]

                stay_slug = expected_stay_folder_slug(
                    definition.stay_slug
                )

                stay_folder, created, metadata_changed = ensure_folder(
                    parent=root,
                    name=definition.stay_name,
                    expected_slug=stay_slug,
                    folder_type="stay_room",
                    display_order=stay_index,
                    dry_run=dry_run,
                    level=0,
                )

                if created:
                    stay_created_count += 1
                else:
                    stay_reused_count += 1

                if metadata_changed:
                    metadata_changed_count += 1

                for room_index, room_definition in enumerate(
                    definition.rooms
                ):
                    room_slug = expected_room_folder_slug(
                        definition.stay_slug,
                        room_definition.folder_name,
                    )

                    room_folder, room_created, room_metadata_changed = (
                        ensure_folder(
                            parent=stay_folder,
                            name=room_definition.folder_name,
                            expected_slug=room_slug,
                            folder_type="stay_room",
                            display_order=room_index,
                            dry_run=dry_run,
                            level=1,
                        )
                    )

                    if room_created:
                        room_created_count += 1
                    else:
                        room_reused_count += 1

                    if room_metadata_changed:
                        metadata_changed_count += 1

                    room = resolved_rooms[
                        (
                            definition.stay_slug,
                            room_definition.room_name,
                        )
                    ]

                    created_link, preserved_link = (
                        validate_existing_room_link(
                            room,
                            room_folder,
                            dry_run=dry_run,
                        )
                    )

                    if created_link:
                        room_links_created += 1

                    if preserved_link:
                        room_links_preserved += 1

            # =================================================================
            # DRY RUN VERIFICATION
            # =================================================================

            print()
            print("-" * 79)
            print("Verification")
            print("-" * 79)

            if dry_run:
                # For dry-run purposes we calculate the expected final state
                # from the resolved hierarchy rather than pretending that
                # newly-created folders already exist in the database.
                existing_stay_children = {
                    child.name
                    for child in folder_children(root)
                }

                existing_stay_count = sum(
                    1
                    for definition in STAYS
                    if definition.stay_name in existing_stay_children
                )

                existing_room_count = 0
                existing_link_count = 0

                for definition in STAYS:
                    existing_stay_folder = find_child_by_name(
                        root,
                        definition.stay_name,
                    )

                    if existing_stay_folder is None:
                        continue

                    for room_definition in definition.rooms:
                        room_folder = find_child_by_name(
                            existing_stay_folder,
                            room_definition.folder_name,
                        )

                        if room_folder is not None:
                            existing_room_count += 1

                        room = resolved_rooms[
                            (
                                definition.stay_slug,
                                room_definition.room_name,
                            )
                        ]

                        if (
                            room_folder is not None
                            and room.media_folder_id
                            == room_folder.id
                        ):
                            existing_link_count += 1

                projected_stay_count = expected_stay_count
                projected_room_count = expected_room_count
                projected_link_count = expected_room_count

                print(
                    f"  Stay Rooms root:       OK (id={root.id})"
                )
                print(
                    f"  Stay folders:          "
                    f"{projected_stay_count}/{expected_stay_count}"
                )
                print(
                    f"  Room folders:          "
                    f"{projected_room_count}/{expected_room_count}"
                )
                print(
                    f"  StayRooms linked:      "
                    f"{projected_link_count}/{expected_room_count}"
                )

            else:
                # Flush everything before verification.
                db.session.flush()

                actual_stay_folders = 0
                actual_room_folders = 0
                actual_links = 0

                for definition in STAYS:
                    stay_folder = find_child_by_name(
                        root,
                        definition.stay_name,
                    )

                    if stay_folder is None:
                        continue

                    if (
                        stay_folder.slug
                        != expected_stay_folder_slug(
                            definition.stay_slug
                        )
                    ):
                        raise RuntimeError(
                            f"Stay folder '{stay_folder.name}' "
                            f"has unexpected slug "
                            f"'{stay_folder.slug}'."
                        )

                    actual_stay_folders += 1

                    for room_definition in definition.rooms:
                        room_folder = find_child_by_name(
                            stay_folder,
                            room_definition.folder_name,
                        )

                        if room_folder is None:
                            continue

                        expected_room_slug = (
                            expected_room_folder_slug(
                                definition.stay_slug,
                                room_definition.folder_name,
                            )
                        )

                        if room_folder.slug != expected_room_slug:
                            raise RuntimeError(
                                f"Room folder '{room_folder.name}' "
                                f"under '{stay_folder.name}' has "
                                f"unexpected slug "
                                f"'{room_folder.slug}'."
                            )

                        actual_room_folders += 1

                        room = resolved_rooms[
                            (
                                definition.stay_slug,
                                room_definition.room_name,
                            )
                        ]

                        if room.media_folder_id == room_folder.id:
                            actual_links += 1
                        else:
                            raise RuntimeError(
                                f"StayRoom #{room.id} "
                                f"('{room.name}') is not linked to "
                                f"its expected room folder "
                                f"(expected id={room_folder.id}, "
                                f"actual id={room.media_folder_id})."
                            )

                print(
                    f"  Stay Rooms root:       OK (id={root.id})"
                )
                print(
                    f"  Stay folders:          "
                    f"{actual_stay_folders}/{expected_stay_count}"
                )
                print(
                    f"  Room folders:          "
                    f"{actual_room_folders}/{expected_room_count}"
                )
                print(
                    f"  StayRooms linked:      "
                    f"{actual_links}/{expected_room_count}"
                )

                if actual_stay_folders != expected_stay_count:
                    raise RuntimeError(
                        "Post-commit verification failed: "
                        f"expected {expected_stay_count} stay folders, "
                        f"found {actual_stay_folders}."
                    )

                if actual_room_folders != expected_room_count:
                    raise RuntimeError(
                        "Post-commit verification failed: "
                        f"expected {expected_room_count} room folders, "
                        f"found {actual_room_folders}."
                    )

                if actual_links != expected_room_count:
                    raise RuntimeError(
                        "Post-commit verification failed: "
                        f"expected {expected_room_count} StayRoom links, "
                        f"found {actual_links}."
                    )

            # =================================================================
            # SUMMARY
            # =================================================================

            print()
            print("=" * 79)
            print("Summary")
            print("=" * 79)

            print(
                f"Mode:                      "
                f"{'APPLY' if apply_mode else 'DRY RUN'}"
            )
            print(
                f"Stay Rooms root:           {ROOT_FOLDER_NAME}"
            )
            print(
                f"Stay folders created:      {stay_created_count}"
            )
            print(
                f"Stay folders reused:       {stay_reused_count}"
            )
            print(
                f"Room folders created:      {room_created_count}"
            )
            print(
                f"Room folders reused:       {room_reused_count}"
            )
            print(
                f"Folder metadata changed:   {metadata_changed_count}"
            )
            print(
                f"Room links created:        {room_links_created}"
            )
            print(
                f"Room links preserved:      {room_links_preserved}"
            )
            print(
                f"Expected room folders:     {expected_room_count}"
            )
            print(
                f"Expected room links:       {expected_room_count}"
            )

            # =================================================================
            # COMMIT
            # =================================================================

            if dry_run:
                print()
                print(
                    "DRY RUN COMPLETE — no database changes were committed."
                )
                print(
                    "Run with --apply to create/normalize the Stay Rooms "
                    "hierarchy and link the StayRoom records."
                )

                return 0

            db.session.commit()

            print()
            print("-" * 79)
            print("Post-commit verification")
            print("-" * 79)

            # Re-query after commit so verification tests the actual persisted
            # state rather than the in-memory SQLAlchemy state.
            db.session.expire_all()

            root_after_commit = MediaFolder.query.filter_by(
                slug=ROOT_FOLDER_SLUG
            ).first()

            if root_after_commit is None:
                raise RuntimeError(
                    "Post-commit verification failed: "
                    "Stay Rooms root was not found."
                )

            actual_stay_folders = 0
            actual_room_folders = 0
            actual_links = 0

            for definition in STAYS:
                stay_folder = find_child_by_name(
                    root_after_commit,
                    definition.stay_name,
                )

                if stay_folder is None:
                    continue

                actual_stay_folders += 1

                expected_stay_slug = expected_stay_folder_slug(
                    definition.stay_slug
                )

                if stay_folder.slug != expected_stay_slug:
                    raise RuntimeError(
                        "Post-commit verification failed: "
                        f"stay folder '{stay_folder.name}' has slug "
                        f"'{stay_folder.slug}', expected "
                        f"'{expected_stay_slug}'."
                    )

                for room_definition in definition.rooms:
                    room_folder = find_child_by_name(
                        stay_folder,
                        room_definition.folder_name,
                    )

                    if room_folder is None:
                        continue

                    actual_room_folders += 1

                    expected_room_slug = expected_room_folder_slug(
                        definition.stay_slug,
                        room_definition.folder_name,
                    )

                    if room_folder.slug != expected_room_slug:
                        raise RuntimeError(
                            "Post-commit verification failed: "
                            f"room folder '{room_folder.name}' has slug "
                            f"'{room_folder.slug}', expected "
                            f"'{expected_room_slug}'."
                        )

                    room = (
                        StayRoom.query
                        .filter_by(
                            stay_id=resolved_stays[
                                definition.stay_slug
                            ].id,
                            name=room_definition.room_name,
                        )
                        .first()
                    )

                    if room is None:
                        raise RuntimeError(
                            "Post-commit verification failed: "
                            f"StayRoom '{room_definition.room_name}' "
                            f"could not be reloaded."
                        )

                    if room.media_folder_id != room_folder.id:
                        raise RuntimeError(
                            "Post-commit verification failed: "
                            f"StayRoom #{room.id} is linked to "
                            f"MediaFolder id={room.media_folder_id}, "
                            f"expected id={room_folder.id}."
                        )

                    actual_links += 1

            print(
                f"  Stay folders:          "
                f"{actual_stay_folders}/{expected_stay_count}"
            )
            print(
                f"  Room folders:          "
                f"{actual_room_folders}/{expected_room_count}"
            )
            print(
                f"  StayRooms linked:      "
                f"{actual_links}/{expected_room_count}"
            )

            if actual_stay_folders != expected_stay_count:
                raise RuntimeError(
                    "Post-commit verification failed: stay folder count "
                    "does not match expected count."
                )

            if actual_room_folders != expected_room_count:
                raise RuntimeError(
                    "Post-commit verification failed: room folder count "
                    "does not match expected count."
                )

            if actual_links != expected_room_count:
                raise RuntimeError(
                    "Post-commit verification failed: StayRoom link count "
                    "does not match expected count."
                )

            print()
            print(
                "POST-COMMIT VERIFICATION PASSED."
            )
            print(
                "Stay Room media folder hierarchy is complete and consistent."
            )

            return 0

        except Exception as exc:
            if apply_mode:
                db.session.rollback()

            print()
            print("=" * 79)
            print("ERROR")
            print("=" * 79)
            print(str(exc))

            if apply_mode:
                print()
                print(
                    "Transaction rolled back. No changes from this run "
                    "were committed."
                )

            return 1


if __name__ == "__main__":
    sys.exit(main())