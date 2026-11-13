"""
===============================================================================
The Uncharted Route
Contact Reply Model
===============================================================================
Stores customer-facing replies sent in response to Contact enquiries.
A Contact represents the original enquiry, while each ContactReply represents
a response in the conversation.
This allows an enquiry to maintain a complete communication history.

Example:

    Contact
        ├── Original customer message
        ├── ContactReply #1
        ├── ContactReply #2
        └── ContactReply #3

Replies may be sent by administrators or staff members and can be tracked
for email delivery and response-time reporting.
"""

from datetime import datetime
from extensions import db
# =============================================================================
# Contact Reply Model
# =============================================================================
class ContactReply(db.Model):
    """
    Customer-facing reply belonging to a Contact enquiry.
    """
    __tablename__ = "contact_replies"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id = db.Column(db.Integer,primary_key=True,)
    # =========================================================================
    # Contact Relationship
    # =========================================================================
    contact_id = db.Column(db.Integer,db.ForeignKey("contacts.id",ondelete="CASCADE",),nullable=False,index=True,)
    # =========================================================================
    # Author / Sender
    # =========================================================================
    user_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="SET NULL",),nullable=True,index=True,)
    sender_name = db.Column(db.String(150),nullable=True,)
    sender_email = db.Column(db.String(255),nullable=True,)
    # =========================================================================
    # Reply Content
    # =========================================================================
    subject = db.Column(db.String(255),nullable=True,)
    message = db.Column(db.Text,nullable=False,)
    # =========================================================================
    # Delivery
    # =========================================================================
    delivery_method = db.Column(db.String(50),default="Email",nullable=False,)
    """
    Suggested delivery methods:
    Email
    Internal
    Manual
    """
    delivery_status = db.Column(db.String(50),default="Pending",nullable=False,index=True,)
    """
    Suggested delivery statuses:
    Pending
    Sent
    Delivered
    Failed
    """
    sent_at = db.Column(db.DateTime,nullable=True,index=True,)
    delivered_at = db.Column(db.DateTime,nullable=True,)
    failed_at = db.Column(db.DateTime,nullable=True,)
    error_message = db.Column(db.Text,nullable=True,)
    direction = db.Column(db.String(20),nullable=False,default="outgoing",index=True,)
    email_message_id = db.Column(db.String(512),nullable=True,unique=True,index=True,)
    received_at = db.Column(db.DateTime,nullable=True,index=True,)

    # =========================================================================
    # Audit
    # =========================================================================
    created_at = db.Column(db.DateTime,default=datetime.utcnow,nullable=False,index=True,)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False,)

    # =========================================================================
    # Relationships
    # =========================================================================
    contact = db.relationship("Contact",back_populates="replies",)
    user = db.relationship("User",backref=db.backref("contact_replies",lazy="dynamic",),)

    # =========================================================================
    # Helper Properties
    # =========================================================================
    @property
    def author_name(self):
        """
        Return the name of the user who sent the reply.
        Falls back to the stored sender name when the original user account
        is no longer available.
        """

        if self.user:
            return self.user.full_name
        return self.sender_name or "Unknown"

    @property
    def is_sent(self):
        """
        Determine whether the reply was successfully sent.
        """
        return self.delivery_status == "Sent"

    @property
    def is_delivered(self):
        """
        Determine whether the reply was delivered.
        """
        return self.delivery_status == "Delivered"

    @property
    def is_pending(self):
        """
        Determine whether the reply is still pending delivery.
        """
        return self.delivery_status == "Pending"

    @property
    def is_failed(self):
        """
        Determine whether delivery failed.
        """
        return self.delivery_status == "Failed"

    # =========================================================================
    # Delivery Helpers
    # =========================================================================
    def mark_sent(self):
        """
        Mark the reply as successfully sent.
        """
        self.delivery_status = "Sent"
        if self.sent_at is None:
            self.sent_at = datetime.utcnow()
        self.failed_at = None
        self.error_message = None
        # Update the parent contact's response timestamps.
        if self.contact:
            if self.contact.first_response_at is None:
                self.contact.first_response_at = self.sent_at
            self.contact.last_response_at = self.sent_at

    def mark_delivered(self):
        """
        Mark the reply as delivered.
        """
        self.delivery_status = "Delivered"
        if self.delivered_at is None:
            self.delivered_at = datetime.utcnow()
        # A delivered message has necessarily been sent.
        if self.sent_at is None:
            self.sent_at = self.delivered_at
        if self.contact:
            if self.contact.first_response_at is None:
                self.contact.first_response_at = self.sent_at
            self.contact.last_response_at = self.sent_at

    def mark_failed(self, error_message=None):
        """
        Mark the reply as failed.
        """
        self.delivery_status = "Failed"
        if self.failed_at is None:
            self.failed_at = datetime.utcnow()
        if error_message is not None:
            self.error_message = error_message

    def reset_delivery(self):
        """
        Reset delivery information so the reply can be attempted again.
        """
        self.delivery_status = "Pending"
        self.sent_at = None
        self.delivered_at = None
        self.failed_at = None
        self.error_message = None

    # =========================================================================
    # Representation
    # =========================================================================
    def __repr__(self):
        return (
            f"<ContactReply "
            f"{self.id} "
            f"Contact:{self.contact_id}>")