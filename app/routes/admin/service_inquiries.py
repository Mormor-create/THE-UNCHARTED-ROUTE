"""
===============================================================================
The Uncharted Route
Admin Service Enquiries CMS
===============================================================================
Central inbox for Safari, Stay, and Experience enquiries.

Supports:
- Unified active enquiries inbox
- Enquiry detail and status management
- Editing existing enquiries
- Archiving and restoring enquiries
- Separate archived enquiries view
- Controlled permanent deletion of archived enquiries

This module does not create booking or process payments.
===============================================================================
"""

from datetime import date, datetime
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,)
from app.decorators.admin import admin_required
from app.models import SafariInquiry, StayInquiry, ExperienceInquiry, StayRoom, Stay
from extensions import db

service_inquiries_bp = Blueprint(
    "service_inquiries",
    __name__,
    url_prefix="/admin/service-inquiries",)

# =============================================================================
# Configuration
# =============================================================================
SERVICE_TYPES = {
    "safari": "Safari",
    "stay": "Stay",
    "experience": "Experience",}

STATUS_OPTIONS = {
    "safari": [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("quoting", "Quoting"),
        ("quoted", "Quoted"),
        ("confirmed", "Confirmed"),
        ("declined", "Declined"),
        ("closed", "Closed"),
    ],
    "stay": [
        ("New", "New"),
        ("Contacted", "Contacted"),
        ("Quoting", "Quoting"),
        ("Quoted", "Quoted"),
        ("Confirmed", "Confirmed"),
        ("Declined", "Declined"),
        ("Closed", "Closed"),
    ],
    "experience": [
        ("New", "New"),
        ("Contacted", "Contacted"),
        ("Quoting", "Quoting"),
        ("Quoted", "Quoted"),
        ("Confirmed", "Confirmed"),
        ("Declined", "Declined"),
        ("Closed", "Closed"),],}

MODEL_BY_TYPE = {
    "safari": SafariInquiry,
    "stay": StayInquiry,
    "experience": ExperienceInquiry,}

# =============================================================================
# Shared Helpers
# =============================================================================
def _value(obj, attribute, default=""):
    """Read an optional model attribute safely."""
    value = getattr(obj, attribute, None)
    return value if value is not None else default

def _relationship_name(obj, attribute, fallback="Not specified"):
    """Return a readable name from a related object."""
    related = getattr(obj, attribute, None)

    if related is None:
        return fallback

    return (
        getattr(related, "name", None)
        or getattr(related, "title", None)
        or getattr(related, "property_name", None)
        or fallback)

def _inquiry_reference(service_type, inquiry):
    """Return the public reference for an enquiry."""
    if service_type == "safari":
        return _value(inquiry, "reference", f"SAF-{inquiry.id}")

    if service_type == "experience":
        return _value(
            inquiry,
            "inquiry_reference",
            f"EXP-{inquiry.id}",)
    return f"STAY-{inquiry.id}"

def _target_name(service_type, inquiry):
    """Return the primary Safari, Stay, or Experience name."""
    if service_type == "safari":
        property_name = _relationship_name(inquiry, "property")
        destination_name = _relationship_name(inquiry, "destination")

        if property_name != "Not specified":
            return property_name
        return destination_name
    if service_type == "stay":
        return _relationship_name(inquiry, "stay")
    return _relationship_name(inquiry, "experience")

def _inquiry_date(inquiry):
    """Return the best available enquiry timestamp."""
    return (
        _value(inquiry, "created_at")
        or _value(inquiry, "updated_at")
        or datetime.min)

