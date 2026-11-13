"""
===============================================================================
The Uncharted Route
Legal & Help Page Model
===============================================================================

Stores CMS-managed public pages such as:

- About
- FAQ
- Privacy Policy
- Terms & Conditions

Page content is organized through related LegalHelpSection records.
===============================================================================
"""

from datetime import datetime
from extensions import db

class LegalHelpPage(db.Model):
    __tablename__ = "legal_help_pages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    slug = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    page_type = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    eyebrow = db.Column(
        db.String(150),
        nullable=True,
    )

    title = db.Column(
        db.String(255),
        nullable=False,
    )

    intro = db.Column(
        db.Text,
        nullable=True,
    )

    meta_title = db.Column(
        db.String(255),
        nullable=True,
    )

    meta_description = db.Column(
        db.Text,
        nullable=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    sections = db.relationship(
        "LegalHelpSection",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="LegalHelpSection.sort_order",
        lazy="selectin",
    )

    @property
    def active_sections(self):
        return [
            section
            for section in self.sections
            if section.active
        ]

    @property
    def sections_by_key(self):
        return {
            section.section_key: section
            for section in self.active_sections
        }

    @property
    def public_title(self):
        return self.meta_title or self.title

    @property
    def public_description(self):
        return self.meta_description or self.intro or ""

    def get_section(self, section_key):
        return next(
            (
                section
                for section in self.active_sections
                if section.section_key == section_key
            ),
            None,
        )

    def __repr__(self):
        return (
            f"<LegalHelpPage "
            f"id={self.id} "
            f"slug={self.slug!r} "
            f"title={self.title!r}>"
        )