"""
===============================================================================
The Uncharted Route
Contact Reply Service
===============================================================================

Service layer for managing customer-facing replies to Contact enquiries.

Responsibilities:
    - Create contact replies
    - Retrieve individual replies
    - Retrieve conversation history
    - Filter and paginate replies
    - Search replies
    - Send replies through the central email service
    - Track delivery state
    - Retry failed replies
    - Mark replies as delivered
    - Record incoming customer replies
    - Track email Message-IDs for conversation threading
    - Calculate reply statistics
    - Delete replies

SMTP implementation remains inside app.services.email_service.
"""
from datetime import datetime
from email.utils import make_msgid
from extensions import db
from app.models import Contact, ContactReply
from app.services.email_service import send_email

# =============================================================================
# Constants
# =============================================================================
DELIVERY_METHOD_EMAIL = "Email"
DELIVERY_METHOD_INTERNAL = "Internal"
DELIVERY_METHOD_MANUAL = "Manual"

DELIVERY_METHODS = {
    DELIVERY_METHOD_EMAIL,
    DELIVERY_METHOD_INTERNAL,
    DELIVERY_METHOD_MANUAL,}

STATUS_PENDING = "Pending"
STATUS_SENT = "Sent"
STATUS_DELIVERED = "Delivered"
STATUS_FAILED = "Failed"
STATUS_RECEIVED = "Received"

DELIVERY_STATUSES = {
    STATUS_PENDING,
    STATUS_SENT,
    STATUS_DELIVERED,
    STATUS_FAILED,
    STATUS_RECEIVED,}

DIRECTION_INCOMING = "incoming"
DIRECTION_OUTGOING = "outgoing"

DIRECTIONS = {
    DIRECTION_INCOMING,
    DIRECTION_OUTGOING,}

