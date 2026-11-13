"""
===============================================================================
The Uncharted Route
Contact / Enquiry Administration Blueprint
===============================================================================

Administrative management of customer enquiries.

This blueprint handles:

    • Enquiry inbox
    • Search and filtering
    • Enquiry details
    • Creating enquiries
    • Editing enquiries
    • Assignment
    • Status
    • Priority
    • Follow-ups
    • Replies
    • Internal notes
    • Resolution
    • Read / unread state
    • Archive / restore
    • Statistics
    • Bulk actions
    • Deletion
    • Quick close / reopen

The blueprint deliberately keeps list retrieval independent of the
ContactService.get_all() signature so that pagination/filtering here does not
depend on unsupported service arguments.
"""

from datetime import datetime
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for, current_app,)
from flask_login import current_user, login_required
from sqlalchemy import or_
from app.decorators.admin import admin_required
from app.forms.contact import (
    ContactArchiveForm,
    ContactAssignmentForm,
    ContactBulkActionForm,
    ContactCreateForm,
    ContactEditForm,
    ContactFilterForm,
    ContactFollowUpForm,
    ContactNoteForm,
    ContactPriorityForm,
    ContactReadStatusForm,
    ContactReplyForm,
    ContactResolutionForm,
    ContactRestoreForm,
    ContactStatusForm,)
from app.models import Contact, User
from app.services.contact_note_service import ContactNoteService
from app.services.contact_reply_service import ContactReplyService
from app.services.contact_service import ContactService
from extensions import db

# =============================================================================
# Blueprint
# =============================================================================
contacts_bp = Blueprint(
    "contacts",
    __name__,
    url_prefix="/admin/contacts",)

# =============================================================================
# Helper Functions
# =============================================================================

# =============================================================================
# Contact Assignment Helpers
# =============================================================================
def _get_assignable_users():
    """Return active internal users eligible for contact assignment."""
    eligible_roles = ("admin", "staff", "guide")

    users = (
        User.query
        .filter(User.is_active.is_(True))
        .order_by(User.first_name.asc(), User.last_name.asc())
        .all()
    )

    # Use normalized_role so capitalization and surrounding whitespace
    # do not accidentally exclude valid internal users.
    return [
        (
            user.id,
            f"{user.full_name} — {user.normalized_role.title()}",
        )
        for user in users
        if user.normalized_role in eligible_roles
    ]


def _populate_assignment_choices(form):
    """Populate the assignment dropdown with eligible internal users."""
    if hasattr(form, "assigned_user_id"):
        form.assigned_user_id.choices = [
            (0, "Unassigned"),
            *_get_assignable_users(),
        ]


def _get_user_by_id(user_id):
    """Return an active internal user by ID, or None if ineligible."""
    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    if user_id <= 0:
        return None

    user = User.query.filter_by(
        id=user_id,
        is_active=True,
    ).first()

    if not user or not user.is_internal_user:
        return None

    return user

def _get_pagination_page():
    """
    Safely parse the requested page number.
    """

    try:
        page = int(
            request.args.get(
                "page",
                1,
            )
        )
    except (TypeError, ValueError):
        page = 1
    return max(page, 1)

def _paginate_list(items, page=1, per_page=25):
    """
    Paginate an ordinary Python list.
    This avoids requiring ContactService.get_all() to support pagination.
    """
    items = items or []
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    total_pages = (
        (total + per_page - 1) // per_page
        if total
        else 0
    )

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < total_pages else None,
    }

def _get_all_contacts():
    """
    Retrieve contacts through ContactService and normalize the result.
    Log retrieval failures instead of silently treating them as no records.
    """
    try:
        result = ContactService.get_all()
        if result is None:
            return []
        if hasattr(result, "all"):
            result = result.all()

        return list(result)

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve contacts for the admin inbox."
        )
        return []

def _contact_value(contact, *names, default=None):
    """
    Return the first available attribute from a Contact object.
    """
    for name in names:
        try:
            value = getattr(contact, name)

            if value is not None:
                return value
        except AttributeError:
            continue
    return default

def _matches_text(contact, search):
    """
    Check whether the search term appears in common contact fields.
    """

    if not search:
        return True

    search = search.lower()

    fields = [
        _contact_value(contact, "first_name", default=""),
        _contact_value(contact, "last_name", default=""),
        _contact_value(contact, "email", default=""),
        _contact_value(contact, "phone", default=""),
        _contact_value(contact, "company", default=""),
        _contact_value(contact, "subject", default=""),
        _contact_value(contact, "message", default=""),
    ]

    combined = " ".join(
        str(value or "")
        for value in fields
    ).lower()
    return search in combined


