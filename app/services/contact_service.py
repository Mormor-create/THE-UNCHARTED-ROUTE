"""
===============================================================================
The Uncharted Route
Contact / Enquiry Service
===============================================================================
Business logic for website contact enquiries.
Handles:

- Creating enquiries
- Retrieving enquiries
- Searching enquiries
- Filtering enquiries
- Updating enquiries
- Assignment
- Status management
- Priority management
- Read / unread management
- Follow-up management
- Resolution
- Closure
- Reopening
- Archiving
- Unarchiving
- Deleting
- Bulk actions
- Dashboard statistics
"""

from datetime import datetime

from extensions import db
from app.models import Contact

# =============================================================================
# Constants
# =============================================================================
OPEN_STATUSES = [
    "New",
    "Assigned",
    "In Progress",
    "Waiting for Customer",
]

CLOSED_STATUSES = [
    "Resolved",
    "Closed",
]

VALID_STATUSES = [
    "New",
    "Assigned",
    "In Progress",
    "Waiting for Customer",
    "Resolved",
    "Closed",
]

VALID_PRIORITIES = [
    "Low",
    "Normal",
    "High",
    "Urgent",
]
# =============================================================================
# Contact Service
# =============================================================================
class ContactService:
    """
    Service layer for managing Contact enquiries.
    """
    # =========================================================================
    # Create
    # =========================================================================
    @staticmethod
    def create_contact(
        first_name,
        email,
        subject,
        message,
        last_name=None,
        phone=None,
        company=None,
        country=None,
        user_id=None,
        enquiry_type="General",
        priority="Normal",
        assigned_user_id=None,
        assigned_to=None,
        department=None,
        follow_up_required=True,
        follow_up_date=None,
        newsletter_opt_in=False,
        ip_address=None,
        user_agent=None,
        source="Website",
        is_read=False,
    ):
        """
        Create and persist a new contact enquiry.
        """

        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company=company,
            country=country,
            user_id=user_id,
            subject=subject,
            enquiry_type=enquiry_type,
            message=message,
            status="New",
            priority=priority,
            assigned_user_id=assigned_user_id,
            assigned_to=assigned_to,
            department=department,
            follow_up_required=follow_up_required,
            follow_up_date=follow_up_date,
            newsletter_opt_in=newsletter_opt_in,
            ip_address=ip_address,
            user_agent=user_agent,
            source=source,
            is_read=is_read,
        )

        if is_read:
            contact.read_at = datetime.utcnow()

        if assigned_user_id is not None:
            assigned_user = ContactService._get_user(
                assigned_user_id
            )

            if assigned_user:
                contact.assigned_user = assigned_user
                contact.assigned_to = assigned_user.full_name
                contact.status = "Assigned"

        db.session.add(contact)
        db.session.commit()

        return contact

    # =========================================================================
    # Retrieve
    # =========================================================================
    @staticmethod
    def get_by_id(contact_id):
        """
        Return a contact enquiry by ID.
        """

        return db.session.get(
            Contact,
            contact_id,
        )

    # =========================================================================
    # Get Query
    # =========================================================================
    @staticmethod
    def get_query():
        """
        Return the base Contact query.
        Useful for routes that need additional custom filtering.
        """

        return Contact.query

    # =========================================================================
    # Get All
    # =========================================================================
    @staticmethod
    def get_all(
        status=None,
        priority=None,
        enquiry_type=None,
        department=None,
        assigned_user_id=None,
        assigned_to=None,
        source=None,
        follow_up_required=None,
        is_read=None,
        is_archived=False,
        search_term=None,
        limit=None,
        offset=0,
    ):
        """
        Return contact enquiries using optional filters.
        """

        query = Contact.query

        # ---------------------------------------------------------------------
        # Status
        # ---------------------------------------------------------------------

        if status:
            query = query.filter(
                Contact.status == status
            )

        # ---------------------------------------------------------------------
        # Priority
        # ---------------------------------------------------------------------

        if priority:
            query = query.filter(
                Contact.priority == priority
            )

        # ---------------------------------------------------------------------
        # Enquiry Type
        # ---------------------------------------------------------------------

        if enquiry_type:
            query = query.filter(
                Contact.enquiry_type == enquiry_type
            )

        # ---------------------------------------------------------------------
        # Department
        # ---------------------------------------------------------------------

        if department:
            query = query.filter(
                Contact.department == department
            )

        # ---------------------------------------------------------------------
        # Assignment
        # ---------------------------------------------------------------------

        if assigned_user_id:
            query = query.filter(
                Contact.assigned_user_id == assigned_user_id
            )

        elif assigned_to:
            query = query.filter(
                Contact.assigned_to == assigned_to
            )

        # ---------------------------------------------------------------------
        # Source
        # ---------------------------------------------------------------------
        if source:
            query = query.filter(
                Contact.source == source
            )

        # ---------------------------------------------------------------------
        # Follow-Up
        # ---------------------------------------------------------------------
        if follow_up_required is not None:
            query = query.filter(
                Contact.follow_up_required == follow_up_required
            )

        # ---------------------------------------------------------------------
        # Read / Unread
        # ---------------------------------------------------------------------
        if is_read is not None:
            query = query.filter(
                Contact.is_read == is_read
            )

        # ---------------------------------------------------------------------
        # Archive
        # ---------------------------------------------------------------------
        if is_archived is not None:
            query = query.filter(
                Contact.is_archived == is_archived
            )

        # ---------------------------------------------------------------------
        # Search
        # ---------------------------------------------------------------------
        if search_term:
            term = f"%{search_term.strip()}%"

            query = query.filter(
                db.or_(
                    Contact.first_name.ilike(term),
                    Contact.last_name.ilike(term),
                    Contact.email.ilike(term),
                    Contact.phone.ilike(term),
                    Contact.company.ilike(term),
                    Contact.subject.ilike(term),
                    Contact.message.ilike(term),
                )
            )

        # ---------------------------------------------------------------------
        # Ordering
        # ---------------------------------------------------------------------

        query = query.order_by(
            Contact.created_at.desc()
        )

        # ---------------------------------------------------------------------
        # Pagination
        # ---------------------------------------------------------------------

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    # =========================================================================
    # Search
    # =========================================================================
    @staticmethod
    def search(
        search_term,
        include_archived=False,
    ):
        """
        Search enquiries by customer details, subject, or message.
        """

        if not search_term:
            return []

        term = f"%{search_term.strip()}%"

        query = Contact.query.filter(
            db.or_(
                Contact.first_name.ilike(term),
                Contact.last_name.ilike(term),
                Contact.email.ilike(term),
                Contact.phone.ilike(term),
                Contact.company.ilike(term),
                Contact.subject.ilike(term),
                Contact.message.ilike(term),
            )
        )

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        return (
            query
            .order_by(Contact.created_at.desc())
            .all()
        )

    # =========================================================================
    # Update
    # =========================================================================
    @staticmethod
    def update_contact(
        contact_id,
        **updates,
    ):
        """
        Update editable contact fields.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "phone",
            "company",
            "country",
            "user_id",
            "subject",
            "enquiry_type",
            "message",
            "status",
            "priority",
            "department",
            "follow_up_required",
            "follow_up_date",
            "resolution_notes",
            "newsletter_opt_in",
            "source",
        }

        for field, value in updates.items():

            if field in allowed_fields:
                setattr(
                    contact,
                    field,
                    value,
                )

        # Assignment is handled separately so that the relationship
        # and backwards-compatible assigned_to field remain synchronized.
        if "assigned_user_id" in updates:
            ContactService._apply_assignment(
                contact,
                updates.get("assigned_user_id"),
            )

        if "assigned_to" in updates:
            contact.assigned_to = updates.get(
                "assigned_to"
            )

        contact.updated_at = datetime.utcnow()
        db.session.commit()
        return contact

    # =========================================================================
    # Status Management
    # =========================================================================
    @staticmethod
    def update_status(
        contact_id,
        status,
        user=None,
        resolution_notes=None,
    ):
        """
        Update the status of an enquiry.

        Handles resolution and closure timestamps automatically.
        """

        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid contact status: {status}"
            )

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        now = datetime.utcnow()

        contact.status = status

        # ---------------------------------------------------------------------
        # New / Active
        # ---------------------------------------------------------------------

        if status in OPEN_STATUSES:
            contact.resolved_at = None
            contact.resolved_by = None
            contact.closed_at = None
            contact.closed_by = None

        # ---------------------------------------------------------------------
        # Resolved
        # ---------------------------------------------------------------------

        elif status == "Resolved":

            if contact.resolved_at is None:
                contact.resolved_at = now

            if user is not None:
                contact.resolved_by = user

            contact.closed_at = None
            contact.closed_by = None

        # ---------------------------------------------------------------------
        # Closed
        # ---------------------------------------------------------------------

        elif status == "Closed":

            if contact.resolved_at is None:
                contact.resolved_at = now

            if user is not None:
                contact.resolved_by = user

            if contact.closed_at is None:
                contact.closed_at = now

            if user is not None:
                contact.closed_by = user

        # ---------------------------------------------------------------------
        # Resolution Notes
        # ---------------------------------------------------------------------

        if resolution_notes is not None:
            contact.resolution_notes = resolution_notes

        contact.updated_at = now

        db.session.commit()

        return contact

    # =========================================================================
    # Assignment
    # =========================================================================
    @staticmethod
    def assign(
        contact_id,
        assigned_user_id=None,
        assigned_to=None,
        department=None,
    ):
        """
        Assign an enquiry to an internal user.
        New code should use assigned_user_id.
        assigned_to remains supported for backwards compatibility.
        """
        contact = ContactService.get_by_id(contact_id)
        if not contact:
            return None

        if assigned_user_id is not None:
            user = ContactService._get_user(assigned_user_id)

            if not user:
                raise ValueError("Assigned user does not exist.")

            ContactService._apply_assignment(
                contact,
                assigned_user_id,)

        elif assigned_to is not None:
            contact.assigned_to = assigned_to

        else:
            contact.assigned_user = None
            contact.assigned_user_id = None
            contact.assigned_to = None

        if department is not None:
            contact.department = department

        if contact.status == "New":
            contact.status = "Assigned"

        contact.updated_at = datetime.utcnow()
        db.session.commit()
        return contact

    # =========================================================================
    # Unassign
    # =========================================================================
    @staticmethod
    def unassign(contact_id):
        """
        Remove the current assignment.
        """
        contact = ContactService.get_by_id(contact_id)
        if not contact:
            return None

        contact.assigned_user = None
        contact.assigned_user_id = None
        contact.assigned_to = None

        if contact.status == "Assigned":
            contact.status = "New"

        contact.updated_at = datetime.utcnow()
        db.session.commit()
        return contact

    # =========================================================================
    # Priority
    # =========================================================================

    @staticmethod
    def set_priority(
        contact_id,
        priority,
    ):
        """
        Update enquiry priority.
        """

        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid contact priority: {priority}"
            )

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.priority = priority
        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Read / Unread
    # =========================================================================

    @staticmethod
    def mark_as_read(contact_id):
        """
        Mark an enquiry as read.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.mark_as_read()
        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    @staticmethod
    def mark_as_unread(contact_id):
        """
        Mark an enquiry as unread.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.mark_as_unread()
        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Follow-Up
    # =========================================================================

    @staticmethod
    def schedule_follow_up(
        contact_id,
        follow_up_date,
    ):
        """
        Schedule a follow-up for an enquiry.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.follow_up_required = True
        contact.follow_up_date = follow_up_date
        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Cancel Follow-Up
    # =========================================================================
    @staticmethod
    def cancel_follow_up(contact_id):
        """
        Remove a scheduled follow-up.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.follow_up_required = False
        contact.follow_up_date = None
        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Resolve
    # =========================================================================

    @staticmethod
    def resolve(
        contact_id,
        resolution_notes=None,
        user=None,
    ):
        """
        Resolve an enquiry.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        now = datetime.utcnow()

        contact.status = "Resolved"

        if contact.resolved_at is None:
            contact.resolved_at = now

        if user is not None:
            contact.resolved_by = user

        if resolution_notes is not None:
            contact.resolution_notes = (
                resolution_notes
            )

        contact.follow_up_required = False
        contact.follow_up_date = None
        contact.closed_at = None
        contact.closed_by = None
        contact.updated_at = now

        db.session.commit()

        return contact

    # =========================================================================
    # Close
    # =========================================================================

    @staticmethod
    def close(
        contact_id,
        resolution_notes=None,
        user=None,
    ):
        """
        Close an enquiry.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        now = datetime.utcnow()

        contact.status = "Closed"

        if contact.resolved_at is None:
            contact.resolved_at = now

        if user is not None:
            contact.resolved_by = user

        if contact.closed_at is None:
            contact.closed_at = now

        if user is not None:
            contact.closed_by = user

        if resolution_notes is not None:
            contact.resolution_notes = (
                resolution_notes
            )

        contact.follow_up_required = False
        contact.follow_up_date = None
        contact.updated_at = now

        db.session.commit()

        return contact

    # =========================================================================
    # Reopen
    # =========================================================================

    @staticmethod
    def reopen(contact_id):
        """
        Reopen a resolved or closed enquiry.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.reopen()

        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Archive
    # =========================================================================
    @staticmethod
    def archive(
        contact_id,
        user=None,
    ):
        """
        Archive an enquiry.
        """

        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None

        contact.archive(
            user=user
        )

        contact.updated_at = datetime.utcnow()

        db.session.commit()

        return contact

    # =========================================================================
    # Unarchive
    # =========================================================================
    @staticmethod
    def unarchive(contact_id):
        """
        Restore an enquiry from the archive.
        """
        contact = ContactService.get_by_id(
            contact_id
        )

        if not contact:
            return None
        contact.unarchive()
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        return contact

    # =========================================================================
    # Delete
    # =========================================================================
    @staticmethod
    def delete(contact_id):
        """
        Permanently delete an enquiry.
        Normally the UI should prefer archive() over delete().
        """
        contact = ContactService.get_by_id(contact_id)
        if not contact:
            return False

        db.session.delete(contact)
        db.session.commit()
        return True

    # =========================================================================
    # Counts
    # =========================================================================
    @staticmethod
    def count(
        status=None,
        priority=None,
        enquiry_type=None,
        is_archived=False,
    ):
        """
        Count enquiries using optional filters.
        """

        query = Contact.query

        if status:
            query = query.filter(
                Contact.status == status
            )

        if priority:
            query = query.filter(
                Contact.priority == priority
            )

        if enquiry_type:
            query = query.filter(
                Contact.enquiry_type == enquiry_type
            )

        if is_archived is not None:
            query = query.filter(
                Contact.is_archived == is_archived
            )

        return query.count()

    # =========================================================================
    # Open Enquiries
    # =========================================================================
    @staticmethod
    def get_open(
        include_archived=False,
    ):
        """
        Return all currently open enquiries.
        """

        query = Contact.query.filter(
            Contact.status.notin_(CLOSED_STATUSES)
        )

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        return (
            query
            .order_by(Contact.created_at.desc())
            .all()
        )

    # =========================================================================
    # New Enquiries
    # =========================================================================
    @staticmethod
    def get_new():
        """
        Return new enquiries.
        """

        return (
            Contact.query
            .filter(
                Contact.status == "New",
                Contact.is_archived.is_(False),
            )
            .order_by(Contact.created_at.desc())
            .all()
        )

    # =========================================================================
    # Unread Enquiries
    # =========================================================================
    @staticmethod
    def get_unread():
        """
        Return unread enquiries.
        """

        return (
            Contact.query
            .filter(
                Contact.is_read.is_(False),
                Contact.is_archived.is_(False),
            )
            .order_by(Contact.created_at.desc())
            .all()
        )

    # =========================================================================
    # Urgent Enquiries
    # =========================================================================
    @staticmethod
    def get_urgent():
        """
        Return high and urgent enquiries that are still open.
        """

        return (
            Contact.query
            .filter(
                Contact.priority.in_(
                    ["High", "Urgent"]
                ),
                Contact.status.notin_(
                    CLOSED_STATUSES
                ),
                Contact.is_archived.is_(False),
            )
            .order_by(
                Contact.priority.desc(),
                Contact.created_at.desc(),
            )
            .all()
        )

    # =========================================================================
    # Follow-Ups Due
    # =========================================================================
    @staticmethod
    def get_follow_ups_due():
        """
        Return enquiries whose follow-up date is due.
        """
        now = datetime.utcnow()
        return (
            Contact.query
            .filter(
                Contact.follow_up_required.is_(True),
                Contact.follow_up_date.isnot(None),
                Contact.follow_up_date <= now,
                Contact.status.notin_(
                    CLOSED_STATUSES
                ),
                Contact.is_archived.is_(False),
            )
            .order_by(
                Contact.follow_up_date.asc()
            )
            .all()
        )

    # =========================================================================
    # Upcoming Follow-Ups
    # =========================================================================
    @staticmethod
    def get_upcoming_follow_ups(
        days=7,
    ):
        """
        Return follow-ups scheduled within the next number of days.
        """

        now = datetime.utcnow()

        from datetime import timedelta

        end_date = now + timedelta(
            days=days
        )

        return (
            Contact.query
            .filter(
                Contact.follow_up_required.is_(True),
                Contact.follow_up_date.isnot(None),
                Contact.follow_up_date >= now,
                Contact.follow_up_date <= end_date,
                Contact.status.notin_(
                    CLOSED_STATUSES
                ),
                Contact.is_archived.is_(False),
            )
            .order_by(
                Contact.follow_up_date.asc()
            )
            .all()
        )

    # =========================================================================
    # Assigned Contacts
    # =========================================================================

    @staticmethod
    def get_assigned_to(
        user_id,
        include_closed=False,
    ):
        """
        Return enquiries assigned to a particular internal user.
        """

        query = Contact.query.filter(
            Contact.assigned_user_id == user_id
        )

        if not include_closed:
            query = query.filter(
                Contact.status.notin_(
                    CLOSED_STATUSES
                )
            )

        query = query.filter(
            Contact.is_archived.is_(False)
        )

        return (
            query
            .order_by(Contact.created_at.desc())
            .all()
        )

    # =========================================================================
    # Statistics
    # =========================================================================
    @staticmethod
    def get_statistics():
        """
        Return CRM/contact statistics.
        """

        active_filter = Contact.is_archived.is_(False)

        total = Contact.query.filter(
            active_filter
        ).count()

        new = Contact.query.filter(
            active_filter,
            Contact.status == "New",
        ).count()

        assigned = Contact.query.filter(
            active_filter,
            Contact.status == "Assigned",
        ).count()

        in_progress = Contact.query.filter(
            active_filter,
            Contact.status == "In Progress",
        ).count()

        waiting = Contact.query.filter(
            active_filter,
            Contact.status == "Waiting for Customer",
        ).count()

        open_count = Contact.query.filter(
            active_filter,
            Contact.status.in_(OPEN_STATUSES),
        ).count()

        resolved = Contact.query.filter(
            active_filter,
            Contact.status == "Resolved",
        ).count()

        closed = Contact.query.filter(
            active_filter,
            Contact.status == "Closed",
        ).count()

        unread = Contact.query.filter(
            active_filter,
            Contact.is_read.is_(False),
        ).count()

        urgent = Contact.query.filter(
            active_filter,
            Contact.priority == "Urgent",
            Contact.status.notin_(CLOSED_STATUSES),
        ).count()

        high_priority = Contact.query.filter(
            active_filter,
            Contact.priority == "High",
            Contact.status.notin_(CLOSED_STATUSES),
        ).count()

        follow_ups = Contact.query.filter(
            active_filter,
            Contact.follow_up_required.is_(True),
        ).count()

        follow_ups_due = ContactService._count_follow_ups_due()

        archived = Contact.query.filter(
            Contact.is_archived.is_(True)
        ).count()

        return {
            "total": total,
            "open": open_count,
            "new": new,
            "assigned": assigned,
            "in_progress": in_progress,
            "waiting_for_customer": waiting,
            "resolved": resolved,
            "closed": closed,
            "unread": unread,
            "urgent": urgent,
            "high_priority": high_priority,
            "follow_ups": follow_ups,
            "follow_ups_due": follow_ups_due,
            "archived": archived,
        }

    # =========================================================================
    # Status Counts
    # =========================================================================
    @staticmethod
    def get_status_counts(
        include_archived=False,
    ):
        """
        Return enquiry counts grouped by status.
        """

        query = Contact.query

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        return {
            status: query.filter(
                Contact.status == status
            ).count()
            for status in VALID_STATUSES
        }

    # =========================================================================
    # Priority Counts
    # =========================================================================

    @staticmethod
    def get_priority_counts(
        include_archived=False,
    ):
        """
        Return enquiry counts grouped by priority.
        """

        query = Contact.query

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        return {
            priority: query.filter(
                Contact.priority == priority
            ).count()
            for priority in VALID_PRIORITIES
        }

    # =========================================================================
    # Enquiry Type Counts
    # =========================================================================
    @staticmethod
    def get_enquiry_type_counts(
        include_archived=False,
    ):
        """
        Return enquiry counts grouped by enquiry type.
        """

        query = Contact.query

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        contacts = query.all()

        counts = {}

        for contact in contacts:
            enquiry_type = (
                contact.enquiry_type
                or "General"
            )

            counts[enquiry_type] = (
                counts.get(
                    enquiry_type,
                    0,
                )
                + 1
            )

        return dict(
            sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    # =========================================================================
    # Source Counts
    # =========================================================================
    @staticmethod
    def get_source_counts(
        include_archived=False,
    ):
        """
        Return enquiry counts grouped by source.
        """

        query = Contact.query

        if not include_archived:
            query = query.filter(
                Contact.is_archived.is_(False)
            )

        contacts = query.all()

        counts = {}

        for contact in contacts:
            source = (
                contact.source
                or "Unknown"
            )

            counts[source] = (
                counts.get(
                    source,
                    0,
                )
                + 1
            )

        return dict(
            sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    # =========================================================================
    # Bulk Mark Read
    # =========================================================================
    @staticmethod
    def mark_many_as_read(contact_ids):
        """
        Mark multiple enquiries as read.
        """

        if not contact_ids:
            return 0

        contacts = Contact.query.filter(
            Contact.id.in_(contact_ids)
        ).all()

        now = datetime.utcnow()

        for contact in contacts:
            contact.is_read = True

            if contact.read_at is None:
                contact.read_at = now

            contact.updated_at = now

        db.session.commit()

        return len(contacts)

    # =========================================================================
    # Bulk Mark Unread
    # =========================================================================
    @staticmethod
    def mark_many_as_unread(contact_ids):
        """
        Mark multiple enquiries as unread.
        """
        if not contact_ids:
            return 0
        contacts = Contact.query.filter(
            Contact.id.in_(contact_ids)
        ).all()
        now = datetime.utcnow()
        for contact in contacts:
            contact.is_read = False
            contact.read_at = None
            contact.updated_at = now

        db.session.commit()

        return len(contacts)

    # =========================================================================
    # Bulk Archive
    # =========================================================================

    @staticmethod
    def archive_many(
        contact_ids,
        user=None,
    ):
        """
        Archive multiple enquiries.
        """

        if not contact_ids:
            return 0

        contacts = Contact.query.filter(
            Contact.id.in_(contact_ids)
        ).all()

        now = datetime.utcnow()

        for contact in contacts:
            contact.is_archived = True

            if contact.archived_at is None:
                contact.archived_at = now

            if user is not None:
                contact.archived_by = user

            contact.updated_at = now

        db.session.commit()

        return len(contacts)

    # =========================================================================
    # Bulk Status
    # =========================================================================
    @staticmethod
    def update_many_status(
        contact_ids,
        status,
        user=None,
    ):
        """
        Update the status of multiple enquiries.
        """

        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid contact status: {status}"
            )

        if not contact_ids:
            return 0

        contacts = Contact.query.filter(
            Contact.id.in_(contact_ids)
        ).all()

        now = datetime.utcnow()

        for contact in contacts:

            contact.status = status

            if status in OPEN_STATUSES:

                contact.resolved_at = None
                contact.resolved_by = None
                contact.closed_at = None
                contact.closed_by = None

            elif status == "Resolved":

                if contact.resolved_at is None:
                    contact.resolved_at = now

                if user is not None:
                    contact.resolved_by = user

                contact.closed_at = None
                contact.closed_by = None

            elif status == "Closed":

                if contact.resolved_at is None:
                    contact.resolved_at = now

                if user is not None:
                    contact.resolved_by = user

                if contact.closed_at is None:
                    contact.closed_at = now

                if user is not None:
                    contact.closed_by = user

            contact.updated_at = now

        db.session.commit()

        return len(contacts)

    # =========================================================================
    # Bulk Priority
    # =========================================================================
    @staticmethod
    def update_many_priority(
        contact_ids,
        priority,
    ):
        """
        Update the priority of multiple enquiries.
        """

        if priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid contact priority: {priority}"
            )

        if not contact_ids:
            return 0

        contacts = Contact.query.filter(
            Contact.id.in_(contact_ids)
        ).all()

        now = datetime.utcnow()

        for contact in contacts:
            contact.priority = priority
            contact.updated_at = now

        db.session.commit()

        return len(contacts)

    # =========================================================================
    # Archived Contacts
    # =========================================================================

    @staticmethod
    def get_archived():
        """
        Return archived enquiries.
        """

        return (
            Contact.query
            .filter(
                Contact.is_archived.is_(True)
            )
            .order_by(
                Contact.archived_at.desc(),
                Contact.created_at.desc(),
            )
            .all()
        )

    # =========================================================================
    # Internal Helpers
    # =========================================================================
    @staticmethod
    def _get_user(user_id):
        """Retrieve an eligible internal user for contact assignment."""
        if not user_id:
            return None

        from app.models import User

        user = db.session.get(User, user_id)

        if (
                user is None
                or not user.is_active
                or not user.is_internal_user
        ):
            return None

        return user

    @staticmethod
    def _apply_assignment(contact, assigned_user_id):
        """Synchronize the assignment relationship and legacy name field."""
        if not assigned_user_id:
            contact.assigned_user = None
            contact.assigned_user_id = None
            contact.assigned_to = None
            return

        user = ContactService._get_user(assigned_user_id)

        if user is None:
            raise ValueError(
                "Only active administrators, staff members, and guides "
                "can be assigned to enquiries."
            )

        contact.assigned_user = user
        contact.assigned_user_id = user.id
        contact.assigned_to = user.full_name

    @staticmethod
    def _count_follow_ups_due():
        """
        Return the number of currently due follow-ups.
        """

        now = datetime.utcnow()

        return Contact.query.filter(
            Contact.follow_up_required.is_(True),
            Contact.follow_up_date.isnot(None),
            Contact.follow_up_date <= now,
            Contact.status.notin_(CLOSED_STATUSES),
            Contact.is_archived.is_(False),
        ).count()


