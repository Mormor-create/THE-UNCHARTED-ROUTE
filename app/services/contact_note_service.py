"""
===============================================================================
The Uncharted Route
Contact Note Service
===============================================================================

Service layer for managing internal notes attached to Contact enquiries.

Responsibilities:
    - Create internal contact notes
    - Retrieve individual notes
    - Retrieve notes belonging to a contact
    - Search and filter notes
    - Track note authors
    - Manage note types
    - Mark/unmark notes as important
    - Update notes
    - Delete notes
    - Provide note statistics

Contact notes are strictly internal and must never be included in
customer-facing communication.
"""

from datetime import datetime

from extensions import db
from app.models import Contact, ContactNote


# =============================================================================
# Constants
# =============================================================================

NOTE_TYPE_GENERAL = "General"
NOTE_TYPE_FOLLOW_UP = "Follow Up"
NOTE_TYPE_CUSTOMER = "Customer"
NOTE_TYPE_OPERATIONS = "Operations"
NOTE_TYPE_BOOKING = "Booking"
NOTE_TYPE_SALES = "Sales"
NOTE_TYPE_MANAGEMENT = "Management"
NOTE_TYPE_ESCALATION = "Escalation"
NOTE_TYPE_RESOLUTION = "Resolution"

NOTE_TYPES = {
    NOTE_TYPE_GENERAL,
    NOTE_TYPE_FOLLOW_UP,
    NOTE_TYPE_CUSTOMER,
    NOTE_TYPE_OPERATIONS,
    NOTE_TYPE_BOOKING,
    NOTE_TYPE_SALES,
    NOTE_TYPE_MANAGEMENT,
    NOTE_TYPE_ESCALATION,
    NOTE_TYPE_RESOLUTION,
}


# =============================================================================
# Contact Note Service
# =============================================================================