def _filter_contacts(contacts, filters):
    """
    Apply dashboard filters to a contact collection.

    Supports active, archived, and all archive filter values while
    preserving the existing search and dashboard filters.
    """
    filtered = []

    search = str(filters.get("search") or "").strip().lower()
    status = str(filters.get("status") or "").strip().lower()
    enquiry_type = str(filters.get("enquiry_type") or "").strip().lower()
    priority = str(filters.get("priority") or "").strip().lower()
    department = str(filters.get("department") or "").strip().lower()
    source = str(filters.get("source") or "").strip().lower()

    assigned_user_id = filters.get("assigned_user_id")
    unread_only = bool(filters.get("unread_only"))
    follow_up_only = bool(filters.get("follow_up_only"))
    urgent_only = bool(filters.get("urgent_only"))

    # Handle archive filters correctly.
    # "active" means non-archived; "archived" means archived only;
    # "all" means include both.
    archive_filter = filters.get("archived", "active")

    if isinstance(archive_filter, str):
        archive_filter = archive_filter.strip().lower()

        show_archived_only = archive_filter == "archived"
        show_active_only = archive_filter not in ("archived", "all")
    else:
        # Preserve support for routes that pass True/False.
        show_archived_only = bool(archive_filter)
        show_active_only = not show_archived_only

    for contact in contacts:
        # Search
        if search and not _matches_text(contact, search):
            continue

        # Status
        contact_status = str(
            _contact_value(contact, "status", default="") or ""
        ).strip().lower()

        if status and contact_status != status:
            continue

        # Enquiry type
        contact_type = str(
            _contact_value(
                contact,
                "enquiry_type",
                "type",
                default="",
            ) or ""
        ).strip().lower()

        if enquiry_type and contact_type != enquiry_type:
            continue

        # Priority
        contact_priority = str(
            _contact_value(contact, "priority", default="") or ""
        ).strip().lower()

        if priority and contact_priority != priority:
            continue

        # Department
        contact_department = str(
            _contact_value(contact, "department", default="") or ""
        ).strip().lower()

        if department and contact_department != department:
            continue

        # Source
        contact_source = str(
            _contact_value(contact, "source", default="") or ""
        ).strip().lower()

        if source and contact_source != source:
            continue

        # Assignment
        if assigned_user_id not in (None, "", 0, "0"):
            contact_assigned_id = _contact_value(
                contact,
                "assigned_user_id",
                "assigned_to_id",
                default=None,
            )

            # Support the legacy assigned_to field when it contains an ID.
            if contact_assigned_id is None:
                contact_assigned_id = _contact_value(
                    contact,
                    "assigned_to",
                    default=None,
                )

            try:
                contact_assigned_id = int(contact_assigned_id)
                requested_assigned_id = int(assigned_user_id)
            except (TypeError, ValueError):
                continue

            if contact_assigned_id != requested_assigned_id:
                continue

        # Read / unread
        if unread_only:
            is_read = _contact_value(
                contact,
                "is_read",
                default=True,
            )

            if is_read:
                continue

        # Follow-up
        if follow_up_only:
            follow_up_required = _contact_value(
                contact,
                "follow_up_required",
                default=False,
            )

            if not follow_up_required:
                continue

        # Urgent
        if urgent_only and contact_priority not in ("urgent", "critical"):
            continue

        # Archived
        contact_archived = _contact_value(
            contact,
            "is_archived",
            "archived",
            default=None,
        )

        if contact_archived is None:
            contact_archived = contact_status in ("closed", "archived")

        contact_archived = bool(contact_archived)

        if show_archived_only and not contact_archived:
            continue

        if show_active_only and contact_archived:
            continue

        filtered.append(contact)

    return filtered

def _get_filtered_contacts(filters):
    """
    Retrieve and filter contacts.
    """
    contacts = _get_all_contacts()
    return _filter_contacts(
        contacts,
        filters,)

def _get_statistics():
    """
    Retrieve contact statistics.
    Prefer ContactService.get_statistics() when available.
    A fallback is provided so that the dashboard still works if the service
    does not yet implement statistics.
    """

    try:
        statistics = ContactService.get_statistics()
        if statistics is not None:
            return statistics

    except (
        AttributeError,
        TypeError,
    ):
        pass

    contacts = _get_all_contacts()

    total = len(contacts)

    open_count = 0
    urgent_count = 0
    unread_count = 0
    resolved_count = 0
    archived_count = 0
    for contact in contacts:
        status = str(
            _contact_value(
                contact,
                "status",
                default="",
            )
            or ""
        ).lower()
        priority = str(
            _contact_value(
                contact,
                "priority",
                default="",
            )
            or ""
        ).lower()

        is_read = _contact_value(
            contact,
            "is_read",
            default=True,
        )

        if status in {
            "open",
            "new",
            "in progress",
        }:
            open_count += 1

        if priority in {
            "urgent",
            "critical",
        }:
            urgent_count += 1

        if not is_read:
            unread_count += 1

        if status in {
            "resolved",
        }:
            resolved_count += 1

        if status in {
            "closed",
            "archived",
        }:
            archived_count += 1

    return {
        "total": total,
        "open": open_count,
        "urgent": urgent_count,
        "unread": unread_count,
        "resolved": resolved_count,
        "archived": archived_count,
    }

