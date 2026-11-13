"""
===============================================================================
THE UNCHARTED ROUTE
Testimonial Categories and Tags
===============================================================================
Reusable taxonomy for curated testimonials and customer-submitted feedback.
===============================================================================
"""

from datetime import datetime
from extensions import db
from app.models.testimonial import (
    testimonial_categories,
    testimonial_tags,
)

def testimonial_taxonomy_utcnow():
    return datetime.utcnow()

class TestimonialCategory(db.Model):
    """A category used to organize testimonials."""

    __tablename__ = "testimonial_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    description = db.Column(db.String(500))

    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=testimonial_taxonomy_utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=testimonial_taxonomy_utcnow,
        onupdate=testimonial_taxonomy_utcnow,
    )

    testimonials = db.relationship(
        "Testimonial",
        secondary=testimonial_categories,
        back_populates="categories",
    )

    def __repr__(self):
        return f"<TestimonialCategory {self.slug}>"


class TestimonialTag(db.Model):
    """A reusable descriptive tag for testimonials."""

    __tablename__ = "testimonial_tags"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(300))

    active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=testimonial_taxonomy_utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=testimonial_taxonomy_utcnow,
        onupdate=testimonial_taxonomy_utcnow,)

    testimonials = db.relationship(
        "Testimonial",
        secondary=testimonial_tags,
        back_populates="tags",)

    def __repr__(self):
        return f"<TestimonialTag {self.slug}>"
