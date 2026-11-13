"""
Stores application notifications for authenticated users.

Notifications are created by notification_service.py and may represent:

• Booking notifications
• Booking confirmations
• Booking cancellations
• Payment notifications
• Review notifications
• Contact enquiries
• Account notifications
• System notifications

Supported channels:

• In-App
• Email
• Both

Notifications may optionally reference another application object such as
a Booking, ExperienceReview, Contact, or User.
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Notification Model
# =============================================================================

class Notification(db.Model):
    """
    Represents an application notification delivered to a user.
    """

    __tablename__ = "notifications"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # =========================================================================
    # Recipient
    # =========================================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Notification Content
    # =========================================================================

    title = db.Column(
        db.String(255),
        nullable=False,
    )

    message = db.Column(
        db.Text,
        nullable=False,
    )

    # =========================================================================
    # Classification
    # =========================================================================

    notification_type = db.Column(
        db.String(100),
        default="General",
        nullable=False,
        index=True,
    )

    # General
    # Booking
    # Booking Confirmation
    # Booking Cancellation
    # Payment
    # Review
    # Contact
    # Account
    # System

    # =========================================================================
    # Delivery Channel
    # =========================================================================

    channel = db.Column(
        db.String(50),
        default="In-App",
        nullable=False,
    )

    # In-App
    # Email
    # Both

    # =========================================================================
    # Priority
    # =========================================================================

    priority = db.Column(
        db.String(30),
        default="Normal",
        nullable=False,
    )

    # Low
    # Normal
    # High
    # Urgent

    # =========================================================================
    # Action
    # =========================================================================

    action_url = db.Column(
        db.String(500),
    )

    # =========================================================================
    # Reference
    # =========================================================================

    reference_type = db.Column(
        db.String(100),
    )

    reference_id = db.Column(
        db.Integer,
        index=True,
    )

    # Examples:
    #
    # reference_type = "Booking"
    # reference_id = 123
    #
    # reference_type = "ExperienceReview"
    # reference_id = 45
    #
    # reference_type = "Contact"
    # reference_id = 18
    #
    # reference_type = "User"
    # reference_id = 7

    # =========================================================================
    # Read Status
    # =========================================================================

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    read_at = db.Column(
        db.DateTime,
    )

    # =========================================================================
    # Delivery Status
    # =========================================================================

    email_sent = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    email_sent_at = db.Column(
        db.DateTime,
    )

    # =========================================================================
    # Status
    # =========================================================================

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    # =========================================================================
    # Relationship
    # =========================================================================

    user = db.relationship(
        "User",
        backref=db.backref(
            "notifications",
            lazy="dynamic",
            cascade="all, delete-orphan",
        ),
    )

    # =========================================================================
    # Audit Fields
    # =========================================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # =========================================================================
    # Helper Properties
    # =========================================================================

    @property
    def is_unread(self):
        """
        Determine whether the notification has not been read.
        """

        return not self.is_read

    @property
    def is_urgent(self):
        """
        Determine whether the notification is urgent.
        """

        return self.priority == "Urgent"

    @property
    def has_action(self):
        """
        Determine whether the notification has an action URL.
        """

        return bool(self.action_url)

    @property
    def has_reference(self):
        """
        Determine whether the notification references another object.
        """

        return (
            self.reference_type is not None
            and self.reference_id is not None
        )

    @property
    def requires_email(self):
        """
        Determine whether this notification should be delivered by email.
        """

        return self.channel in {
            "Email",
            "Both",
        }

    @property
    def is_in_app(self):
        """
        Determine whether this notification should appear in the application.
        """

        return self.channel in {
            "In-App",
            "Both",
        }

    # =========================================================================
    # Read Management Helpers
    # =========================================================================

    def mark_as_read(self):
        """
        Mark this notification as read.
        """

        self.is_read = True
        self.read_at = datetime.utcnow()

    def mark_as_unread(self):
        """
        Mark this notification as unread.
        """

        self.is_read = False
        self.read_at = None

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<Notification "
            f"id={self.id} "
            f"user_id={self.user_id} "
            f"title='{self.title}'>"
        )