# =============================================================================
# Inbox / Dashboard
# =============================================================================
@contacts_bp.route("/",methods=["GET"],)
@admin_required
@login_required
def index():
    """
    Contact enquiry inbox.
    Supports:
        • keyword search
        • status
        • enquiry type
        • priority
        • assignment
        • department
        • source
        • unread-only
        • follow-up-only
        • urgent-only
        • archived filtering
    """

    form = ContactFilterForm(
        request.args or None
    )

    _populate_assignment_choices(
        form
    )

    filters = {
        "search": form.search.data,
        "status": form.status.data,
        "enquiry_type": form.enquiry_type.data,
        "priority": form.priority.data,
        "assigned_user_id": form.assigned_user_id.data,
        "department": form.department.data,
        "source": form.source.data,
        "unread_only": form.unread_only.data,
        "follow_up_only": form.follow_up_only.data,
        "urgent_only": form.urgent_only.data,
        "archived": form.archived.data,
    }

    page = _get_pagination_page()
    contacts = _get_filtered_contacts(
        filters
    )

    # Newest enquiries first where possible.
    try:
        contacts.sort(
            key=lambda contact: (
                _contact_value(
                    contact,
                    "created_at",
                    default=datetime.min,
                )
                or datetime.min
            ),
            reverse=True,
        )
    except Exception:
        pass

    pagination = _paginate_list(
        contacts,
        page=page,
        per_page=25,
    )
    archive_form = ContactArchiveForm()
    archive_form.action.data = "archive"

    statistics = _get_statistics()
    return render_template(
        "admin/contact/index.html",
        form=form,
        archive_form=archive_form,
        contacts=pagination["items"],
        pagination=pagination,
        statistics=statistics,
        filters=filters,
    )

# =============================================================================
# Detail
# =============================================================================
@contacts_bp.route("/<int:contact_id>",methods=["GET"],)
@admin_required
@login_required
def detail(contact_id):
    """
    Display a complete enquiry and its conversation/history.
    """

    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)

        return redirect(
            url_for("contacts.index"))

    # -------------------------------------------------------------------------
    # Mark Read
    # -------------------------------------------------------------------------
    try:
        ContactService.mark_many_as_read([contact_id])

        # Refresh the object if the service updates the database directly.
        db.session.refresh(contact)

    except Exception:
        current_app.logger.exception(
            "Failed to mark contact %s as read.",
            contact_id,
        )

    # -------------------------------------------------------------------------
    # Replies
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Replies — load incoming and outgoing messages for this enquiry
    # -------------------------------------------------------------------------
    replies = []

    try:
        replies = ContactReplyService.get_by_contact(
            contact_id=contact_id,
            newest_first=False,
        ) or []

        current_app.logger.info(
            "Contact %s conversation loaded: %s replies; IDs=%s; directions=%s",
            contact_id,
            len(replies),
            [reply.id for reply in replies],
            [reply.direction for reply in replies],
        )

    except Exception:
        current_app.logger.exception(
            "Failed to load replies for contact %s.",
            contact_id,
        )
        replies = []
    # -------------------------------------------------------------------------
    # Notes
    # -------------------------------------------------------------------------
    notes = []
    try:
        notes = (
            ContactNoteService.get_by_contact(
                contact_id)
            or [])

    except (AttributeError,TypeError,):
        notes = []

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------
    history = []
    try:
        history = (
            ContactNoteService.get_contact_history(
                contact_id)
            or [])

    except (
        AttributeError,
        TypeError,
    ):
        history = notes

    # -------------------------------------------------------------------------
    # Forms
    # -------------------------------------------------------------------------
    reply_form = ContactReplyForm()
    note_form = ContactNoteForm()
    status_form = ContactStatusForm()
    priority_form = ContactPriorityForm()
    assignment_form = ContactAssignmentForm()
    follow_up_form = ContactFollowUpForm()
    resolution_form = ContactResolutionForm()
    archive_form = ContactArchiveForm()
    read_status_form = ContactReadStatusForm()
    _populate_assignment_choices(assignment_form)

    return render_template(
        "admin/contact/detail.html",
        contact=contact,
        replies=replies,
        notes=notes,
        history=history,
        reply_form=reply_form,
        note_form=note_form,
        status_form=status_form,
        priority_form=priority_form,
        assignment_form=assignment_form,
        follow_up_form=follow_up_form,
        resolution_form=resolution_form,
        archive_form=archive_form,
        read_status_form=read_status_form,)

# =============================================================================
# Create
# =============================================================================
@contacts_bp.route("/create",methods=["GET", "POST"],)
@admin_required
@login_required
def create():
    """
    Manually create a new customer enquiry.
    """
    form = ContactCreateForm()
    if form.validate_on_submit():
        try:
            contact = ContactService.create_contact(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company=form.company.data,
                country=form.country.data,
                subject=form.subject.data,
                enquiry_type=form.enquiry_type.data,
                message=form.message.data,
                priority=form.priority.data,
                department=form.department.data,
                source=form.source.data,
                newsletter_opt_in=form.newsletter_opt_in.data,)

            flash("Enquiry created successfully.","success",)

            return redirect(
                url_for("contacts.detail",contact_id=contact.id,))

        except Exception as exc:
            flash(f"Unable to create the enquiry: {exc}","danger",)

    return render_template(
        "admin/contact/create.html",form=form,)

