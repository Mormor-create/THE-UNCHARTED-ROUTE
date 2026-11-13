"""
===============================================================================
The Uncharted Route
Blog Post Model
===============================================================================

Represents articles published on The Uncharted Route website.

The blog is a core marketing channel used to:

    • Educate travelers
    • Improve SEO
    • Inspire booking
    • Showcase destinations
    • Showcase experiences
    • Promote conservation
    • Share travel advice
    • Build brand authority
"""

from datetime import datetime
from extensions import db

# =============================================================================
# Blog Post Model
# =============================================================================
class BlogPost(db.Model):
    """
    Blog article.
    """
    __tablename__ = "blog_posts"

    # =========================================================================
    # Status Constants
    # =========================================================================
    STATUS_DRAFT = "Draft"
    STATUS_REVIEW = "Review"
    STATUS_SCHEDULED = "Scheduled"
    STATUS_PUBLISHED = "Published"
    STATUS_ARCHIVED = "Archived"
    STATUSES = (
        STATUS_DRAFT,
        STATUS_REVIEW,
        STATUS_SCHEDULED,
        STATUS_PUBLISHED,
        STATUS_ARCHIVED,)

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True)

    # =========================================================================
    # Category
    # =========================================================================
    category_id = db.Column(db.Integer,db.ForeignKey(
            "blog_categories.id",
            ondelete="RESTRICT"),
        nullable=False,index=True)

    # =========================================================================
    # Basic Information
    # =========================================================================
    title = db.Column(db.String(255),nullable=False,index=True)
    slug = db.Column(db.String(300),unique=True,nullable=False,index=True)
    subtitle = db.Column(db.String(500),nullable=True)
    excerpt = db.Column(db.Text,nullable=True)
    content = db.Column(db.Text,nullable=False)

    # =========================================================================
    # Author
    # =========================================================================
    author = db.Column(db.String(150),nullable=False)
    author_title = db.Column(db.String(150),nullable=True)
    author_photo = db.Column(db.String(255),nullable=True)

    # =========================================================================
    # Media
    # =========================================================================
    featured_image = db.Column(db.String(255),nullable=True)
    featured_image_alt = db.Column(db.String(255),nullable=True)
    cover_video = db.Column(db.String(500),nullable=True)
    gallery = db.Column(db.JSON,nullable=True)

    # =========================================================================
    # Reading Information
    # =========================================================================
    reading_time = db.Column(db.Integer,default=5,nullable=False)
    word_count = db.Column(db.Integer,default=0,nullable=False)

    # =========================================================================
    # Publishing
    # =========================================================================
    status = db.Column(db.String(50),default=STATUS_DRAFT,nullable=False,index=True)
    published_at = db.Column(db.DateTime,nullable=True,index=True)
    scheduled_for = db.Column(db.DateTime,nullable=True,index=True)
    featured = db.Column(db.Boolean,default=False,nullable=False,index=True)
    pinned = db.Column(db.Boolean,default=False,nullable=False,index=True)
    allow_comments = db.Column(db.Boolean,default=True,nullable=False)

    # =========================================================================
    # Related Experience / Destination
    # =========================================================================
    related_experience_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "experiences.id",
            ondelete="SET NULL"
        ),nullable=True,index=True)

    related_destination_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "destinations.id",
            ondelete="SET NULL"
        ),nullable=True,index=True)

    # =========================================================================
    # Marketing CTA
    # =========================================================================
    cta_title = db.Column(db.String(255),nullable=True)
    cta_text = db.Column(db.Text,nullable=True)
    cta_button_text = db.Column(db.String(100),nullable=True)
    cta_button_url = db.Column(db.String(500),nullable=True)

    # =========================================================================
    # SEO
    # =========================================================================
    meta_title = db.Column(db.String(255),nullable=True)
    meta_description = db.Column(db.Text,nullable=True)
    meta_keywords = db.Column(db.Text,nullable=True)
    canonical_url = db.Column(db.String(500),nullable=True)
    social_title = db.Column(db.String(255),nullable=True)
    social_description = db.Column(db.Text,nullable=True)
    social_image = db.Column(db.String(255),nullable=True)

    # =========================================================================
    # Statistics
    # =========================================================================
    views = db.Column(db.Integer,default=0,nullable=False)
    likes = db.Column(db.Integer,default=0,nullable=False)
    shares = db.Column(db.Integer,default=0,nullable=False)
    newsletter_sent = db.Column(db.Boolean,default=False,nullable=False)
    search_indexed = db.Column(db.Boolean,default=False,nullable=False)

    # =========================================================================
    # Relationships
    # =========================================================================
    category = db.relationship("BlogCategory",back_populates="posts")
    experience = db.relationship(
        "Experience",
        backref=db.backref(
            "blog_posts",
            lazy="dynamic"))
    destination = db.relationship(
        "Destination",
        backref=db.backref(
            "blog_posts",
            lazy="dynamic"))

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,index=True)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # =========================================================================
    # Status Properties
    # =========================================================================
    @property
    def is_draft(self):
        return self.status == self.STATUS_DRAFT

    @property
    def is_in_review(self):
        return self.status == self.STATUS_REVIEW

    @property
    def is_scheduled(self):
        return self.status == self.STATUS_SCHEDULED

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def is_archived(self):
        return self.status == self.STATUS_ARCHIVED

    @property
    def is_featured(self):
        return self.featured

    @property
    def is_pinned(self):
        return self.pinned

    # =========================================================================
    # Reading Properties
    # =========================================================================
    @property
    def reading_time_text(self):
        minutes = self.reading_time or 1
        return f"{minutes} min read"

    # =========================================================================
    # Publishing Helpers
    # =========================================================================

    def publish(self, published_at=None):
        """
        Publish the article immediately.
        """
        self.status = self.STATUS_PUBLISHED
        self.published_at = (published_at or datetime.utcnow())
        self.scheduled_for = None

    def unpublish(self):
        """
        Return a published article to draft status.
        """
        self.status = self.STATUS_DRAFT
        self.published_at = None
        self.scheduled_for = None

    def submit_for_review(self):
        """
        Submit the article for editorial review.
        """
        self.status = self.STATUS_REVIEW

    def schedule(self, scheduled_for):
        """
        Schedule the article for future publication.
        """
        if scheduled_for is None:
            raise ValueError(
                "scheduled_for is required."
            )

        self.status = self.STATUS_SCHEDULED
        self.scheduled_for = scheduled_for
        self.published_at = None

    def archive(self):
        """
        Archive the article.
        """
        self.status = self.STATUS_ARCHIVED
        self.scheduled_for = None

    def restore(self):
        """
        Restore an archived article to draft status.
        """
        self.status = self.STATUS_DRAFT
        self.scheduled_for = None
        self.published_at = None

    # =========================================================================
    # Statistics Helpers
    # =========================================================================
    def increment_views(self, amount=1):
        """
        Increment article views.
        """
        if amount < 1:
            return
        self.views = (self.views or 0) + amount

    def increment_likes(self, amount=1):
        """
        Increment article likes.
        """
        if amount < 1:
            return
        self.likes = (self.likes or 0) + amount

    def increment_shares(self, amount=1):
        """
        Increment article shares.
        """
        if amount < 1:
            return
        self.shares = (self.shares or 0) + amount

    # =========================================================================
    # Reading Statistics
    # =========================================================================

    def calculate_reading_stats(self, words_per_minute=200):
        """
        Calculate and store word count and estimated reading time.

        Returns:
            tuple: (word_count, reading_time)
        """

        if not self.content:
            self.word_count = 0
            self.reading_time = 1
            return self.word_count, self.reading_time

        words = self.content.split()

        self.word_count = len(words)

        words_per_minute = max(
            int(words_per_minute or 200),
            1
        )

        self.reading_time = max(
            1,
            round(
                self.word_count / words_per_minute
            )
        )

        return self.word_count, self.reading_time

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return f"<BlogPost {self.title}>"