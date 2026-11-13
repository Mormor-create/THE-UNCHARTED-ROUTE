"""
===============================================================================
THE UNCHARTED ROUTE — BLOG CATALOGUE AUDIT
===============================================================================

Purpose
-------
Inspect the current Blog Category and Blog Post catalogue before population.
This script is READ-ONLY.
It does NOT:
    - create records
    - update records
    - delete records
    - flush changes
    - commit changes
    - alter existing content

The audit reports:
    - all Blog Categories
    - all Blog Posts
    - complete post metadata
    - complete article content
    - publishing status
    - related Experiences
    - related Destinations
    - media fields
    - SEO fields
    - CTA fields
    - reading statistics
    - engagement statistics
    - detected HTML/content structure
    - category/post relationships

The existing Blog Post content is printed in full so that its editorial
formatting can be studied before creating the new launch articles.

Run
---
    python audit_blog_catalogue.py
===============================================================================
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------
# PROJECT BOOTSTRAP
# --------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("FLASK_ENV", "development")

from collections import Counter
from datetime import datetime
from flask import Flask
from extensions import db
from app.models.blog_post import BlogPost
from app.models.blog_category import BlogCategory

# =============================================================================
# Flask Application Bootstrap
# =============================================================================
def create_audit_app():
    """
    Import the application's existing Flask app factory.

    Adjust only the import path if this project exposes the factory under
    another module.
    """
    from app import create_app

    app = create_app()
    return app


# =============================================================================
# Formatting Helpers
# =============================================================================
SEPARATOR = "=" * 88
SUB_SEPARATOR = "-" * 88


def print_section(title):
    print()
    print(SEPARATOR)
    print(title)
    print(SEPARATOR)


def print_subsection(title):
    print()
    print(SUB_SEPARATOR)
    print(title)
    print(SUB_SEPARATOR)


def value_or_none(value):
    if value is None:
        return "None"
    return value


def yes_no(value):
    return "YES" if value else "NO"


def format_datetime(value):
    if value is None:
        return "None"

    if isinstance(value, datetime):
        return value.isoformat(sep=" ")

    return str(value)


def print_field(label, value):
    print(f"{label:<32}: {value_or_none(value)}")


# =============================================================================
# Content / HTML Inspection
# =============================================================================

HTML_TAG_PATTERN = re.compile(r"<\s*([a-zA-Z0-9]+)\b[^>]*>", re.IGNORECASE)


def detect_content_structure(content):
    """
    Inspect the stored BlogPost.content without modifying it.

    Detects common HTML/editor structures so the existing article's formatting
    can be reproduced in future launch posts.
    """

    if not content:
        return {
            "content_type": "EMPTY",
            "tags": [],
            "tag_counts": {},
            "has_headings": False,
            "has_paragraphs": False,
            "has_unordered_lists": False,
            "has_ordered_lists": False,
            "has_links": False,
            "has_images": False,
            "has_blockquotes": False,
            "has_tables": False,
            "has_strong_text": False,
            "has_emphasis": False,
            "has_breaks": False,
        }

    tags = [
        tag.lower()
        for tag in HTML_TAG_PATTERN.findall(content)
    ]

    tag_counts = Counter(tags)

    html_indicators = {
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "a",
        "img",
        "blockquote",
        "table",
        "strong",
        "b",
        "em",
        "i",
        "br",
    }

    has_html = any(tag in html_indicators for tag in tag_counts)

    return {
        "content_type": "HTML/RICH TEXT" if has_html else "PLAIN TEXT",
        "tags": sorted(set(tags)),
        "tag_counts": dict(sorted(tag_counts.items())),
        "has_headings": any(
            tag in tag_counts
            for tag in ("h1", "h2", "h3", "h4", "h5", "h6")
        ),
        "has_paragraphs": "p" in tag_counts,
        "has_unordered_lists": "ul" in tag_counts,
        "has_ordered_lists": "ol" in tag_counts,
        "has_links": "a" in tag_counts,
        "has_images": "img" in tag_counts,
        "has_blockquotes": "blockquote" in tag_counts,
        "has_tables": "table" in tag_counts,
        "has_strong_text": any(
            tag in tag_counts
            for tag in ("strong", "b")
        ),
        "has_emphasis": any(
            tag in tag_counts
            for tag in ("em", "i")
        ),
        "has_breaks": "br" in tag_counts,
    }


def print_content_structure(content):
    structure = detect_content_structure(content)

    print_field("Stored content type", structure["content_type"])
    print_field(
        "Detected HTML tags",
        ", ".join(structure["tags"]) if structure["tags"] else "None",
    )

    if structure["tag_counts"]:
        print("Tag counts:")
        for tag, count in structure["tag_counts"].items():
            print(f"    <{tag}>: {count}")
    else:
        print("Tag counts: None")

    print()
    print("Formatting features:")
    print(f"    Headings       : {yes_no(structure['has_headings'])}")
    print(f"    Paragraphs     : {yes_no(structure['has_paragraphs'])}")
    print(f"    Bullet lists   : {yes_no(structure['has_unordered_lists'])}")
    print(f"    Numbered lists : {yes_no(structure['has_ordered_lists'])}")
    print(f"    Links          : {yes_no(structure['has_links'])}")
    print(f"    Images         : {yes_no(structure['has_images'])}")
    print(f"    Blockquotes    : {yes_no(structure['has_blockquotes'])}")
    print(f"    Tables         : {yes_no(structure['has_tables'])}")
    print(f"    Bold text      : {yes_no(structure['has_strong_text'])}")
    print(f"    Italic text    : {yes_no(structure['has_emphasis'])}")
    print(f"    Line breaks    : {yes_no(structure['has_breaks'])}")


# =============================================================================
# Category Audit
# =============================================================================

def audit_categories():
    categories = (
        BlogCategory.query
        .order_by(
            BlogCategory.sort_order.asc(),
            BlogCategory.name.asc(),
            BlogCategory.id.asc(),
        )
        .all()
    )

    print_section("BLOG CATEGORIES")

    print(f"Total categories: {len(categories)}")

    if not categories:
        print("No BlogCategory records found.")
        return categories

    for category in categories:
        print_subsection(
            f"Category #{category.id} — {category.name}"
        )

        print_field("ID", category.id)
        print_field("Name", category.name)
        print_field("Slug", category.slug)
        print_field("Description", category.description)
        print_field("Icon", category.icon)
        print_field("Color", category.color)
        print_field("Banner Image", category.banner_image)

        print_field("Meta Title", category.meta_title)
        print_field("Meta Description", category.meta_description)
        print_field("Meta Keywords", category.meta_keywords)

        print_field("Featured", yes_no(category.featured))
        print_field("Active", yes_no(category.active))
        print_field("Sort Order", category.sort_order)

        print_field("Total Posts", category.post_count)
        print_field(
            "Published Posts",
            category.published_post_count,
        )

        print_field(
            "Created At",
            format_datetime(category.created_at),
        )
        print_field(
            "Updated At",
            format_datetime(category.updated_at),
        )

    return categories


# =============================================================================
# Post Audit
# =============================================================================

def audit_posts():
    posts = (
        BlogPost.query
        .order_by(
            BlogPost.created_at.asc(),
            BlogPost.id.asc(),
        )
        .all()
    )

    print_section("BLOG POSTS")

    print(f"Total posts: {len(posts)}")

    if not posts:
        print("No BlogPost records found.")
        return posts

    for post in posts:
        print_subsection(
            f"POST #{post.id} — {post.title}"
        )

        # ---------------------------------------------------------------------
        # Identity
        # ---------------------------------------------------------------------
        print("IDENTITY")
        print_field("ID", post.id)
        print_field("Title", post.title)
        print_field("Slug", post.slug)
        print_field("Subtitle", post.subtitle)
        print_field("Category ID", post.category_id)
        print_field(
            "Category Name",
            post.category.name if post.category else None,
        )
        print_field(
            "Category Slug",
            post.category.slug if post.category else None,
        )

        # ---------------------------------------------------------------------
        # Author
        # ---------------------------------------------------------------------
        print()
        print("AUTHOR")
        print_field("Author", post.author)
        print_field("Author Title", post.author_title)
        print_field("Author Photo", post.author_photo)

        # ---------------------------------------------------------------------
        # Editorial
        # ---------------------------------------------------------------------
        print()
        print("EDITORIAL")
        print_field("Excerpt", post.excerpt)

        print()
        print("CONTENT STRUCTURE")
        print_content_structure(post.content)

        print()
        print("FULL STORED CONTENT")
        print(SUB_SEPARATOR)
        print(post.content or "")
        print(SUB_SEPARATOR)

        # ---------------------------------------------------------------------
        # Reading
        # ---------------------------------------------------------------------
        print()
        print("READING INFORMATION")
        print_field("Reading Time", post.reading_time)
        print_field("Reading Time Text", post.reading_time_text)
        print_field("Word Count", post.word_count)

        # ---------------------------------------------------------------------
        # Media
        # ---------------------------------------------------------------------
        print()
        print("MEDIA")
        print_field("Featured Image", post.featured_image)
        print_field(
            "Featured Image Alt",
            post.featured_image_alt,
        )
        print_field("Cover Video", post.cover_video)
        print_field("Gallery", post.gallery)

        # ---------------------------------------------------------------------
        # Publishing
        # ---------------------------------------------------------------------
        print()
        print("PUBLISHING")
        print_field("Status", post.status)
        print_field("Published At", format_datetime(post.published_at))
        print_field("Scheduled For", format_datetime(post.scheduled_for))
        print_field("Featured", yes_no(post.featured))
        print_field("Pinned", yes_no(post.pinned))
        print_field(
            "Allow Comments",
            yes_no(post.allow_comments),
        )

        print_field("Is Draft", yes_no(post.is_draft))
        print_field("Is In Review", yes_no(post.is_in_review))
        print_field("Is Scheduled", yes_no(post.is_scheduled))
        print_field("Is Published", yes_no(post.is_published))
        print_field("Is Archived", yes_no(post.is_archived))

        # ---------------------------------------------------------------------
        # Related Experience / Destination
        # ---------------------------------------------------------------------
        print()
        print("RELATED EXPERIENCE / DESTINATION")

        print_field(
            "Related Experience ID",
            post.related_experience_id,
        )
        print_field(
            "Related Experience",
            (
                post.experience.title
                if post.experience
                else None
            ),
        )
        print_field(
            "Related Experience Slug",
            (
                post.experience.slug
                if post.experience
                else None
            ),
        )

        print_field(
            "Related Destination ID",
            post.related_destination_id,
        )
        print_field(
            "Related Destination",
            (
                post.destination.name
                if post.destination
                else None
            ),
        )
        print_field(
            "Related Destination Slug",
            (
                post.destination.slug
                if post.destination
                else None
            ),
        )

        # ---------------------------------------------------------------------
        # Marketing CTA
        # ---------------------------------------------------------------------
        print()
        print("MARKETING CTA")
        print_field("CTA Title", post.cta_title)
        print_field("CTA Text", post.cta_text)
        print_field("CTA Button Text", post.cta_button_text)
        print_field("CTA Button URL", post.cta_button_url)

        # ---------------------------------------------------------------------
        # SEO
        # ---------------------------------------------------------------------
        print()
        print("SEO")
        print_field("Meta Title", post.meta_title)
        print_field("Meta Description", post.meta_description)
        print_field("Meta Keywords", post.meta_keywords)
        print_field("Canonical URL", post.canonical_url)
        print_field("Social Title", post.social_title)
        print_field("Social Description", post.social_description)
        print_field("Social Image", post.social_image)

        # ---------------------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------------------
        print()
        print("STATISTICS")
        print_field("Views", post.views)
        print_field("Likes", post.likes)
        print_field("Shares", post.shares)
        print_field(
            "Newsletter Sent",
            yes_no(post.newsletter_sent),
        )
        print_field(
            "Search Indexed",
            yes_no(post.search_indexed),
        )

        # ---------------------------------------------------------------------
        # Audit
        # ---------------------------------------------------------------------
        print()
        print("AUDIT")
        print_field(
            "Created At",
            format_datetime(post.created_at),
        )
        print_field(
            "Updated At",
            format_datetime(post.updated_at),
        )

        return posts

# =============================================================================
# Catalogue Summary
# =============================================================================
def print_summary(categories, posts):
    print_section("BLOG CATALOGUE SUMMARY")

    published = [
        post for post in posts
        if post.status == BlogPost.STATUS_PUBLISHED
    ]

    draft = [
        post for post in posts
        if post.status == BlogPost.STATUS_DRAFT
    ]

    review = [
        post for post in posts
        if post.status == BlogPost.STATUS_REVIEW
    ]

    scheduled = [
        post for post in posts
        if post.status == BlogPost.STATUS_SCHEDULED
    ]

    archived = [
        post for post in posts
        if post.status == BlogPost.STATUS_ARCHIVED
    ]

    featured = [
        post for post in posts
        if post.featured
    ]

    pinned = [
        post for post in posts
        if post.pinned
    ]

    print_field("Total categories", len(categories))
    print_field("Total posts", len(posts))
    print_field("Published posts", len(published))
    print_field("Draft posts", len(draft))
    print_field("Review posts", len(review))
    print_field("Scheduled posts", len(scheduled))
    print_field("Archived posts", len(archived))
    print_field("Featured posts", len(featured))
    print_field("Pinned posts", len(pinned))

    print()
    print("Category distribution:")

    if not categories:
        print("    None")

    for category in categories:
        print(
            f"    {category.id}: "
            f"{category.name} — "
            f"{category.post_count} post(s)"
        )

    print()
    print("Post status distribution:")

    status_counts = Counter(
        post.status
        for post in posts
    )

    if not status_counts:
        print("    None")
    else:
        for status, count in sorted(status_counts.items()):
            print(f"    {status}: {count}")


# =============================================================================
# Main
# =============================================================================

def main():
    app = create_audit_app()

    with app.app_context():
        print()
        print(SEPARATOR)
        print("THE UNCHARTED ROUTE — BLOG CATALOGUE AUDIT")
        print(SEPARATOR)
        print("READ-ONLY AUDIT")
        print("No records will be created, updated, deleted, or committed.")
        print()

        categories = audit_categories()
        posts = audit_posts()

        print_summary(categories, posts)

        print()
        print(SEPARATOR)
        print("BLOG AUDIT COMPLETE")
        print(SEPARATOR)
        print()


if __name__ == "__main__":
    main()