# =============================================================================
# Edit Contact / Enquiry
# =============================================================================
@contacts_bp.route("/<int:contact_id>/edit", methods=["GET", "POST"])
@admin_required
@login_required
def edit(contact_id):
    """Edit an existing customer enquiry."""

    contact = ContactService.get_by_id(contact_id)

    if not contact:
        flash(
            "The requested enquiry could not be found.",
            "warning",
        )
        return redirect(url_for("contacts.index"))

    form = ContactEditForm(obj=contact)

    # Populate assignment choices before validating the submitted form.
    # Preserve your application's existing user-query/authorization rules here.
    if hasattr(form, "assigned_user_id"):
        form.assigned_user_id.choices = [
            (0, "Unassigned"),
            *[
                (user.id, user.full_name)
                for user in User.query.order_by(User.id.asc()).all()
            ],
        ]

    if form.validate_on_submit():
        try:
            assigned_user_id = form.assigned_user_id.data

            ContactService.update_contact(
                contact_id=contact_id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company=form.company.data,
                country=form.country.data,
                subject=form.subject.data,
                enquiry_type=form.enquiry_type.data,
                message=form.message.data,
                status=form.status.data,
                priority=form.priority.data,
                department=form.department.data,
                source=form.source.data,
                assigned_user_id=(
                    assigned_user_id if assigned_user_id else None
                ),
                follow_up_required=form.follow_up_required.data,
                follow_up_date=form.follow_up_date.data,
                resolution_notes=form.resolution_notes.data,
                newsletter_opt_in=form.newsletter_opt_in.data,
            )

            flash(
                "Enquiry updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "contacts.detail",
                    contact_id=contact_id,
                )
            )

        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to update contact %s",
                contact_id,
            )
            flash(
                "Unable to update the enquiry. Please check the form "
                "and try again.",
                "danger",
            )

    return render_template(
        "admin/contact/edit.html",
        form=form,
        contact=contact,
    )

# =============================================================================
# Assignment
# =============================================================================
@contacts_bp.route("/<int:contact_id>/assign", methods=["POST"])
@admin_required
@login_required
def assign(contact_id):
    """Assign an enquiry to an eligible internal user or unassign it."""
    contact = ContactService.get_by_id(contact_id)

    if not contact:
        flash("The requested enquiry could not be found.", "warning")
        return redirect(url_for("contacts.index"))

    form = ContactAssignmentForm()
    _populate_assignment_choices(form)

    if form.validate_on_submit():
        assigned_user_id = form.assigned_user_id.data

        try:
            if assigned_user_id:
                assigned_user = _get_user_by_id(assigned_user_id)

                if (
                    not assigned_user
                    or not assigned_user.is_active
                    or not assigned_user.is_internal_user
                ):
                    raise ValueError(
                        "Select an active administrator, staff member, "
                        "or guide."
                    )

                ContactService.assign(
                    contact_id=contact_id,
                    assigned_user_id=assigned_user.id,
                    department=form.department.data,
                )
                flash(
                    f"Enquiry assigned to {assigned_user.full_name}.",
                    "success",
                )
            else:
                ContactService.unassign(contact_id)

                # Preserve the submitted department if provided.
                if form.department.data is not None:
                    contact.department = form.department.data
                    db.session.commit()

                flash("Enquiry has been unassigned.", "success")

        except ValueError as exc:
            flash(str(exc), "warning")
        except Exception:
            db.session.rollback()
            current_app.logger.exception(
                "Failed to assign contact %s.", contact_id
            )
            flash("Unable to update the enquiry assignment.", "danger")
    else:
        flash(
            "The assignment could not be processed. Please check the form.",
            "warning",
        )

    return redirect(
        url_for("contacts.detail", contact_id=contact_id)
    )

# =============================================================================
# Status
# =============================================================================
@contacts_bp.route("/<int:contact_id>/status",methods=["POST"],)
@admin_required
@login_required
def status(contact_id):
    """
    Change enquiry status.
    """

    contact = ContactService.get_by_id(
        contact_id
    )

    if not contact:

        flash(
            "The requested enquiry could not be found.",
            "warning",
        )

        return redirect(
            url_for(
                "contacts.index"
            )
        )

    form = ContactStatusForm()

    if form.validate_on_submit():

        try:

            ContactService.update_status(
                contact_id=contact_id,
                status=form.status.data,
            )

            flash(
                "Enquiry status updated.",
                "success",
            )

        except Exception as exc:

            flash(
                f"Unable to update status: {exc}",
                "danger",
            )

    else:

        flash(
            "Invalid status selection.",
            "warning",
        )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        ))

# =============================================================================
# Priority
# =============================================================================
@contacts_bp.route("/<int:contact_id>/priority",methods=["POST"],)
@admin_required
@login_required
def priority(contact_id):
    """
    Change enquiry priority.
    """

    contact = ContactService.get_by_id(
        contact_id
    )

    if not contact:

        flash(
            "The requested enquiry could not be found.",
            "warning",
        )

        return redirect(
            url_for(
                "contacts.index"
            )
        )

    form = ContactPriorityForm()

    if form.validate_on_submit():

        try:

            ContactService.set_priority(
                contact_id=contact_id,
                priority=form.priority.data,
            )

            flash(
                "Enquiry priority updated.",
                "success",
            )

        except Exception as exc:

            flash(
                f"Unable to update priority: {exc}",
                "danger",
            )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        )
    )

