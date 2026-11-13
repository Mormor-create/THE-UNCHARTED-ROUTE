"""
===============================================================================
The Uncharted Route — Homepage Model
===============================================================================

Central CMS configuration for the public homepage.

The homepage is managed through the administrative CMS rather than relying
entirely on hard-coded template content.

Responsibilities
----------------
• Store homepage publishing state
• Store homepage-level metadata
• Store homepage SEO metadata
• Provide access to the current homepage configuration
• Maintain the relationship with homepage sections

The homepage does not duplicate experiences, destination, blog, or media
records. Those systems remain responsible for their own data.

===============================================================================
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Homepage
# =============================================================================

class Homepage(db.Model):
    """
    CMS configuration for the public homepage.

    The application is designed around a single homepage configuration.
    Individual pieces of homepage content are represented by
    HomepageSection records.
    """

    __tablename__ = "homepages"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # =========================================================================
    # Publishing
    # =========================================================================

    is_published = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )

    # =========================================================================
    # Homepage Metadata
    # =========================================================================

    title = db.Column(
        db.String(255),
        nullable=True,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    # =========================================================================
    # SEO
    # =========================================================================

    meta_title = db.Column(
        db.String(255),
        nullable=True,
    )

    meta_description = db.Column(
        db.Text,
        nullable=True,
    )

    # =========================================================================
    # Timestamps
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # =========================================================================
    # Relationships
    # =========================================================================

    sections = db.relationship(
        "HomepageSection",
        back_populates="homepage",
        cascade="all, delete-orphan",
        order_by="HomepageSection.display_order",
        lazy="select",
    )

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<Homepage "
            f"id={self.id!r} "
            f"is_published={self.is_published!r}>"
        )

    # =========================================================================
    # Current Homepage
    # =========================================================================

    @classmethod
    def get_current(cls):
        """
        Return the current homepage configuration.

        If no homepage configuration exists yet, an initial configuration
        is created.

        Returns
        -------
        Homepage
            The current homepage configuration.
        """

        homepage = cls.query.order_by(
            cls.id.asc()
        ).first()

        if homepage is None:

            homepage = cls(
                is_published=True,
            )

            db.session.add(homepage)
            db.session.commit()

        return homepage

    # =========================================================================
    # Publishing Helpers
    # =========================================================================

    def publish(self):
        """
        Publish the homepage.
        """

        self.is_published = True

    def unpublish(self):
        """
        Unpublish the homepage.
        """

        self.is_published = False