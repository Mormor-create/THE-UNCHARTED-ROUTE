"""
===============================================================================
The Uncharted Route
Legal & Help Section Model
===============================================================================

Represents a major content section belonging to a LegalHelpPage.

Examples:

About:
- hero
- story
- philosophy
- creations
- kenya
- journal
- final_cta

FAQ:
- hero
- faq
- final_cta

Privacy:
- hero
- privacy_content

Terms:
- hero
- terms_content
===============================================================================
"""

from datetime import datetime

from extensions import db


class LegalHelpSection(db.Model):
    __tablename__ = "legal_help_sections"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    page_id = db.Column(
        db.Integer,
        db.ForeignKey("legal_help_pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    section_key = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    section_type = db.Column(
        db.String(50),
        nullable=False,
        default="content",
    )

    eyebrow = db.Column(
        db.String(150),
        nullable=True,
    )

    title = db.Column(
        db.String(255),
        nullable=True,
    )

    body = db.Column(
        db.Text,
        nullable=True,
    )

    secondary_body = db.Column(
        db.Text,
        nullable=True,
    )

    primary_cta_label = db.Column(
        db.String(150),
        nullable=True,
    )

    primary_cta_url = db.Column(
        db.String(500),
        nullable=True,
    )

    secondary_cta_label = db.Column(
        db.String(150),
        nullable=True,
    )

    secondary_cta_url = db.Column(
        db.String(500),
        nullable=True,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        index=True,
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

    page = db.relationship(
        "LegalHelpPage",
        back_populates="sections",
    )

    items = db.relationship(
        "LegalHelpItem",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="LegalHelpItem.sort_order",
        lazy="selectin",
    )

    @property
    def active_items(self):
        return [
            item
            for item in self.items
            if item.active
        ]

    def __repr__(self):
        return (
            f"<LegalHelpSection "
            f"id={self.id} "
            f"page_id={self.page_id} "
            f"key={self.section_key!r}>"
        )