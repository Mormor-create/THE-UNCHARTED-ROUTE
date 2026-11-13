"""
===============================================================================
The Uncharted Route
Populate Experience Media Gallery Folders
===============================================================================

Creates one MediaFolder for every Experience under the existing:

    Experience Media Gallery

folder in the Media Library.

Existing experience folders are preserved.
Only missing folders are created.

Usage
-----

Dry run:

    python scripts/populate_experience_media_gallery_folders.py

Apply:

    python scripts/populate_experience_media_gallery_folders.py --apply

The script is intentionally idempotent. Running it again will not create
duplicate folders for experiences that already have a matching folder.
===============================================================================
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
import unicodedata
from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from extensions import db
from app.models.experience import Experience
from app.models.media_folder import MediaFolder


# =============================================================================
# CONFIGURATION
# =============================================================================

ROOT_FOLDER_NAME = "Experience Media Gallery"
ROOT_FOLDER_SLUG = "experience-media-gallery"

EXPECTED_EXPERIENCE_COUNT = 61


# =============================================================================
# HELPERS
# =============================================================================

def slugify(value: str) -> str:
    """
    Convert a human-readable experience title into a clean URL-safe slug.

    Example:

        Nairobi National Park Experience
        ->
        nairobi-national-park-experience
    """
    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = value.encode(
        "ascii",
        "ignore",
    ).decode(
        "ascii",
    )

    value = value.lower()

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


def find_root_folder() -> MediaFolder | None:
    """
    Find the Experience Media Gallery root folder.

    The root must be a top-level folder.
    """

    root = (
        MediaFolder.query
        .filter(
            MediaFolder.parent_id.is_(None),
            MediaFolder.active.is_(True),
        )
        .filter(
            db.or_(
                MediaFolder.slug == ROOT_FOLDER_SLUG,
                MediaFolder.name == ROOT_FOLDER_NAME,
            )
        )
        .first()
    )

    return root


def get_existing_child_folders(root_folder: MediaFolder):
    """
    Return direct child folders belonging to the Experience Media Gallery.
    """

    return (
        MediaFolder.query
        .filter(
            MediaFolder.parent_id == root_folder.id,
        )
        .order_by(
            MediaFolder.display_order.asc(),
            MediaFolder.name.asc(),
            MediaFolder.id.asc(),
        )
        .all()
    )


def make_unique_slug(
    base_slug: str,
    used_slugs: set[str],
) -> str:
    """
    Generate a globally unique MediaFolder slug.

    If the normal slug is already used, append -2, -3, etc.
    """

    if base_slug not in used_slugs:
        return base_slug

    counter = 2

    while True:
        candidate = f"{base_slug}-{counter}"

        if candidate not in used_slugs:
            return candidate

        counter += 1


def build_folder_name_set(folders):
    """
    Build a case-insensitive set of existing child-folder names.
    """

    return {
        folder.name.strip().casefold()
        for folder in folders
        if folder.name
    }


def get_next_display_order(folders):
    """
    Return the next display order after existing child folders.
    """

    if not folders:
        return 0

    return max(
        (
            folder.display_order
            for folder in folders
        ),
        default=-1,
    ) + 1


# =============================================================================
# MAIN
# =============================================================================

def populate(app: Flask, apply_changes: bool = False):
    """
    Discover missing Experience Media Gallery folders and optionally create
    them.
    """

    with app.app_context():

        print()
        print("=" * 79)
        print("THE UNCHARTED ROUTE")
        print("Experience Media Gallery Folder Population")
        print("=" * 79)
        print()

        # ---------------------------------------------------------------------
        # Find root
        # ---------------------------------------------------------------------

        root_folder = find_root_folder()

        if root_folder is None:
            print(
                "ERROR: Could not find the 'Experience Media Gallery' "
                "root folder."
            )
            print()
            print(
                "Expected either:"
            )
            print(
                f"  Name: {ROOT_FOLDER_NAME}"
            )
            print(
                f"  Slug: {ROOT_FOLDER_SLUG}"
            )
            print()
            return False

        print(
            f"Root folder found:"
        )
        print(
            f"  ID:   {root_folder.id}"
        )
        print(
            f"  Name: {root_folder.name}"
        )
        print(
            f"  Slug: {root_folder.slug}"
        )
        print()

        # ---------------------------------------------------------------------
        # Load experiences
        # ---------------------------------------------------------------------

        experiences = (
            Experience.query
            .order_by(
                Experience.id.asc()
            )
            .all()
        )

        print(
            f"Experiences found: {len(experiences)}"
        )

        if len(experiences) != EXPECTED_EXPERIENCE_COUNT:
            print()
            print(
                "WARNING:"
            )
            print(
                f"Expected approximately "
                f"{EXPECTED_EXPERIENCE_COUNT} experiences, "
                f"but found {len(experiences)}."
            )
            print()
            print(
                "The script will NOT stop automatically because the "
                "database may legitimately have changed."
            )

        print()

        # ---------------------------------------------------------------------
        # Existing child folders
        # ---------------------------------------------------------------------

        existing_folders = get_existing_child_folders(
            root_folder
        )

        existing_names = build_folder_name_set(
            existing_folders
        )

        used_slugs = {
            folder.slug.strip().lower()
            for folder in MediaFolder.query.all()
            if folder.slug
        }

        next_display_order = get_next_display_order(
            existing_folders
        )

        # ---------------------------------------------------------------------
        # Identify missing folders
        # ---------------------------------------------------------------------

        missing = []

        already_exists = []

        for experience in experiences:

            experience_name = (
                (experience.title or "").strip()
            )

            if not experience_name:
                print(
                    f"WARNING: Experience ID {experience.id} "
                    f"has no title. Skipping."
                )
                continue

            normalized_name = (
                experience_name.casefold()
            )

            if normalized_name in existing_names:
                matching_folder = next(
                    (
                        folder
                        for folder in existing_folders
                        if (
                            folder.name
                            and folder.name.strip().casefold()
                            == normalized_name
                        )
                    ),
                    None,
                )

                already_exists.append(
                    (
                        experience,
                        matching_folder,
                    )
                )

                continue

            base_slug = slugify(
                experience_name
            )

            if not base_slug:
                base_slug = (
                    f"experience-{experience.id}"
                )

            folder_slug = make_unique_slug(
                base_slug,
                used_slugs,
            )

            used_slugs.add(
                folder_slug
            )

            missing.append(
                {
                    "experience": experience,
                    "name": experience_name,
                    "slug": folder_slug,
                    "display_order": next_display_order,
                }
            )

            next_display_order += 1

        # ---------------------------------------------------------------------
        # Report existing folders
        # ---------------------------------------------------------------------

        print("-" * 79)
        print("EXISTING EXPERIENCE FOLDERS")
        print("-" * 79)

        if already_exists:
            for experience, folder in already_exists:
                print(
                    f"  [EXISTS] "
                    f"Experience #{experience.id}: "
                    f"{experience.title}"
                )
                print(
                    f"           Folder ID: {folder.id}"
                )
                print(
                    f"           Folder:    {folder.name}"
                )
        else:
            print(
                "  None found."
            )

        print()

        # ---------------------------------------------------------------------
        # Report missing folders
        # ---------------------------------------------------------------------

        print("-" * 79)
        print("MISSING EXPERIENCE FOLDERS")
        print("-" * 79)

        if missing:
            for item in missing:
                experience = item["experience"]

                print(
                    f"  [CREATE] "
                    f"Experience #{experience.id}: "
                    f"{item['name']}"
                )
                print(
                    f"           Slug: {item['slug']}"
                )
                print(
                    f"           Parent: "
                    f"{root_folder.name} "
                    f"(ID {root_folder.id})"
                )
        else:
            print(
                "  No missing folders."
            )

        print()

        # ---------------------------------------------------------------------
        # Summary
        # ---------------------------------------------------------------------

        print("=" * 79)
        print("SUMMARY")
        print("=" * 79)
        print(
            f"Experiences:          {len(experiences)}"
        )
        print(
            f"Existing folders:     {len(already_exists)}"
        )
        print(
            f"Folders to create:    {len(missing)}"
        )
        print(
            f"Target root folder:   "
            f"{root_folder.name} (ID {root_folder.id})"
        )
        print()

        if not missing:
            print(
                "Nothing needs to be created."
            )
            print()

            return True

        # ---------------------------------------------------------------------
        # Dry run
        # ---------------------------------------------------------------------

        if not apply_changes:

            print(
                "DRY RUN"
            )
            print(
                "No database changes have been made."
            )
            print()
            print(
                "If this list looks correct, run:"
            )
            print()
            print(
                "    python "
                "scripts/populate_experience_media_gallery_folders.py "
                "--apply"
            )
            print()

            return True

        # ---------------------------------------------------------------------
        # Apply changes
        # ---------------------------------------------------------------------

        print(
            "APPLYING CHANGES..."
        )
        print()

        created_count = 0

        try:

            for item in missing:

                experience = item["experience"]

                folder = MediaFolder(
                    name=item["name"],
                    slug=item["slug"],
                    description=(
                        f"Media folder for the experience "
                        f"'{item['name']}'."
                    ),
                    parent_id=root_folder.id,
                    folder_type="experience",
                    display_order=item["display_order"],
                    active=True,
                )

                db.session.add(folder)

                created_count += 1

                print(
                    f"  Created: "
                    f"{item['name']}"
                )

            db.session.commit()

        except Exception as exc:

            db.session.rollback()

            print()
            print(
                "ERROR: Database transaction failed."
            )
            print(
                f"Reason: {exc}"
            )
            print()
            print(
                "All changes from this run have been rolled back."
            )

            return False

        # ---------------------------------------------------------------------
        # Verify
        # ---------------------------------------------------------------------

        final_folders = get_existing_child_folders(
            root_folder
        )

        final_count = len(final_folders)

        print()
        print("=" * 79)
        print("COMPLETE")
        print("=" * 79)
        print(
            f"Folders created this run: {created_count}"
        )
        print(
            f"Total folders under "
            f"'{root_folder.name}': {final_count}"
        )
        print()

        # ---------------------------------------------------------------------
        # Verify every experience has a folder
        # ---------------------------------------------------------------------

        final_names = {
            folder.name.strip().casefold()
            for folder in final_folders
            if folder.name
        }

        missing_after_apply = [
            experience
            for experience in experiences
            if (
                experience.title
                and experience.title.strip().casefold()
                not in final_names
            )
        ]

        if missing_after_apply:

            print(
                "WARNING: Some experiences still do not have "
                "a matching folder:"
            )

            for experience in missing_after_apply:
                print(
                    f"  - #{experience.id}: "
                    f"{experience.title}"
                )

            print()

            return False

        print(
            "Verification passed."
        )
        print(
            "Every experience has a matching direct child folder "
            "under Experience Media Gallery."
        )
        print()

        return True


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Populate Experience Media Gallery folders "
            "for all TUR experiences."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually create missing folders. "
            "Without this flag the script performs a dry run."
        ),
    )

    args = parser.parse_args()

    app = create_app()

    success = populate(
        app,
        apply_changes=args.apply,
    )

    raise SystemExit(
        0 if success else 1
    )


if __name__ == "__main__":
    main()