# =============================================================================
# Convenience Functions
# =============================================================================
def create_contact(**kwargs):
    """
    Convenience wrapper for creating a contact.
    """
    return ContactService.create_contact(
        **kwargs)

def get_contact(contact_id):
    """
    Convenience wrapper for retrieving a contact.
    """
    return ContactService.get_by_id(contact_id)

def get_contacts(**kwargs):
    """
    Convenience wrapper for retrieving contacts.
    """
    return ContactService.get_all(
        **kwargs)

def search_contacts(
    search_term,
    include_archived=False,
):
    """
    Convenience wrapper for searching contacts.
    """
    return ContactService.search(
        search_term,
        include_archived=include_archived,
    )


def update_contact(
    contact_id,
    **updates,
):
    """
    Convenience wrapper for updating a contact.
    """
    return ContactService.update_contact(
        contact_id,
        **updates
    )

def assign_contact(
    contact_id,
    assigned_user_id=None,
    assigned_to=None,
    department=None,):
    """
    Convenience wrapper for assigning a contact.
    """
    return ContactService.assign(
        contact_id,
        assigned_user_id=assigned_user_id,
        assigned_to=assigned_to,
        department=department,)

def mark_contact_read(contact_id):
    """
    Convenience wrapper for marking a contact as read.
    """
    return ContactService.mark_as_read(contact_id)

def mark_contact_unread(contact_id):
    """
    Convenience wrapper for marking a contact as unread.
    """
    return ContactService.mark_as_unread(contact_id)

def resolve_contact(
    contact_id,
    resolution_notes=None,
    user=None,):
    """
    Convenience wrapper for resolving a contact.
    """
    return ContactService.resolve(
        contact_id,
        resolution_notes=resolution_notes,
        user=user,)

def close_contact(
    contact_id,
    resolution_notes=None,
    user=None,):
    """
    Convenience wrapper for closing a contact.
    """
    return ContactService.close(
        contact_id,
        resolution_notes=resolution_notes,
        user=user,)

def reopen_contact(contact_id):
    """
    Convenience wrapper for reopening a contact.
    """
    return ContactService.reopen(
        contact_id)

def archive_contact(
    contact_id,
    user=None,
):
    """
    Convenience wrapper for archiving a contact.
    """
    return ContactService.archive(
        contact_id,
        user=user,)

def unarchive_contact(contact_id):
    """
    Convenience wrapper for restoring an archived contact.
    """
    return ContactService.unarchive(contact_id)