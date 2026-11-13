"""
===============================================================================
The Uncharted Route
Contact / Enquiry Forms
===============================================================================

Forms used by the Contact / Enquiries CRM module.

Includes:

    - Contact filtering
    - Manual enquiry creation
    - Enquiry editing
    - Assignment
    - Customer-facing replies
    - Internal notes
    - Status updates
    - Priority updates
    - Follow-up management
    - Resolution handling
    - Archive / restore
    - Bulk enquiry actions

These forms are intentionally kept separate from the service layer.

Validation belongs here.
Business logic belongs in:
    app/services/contact_service.py
    app/services/contact_reply_service.py
    app/services/contact_note_service.py
"""

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    HiddenField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    ValidationError,)

# =============================================================================
# Shared Choices
# =============================================================================
ENQUIRY_TYPE_CHOICES = [
    ("", "All Enquiry Types"),
    ("General", "General"),
    ("Tour", "Tour / Experience"),
    ("Booking", "Booking"),
    ("Corporate", "Corporate Travel"),
    ("Partnership", "Partnership"),
    ("Media", "Media"),
    ("Supplier", "Supplier"),
    ("Complaint", "Complaint"),
    ("Compliment", "Compliment"),
    ("Support", "Support"),
    ("Custom Experience", "Custom Experience"),]

ENQUIRY_TYPE_FORM_CHOICES = [
    ("General", "General"),
    ("Tour", "Tour / Experience"),
    ("Booking", "Booking"),
    ("Corporate", "Corporate Travel"),
    ("Partnership", "Partnership"),
    ("Media", "Media"),
    ("Supplier", "Supplier"),
    ("Complaint", "Complaint"),
    ("Compliment", "Compliment"),
    ("Support", "Support"),
    ("Custom Experience", "Custom Experience"),]

STATUS_CHOICES = [
    ("", "All Statuses"),
    ("New", "New"),
    ("Assigned", "Assigned"),
    ("In Progress", "In Progress"),
    ("Waiting for Customer", "Waiting for Customer"),
    ("Resolved", "Resolved"),
    ("Closed", "Closed"),]

STATUS_FORM_CHOICES = [
    ("New", "New"),
    ("Assigned", "Assigned"),
    ("In Progress", "In Progress"),
    ("Waiting for Customer", "Waiting for Customer"),
    ("Resolved", "Resolved"),
    ("Closed", "Closed"),]

PRIORITY_CHOICES = [
    ("", "All Priorities"),
    ("Low", "Low"),
    ("Normal", "Normal"),
    ("High", "High"),
    ("Urgent", "Urgent"),]

PRIORITY_FORM_CHOICES = [
    ("Low", "Low"),
    ("Normal", "Normal"),
    ("High", "High"),
    ("Urgent", "Urgent"),]

NOTE_TYPE_CHOICES = [
    ("General", "General"),
    ("Follow Up", "Follow Up"),
    ("Customer", "Customer"),
    ("Operations", "Operations"),
    ("Booking", "Booking"),
    ("Sales", "Sales"),
    ("Management", "Management"),
    ("Escalation", "Escalation"),
    ("Resolution", "Resolution"),]

SOURCE_CHOICES = [
    ("Website", "Website"),
    ("Landing Page", "Landing Page"),
    ("Facebook", "Facebook"),
    ("Instagram", "Instagram"),
    ("LinkedIn", "LinkedIn"),
    ("Google", "Google"),
    ("WhatsApp", "WhatsApp"),
    ("Email", "Email"),
    ("Referral", "Referral"),
    ("Manual", "Manual"),]

ARCHIVE_CHOICES = [
    ("active", "Active"),
    ("archived", "Archived"),
    ("all", "All"),]

BULK_ACTION_CHOICES = [
    ("", "Select Action"),
    ("mark_read", "Mark as Read"),
    ("mark_unread", "Mark as Unread"),
    ("assign", "Assign"),
    ("set_priority", "Set Priority"),
    ("set_status", "Set Status"),
    ("archive", "Archive"),
    ("restore", "Restore"),]

# =============================================================================
# Validation Helpers
# =============================================================================
def validate_follow_up_date(form, field):
    """
    Ensure a supplied follow-up date is not in the past.
    A blank value is allowed because follow-up dates are optional.
    """
    if not field.data:
        return
    if field.data < datetime.now():
        raise ValidationError(
            "Follow-up date cannot be in the past.")


def validate_resolution_notes(form, field):
    """
    Ensure resolution notes contain meaningful content when supplied.
    """

    if field.data and not field.data.strip():
        raise ValidationError(
            "Resolution notes cannot contain only whitespace.")

