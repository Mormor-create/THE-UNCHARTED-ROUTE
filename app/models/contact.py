"""
===============================================================================
The Uncharted Route
Contact / Enquiry Model
===============================================================================
Stores enquiries submitted through the website and serves as the company's
CRM inbox.
The model supports:
- General enquiries
- Tour / experience enquiries
- Booking support
- Corporate travel
- Custom safari requests
- Partnership requests
- Media enquiries
- Supplier enquiries
- Complaints
- Compliments
- Customer support
Contacts may originate from the public website, landing pages, social
channels, WhatsApp, or other configured sources.

The model also supports:

- Assignment to internal users
- Status tracking
- Priority management
- Follow-up management
- Read / unread tracking
- Resolution tracking
- Archiving
- Newsletter consent
- Technical submission information
"""

from datetime import datetime

from extensions import db

# =============================================================================
# Contact Model
# =============================================================================
class Contact(db.Model):
    """
    Website contact enquiry.
    A Contact represents the original enquiry/conversation record.
    Customer-facing replies and internal notes are stored separately through
    ContactReply and ContactNote models.
    """
    __tablename__ = "contacts"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)

    # =========================================================================
    # Customer / User Relationship
    # =========================================================================
    user_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="SET NULL",),nullable=True,index=True,)

    # =========================================================================
    # Contact Information
    # =========================================================================
    first_name = db.Column(db.String(100),nullable=False,)
    last_name = db.Column(db.String(100),nullable=True,)
    email = db.Column(db.String(255),nullable=False,index=True,)
    phone = db.Column(db.String(50),nullable=True,)
    company = db.Column(db.String(150),nullable=True,)
    country = db.Column(db.String(100),nullable=True,)

    # =========================================================================
    # Enquiry Details
    # =========================================================================
    subject = db.Column(db.String(255),nullable=False,)
    enquiry_type = db.Column(db.String(100),nullable=False,default="General",index=True,)
    """
    Suggested enquiry types:

    General
    Tour
    Booking
    Corporate
    Partnership
    Media
    Supplier
    Complaint
    Compliment
    Support
    Custom Experience
    """
    message = db.Column(db.Text,nullable=False,)

    # =========================================================================
    # Status
    # =========================================================================
    status = db.Column(db.String(50),default="New",nullable=False,index=True,)
    """
    Suggested statuses:

    New
    Assigned
    In Progress
    Waiting for Customer
    Resolved
    Closed
    """

    priority = db.Column(db.String(50),default="Normal",nullable=False,index=True,)
    """
    Suggested priorities:

    Low
    Normal
    High
    Urgent
    """

    # =========================================================================
    # Assignment
    # =========================================================================
    assigned_user_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="SET NULL",),nullable=True,index=True,)

    # Kept for backwards compatibility with the original model/database
    # structure. New application logic should prefer assigned_user_id.
    assigned_to = db.Column(db.String(150),nullable=True,)
    department = db.Column(db.String(100),nullable=True,index=True,)

    # =========================================================================
    # Conversation Tracking
    # =========================================================================
    is_read = db.Column(db.Boolean,default=False,nullable=False,index=True,)
    read_at = db.Column(db.DateTime,nullable=True,)
    first_response_at = db.Column(db.DateTime,nullable=True,)
    last_response_at = db.Column(db.DateTime,nullable=True,)

    # =========================================================================
    # Follow Up
    # =========================================================================
    follow_up_required = db.Column(db.Boolean,default=True,nullable=False,)
    follow_up_date = db.Column(db.DateTime,nullable=True,index=True,)

    # =========================================================================
    # Resolution
    # =========================================================================
    resolved_at = db.Column(db.DateTime,nullable=True,)
    resolved_by_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="SET NULL",),nullable=True,index=True,)
    resolution_notes = db.Column(db.Text,nullable=True,)

    # =========================================================================
    # Closure
    # =========================================================================

    closed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    closed_by_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,)

    # =========================================================================
    # Archive
    # =========================================================================
    is_archived = db.Column(db.Boolean,default=False,nullable=False,index=True,)
    archived_at = db.Column(db.DateTime,nullable=True,)
    archived_by_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="SET NULL",),nullable=True,index=True,)

    # =========================================================================
    # Marketing
    # =========================================================================
    newsletter_opt_in = db.Column(db.Boolean,default=False,nullable=False,)

    # =========================================================================
    # Technical Information
    # =========================================================================
    ip_address = db.Column(db.String(100),nullable=True,)
    user_agent = db.Column(db.Text,nullable=True,)
    source = db.Column(db.String(100),default="Website",nullable=True,index=True,)
    """
    Suggested sources:
    Website
    Landing Page
    Facebook
    Instagram
    LinkedIn
    Google
    WhatsApp
    Email
    Referral
    Manual
    """
    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,index=True,)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,)

    # =========================================================================
    # Relationships
    # =========================================================================
    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref=db.backref(
            "contact_enquiries",
            lazy="dynamic",),)

    assigned_user = db.relationship(
        "User",
        foreign_keys=[assigned_user_id],
        backref=db.backref(
            "assigned_contacts",
            lazy="dynamic",),)

    resolved_by = db.relationship(
        "User",
        foreign_keys=[resolved_by_id],
        backref=db.backref(
            "resolved_contacts",
            lazy="dynamic",),)

    closed_by = db.relationship(
        "User",
        foreign_keys=[closed_by_id],
        backref=db.backref(
            "closed_contacts",
            lazy="dynamic",),)

    archived_by = db.relationship(
        "User",
        foreign_keys=[archived_by_id],
        backref=db.backref(
            "archived_contacts",
            lazy="dynamic",),)

    replies = db.relationship(
        "ContactReply",
        back_populates="contact",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="ContactReply.created_at.asc()",)

    notes = db.relationship(
        "ContactNote",
        back_populates="contact",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="ContactNote.created_at.asc()",)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def full_name(self):
        """
        Return the customer's full name.
        """
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_open(self):
        """
        Determine whether the enquiry is still active.
        """
        return self.status not in {
            "Resolved",
            "Closed",}

    @property
    def is_new(self):
        """
        Determine whether the enquiry is new.
        """
        return self.status == "New"

    @property
    def is_unread(self):
        """
        Determine whether the enquiry has not yet been read.
        """
        return not self.is_read

    @property
    def is_resolved(self):
        """
        Determine whether the enquiry has been resolved.
        """
        return self.status == "Resolved"

    @property
    def is_closed(self):
        """
        Determine whether the enquiry has been closed.
        """
        return self.status == "Closed"

    @property
    def is_archived_contact(self):
        """
        Determine whether the enquiry has been archived.
        """
        return self.is_archived

    @property
    def has_assignment(self):
        """
        Determine whether the enquiry has been assigned.
        """
        return self.assigned_user_id is not None or bool(
            self.assigned_to)

    @property
    def needs_follow_up(self):
        """
        Determine whether the enquiry currently requires follow-up.
        """
        if not self.follow_up_required:
            return False
        if not self.follow_up_date:
            return True
        return self.follow_up_date <= datetime.utcnow()

    @property
    def has_received_reply(self):
        """
        Determine whether at least one response has been recorded.
        """

        return self.first_response_at is not None

    @property
    def response_time(self):
        """
        Return the time between enquiry creation and first response.
        Returns a timedelta when a response has been recorded, otherwise None.
        """
        if not self.first_response_at:
            return None
        return self.first_response_at - self.created_at

    @property
    def resolution_time(self):
        """
        Return the time between enquiry creation and resolution.
        Returns a timedelta when resolved, otherwise None.
        """
        if not self.resolved_at:
            return None
        return self.resolved_at - self.created_at

    @property
    def assigned_name(self):
        """
        Return the assigned user's name.
        Falls back to the legacy assigned_to field where necessary.
        """
        if self.assigned_user:
            return self.assigned_user.full_name
        return self.assigned_to

    # =========================================================================
    # Status Helpers
    # =========================================================================
    def mark_as_read(self):
        """
        Mark the enquiry as read.
        """
        self.is_read = True
        if self.read_at is None:
            self.read_at = datetime.utcnow()

    def mark_as_unread(self):
        """
        Mark the enquiry as unread.
        """
        self.is_read = False
        self.read_at = None

    def assign_to(self, user):
        """
        Assign the enquiry to an internal user.

        The legacy assigned_to field is also populated for compatibility.
        """
        self.assigned_user = user
        if user:
            self.assigned_to = user.full_name
            self.status = "Assigned"

    def clear_assignment(self):
        """
        Remove the current assignment.
        """
        self.assigned_user = None
        self.assigned_to = None

    def mark_in_progress(self):
        """
        Mark the enquiry as actively being handled.
        """
        self.status = "In Progress"

    def mark_waiting_for_customer(self):
        """
        Mark the enquiry as waiting for a customer response.
        """
        self.status = "Waiting for Customer"

    def mark_resolved(self, user=None, notes=None):
        """
        Mark the enquiry as resolved.
        """
        self.status = "Resolved"
        if self.resolved_at is None:
            self.resolved_at = datetime.utcnow()
        if user is not None:
            self.resolved_by = user
        if notes is not None:
            self.resolution_notes = notes

    def mark_closed(self, user=None):
        """
        Mark the enquiry as closed.
        """
        self.status = "Closed"
        if self.closed_at is None:
            self.closed_at = datetime.utcnow()
        if user is not None:
            self.closed_by = user

    def reopen(self):
        """
        Reopen a resolved or closed enquiry.
        """
        self.status = "In Progress"
        self.resolved_at = None
        self.resolved_by = None
        self.closed_at = None
        self.closed_by = None

    def archive(self, user=None):
        """
        Archive the enquiry.
        """
        self.is_archived = True
        if self.archived_at is None:
            self.archived_at = datetime.utcnow()
        if user is not None:
            self.archived_by = user

    def unarchive(self):
        """
        Remove the enquiry from the archive.
        """
        self.is_archived = False
        self.archived_at = None
        self.archived_by = None

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<Contact "
            f"{self.id}: "
            f"{self.full_name}>")