# =============================================================================
# Follow-up
# =============================================================================
@contacts_bp.route("/<int:contact_id>/follow-up",methods=["POST"],)
@admin_required
@login_required
def follow_up(contact_id):
    """
    Schedule a follow-up for an enquiry.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)

        return redirect(
            url_for("contacts.index"))

    form = ContactFollowUpForm()
    if form.validate_on_submit():
        try:

            ContactService.schedule_follow_up(
                contact_id=contact_id,
                follow_up_date=form.follow_up_date.data,
            )

            flash(
                "Follow-up scheduled successfully.",
                "success",
            )

        except Exception as exc:

            flash(
                f"Unable to schedule follow-up: {exc}",
                "danger",
            )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        )
    )


@contacts_bp.route("/<int:contact_id>/follow-up/cancel",methods=["POST"],)
@login_required
def cancel_follow_up(contact_id):
    """
    Cancel an existing follow-up.
    """

    contact = ContactService.get_by_id(
        contact_id
    )

    if not contact:

        flash(
            "The requested enquiry could not be found.",
            "warning",
        )

        return redirect(
            url_for(
                "contacts.index"
            )
        )

    try:

        ContactService.cancel_follow_up(
            contact_id
        )

        flash(
            "Follow-up cancelled.",
            "success",
        )

    except Exception as exc:

        flash(
            f"Unable to cancel follow-up: {exc}",
            "danger",
        )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        ))

# =============================================================================
# Reply
# =============================================================================
@contacts_bp.route("/<int:contact_id>/reply",methods=["GET", "POST"],)
@admin_required
@login_required
def reply(contact_id):
    """
    Compose and send a response to an enquiry.
    Email delivery is delegated to ContactReplyService.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)
        return redirect(url_for("contacts.index"))

    form = ContactReplyForm()
    if request.method == "GET":
        if not form.subject.data:
            form.subject.data = (
                f"Re: {contact.subject}"
                if contact.subject
                else "Re: Your enquiry")

    if form.validate_on_submit():
        try:
            reply = ContactReplyService.create_reply(
                contact_id=contact_id,
                user_id=current_user.id,
                sender_name=current_user.full_name,
                sender_email=current_user.email,
                subject=form.subject.data,
                message=form.message.data,
                delivery_method="Email",)

            if form.send_email.data:
                ContactReplyService.send_reply(
                    reply.id,
                    reply_to="theunchartedrouteke@gmail.com",
                )
                flash("Reply sent successfully.", "success")

            else:
                flash("Reply saved without sending an email.","success",)
            if form.mark_in_progress.data:
                try:
                    ContactService.update_status(
                        contact_id=contact_id,
                        status="In Progress",)
                except Exception:
                    pass

            return redirect(
                url_for(
                    "contacts.detail",contact_id=contact_id,))
        except Exception as exc:
            flash(f"Unable to send the reply: {exc}","danger",)

    return render_template(
        "admin/contact/reply.html",
        form=form,
        contact=contact,)

from app.services.contact_mailbox_sync_service import (
    ContactMailboxSyncService,)

@contacts_bp.route("/sync-mailbox", methods=["POST"])
@admin_required
@login_required
def sync_mailbox():
    # Apply your existing admin/authorized-user guard here.
    try:
        result = ContactMailboxSyncService.sync_inbox()

        flash(
            (
                "Mailbox sync completed. "
                f"Imported: {result['imported']}; "
                f"already processed or skipped: {result['skipped']}; "
                f"unmatched: {result['unmatched']}."
            ),
            "success",
        )
    except Exception:
        current_app.logger.exception(
            "Admin-triggered contact mailbox synchronization failed."
        )
        flash(
            "Mailbox synchronization failed. Check the server logs "
            "and mailbox configuration.",
            "danger",
        )

    return redirect(url_for("contacts.index"))
# =============================================================================
# Internal Notes
# =============================================================================
@contacts_bp.route("/<int:contact_id>/note",methods=["POST"],)
@admin_required
@login_required
def add_note(contact_id):
    """
    Add an internal note to an enquiry.
    """

    contact = ContactService.get_by_id(
        contact_id
    )

    if not contact:

        flash(
            "The requested enquiry could not be found.",
            "warning",
        )

        return redirect(
            url_for(
                "contacts.index"
            )
        )

    form = ContactNoteForm()

    if form.validate_on_submit():

        try:

            ContactNoteService.create_note(
                contact_id=contact_id,
                user_id=current_user.id,
                author_name=current_user.full_name,
                note=form.note.data,
                note_type=form.note_type.data,
                is_important=form.is_important.data,
            )

            flash(
                "Internal note added.",
                "success",
            )

        except Exception as exc:

            flash(
                f"Unable to add note: {exc}",
                "danger",
            )

    else:

        flash(
            "The note could not be added.",
            "warning",
        )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        )
    )


