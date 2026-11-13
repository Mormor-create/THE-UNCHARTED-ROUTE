"""
===============================================================================
The Uncharted Route
Experience Inquiry Model
===============================================================================
Stores public enquiries submitted by guests interested in an experience.
An inquiry is not a confirmed booking. The team can review the enquiry,
contact the guest, and follow up separately.
"""

from datetime import datetime
from uuid import uuid4
from extensions import db

class ExperienceInquiry(db.Model):
    """Public enquiry for a TUR experience."""
    __tablename__ = "experience_inquiries"

    # =========================================================================
    # Primary Key and Reference
    # =========================================================================
    id = db.Column(db.Integer, primary_key=True)
    inquiry_reference = db.Column(db.String(40),unique=True,nullable=False,index=True,default=lambda: f"EXP-{uuid4().hex[:12].upper()}",)

    # =========================================================================
    # Experience
    # =========================================================================
    experience_id = db.Column(db.Integer,db.ForeignKey("experiences.id", ondelete="RESTRICT"),nullable=False,index=True,)
    experience = db.relationship(
        "Experience",
        backref=db.backref(
            "inquiries",
            lazy="dynamic",),)

    # =========================================================================
    # Guest Contact Information
    # =========================================================================
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), nullable=False, index=True)
    phone = db.Column(db.String(40), nullable=False)
    country = db.Column(db.String(100))

    # =========================================================================
    # Enquiry Details
    # =========================================================================
    preferred_date = db.Column(db.Date, nullable=True)
    adults = db.Column(db.Integer, nullable=False, default=1)
    children = db.Column(db.Integer, nullable=False, default=0)
    infants = db.Column(db.Integer, nullable=False, default=0)
    preferred_currency = db.Column(
        db.String(10),
        nullable=False,
        default="KES",)
    special_requests = db.Column(db.Text)

    # =========================================================================
    # Enquiry Management
    # =========================================================================
    status = db.Column(db.String(30),nullable=False,default="New",index=True,)
    source = db.Column(db.String(50),nullable=False,default="Website",)
    internal_notes = db.Column(db.Text)
    assigned_to_id = db.Column(db.Integer,db.ForeignKey("users.id", ondelete="SET NULL"),nullable=True,index=True,)
    assigned_to = db.relationship("User",foreign_keys=[assigned_to_id],)

    # =========================================================================
    # Audit Fields
    # =========================================================================
    created_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,index=True,)
    updated_at = db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow,)
    is_archived = db.Column(db.Boolean,nullable=False,default=False,server_default=db.false(),index=True,)

    # =========================================================================
    # Helpers
    # =========================================================================
    @property
    def total_guests(self):
        """Return the total number of guests included in the enquiry."""
        return (self.adults or 0) + (self.children or 0) + (self.infants or 0)

    def __repr__(self):
        return (
            f"<ExperienceInquiry "
            f"{self.inquiry_reference} - {self.full_name}>")