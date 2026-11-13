"""
===============================================================================
The Uncharted Route
Experience Tag Model
===============================================================================
Stores searchable tags associated with experiences.
Tags improve search, filtering, recommendations, and SEO.
Examples

Adventure
Luxury
Photography
Bird Watching
Big Five
Family Friendly
Corporate
Romantic
Hiking
Camping
Beach
Wildlife
Conservation
Food
Culture
Nairobi
Weekend Escape
"""

from datetime import datetime

from extensions import db

# =============================================================================
# Association Table
# =============================================================================
experience_tags = db.Table(
    "experience_tags",

    db.Column(
        "experience_id",
        db.Integer,
        db.ForeignKey("experiences.id"),
        primary_key=True),

    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True))

# =============================================================================
# Experience Tag Model
# =============================================================================
class ExperienceTag(db.Model):
    """
    Searchable tags used to classify experiences.
    """
    __tablename__ = "tags"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(
        db.Integer,
        primary_key=True)

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = db.Column(db.String(100),unique=True,nullable=False,index=True)
    slug = db.Column(db.String(120),unique=True,nullable=False,index=True)
    description = db.Column(db.Text)

    # =========================================================================
    # Display
    # =========================================================================
    color = db.Column(db.String(20),default="#10B981")
    icon = db.Column(db.String(100))
    featured = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = db.Column(
        db.String(255)
    )

    meta_description = db.Column(
        db.Text
    )

    # =========================================================================
    # Status
    # =========================================================================
    active = db.Column(db.Boolean,default=True,nullable=False)
    sort_order = db.Column(db.Integer,default=0,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    experiences = db.relationship("Experience",secondary=experience_tags,back_populates="tags",lazy="dynamic")

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def experience_count(self):
        return self.experiences.count()

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<ExperienceTag {self.name}>")