# =============================================================================
# Resolution
# =============================================================================
@contacts_bp.route("/<int:contact_id>/resolve",methods=["POST"],)
@login_required
def resolve(contact_id):
    """
    Resolve an enquiry and record resolution notes.
    """

    contact = ContactService.get_by_id(
        contact_id
    )

    if not contact:

        flash(
            "The requested enquiry could not be found.",
            "warning",
        )

        return redirect(
            url_for(
                "contacts.index"
            )
        )

    form = ContactResolutionForm()

    if form.validate_on_submit():

        try:

            ContactService.resolve(
                contact_id=contact_id,
                resolution_notes=form.resolution_notes.data,
            )

            # Preserve the resolution as an internal note.
            try:

                ContactNoteService.create_note(
                    contact_id=contact_id,
                    user_id=current_user.id,
                    author_name=current_user.full_name,
                    note=form.resolution_notes.data,
                    note_type="Resolution",
                    is_important=True,
                )

            except Exception:
                pass

            flash(
                "Enquiry resolved successfully.",
                "success",
            )

        except Exception as exc:

            flash(
                f"Unable to resolve enquiry: {exc}",
                "danger",
            )

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,
        )
    )


@contacts_bp.route("/<int:contact_id>/reopen",methods=["POST"],)
@admin_required
@login_required
def reopen(contact_id):
    """
    Reopen a previously resolved or closed enquiry.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)

        return redirect(
            url_for("contacts.index"))

    try:
        ContactService.reopen(contact_id)
        flash("Enquiry reopened.","success",)

    except Exception as exc:
        flash(f"Unable to reopen enquiry: {exc}","danger",)

    return redirect(
        url_for(
            "contacts.detail",
            contact_id=contact_id,))

# =============================================================================
# Mark Enquiry as Read
# =============================================================================
@contacts_bp.route("/<int:contact_id>/read", methods=["POST"])
@admin_required
@login_required
def mark_read(contact_id):
    contact = ContactService.get_by_id(contact_id)

    if not contact:
        flash("The requested enquiry could not be found.", "warning")
        return redirect(url_for("contacts.index"))

    try:
        ContactService.mark_as_read(contact_id)
        flash("Enquiry marked as read.", "success")
    except Exception:
        current_app.logger.exception(
            "Failed to mark contact %s as read.", contact_id
        )
        flash("Unable to mark the enquiry as read.", "danger")

    return redirect(
        request.referrer
        or url_for("contacts.detail", contact_id=contact_id))

# =============================================================================
# Mark Enquiry as Unread
# =============================================================================
@contacts_bp.route("/<int:contact_id>/unread", methods=["POST"])
@admin_required
@login_required
def mark_unread(contact_id):
    contact = ContactService.get_by_id(contact_id)

    if not contact:
        flash("The requested enquiry could not be found.", "warning")
        return redirect(url_for("contacts.index"))

    try:
        ContactService.mark_as_unread(contact_id)
        flash("Enquiry marked as unread.", "success")
    except Exception:
        current_app.logger.exception(
            "Failed to mark contact %s as unread.", contact_id
        )
        flash("Unable to mark the enquiry as unread.", "danger")

    return redirect(
        request.referrer
        or url_for("contacts.detail", contact_id=contact_id))

# =============================================================================
# Archive
# =============================================================================
@contacts_bp.route("/<int:contact_id>/archive", methods=["POST"])
@admin_required
@login_required
def archive(contact_id):
    """Archive an enquiry."""
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)
        return redirect(url_for("contacts.index"))

    form = ContactArchiveForm()

    if not form.validate_on_submit():
        errors = "; ".join(
            f"{field}: {', '.join(messages)}"
            for field, messages in form.errors.items())

        current_app.logger.warning(
            "Contact archive validation failed for ID %s: %s",
            contact_id,
            errors,)

        flash(f"Unable to archive enquiry. Please check the form. {errors}","danger",)
        return redirect(
            request.referrer or url_for("contacts.index"))

    try:
        archived_contact = ContactService.archive(contact_id)

        if archived_contact is None:
            flash("The requested enquiry could not be found.", "warning")
        else:
            flash("Enquiry archived successfully.", "success")

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "Failed to archive contact ID %s",
            contact_id,
        )

        flash(
            "An unexpected error occurred while archiving the enquiry.",
            "danger",
        )

    return redirect(
        request.referrer or url_for("contacts.index"))

@contacts_bp.route("/<int:contact_id>/restore",methods=["POST"],)
@admin_required
@login_required
def restore(contact_id):
    """
    Restore an archived enquiry.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)
        return redirect(
            url_for("contacts.index"))
    form = ContactRestoreForm()
    if form.validate_on_submit():
        try:
            ContactService.unarchive(contact_id)
            flash("Enquiry restored successfully.","success",)

        except Exception as exc:
            flash(f"Unable to restore enquiry: {exc}","danger",)

    return redirect(
        request.referrer
        or url_for(
            "contacts.index"))