class ContactNoteService:
    """
    Service class for managing ContactNote records.
    """

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_note_type(note_type):
        """
        Validate a contact note type.
        """

        if note_type not in NOTE_TYPES:
            raise ValueError(
                f"Invalid note type: {note_type}. "
                f"Expected one of: {', '.join(sorted(NOTE_TYPES))}."
            )

    # =========================================================================
    # Create
    # =========================================================================

    @staticmethod
    def create_note(
        contact_id,
        note,
        user_id=None,
        author_name=None,
        note_type=NOTE_TYPE_GENERAL,
        is_important=False,
        commit=True,
    ):
        """
        Create an internal note for a Contact enquiry.

        Parameters
        ----------
        contact_id:
            ID of the Contact the note belongs to.

        note:
            Internal note content.

        user_id:
            Optional ID of the staff/admin user creating the note.

        author_name:
            Fallback author name retained on the note.

        note_type:
            Classification of the note.

        is_important:
            Whether the note should be flagged as important.

        commit:
            Whether to commit immediately.
        """

        if not contact_id:
            raise ValueError("contact_id is required.")

        if not note or not str(note).strip():
            raise ValueError("Note content cannot be empty.")

        ContactNoteService._validate_note_type(note_type)

        contact = Contact.query.get(contact_id)

        if contact is None:
            raise ValueError(
                f"Contact with ID {contact_id} was not found."
            )

        contact_note = ContactNote(
            contact_id=contact.id,
            user_id=user_id,
            author_name=author_name,
            note=str(note).strip(),
            note_type=note_type,
            is_important=bool(is_important),
        )

        db.session.add(contact_note)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Retrieval
    # =========================================================================

    @staticmethod
    def get_by_id(note_id):
        """
        Retrieve a ContactNote by ID.
        """

        if not note_id:
            return None

        return ContactNote.query.get(note_id)

    @staticmethod
    def get_note(note_id):
        """
        Alias for get_by_id().
        """

        return ContactNoteService.get_by_id(note_id)

    @staticmethod
    def get_by_contact(
        contact_id,
        note_type=None,
        important_only=False,
        user_id=None,
        limit=None,
        offset=0,
        newest_first=True,
    ):
        """
        Retrieve notes belonging to a specific Contact.
        """

        if not contact_id:
            return []

        query = ContactNote.query.filter(
            ContactNote.contact_id == contact_id
        )

        if note_type:
            ContactNoteService._validate_note_type(note_type)

            query = query.filter(
                ContactNote.note_type == note_type
            )

        if important_only:
            query = query.filter(
                ContactNote.is_important.is_(True)
            )

        if user_id is not None:
            query = query.filter(
                ContactNote.user_id == user_id
            )

        if newest_first:
            query = query.order_by(
                ContactNote.created_at.desc(),
                ContactNote.id.desc(),
            )
        else:
            query = query.order_by(
                ContactNote.created_at.asc(),
                ContactNote.id.asc(),
            )

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_contact_history(contact_id):
        """
        Return the complete internal note history for a Contact.
        """

        return ContactNoteService.get_by_contact(
            contact_id=contact_id,
            newest_first=False,
        )

    # =========================================================================
    # Retrieval by Type
    # =========================================================================

    @staticmethod
    def get_by_type(
        note_type,
        limit=None,
        offset=0,
    ):
        """
        Retrieve notes belonging to a specific note type.
        """

        ContactNoteService._validate_note_type(note_type)

        query = ContactNote.query.filter(
            ContactNote.note_type == note_type
        ).order_by(
            ContactNote.created_at.desc(),
            ContactNote.id.desc(),
        )

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_important(
        limit=None,
        offset=0,
    ):
        """
        Retrieve all important contact notes.
        """

        query = ContactNote.query.filter(
            ContactNote.is_important.is_(True)
        ).order_by(
            ContactNote.created_at.desc(),
            ContactNote.id.desc(),
        )

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_follow_up_notes(
        limit=None,
        offset=0,
    ):
        """
        Retrieve notes classified as Follow Up.
        """

        return ContactNoteService.get_by_type(
            NOTE_TYPE_FOLLOW_UP,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_resolution_notes(
        limit=None,
        offset=0,
    ):
        """
        Retrieve notes classified as Resolution.
        """

        return ContactNoteService.get_by_type(
            NOTE_TYPE_RESOLUTION,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get_escalation_notes(
        limit=None,
        offset=0,
    ):
        """
        Retrieve notes classified as Escalation.
        """

        return ContactNoteService.get_by_type(
            NOTE_TYPE_ESCALATION,
            limit=limit,
            offset=offset,
        )

    # =========================================================================
    # Query / Filtering
    # =========================================================================

    @staticmethod
    def get_all(
        contact_id=None,
        user_id=None,
        note_type=None,
        important_only=False,
        date_from=None,
        date_to=None,
        limit=None,
        offset=0,
        newest_first=True,
    ):
        """
        Retrieve ContactNote records using optional filters.
        """

        query = ContactNote.query

        if contact_id is not None:
            query = query.filter(
                ContactNote.contact_id == contact_id
            )

        if user_id is not None:
            query = query.filter(
                ContactNote.user_id == user_id
            )

        if note_type:
            ContactNoteService._validate_note_type(note_type)

            query = query.filter(
                ContactNote.note_type == note_type
            )

        if important_only:
            query = query.filter(
                ContactNote.is_important.is_(True)
            )

        if date_from:
            query = query.filter(
                ContactNote.created_at >= date_from
            )

        if date_to:
            query = query.filter(
                ContactNote.created_at <= date_to
            )

        if newest_first:
            query = query.order_by(
                ContactNote.created_at.desc(),
                ContactNote.id.desc(),
            )
        else:
            query = query.order_by(
                ContactNote.created_at.asc(),
                ContactNote.id.asc(),
            )

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
        contact_id=None,
        note_type=None,
        limit=None,
        offset=0,
    ):
        """
        Search internal notes.

        Searches note content and stored author name.
        """

        if not search_term or not search_term.strip():
            return []

        ContactNoteService._validate_note_type(
            note_type
        ) if note_type else None

        term = f"%{search_term.strip()}%"

        query = ContactNote.query.filter(
            db.or_(
                ContactNote.note.ilike(term),
                ContactNote.author_name.ilike(term),
            )
        )

        if contact_id is not None:
            query = query.filter(
                ContactNote.contact_id == contact_id
            )

        if note_type:
            query = query.filter(
                ContactNote.note_type == note_type
            )

        query = query.order_by(
            ContactNote.created_at.desc(),
            ContactNote.id.desc(),
        )

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    # =========================================================================
    # Update
    # =========================================================================

    @staticmethod
    def update_note(
        note_id,
        commit=True,
        **updates,
    ):
        """
        Update editable fields on a ContactNote.

        Allowed fields:
            note
            author_name
            note_type
            is_important
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        allowed_fields = {
            "note",
            "author_name",
            "note_type",
            "is_important",
        }

        for field, value in updates.items():

            if field not in allowed_fields:
                continue

            if field == "note":
                if not value or not str(value).strip():
                    raise ValueError(
                        "Note content cannot be empty."
                    )

                value = str(value).strip()

            if field == "note_type":
                ContactNoteService._validate_note_type(
                    value
                )

            if field == "is_important":
                value = bool(value)

            setattr(
                contact_note,
                field,
                value,
            )

        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Important Flag
    # =========================================================================

    @staticmethod
    def mark_important(
        note_id,
        commit=True,
    ):
        """
        Mark a note as important.
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        contact_note.mark_important()
        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def mark_not_important(
        note_id,
        commit=True,
    ):
        """
        Remove the important flag from a note.
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        contact_note.mark_not_important()
        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def toggle_important(
        note_id,
        commit=True,
    ):
        """
        Toggle the important flag on a note.
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        contact_note.toggle_important()
        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Note Type
    # =========================================================================

    @staticmethod
    def change_type(
        note_id,
        note_type,
        commit=True,
    ):
        """
        Change the classification of an existing note.
        """

        ContactNoteService._validate_note_type(
            note_type
        )

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        contact_note.note_type = note_type
        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Author
    # =========================================================================

    @staticmethod
    def assign_author(
        note_id,
        user_id,
        author_name=None,
        commit=True,
    ):
        """
        Associate an existing note with a staff/admin user.

        author_name is retained as a fallback display value.
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return None

        contact_note.user_id = user_id

        if author_name is not None:
            contact_note.author_name = author_name

        contact_note.updated_at = datetime.utcnow()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()

            return contact_note

        except Exception:
            db.session.rollback()
            raise

    # =========================================================================
    # Counts
    # =========================================================================

    @staticmethod
    def count(
        contact_id=None,
        user_id=None,
        note_type=None,
        important_only=False,
    ):
        """
        Count notes matching the supplied filters.
        """

        query = ContactNote.query

        if contact_id is not None:
            query = query.filter(
                ContactNote.contact_id == contact_id
            )

        if user_id is not None:
            query = query.filter(
                ContactNote.user_id == user_id
            )

        if note_type:
            ContactNoteService._validate_note_type(
                note_type
            )

            query = query.filter(
                ContactNote.note_type == note_type
            )

        if important_only:
            query = query.filter(
                ContactNote.is_important.is_(True)
            )

        return query.count()

    # =========================================================================
    # Contact Summary
    # =========================================================================

    @staticmethod
    def get_contact_summary(contact_id):
        """
        Return a summary of internal notes attached to a Contact.
        """

        contact = Contact.query.get(contact_id)

        if contact is None:
            return None

        total = ContactNoteService.count(
            contact_id=contact_id
        )

        important = ContactNoteService.count(
            contact_id=contact_id,
            important_only=True,
        )

        follow_up = ContactNoteService.count(
            contact_id=contact_id,
            note_type=NOTE_TYPE_FOLLOW_UP,
        )

        resolution = ContactNoteService.count(
            contact_id=contact_id,
            note_type=NOTE_TYPE_RESOLUTION,
        )

        escalation = ContactNoteService.count(
            contact_id=contact_id,
            note_type=NOTE_TYPE_ESCALATION,
        )

        latest_note = ContactNote.query.filter(
            ContactNote.contact_id == contact_id
        ).order_by(
            ContactNote.created_at.desc(),
            ContactNote.id.desc(),
        ).first()

        return {
            "contact_id": contact_id,
            "total_notes": total,
            "important_notes": important,
            "follow_up_notes": follow_up,
            "resolution_notes": resolution,
            "escalation_notes": escalation,
            "latest_note": latest_note,
            "latest_note_at": (
                latest_note.created_at
                if latest_note
                else None
            ),
        }

    # =========================================================================
    # Statistics
    # =========================================================================

    @staticmethod
    def get_statistics():
        """
        Return overall ContactNote statistics.
        """

        total = ContactNoteService.count()

        important = ContactNoteService.count(
            important_only=True
        )

        statistics = {
            "total": total,
            "important": important,
        }

        for note_type in sorted(NOTE_TYPES):
            statistics[
                note_type.lower().replace(" ", "_")
            ] = ContactNoteService.count(
                note_type=note_type
            )

        return statistics

    # =========================================================================
    # Delete
    # =========================================================================

    @staticmethod
    def delete_note(note_id):
        """
        Permanently delete a ContactNote.
        """

        contact_note = ContactNoteService.get_by_id(
            note_id
        )

        if contact_note is None:
            return False

        try:
            db.session.delete(contact_note)
            db.session.commit()

            return True

        except Exception:
            db.session.rollback()
            raise


# =============================================================================
# Convenience Functions
# =============================================================================

def create_contact_note(**kwargs):
    """
    Convenience wrapper for ContactNoteService.create_note().
    """

    return ContactNoteService.create_note(**kwargs)


def get_contact_note(note_id):
    """
    Convenience wrapper for ContactNoteService.get_by_id().
    """

    return ContactNoteService.get_by_id(note_id)


def get_contact_notes(contact_id, **kwargs):
    """
    Convenience wrapper for retrieving a Contact's notes.
    """

    return ContactNoteService.get_by_contact(
        contact_id=contact_id,
        **kwargs,
    )


def search_contact_notes(search_term, **kwargs):
    """
    Convenience wrapper for searching contact notes.
    """

    return ContactNoteService.search(
        search_term,
        **kwargs,
    )


def mark_contact_note_important(note_id, **kwargs):
    """
    Convenience wrapper for marking a note important.
    """

    return ContactNoteService.mark_important(
        note_id,
        **kwargs,
    )


def mark_contact_note_not_important(note_id, **kwargs):
    """
    Convenience wrapper for removing the important flag.
    """

    return ContactNoteService.mark_not_important(
        note_id,
        **kwargs,
    )


def toggle_contact_note_important(note_id, **kwargs):
    """
    Convenience wrapper for toggling the important flag.
    """

    return ContactNoteService.toggle_important(
        note_id,
        **kwargs,
    )


def delete_contact_note(note_id):
    """
    Convenience wrapper for deleting a note.
    """

    return ContactNoteService.delete_note(note_id)