def _make_inbox_item(service_type, inquiry):
    """Normalize the different enquiry models for combined views."""

    if service_type == "safari":

        start_date = _value(
            inquiry,
            "preferred_start_date",)

        end_date = _value(
            inquiry,
            "preferred_end_date",)

        requested_dates = "Flexible dates"

        if start_date and end_date:
            requested_dates = (
                f"{start_date} – {end_date}")

        elif start_date:
            requested_dates = str(start_date)

        elif end_date:
            requested_dates = str(end_date)

        guest_count = (
            (_value(inquiry, "adults", 0) or 0)
            + (_value(inquiry, "children", 0) or 0)
            + (_value(inquiry, "infants", 0) or 0))

        target_name = _target_name(
            service_type,
            inquiry,)

        stay_name = ""
        room_name = ""


    elif service_type == "stay":
        start_date = _value(
            inquiry,"check_in",)

        end_date = _value(
            inquiry,
            "check_out",)

        requested_dates = (
            f"{start_date} – {end_date}"
            if start_date and end_date
            else "Dates not specified")

        guest_count = (
                (_value(inquiry, "adults", 0) or 0)
                + (_value(inquiry, "children", 0) or 0))

        # -------------------------------------------------------------------------
        # Stay
        # -------------------------------------------------------------------------
        # StayInquiry stores stay_id, but does not expose a `stay` relationship.
        # Resolve the Stay directly from its foreign key.
        # -------------------------------------------------------------------------
        stay = (
            db.session.get(Stay, inquiry.stay_id)
            if inquiry.stay_id
            else None)

        if stay:
            stay_name = (
                    getattr(stay, "name", None)
                    or getattr(stay, "title", None)
                    or getattr(stay, "property_name", None)
                    or "Not specified")

        else:
            stay_name = "Not specified"

        # -------------------------------------------------------------------------
        # Room
        # -------------------------------------------------------------------------
        # The existing room relationship is already working, so retain it.
        # -------------------------------------------------------------------------
        room_name = _relationship_name(
            inquiry,
            "room",
            "Any suitable room",)
        target_name = stay_name
    else:

        preferred_date = _value(
            inquiry,
            "preferred_date",)

        requested_dates = (
            str(preferred_date)
            if preferred_date
            else "Flexible dates")

        guest_count = (
            (_value(inquiry, "adults", 0) or 0)
            + (_value(inquiry, "children", 0) or 0)
            + (_value(inquiry, "infants", 0) or 0))

        target_name = _target_name(
            service_type,
            inquiry,)

        stay_name = ""
        room_name = ""

    return {
        "service_type": service_type,
        "service_label": SERVICE_TYPES[service_type],
        "id": inquiry.id,
        "reference": _inquiry_reference(
            service_type,
            inquiry,),
        "customer": _value(
            inquiry,
            "full_name",
            "Unknown customer",),
        "email": _value(
            inquiry,
            "email",),
        "phone": _value(
            inquiry,
            "phone",),
        "target": target_name,

        # Explicit Stay/Room values for Stay enquiries.
        "stay_name": stay_name,
        "room_name": room_name,
        "status": _value(
            inquiry,
            "status",
            "New",),
        "source": _value(
            inquiry,
            "source",
            "Website",),
        "requested_dates": requested_dates,
        "guest_count": guest_count,
        "created_at": _inquiry_date(
            inquiry,),
        "is_archived": bool(
            _value(
                inquiry,
                "is_archived",
                False,)),

        "url": url_for(
            "service_inquiries.detail",
            service_type=service_type,
            inquiry_id=inquiry.id,),}

def _all_inquiries(archived=None):
    """
    Load and normalize enquiries across all three service models.

    archived=False: active enquiries only.
    archived=True: archived enquiries only.
    archived=None: all enquiries.
    """
    items = []

    for service_type, model in MODEL_BY_TYPE.items():
        query = model.query

        if archived is not None:
            query = query.filter(
                model.is_archived.is_(archived)
            )

        records = query.all()

        items.extend(
            _make_inbox_item(service_type, record)
            for record in records
        )

    items.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    return items


def _get_inquiry(service_type, inquiry_id):
    """Fetch an enquiry by service type and ID."""
    service_type = (service_type or "").lower()
    model = MODEL_BY_TYPE.get(service_type)

    if model is None:
        abort(404)

    inquiry = db.session.get(model, inquiry_id)

    if inquiry is None:
        abort(404)

    return inquiry