# =============================================================================
# Contact Reply Service
# =============================================================================
class ContactReplyService:
    """Manage ContactReply records, conversation history, and email delivery."""

    # =========================================================================
    # Validation Helpers
    # =========================================================================
    @staticmethod
    def _validate_delivery_method(delivery_method):
        """Validate a reply delivery method."""
        if delivery_method not in DELIVERY_METHODS:
            raise ValueError(
                f"Invalid delivery method: {delivery_method}. "
                f"Expected one of: {', '.join(sorted(DELIVERY_METHODS))}."
            )

    @staticmethod
    def _validate_delivery_status(delivery_status):
        """Validate a reply delivery status."""
        if delivery_status not in DELIVERY_STATUSES:
            raise ValueError(
                f"Invalid delivery status: {delivery_status}. "
                f"Expected one of: {', '.join(sorted(DELIVERY_STATUSES))}."
            )

    @staticmethod
    def _validate_direction(direction):
        """Validate whether a message is incoming or outgoing."""
        if direction not in DIRECTIONS:
            raise ValueError(
                f"Invalid message direction: {direction}. "
                f"Expected one of: {', '.join(sorted(DIRECTIONS))}."
            )

    @staticmethod
    def _normalise_message_id(message_id):
        """Return a clean Message-ID value or None."""
        if not message_id:
            return None

        message_id = str(message_id).strip()

        if not message_id:
            return None

        if not message_id.startswith("<"):
            message_id = f"<{message_id}"

        if not message_id.endswith(">"):
            message_id = f"{message_id}>"

        return message_id

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_reply(
        contact_id,
        message,
        user_id=None,
        sender_name=None,
        sender_email=None,
        subject=None,
        delivery_method=DELIVERY_METHOD_EMAIL,
        delivery_status=STATUS_PENDING,
        direction=DIRECTION_OUTGOING,
        email_message_id=None,
        received_at=None,
        commit=True,
    ):
        """
        Create a ContactReply.

        Outgoing replies default to Pending. Incoming customer messages can be
        created with direction="incoming" and delivery_status="Received".
        """
        if not contact_id:
            raise ValueError("contact_id is required.")

        if not message or not str(message).strip():
            raise ValueError("Reply message cannot be empty.")

        ContactReplyService._validate_delivery_method(delivery_method)
        ContactReplyService._validate_delivery_status(delivery_status)
        ContactReplyService._validate_direction(direction)

        contact = db.session.get(Contact, contact_id)

        if contact is None:
            raise ValueError(
                f"Contact with ID {contact_id} was not found."
            )

        email_message_id = ContactReplyService._normalise_message_id(
            email_message_id
        )

        if email_message_id:
            existing = ContactReply.query.filter_by(
                email_message_id=email_message_id
            ).first()

            if existing is not None:
                return existing

        reply = ContactReply(
            contact_id=contact.id,
            user_id=user_id,
            sender_name=sender_name,
            sender_email=sender_email,
            subject=subject,
            message=str(message).strip(),
            delivery_method=delivery_method,
            delivery_status=delivery_status,
            direction=direction,
            email_message_id=email_message_id,
            received_at=received_at,
        )

        if direction == DIRECTION_INCOMING and received_at is None:
            reply.received_at = datetime.utcnow()

        db.session.add(reply)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Incoming Messages
    # =========================================================================
    @staticmethod
    def record_incoming_reply(
        contact_id,
        message,
        sender_email,
        sender_name=None,
        subject=None,
        email_message_id=None,
        received_at=None,
        commit=True,
    ):
        """
        Record a customer email received by the business mailbox.

        The mailbox synchronisation service must identify and validate the
        associated Contact before calling this method.

        Incoming customer messages do not belong to a CMS user, so user_id
        remains None.
        """
        if not sender_email or not str(sender_email).strip():
            raise ValueError("The incoming message sender email is required.")

        email_message_id = ContactReplyService._normalise_message_id(
            email_message_id
        )

        if email_message_id:
            existing = ContactReply.query.filter_by(
                email_message_id=email_message_id
            ).first()

            if existing is not None:
                return existing

        return ContactReplyService.create_reply(
            contact_id=contact_id,
            message=message,
            user_id=None,
            sender_name=sender_name,
            sender_email=str(sender_email).strip(),
            subject=subject,
            delivery_method=DELIVERY_METHOD_EMAIL,
            delivery_status=STATUS_RECEIVED,
            direction=DIRECTION_INCOMING,
            email_message_id=email_message_id,
            received_at=received_at or datetime.utcnow(),
            commit=commit,
        )

    # =========================================================================
    # Retrieval
    # =========================================================================
    @staticmethod
    def get_by_id(reply_id):
        """Retrieve a reply by ID."""
        if not reply_id:
            return None

        return db.session.get(ContactReply, reply_id)

    @staticmethod
    def get_reply(reply_id):
        """Alias for get_by_id()."""
        return ContactReplyService.get_by_id(reply_id)

    @staticmethod
    def get_by_contact(
        contact_id,
        delivery_status=None,
        delivery_method=None,
        direction=None,
        limit=None,
        offset=0,
        newest_first=False,
    ):
        """Retrieve replies belonging to a specific contact."""
        if not contact_id:
            return []

        query = ContactReply.query.filter(
            ContactReply.contact_id == contact_id
        )

        if delivery_status:
            ContactReplyService._validate_delivery_status(delivery_status)
            query = query.filter(
                ContactReply.delivery_status == delivery_status
            )

        if delivery_method:
            ContactReplyService._validate_delivery_method(delivery_method)
            query = query.filter(
                ContactReply.delivery_method == delivery_method
            )

        if direction:
            ContactReplyService._validate_direction(direction)
            query = query.filter(ContactReply.direction == direction)

        if newest_first:
            query = query.order_by(
                ContactReply.created_at.desc(),
                ContactReply.id.desc(),
            )
        else:
            query = query.order_by(
                ContactReply.created_at.asc(),
                ContactReply.id.asc(),
            )

        if offset:
            query = query.offset(max(0, offset))

        if limit is not None:
            query = query.limit(max(0, limit))

        return query.all()

    @staticmethod
    def get_conversation(contact_id):
        """Return the conversation history in chronological order."""
        return ContactReplyService.get_by_contact(
            contact_id=contact_id,
            newest_first=False,
        )

    @staticmethod
    def get_incoming(contact_id=None, limit=None, offset=0):
        """Retrieve incoming customer messages."""
        return ContactReplyService.get_all(
            contact_id=contact_id,
            direction=DIRECTION_INCOMING,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    @staticmethod
    def get_outgoing(contact_id=None, limit=None, offset=0):
        """Retrieve outgoing team replies."""
        return ContactReplyService.get_all(
            contact_id=contact_id,
            direction=DIRECTION_OUTGOING,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    # =========================================================================
    # Query / Filtering
    # =========================================================================
    @staticmethod
    def get_all(
        contact_id=None,
        user_id=None,
        delivery_status=None,
        delivery_method=None,
        sender_email=None,
        direction=None,
        date_from=None,
        date_to=None,
        limit=None,
        offset=0,
        newest_first=True,
    ):
        """Retrieve replies using optional filters."""
        query = ContactReply.query

        if contact_id is not None:
            query = query.filter(
                ContactReply.contact_id == contact_id
            )

        if user_id is not None:
            query = query.filter(ContactReply.user_id == user_id)

        if delivery_status:
            ContactReplyService._validate_delivery_status(delivery_status)
            query = query.filter(
                ContactReply.delivery_status == delivery_status
            )

        if delivery_method:
            ContactReplyService._validate_delivery_method(delivery_method)
            query = query.filter(
                ContactReply.delivery_method == delivery_method
            )

        if direction:
            ContactReplyService._validate_direction(direction)
            query = query.filter(ContactReply.direction == direction)

        if sender_email:
            query = query.filter(
                db.func.lower(ContactReply.sender_email)
                == str(sender_email).strip().lower()
            )

        if date_from:
            query = query.filter(ContactReply.created_at >= date_from)

        if date_to:
            query = query.filter(ContactReply.created_at <= date_to)

        if newest_first:
            query = query.order_by(
                ContactReply.created_at.desc(),
                ContactReply.id.desc(),
            )
        else:
            query = query.order_by(
                ContactReply.created_at.asc(),
                ContactReply.id.asc(),
            )

        if offset:
            query = query.offset(max(0, offset))

        if limit is not None:
            query = query.limit(max(0, limit))

        return query.all()

    # =========================================================================
    # Search
    # =========================================================================
    @staticmethod
    def search(search_term, limit=None, offset=0):
        """Search replies by subject, message, sender name, or sender email."""
        if not search_term or not str(search_term).strip():
            return []

        term = f"%{str(search_term).strip()}%"

        query = ContactReply.query.filter(
            db.or_(
                ContactReply.subject.ilike(term),
                ContactReply.message.ilike(term),
                ContactReply.sender_name.ilike(term),
                ContactReply.sender_email.ilike(term),
            )
        ).order_by(
            ContactReply.created_at.desc(),
            ContactReply.id.desc(),
        )

        if offset:
            query = query.offset(max(0, offset))

        if limit is not None:
            query = query.limit(max(0, limit))

        return query.all()

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_reply(reply_id, commit=True, **updates):
        """Update editable ContactReply fields."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return None

        allowed_fields = {
            "sender_name",
            "sender_email",
            "subject",
            "message",
            "delivery_method",
        }

        for field, value in updates.items():
            if field not in allowed_fields:
                continue

            if field == "message":
                if not value or not str(value).strip():
                    raise ValueError("Reply message cannot be empty.")
                value = str(value).strip()

            if field == "delivery_method":
                ContactReplyService._validate_delivery_method(value)

            setattr(reply, field, value)

        if hasattr(reply, "updated_at"):
            reply.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Delivery
    # =========================================================================
    @staticmethod
    def send_reply(
        reply_id,
        recipient=None,
        subject=None,
        sender=None,
        reply_to=None,
    ):
        """
        Send a ContactReply through the central email service.

        A Message-ID is generated and saved before delivery so future customer
        responses can be associated with this conversation through their
        In-Reply-To or References email headers.

        The email service must accept the message_id argument for the generated
        ID to be sent as the actual email Message-ID header.
        """
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            raise ValueError(
                f"Contact reply with ID {reply_id} was not found."
            )

        if reply.contact is None:
            raise ValueError(
                "Cannot send reply because the associated contact "
                "does not exist."
            )

        if reply.direction == DIRECTION_INCOMING:
            raise ValueError(
                "Incoming customer messages cannot be sent as team replies."
            )

        recipient = recipient or reply.contact.email

        if not recipient:
            raise ValueError("No recipient email address is available.")

        if not reply.message or not reply.message.strip():
            raise ValueError("Cannot send an empty reply.")

        email_subject = (
            subject
            or reply.subject
            or reply.contact.subject
            or "The Uncharted Route — Enquiry Response"
        )

        email_reply_to = (
            reply_to
            or reply.contact.email
            or reply.sender_email
            or None
        )

        reply.delivery_method = DELIVERY_METHOD_EMAIL
        reply.delivery_status = STATUS_PENDING
        reply.error_message = None
        reply.failed_at = None

        if not reply.email_message_id:
            reply.email_message_id = make_msgid(
                domain="theunchartedrouteke@gmail.com"
            )

        message_id = reply.email_message_id

        try:
            # Persist the Message-ID before sending. This allows the system
            # to retain the ID even if SMTP delivery subsequently fails.
            db.session.commit()

            result = send_email(
                recipient=recipient,
                subject=email_subject,
                body=reply.message,
                reply_to=email_reply_to,
                sender=sender,
                message_id=message_id,
            )

            if result is False:
                raise RuntimeError(
                    "The email service reported that the email could not "
                    "be sent."
                )

            reply.mark_sent()
            db.session.commit()

            return reply

        except Exception as exc:
            try:
                reply.mark_failed(str(exc))
                db.session.commit()
            except Exception:
                db.session.rollback()

            raise

    # =========================================================================
    # Delivery State
    # =========================================================================
    @staticmethod
    def mark_sent(reply_id, sent_at=None, commit=True):
        """Mark an outgoing reply as sent."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return None

        if sent_at is not None:
            reply.sent_at = sent_at

        reply.mark_sent()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def mark_delivered(reply_id, delivered_at=None, commit=True):
        """Mark an outgoing reply as delivered."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return None

        if delivered_at is not None:
            reply.delivered_at = delivered_at

        reply.mark_delivered()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def mark_failed(reply_id, error_message=None, commit=True):
        """Mark an outgoing reply as failed."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return None

        reply.mark_failed(error_message)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def reset_delivery(reply_id, commit=True):
        """Reset a reply's delivery state for another send attempt."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return None

        if reply.direction == DIRECTION_INCOMING:
            raise ValueError(
                "Incoming customer messages cannot be retried for sending."
            )

        reply.reset_delivery()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return reply

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Retry
    # =========================================================================
    @staticmethod
    def retry(reply_id, recipient=None):
        """Retry delivery of a failed outgoing reply."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            raise ValueError(
                f"Contact reply with ID {reply_id} was not found."
            )

        if reply.direction == DIRECTION_INCOMING:
            raise ValueError(
                "Incoming customer messages cannot be retried for sending."
            )

        if not reply.is_failed:
            raise ValueError("Only failed replies can be retried.")

        reply.reset_delivery()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return ContactReplyService.send_reply(
            reply_id=reply.id,
            recipient=recipient,
        )

    # =========================================================================
    # Pending / Failed / Delivered
    # =========================================================================
    @staticmethod
    def get_pending(limit=None, offset=0):
        """Return pending replies."""
        return ContactReplyService.get_all(
            delivery_status=STATUS_PENDING,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    @staticmethod
    def get_failed(limit=None, offset=0):
        """Return failed replies."""
        return ContactReplyService.get_all(
            delivery_status=STATUS_FAILED,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    @staticmethod
    def get_sent(limit=None, offset=0):
        """Return sent replies."""
        return ContactReplyService.get_all(
            delivery_status=STATUS_SENT,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    @staticmethod
    def get_delivered(limit=None, offset=0):
        """Return delivered replies."""
        return ContactReplyService.get_all(
            delivery_status=STATUS_DELIVERED,
            limit=limit,
            offset=offset,
            newest_first=True,
        )

    # =========================================================================
    # Counts
    # =========================================================================

    @staticmethod
    def count(
        contact_id=None,
        user_id=None,
        delivery_status=None,
        delivery_method=None,
        direction=None,
    ):
        """Count replies matching the supplied filters."""
        query = ContactReply.query

        if contact_id is not None:
            query = query.filter(
                ContactReply.contact_id == contact_id
            )

        if user_id is not None:
            query = query.filter(ContactReply.user_id == user_id)

        if delivery_status:
            ContactReplyService._validate_delivery_status(delivery_status)
            query = query.filter(
                ContactReply.delivery_status == delivery_status
            )

        if delivery_method:
            ContactReplyService._validate_delivery_method(delivery_method)
            query = query.filter(
                ContactReply.delivery_method == delivery_method
            )

        if direction:
            ContactReplyService._validate_direction(direction)
            query = query.filter(ContactReply.direction == direction)

        return query.count()

    # =========================================================================
    # Contact Reply Summary
    # =========================================================================

    @staticmethod
    def get_contact_summary(contact_id):
        """Return a compact communication summary for a contact."""
        contact = db.session.get(Contact, contact_id)

        if contact is None:
            return None

        total = ContactReplyService.count(contact_id=contact_id)

        pending = ContactReplyService.count(
            contact_id=contact_id,
            delivery_status=STATUS_PENDING,
        )

        sent = ContactReplyService.count(
            contact_id=contact_id,
            delivery_status=STATUS_SENT,
        )

        delivered = ContactReplyService.count(
            contact_id=contact_id,
            delivery_status=STATUS_DELIVERED,
        )

        failed = ContactReplyService.count(
            contact_id=contact_id,
            delivery_status=STATUS_FAILED,
        )

        incoming = ContactReplyService.count(
            contact_id=contact_id,
            direction=DIRECTION_INCOMING,
        )

        outgoing = ContactReplyService.count(
            contact_id=contact_id,
            direction=DIRECTION_OUTGOING,
        )

        last_reply = ContactReply.query.filter_by(
            contact_id=contact_id
        ).order_by(
            ContactReply.created_at.desc(),
            ContactReply.id.desc(),
        ).first()

        return {
            "contact_id": contact_id,
            "total_replies": total,
            "pending": pending,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "incoming": incoming,
            "outgoing": outgoing,
            "last_reply": last_reply,
            "last_reply_at": (
                last_reply.received_at
                if last_reply
                and last_reply.direction == DIRECTION_INCOMING
                and last_reply.received_at
                else last_reply.sent_at
                if last_reply and last_reply.sent_at
                else last_reply.created_at
                if last_reply
                else None
            ),
        }

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """Return overall ContactReply delivery and direction statistics."""
        return {
            "total": ContactReplyService.count(),
            "pending": ContactReplyService.count(
                delivery_status=STATUS_PENDING
            ),
            "sent": ContactReplyService.count(
                delivery_status=STATUS_SENT
            ),
            "delivered": ContactReplyService.count(
                delivery_status=STATUS_DELIVERED
            ),
            "failed": ContactReplyService.count(
                delivery_status=STATUS_FAILED
            ),
            "received": ContactReplyService.count(
                delivery_status=STATUS_RECEIVED
            ),
            "incoming": ContactReplyService.count(
                direction=DIRECTION_INCOMING
            ),
            "outgoing": ContactReplyService.count(
                direction=DIRECTION_OUTGOING
            ),
            "email": ContactReplyService.count(
                delivery_method=DELIVERY_METHOD_EMAIL
            ),
            "internal": ContactReplyService.count(
                delivery_method=DELIVERY_METHOD_INTERNAL
            ),
            "manual": ContactReplyService.count(
                delivery_method=DELIVERY_METHOD_MANUAL
            ),
        }

    # =========================================================================
    # Delete
    # =========================================================================
    @staticmethod
    def delete_reply(reply_id):
        """Permanently delete a ContactReply."""
        reply = ContactReplyService.get_by_id(reply_id)

        if reply is None:
            return False

        try:
            db.session.delete(reply)
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise

# =============================================================================
# Convenience Functions
# =============================================================================
def create_contact_reply(**kwargs):
    """Create a ContactReply."""
    return ContactReplyService.create_reply(**kwargs)

def get_contact_reply(reply_id):
    """Retrieve a ContactReply by ID."""
    return ContactReplyService.get_by_id(reply_id)

def get_contact_replies(contact_id, **kwargs):
    """Retrieve replies for a contact."""
    return ContactReplyService.get_by_contact(
        contact_id=contact_id,
        **kwargs,)

def send_contact_reply(reply_id, **kwargs):
    """Send a ContactReply."""
    return ContactReplyService.send_reply(
        reply_id=reply_id,
        **kwargs,)

def retry_contact_reply(reply_id, **kwargs):
    """Retry a failed ContactReply."""
    return ContactReplyService.retry(
        reply_id=reply_id,
        **kwargs,)

def mark_contact_reply_delivered(reply_id, **kwargs):
    """Mark a ContactReply as delivered."""
    return ContactReplyService.mark_delivered(
        reply_id=reply_id,
        **kwargs,)

def record_incoming_contact_reply(**kwargs):
    """Record an incoming customer email in an existing contact thread."""
    return ContactReplyService.record_incoming_reply(**kwargs)