# =============================================================================
# Contact Filter Form
# =============================================================================
class ContactFilterForm(FlaskForm):
    """
    Filter and search the Contact / Enquiry inbox.
    """
    search = StringField(
        "Search",
        validators=[
            Optional(),
            Length(max=255),],)

    status = SelectField(
        "Status",
        choices=STATUS_CHOICES,
        validators=[
            Optional(),],)

    enquiry_type = SelectField(
        "Enquiry Type",
        choices=ENQUIRY_TYPE_CHOICES,
        validators=[
            Optional(),
        ],
    )

    priority = SelectField(
        "Priority",
        choices=PRIORITY_CHOICES,
        validators=[
            Optional(),
        ],
    )

    assigned_user_id = SelectField(
        "Assigned To",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=100),],)

    source = SelectField(
        "Source",
        choices=[
            ("", "All Sources"),
            *SOURCE_CHOICES,
        ],
        validators=[
            Optional(),
        ],
    )

    unread_only = BooleanField(
        "Unread Only",
    )

    follow_up_only = BooleanField(
        "Follow-Up Required",
    )

    urgent_only = BooleanField(
        "Urgent Only",
    )

    archived = SelectField(
        "Archive",
        choices=ARCHIVE_CHOICES,
        default="active",
        validators=[
            Optional(),
        ],
    )

    submit = SubmitField(
        "Apply Filters",
    )

    reset = SubmitField("Reset",)

# =============================================================================
# Contact Create Form
# =============================================================================
class ContactCreateForm(FlaskForm):
    """
    Form for manually creating a Contact / Enquiry.
    """
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=100,),],)

    last_name = StringField(
        "Last Name",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    company = StringField(
        "Company",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    subject = StringField(
        "Subject",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=255,
            ),
        ],
    )

    enquiry_type = SelectField(
        "Enquiry Type",
        choices=ENQUIRY_TYPE_FORM_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=10000,
            ),
        ],
    )

    priority = SelectField(
        "Priority",
        choices=PRIORITY_FORM_CHOICES,
        default="Normal",
        validators=[
            DataRequired(),
        ],
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    source = SelectField(
        "Source",
        choices=SOURCE_CHOICES,
        default="Manual",
        validators=[
            DataRequired(),
        ],
    )

    follow_up_required = BooleanField(
        "Follow-Up Required",
        default=False,
    )

    follow_up_date = DateTimeLocalField(
        "Follow-Up Date",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_follow_up_date,],)
    newsletter_opt_in = BooleanField("Subscribe to Newsletter",)
    submit = SubmitField("Create Enquiry",)

# =============================================================================
# Contact Edit Form
# =============================================================================
class ContactEditForm(FlaskForm):
    """
    Form for editing an existing Contact / Enquiry.
    """
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=100,),],)

    last_name = StringField(
        "Last Name",
        validators=[
            Optional(),
            Length(max=100),],)

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),],)

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=50),],)

    company = StringField(
        "Company",
        validators=[
            Optional(),
            Length(max=150),],)

    country = StringField(
        "Country",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    subject = StringField(
        "Subject",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=255,
            ),
        ],
    )

    enquiry_type = SelectField(
        "Enquiry Type",
        choices=ENQUIRY_TYPE_FORM_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=10000,
            ),
        ],
    )

    status = SelectField(
        "Status",
        choices=STATUS_FORM_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    priority = SelectField(
        "Priority",
        choices=PRIORITY_FORM_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    source = SelectField(
        "Enquiry Source",
        choices=[
            ("Website", "Website"),
            ("Landing Page", "Landing Page"),
            ("Facebook", "Facebook"),
            ("Instagram", "Instagram"),
            ("LinkedIn", "LinkedIn"),
            ("Google", "Google"),
            ("WhatsApp", "WhatsApp"),
            ("Email", "Email"),
            ("Referral", "Referral"),
            ("Manual", "Manual"),
        ],
        validators=[Optional()],
    )

    assigned_user_id = SelectField(
        "Assigned To",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    follow_up_required = BooleanField("Follow-Up Required",)
    follow_up_date = DateTimeLocalField(
        "Follow-Up Date",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_follow_up_date,],)

    resolution_notes = TextAreaField(
        "Resolution Notes",
        validators=[
            Optional(),
            validate_resolution_notes,
            Length(max=10000),],)

    newsletter_opt_in = BooleanField("Newsletter Opt-In",)
    submit = SubmitField("Save Changes",)

# =============================================================================
# Contact Assignment Form
# =============================================================================
class ContactAssignmentForm(FlaskForm):
    """
    Assign an enquiry to an internal user.
    """
    assigned_user_id = SelectField(
        "Assign To",
        coerce=int,
        choices=[],
        validators=[
            Optional(),],)

    department = StringField(
        "Department",
        validators=[
            Optional(),
            Length(max=100),],)

    submit = SubmitField("Assign Enquiry",)

# =============================================================================
# Contact Status Form
# =============================================================================
class ContactStatusForm(FlaskForm):
    """
    Quickly update the status of an enquiry.
    """
    status = SelectField(
        "Status",
        choices=STATUS_FORM_CHOICES,
        validators=[
            DataRequired(),],)

    submit = SubmitField("Update Status",)

# =============================================================================
# Contact Priority Form
# =============================================================================
class ContactPriorityForm(FlaskForm):
    """
    Quickly update enquiry priority.
    """
    priority = SelectField(
        "Priority",
        choices=PRIORITY_FORM_CHOICES,
        validators=[
            DataRequired(),],)

    submit = SubmitField("Update Priority",)

# =============================================================================
# Contact Follow-Up Form
# =============================================================================

class ContactFollowUpForm(FlaskForm):
    """
    Schedule, update, or cancel a follow-up.
    """

    follow_up_required = BooleanField(
        "Follow-Up Required",
        default=True,
    )

    follow_up_date = DateTimeLocalField(
        "Follow-Up Date",
        format="%Y-%m-%dT%H:%M",
        validators=[
            Optional(),
            validate_follow_up_date,
        ],
    )

    submit = SubmitField(
        "Save Follow-Up",
    )


# =============================================================================
# Contact Reply Form
# =============================================================================
class ContactReplyForm(FlaskForm):
    """
    Form for composing a customer-facing reply.

    The actual email delivery is handled by:
        app.services.contact_reply_service
        app.services.email_service
    """

    subject = StringField(
        "Subject",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=20000,
            ),
        ],
    )

    send_email = BooleanField(
        "Send via Email",
        default=True,)

    mark_in_progress = BooleanField(
        "Mark Enquiry as In Progress",
        default=True,)

    submit = SubmitField(
        "Send Reply",)