def _detail_context(service_type, inquiry):
    """Build common detail fields while retaining model relationships."""
    item = _make_inbox_item(service_type, inquiry)

    details = [
        ("Reference", item["reference"]),
        ("Service", item["service_label"]),
        ("Customer", item["customer"]),
        ("Email", item["email"] or "Not provided"),
        ("Phone", item["phone"] or "Not provided"),
        ("Requested service", item["target"]),
        ("Requested dates", item["requested_dates"]),
        ("Adults", _value(inquiry, "adults", 0)),
        ("Children", _value(inquiry, "children", 0)),
        ("Infants", _value(inquiry, "infants", 0)),
        (
            "Currency",
            _value(
                inquiry,
                "preferred_currency",
                _value(inquiry, "currency", "Not specified"),),),
        ("Source", item["source"]),
        ("Submitted", item["created_at"]),
        ("Archived", "Yes" if item["is_archived"] else "No"),]

    if service_type == "safari":
        details.extend([
            (
                "Safari destination",
                _relationship_name(inquiry, "destination"),
            ),
            (
                "Safari property",
                _relationship_name(inquiry, "property"),
            ),
            (
                "Package",
                _relationship_name(inquiry, "package_option"),
            ),
            (
                "Rate",
                _relationship_name(inquiry, "rate"),
            ),
            (
                "Children's ages",
                _value(inquiry, "children_ages", "Not provided"),),])

    elif service_type == "stay":

        # Stay is resolved from the foreign key because StayInquiry does not
        # expose a `stay` relationship.
        stay = (
            db.session.get(Stay, inquiry.stay_id)
            if inquiry.stay_id
            else None)

        stay_name = (
                getattr(stay, "name", None)
                or getattr(stay, "title", None)
                or getattr(stay, "property_name", None)
                or "Not specified")

        room_name = _relationship_name(
            inquiry,
            "room",
            "Any suitable room",)

        details.extend([
            ("Stay", stay_name),
            ("Room", room_name),
            ("Country", _value(inquiry, "country", "Not provided")),
            ("Check-in", _value(inquiry, "check_in", "Not specified")),
            ("Check-out", _value(inquiry, "check_out", "Not specified")),
        ])
    else:
        details.extend([
            (
                "Experience",
                _relationship_name(inquiry, "experience"),
            ),
            ("Country", _value(inquiry, "country", "Not provided")),
            (
                "Preferred date",
                _value(inquiry, "preferred_date", "Not specified"),
            ),
        ])

    return item, details


def _filter_inquiries(items):
    """Apply the common service type, status, and search filters."""
    selected_type = request.args.get("type", "").strip().lower()
    selected_status = request.args.get("status", "").strip().lower()
    search = request.args.get("q", "").strip()

    if selected_type in SERVICE_TYPES:
        items = [
            item for item in items
            if item["service_type"] == selected_type
        ]
    else:
        selected_type = ""

    if selected_status:
        items = [
            item for item in items
            if str(item["status"]).lower() == selected_status
        ]

    if search:
        query = search.casefold()

        items = [
            item for item in items
            if any(
                query in str(item.get(field, "")).casefold()
                for field in (
                    "reference",
                    "customer",
                    "email",
                    "phone",
                    "target",
                    "service_label",
                    "source",
                )
            )
        ]

    return items, selected_type, selected_status, search


def _inquiry_counts(items):
    """Calculate counts for whichever collection is supplied."""
    return {
        "total": len(items),
        "safari": sum(
            item["service_type"] == "safari" for item in items
        ),
        "stay": sum(
            item["service_type"] == "stay" for item in items
        ),
        "experience": sum(
            item["service_type"] == "experience" for item in items
        ),
        "new": sum(
            str(item["status"]).lower() == "new" for item in items
        ),
    }


def _parse_optional_date(value, field_label, errors):
    """Parse an optional ISO date from a submitted form."""
    value = (value or "").strip()

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field_label} must be a valid date.")
        return None


def _submitted_int(field, label, errors, default, minimum=0):
    """Read and validate an integer form field."""
    raw_value = request.form.get(field, str(default)).strip()

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be a whole number.")
        return default

    if value < minimum:
        errors.append(f"{label} must be at least {minimum}.")
        return default

    return value


def _edit_form_context(service_type, inquiry, errors=None):
    """Prepare common data for the edit template."""
    item = _make_inbox_item(service_type, inquiry)

    return {
        "inquiry": inquiry,
        "item": item,
        "service_type": service_type,
        "service_label": SERVICE_TYPES[service_type],
        "errors": errors or [],
        "form_data": request.form if request.method == "POST" else {},}

