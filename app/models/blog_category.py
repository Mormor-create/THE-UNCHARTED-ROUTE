"""
===============================================================================
The Uncharted Route
Blog Category Model
===============================================================================

Defines categories used to organize blog posts.

Categories improve:
    • Navigation
    • SEO
    • Content organization
    • Blog filtering
    • Content discovery

Examples:
    • Travel Guides
    • Safari Tips
    • Luxury Travel
    • Wildlife
    • Conservation
    • Beaches
    • Corporate Travel
    • Adventure
    • Food & Culture
    • Photography
    • News
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Blog Category Model
# =============================================================================
class BlogCategory(db.Model):
    """
    Category used to organize blog posts.
    """
    __tablename__ = "blog_categories"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Basic Information
    # =========================================================================
    name = db.Column(db.String(150),unique=True,nullable=False,index=True)
    slug = db.Column(db.String(180),unique=True,nullable=False,index=True)
    description = db.Column(db.Text,nullable=True)

    # =========================================================================
    # Display
    # =========================================================================
    icon = db.Column(db.String(100),nullable=True)
    color = db.Column(db.String(20),default="#14B8A6",nullable=False)
    banner_image = db.Column(db.String(255),nullable=True)

    # =========================================================================
    # SEO
    # =========================================================================
    meta_title = db.Column(db.String(255),nullable=True)
    meta_description = db.Column(db.Text,nullable=True)
    meta_keywords = db.Column(db.Text,nullable=True)

    # =========================================================================
    # Status / Display Control
    # =========================================================================
    featured = db.Column(db.Boolean,default=False,nullable=False,index=True)
    active = db.Column(db.Boolean,default=True,nullable=False,index=True)
    sort_order = db.Column(db.Integer,default=0,nullable=False,index=True)

    # =========================================================================
    # Relationships
    # =========================================================================
    posts = db.relationship(
        "BlogPost",
        back_populates="category",
        lazy="dynamic",
        cascade="all, delete-orphan")

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,index=True)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def post_count(self):
        """
        Return the total number of posts assigned to this category.
        """
        return self.posts.count()

    @property
    def published_post_count(self):
        """
        Return the number of published posts in this category.
        """
        return self.posts.filter_by(status="Published").count()

    @property
    def is_active(self):
        """
        Whether the category is currently active.
        """
        return self.active

    @property
    def is_featured(self):
        """
        Whether the category is featured.
        """
        return self.featured

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return f"<BlogCategory {self.name}>"