# =============================================================================
# Archived Enquiries
# =============================================================================
@contacts_bp.route("/archived", methods=["GET"])
@login_required
def archived():
    """Display, search, filter, and paginate archived enquiries."""

    # -------------------------------------------------------------------------
    # Base query: archived records only
    # -------------------------------------------------------------------------
    archived_query = Contact.query.filter(
        Contact.is_archived.is_(True)
    )

    # Total archive count, independent of current filters and pagination.
    total_archived = archived_query.count()

    # -------------------------------------------------------------------------
    # Read filters
    # -------------------------------------------------------------------------
    search = request.args.get("search", "", type=str).strip()
    enquiry_type = request.args.get("enquiry_type", "", type=str).strip()
    priority = request.args.get("priority", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    if search:
        search_term = f"%{search}%"

        archived_query = archived_query.filter(
            or_(
                Contact.full_name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.subject.ilike(search_term),
                Contact.message.ilike(search_term),
                Contact.company.ilike(search_term),
            )
        )

    # -------------------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------------------
    if enquiry_type:
        archived_query = archived_query.filter(
            Contact.enquiry_type == enquiry_type
        )

    if priority:
        archived_query = archived_query.filter(
            Contact.priority == priority
        )

    if status:
        archived_query = archived_query.filter(
            Contact.status == status
        )

    # -------------------------------------------------------------------------
    # Filtered count and status statistics
    # -------------------------------------------------------------------------
    filtered_count = archived_query.count()

    statistics = {
        "archived": total_archived,
        "resolved": Contact.query.filter(
            Contact.is_archived.is_(True),
            Contact.status == "Resolved",
        ).count(),
        "closed": Contact.query.filter(
            Contact.is_archived.is_(True),
            Contact.status == "Closed",
        ).count(),
    }

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    page = max(
        request.args.get("page", 1, type=int),
        1,
    )

    per_page = request.args.get(
        "per_page",
        25,
        type=int,
    )

    if per_page not in {10, 25, 50, 100}:
        per_page = 25

    pagination = (
        archived_query
        .order_by(
            Contact.archived_at.desc(),
            Contact.created_at.desc(),
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
    )

    contacts = pagination.items

    # -------------------------------------------------------------------------
    # Filter choices
    # -------------------------------------------------------------------------
    enquiry_types = [
        value
        for value, in (
            Contact.query
            .with_entities(Contact.enquiry_type)
            .filter(
                Contact.is_archived.is_(True),
                Contact.enquiry_type.isnot(None),
                Contact.enquiry_type != "",
            )
            .distinct()
            .order_by(Contact.enquiry_type.asc())
            .all()
        )
    ]

    priorities = [
        value
        for value, in (
            Contact.query
            .with_entities(Contact.priority)
            .filter(
                Contact.is_archived.is_(True),
                Contact.priority.isnot(None),
                Contact.priority != "",
            )
            .distinct()
            .order_by(Contact.priority.asc())
            .all()
        )
    ]

    # -------------------------------------------------------------------------
    # Forms for row actions
    # -------------------------------------------------------------------------
    restore_form = ContactRestoreForm()
    restore_form.action.data = "restore"

    # -------------------------------------------------------------------------
    # Render
    # -------------------------------------------------------------------------
    return render_template(
        "admin/contact/archived.html",
        contacts=contacts,
        pagination=pagination,
        statistics=statistics,
        total_archived=total_archived,
        filtered_count=filtered_count,
        enquiry_types=enquiry_types,
        priorities=priorities,
        restore_form=restore_form,
    )

# =============================================================================
# Statistics
# =============================================================================
@contacts_bp.route("/statistics",methods=["GET"],)
@admin_required
@login_required
def statistics():
    """
    Display contact / enquiry analytics.
    """
    try:
        statistics_data = (ContactService.get_statistics())
    except Exception:
        statistics_data = (_get_statistics())

    try:
        reply_statistics = (ContactReplyService.get_statistics())
    except Exception:
        reply_statistics = {}
    try:
        note_statistics = (
            ContactNoteService.get_statistics()
        )

    except Exception:
        note_statistics = {}
    return render_template(
        "admin/contact/statistics.html",
        statistics=statistics_data,
        reply_statistics=reply_statistics,
        note_statistics=note_statistics,)

# =============================================================================
# Bulk Actions
# =============================================================================
@contacts_bp.route("/bulk-action", methods=["POST"])
@admin_required
@login_required
def bulk_action():
    """
    Apply an action to multiple enquiries.
    """
    form = ContactBulkActionForm()
    _populate_assignment_choices(form)
    # -------------------------------------------------------------------------
    # Validate CSRF and submitted form fields
    # -------------------------------------------------------------------------
    if not form.validate_on_submit():
        flash("Invalid bulk action or expired form. Please try again.","warning",)

        return redirect(
            request.referrer or url_for("contacts.index"))

    # -------------------------------------------------------------------------
    # Validate selected enquiry IDs
    # -------------------------------------------------------------------------
    selected_ids = request.form.getlist("contact_ids")
    if not selected_ids:
        flash("Please select at least one enquiry.","warning",)

        return redirect(
            request.referrer
            or url_for("contacts.index"))

    contact_ids = []
    for raw_contact_id in selected_ids:
        try:
            contact_id = int(raw_contact_id)

            if contact_id > 0 and contact_id not in contact_ids:
                contact_ids.append(contact_id)

        except (TypeError, ValueError):
            continue

    if not contact_ids:
        flash("No valid enquiries were selected.","warning",)

        return redirect(
            request.referrer
            or url_for("contacts.index"))

    action = form.action.data
    try:
        # =====================================================================
        # Update Status
        # =====================================================================
        if action == "status":
            if not form.status.data:
                flash("Please select a status.","warning",)

                return redirect(
                    request.referrer
                    or url_for("contacts.index"))

            successful = 0
            for contact_id in contact_ids:
                result = ContactService.update_status(
                    contact_id=contact_id,
                    status=form.status.data,)

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries updated successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Update Priority
        # =====================================================================
        elif action == "priority":

            if not form.priority.data:
                flash(
                    "Please select a priority.",
                    "warning",
                )

                return redirect(
                    request.referrer
                    or url_for("contacts.index")
                )

            successful = 0

            for contact_id in contact_ids:
                result = ContactService.set_priority(
                    contact_id=contact_id,
                    priority=form.priority.data,
                )

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries reprioritized successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Assign Enquiries
        # =====================================================================
        elif action == "assign":

            # None allows the service to clear an existing assignment,
            # provided that this is supported by ContactService.assign().
            assigned_user_id = (
                form.assigned_user_id.data
                or None
            )

            successful = 0

            for contact_id in contact_ids:
                result = ContactService.assign(
                    contact_id=contact_id,
                    assigned_user_id=assigned_user_id,
                )

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries assigned successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Mark as Read
        # =====================================================================
        elif action == "read":

            successful = ContactService.mark_many_as_read(
                contact_ids
            )

            # Supports services that return None after successful execution.
            if successful is None:
                successful = len(contact_ids)

            flash(
                f"{successful} enquiries marked as read.",
                "success",
            )

        # =====================================================================
        # Mark as Unread
        # =====================================================================
        elif action == "unread":

            successful = ContactService.mark_many_as_unread(
                contact_ids
            )

            if successful is None:
                successful = len(contact_ids)

            flash(
                f"{successful} enquiries marked as unread.",
                "success",
            )

        # =====================================================================
        # Archive Enquiries
        # =====================================================================
        elif action == "archive":

            successful = 0

            for contact_id in contact_ids:
                result = ContactService.archive(contact_id)

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries archived successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Restore Archived Enquiries
        # =====================================================================
        elif action == "restore":

            successful = 0

            for contact_id in contact_ids:
                result = ContactService.unarchive(contact_id)

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries restored successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Delete Enquiries
        # =====================================================================
        elif action == "delete":

            successful = 0

            for contact_id in contact_ids:
                result = ContactService.delete(contact_id)

                if result is not False:
                    successful += 1

            flash(
                f"{successful} enquiries deleted successfully.",
                "success" if successful else "warning",
            )

        # =====================================================================
        # Unsupported Action
        # =====================================================================
        else:
            flash(
                "Unsupported bulk action.",
                "warning",
            )

    except Exception:
        # Log the exception for debugging without exposing internal details
        # to the user-facing interface.
        current_app.logger.exception(
            "Bulk contact action failed. Action=%s, Contact IDs=%s",
            action,
            contact_ids,
        )

        flash(
            "The bulk action could not be completed. Please try again.",
            "danger",
        )

    return redirect(
        request.referrer
        or url_for("contacts.index")
    )
# =============================================================================
# Delete
# =============================================================================
@contacts_bp.route("/<int:contact_id>/delete",methods=["POST"],)
@admin_required
@login_required
def delete(contact_id):
    """
    Permanently delete an enquiry.
    This is intentionally POST-only because deletion is destructive.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)
        return redirect(
            url_for("contacts.index"))
    try:
        ContactService.delete(contact_id)
        flash("Enquiry deleted permanently.","success",)
    except Exception as exc:

        flash(f"Unable to delete enquiry: {exc}","danger",)

    return redirect(url_for("contacts.index"))

# =============================================================================
# Quick Actions
# =============================================================================
@contacts_bp.route("/<int:contact_id>/close",methods=["POST"],)
@login_required
def close(contact_id):
    """
    Quickly close an enquiry.
    """
    contact = ContactService.get_by_id(contact_id)
    if not contact:
        flash("The requested enquiry could not be found.","warning",)

        return redirect(
            url_for("contacts.index"))

    try:
        ContactService.close(contact_id)
        flash("Enquiry closed.","success",)

    except Exception as exc:
        flash(f"Unable to close enquiry: {exc}","danger",)

    return redirect(
        request.referrer
        or url_for(
            "contacts.detail",
            contact_id=contact_id,))

# =============================================================================
# Reopen Compatibility Alias
# =============================================================================
@contacts_bp.route("/<int:contact_id>/reopen-legacy",methods=["POST"],)
@admin_required
@login_required
def reopen_enquiry(contact_id):
    """
    Compatibility alias for reopening an enquiry.
    The primary reopen route is:
        /<contact_id>/reopen
    """
    return reopen(contact_id)

# =============================================================================
# Error Handling
# =============================================================================
@contacts_bp.errorhandler(404)
def contact_not_found(error):
    """
    Handle missing contact resources.
    """
    flash(
        "The requested contact enquiry was not found.",
        "warning",)

    return redirect(
        url_for("contacts.index"))

@contacts_bp.errorhandler(403)
def contact_forbidden(error):
    """
    Handle forbidden contact access.
    """
    flash("You do not have permission to access this area.","danger",)
    return redirect(
        url_for("admin.dashboard"))

# =============================================================================
# Public API
# =============================================================================
__all__ = ["contacts_bp",]