# =============================================================================
# Active Enquiries Inbox
# =============================================================================
@service_inquiries_bp.route("/", methods=["GET"])
@admin_required
def index():
    """Display the active Service Enquiries inbox."""
    items, selected_type, selected_status, search = _filter_inquiries(_all_inquiries(archived=False))
    counts = _inquiry_counts(_all_inquiries(archived=False))

    return render_template(
        "admin/service_inquiries/index.html",
        inquiries=items,
        counts=counts,
        service_types=SERVICE_TYPES,
        selected_type=selected_type,
        selected_status=selected_status,
        search=search,)

# =============================================================================
# Enquiry Detail and Status Updates
# =============================================================================
@service_inquiries_bp.route("/<string:service_type>/<int:inquiry_id>",methods=["GET", "POST"],)
@admin_required
def detail(service_type, inquiry_id):
    """View an enquiry and update its status when it is active."""

    service_type = service_type.lower()
    inquiry = _get_inquiry(service_type, inquiry_id)

    allowed_statuses = STATUS_OPTIONS[service_type]
    is_archived = bool(getattr(inquiry, "is_archived", False))

    if request.method == "POST":

        # Archived enquiries must be restored before status changes.
        if is_archived:
            flash(
                "Restore this enquiry before updating its status.",
                "warning",
            )

            return redirect(
                url_for(
                    "service_inquiries.detail",
                    service_type=service_type,
                    inquiry_id=inquiry.id,
                )
            )

        new_status = request.form.get("status", "").strip()

        allowed_values = {
            value for value, _label in allowed_statuses
        }

        if new_status not in allowed_values:
            flash(
                "Please choose a valid enquiry status.",
                "warning",
            )

            return redirect(
                url_for(
                    "service_inquiries.detail",
                    service_type=service_type,
                    inquiry_id=inquiry.id,
                )
            )

        inquiry.status = new_status

        try:
            db.session.commit()

            flash(
                "Enquiry status updated successfully.",
                "success",
            )

        except Exception:
            db.session.rollback()

            flash(
                "The enquiry status could not be updated. Please try again.",
                "danger",
            )

        return redirect(
            url_for(
                "service_inquiries.detail",
                service_type=service_type,
                inquiry_id=inquiry.id,
            )
        )

    # -------------------------------------------------------------------------
    # Build the standard detail context.
    # -------------------------------------------------------------------------
    item, details = _detail_context(service_type, inquiry)

    # -------------------------------------------------------------------------
    # Stay-specific context
    # -------------------------------------------------------------------------
    # Stay inquiries store:
    #   inquiry.stay_id -> Stay
    #   inquiry.room_id -> StayRoom
    #
    # Resolve those records directly for the CMS detail page.
    # -------------------------------------------------------------------------
    if service_type == "stay":
        stay = db.session.get(Stay, inquiry.stay_id)
        room = db.session.get(StayRoom, inquiry.room_id) if inquiry.room_id else None

        item["stay_name"] = (
                getattr(stay, "name", None)
                or getattr(stay, "title", None)
                or "Stay not specified"
        )

        item["room_name"] = (
                getattr(room, "name", None)
                or getattr(room, "room_name", None)
                or "Any suitable room")

    return render_template(
        "admin/service_inquiries/detail.html",
        inquiry=inquiry,
        item=item,
        details=details,
        service_type=service_type,
        status_options=allowed_statuses,
        special_requests=_value(
            inquiry,
            "special_requests",
            "",),
        internal_notes=_value(
            inquiry,
            "internal_notes",
            "",),
        is_archived=is_archived,)
