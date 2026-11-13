"""
===============================================================================
The Uncharted Route
Legal & Help Item Model
===============================================================================
Flexible content items belonging to a LegalHelpSection.

Used for:

- FAQ questions and answers
- About philosophy cards
- About experience category cards
- Legal sections
- Future CMS content blocks
===============================================================================
"""

from datetime import datetime

from extensions import db


class LegalHelpItem(db.Model):
    __tablename__ = "legal_help_items"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    section_id = db.Column(
        db.Integer,
        db.ForeignKey("legal_help_sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_type = db.Column(
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
        nullable=False,
    )

    body = db.Column(
        db.Text,
        nullable=True,
    )

    link_label = db.Column(
        db.String(150),
        nullable=True,
    )

    link_url = db.Column(
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

    section = db.relationship(
        "LegalHelpSection",
        back_populates="items",
    )

    def __repr__(self):
        return (
            f"<LegalHelpItem "
            f"id={self.id} "
            f"section_id={self.section_id} "
            f"title={self.title!r}>"
        )