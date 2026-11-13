"""
===============================================================================
The Uncharted Route
Legal & Help Admin Service
===============================================================================
"""

from sqlalchemy.orm import selectinload
from extensions import db
from app.models.legal_help_page import LegalHelpPage
from app.models.legal_help_section import LegalHelpSection
from app.models.legal_help_item import LegalHelpItem

class LegalHelpService:

    # =========================================================================
    # PUBLIC
    # =========================================================================
    @staticmethod
    def get_public_page(slug):
        return (
            LegalHelpPage.query
            .options(
                selectinload(LegalHelpPage.sections)
                .selectinload(LegalHelpSection.items)
            )
            .filter(
                LegalHelpPage.slug == slug,
                LegalHelpPage.active.is_(True),
            )
            .first()
        )

    # =========================================================================
    # PAGES
    # =========================================================================

    @staticmethod
    def get_pages():
        return (
            LegalHelpPage.query
            .order_by(
                LegalHelpPage.page_type,
                LegalHelpPage.title,
            )
            .all()
        )

    @staticmethod
    def get_page(page_id):
        return (
            LegalHelpPage.query
            .options(
                selectinload(LegalHelpPage.sections)
                .selectinload(LegalHelpSection.items)
            )
            .get(page_id)
        )

    @staticmethod
    def create_page(data):
        page = LegalHelpPage(
            slug=data["slug"].strip().lower(),
            page_type=data["page_type"],
            eyebrow=data.get("eyebrow"),
            title=data["title"],
            intro=data.get("intro"),
            meta_title=data.get("meta_title"),
            meta_description=data.get("meta_description"),
            active=data.get("active", True),
        )

        db.session.add(page)
        db.session.commit()

        return page

    @staticmethod
    def update_page(page, data):
        page.slug = data["slug"].strip().lower()
        page.page_type = data["page_type"]
        page.eyebrow = data.get("eyebrow")
        page.title = data["title"]
        page.intro = data.get("intro")
        page.meta_title = data.get("meta_title")
        page.meta_description = data.get("meta_description")
        page.active = data.get("active", False)

        db.session.commit()

        return page

    @staticmethod
    def delete_page(page):
        db.session.delete(page)
        db.session.commit()

    # =========================================================================
    # SECTIONS
    # =========================================================================

    @staticmethod
    def get_section(section_id):
        return (
            LegalHelpSection.query
            .options(
                selectinload(LegalHelpSection.items)
            )
            .get(section_id)
        )

    @staticmethod
    def create_section(page, data):
        section = LegalHelpSection(
            page_id=page.id,
            section_key=data["section_key"].strip().lower(),
            section_type=data["section_type"],
            eyebrow=data.get("eyebrow"),
            title=data.get("title"),
            body=data.get("body"),
            secondary_body=data.get("secondary_body"),
            primary_cta_label=data.get("primary_cta_label"),
            primary_cta_url=data.get("primary_cta_url"),
            secondary_cta_label=data.get("secondary_cta_label"),
            secondary_cta_url=data.get("secondary_cta_url"),
            sort_order=data.get("sort_order", 0),
            active=data.get("active", True),
        )

        db.session.add(section)
        db.session.commit()

        return section

    @staticmethod
    def update_section(section, data):
        section.section_key = data["section_key"].strip().lower()
        section.section_type = data["section_type"]
        section.eyebrow = data.get("eyebrow")
        section.title = data.get("title")
        section.body = data.get("body")
        section.secondary_body = data.get("secondary_body")
        section.primary_cta_label = data.get("primary_cta_label")
        section.primary_cta_url = data.get("primary_cta_url")
        section.secondary_cta_label = data.get("secondary_cta_label")
        section.secondary_cta_url = data.get("secondary_cta_url")
        section.sort_order = data.get("sort_order", 0)
        section.active = data.get("active", False)

        db.session.commit()

        return section

    @staticmethod
    def delete_section(section):
        db.session.delete(section)
        db.session.commit()

    # =========================================================================
    # ITEMS
    # =========================================================================

    @staticmethod
    def get_item(item_id):
        return LegalHelpItem.query.get(item_id)

    @staticmethod
    def create_item(section, data):
        item = LegalHelpItem(
            section_id=section.id,
            item_type=data["item_type"],
            eyebrow=data.get("eyebrow"),
            title=data["title"],
            body=data.get("body"),
            link_label=data.get("link_label"),
            link_url=data.get("link_url"),
            sort_order=data.get("sort_order", 0),
            active=data.get("active", True),
        )

        db.session.add(item)
        db.session.commit()

        return item

    @staticmethod
    def update_item(item, data):
        item.item_type = data["item_type"]
        item.eyebrow = data.get("eyebrow")
        item.title = data["title"]
        item.body = data.get("body")
        item.link_label = data.get("link_label")
        item.link_url = data.get("link_url")
        item.sort_order = data.get("sort_order", 0)
        item.active = data.get("active", False)

        db.session.commit()

        return item

    @staticmethod
    def delete_item(item):
        db.session.delete(item)
        db.session.commit()