# =============================================================================
# Edit Enquiry
# =============================================================================
@service_inquiries_bp.route("/<string:service_type>/<int:inquiry_id>/edit",methods=["GET", "POST"],)
@admin_required
def edit(service_type, inquiry_id):
    """
    Edit customer and enquiry details.

    The linked Safari, Stay, or Experience is deliberately preserved.
    The enquiry reference and status are also preserved.
    """
    service_type = service_type.lower()
    inquiry = _get_inquiry(service_type, inquiry_id)

    if inquiry.is_archived:
        flash(
            "Restore this enquiry before editing it.",
            "warning",
        )
        return redirect(
            url_for(
                "service_inquiries.archived",
            )
        )

    if request.method == "POST":
        errors = []

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        country = request.form.get("country", "").strip()
        currency = request.form.get(
            "preferred_currency",
            _value(inquiry, "preferred_currency", "KES"),
        ).strip().upper()

        special_requests = request.form.get(
            "special_requests", ""
        ).strip()

        internal_notes = request.form.get(
            "internal_notes", ""
        ).strip()

        if not full_name:
            errors.append("Customer name is required.")

        if not email:
            errors.append("Email address is required.")

        if not currency:
            errors.append("Preferred currency is required.")

        adults = _submitted_int(
            "adults",
            "Adults",
            errors,
            default=_value(inquiry, "adults", 1),
            minimum=1,
        )

        children = _submitted_int(
            "children",
            "Children",
            errors,
            default=_value(inquiry, "children", 0),
            minimum=0,
        )

        infants = _submitted_int(
            "infants",
            "Infants",
            errors,
            default=_value(inquiry, "infants", 0),
            minimum=0,
        )

        if service_type == "safari":
            start_date = _parse_optional_date(
                request.form.get("preferred_start_date"),
                "Preferred start date",
                errors,
            )

            end_date = _parse_optional_date(
                request.form.get("preferred_end_date"),
                "Preferred end date",
                errors,
            )

            if start_date and end_date and end_date < start_date:
                errors.append(
                    "Preferred end date cannot be before the start date."
                )

            children_ages = request.form.get(
                "children_ages", ""
            ).strip()

        elif service_type == "stay":
            check_in = _parse_optional_date(
                request.form.get("check_in"),
                "Check-in date",
                errors,
            )

            check_out = _parse_optional_date(
                request.form.get("check_out"),
                "Check-out date",
                errors,
            )

            if not check_in:
                errors.append("Check-in date is required.")

            if not check_out:
                errors.append("Check-out date is required.")

            if check_in and check_out and check_out <= check_in:
                errors.append(
                    "Check-out must be after check-in."
                )

            preferred_room_type = request.form.get(
                "preferred_room_type", ""
            ).strip()

        else:
            preferred_date = _parse_optional_date(
                request.form.get("preferred_date"),
                "Preferred date",
                errors,
            )

        # Respect each model's existing maximum field lengths.
        max_lengths = {
            "full_name": 180 if service_type == "safari" else 150,
            "email": 255 if service_type == "stay" else 254,
            "phone": 40,
            "preferred_currency": 10,
        }

        values_to_check = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "preferred_currency": currency,
        }

        for field, value in values_to_check.items():
            if len(value) > max_lengths[field]:
                errors.append(
                    f"{field.replace('_', ' ').capitalize()} "
                    f"cannot exceed {max_lengths[field]} characters."
                )

        if errors:
            for error in errors:
                flash(error, "warning")

            return render_template(
                "admin/service_inquiries/edit.html",
                **_edit_form_context(
                    service_type,
                    inquiry,
                    errors,
                ),
            )

        # Update shared fields.
        inquiry.full_name = full_name
        inquiry.email = email
        inquiry.phone = phone
        inquiry.adults = adults
        inquiry.children = children
        inquiry.preferred_currency = currency
        inquiry.special_requests = special_requests

        # These fields exist only on selected inquiry models.
        if hasattr(inquiry, "country"):
            inquiry.country = country

        if hasattr(inquiry, "infants"):
            inquiry.infants = infants

        if hasattr(inquiry, "internal_notes"):
            inquiry.internal_notes = internal_notes

        # Update only the date and service-specific preference fields.
        if service_type == "safari":
            inquiry.preferred_start_date = start_date
            inquiry.preferred_end_date = end_date
            inquiry.children_ages = children_ages

        elif service_type == "stay":
            inquiry.check_in = check_in
            inquiry.check_out = check_out
            inquiry.preferred_room_type = preferred_room_type

        else:
            inquiry.preferred_date = preferred_date

        try:
            db.session.commit()
            flash(
                "Enquiry details updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "service_inquiries.detail",
                    service_type=service_type,
                    inquiry_id=inquiry.id,
                )
            )

        except Exception:
            db.session.rollback()
            flash(
                "The enquiry could not be updated. "
                "Please check the submitted details and try again.",
                "danger",
            )

            return render_template(
                "admin/service_inquiries/edit.html",
                **_edit_form_context(service_type, inquiry),
            )

    return render_template(
        "admin/service_inquiries/edit.html",
        **_edit_form_context(service_type, inquiry),
    )


