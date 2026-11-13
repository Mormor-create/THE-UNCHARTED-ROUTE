"""
===============================================================================
The Uncharted Route
FAQ Model
===============================================================================

Stores individual Frequently Asked Questions managed through the admin CMS.
===============================================================================
"""

from datetime import datetime
from extensions import db

class FAQ(db.Model):
    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(
        db.String(500),
        nullable=False,
    )

    answer = db.Column(
        db.Text,
        nullable=False,
    )

    category = db.Column(
        db.String(100),
        nullable=True,
        index=True,
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

    @property
    def category_label(self):
        return self.category or "General"

    def __repr__(self):
        return f"<FAQ {self.question!r}>"