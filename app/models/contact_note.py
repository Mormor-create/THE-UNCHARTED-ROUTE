"""
===============================================================================
The Uncharted Route
Contact Note Model
===============================================================================

Stores internal notes attached to Contact enquiries.

Contact notes are for internal use only and must never be sent to the
customer as part of a customer-facing reply.

Typical uses include:

- Internal handover notes
- Customer preferences
- Follow-up instructions
- Pricing discussions
- Operations notes
- Management notes
- Escalation details
- Research findings
- Resolution context

Example:

    Contact
        ├── Original customer enquiry
        ├── Customer Reply
        ├── Internal Note
        ├── Customer Reply
        └── Internal Note
"""

from datetime import datetime

from extensions import db


# =============================================================================
# Contact Note Model
# =============================================================================

class ContactNote(db.Model):
    """
    Internal note belonging to a Contact enquiry.
    """

    __tablename__ = "contact_notes"

    # =========================================================================
    # Primary Key
    # =========================================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # =========================================================================
    # Contact Relationship
    # =========================================================================

    contact_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "contacts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Author
    # =========================================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    author_name = db.Column(
        db.String(150),
        nullable=True,
    )

    # =========================================================================
    # Note Content
    # =========================================================================

    note = db.Column(
        db.Text,
        nullable=False,
    )

    # =========================================================================
    # Note Classification
    # =========================================================================

    note_type = db.Column(
        db.String(50),
        default="General",
        nullable=False,
        index=True,
    )
    """
    Suggested note types:

    General
    Follow Up
    Customer
    Operations
    Booking
    Sales
    Management
    Escalation
    Resolution
    """

    is_important = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # =========================================================================
    # Audit
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
    # Relationships
    # =========================================================================

    contact = db.relationship(
        "Contact",
        back_populates="notes",
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "contact_notes",
            lazy="dynamic",
        ),
    )

    # =========================================================================
    # Helper Properties
    # =========================================================================

    @property
    def created_by_name(self):
        """
        Return the name of the user who created the note.

        Falls back to the stored author name if the original user account
        is no longer available.
        """

        if self.user:
            return self.user.full_name

        return self.author_name or "Unknown"

    @property
    def is_general(self):
        """
        Determine whether this is a general note.
        """

        return self.note_type == "General"

    @property
    def is_follow_up(self):
        """
        Determine whether this note concerns a follow-up.
        """

        return self.note_type == "Follow Up"

    @property
    def is_resolution(self):
        """
        Determine whether this note concerns resolution of the enquiry.
        """

        return self.note_type == "Resolution"

    @property
    def is_escalation(self):
        """
        Determine whether this note concerns an escalation.
        """

        return self.note_type == "Escalation"

    # =========================================================================
    # Note Helpers
    # =========================================================================

    def mark_important(self):
        """
        Mark the note as important.
        """

        self.is_important = True

    def mark_not_important(self):
        """
        Remove the important flag from the note.
        """

        self.is_important = False

    def toggle_important(self):
        """
        Toggle the important flag.
        """

        self.is_important = not self.is_important

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self):
        return (
            f"<ContactNote "
            f"{self.id} "
            f"Contact:{self.contact_id}>"
        )