# =============================================================================
# Archive Enquiry
# =============================================================================
@service_inquiries_bp.route("/<string:service_type>/<int:inquiry_id>/archive",methods=["POST"],)
@admin_required
def archive(service_type, inquiry_id):
    """Archive an enquiry without permanently deleting it."""
    service_type = service_type.lower()
    inquiry = _get_inquiry(service_type, inquiry_id)

    if inquiry.is_archived:
        flash("This enquiry is already archived.", "info")
        return redirect(
            url_for("service_inquiries.archived")
        )

    inquiry.is_archived = True

    try:
        db.session.commit()
        flash(
            f"{SERVICE_TYPES[service_type]} enquiry archived successfully.",
            "success",
        )
    except Exception:
        db.session.rollback()
        flash("The enquiry could not be archived.","danger",)

    return redirect(url_for("service_inquiries.index"))

# =============================================================================
# Restore Enquiry
# =============================================================================
@service_inquiries_bp.route("/<string:service_type>/<int:inquiry_id>/restore",methods=["POST"],)
@admin_required
def restore(service_type, inquiry_id):
    """Restore an archived enquiry to the active inbox."""
    service_type = service_type.lower()
    inquiry = _get_inquiry(service_type, inquiry_id)

    if not inquiry.is_archived:
        flash("This enquiry is already active.", "info")
        return redirect(
            url_for("service_inquiries.index")
        )

    inquiry.is_archived = False

    try:
        db.session.commit()
        flash(
            f"{SERVICE_TYPES[service_type]} enquiry restored successfully.",
            "success",
        )
    except Exception:
        db.session.rollback()
        flash(
            "The enquiry could not be restored.",
            "danger",)

    return redirect(url_for("service_inquiries.index"))

# =============================================================================
# Archived Enquiries View
# =============================================================================
@service_inquiries_bp.route("/archived",methods=["GET"],)
@admin_required
def archived():
    """Display archived enquiries separately from the active inbox."""
    items, selected_type, selected_status, search = _filter_inquiries(
        _all_inquiries(archived=True))

    counts = _inquiry_counts(_all_inquiries(archived=True))

    return render_template(
        "admin/service_inquiries/archived.html",
        inquiries=items,
        counts=counts,
        service_types=SERVICE_TYPES,
        selected_type=selected_type,
        selected_status=selected_status,
        search=search,)

# =============================================================================
# Permanently Delete Enquiry
# =============================================================================
@service_inquiries_bp.route("/<string:service_type>/<int:inquiry_id>/delete",methods=["GET", "POST"],)
@admin_required
def delete(service_type, inquiry_id):
    """
    Permanently delete an archived enquiry.
    GET displays a confirmation page.
    POST performs the deletion.
    Active enquiries must be archived before they can be deleted.
    """
    service_type = service_type.lower()
    inquiry = _get_inquiry(service_type, inquiry_id)

    if not inquiry.is_archived:
        flash(
            "For safety, archive this enquiry before permanently deleting it.",
            "warning",
        )
        return redirect(
            url_for(
                "service_inquiries.detail",
                service_type=service_type,
                inquiry_id=inquiry.id,))

    item = _make_inbox_item(service_type, inquiry)

    if request.method == "GET":
        return render_template(
            "admin/service_inquiries/delete.html",
            inquiry=inquiry,
            item=item,
            service_type=service_type,
            service_label=SERVICE_TYPES[service_type],)

    if request.form.get("confirm_delete") != "yes":
        flash(
            "Please confirm that you understand the deletion is permanent.",
            "warning",
        )
        return redirect(
            url_for(
                "service_inquiries.delete",
                service_type=service_type,
                inquiry_id=inquiry.id,
            )
        )

    # Only an explicit POST request reaches the permanent deletion.
    try:
        db.session.delete(inquiry)
        db.session.commit()
        flash(f"Enquiry {item['reference']} was permanently deleted.","success",)
        return redirect(url_for("service_inquiries.archived"))

    except Exception:
        db.session.rollback()
        flash(
            "The enquiry could not be permanently deleted. "
            "Check whether another record depends on it.",
            "danger",)

        return redirect(
            url_for("service_inquiries.archived"))

# =============================================================================
# Blueprint Exports
# =============================================================================
__all__ = ["service_inquiries_bp"]