# =============================================================================
# Contact Note Form
# =============================================================================
class ContactNoteForm(FlaskForm):
    """
    Form for adding an internal note.
    Internal notes are never sent to the customer.
    """
    note = TextAreaField(
        "Internal Note",
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=20000,
            ),
        ],
    )

    note_type = SelectField(
        "Note Type",
        choices=NOTE_TYPE_CHOICES,
        default="General",
        validators=[
            DataRequired(),
        ],
    )

    is_important = BooleanField("Mark as Important",)
    submit = SubmitField("Add Note",)

# =============================================================================
# Contact Resolution Form
# =============================================================================
class ContactResolutionForm(FlaskForm):
    """
    Form for resolving an enquiry.
    """
    resolution_notes = TextAreaField(
        "Resolution Notes",
        validators=[
        DataRequired(),
        Length(
            min=1,
            max=10000,
        ),
        validate_resolution_notes,
        ],
    )

    close_after_resolution = BooleanField(
        "Close Enquiry After Resolution",
        default=False,
    )

    submit = SubmitField(
        "Resolve Enquiry",
    )

# =============================================================================
# Contact Archive Form
# =============================================================================
class ContactArchiveForm(FlaskForm):
    """
    Form for archiving or restoring an enquiry.
    """

    action = HiddenField(
        "Action",
        validators=[
            DataRequired(),
        ],
    )

    submit = SubmitField(
        "Archive Enquiry",
    )

# =============================================================================
# Contact Bulk Action Form
# =============================================================================
class ContactBulkActionForm(FlaskForm):
    """
    Form for performing bulk actions on selected enquiries.
    Selected Contact IDs are normally supplied by the route from submitted
    checkbox values.
    Depending on the selected action, the route may use:
        assigned_user_id
        priority
        status
    """

    action = SelectField(
        "Action",
        choices=BULK_ACTION_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    assigned_user_id = SelectField(
        "Assign To",
        coerce=int,
        choices=[],
        validators=[
            Optional(),],)

    priority = SelectField(
        "Priority",
        choices=PRIORITY_FORM_CHOICES,
        validators=[
            Optional(),],)

    status = SelectField(
        "Status",
        choices=STATUS_FORM_CHOICES,
        validators=[
            Optional(),],)
    submit = SubmitField("Apply Action",)

# =============================================================================
# Contact Read Status Form
# =============================================================================
class ContactReadStatusForm(FlaskForm):
    """
    Quickly mark an enquiry as read or unread.
    """
    action = HiddenField(
        "Action",
        validators=[
            DataRequired(),],)
    submit = SubmitField("Update Read Status",)


# =============================================================================
# Contact Restore Form
# =============================================================================
class ContactRestoreForm(FlaskForm):
    """Form for restoring an archived enquiry."""
    action = HiddenField(
        "Action",
        validators=[DataRequired()],
    )
    submit = SubmitField("Restore Enquiry")
